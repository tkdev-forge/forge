import argparse
import csv
import json
import logging
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
        self.deployer_private_key = os.getenv("DEPLOYER_PRIVATE_KEY")
        self.use_external_signer = os.getenv("DEPLOYER_USE_EXTERNAL_SIGNER", "false").lower() == "true"
        self.logger = logging.getLogger(__name__)

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

        if not abi or not bytecode or not isinstance(bytecode, str) or not bytecode.startswith("0x") or len(bytecode) <= 2:
            raise ValueError(f"Invalid artifact format for {contract_name}: missing abi/bytecode")

        return {"abi": abi, "bytecode": bytecode}

    def _validate_deployment_prerequisites(self) -> str:
        if not self.w3.is_connected():
            raise ConnectionError("RPC is not reachable: self.w3.is_connected() is False")

        if not Web3.is_address(self.deployer_address):
            raise ValueError("DEPLOYER_ADDRESS must be a valid Ethereum address")

        checksum_deployer = Web3.to_checksum_address(self.deployer_address)
        zero_address = "0x0000000000000000000000000000000000000000"

        if self.deployer_private_key:
            account = self.w3.eth.account.from_key(self.deployer_private_key)
            signer_address = Web3.to_checksum_address(account.address)
            if checksum_deployer != zero_address and checksum_deployer != signer_address:
                raise ValueError(
                    "DEPLOYER_ADDRESS does not match DEPLOYER_PRIVATE_KEY signer address "
                    f"({checksum_deployer} != {signer_address})"
                )
            return signer_address

        if self.use_external_signer:
            if checksum_deployer == zero_address:
                raise ValueError("DEPLOYER_ADDRESS must be set when DEPLOYER_USE_EXTERNAL_SIGNER=true")
            return checksum_deployer

        raise ValueError(
            "No signer configured. Set DEPLOYER_PRIVATE_KEY or DEPLOYER_USE_EXTERNAL_SIGNER=true"
        )

    def _next_tx_params(self, deployer: str, nonce: int) -> dict[str, Any]:
        latest_block = self.w3.eth.get_block("latest")
        tx_params: dict[str, Any] = {
            "from": deployer,
            "nonce": nonce,
            "chainId": self.w3.eth.chain_id,
        }

        if latest_block.get("baseFeePerGas") is not None:
            try:
                priority_fee = self.w3.eth.max_priority_fee
            except Exception:
                priority_fee = self.w3.to_wei(2, "gwei")
            tx_params["maxPriorityFeePerGas"] = priority_fee
            tx_params["maxFeePerGas"] = int(latest_block["baseFeePerGas"] + (priority_fee * 2))
        else:
            tx_params["gasPrice"] = self.w3.eth.gas_price

        return tx_params

    def _deploy_contract(
        self,
        contract_name: str,
        artifact: dict[str, Any],
        constructor_args: list[Any],
        deployer: str,
        nonce: int,
    ) -> tuple[str, str]:
        contract = self.w3.eth.contract(abi=artifact["abi"], bytecode=artifact["bytecode"])
        constructor = contract.constructor(*constructor_args)

        tx_params = self._next_tx_params(deployer, nonce)
        gas_estimate = constructor.estimate_gas({"from": deployer})
        tx_params["gas"] = int(gas_estimate * 1.2)

        if self.deployer_private_key:
            unsigned_tx = constructor.build_transaction(tx_params)
            signed_tx = self.w3.eth.account.sign_transaction(unsigned_tx, private_key=self.deployer_private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        else:
            tx_hash = constructor.transact(tx_params)

        tx_hash_hex = tx_hash.hex()
        self.logger.info("%s deployment txHash=%s", contract_name, tx_hash_hex)

        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status != 1 or not receipt.contractAddress:
            raise RuntimeError(f"{contract_name} deployment failed (tx={tx_hash_hex})")

        return Web3.to_checksum_address(receipt.contractAddress), tx_hash_hex

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
        signer_address = self._validate_deployment_prerequisites()
        profiles = self._load_profiles()
        if profile not in profiles:
            raise ValueError(f"Unknown profile: {profile}")

        contracts = ["ForgeREP", "ForgeDAO", "ForgePolicy"]
        addresses: dict[str, str] = {}
        tx_hashes: dict[str, str] = {}

        artifacts = {name: self._load_artifact(name) for name in contracts}

        nonce = self.w3.eth.get_transaction_count(signer_address, "pending")

        try:
            forge_rep, tx_hash = self._deploy_contract(
                contract_name="ForgeREP",
                artifact=artifacts["ForgeREP"],
                constructor_args=[],
                deployer=signer_address,
                nonce=nonce,
            )
            addresses["ForgeREP"] = forge_rep
            tx_hashes["ForgeREP"] = tx_hash
            nonce += 1

            forge_dao, tx_hash = self._deploy_contract(
                contract_name="ForgeDAO",
                artifact=artifacts["ForgeDAO"],
                constructor_args=[forge_rep],
                deployer=signer_address,
                nonce=nonce,
            )
            addresses["ForgeDAO"] = forge_dao
            tx_hashes["ForgeDAO"] = tx_hash
            nonce += 1

            forge_policy, tx_hash = self._deploy_contract(
                contract_name="ForgePolicy",
                artifact=artifacts["ForgePolicy"],
                constructor_args=[forge_dao],
                deployer=signer_address,
                nonce=nonce,
            )
            addresses["ForgePolicy"] = forge_policy
            tx_hashes["ForgePolicy"] = tx_hash
        except Exception:
            # Intentionally avoid writing partial contract state to config/onchain.json.
            raise

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
            "deployer": signer_address,
            "contracts": addresses,
            "tx_hashes": tx_hashes,
            "profile": profile,
            "profile_config": profiles[profile],
            "founders": founder_allocations,
            "rpc_connected": True,
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
