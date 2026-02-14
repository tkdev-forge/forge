"""RLI (Remote Labor Index) Integration for Forge Reputation Layer.

This module provides oracle functionality for connecting Forge's reputation
system with the RLI evaluation platform for objective performance measurement.
"""

from .rli_oracle import RLIPerformanceOracle
from .rli_client import RLIPlatformClient

__all__ = ['RLIPerformanceOracle', 'RLIPlatformClient']
__version__ = '0.1.0'
