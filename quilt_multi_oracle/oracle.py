"""
oracle.py — multi-model JEV oracle. Probes a lore across N workers
in parallel and aggregates the canonical chord.
"""

import concurrent.futures
import statistics
from typing import List, Dict, Any, Optional
from .workers import OracleWorker, StubWorker


class MultiOracle:
    """The multi-model JEV oracle.

    Probes a lore across multiple LLM workers and returns the aggregated
    chord. The canon gate is a chord — multiple voices must participate.
    """

    def __init__(self, workers: Optional[List[OracleWorker]] = None):
        if workers is None:
            workers = [StubWorker("default")]
        self.workers = workers

    def add_worker(self, worker: OracleWorker) -> None:
        self.workers.append(worker)

    def probe(self, lore: str) -> dict:
        """Probe the lore across all workers in parallel."""
        if not self.workers:
            return {"_error": "no workers", "composite": 0.0}
        results = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.workers)) as executor:
            future_to_name = {
                executor.submit(w.probe, lore): w.name for w in self.workers
            }
            for future in concurrent.futures.as_completed(future_to_name):
                name = future_to_name[future]
                try:
                    results[name] = future.result()
                except Exception as e:
                    results[name] = {"_error": str(e)}
        return aggregate_chord(results)

    def probe_batch(self, lores: List[str]) -> List[dict]:
        """Probe multiple lores through the multi-oracle."""
        return [self.probe(lore) for lore in lores]


def aggregate_chord(worker_results: Dict[str, dict]) -> dict:
    """Aggregate multiple worker scores into a canonical chord.

    The chord computes:
      - mean composite across all workers
      - std deviation (high std = disagreement)
      - consensus_promoted: True if ALL workers agree (no worker below 0.7)
      - majority_promoted: True if majority of workers promote
      - per-worker breakdown

    The chord carries the load. The canon gate hears ALL voices.
    """
    composites = []
    doctrine_anchors = []
    canon_worthies = []
    distinct_voices = []
    promoted_votes = []
    per_worker = {}

    for name, result in worker_results.items():
        per_worker[name] = result
        if "_error" in result:
            # Worker failed — skip from aggregation but record
            continue
        c = result.get("composite")
        if c is None:
            continue
        composites.append(c)
        doctrine_anchors.append(result.get("doctrine_anchor", 0))
        canon_worthies.append(result.get("canon_worthy", 0))
        distinct_voices.append(result.get("distinct_voice", 0))
        promoted_votes.append(c >= 0.7)

    if not composites:
        return {
            "composite": 0.0,
            "doctrine_anchor": 0.0,
            "canon_worthy": 0.0,
            "distinct_voice": 0.0,
            "promoted": False,
            "consensus_promoted": False,
            "majority_promoted": False,
            "n_workers": 0,
            "n_workers_failed": len(worker_results),
            "variance": 0.0,
            "per_worker": per_worker,
            "_error": "all workers failed",
        }

    composite = statistics.mean(composites)
    n = len(composites)
    n_promoted = sum(promoted_votes)
    return {
        "composite": round(composite, 3),
        "doctrine_anchor": round(statistics.mean(doctrine_anchors), 3),
        "canon_worthy": round(statistics.mean(canon_worthies), 3),
        "distinct_voice": round(statistics.mean(distinct_voices), 3),
        "promoted": composite >= 0.7,
        "consensus_promoted": (n_promoted == n) if n else False,
        "majority_promoted": (n_promoted > n / 2) if n else False,
        "n_workers": n,
        "n_workers_failed": len(worker_results) - n,
        "n_promoted_workers": n_promoted,
        "variance": round(statistics.variance(composites), 4) if n > 1 else 0.0,
        "per_worker": per_worker,
    }


def probe_lore_multi(lore: str, workers: List[OracleWorker]) -> dict:
    """Convenience: probe a lore with the given workers."""
    oracle = MultiOracle(workers)
    return oracle.probe(lore)
