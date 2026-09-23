"""quilt-multi-oracle — multi-model JEV oracle.

The canon gate is a chord. This module probes lores across multiple LLMs
in parallel and aggregates their scores. Each worker is a different
"voice" in the canon-gate chord.

Supported workers:
  - zai (ZAI GLM-4.5 via /api/coding/paas/v4)
  - deepseek (DeepSeek chat)
  - deepinfra (any DeepInfra chat model)
  - gemini (Gemini 2.5 Flash via structured output)
"""

from .oracle import MultiOracle, OracleWorker, probe_lore_multi, aggregate_chord
from .workers import (
    ZAIWorker, DeepSeekWorker, DeepInfraWorker, GeminiWorker, StubWorker,
    get_worker_for_model,
)

__all__ = [
    "MultiOracle", "OracleWorker",
    "probe_lore_multi", "aggregate_chord",
    "ZAIWorker", "DeepSeekWorker", "DeepInfraWorker", "GeminiWorker", "StubWorker",
    "get_worker_for_model",
]

__version__ = "0.1.0"
