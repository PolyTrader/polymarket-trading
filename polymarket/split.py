from .utils import approve_erc20, conditional_token_address, load_evm_abi, usdc_address

hash_zero = "0x0000000000000000000000000000000000000000000000000000000000000000"


def split(web3_provider, condition_id, num_outcomes, amount):
    conditional_token_abi = load_evm_abi('ConditionalTokens.json')

    index_set = [1 << x for x in range(num_outcomes)]
    approved_amount = approve_erc20(web3_provider, conditional_token_address, amount)

    contract = web3_provider.eth.contract(address=conditional_token_address, abi=conditional_token_abi)
    trx_hash = contract.functions.splitPosition(usdc_address, hash_zero, condition_id, index_set, approved_amount)\
        .transact()
    web3_provider.eth.wait_for_transaction_receipt(trx_hash)
    return trx_hash
