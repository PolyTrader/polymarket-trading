from .amm.maths import calc_sell_amount_in_collateral
from .markets import get_active_markets
from .utils import conditional_token_approve_for_all, get_pool_balances, load_evm_abi


def sell(web3_provider, market_maker_address, return_amount, index, maximum_shares):
    fixed_product_market_maker_address_abi = load_evm_abi('FixedProductMarketMaker.json')

    fixed_return_amount = int(return_amount * (10**6))
    fixed_maximum_shares = int(maximum_shares * (10**6))

    conditional_token_approve_for_all(web3_provider, market_maker_address, True)
    contract = web3_provider.eth.contract(address=market_maker_address, abi=fixed_product_market_maker_address_abi)
    trx_hash = contract.functions.sell(fixed_return_amount, index, fixed_maximum_shares).transact()
    web3_provider.eth.wait_for_transaction_receipt(trx_hash)

    conditional_token_approve_for_all(web3_provider, market_maker_address, False)

    return trx_hash


def sell_shares(web3_provider, slug, outcome, num_shares, slippage):
    market_json = get_active_markets(slug=slug)[0]
    fixed_product_market_maker_address_abi = load_evm_abi('FixedProductMarketMaker.json')

    fixed_share_count = int(num_shares * (10**6))
    condition_id = market_json['conditionId']
    market_maker_address = market_json['marketMakerAddress']
    num_outcomes = len(market_json['outcomes'])
    outcome_index = market_json['outcomes'].index(outcome)
    fee = float(int(market_json['fee']) / (10**18))

    conditional_token_approve_for_all(web3_provider, market_maker_address, True)
    contract = web3_provider.eth.contract(address=market_maker_address, abi=fixed_product_market_maker_address_abi)

    pool_balances = get_pool_balances(web3_provider, market_maker_address, condition_id, num_outcomes)
    sell_amount_in_usdc = calc_sell_amount_in_collateral(fixed_share_count, outcome_index, pool_balances, fee)

    fixed_return_amount = int(round(float(sell_amount_in_usdc)))

    slippage_fixed_share_count = int(fixed_share_count * (1 + (slippage/100)))

    trx_hash = contract.functions.sell(fixed_return_amount, outcome_index, slippage_fixed_share_count).transact()
    web3_provider.eth.wait_for_transaction_receipt(trx_hash)

    conditional_token_approve_for_all(web3_provider, market_maker_address, False)

    return trx_hash
