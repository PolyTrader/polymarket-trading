import json

import polymarket


quickswap_address = "0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff"
wmatic_address = '0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270'
usdc_address = '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174'
decimals = 18


def load_contract(w3, address, file_name):
    with open(file_name) as fp:
        abi = json.load(fp)

    return w3.eth.contract(address=address, abi=abi)


def main():
    w3 = polymarket.initialize_identity()

    quickswap = load_contract(w3, quickswap_address, 'tests/router.json')
    wmatic = load_contract(w3, wmatic_address, 'tests/weth9.json')
    usdc = load_contract(w3, usdc_address, 'polymarket/abi/ERC20.json')

    balance = w3.eth.get_balance(w3.eth.default_account)
    deposit_amount = int(balance/2)
    wmatic.functions.deposit().transact({"value": deposit_amount})
    wmatic.functions.approve(quickswap_address, deposit_amount).transact()

    withdrawal_amount = int(0.9 * deposit_amount)
    path = [wmatic_address, usdc_address]
    quickswap.functions.swapExactETHForTokens(1, path, w3.eth.default_account, 1657180785)\
        .transact({"value": withdrawal_amount})

    print(usdc.functions.balanceOf(w3.eth.default_account).call() / 10 ** 6)


if __name__ == "__main__":
    exit(main())
