import json

import importlib_resources as resources
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

from .markets import get_active_markets
from .utils import conditional_token_address, get_pool_balances, load_evm_abi, usdc_address


parent_collection_id = '0x0000000000000000000000000000000000000000000000000000000000000000'


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def reduce(function, iterable, initializer=None):
    it = iter(iterable)
    if initializer is None:
        value = next(it)
    else:
        value = initializer
    for element in it:
        value = function(value, element)
    return value


def get_balance_list(web3_provider, contract, wallet, token_query_list):
    checked_wallet = web3_provider.toChecksumAddress(wallet)

    balances = []
    for token_chunk in chunks(token_query_list, 250):
        wallets = [checked_wallet] * len(token_chunk)
        balances.extend(contract.functions.balanceOfBatch(wallets, token_chunk).call())

    return balances


def build_token_balance_dict(balances, token_query_list):
    token_balance = {}
    for idx in range(len(balances)):
        token_balance[token_query_list[idx]] = balances[idx]

    return token_balance


def build_token_price_dict(web3_provider, token_balance, token_markets):
    token_prices = {}
    for token, balance in token_balance.items():
        if balance != 0:
            market = token_markets[token]
            prices = get_chain_price(web3_provider,
                                     market['marketMakerAddress'],
                                     market['conditionId'],
                                     len(market['outcomes']))

            idx = market['outcome_tokens'].index(token)
            token_prices[token] = prices[idx]

    return token_prices


def get_positions(user):
    gql_uri = "https://api.thegraph.com/subgraphs/name/tokenunion/polymarket-matic"
    transport = RequestsHTTPTransport(gql_uri)
    client = Client(transport=transport, fetch_schema_from_transport=True)
    query = gql(resources.read_text('polymarket.gql', 'positions.gql'))

    return client.execute(query, {"user": user.lower()})


def calc_price(pool_balances):
    product = reduce(lambda a, b: a*b, pool_balances)
    denominator = reduce(lambda a, b: a+b, map(lambda h: product / h, pool_balances))
    prices = map(lambda h: (product / h) / denominator, pool_balances)

    return list(prices)


def get_chain_price(web3_provider, mkt_id, condition_id, num_outcomes):
    pool_balances = get_pool_balances(web3_provider, mkt_id, condition_id, num_outcomes)
    try:
        prices = calc_price(pool_balances)
    except ZeroDivisionError:
        prices = [0] * len(pool_balances)

    return prices


def load_cached_market_data():
    mapped_data = {}
    try:
        cached_data = json.load(open("market_data.json"))
        mapped_data = {mkt["id"]: mkt for mkt in cached_data}
    except Exception:
        pass

    return mapped_data


def get_all_balances(web3_provider, wallet, markets):
    conditional_token_abi = load_evm_abi('ConditionalTokens.json')
    contract = web3_provider.eth.contract(address=conditional_token_address, abi=conditional_token_abi)
    mapped_data = load_cached_market_data()

    token_query_list = []
    token_markets = {}
    for mkt in markets:
        num_outcomes = len(mkt['outcomes'])
        condition_id = mkt['conditionId']
        mkt_id = mkt['id']

        outcome_tokens = []
        for idx in range(num_outcomes):
            if mapped_data.get(mkt_id, None) is None:
                val = contract.functions.getCollectionId(parent_collection_id, condition_id, 0x1 << idx).call()
                position_id = contract.functions.getPositionId(usdc_address, val).call()
            else:
                position_id = mapped_data[mkt_id]['outcome_tokens'][idx]

            outcome_tokens.append(int(position_id))
            token_query_list.append(int(position_id))

        mkt['outcome_tokens'] = outcome_tokens

        for token in outcome_tokens:
            token_markets[token] = mkt

    if mapped_data == {}:
        json.dump(markets, open('market_data.json', 'w'))

    balances = get_balance_list(web3_provider, contract, wallet, token_query_list)
    token_balance = build_token_balance_dict(balances, token_query_list)
    token_prices = build_token_price_dict(web3_provider, token_balance, token_markets)

    print_table_header()
    for mkt in markets:
        print_market = False

        for tkn in mkt['outcome_tokens']:
            if token_balance[tkn]:
                print_market = True

        if print_market:
            print_position_header(mkt['question'], mkt['conditionId'])

            for idx in range(len(mkt['outcome_tokens'])):
                tkn = mkt['outcome_tokens'][idx]
                if token_balance[tkn]:
                    print_position(mkt['outcomes'][idx], token_balance[tkn], token_prices[tkn])


def list_positions(web3_provider, user):
    markets = get_active_markets()
    get_all_balances(web3_provider, user, markets)


def print_table_header():
    print("-"*80)
    print("Question (condition id)")
    print("    position / number shares / share price / position value / condition id")


def print_position_header(question, condition_id):
    print("-" * 80)
    print(f"{question} ({condition_id})")


def print_position(position_name, num_shares, share_price):
    ONE = 10 ** 6
    num_shares = num_shares / ONE
    position_value = num_shares * share_price

    print(f"    {position_name} / {num_shares:.6f} / {share_price:.4f} / ${position_value:.4f} ")
