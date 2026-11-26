import json
import tempfile
import unittest
from pathlib import Path

from window_light_polymer.static_site import build_static_site


class StaticSiteTests(unittest.TestCase):
    def test_build_bundles_validated_json_and_relative_assets(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = build_static_site(Path(temporary_directory) / "site")

            self.assertTrue((output / ".nojekyll").exists())
            page = (output / "index.html").read_text(encoding="utf-8")
            script = (output / "app.js").read_text(encoding="utf-8")
            self.assertIn('href="./styles.css"', page)
            self.assertIn('src="./app.js"', page)
            self.assertIn("./data/polly-tg-model-card.json", script)
            self.assertIn("./data/polly-map-pals-proxy.json", script)
            self.assertNotIn('fetch("/api/', script)

            model_card = json.loads((output / "data" / "polly-tg-model-card.json").read_text(encoding="utf-8"))
            proxy = json.loads((output / "data" / "polly-map-pals-proxy.json").read_text(encoding="utf-8"))
            self.assertEqual(model_card["dataset"]["polyurethane_records"], 123)
            self.assertEqual(proxy["data"]["numeric_surrogate_points"], 39)

    def test_build_requires_both_artifacts(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            missing = Path(temporary_directory) / "missing.json"
            with self.assertRaisesRegex(ValueError, "Model card not found"):
                build_static_site(Path(temporary_directory) / "site", model_card_path=missing)


if __name__ == "__main__":
    unittest.main()
