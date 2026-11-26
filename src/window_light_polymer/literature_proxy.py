"""Build an auditable PALS proxy layer from curated literature evidence."""

from __future__ import annotations

import json
from collections import defaultdict
from math import pi, sin
from pathlib import Path
from typing import Any, Iterable


SUPPORTED_FAMILIES = frozenset({"polyether", "polyester", "polycaprolactone", "polycarbonate"})
TOPOLOGY_MAP = {
    "linear_thermoplastic": "thermoplastic",
    "crosslinked": "thermoset",
}


def tao_eldrup_radius_angstrom(lifetime_ns: float, delta_r_angstrom: float = 1.66) -> float:
    """Invert the spherical Tao-Eldrup relation used by the curated PALS papers."""

    if lifetime_ns <= 0.5:
        raise ValueError("o-Ps lifetime must be greater than 0.5 ns")

    def lifetime(radius: float) -> float:
        ratio = radius / (radius + delta_r_angstrom)
        return 0.5 / (1.0 - ratio + sin(2.0 * pi * ratio) / (2.0 * pi))

    lower, upper = 0.0, 20.0
    if lifetime(upper) < lifetime_ns:
        raise ValueError("o-Ps lifetime is outside the supported Tao-Eldrup inversion range")
    for _ in range(100):
        midpoint = (lower + upper) / 2.0
        if lifetime(midpoint) < lifetime_ns:
            lower = midpoint
        else:
            upper = midpoint
    return (lower + upper) / 2.0


