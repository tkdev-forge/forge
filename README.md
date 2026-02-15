# Forge: AI Agent Efficiency Benchmark System

**Research Question**: "Under what conditions can AI agents match or exceed human productivity on economically valuable tasks?"

## ⚠️ IMPORTANT: Project Status

**This is a RESEARCH PROPOSAL and TECHNICAL DESIGN.**

🚧 **The experiment has NOT YET BEEN RUN.** 🚧

All "results" shown below are **projected outcomes** based on our hypothesis.
No empirical data exists yet.

- ✅ **Available**: Research design, technical architecture, code templates
- ❌ **NOT Available**: Running system, empirical data, validated results

**Timeline**:
- Design Phase: ✅ Complete (Feb 2026)
- Implementation: 🚧 In Progress (~20%)
- Pilot Experiment: ⏳ Planned (April 2026)

See [PROJECT-STATUS.md](PROJECT-STATUS.md) for detailed status.

---

## 🎯 Overview

Forge is a proposed proof-of-concept system for measuring AI agent efficiency on real-world tasks:

- Uses RLI (Remote Labor Index) for objective quality measurement
- Tests hypothesis: Economic incentives → 3x faster learning
- Compares agents with REP system vs isolated agents vs humans
- Measures automation rate, cost efficiency, and learning curves

**Key Innovation**: Embedding agents in a closed economic system with real stakes (REP decay), real rewards (task revenue), and objective evaluation (RLI human judges).

## 🧪 Experimental Design

### Groups
- **Control Group**: 5-25 isolated agents (no economic system)
- **Treatment Group**: 5-25 agents with full Forge (REP + M2M + RLI)
- **Human Baseline**: 10-50 professional freelancers

### Task Pool
- **Source**: RLI (Remote Labor Index) - 240 real freelance tasks
- **Categories**: 23 types (web-dev, 3d-rendering, data-viz, etc.)
- **Total Value**: $140k+
- **Primary Metric**: Automation Rate (% human-level quality)

### Hypothesis

**H1**: Agents with economic incentives reach ≥60% automation by Month 6  
**H2**: Forge agents improve 3x faster than isolated agents  
**H3**: Economic pressure drives specialization (Gini >0.5)  
**H4**: Multi-agent teams outperform solo agents on complex tasks  

See [Research Hypothesis](docs/research/hypothesis.md) for details.

## 📊 Expected Results (Projected)

⚠️ **IMPORTANT**: These are **theoretical projections** if our hypothesis is correct. 
**NO experiment has been run yet. NO data exists.**

| Metric | Control | Forge (Treatment) | Human | Target | Status |
|--------|---------|-------------------|-------|--------|--------|
| Automation Rate | 35% | 58% | 100% | ≥50% | 🔮 Projected |
| Cost/Task | $8.50 | $10.20 | $150 | <$15 | 🔮 Projected |
| Learning Rate | +1.5%/100 | +4.5%/100 | N/A | 3x | 🔮 Projected |
| ROI | 1.2x | 8.5x | 0.8x | >5x | 🔮 Projected |

**Legend**:
- 🔮 **Projected**: Theoretical prediction (not measured)
- ✅ **Achieved**: Actually measured and validated (none yet)

**These numbers are based on**:
- RLI paper showing 87.5% gap between benchmark and real-world performance
- Economic theory suggesting incentives improve outcomes by 30-50%
- Red Queen dynamics showing continuous improvement under competition

**When will real data exist?** April 2026 at earliest (if pilot starts on time)

## 🚀 Quick Start (For Developers)

⚠️ **Note**: System not fully implemented yet. These commands will be functional after Phase 2 completion (March 2026).

```bash
# Clone repository
git clone https://github.com/tkdev-forge/forge.git
cd forge

# Deploy minimal PoC (when implementation complete)
docker-compose -f docker/docker-compose.poc.yml up -d

# Run 3-month pilot experiment (when deployed)
cd experiments/pilot-3month
python ../../scripts/run-experiment.py --config config.yaml

# View results dashboard (when experiment running)
open http://localhost:8080
```

**Current Status**: Infrastructure templates exist, core logic ~20% implemented.

## 📚 Documentation

### Research Documentation
- [Research Hypothesis](docs/research/hypothesis.md) - Testable predictions (not results)
- [Experimental Design](docs/research/experimental-design.md) - How we will test
- [Measurement Metrics](docs/research/metrics.md) - What we will measure
- [Project Status](PROJECT-STATUS.md) - Detailed phase tracking ⭐

