import json
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_PATH = PROJECT_ROOT / "research" / "literature" / "pu-free-volume-evidence.jsonl"


class LiteratureEvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.records = [
            json.loads(line)
            for line in EVIDENCE_PATH.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def test_records_have_unique_ids_and_traceability(self) -> None:
        ids = [record["record_id"] for record in self.records]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertGreaterEqual(len(self.records), 48)
        for record in self.records:
            self.assertTrue(record["citation"])
            self.assertTrue(record["source_url"].startswith("https://"))
            self.assertIn(record["extraction"]["kind"], {
                "reported_text",
                "reported_table",
                "figure_digitized",
                "abstract_only",
            })

    def test_requested_families_are_covered(self) -> None:
        families = {record["family"] for record in self.records}
        self.assertTrue({"polyether", "polyester", "polycaprolactone", "polycarbonate"} <= families)
        self.assertTrue(
            any(record["family"] == "polyether" and record["topology"] == "crosslinked" for record in self.records)
        )

    def test_opening_surrogates_are_not_mislabeled_as_connected_openings(self) -> None:
        radius_records = [
            record for record in self.records
            if "hole_radius" in record["measurement"]["observable"]
        ]
        self.assertTrue(radius_records)
        for record in radius_records:
            self.assertEqual(record["eligibility"]["polly_map_opening_label"], "surrogate_only")
            self.assertIn("spherical_equivalent_diameter_a", record["derived"])

    def test_direct_transport_records_are_kept_separate(self) -> None:
        transport_records = [
            record for record in self.records
            if record["measurement"]["observable"] in {
                "nitric_oxide_diffusion_coefficient",
                "nitric_oxide_partition_coefficient",
            }
        ]
        self.assertGreaterEqual(len(transport_records), 12)
        for record in transport_records:
            self.assertEqual(record["eligibility"]["polly_map_opening_label"], "no")
            self.assertTrue(record["eligibility"]["transport_validation"])

    def test_temperature_resolved_lifetime_series_keeps_reliability_boundary(self) -> None:
        lifetime_records = [
            record for record in self.records
            if record["source_id"] == "consolati2016"
            and record["measurement"]["observable"] == "o_ps_lifetime"
        ]
        self.assertEqual(len(lifetime_records), 17)
        self.assertTrue(all(record["validity"]["max_reliable_temperature_k"] == 300 for record in lifetime_records))
        self.assertEqual(sum(record["condition"]["temperature_k"] > 300 for record in lifetime_records), 4)


if __name__ == "__main__":
    unittest.main()
