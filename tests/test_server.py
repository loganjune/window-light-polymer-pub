import unittest
from importlib.resources import files
from pathlib import Path

from window_light_polymer.server import health_payload, load_migration_proxy, load_model_card, resolve_asset


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class ServerTests(unittest.TestCase):
    def test_health_payload_is_ready(self):
        payload = health_payload()
        self.assertEqual(payload["service"], "Window Light Polymer")
        self.assertEqual(payload["guide"], "Polly")
        self.assertTrue(payload["ready"])
        self.assertFalse(payload["model_ready"])
        self.assertFalse(payload["migration_proxy_ready"])

        self.assertTrue(health_payload(model_ready=True)["model_ready"])
        self.assertTrue(health_payload(migration_proxy_ready=True)["migration_proxy_ready"])

    def test_home_page_contains_both_polyurethane_families(self):
        page = files("window_light_polymer").joinpath("web", "index.html").read_text()
        self.assertIn("Thermoplastic", page)
        self.assertIn("Thermoset", page)
        self.assertIn("Meet Polly", page)
        self.assertIn("POLLY'S FIRST TRAINABLE MODEL", page)
        self.assertIn("Temperature vs accessible opening", page)
        self.assertIn("additive-size", page)
        self.assertIn("POLLY-MAP ALPHA", page)
        self.assertIn("Polycaprolactone", page)
        self.assertIn("Loading literature evidence", page)
        self.assertIn("polymer-canvas", page)

    def test_generated_model_card_is_loadable(self):
        card = load_model_card(PROJECT_ROOT / "artifacts" / "polly-tg-model-card.json")
        self.assertIsNotNone(card)
        self.assertEqual(card["dataset"]["polyurethane_records"], 123)
        self.assertFalse(card["dataset"]["geometry_targets"]["available"])
        self.assertEqual(card["evaluation"]["polyurethane_ood_test"]["base"]["records"], 25)

    def test_literature_proxy_is_loadable(self):
        proxy = load_migration_proxy(PROJECT_ROOT / "artifacts" / "polly-map-pals-proxy.json")
        self.assertIsNotNone(proxy)
        self.assertEqual(proxy["data"]["proxy_points"], 18)
        self.assertEqual(proxy["data"]["numeric_surrogate_points"], 24)
        self.assertEqual(proxy["target"], "PALS spherical-equivalent local cavity diameter")

    def test_unknown_assets_are_not_served(self):
        self.assertEqual(resolve_asset("/"), "index.html")
        self.assertEqual(resolve_asset("/styles.css?version=1"), "styles.css")
        self.assertIsNone(resolve_asset("/../pyproject.toml"))


if __name__ == "__main__":
    unittest.main()
