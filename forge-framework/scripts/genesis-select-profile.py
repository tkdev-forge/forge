#!/usr/bin/env python3
import json
import os
from pathlib import Path

from web3 import Web3

PROFILE_FILE = Path(__file__).resolve().parent.parent / "config" / "domain-profiles.json"


def main():
    with open(PROFILE_FILE, "r", encoding="utf-8") as f:
        profiles = json.load(f)

    profile = input("Select profile (research/product/city): ").strip().lower()
    if profile not in profiles:
        raise SystemExit(f"Unknown profile: {profile}")

    rpc = os.getenv("ALCHEMY_RPC")
    policy_addr = os.getenv("FORGE_POLICY_ADDRESS")
    print(f"Applying profile={profile} to policy={policy_addr} via {rpc}")

    w3 = Web3(Web3.HTTPProvider(rpc))
    print("Connected:", w3.is_connected())
    print("Target params:", profiles[profile])
    print("TODO: call updateDecayRate/updateBooster/updateCommunityAvgWindow on ForgePolicy")


if __name__ == "__main__":
    main()
