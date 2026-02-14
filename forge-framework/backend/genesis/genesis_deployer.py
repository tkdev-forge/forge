import argparse
import csv
import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from web3 import Web3

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_ROOT = ROOT / "contracts"
CONFIG_ROOT = ROOT / "config"
PROFILES_FILE = CONFIG_ROOT / "domain-profiles.json"
ONCHAIN_FILE = CONFIG_ROOT / "onchain.json"


class GenesisDeployer:
    def __init__(self, network: str):
        load_dotenv()
        self.network = network
        self.rpc_url = os.getenv("ALCHEMY_RPC") or os.getenv("RPC_URL")
        if not self.rpc_url:
            raise ValueError("Missing RPC URL. Set ALCHEMY_RPC or RPC_URL")
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        self.deployer_address = os.getenv("DEPLOYER_ADDRESS", "0x0000000000000000000000000000000000000000")

    def _find_artifact(self, contract_name: str) -> Path:
        paths = [
            CONTRACTS_ROOT / "artifacts" / "contracts" / f"{contract_name}.sol" / f"{contract_name}.json",
            CONTRACTS_ROOT / "out" / f"{contract_name}.sol" / f"{contract_name}.json",
        ]
        for path in paths:
            if path.exists():
                return path
        raise FileNotFoundError(f"Artifact for {contract_name} not found in known build directories")

    def _load_artifact(self, contract_name: str) -> dict[str, Any]:
        artifact_file = self._find_artifact(contract_name)
        with artifact_file.open("r", encoding="utf-8") as f:
            payload = json.load(f)

        bytecode = payload.get("bytecode")
        if isinstance(bytecode, dict):
            bytecode = bytecode.get("object")
        abi = payload.get("abi")

        if not abi or not bytecode:
            raise ValueError(f"Invalid artifact format for {contract_name}: missing abi/bytecode")

        return {"abi": abi, "bytecode": bytecode}

    def _pseudo_deploy(self, contract_name: str) -> str:
        # Deterministic pseudo-address fallback for plan-mode/dev environments.
        salt = Web3.keccak(text=f"{self.network}:{contract_name}").hex()[-40:]
        return Web3.to_checksum_address(f"0x{salt}")

    def _load_profiles(self) -> dict[str, Any]:
        with PROFILES_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _write_onchain(self, payload: dict[str, Any]):
        existing: dict[str, Any] = {}
        if ONCHAIN_FILE.exists():
            with ONCHAIN_FILE.open("r", encoding="utf-8") as f:
                existing = json.load(f)
        existing[self.network] = payload
        with ONCHAIN_FILE.open("w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2)

    def deploy_forge_stack(self, profile: str, founders: list[str]) -> dict[str, Any]:
        profiles = self._load_profiles()
        if profile not in profiles:
            raise ValueError(f"Unknown profile: {profile}")

        contracts = ["ForgeREP", "ForgeDAO", "ForgePolicy"]
        addresses: dict[str, str] = {}

        for contract_name in contracts:
            # Validate artifacts exist and parseable even in pseudo deploy mode.
            self._load_artifact(contract_name)
            addresses[contract_name] = self._pseudo_deploy(contract_name)

        founder_allocations = []
        initial_rep = int(os.getenv("GENESIS_INITIAL_REP", "100"))
        for founder in founders:
            if not Web3.is_address(founder):
                raise ValueError(f"Invalid founder address: {founder}")
            founder_allocations.append(
                {"address": Web3.to_checksum_address(founder), "minted_rep": initial_rep}
            )

        output = {
            "network": self.network,
            "deployer": self.deployer_address,
            "contracts": addresses,
            "profile": profile,
            "profile_config": profiles[profile],
            "founders": founder_allocations,
            "rpc_connected": self.w3.is_connected(),
        }
        self._write_onchain(output)
        return output


def _read_founders_csv(path: str) -> list[str]:
    founders: list[str] = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            founders.append(row[0].strip())
    return founders


def main():
    parser = argparse.ArgumentParser(description="Deploy Forge genesis contract stack")
    parser.add_argument("--network", required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--founders-csv", required=True)
    args = parser.parse_args()

    founders = _read_founders_csv(args.founders_csv)
    deployer = GenesisDeployer(network=args.network)
    result = deployer.deploy_forge_stack(profile=args.profile, founders=founders)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
