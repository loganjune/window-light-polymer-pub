"""Create the POLLY-MAP literature proxy artifact from curated evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .literature_proxy import build_pals_proxy_artifact, read_evidence


DEFAULT_DATASET = Path("research/literature/pu-free-volume-evidence.jsonl")
DEFAULT_OUTPUT = Path("artifacts/polly-map-pals-proxy.json")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build an interpolation-only POLLY-MAP PALS proxy artifact.")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    artifact = build_pals_proxy_artifact(read_evidence(args.dataset))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        f"Wrote {args.output} with {artifact['data']['proxy_points']} live points "
        f"across {artifact['data']['curves']} proxy curves; retained "
        f"{artifact['data']['numeric_surrogate_points']} numeric PALS points from "
        f"{artifact['data']['independent_surrogate_sources']} independent sources"
    )


if __name__ == "__main__":
    main()
