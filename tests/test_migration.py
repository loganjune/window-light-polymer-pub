import unittest

from window_light_polymer.migration import GroupConformalOpeningModel, OpeningRecord


def synthetic_records():
    records = []
    groups = (
        ("polyether-aromatic", "thermoplastic", 0.30, 0.0, 315.0),
        ("polyester-aromatic", "thermoplastic", 0.42, 0.0, 340.0),
        ("polycarbonate-aliphatic", "thermoplastic", 0.50, 0.0, 355.0),
        ("crosslinked-polyether", "thermoset", 0.38, 1.8, 350.0),
    )
    for group_index, (group, topology, hard_fraction, crosslink, tg_k) in enumerate(groups):
        for temperature_k in (280.0, 320.0, 360.0, 400.0, 440.0):
            delta = temperature_k - tg_k
            slope = 0.010 if topology == "thermoplastic" else 0.004
            opening = 4.4 + 0.003 * (temperature_k - 280.0) + slope * max(delta, 0.0)
            opening -= 0.7 * hard_fraction + 0.12 * crosslink
            opening += (group_index - 1.5) * 0.035
            records.append(
                OpeningRecord(
                    polymer_id=f"{group}-{int(temperature_k)}",
                    chemistry_group=group,
                    topology=topology,
                    temperature_k=temperature_k,
                    tg_k=tg_k,
                    hard_segment_fraction=hard_fraction,
                    crosslink_density_mol_l=crosslink,
                    opening_p50_a=opening,
                    provenance_kind="simulation",
                )
            )
    return records


class MigrationModelTests(unittest.TestCase):
    def test_group_conformal_model_is_monotonic_and_auditable(self):
        model = GroupConformalOpeningModel(coverage=0.90).fit(synthetic_records())
        template = synthetic_records()[0]
        cold = model.predict(template)
        hot = model.predict(OpeningRecord(**{**template.__dict__, "temperature_k": 430.0}))

        self.assertGreater(hot.median_a, cold.median_a)
        self.assertGreater(model.conformal_radius_a, 0.0)
        self.assertEqual(len(model.groups), 4)
        self.assertEqual(model.artifact()["method"]["coverage"], 0.90)

    def test_crossing_interval_orders_uncertainty(self):
        records = synthetic_records()
        model = GroupConformalOpeningModel().fit(records)
        crossing = model.crossing_interval(4.8, records[0], 260.0, 500.0)

        self.assertIsNotNone(crossing["earliest_k"])
        self.assertIsNotNone(crossing["median_k"])
        self.assertIsNotNone(crossing["latest_k"])
        self.assertLessEqual(crossing["earliest_k"], crossing["median_k"])
        self.assertLessEqual(crossing["median_k"], crossing["latest_k"])


if __name__ == "__main__":
    unittest.main()