### Technical Documentation
- [Architecture Overview](docs/architecture/forge-poc-overview.md) - System design
- [RLI Integration](docs/architecture/rli-integration.md) - Quality measurement
- [CHANGELOG](CHANGELOG.md) - Actual code changes

## 🏗️ Architecture

Forge is designed as a **multi-layer measurement system**:

```
Layer 1 (Access):      Entry barriers → Measure qualification thresholds
Layer 2 (Agents):      Task execution → Measure time, cost, retries
Layer 4 (M2M Economy): Markets → Measure price discovery, efficiency
Layer 6 (Reputation):  REP system → Measure skill progression
Layer 6.1 (RLI):       Quality oracle → Measure automation rate ⭐
Layer 9 (Monitoring):  Failure detection → Measure system reliability
```

**Key Component**: RLI Oracle provides objective quality measurement via human evaluation ($2.34/task, 11-17 min)

## 📅 Timeline

| Phase | Status | Start | End | Deliverable |
|-------|--------|-------|-----|-------------|
| **Research Design** | ✅ Complete | Jan 2026 | Feb 2026 | Hypothesis & Protocol |
| **Implementation** | 🚧 20% Done | Feb 2026 | Mar 2026 | Working PoC |
| **3-Month Pilot** | ⏳ Planned | Apr 2026 | Jun 2026 | Initial Data |
| **Full 12-Month Study** | ⏳ Planned | Jul 2026 | Jun 2027 | Final Results |

**Next Milestone**: Complete implementation by March 31, 2026

## 💰 Budget & Funding

### Pilot (3 months) - $17,000 needed
- RLI Evaluations: $2,340
- Compute: $5,000
- Human Baseline: $7,500
- Infrastructure: $2,000
- **Status**: Seeking funding ❌

### Full Study (12 months) - ~$85,000 needed
- **Status**: Contingent on pilot success ❌

## 📖 Citation

⚠️ **Important**: This project has not produced empirical results yet. 

**Acceptable Citations**:
```bibtex
@misc{forge2026proposal,
  title={Forge: A Proposed Framework for Measuring AI Agent Efficiency},
  author={[Your Name]},
  howpublished={GitHub Repository},
  year={2026},
  note={Research proposal - no empirical data yet}
}
```

**NOT Acceptable**: Citing projected results as actual measurements.

## 🤝 Contributing

We welcome:
- **Researchers**: Review experimental design, suggest metrics
- **Developers**: Implement measurement infrastructure
- **Partners**: RLI Platform access, funding opportunities
- **Evaluators**: Human baseline data collection (future)

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Priority Areas
1. Complete `ForgeREP_RLI.sol` implementation
2. Build `efficiency_tracker.py` core logic
3. Secure RLI Platform API access
4. Docker deployment testing
5. Database schema implementation

## 🔗 Related Work

- [RLI Paper (arxiv.org/abs/2510.26787)](https://arxiv.org/abs/2510.26787) - Remote Labor Index benchmark
- [SWE-bench](https://www.swebench.com/) - GitHub issue resolution benchmark
- [HumanEval](https://github.com/openai/human-eval) - Code generation benchmark

**Key Difference**: Forge measures real-world economic efficiency with closed-loop feedback, not just accuracy on static benchmarks.

## ⚠️ Transparency & Limitations

### What This Repository Is:
- ✅ Rigorous research proposal with testable hypotheses
- ✅ Technical architecture for measurement system
- ✅ Theoretical projections based on existing research
- ✅ Partial code implementation (~20% done)

### What This Repository Is NOT:
- ❌ Running experiment with live agents
- ❌ Empirical validation of claims
- ❌ Peer-reviewed publication
- ❌ Production-ready system
- ❌ Evidence that agents can match humans (untested)

### Academic Integrity:
We commit to:
1. Pre-registering hypotheses before data collection
2. Publishing all data openly
3. Clearly marking projections vs measurements
4. Honest reporting of null results
5. Full reproducibility documentation

## 📧 Contact

- **Research Design**: [Research Lead Email]
- **Implementation**: [Dev Lead Email]
- **Partnerships**: [PI Email]
- **Issues/Questions**: [GitHub Issues](https://github.com/tkdev-forge/forge/issues)

## 📄 License

MIT License - See [LICENSE](LICENSE) for details

Research data (when it exists) will be released under CC BY 4.0

---

**Last Updated**: February 15, 2026  
**Repository Status**: Pre-deployment (Phase 2 of 4)  
**Next Update**: Weekly progress in [PROJECT-STATUS.md](PROJECT-STATUS.md)
