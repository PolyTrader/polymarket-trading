import argparse

from web3 import Web3

from .utils import initialize_identity
from .buy import buy

def main():
    parser = argparse.ArgumentParser(prog="pm-trade")
    sub_parser = parser.add_subparsers()

    parser_buy = sub_parser.add_parser('buy', help='Buy Shares')
    parser_buy.add_argument('-m', help="Market Maker Address", required=True)
    parser_buy.add_argument('-a', help="Amount to spend (USDC)", required=True)
    parser_buy.add_argument('-i', help="Index of outcome choice", required=True)
    parser_buy.add_argument('-n', help="Minimum number of shares expected (slippage)", required=True)

    sell_parser = sub_parser.add_parser('sell', help='Sell Shares (Not Implemented)')

    args = parser.parse_args()
    market = args.m
    amount = args.a
    index = args.i
    minimum_shares = args.n

    w3 = initialize_identity()
    trx_hash = buy(w3, market, amount, index, minimum_shares)

    print(Web3.toHex(trx_hash))

