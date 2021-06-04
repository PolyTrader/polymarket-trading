import argparse
import logging

from web3 import Web3

from .utils import initialize_identity
from .buy import buy
from .sell import sell
from .redeem import redeem


logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(prog="pm-trade")
    sub_parser = parser.add_subparsers(dest='subparser_name')

    buy_parser = sub_parser.add_parser('buy', help='Buy Shares')
    buy_parser.add_argument('-m', help="Market Maker Address", required=True)
    buy_parser.add_argument('-a', help="Amount to spend (USDC)", required=True)
    buy_parser.add_argument('-i', help="Index of outcome choice", required=True)
    buy_parser.add_argument('-n', help="Minimum number of shares expected (slippage)", required=True)

    sell_parser = sub_parser.add_parser('sell', help='Sell Shares')
    sell_parser.add_argument('-m', help="Market Maker Address", required=True)
    sell_parser.add_argument('-a', help="Amount to recover (USDC)", required=True)
    sell_parser.add_argument('-i', help="Index of outcome choice", required=True)
    sell_parser.add_argument('-n', help="Maximum number of shares expected (slippage)", required=True)

    redeem_parser = sub_parser.add_parser('redeem', help='Redeem Shares')
    redeem_parser.add_argument('-c', help='Condition ID to redeem', required=True)
    redeem_parser.add_argument('-n', help='Number of outcomes', type=int, required=True)

    args = parser.parse_args()

    if args.subparser_name in ['buy', 'sell']:
        try:
            market = args.m
            amount = args.a
            index = args.i
            slip_shares = args.n
        except AttributeError as e:
            logger.error(e)
            exit()

    elif args.subparser_name in ['redeem']:
        try:
            condition_id = args.c
            num_outcomes = args.n
        except AttributeError as e:
            logger.error(e)
            exit()

    w3 = initialize_identity()
    if args.subparser_name == 'buy':
        trx_hash = buy(w3, market, amount, index, slip_shares)

    elif args.subparser_name == 'sell':
        trx_hash = sell(w3, market, amount, index, slip_shares)

    elif args.subparser_name == 'redeem':
        trx_hash = redeem(w3, condition_id, num_outcomes)

    print(Web3.toHex(trx_hash))

