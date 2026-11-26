"""Build Polly as a self-contained static website."""

from __future__ import annotations

import argparse
import json
from importlib.resources import files
from pathlib import Path
from typing import Any

from .server import DEFAULT_MIGRATION_PROXY_PATH, DEFAULT_MODEL_CARD_PATH, WEB_ASSETS, load_migration_proxy, load_model_card


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_static_site(
    output_directory: Path,
    model_card_path: Path = DEFAULT_MODEL_CARD_PATH,
    migration_proxy_path: Path = DEFAULT_MIGRATION_PROXY_PATH,
) -> Path:
    """Copy browser assets and validated model artifacts into one static directory."""

    output_directory = output_directory.resolve()
    output_directory.mkdir(parents=True, exist_ok=True)
    data_directory = output_directory / "data"
    data_directory.mkdir(exist_ok=True)

    web_root = files("window_light_polymer").joinpath("web")
    for asset_name in sorted(WEB_ASSETS):
        (output_directory / asset_name).write_bytes(web_root.joinpath(asset_name).read_bytes())

    model_card = load_model_card(model_card_path)
    if model_card is None:
        raise ValueError(f"Model card not found: {model_card_path}")
    migration_proxy = load_migration_proxy(migration_proxy_path)
    if migration_proxy is None:
        raise ValueError(f"Literature proxy not found: {migration_proxy_path}")

    _write_json(data_directory / "polly-tg-model-card.json", model_card)
    _write_json(data_directory / "polly-map-pals-proxy.json", migration_proxy)
    (output_directory / ".nojekyll").write_text("", encoding="utf-8")
    return output_directory


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build Polly's self-contained static research preview.")
    parser.add_argument("--output", type=Path, default=Path("_site"))
    parser.add_argument("--model-card", type=Path, default=DEFAULT_MODEL_CARD_PATH)
    parser.add_argument("--migration-proxy", type=Path, default=DEFAULT_MIGRATION_PROXY_PATH)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    output = build_static_site(args.output, args.model_card, args.migration_proxy)
    print(f"Built Polly static research preview: {output}")


if __name__ == "__main__":
    main()
