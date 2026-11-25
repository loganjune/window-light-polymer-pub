"""POLLY-MAP: topology-aware opening curves with group cross-conformal uncertainty."""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np
from scipy.optimize import lsq_linear


TOPOLOGIES = frozenset({"thermoplastic", "thermoset"})
FEATURE_NAMES = (
    "intercept",
    "temperature_thermoplastic",
    "temperature_thermoset",
    "above_tg_thermoplastic",
    "above_tg_thermoset",
    "hard_segment_fraction",
    "crosslink_density_mol_l",
)
NONNEGATIVE_COEFFICIENTS = frozenset({1, 2, 3, 4})


@dataclass(frozen=True)
class OpeningRecord:
    polymer_id: str
    chemistry_group: str
    topology: str
    temperature_k: float
    tg_k: float
    hard_segment_fraction: float
    crosslink_density_mol_l: float
    opening_p50_a: float
    provenance_kind: str

    def validate(self) -> None:
        numeric = (
            self.temperature_k,
            self.tg_k,
            self.hard_segment_fraction,
            self.crosslink_density_mol_l,
            self.opening_p50_a,
        )
        if not self.polymer_id or not self.chemistry_group:
            raise ValueError("polymer_id and chemistry_group are required")
        if self.topology not in TOPOLOGIES:
            raise ValueError(f"topology must be one of {sorted(TOPOLOGIES)}")
        if not all(math.isfinite(value) for value in numeric):
            raise ValueError("all numeric opening fields must be finite")
        if self.temperature_k <= 0 or self.tg_k <= 0 or self.opening_p50_a <= 0:
            raise ValueError("temperature, Tg and opening diameter must be positive")
        if not 0 <= self.hard_segment_fraction <= 1:
            raise ValueError("hard_segment_fraction must be between 0 and 1")
        if self.crosslink_density_mol_l < 0:
            raise ValueError("crosslink_density_mol_l cannot be negative")
        if self.provenance_kind not in {"experiment", "simulation"}:
            raise ValueError("provenance_kind must be experiment or simulation")


@dataclass(frozen=True)
class OpeningPrediction:
    median_a: float
    lower_a: float
    upper_a: float
    coverage: float


def read_opening_records(path: Path) -> list[OpeningRecord]:
    records: list[OpeningRecord] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
                record = OpeningRecord(**value)
                record.validate()
            except (json.JSONDecodeError, TypeError, ValueError) as exc:
                raise ValueError(f"Invalid opening record on line {line_number}: {exc}") from exc
            records.append(record)
    return records


def _design(records: Sequence[OpeningRecord]) -> np.ndarray:
    rows: list[list[float]] = []
    for record in records:
        thermoplastic = 1.0 if record.topology == "thermoplastic" else 0.0
        thermoset = 1.0 - thermoplastic
        temperature = record.temperature_k - 250.0
        above_tg = max(record.temperature_k - record.tg_k, 0.0)
        rows.append(
            [
                1.0,
                temperature * thermoplastic,
                temperature * thermoset,
                above_tg * thermoplastic,
                above_tg * thermoset,
                record.hard_segment_fraction,
                record.crosslink_density_mol_l,
            ]
        )
    return np.asarray(rows, dtype=np.float64)


def _fit_coefficients(records: Sequence[OpeningRecord]) -> np.ndarray:
    if len(records) < len(FEATURE_NAMES) + 1:
        raise ValueError(f"At least {len(FEATURE_NAMES) + 1} records are required")
    design = _design(records)
    target = np.asarray([record.opening_p50_a for record in records], dtype=np.float64)
    lower = np.full(len(FEATURE_NAMES), -np.inf)
    lower[list(NONNEGATIVE_COEFFICIENTS)] = 0.0
    result = lsq_linear(design, target, bounds=(lower, np.full(len(FEATURE_NAMES), np.inf)))
    if not result.success or not np.all(np.isfinite(result.x)):
        raise ValueError(f"Opening-curve fit failed: {result.message}")
    return np.asarray(result.x, dtype=np.float64)


def _conformal_quantile(residuals: np.ndarray, coverage: float) -> float:
    if not 0 < coverage < 1:
        raise ValueError("coverage must be between zero and one")
    if residuals.size == 0:
        raise ValueError("group-held-out residuals are required")
    rank = min(residuals.size, int(math.ceil((residuals.size + 1) * coverage)))
    return float(np.sort(residuals)[rank - 1])


