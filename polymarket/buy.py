from json import loads
import importlib_resources as resources

from web3 import Web3
from web3.gas_strategies import rpc
from web3.middleware import geth_poa_middleware, construct_sign_and_send_raw_middleware

from .utils import approve_erc20, load_evm_abi


def buy(web3_provider, market_maker_address, amount, index, minimum_shares):
    fixed_product_market_maker_address_abi = load_evm_abi('FixedProductMarketMaker.json')

    usdc_address = '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174'
    approved_amount = approve_erc20(web3_provider, usdc_address, market_maker_address, amount)

    # Adjust share number to the raw value used by the buy contract
    fixed_minimum_shares = int(float(minimum_shares) * (10**6))

    contract = web3_provider.eth.contract(address=market_maker_address, abi=fixed_product_market_maker_address_abi)
    return contract.functions.buy(approved_amount, int(index), int(fixed_minimum_shares)).transact()

