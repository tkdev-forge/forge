"""RLI Performance Oracle - Chainlink External Adapter.

Connects Forge reputation system with RLI evaluation platform
for objective AI agent performance measurement.
"""

import asyncio
import os
import json
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import aiohttp
from aiohttp import web
from web3 import Web3
from eth_account import Account
import logging

from .rli_client import RLIPlatformClient, RLIComparison

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class RLITaskResult:
    """Result from RLI evaluation."""
    task_id: int
    automation_rate: float  # 0.0 - 1.0
    elo_score: int
    economic_value: float  # USD
    task_category: str
    comparison_url: str
    evaluation_timestamp: datetime


class RLIPerformanceOracle:
    """Chainlink External Adapter for RLI Platform Integration.
    
    This oracle bridges Forge's on-chain reputation system with the
    RLI evaluation platform for objective performance measurement.
    
    Architecture:
    1. Forge contract calls requestRLIEvaluation()
    2. Chainlink node routes request to this adapter
    3. Adapter downloads deliverable from IPFS
    4. Submits to RLI platform for human evaluation
    5. Polls for results (11-17 min typical)
    6. Submits result back to chain via fulfillRLIEvaluation()
    """
    
    def __init__(
        self,
        rli_platform_url: str,
        rli_admin_token: str,
        forge_contract_address: str,
        web3_provider_url: str,
        oracle_private_key: str,
        ipfs_gateway: str = "https://ipfs.io/ipfs/"
    ):
        self.rli_platform_url = rli_platform_url
        self.rli_token = rli_admin_token
        self.forge_contract_address = forge_contract_address
        self.ipfs_gateway = ipfs_gateway
        
        # Web3 setup
        self.web3 = Web3(Web3.HTTPProvider(web3_provider_url))
        self.account = Account.from_key(oracle_private_key)
        
        # Load contract ABI
        self.contract = self._load_contract()
        
        # Pending evaluations queue
        self.pending_evaluations: Dict[str, dict] = {}
        
        logger.info(f"RLI Oracle initialized for contract: {forge_contract_address}")
        logger.info(f"Oracle address: {self.account.address}")
    
    def _load_contract(self):
        """Load ForgeREP_RLI contract ABI and create Web3 contract instance."""
        try:
            abi_path = os.path.join(
                os.path.dirname(__file__),
                '../../../../contracts/artifacts/ForgeREP_RLI.json'
            )
            
            with open(abi_path, 'r') as f:
                contract_json = json.load(f)
                abi = contract_json['abi']
            
            return self.web3.eth.contract(
                address=Web3.to_checksum_address(self.forge_contract_address),
                abi=abi
            )
        except Exception as e:
            logger.warning(f"Could not load contract ABI: {e}. Using minimal ABI.")
            # Fallback minimal ABI for fulfillRLIEvaluation
            minimal_abi = [{
                "inputs": [
                    {"name": "_requestId", "type": "bytes32"},
                    {"name": "member", "type": "address"},
                    {"name": "taskId", "type": "uint256"},
                    {"name": "automationRate", "type": "uint256"},
                    {"name": "eloScore", "type": "uint256"},
                    {"name": "economicValue", "type": "uint256"},
                    {"name": "taskCategory", "type": "string"}
                ],
                "name": "fulfillRLIEvaluation",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            }]
            
            return self.web3.eth.contract(
                address=Web3.to_checksum_address(self.forge_contract_address),
                abi=minimal_abi
            )
    
    async def handle_evaluation_request(
        self,
        request_id: str,
        member_address: str,
        task_id: int,
        task_category: str,
        deliverable_ipfs_hash: str
    ) -> RLITaskResult:
        """Main handler for Chainlink evaluation requests.
        
        Flow:
        1. Download deliverable from IPFS
        2. Get benchmark task from RLI platform
        3. Create comparison
        4. Wait for human evaluation
        5. Return result
        
        Args:
            request_id: Chainlink request ID
            member_address: Ethereum address of member being evaluated
            task_id: Unique task identifier
            task_category: Category (e.g., 'web-development')
            deliverable_ipfs_hash: IPFS hash of AI deliverable
            
        Returns:
            RLITaskResult with evaluation metrics
        """
        logger.info(f"[RLI] Processing request {request_id} for {member_address}")
        
        try:
            # 1. Download deliverable from IPFS
            logger.info(f"[RLI] Downloading deliverable from IPFS: {deliverable_ipfs_hash}")
            deliverable_path = await self._download_from_ipfs(deliverable_ipfs_hash)
            
            # 2. Get benchmark task
            logger.info(f"[RLI] Fetching benchmark task (category: {task_category})")
            async with RLIPlatformClient(self.rli_platform_url, self.rli_token) as client:
                benchmark_task = await client.get_random_benchmark_task(task_category)
                
                # 3. Submit comparison
                logger.info(f"[RLI] Creating comparison with task {benchmark_task.task_id}")
                comparison_id = await client.create_comparison(
                    ai_deliverable_path=deliverable_path,
                    human_baseline=benchmark_task.human_deliverable,
                    task_brief=benchmark_task.brief,
                    task_category=task_category
                )
                
                logger.info(f"[RLI] Comparison created: {comparison_id}. Waiting for evaluation...")
                
                # 4. Wait for evaluation (11-17 min typical)
                comparison = await client.poll_for_completion(
                    comparison_id,
                    timeout_seconds=3600  # 1 hour max
                )
            
            # 5. Convert to result format
            result = RLITaskResult(
                task_id=task_id,
                automation_rate=comparison.automation_rate,
                elo_score=comparison.elo_score,
                economic_value=benchmark_task.economic_value,
                task_category=task_category,
                comparison_url=f"{self.rli_platform_url}/comparisons/{comparison_id}",
                evaluation_timestamp=comparison.completed_at
            )
            
            logger.info(
                f"[RLI] Evaluation complete: {result.automation_rate:.1%} automation, "
                f"Elo {result.elo_score}"
            )
            
            # Store for blockchain submission
            self.pending_evaluations[request_id] = {
                'member': member_address,
                'task_id': task_id,
                'result': result
            }
            
            return result
            
        except Exception as e:
            logger.error(f"[RLI] Error processing request {request_id}: {e}")
            raise
    
    async def _download_from_ipfs(self, ipfs_hash: str) -> str:
        """Download deliverable from IPFS gateway.
        
        Args:
            ipfs_hash: IPFS content hash
            
        Returns:
            Local path to downloaded file
        """
        ipfs_url = f"{self.ipfs_gateway}{ipfs_hash}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(ipfs_url) as response:
                if response.status != 200:
                    raise Exception(f"IPFS download failed: HTTP {response.status}")
                
                content = await response.read()
                
                # Save to temp directory
                temp_dir = "/tmp/rli_deliverables"
                os.makedirs(temp_dir, exist_ok=True)
                temp_path = os.path.join(temp_dir, ipfs_hash)
                
                with open(temp_path, 'wb') as f:
                    f.write(content)
                
                logger.info(f"[RLI] Downloaded {len(content)} bytes to {temp_path}")
                return temp_path
    
    async def submit_to_blockchain(self, request_id: str) -> dict:
        """Submit evaluation result to ForgeREP_RLI contract.
        
        Fulfills the Chainlink request with evaluation data.
        
        Args:
            request_id: Chainlink request ID (bytes32)
            
        Returns:
            Transaction receipt
        """
        if request_id not in self.pending_evaluations:
            raise ValueError(f"No pending evaluation for request {request_id}")
        
        eval_data = self.pending_evaluations[request_id]
        result = eval_data['result']
        
        logger.info(f"[RLI] Submitting result to blockchain for request {request_id}")
        
        # Convert request_id to bytes32
        request_id_bytes = bytes.fromhex(request_id.replace('0x', ''))
        
        # Prepare transaction
        tx = self.contract.functions.fulfillRLIEvaluation(
            request_id_bytes,
            Web3.to_checksum_address(eval_data['member']),
            eval_data['task_id'],
            int(result.automation_rate * 10000),  # Convert to basis points
            result.elo_score,
            int(result.economic_value * 100),  # Convert to cents
            result.task_category
        ).build_transaction({
            'from': self.account.address,
            'gas': 500000,
            'gasPrice': self.web3.eth.gas_price,
            'nonce': self.web3.eth.get_transaction_count(self.account.address)
        })
        
        # Sign and send
        signed_tx = self.web3.eth.account.sign_transaction(tx, self.account.key)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        logger.info(f"[RLI] Transaction sent: {tx_hash.hex()}")
        
        # Wait for confirmation
        receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        
        logger.info(
            f"[RLI] Transaction confirmed in block {receipt['blockNumber']}, "
            f"gas used: {receipt['gasUsed']}"
        )
        
        # Clean up
        del self.pending_evaluations[request_id]
        
        return receipt
    
    async def run_oracle_server(self, host: str = '0.0.0.0', port: int = 6688):
        """Run HTTP server for Chainlink External Adapter.
        
        Chainlink node sends POST requests to this endpoint with job data.
        
        Args:
            host: Listen address
            port: Listen port (default 6688)
        """
        
        async def handle_request(request: web.Request) -> web.Response:
            """Handle incoming Chainlink request."""
            try:
                data = await request.json()
                
                # Extract Chainlink request data
                job_run_id = data['id']
                params = data['data']
                
                logger.info(f"[RLI] Received Chainlink request: {job_run_id}")
                
                # Process evaluation
                result = await self.handle_evaluation_request(
                    request_id=job_run_id,
                    member_address=params['member'],
                    task_id=int(params['taskId']),
                    task_category=params['category'],
                    deliverable_ipfs_hash=params['deliverable']
                )
                
                # Submit to blockchain
                receipt = await self.submit_to_blockchain(job_run_id)
                
                # Return success to Chainlink node
                return web.json_response({
                    'jobRunID': job_run_id,
                    'data': {
                        'automation_rate': result.automation_rate,
                        'elo_score': result.elo_score,
                        'economic_value': result.economic_value,
                        'transaction_hash': receipt['transactionHash'].hex()
                    },
                    'statusCode': 200
                })
            
            except Exception as e:
                logger.error(f"[RLI] Error processing request: {e}", exc_info=True)
                return web.json_response({
                    'jobRunID': data.get('id', 'unknown'),
                    'status': 'errored',
                    'error': str(e),
                    'statusCode': 500
                })
        
        # Health check endpoint
        async def health_check(request: web.Request) -> web.Response:
            return web.json_response({
                'status': 'healthy',
                'oracle_address': self.account.address,
                'pending_evaluations': len(self.pending_evaluations)
            })
        
        # Create app
        app = web.Application()
        app.router.add_post('/', handle_request)
        app.router.add_get('/health', health_check)
        
        # Start server
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        
        logger.info(f"[RLI] Oracle server running on {host}:{port}")
        logger.info(f"[RLI] Health check: http://{host}:{port}/health")
        
        await site.start()
        
        # Keep running
        await asyncio.Event().wait()


