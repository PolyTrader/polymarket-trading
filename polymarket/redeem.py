from json import loads
import importlib_resources as resources

from .utils import approve_erc20, load_evm_abi, conditional_token_address, usdc_address

hash_zero = "0x0000000000000000000000000000000000000000000000000000000000000000"


def redeem(web3_provider, condition_id, num_outcomes):
    conditional_token_abi = load_evm_abi('ConditionalTokens.json')

    index_set = [1 << x for x in range(num_outcomes)]

    contract = web3_provider.eth.contract(address=conditional_token_address, abi=conditional_token_abi)
    return contract.functions.redeemPositions(usdc_address, hash_zero, condition_id, index_set).transact()
