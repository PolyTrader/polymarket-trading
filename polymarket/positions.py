import importlib_resources as resources
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

from .markets import get_active_markets
from .utils import get_pool_balances

parent_collection_id = '0x0000000000000000000000000000000000000000000000000000000000000000'


def reduce(function, iterable, initializer=None):
    it = iter(iterable)
    if initializer is None:
        value = next(it)
    else:
        value = initializer
    for element in it:
        value = function(value, element)
    return value


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
    return calc_price(pool_balances)


def list_positions(web3_provider, user):
    markets = get_active_markets()
    mkt_pos = get_positions(user)

    mkts = {mkt['marketMakerAddress'].lower(): mkt for mkt in markets}

    positions = {}
    for pos in mkt_pos['marketPositions']:
        # If you don't currently own any shares in this position, don't list it.
        if pos['netQuantity'] == '0':
            continue

        mkt_id = pos['market']['id']
        if not positions.get(mkt_id):
            positions[mkt_id] = {}

        if not positions[mkt_id].get('question'):
            positions[mkt_id] = {'question': mkts[mkt_id]['question']}

        if not positions[mkt_id].get('positions'):
            positions[mkt_id]['positions'] = [None] * len(mkts[mkt_id]['outcomes'])

        outcome_label = mkts[mkt_id]['outcomes'][int(pos['outcomeIndex'])]

        condition_id = mkts[mkt_id]['conditionId']
        num_outcomes = len(mkts[mkt_id]['outcomes'])
        outcome_prices = get_chain_price(web3_provider, mkt_id, condition_id, num_outcomes)
        outcome_price = outcome_prices[int(pos['outcomeIndex'])]

        positions[mkt_id]['condition_id'] = condition_id
        positions[mkt_id]['positions'][int(pos['outcomeIndex'])] = (outcome_label, pos['netQuantity'], outcome_price,
                                                                    pos['netValue'])

    print("-"*80)
    print("Question (condition id)")
    print("    position / number shares / share price / position value / condition id")
    for _, v in positions.items():
        print("-" * 80)
        print(f"{v['question']} ({v['condition_id']})")

        for z in v['positions']:
            if z is not None:
                position_name = z[0]
                num_shares = int(z[1])/10**6
                share_price = float(z[2])
                position_value = num_shares * share_price

                print(f"    {position_name} / {num_shares:.6f} / {share_price:.4f} / ${position_value:.4f} ")
