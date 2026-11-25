import hashlib
import tempfile
import unittest
from pathlib import Path

from window_light_polymer.data import PolymerRecord, count_values, file_md5


class DataTests(unittest.TestCase):
    def test_file_md5_matches_known_content(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.csv"
            path.write_bytes(b"polly\n")
            self.assertEqual(file_md5(path), hashlib.md5(b"polly\n").hexdigest())  # noqa: S324

    def test_count_values_is_sorted_and_complete(self):
        records = [
            PolymerRecord("a", 300.0, "Polyurethanes", "z", "black", (1.0,)),
            PolymerRecord("b", 310.0, "Polyurethanes", "a", "black", (2.0,)),
            PolymerRecord("c", 320.0, "Other", "z", "gold", (3.0,)),
        ]
        self.assertEqual(count_values(records, "source"), {"a": 1, "z": 2})


if __name__ == "__main__":
    unittest.main()
