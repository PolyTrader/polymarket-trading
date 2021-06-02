from json import loads
from time import sleep
import importlib_resources as resources

from .utils import approve_erc20, load_evm_abi, conditional_token_approve_for_all, conditional_token_is_approved_for_all


def sell(web3_provider, market_maker_address, return_amount, index, maximum_shares):
    fixed_product_market_maker_address_abi = load_evm_abi('FixedProductMarketMaker.json')

    fixed_return_amount = int(float(return_amount) * (10**6))
    fixed_maximum_shares = int(float(maximum_shares) * (10**6))

    conditional_token_approve_for_all(web3_provider, market_maker_address, True)
    sleep(2) # Force transactions into different blocks.
    contract = web3_provider.eth.contract(address=market_maker_address, abi=fixed_product_market_maker_address_abi)
    trx_hash = contract.functions.sell(fixed_return_amount, int(index), int(fixed_maximum_shares)).transact()
    conditional_token_approve_for_all(web3_provider, market_maker_address, False)

    return trx_hash
