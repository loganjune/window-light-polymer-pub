import json
import unittest
from pathlib import Path

from window_light_polymer.literature_proxy import (
    build_pals_proxy_artifact,
    read_evidence,
    tao_eldrup_radius_angstrom,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_PATH = PROJECT_ROOT / "research" / "literature" / "pu-free-volume-evidence.jsonl"
ARTIFACT_PATH = PROJECT_ROOT / "artifacts" / "polly-map-pals-proxy.json"


class LiteratureProxyTests(unittest.TestCase):
    def test_proxy_is_built_from_surrogate_records_only(self) -> None:
        artifact = build_pals_proxy_artifact(read_evidence(EVIDENCE_PATH))
        self.assertEqual(artifact["data"]["proxy_points"], 18)
        self.assertEqual(artifact["data"]["numeric_surrogate_points"], 24)
        self.assertEqual(artifact["data"]["independent_surrogate_sources"], 3)
        self.assertEqual(artifact["data"]["independent_polymer_series"], 4)
        self.assertEqual(artifact["data"]["curves"], 3)
        self.assertIn("thermoplastic:polyester", artifact["curves"])
        self.assertIn("thermoplastic:polycaprolactone", artifact["curves"])
        self.assertIn("thermoset:polyether", artifact["curves"])
        self.assertIn("thermoplastic:polycarbonate", artifact["missing_curves"])
        self.assertIn("does not establish", artifact["claim_boundary"])

        polyester = artifact["curves"]["thermoplastic:polyester"]
        self.assertEqual(len(polyester["points"]), 13)
        self.assertEqual(polyester["excluded_observations_from_live_interpolation"], 4)
        self.assertEqual(polyester["temperature_range_k"], [200.0, 296.0])
        self.assertEqual(len(polyester["available_series"]), 2)

    def test_tao_eldrup_conversion_matches_curated_point(self) -> None:
        radius = tao_eldrup_radius_angstrom(1.2695)
        self.assertAlmostEqual(2.0 * radius, 4.117, places=3)

    def test_committed_proxy_matches_rebuilt_artifact(self) -> None:
        committed = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
        rebuilt = build_pals_proxy_artifact(read_evidence(EVIDENCE_PATH))
        self.assertEqual(committed, rebuilt)


if __name__ == "__main__":
    unittest.main()
