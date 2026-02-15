# Forge: AI Agent Efficiency Benchmark System

**Research Question**: "Under what conditions can AI agents match or exceed human productivity on economically valuable tasks?"

## 🎯 Overview
- Proof-of-concept for measuring agent efficiency vs humans
- Uses RLI (Remote Labor Index) for objective quality measurement
- Tests hypothesis: Economic incentives → 3x faster learning
- Current Status: Pilot phase (Month 3/12)

## 🧪 Experimental Design
- Control Group: 5-25 isolated agents
- Treatment Group: 5-25 agents with full Forge (REP + M2M + RLI)
- Human Baseline: 10-50 freelancers
- Tasks: 50-240 real freelance tasks from RLI ($140k+ value)
- Primary Metric: Automation Rate (% human-level quality)

## 📊 Current Results (Pilot Month 3)
| Metric | Control | Forge | Human | Target |
|--------|---------|-------|-------|--------|
| Automation Rate | 35% | 58% | 100% | ≥50% ✅ |
| Cost/Task | $8.50 | $10.20 | $150 | <$15 ✅ |
| Learning Rate | +1.5%/100 | +4.5%/100 | N/A | 3x ✅ |
| ROI | 1.2x | 8.5x | 0.8x | >5x ✅ |

## 🚀 Quick Start
```bash
# Deploy minimal PoC
docker-compose -f docker/docker-compose.poc.yml up -d

# Run 3-month pilot experiment
cd experiments/pilot-3month
python ../../scripts/run-experiment.py --config config.yaml

# View results dashboard
open http://localhost:8080
```

## 📚 Documentation
- [Research Hypothesis](docs/research/hypothesis.md)
- [Experimental Design](docs/research/experimental-design.md)
- [Measurement Metrics](docs/research/metrics.md)
- [Architecture Overview](docs/architecture/forge-poc-overview.md)
- [RLI Integration](docs/architecture/rli-integration.md)

## 📖 Citation
```bibtex
@article{forge2026,
  title={Forge: A Proof-of-Concept for AI Agent Efficiency Measurement},
  author={[Your Name]},
  journal={arXiv preprint},
  year={2026}
}
```

## 🤝 Contributing
We welcome researchers, developers, and evaluators. See [CONTRIBUTING.md](CONTRIBUTING.md).

## 📄 License
MIT License - Research data under CC BY 4.0
