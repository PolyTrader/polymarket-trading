from .utils import approve_erc20, load_evm_abi


def buy(web3_provider, market_maker_address, amount, index, minimum_shares):
    fixed_product_market_maker_address_abi = load_evm_abi('FixedProductMarketMaker.json')

    approved_amount = approve_erc20(web3_provider, market_maker_address, amount)

    # Adjust share number to the raw value used by the buy contract
    fixed_minimum_shares = int(minimum_shares * (10**6))

    contract = web3_provider.eth.contract(address=market_maker_address, abi=fixed_product_market_maker_address_abi)
    trx_hash = contract.functions.buy(approved_amount, index, fixed_minimum_shares).transact()
    web3_provider.eth.wait_for_transaction_receipt(trx_hash)
    return trx_hash
