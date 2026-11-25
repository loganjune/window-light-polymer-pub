"""Train POLLY-MAP from temperature-indexed PALS or MD opening records."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .migration import GroupConformalOpeningModel, read_opening_records


DEFAULT_OUTPUT = Path("artifacts/polly-migration-model.json")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train POLLY-MAP with chemistry-group cross-conformal calibration.")
    parser.add_argument("--dataset", type=Path, required=True, help="Newline-delimited JSON matching the research schema.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--coverage", type=float, default=0.90)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    records = read_opening_records(args.dataset)
    model = GroupConformalOpeningModel(coverage=args.coverage).fit(records)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(model.artifact(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {args.output} from {len(records)} records across {len(model.groups)} chemistry groups")
    print(f"Group-held-out MAE: {model.holdout_mae_a:.3f} Å; interval radius: {model.conformal_radius_a:.3f} Å")


if __name__ == "__main__":
    main()
