"""Command-line training entry point for Polly's first scientific baseline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .data import DEFAULT_DATASET_PATH, read_records
from .model import train_transfer_baseline


DEFAULT_MODEL_PATH = Path("artifacts/polly-tg-model.json")
DEFAULT_CARD_PATH = Path("artifacts/polly-tg-model-card.json")


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train and audit Polly's polyurethane Tg transfer baseline.")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_MODEL_PATH)
    parser.add_argument("--model-card", type=Path, default=DEFAULT_CARD_PATH)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    records, feature_names = read_records(args.dataset)
    model, card = train_transfer_baseline(records, feature_names)
    write_json(args.output, model)
    write_json(args.model_card, card)
    pu = card["evaluation"]["polyurethane_ood_test"]
    general = card["evaluation"]["general_polymer_audit"]
    print(f"Wrote {args.output} and {args.model_card}")
    print(
        "PU OOD MAE: "
        f"{pu['base']['mae_k']:.3f} K -> {pu['fine_tuned']['mae_k']:.3f} K; "
        "general audit MAE: "
        f"{general['base']['mae_k']:.3f} K -> {general['fine_tuned']['mae_k']:.3f} K"
    )


if __name__ == "__main__":
    main()

