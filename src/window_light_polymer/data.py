"""Download, verify and parse the PolyMetriX glass-transition dataset."""

from __future__ import annotations

import argparse
import csv
import hashlib
import math
import shutil
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


DATASET_DOI = "10.5281/zenodo.15789599"
DATASET_LICENSE = "CC BY 4.0"
DATASET_FILENAME = "LAMALAB_CURATED_Tg_structured_polymerclass_with_embeddings.csv"
DATASET_URL = (
    "https://zenodo.org/api/records/15789599/files/"
    f"{DATASET_FILENAME}/content"
)
DATASET_MD5 = "31400a5f499394e3a6e0658488a464bb"
DEFAULT_DATASET_PATH = Path("data") / DATASET_FILENAME
FEATURE_PREFIX = "fullpolymerlevel.features."


@dataclass(frozen=True)
class PolymerRecord:
    psmiles: str
    tg_k: float
    polymer_class: str
    source: str
    reliability: str
    features: tuple[float, ...]


def file_md5(path: Path) -> str:
    digest = hashlib.md5()  # noqa: S324 - integrity check against the published record
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_dataset(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Missing dataset: {path}. Run window-light-polymer-fetch.")
    actual = file_md5(path)
    if actual != DATASET_MD5:
        raise ValueError(f"Dataset checksum mismatch: expected {DATASET_MD5}, found {actual}")


def download_dataset(path: Path = DEFAULT_DATASET_PATH) -> Path:
    """Download the exact published CSV and atomically move it into place."""

    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        verify_dataset(path)
        return path

    temporary = path.with_suffix(path.suffix + ".part")
    request = urllib.request.Request(DATASET_URL, headers={"User-Agent": "window-light-polymer/0.1"})
    try:
        with urllib.request.urlopen(request, timeout=120) as response, temporary.open("wb") as output:
            shutil.copyfileobj(response, output)
        verify_dataset(temporary)
        temporary.replace(path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    return path


def read_records(path: Path = DEFAULT_DATASET_PATH) -> tuple[list[PolymerRecord], list[str]]:
    verify_dataset(path)
    records: list[PolymerRecord] = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("Dataset has no header")
        feature_names = [name for name in reader.fieldnames if name.startswith(FEATURE_PREFIX)]
        if len(feature_names) != 28:
            raise ValueError(f"Expected 28 full-polymer descriptors, found {len(feature_names)}")
        for line_number, row in enumerate(reader, start=2):
            try:
                target = float(row["labels.Exp_Tg(K)"])
                features = tuple(float(row[name]) for name in feature_names)
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError(f"Invalid numeric value on CSV line {line_number}") from exc
            if not math.isfinite(target) or not all(math.isfinite(value) for value in features):
                raise ValueError(f"Non-finite value on CSV line {line_number}")
            records.append(
                PolymerRecord(
                    psmiles=row["PSMILES"],
                    tg_k=target,
                    polymer_class=row["meta.polymer_class"],
                    source=row["meta.source"],
                    reliability=row["meta.reliability"],
                    features=features,
                )
            )
    return records, feature_names


def count_values(records: Iterable[PolymerRecord], field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for record in records:
        value = str(getattr(record, field))
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Download and verify Polly's PolyMetriX dataset.")
    parser.add_argument("--output", type=Path, default=DEFAULT_DATASET_PATH)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    path = download_dataset(args.output)
    records, feature_names = read_records(path)
    polyurethane_count = sum(record.polymer_class == "Polyurethanes" for record in records)
    print(f"Verified {path} ({len(records):,} records, {len(feature_names)} descriptors)")
    print(f"Polyurethane records: {polyurethane_count}")


if __name__ == "__main__":
    main()

