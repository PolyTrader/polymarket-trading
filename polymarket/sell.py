from time import sleep

from .utils import conditional_token_approve_for_all, load_evm_abi


def sell(web3_provider, market_maker_address, return_amount, index, maximum_shares):
    fixed_product_market_maker_address_abi = load_evm_abi('FixedProductMarketMaker.json')

    fixed_return_amount = int(return_amount * (10**6))
    fixed_maximum_shares = int(maximum_shares * (10**6))

    conditional_token_approve_for_all(web3_provider, market_maker_address, True)
    sleep(2)  # Force transactions into different blocks.
    contract = web3_provider.eth.contract(address=market_maker_address, abi=fixed_product_market_maker_address_abi)
    trx_hash = contract.functions.sell(fixed_return_amount, index, fixed_maximum_shares).transact()
    conditional_token_approve_for_all(web3_provider, market_maker_address, False)

    return trx_hash
