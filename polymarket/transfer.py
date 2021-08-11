from .utils import conditional_token_address, load_evm_abi, usdc_address, parent_collection_id

def transfer(web3_provider, condition_id, index, amount, toAddress):
    conditional_token_abi = load_evm_abi('ConditionalTokens.json')
    contract = web3_provider.eth.contract(address=conditional_token_address, abi=conditional_token_abi)

    collId = contract.functions.getCollectionId(parent_collection_id, condition_id, 0x1 << index).call()
    position_id = contract.functions.getPositionId(usdc_address, collId).call()

    myAddress = web3_provider.eth.default_account
    decimals = 6
    raw_amount = int(float(amount) * (10 ** decimals))
    trx_hash = contract.functions.safeTransferFrom(myAddress, toAddress, position_id, raw_amount, "").transact()
    web3_provider.eth.wait_for_transaction_receipt(trx_hash)
    return trx_hash
