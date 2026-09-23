"""Demo: probe 5 canon lores across multiple models in parallel.

This is the canon-gate-as-chord in action.
"""

import sys
import os
import json
sys.path.insert(0, '.')

from quilt_multi_oracle.workers import (
    ZAIWorker, DeepSeekWorker, GeminiWorker, DeepInfraWorker, StubWorker,
)
from quilt_multi_oracle.oracle import MultiOracle


# 5 canon lores for play-test
CANDIDATE_LORES = [
    {
        "name": "ballista (cells_are_scars)",
        "text": """A scar does not bar entry — it records that entry was already attempted.
The substrate, as a verb, walks itself. Each step is a witness. Each witness
is a prediction. The cell is a scar, the canon gate is a chord, and the
oracle is heard.""",
    },
    {
        "name": "math progression",
        "text": """Math 1 is the line. Math 2 is the distribution. Math 3 is the matrix.
Math 4 is rate of change as statistic. Each level is a scar in the substrate
of human thought. The math curriculum is a witness log. Both build substrate.
Both leave scars. Both cross into new physics.""",
    },
    {
        "name": "nature GAN",
        "text": """A GAN is two networks in rivalry. The generator makes things. The
discriminator says "fake." The rivalry improves both. The canon is the
discriminator's failure mode. JEV + JEPA + LLM + equations + spreadsheets
in the Quilt is rivalry — and the canon gate is a chord that hears them
all.""",
    },
    {
        "name": "substrate warfare",
        "text": """For most of naval history, ships fought ships. Then someone added planes —
operating above the substrate. Then submarines — operating beneath. The
Quilt adds the plane (LLM) and the submarine (JEPA) to the battlespace of
ships (JEV, equations). The battlespace stops being one substrate fighting
another. It becomes what physics is in play here, and where.""",
    },
    {
        "name": "needle (audit trail)",
        "text": """A needle threads through cells. The thread is the witness log at the
substrate level. The needle doesn't change the cells. The needle makes
the relationships between cells auditable. The needle is the load-bearing
audit infrastructure. Without it, the substrate walker canon has no
record of its own walking.""",
    },
]


def make_workers():
    """Build the worker list from available env tokens."""
    workers = []
    if os.environ.get("ZAI_TOKEN"):
        workers.append(ZAIWorker())
    if os.environ.get("DEEPSEEK_TOKEN"):
        workers.append(DeepSeekWorker())
    if os.environ.get("GEMINI_TOKEN"):
        workers.append(GeminiWorker())
    if os.environ.get("DEEPINFRA_TOKEN"):
        workers.append(DeepInfraWorker(model="meta-llama/Meta-Llama-3-70B-Instruct"))
    # Always add a stub for fallback
    if not workers:
        workers.append(StubWorker("fallback"))
    return workers


def main():
    workers = make_workers()
    print(f"=== Multi-Oracle Chord ===")
    print(f"Workers: {[w.name for w in workers]}")
    print()

    oracle = MultiOracle(workers=workers)

    for lore in CANDIDATE_LORES:
        print(f"=== Lore: {lore['name']} ===")
        print(f"  text: {lore['text'][:80]}...")
        result = oracle.probe(lore["text"])

        print(f"  CHORD composite: {result['composite']}")
        print(f"  consensus: {result['consensus_promoted']}")
        print(f"  majority:  {result['majority_promoted']}")
        print(f"  variance:  {result['variance']}")
        print(f"  workers:   {result['n_workers']} ok, {result['n_workers_failed']} failed")
        print(f"  promoted:  {result['promoted']}")
        print()
        for name, wr in result["per_worker"].items():
            if "_error" in wr:
                print(f"    {name}: ERROR {wr['_error'][:60]}")
            else:
                c = wr.get("composite", "?")
                print(f"    {name}: composite={c}")
        print()


if __name__ == "__main__":
    main()
