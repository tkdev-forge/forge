#!/usr/bin/env python3

AGENTS = ["orchestrator", "voter", "trader", "auditor", "monitor", "recruiter"]


def main():
    for a in AGENTS:
        print(f"Spawned {a} agent")


if __name__ == "__main__":
    main()