class GroupConformalOpeningModel:
    """Monotonic thermal opening model calibrated by leave-one-group-out residuals."""

    def __init__(self, coverage: float = 0.90):
        if not 0 < coverage < 1:
            raise ValueError("coverage must be between zero and one")
        self.coverage = coverage
        self.coefficients: np.ndarray | None = None
        self.conformal_radius_a: float | None = None
        self.groups: tuple[str, ...] = ()
        self.holdout_mae_a: float | None = None
        self.records: int = 0

    def fit(self, records: Sequence[OpeningRecord]) -> "GroupConformalOpeningModel":
        values = list(records)
        for record in values:
            record.validate()
        groups = tuple(sorted({record.chemistry_group for record in values}))
        if len(groups) < 3:
            raise ValueError("At least three chemistry groups are required for group-conformal calibration")

        residuals: list[float] = []
        for group in groups:
            training = [record for record in values if record.chemistry_group != group]
            held_out = [record for record in values if record.chemistry_group == group]
            coefficients = _fit_coefficients(training)
            prediction = _design(held_out) @ coefficients
            residuals.extend(np.abs(prediction - np.asarray([record.opening_p50_a for record in held_out])).tolist())

        residual_array = np.asarray(residuals, dtype=np.float64)
        self.coefficients = _fit_coefficients(values)
        self.conformal_radius_a = _conformal_quantile(residual_array, self.coverage)
        self.groups = groups
        self.holdout_mae_a = float(np.mean(residual_array))
        self.records = len(values)
        return self

    def _require_fit(self) -> tuple[np.ndarray, float]:
        if self.coefficients is None or self.conformal_radius_a is None:
            raise ValueError("Fit the POLLY-MAP model before prediction")
        return self.coefficients, self.conformal_radius_a

    def predict(self, record: OpeningRecord) -> OpeningPrediction:
        record.validate()
        coefficients, radius = self._require_fit()
        median = float((_design([record]) @ coefficients)[0])
        return OpeningPrediction(
            median_a=median,
            lower_a=max(0.0, median - radius),
            upper_a=median + radius,
            coverage=self.coverage,
        )

    def crossing_interval(
        self,
        additive_diameter_a: float,
        template: OpeningRecord,
        minimum_temperature_k: float,
        maximum_temperature_k: float,
        step_k: float = 1.0,
    ) -> dict[str, float | None]:
        if additive_diameter_a <= 0 or step_k <= 0 or maximum_temperature_k <= minimum_temperature_k:
            raise ValueError("Crossing inputs must define positive size, step and temperature range")
        temperatures = np.arange(minimum_temperature_k, maximum_temperature_k + step_k / 2, step_k)
        predictions = [
            self.predict(
                OpeningRecord(
                    **{
                        **asdict(template),
                        "temperature_k": float(temperature),
                    }
                )
            )
            for temperature in temperatures
        ]

        def first_crossing(values: Iterable[float]) -> float | None:
            previous_temperature: float | None = None
            previous_value: float | None = None
            for temperature, value in zip(temperatures, values):
                if value >= additive_diameter_a:
                    if previous_temperature is None or previous_value is None or value == previous_value:
                        return float(temperature)
                    fraction = (additive_diameter_a - previous_value) / (value - previous_value)
                    return float(previous_temperature + fraction * (temperature - previous_temperature))
                previous_temperature = float(temperature)
                previous_value = float(value)
            return None

        return {
            "earliest_k": first_crossing(prediction.upper_a for prediction in predictions),
            "median_k": first_crossing(prediction.median_a for prediction in predictions),
            "latest_k": first_crossing(prediction.lower_a for prediction in predictions),
        }

    def artifact(self) -> dict[str, Any]:
        coefficients, radius = self._require_fit()
        return {
            "schema_version": 1,
            "name": "POLLY-MAP alpha",
            "status": "research prototype; not validated for leaching or safety decisions",
            "target": "median connected probe-accessible opening diameter",
            "unit": "angstrom",
            "method": {
                "curve": "topology-aware bounded least squares with nonnegative temperature slopes",
                "uncertainty": "leave-one-chemistry-group-out cross-conformal absolute-residual interval",
                "coverage": self.coverage,
                "conformal_radius_a": radius,
            },
            "training": {
                "records": self.records,
                "chemistry_groups": list(self.groups),
                "group_holdout_mae_a": self.holdout_mae_a,
            },
            "features": list(FEATURE_NAMES),
            "coefficients": coefficients.tolist(),
            "claim_boundary": "A size crossing is geometric accessibility, not diffusion, partitioning or leaching.",
        }
