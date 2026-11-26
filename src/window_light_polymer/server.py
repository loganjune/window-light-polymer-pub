"""Small standard-library server for the polyurethane structure explorer."""

from __future__ import annotations

import argparse
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
}
WEB_ASSETS = frozenset({"index.html", "styles.css", "app.js"})
DEFAULT_MODEL_CARD_PATH = Path("artifacts/polly-tg-model-card.json")
DEFAULT_MIGRATION_PROXY_PATH = Path("artifacts/polly-map-pals-proxy.json")
MODEL_CARD_DATA_ROUTE = "/data/polly-tg-model-card.json"
MIGRATION_PROXY_DATA_ROUTE = "/data/polly-map-pals-proxy.json"


def health_payload(model_ready: bool = False, migration_proxy_ready: bool = False) -> dict[str, Any]:
    """Return a small, stable readiness record for local preview tooling."""

    return {
        "ready": True,
        "service": "Window Light Polymer",
        "guide": "Polly",
        "mode": "educational structure explorer",
        "model_ready": model_ready,
        "migration_proxy_ready": migration_proxy_ready,
    }


def resolve_asset(path: str) -> str | None:
    """Map an HTTP path to a packaged asset without permitting traversal."""

    parsed_path = urlparse(path).path
    asset_name = "index.html" if parsed_path in ("/", "/index.html") else parsed_path.lstrip("/")
    return asset_name if asset_name in WEB_ASSETS else None


def load_model_card(path: Path | None) -> dict[str, Any] | None:
    if path is None or not path.exists():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Could not load model card {path}: {exc}") from exc
    if not isinstance(value, dict) or value.get("schema_version") != 1:
        raise ValueError(f"Unsupported model card schema in {path}")
    return value


def load_migration_proxy(path: Path | None) -> dict[str, Any] | None:
    if path is None or not path.exists():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Could not load migration proxy {path}: {exc}") from exc
    if (
        not isinstance(value, dict)
        or value.get("schema_version") not in {1, 2}
        or value.get("name") != "POLLY-MAP literature PALS proxy"
    ):
        raise ValueError(f"Unsupported migration proxy schema in {path}")
    return value


def make_handler(
    model_card_path: Path | None = DEFAULT_MODEL_CARD_PATH,
    migration_proxy_path: Path | None = DEFAULT_MIGRATION_PROXY_PATH,
):
    web_root = files("window_light_polymer").joinpath("web")
    model_card = load_model_card(model_card_path)
    migration_proxy = load_migration_proxy(migration_proxy_path)

    class Handler(BaseHTTPRequestHandler):
        server_version = "WindowLightPolymer/0.1"

        def send_json(self, value: Any, status: HTTPStatus = HTTPStatus.OK) -> None:
            body = json.dumps(value).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
            path = urlparse(self.path).path
            if path == "/favicon.ico":
                self.send_response(HTTPStatus.NO_CONTENT)
                self.end_headers()
                return
            if path == MODEL_CARD_DATA_ROUTE:
                if model_card is None:
                    self.send_json(
                        {"error": "Bundled model card unavailable. Run window-light-polymer-train."},
                        HTTPStatus.SERVICE_UNAVAILABLE,
                    )
                else:
                    self.send_json(model_card)
                return
            if path == MIGRATION_PROXY_DATA_ROUTE:
                if migration_proxy is None:
                    self.send_json(
                        {"error": "Bundled literature proxy unavailable. Run window-light-polymer-literature-proxy."},
                        HTTPStatus.SERVICE_UNAVAILABLE,
                    )
                else:
                    self.send_json(migration_proxy)
                return
            if path == "/api/health":
                self.send_json(health_payload(model_card is not None, migration_proxy is not None))
                return
            if path == "/api/model-card":
                if model_card is None:
                    self.send_json(
                        {"error": "Model card unavailable. Run window-light-polymer-train."},
                        HTTPStatus.SERVICE_UNAVAILABLE,
                    )
                else:
                    self.send_json(model_card)
                return
            if path == "/api/polly-map-proxy":
                if migration_proxy is None:
                    self.send_json(
                        {"error": "Literature proxy unavailable. Run window-light-polymer-literature-proxy."},
                        HTTPStatus.SERVICE_UNAVAILABLE,
                    )
                else:
                    self.send_json(migration_proxy)
                return

            asset_name = resolve_asset(path)
            if asset_name is None:
                self.send_error(HTTPStatus.NOT_FOUND)
                return

            body = web_root.joinpath(asset_name).read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", CONTENT_TYPES[Path(asset_name).suffix])
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(body)

    return Handler


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Serve the Window Light Polymer explorer.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=4175)
    parser.add_argument("--model-card", type=Path, default=DEFAULT_MODEL_CARD_PATH)
    parser.add_argument("--migration-proxy", type=Path, default=DEFAULT_MIGRATION_PROXY_PATH)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    server = ThreadingHTTPServer((args.host, args.port), make_handler(args.model_card, args.migration_proxy))
    print(f"Window Light Polymer: http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
