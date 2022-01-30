from .markets import get_active_markets
from .utils import approve_erc20, load_evm_abi


def add_liquidity(web3_provider, slug=None, market_maker_address=None, amount=0):
    if slug is None and market_maker_address is None:
        raise RuntimeError('Most provide either slug or market address.')

    if not market_maker_address:
        market_json = get_active_markets(slug=slug)[0]
        market_maker_address = market_json['marketMakerAddress']

    fixed_product_market_maker_address_abi = load_evm_abi('FixedProductMarketMaker.json')

    approved_amount = approve_erc20(web3_provider, market_maker_address, amount)

    contract = web3_provider.eth.contract(address=market_maker_address, abi=fixed_product_market_maker_address_abi)
    trx_hash = contract.functions.addFunding(approved_amount, []).transact()
    web3_provider.eth.wait_for_transaction_receipt(trx_hash)
    return trx_hash


def remove_liquidity(web3_provider, slug=None, market_maker_address=None, amount=0):
    if slug is None and market_maker_address is None:
        raise RuntimeError('Most provide either slug or market address.')

    if not market_maker_address:
        market_json = get_active_markets(slug=slug)[0]
        market_maker_address = market_json['marketMakerAddress']

    fixed_product_market_maker_address_abi = load_evm_abi('FixedProductMarketMaker.json')

    amount = int(amount * (10 ** 6))

    contract = web3_provider.eth.contract(address=market_maker_address, abi=fixed_product_market_maker_address_abi)
    trx_hash = contract.functions.removeFunding(amount).transact()
    web3_provider.eth.wait_for_transaction_receipt(trx_hash)
    return trx_hash


def liquidity_balance(web3_provider, slug=None, market_maker_address=None, user=None):
    if slug is None and market_maker_address is None:
        raise RuntimeError('Most provide either slug or market address.')

    if not market_maker_address:
        market_json = get_active_markets(slug=slug)[0]
        market_maker_address = market_json['marketMakerAddress']

    fixed_product_market_maker_address_abi = load_evm_abi('FixedProductMarketMaker.json')
    contract = web3_provider.eth.contract(address=market_maker_address, abi=fixed_product_market_maker_address_abi)
    value = contract.functions.balanceOf(web3_provider.eth.default_account).call()
    print(f"LP Tokens: {value / (10 ** 6)}")


def liquidity_withdraw_fees(web3_provider, slug=None, market_maker_address=None):
    if slug is None and market_maker_address is None:
        raise RuntimeError('Most provide either slug or market address.')

    if not market_maker_address:
        market_json = get_active_markets(slug=slug)[0]
        market_maker_address = market_json['marketMakerAddress']

    fixed_product_market_maker_address_abi = load_evm_abi('FixedProductMarketMaker.json')

    contract = web3_provider.eth.contract(address=market_maker_address, abi=fixed_product_market_maker_address_abi)
    trx_hash = contract.functions.withdrawFees(web3_provider.eth.default_account).transact()
    web3_provider.eth.wait_for_transaction_receipt(trx_hash)
    return trx_hash
