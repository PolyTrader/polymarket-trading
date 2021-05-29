import argparse

from web3 import Web3

from polymarket import buy, initialize_identity

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', help="Market Maker Address", required=True)
    parser.add_argument('-a', help="Amount to spend (USDC)", required=True)
    parser.add_argument('-i', help="Index of outcome choice", required=True)
    parser.add_argument('-n', help="Mininum number of shares expected (slippage)", required=True)

    args = parser.parse_args()
    market = args.m
    amount = args.a
    index = args.i
    minimum_shares = args.n

    w3 = initialize_identity()
    trx_hash = buy(w3, market, amount, index, minimum_shares)

    print(Web3.toHex(trx_hash))


if __name__ == "__main__":
    exit(main())
