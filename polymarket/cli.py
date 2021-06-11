import argparse
import logging

from web3 import Web3

from .buy import buy
from .merge import merge
from .redeem import redeem
from .sell import sell
from .split import split
from .utils import initialize_identity


logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(prog="pm-trade")
    parser.add_argument('-g', help='User supplied gas price (in gwei)', type=int)
    sub_parser = parser.add_subparsers(dest='subparser_name')

    buy_parser = sub_parser.add_parser('buy', help='Buy Shares')
    buy_parser.add_argument('-m', help="Market Maker Address", required=True)
    buy_parser.add_argument('-a', help="Amount to spend (USDC)", type=float, required=True)
    buy_parser.add_argument('-i', help="Index of outcome choice", type=int, required=True)
    buy_parser.add_argument('-n', help="Minimum number of shares expected (slippage)", type=float, required=True)

    sell_parser = sub_parser.add_parser('sell', help='Sell Shares')
    sell_parser.add_argument('-m', help="Market Maker Address", required=True)
    sell_parser.add_argument('-a', help="Amount to recover (USDC)", type=float, required=True)
    sell_parser.add_argument('-i', help="Index of outcome choice", type=int, required=True)
    sell_parser.add_argument('-n', help="Maximum number of shares expected (slippage)", type=float, required=True)

    redeem_parser = sub_parser.add_parser('redeem', help='Redeem Shares')
    redeem_parser.add_argument('-c', help='Condition ID to redeem', required=True)
    redeem_parser.add_argument('-n', help='Number of outcomes', type=int, required=True)

    redeem_parser = sub_parser.add_parser('split', help='Split Shares')
    redeem_parser.add_argument('-c', help='Condition ID to redeem', required=True)
    redeem_parser.add_argument('-n', help='Number of outcomes', type=int, required=True)
    redeem_parser.add_argument('-a', help='Amount of collateral to split', type=float, required=True)

    redeem_parser = sub_parser.add_parser('merge', help='Merge Shares')
    redeem_parser.add_argument('-c', help='Condition ID to redeem', required=True)
    redeem_parser.add_argument('-n', help='Number of outcomes', type=int, required=True)
    redeem_parser.add_argument('-a', help='Amount of collateral to merge', type=float, required=True)

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

    elif args.subparser_name in ['redeem', 'split', 'merge']:
        try:
            condition_id = args.c
            num_outcomes = args.n
            amount = getattr(args, 'a', None)
        except AttributeError as e:
            logger.error(e)
            exit()

    gas_price = getattr(args, 'g', None)
    w3 = initialize_identity(gas_price)

    if args.subparser_name == 'buy':
        trx_hash = buy(w3, market, amount, index, slip_shares)

    elif args.subparser_name == 'sell':
        trx_hash = sell(w3, market, amount, index, slip_shares)

    elif args.subparser_name == 'redeem':
        trx_hash = redeem(w3, condition_id, num_outcomes)

    elif args.subparser_name == 'split':
        trx_hash = split(w3, condition_id, num_outcomes, amount)

    elif args.subparser_name == 'merge':
        trx_hash = merge(w3, condition_id, num_outcomes, amount)

    print(Web3.toHex(trx_hash))
