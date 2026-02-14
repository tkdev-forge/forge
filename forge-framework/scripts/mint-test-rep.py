#!/usr/bin/env python3
import os

from web3 import Web3


def main():
    rpc = os.getenv("ALCHEMY_RPC")
    rep = os.getenv("FORGEREP_ADDRESS")
    member = os.getenv("TEST_MEMBER")
    amount = int(os.getenv("TEST_REP_AMOUNT", "25"))

    w3 = Web3(Web3.HTTPProvider(rpc))
    print("Connected:", w3.is_connected())
    print(f"Would mint {amount} REP to {member} on {rep}")


if __name__ == "__main__":
    main()
