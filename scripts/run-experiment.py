#!/usr/bin/env python3
"""Forge Experiment Runner."""

import argparse
import asyncio
from pathlib import Path
import yaml


def load_config(path: Path):
    with path.open() as f:
        return yaml.safe_load(f)


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="experiments/pilot-3month/config.yaml")
    args = parser.parse_args()

    config = load_config(Path(args.config))
    print(f"Starting experiment: {config['experiment']['name']}")
    print(f"Duration: {config['experiment']['duration_months']} months")
    print(f"Control agents: {config['groups']['control']['size']}")
    print(f"Treatment agents: {config['groups']['treatment']['size']}")
    await asyncio.sleep(0.1)
    print("Experiment scaffold initialized. Implement group execution pipeline next.")


if __name__ == "__main__":
    asyncio.run(main())
