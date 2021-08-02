from mpmath import mp
from pydash import _

from ..utils import conditional_token_address, load_evm_abi, usdc_address

parent_collection_id = '0x0000000000000000000000000000000000000000000000000000000000000000'


def get_pool_balances(web3_provider, mkt_id, condition_id, num_outcomes):
    conditional_token_abi = load_evm_abi('ConditionalTokens.json')
    contract = web3_provider.eth.contract(address=conditional_token_address, abi=conditional_token_abi)
    checked_mkt_id = web3_provider.toChecksumAddress(mkt_id)

    pool_balances = []
    for idx in range(num_outcomes):
        val = contract.functions.getCollectionId(parent_collection_id, condition_id, 0x1 << idx).call()

        position_id = contract.functions.getPositionId(usdc_address, val).call()

        balance = contract.functions.balanceOf(checked_mkt_id, position_id).call()
        pool_balances.append(balance)

    return pool_balances


def calc_sell_amount_in_collateral(shares_to_sell, outcome_index, pool_balances, fee):
    mp.dps = 90

    if outcome_index < 0 or outcome_index >= len(pool_balances):
        raise RuntimeError(f'Outcome index {outcome_index} must be between 0 and {len(pool_balances) - 1}')

    holdings = pool_balances[outcome_index]
    other_holdings = _.filter(pool_balances, lambda val, idx: outcome_index != idx)

    shares_to_sell_big = mp.mpf(shares_to_sell)
    holdings_big = mp.mpf(holdings)
    other_holdings_big = _.map(other_holdings, lambda x: mp.mpf(x))

    def func(r):
        R = r / (1 - fee)
        first_term = _.reduce(_.map(other_holdings_big, lambda h: h - R), lambda a, b: a * b)
        second_term = holdings_big + shares_to_sell_big - R
        third_term = _.reduce(other_holdings_big, lambda a, b: a * b, holdings_big)
        return first_term * second_term - third_term

    try:
        r = mp.findroot(func, 0, maxsteps=100)
    except Exception as e:
        r = None

    return r




