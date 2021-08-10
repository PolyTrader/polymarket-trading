import json

import polymarket
import pytest

quickswap_address = "0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff"
wmatic_address = '0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270'
usdc_address = '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174'
decimals = 18

# Use a closed market to trade against since it will never go away.
# Will the Ever Given exit the Great Bitter Lake in the Suez Canal by July 25?
condition_id = "0x2a2245d9db4616bd30240e64b424e2184d7fb9ee222d72d92313e5fb962ef0fb"
market_address = "0xe25fC2fAA77Cb4EC7312466fCC104EDB02596831"
slug = "will-the-ever-given-exit-the-great-bitter-lake-in-the-suez-canal-by-july-25"


def load_contract(w3, address, file_name):
    with open(file_name) as fp:
        abi = json.load(fp)

    return w3.eth.contract(address=address, abi=abi)


@pytest.fixture(scope="module")
def web3():
    w3 = polymarket.initialize_identity()

    quickswap = load_contract(w3, quickswap_address, 'tests/router02.json')
    wmatic = load_contract(w3, wmatic_address, 'tests/weth9.json')
    # usdc = load_contract(w3, usdc_address, 'polymarket/abi/ERC20.json')

    balance = w3.eth.get_balance(w3.eth.default_account)
    deposit_amount = int(0.1 * balance)
    wmatic.functions.deposit().transact({"value": deposit_amount})
    wmatic.functions.approve(quickswap_address, deposit_amount).transact()

    withdrawal_amount = int(0.5 * deposit_amount)
    path = [wmatic_address, usdc_address]
    quickswap.functions.swapExactETHForTokens(1, path, w3.eth.default_account, 1657180785)\
        .transact({"value": withdrawal_amount})

    return w3


def test_buy(web3):
    trx = polymarket.buy(web3, market_address, 1, 0, 0.01)
    assert trx is not None


def test_sell(web3):
    trx = polymarket.sell(web3, market_address, 0.1, 0, 1)
    assert trx is not None


def test_sell_shares(web3):
    trx = polymarket.sell_shares(web3, slug, "Yes", 2)
    assert trx is not None


def test_split(web3):
    trx = polymarket.split(web3, condition_id, 2, 1)
    assert trx is not None


def test_merge(web3):
    trx = polymarket.merge(web3, condition_id, 2, 1)
    assert trx is not None


def test_redeem(web3):
    trx = polymarket.redeem(web3, condition_id, 2)
    assert trx is not None
