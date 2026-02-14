import os

from web3 import Web3


def get_web3() -> Web3:
    rpc = os.getenv("ALCHEMY_RPC", "http://localhost:8545")
    return Web3(Web3.HTTPProvider(rpc))