async def main():
    """Main entry point for RLI Oracle server."""
    
    # Load configuration from environment
    config = {
        'rli_platform_url': os.getenv('RLI_PLATFORM_URL', 'https://rli-eval.forge.network'),
        'rli_admin_token': os.getenv('RLI_ADMIN_TOKEN'),
        'forge_contract_address': os.getenv('FORGE_REP_RLI_CONTRACT'),
        'web3_provider_url': os.getenv('WEB3_PROVIDER_URL', 'http://localhost:8545'),
        'oracle_private_key': os.getenv('ORACLE_PRIVATE_KEY'),
        'server_port': int(os.getenv('ORACLE_PORT', '6688'))
    }
    
    # Validate config
    required_keys = ['rli_admin_token', 'forge_contract_address', 'oracle_private_key']
    missing = [k for k in required_keys if not config[k]]
    
    if missing:
        logger.error(f"Missing required environment variables: {', '.join(missing.upper())}")
        return
    
    # Create and run oracle
    oracle = RLIPerformanceOracle(
        rli_platform_url=config['rli_platform_url'],
        rli_admin_token=config['rli_admin_token'],
        forge_contract_address=config['forge_contract_address'],
        web3_provider_url=config['web3_provider_url'],
        oracle_private_key=config['oracle_private_key']
    )
    
    await oracle.run_oracle_server(port=config['server_port'])


if __name__ == '__main__':
    asyncio.run(main())
