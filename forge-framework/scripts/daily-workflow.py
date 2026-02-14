#!/usr/bin/env python3
from backend.agents.trendscraper import TrendScraperAgent
from backend.agents.builderagent import BuilderAgent
from backend.agents.humanloop import HumanLoopAgent


def main():
    trends = TrendScraperAgent().fetch_trends()
    print("Trends:", trends)

    top = trends[0]
    build_prompt = f"Build lightweight MVP for trend: {top}"
    artifact = BuilderAgent().build_spa(build_prompt)
    print("Build candidate:", artifact)

    approved = HumanLoopAgent().parse_reply("YES")
    print("Human approval:", approved)

    if approved:
        print("Trigger RLI evaluation request for generated deliverable (stub).")


if __name__ == "__main__":
    main()
