import json
import math
import unittest
from pathlib import Path

import numpy as np

from window_light_polymer.model import regression_metrics, stable_bucket


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class ModelTests(unittest.TestCase):
    def test_stable_bucket_is_deterministic_and_bounded(self):
        first = stable_bucket("[*]CC[*]", "polly-test", modulo=17)
        self.assertEqual(first, stable_bucket("[*]CC[*]", "polly-test", modulo=17))
        self.assertGreaterEqual(first, 0)
        self.assertLess(first, 17)

    def test_regression_metrics(self):
        metrics = regression_metrics(np.array([1.0, 2.0, 3.0]), np.array([1.0, 2.0, 4.0]))
        self.assertAlmostEqual(metrics.mae_k, 1.0 / 3.0)
        self.assertAlmostEqual(metrics.rmse_k, math.sqrt(1.0 / 3.0))
        self.assertAlmostEqual(metrics.r2, 0.5)

    def test_committed_artifacts_are_finite_and_auditable(self):
        model = json.loads((PROJECT_ROOT / "artifacts" / "polly-tg-model.json").read_text())
        card = json.loads((PROJECT_ROOT / "artifacts" / "polly-tg-model-card.json").read_text())

        self.assertEqual(model["schema_version"], 1)
        self.assertEqual(len(model["input"]["features"]), 28)
        self.assertTrue(all(math.isfinite(value) for value in model["fine_tuned_model"]["coefficients"]))
        self.assertEqual(sum(card["splits"].get(name, 0) for name in (
            "general_train",
            "general_guard",
            "general_audit",
            "polyurethane_train",
            "polyurethane_validation",
            "polyurethane_ood_test",
        )), card["dataset"]["records"])
        self.assertGreaterEqual(card["evaluation"]["general_polymer_audit"]["mae_change_k"], 0.0)


if __name__ == "__main__":
    unittest.main()
