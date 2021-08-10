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
parent_collection_id = '0x0000000000000000000000000000000000000000000000000000000000000000'


@lru_cache(maxsize=16)
def load_evm_abi(abi):
    return json.loads(resources.read_text('polymarket.abi', abi))


def approve_erc20(w3, spender, amount):
    global usdc_address

    erc20_abi = load_evm_abi('ERC20.json')
    instance = w3.eth.contract(address=usdc_address, abi=erc20_abi)
    decimals = instance.functions.decimals().call()

    raw_amount = int(float(amount) * (10 ** decimals)) + 1
    w3.eth.wait_for_transaction_receipt(instance.functions.approve(_spender=spender, _value=raw_amount).transact())
    return raw_amount - 1


def conditional_token_approve_for_all(w3, fixed_product_market_maker_address, status):
    global conditional_token_address

    conditional_token_abi = load_evm_abi('ConditionalTokens.json')
    instance = w3.eth.contract(address=conditional_token_address, abi=conditional_token_abi)
    receipt = w3.eth.wait_for_transaction_receipt(
        instance.functions.setApprovalForAll(fixed_product_market_maker_address, status).transact())
    return receipt['transactionIndex']


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

    rpc_uri = os.getenv('RPC_URI')

    vigil_key = None
    if not rpc_uri:
        vigil_key = os.getenv('MATIC_VIGIL_RPC_KEY')
        rpc_uri = f'https://rpc-mainnet.maticvigil.com/v1/{vigil_key}'

    if not vigil_key and not rpc_uri:
        raise RuntimeError('Must include either RPC_URI or MATIC_VIGIL_RPC_KEY environment variable')

    acct = Account.from_key(private_key)
    w3 = Web3(Web3.HTTPProvider(rpc_uri))

    w3.eth.default_account = acct.address
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    w3.middleware_onion.add(construct_sign_and_send_raw_middleware(acct))

    if gas_price:
        w3.eth.set_gas_price_strategy(user_supplied_gas_price)
    else:
        w3.eth.set_gas_price_strategy(rpc.rpc_gas_price_strategy)

    return w3


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