def read_evidence(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid evidence JSON on line {line_number}: {exc}") from exc
            if not isinstance(value, dict) or not value.get("record_id"):
                raise ValueError(f"Evidence line {line_number} must be an object with record_id")
            records.append(value)
    return records


def _curve_key(record: dict[str, Any]) -> str | None:
    topology = TOPOLOGY_MAP.get(record.get("topology"))
    family = record.get("family")
    if topology is None or family not in SUPPORTED_FAMILIES:
        return None
    return f"{topology}:{family}"


def _source_summary(records: Iterable[dict[str, Any]]) -> list[dict[str, str | None]]:
    by_source: dict[str, dict[str, str | None]] = {}
    for record in records:
        source_id = str(record["source_id"])
        by_source[source_id] = {
            "source_id": source_id,
            "citation": str(record["citation"]),
            "doi": record.get("doi"),
            "url": str(record["source_url"]),
        }
    return [by_source[source_id] for source_id in sorted(by_source)]


def _series_id(record: dict[str, Any]) -> str:
    return f"{record['source_id']}::{record['polymer_id']}"


def _diameter_uncertainty(record: dict[str, Any]) -> float | None:
    derived = record.get("derived") or {}
    explicit = derived.get("spherical_equivalent_diameter_uncertainty_a")
    if isinstance(explicit, (int, float)):
        return float(explicit)

    extraction = record.get("extraction") or {}
    tolerance = extraction.get("digitization_tolerance")
    tolerance_unit = extraction.get("digitization_tolerance_unit")
    observable = (record.get("measurement") or {}).get("observable")
    if (
        isinstance(tolerance, (int, float))
        and tolerance_unit == "angstrom"
        and isinstance(observable, str)
        and "radius" in observable
    ):
        return float(tolerance) * 2.0
    return None


def _proxy_points(group: list[dict[str, Any]]) -> list[dict[str, Any]]:
    limits = [
        float(record["validity"]["max_reliable_temperature_k"])
        for record in group
        if isinstance((record.get("validity") or {}).get("max_reliable_temperature_k"), (int, float))
    ]
    reliability_limit = min(limits) if limits else None
    points: list[dict[str, Any]] = []
    for record in sorted(group, key=lambda value: value["condition"]["temperature_k"]):
        temperature = float(record["condition"]["temperature_k"])
        point = {
            "temperature_k": temperature,
            "diameter_a": float(record["derived"]["spherical_equivalent_diameter_a"]),
            "diameter_uncertainty_a": _diameter_uncertainty(record),
            "record_id": str(record["record_id"]),
            "extraction_kind": str(record["extraction"]["kind"]),
        }
        measurement = record.get("measurement") or {}
        if measurement.get("observable") == "o_ps_lifetime" and isinstance(measurement.get("value"), (int, float)):
            point["o_ps_lifetime_ns"] = float(measurement["value"])
        if reliability_limit is not None:
            point["reliability"] = (
                "author_caution_above_limit" if temperature > reliability_limit else "within_author_recommended_range"
            )
        points.append(point)
    return points


def build_pals_proxy_artifact(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Convert eligible local PALS diameters into interpolation-only proxy curves."""

    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    eligible_records: list[dict[str, Any]] = []
    for record in records:
        derived = record.get("derived") or {}
        diameter = derived.get("spherical_equivalent_diameter_a")
        temperature = (record.get("condition") or {}).get("temperature_k")
        eligibility = record.get("eligibility") or {}
        key = _curve_key(record)
        if (
            key is None
            or eligibility.get("polly_map_opening_label") != "surrogate_only"
            or not isinstance(diameter, (int, float))
            or not isinstance(temperature, (int, float))
        ):
            continue
        eligible_records.append(record)
        grouped[(key, _series_id(record))].append(record)

    evidence_series: list[dict[str, Any]] = []
    by_key: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for (key, series_id), group in sorted(grouped.items()):
        points = _proxy_points(group)
        if len(points) < 2:
            continue
        topology, family = key.split(":", maxsplit=1)
        tg_values = [
            float(record["measurement"]["value"])
            for record in records
            if _series_id(record) == series_id
            and record.get("measurement", {}).get("observable") == "glass_transition_temperature"
            and isinstance(record.get("measurement", {}).get("value"), (int, float))
        ]
        reliability_limits = [
            float(record["validity"]["max_reliable_temperature_k"])
            for record in group
            if isinstance((record.get("validity") or {}).get("max_reliable_temperature_k"), (int, float))
        ]
        series = {
            "series_id": series_id,
            "curve_key": key,
            "topology": topology,
            "family": family,
            "label": str(group[0]["polymer_id"]),
            "label_kind": "PALS spherical-equivalent cavity diameter proxy",
            "temperature_range_k": [points[0]["temperature_k"], points[-1]["temperature_k"]],
            "tg_k": tg_values[0] if len(tg_values) == 1 else None,
            "selection_priority": max(
                float((record.get("composition") or {}).get("live_proxy_priority", 0))
                for record in group
            ),
            "pals_reliability_limit_k": min(reliability_limits) if reliability_limits else None,
            "points": points,
            "interpolation": "piecewise linear between literature observations",
            "extrapolation": "disabled",
            "sources": _source_summary(group),
        }
        evidence_series.append(series)
        by_key[key].append(series)

    curves: dict[str, Any] = {}
    for key, series_group in sorted(by_key.items()):
        selected = max(
            series_group,
            key=lambda series: (
                len(series["points"]),
                series["selection_priority"],
                series["series_id"],
            ),
        )
        curve = dict(selected)
        reliability_limit = curve.get("pals_reliability_limit_k")
        if isinstance(reliability_limit, (int, float)):
            curve["points"] = [
                point for point in selected["points"] if point["temperature_k"] <= reliability_limit
            ]
            curve["excluded_observations_from_live_interpolation"] = (
                len(selected["points"]) - len(curve["points"])
            )
            curve["temperature_range_k"] = [
                curve["points"][0]["temperature_k"],
                curve["points"][-1]["temperature_k"],
            ]
        else:
            curve["excluded_observations_from_live_interpolation"] = 0
        curve["selection_reason"] = (
            "most temperature-resolved matched series; an auditable curation priority breaks ties; "
            "chemistries are not pooled"
        )
        curve["available_series"] = [
            {
                "series_id": series["series_id"],
                "label": series["label"],
                "observations": len(series["points"]),
                "source_id": series["sources"][0]["source_id"],
            }
            for series in sorted(series_group, key=lambda item: item["series_id"])
        ]
        curves[key] = curve

    default_series_ids = {curve["series_id"] for curve in curves.values()}
    for series in evidence_series:
        series["is_live_default"] = series["series_id"] in default_series_ids

    return {
        "schema_version": 2,
        "name": "POLLY-MAP literature PALS proxy",
        "status": "literature proxy; not calibrated for connected openings, diffusion, leaching or safety decisions",
        "target": "PALS spherical-equivalent local cavity diameter",
        "unit": "angstrom",
        "method": {
            "curve": "piecewise linear interpolation within one matched polymer series; chemistries and papers are not pooled",
            "extrapolation": "disabled",
            "uncertainty": "reported uncertainty when available; figure-digitization tolerance otherwise; absent values remain null",
            "series_selection": "the most temperature-resolved series is shown for each topology/family key; an auditable curation priority breaks ties; every eligible series remains auditable",
        },
        "data": {
            "curated_records_scanned": len(records),
            "proxy_points": sum(len(curve["points"]) for curve in curves.values()),
            "numeric_surrogate_points": len(eligible_records),
            "independent_surrogate_sources": len({str(record["source_id"]) for record in eligible_records}),
            "independent_polymer_series": len(evidence_series),
            "curves": len(curves),
        },
        "curves": curves,
        "evidence_series": evidence_series,
        "missing_curves": [
            key
            for key in (
                "thermoplastic:polyether",
                "thermoplastic:polycarbonate",
                "thermoset:polyether",
            )
            if key not in curves
        ],
        "claim_boundary": (
            "PALS local cavity diameter is a structural proxy. A size-line crossing does not establish a connected path, "
            "diffusion, partitioning, migrated mass, leaching, or safety."
        ),
    }
