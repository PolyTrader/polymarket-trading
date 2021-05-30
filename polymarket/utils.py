import os
import json

from eth_account import Account
from web3 import Web3, eth
from web3.gas_strategies import rpc
from web3.middleware import geth_poa_middleware, construct_sign_and_send_raw_middleware
import importlib_resources as resources


# Load the ABI at start-up
erc20_abi = json.loads(resources.read_text('polymarket.abi', 'ERC20.json'))


def approve_erc20(w3, token_address, spender, amount):
    instance = w3.eth.contract(address=token_address, abi=erc20_abi)
    decimals = instance.functions.decimals().call()

    raw_amount = int(float(amount) * (10 ** decimals))
    instance.functions.approve(_spender=spender, _value=int(raw_amount)).transact()
    return raw_amount


def initialize_identity():
    private_key = os.getenv('POLYGON_PRIVATE_KEY')
    if not private_key:
        raise RuntimeError('POLYGON_PRIVATE_KEY Environment Variable Not Found')

    vigil_key = os.getenv('MATIC_VIGIL_RPC_KEY')
    if not vigil_key:
        raise RuntimeError('MATIC_VIGIL_RPC_KEY Environment Variable Not Found')

    acct = Account.from_key(private_key)
    w3 = Web3(Web3.HTTPProvider(f'https://rpc-mainnet.maticvigil.com/v1/{vigil_key}'))

    w3.eth.default_account = acct.address
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    w3.middleware_onion.add(construct_sign_and_send_raw_middleware(acct))
    w3.eth.set_gas_price_strategy(rpc.rpc_gas_price_strategy)

    return w3
