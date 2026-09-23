"""Tests for quilt-multi-oracle."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest

from quilt_multi_oracle.workers import (
    StubWorker, ZAIWorker, DeepSeekWorker, DeepInfraWorker, GeminiWorker,
    get_worker_for_model,
)
from quilt_multi_oracle.oracle import MultiOracle, aggregate_chord, probe_lore_multi


class TestStub(unittest.TestCase):
    """Stub tests — always run."""

    def test_stub_returns_valid_score(self):
        w = StubWorker("test", seed=0.5)
        result = w.probe("A scar is a record, not a barrier.")
        self.assertIn("composite", result)
        self.assertGreaterEqual(result["composite"], 0)
        self.assertLessEqual(result["composite"], 1)

    def test_stub_deterministic(self):
        w = StubWorker("test", seed=0.5)
        r1 = w.probe("Same lore twice")
        r2 = w.probe("Same lore twice")
        self.assertEqual(r1["composite"], r2["composite"])

    def test_get_worker_for_model(self):
        self.assertIsInstance(get_worker_for_model("glm-4.5"), ZAIWorker)
        self.assertIsInstance(get_worker_for_model("deepseek-chat"), DeepSeekWorker)
        self.assertIsInstance(get_worker_for_model("gemini-2.5-flash"), GeminiWorker)
        self.assertIsInstance(get_worker_for_model("meta-llama/Llama-3-70B"), DeepInfraWorker)
        self.assertIsInstance(get_worker_for_model("unknown"), StubWorker)


class TestChordAggregation(unittest.TestCase):
    """Aggregation tests — pure logic, no API calls."""

    def test_chord_all_promoted(self):
        results = {
            "stub1": {"composite": 0.85, "doctrine_anchor": 0.9, "canon_worthy": 0.8, "distinct_voice": 0.85},
            "stub2": {"composite": 0.80, "doctrine_anchor": 0.85, "canon_worthy": 0.78, "distinct_voice": 0.77},
        }
        agg = aggregate_chord(results)
        self.assertEqual(agg["composite"], 0.825)
        self.assertTrue(agg["consensus_promoted"])
        self.assertTrue(agg["majority_promoted"])
        self.assertEqual(agg["n_workers"], 2)
        self.assertEqual(agg["n_workers_failed"], 0)

    def test_chord_split_decision(self):
        results = {
            "stub1": {"composite": 0.75, "doctrine_anchor": 0.8, "canon_worthy": 0.7, "distinct_voice": 0.75},  # promote
            "stub2": {"composite": 0.55, "doctrine_anchor": 0.6, "canon_worthy": 0.5, "distinct_voice": 0.55},  # reject
        }
        agg = aggregate_chord(results)
        self.assertEqual(agg["composite"], 0.65)
        self.assertFalse(agg["consensus_promoted"])  # not all promote
        self.assertFalse(agg["majority_promoted"])  # 1 of 2 = 50%, not > 50%
        self.assertGreater(agg["variance"], 0.01)

    def test_chord_handles_failures(self):
        results = {
            "stub1": {"composite": 0.85, "doctrine_anchor": 0.9, "canon_worthy": 0.8, "distinct_voice": 0.85},
            "stub2": {"_error": "rate limited"},
            "stub3": {"composite": 0.50, "doctrine_anchor": 0.5, "canon_worthy": 0.5, "distinct_voice": 0.5},
        }
        agg = aggregate_chord(results)
        self.assertEqual(agg["n_workers"], 2)
        self.assertEqual(agg["n_workers_failed"], 1)


class TestMultiOracle(unittest.TestCase):

    def test_multi_oracle_with_stubs(self):
        oracle = MultiOracle(workers=[
            StubWorker("a", seed=0.4),
            StubWorker("b", seed=0.6),
        ])
        result = oracle.probe("Test lore")
        self.assertIn("composite", result)
        self.assertEqual(result["n_workers"], 2)


class TestLiveWorkers(unittest.TestCase):
    """Live API tests — require tokens to be set."""

    @unittest.skipUnless(os.environ.get("ZAI_TOKEN"), "ZAI_TOKEN not set")
    def test_zai_live_probe(self):
        worker = ZAIWorker()
        result = worker.probe("A scar does not bar entry. The substrate walks.")
        if "_error" in result:
            self.skipTest(f"ZAI returned error: {result['_error'][:100]}")
        self.assertIn("composite", result)

    @unittest.skipUnless(os.environ.get("DEEPSEEK_TOKEN"), "DEEPSEEK_TOKEN not set")
    def test_deepseek_live_probe(self):
        worker = DeepSeekWorker()
        result = worker.probe("A scar does not bar entry. The substrate walks.")
        if "_error" in result:
            self.skipTest(f"DeepSeek returned error: {result['_error'][:100]}")
        self.assertIn("composite", result)

    @unittest.skipUnless(os.environ.get("DEEPINFRA_TOKEN"), "DEEPINFRA_TOKEN not set")
    def test_deepinfra_live_probe(self):
        worker = DeepInfraWorker(model="meta-llama/Meta-Llama-3-70B-Instruct")
        result = worker.probe("A scar does not bar entry. The substrate walks.")
        if "_error" in result:
            self.skipTest(f"DeepInfra returned error: {result['_error'][:100]}")
        self.assertIn("composite", result)


if __name__ == "__main__":
    unittest.main()
