import json
import os
from functools import lru_cache

import importlib_resources as resources
from eth_account import Account
from web3 import Web3
from web3.gas_strategies import rpc
from web3.middleware import construct_sign_and_send_raw_middleware, geth_poa_middleware

conditional_token_address = '0x4D97DCd97eC945f40cF65F87097ACe5EA0476045'
usdc_address = '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174'


@lru_cache(maxsize=16)
def load_evm_abi(abi):
    return json.loads(resources.read_text('polymarket.abi', abi))


def approve_erc20(w3, spender, amount):
    global usdc_address

    erc20_abi = load_evm_abi('ERC20.json')
    instance = w3.eth.contract(address=usdc_address, abi=erc20_abi)
    decimals = instance.functions.decimals().call()

    raw_amount = int(float(amount) * (10 ** decimals)) + 1
    instance.functions.approve(_spender=spender, _value=raw_amount).transact()
    return raw_amount - 1


def conditional_token_approve_for_all(w3, fixed_product_market_maker_address, status):
    global conditional_token_address

    conditional_token_abi = load_evm_abi('ConditionalTokens.json')
    instance = w3.eth.contract(address=conditional_token_address, abi=conditional_token_abi)
    return instance.functions.setApprovalForAll(fixed_product_market_maker_address, status).transact()


def conditional_token_is_approved_for_all(w3, owner, operator):
    global conditional_token_address

    conditional_token_abi = load_evm_abi('ConditionalTokens.json')
    instance = w3.eth.contract(address=conditional_token_address, abi=conditional_token_abi)
    return instance.functions.isApprovedForAll(owner, operator).call()


def initialize_identity(gas_price=None):
    def user_supplied_gas_price(_, trx_params=None):
        return Web3.toWei(gas_price, 'gwei')

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

    if gas_price:
        w3.eth.set_gas_price_strategy(user_supplied_gas_price)
    else:
        w3.eth.set_gas_price_strategy(rpc.rpc_gas_price_strategy)

    return w3
