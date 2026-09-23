# quilt-multi-oracle

> **Multi-model JEV oracle.**
> Probes canon lores across N LLM workers in parallel. Aggregates via
> the canonical chord (canon_gate_is_chord doctrine).

## TL;DR

```python
from quilt_multi_oracle.workers import ZAIWorker, DeepSeekWorker, GeminiWorker
from quilt_multi_oracle.oracle import MultiOracle

oracle = MultiOracle(workers=[
    ZAIWorker(),
    DeepSeekWorker(),
    GeminiWorker(),
])

result = oracle.probe("A scar does not bar entry. The substrate walks.")
print(result["composite"])  # the chord's mean
print(result["consensus_promoted"])  # all workers agree
print(result["majority_promoted"])  # majority promote
print(result["per_worker"])  # per-worker breakdown
```

## What this is

The canon gate is a chord. This module runs the chord.

Multiple LLMs (ZAI, DeepSeek, Gemini, DeepInfra) probe the same lore in
parallel. The chord aggregates their scores:

- **composite** — mean across all workers
- **consensus_promoted** — TRUE if ALL workers promote
- **majority_promoted** — TRUE if majority promote
- **variance** — how much the workers disagreed
- **per_worker** — the breakdown

This is the substrate walker canon discovery's load-bearing insight:
**the canon gate is not a single test, it's a chord of voices**.

## Quick start

```bash
# Set env vars (any subset will work)
export ZAI_TOKEN=...
export DEEPSEEK_TOKEN=...
export DEEPINFRA_TOKEN=...
export GEMINI_TOKEN=...

# Run tests
PYTHONPATH=. python3 -m unittest discover -s tests -v

# Run play-test
PYTHONPATH=. python3 demos/demo_playtest.py
```

## Architecture

```
lore → MultiOracle.probe()
          ↓ (parallel)
      ┌─────────┬─────────┬─────────┐
      │  ZAI    │  DeepS  │  Gemini │
      │ GLM-4.5 │  chat   │  2.5-fl │
      └────┬────┴────┬────┴────┬────┘
           ↓         ↓         ↓
         score    score    score
           ↓         ↓         ↓
       aggregate_chord()
           ↓
       {composite, consensus, majority, variance, per_worker}
```

## The polyformalism doctrine

Same canon, many workers. The substrate walker doesn't care which LLM
probes the lore — what matters is that the JEV-schema contract is filled.
The chord hears all voices.

## Layered navigation

| Layer | Where |
|---|---|
| **CANON.md** | [CANON.md](CANON.md) — what this repo is, in 24 lines |
| **README** | [README.md](README.md) — quick start, navigation |
| **Chord** | [docs/ORACLE_CHORD.md](docs/ORACLE_CHORD.md) — chord semantics |
| **Source** | [quilt_multi_oracle/](quilt_multi_oracle/) — `workers.py`, `oracle.py` |
| **Demos** | [demos/](demos/) — play-test scripts |
| **Tests** | [tests/](tests/) — unit + live tests |

## License

MIT — Casey / SuperInstance, Sept 23, 2026
