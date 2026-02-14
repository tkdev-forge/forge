"""RLI Platform API Client.

Wrapper for interacting with the RLI evaluation platform.
"""

import aiohttp
import asyncio
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class RLITask:
    """Represents an RLI benchmark task."""
    task_id: int
    category: str
    brief: str
    human_deliverable: str  # Path or URL
    economic_value: float  # USD
    avg_completion_time_minutes: int


@dataclass
class RLIComparison:
    """Represents a comparison between AI and human deliverables."""
    comparison_id: str
    task_id: int
    ai_deliverable: str
    human_baseline: str
    status: str  # 'pending', 'in_progress', 'completed'
    created_at: datetime
    completed_at: Optional[datetime] = None
    automation_rate: Optional[float] = None
    elo_score: Optional[int] = None
    evaluator_count: int = 0


class RLIPlatformClient:
    """Client for RLI evaluation platform API."""
    
    def __init__(self, platform_url: str, api_token: str):
        self.platform_url = platform_url.rstrip('/')
        self.api_token = api_token
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={'Authorization': f'Bearer {self.api_token}'}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_random_benchmark_task(self, category: str) -> RLITask:
        """Fetch a random benchmark task from specified category.
        
        Args:
            category: Task category (e.g., 'web-development', '3d-rendering')
            
        Returns:
            RLITask object with benchmark details
        """
        async with self.session.get(
            f"{self.platform_url}/api/benchmarks/random",
            params={'category': category}
        ) as response:
            response.raise_for_status()
            data = await response.json()
            
            return RLITask(
                task_id=data['task_id'],
                category=data['category'],
                brief=data['brief'],
                human_deliverable=data['human_deliverable'],
                economic_value=data['economic_value'],
                avg_completion_time_minutes=data['avg_completion_time_minutes']
            )
    
    async def create_comparison(
        self,
        ai_deliverable_path: str,
        human_baseline: str,
        task_brief: str,
        task_category: str,
        required_evaluators: int = 3
    ) -> str:
        """Submit a new comparison for evaluation.
        
        Args:
            ai_deliverable_path: Local path to AI-generated deliverable
            human_baseline: Reference to human baseline deliverable
            task_brief: Task description
            task_category: Category of the task
            required_evaluators: Number of human evaluators required
            
        Returns:
            Comparison ID for tracking
        """
        # Upload AI deliverable
        with open(ai_deliverable_path, 'rb') as f:
            data = aiohttp.FormData()
            data.add_field('ai_deliverable', f, filename=ai_deliverable_path.split('/')[-1])
            data.add_field('human_baseline', human_baseline)
            data.add_field('task_brief', task_brief)
            data.add_field('category', task_category)
            data.add_field('required_completions', str(required_evaluators))
            
            async with self.session.post(
                f"{self.platform_url}/api/comparisons/create",
                data=data
            ) as response:
                response.raise_for_status()
                result = await response.json()
                return result['comparison_id']
    
    async def get_comparison_status(self, comparison_id: str) -> RLIComparison:
        """Get status and results of a comparison.
        
        Args:
            comparison_id: ID returned from create_comparison
            
        Returns:
            RLIComparison object with current status and results
        """
        async with self.session.get(
            f"{self.platform_url}/api/comparisons/{comparison_id}/status"
        ) as response:
            response.raise_for_status()
            data = await response.json()
            
            return RLIComparison(
                comparison_id=comparison_id,
                task_id=data['task_id'],
                ai_deliverable=data['ai_deliverable'],
                human_baseline=data['human_baseline'],
                status=data['status'],
                created_at=datetime.fromisoformat(data['created_at']),
                completed_at=datetime.fromisoformat(data['completed_at']) if data.get('completed_at') else None,
                automation_rate=data.get('automation_rate'),
                elo_score=data.get('elo_score'),
                evaluator_count=data.get('evaluator_count', 0)
            )
    
    async def poll_for_completion(
        self,
        comparison_id: str,
        timeout_seconds: int = 3600,
        poll_interval: int = 30
    ) -> RLIComparison:
        """Poll for comparison completion with timeout.
        
        Args:
            comparison_id: ID to poll
            timeout_seconds: Maximum wait time (default 1 hour)
            poll_interval: Seconds between polls (default 30s)
            
        Returns:
            Completed RLIComparison object
            
        Raises:
            TimeoutError: If evaluation doesn't complete within timeout
        """
        start_time = datetime.now()
        
        while (datetime.now() - start_time).seconds < timeout_seconds:
            comparison = await self.get_comparison_status(comparison_id)
            
            if comparison.status == 'completed':
                return comparison
            
            await asyncio.sleep(poll_interval)
        
        raise TimeoutError(
            f"RLI evaluation timeout for comparison {comparison_id}. "
            f"Typical evaluation time: 11-17 minutes."
        )
    
    async def list_categories(self) -> Dict[str, dict]:
        """List available task categories.
        
        Returns:
            Dictionary of category metadata
        """
        async with self.session.get(
            f"{self.platform_url}/api/categories"
        ) as response:
            response.raise_for_status()
            return await response.json()
