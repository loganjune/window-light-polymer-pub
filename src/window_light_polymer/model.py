"""Transparent transfer baseline for polyurethane glass-transition temperature."""

from __future__ import annotations

import hashlib
import math
import platform
from dataclasses import asdict, dataclass
from typing import Any, Sequence

import numpy as np
import sklearn
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

from .data import DATASET_DOI, DATASET_LICENSE, DATASET_MD5, PolymerRecord, count_values


PU_CLASS = "Polyurethanes"
GENERAL_DEGRADATION_CEILING = 0.05
BASE_ALPHA_GRID = (0.1, 1.0, 10.0, 100.0, 1000.0)
PU_WEIGHT_GRID = (0.0, 1.0, 3.0, 10.0, 30.0, 100.0)


@dataclass(frozen=True)
class Metrics:
    records: int
    mae_k: float
    rmse_k: float
    r2: float


def stable_bucket(value: str, salt: str, modulo: int = 10) -> int:
    digest = hashlib.sha256(f"{salt}\0{value}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") % modulo


def regression_metrics(truth: np.ndarray, prediction: np.ndarray) -> Metrics:
    residual = prediction - truth
    mae = float(np.mean(np.abs(residual)))
    rmse = float(np.sqrt(np.mean(np.square(residual))))
    denominator = float(np.sum(np.square(truth - np.mean(truth))))
    r2 = float(1.0 - np.sum(np.square(residual)) / denominator) if denominator > 0 else float("nan")
    return Metrics(records=int(truth.shape[0]), mae_k=mae, rmse_k=rmse, r2=r2)


def _arrays(records: Sequence[PolymerRecord]) -> tuple[np.ndarray, np.ndarray]:
    return (
        np.asarray([record.features for record in records], dtype=np.float64),
        np.asarray([record.tg_k for record in records], dtype=np.float64),
    )


def _metric_dict(metrics: Metrics) -> dict[str, Any]:
    values = asdict(metrics)
    return {key: (round(value, 6) if isinstance(value, float) and math.isfinite(value) else value) for key, value in values.items()}


def _split_general(records: Sequence[PolymerRecord]) -> tuple[list[PolymerRecord], list[PolymerRecord], list[PolymerRecord]]:
    train: list[PolymerRecord] = []
    guard: list[PolymerRecord] = []
    audit: list[PolymerRecord] = []
    for record in records:
        bucket = stable_bucket(record.psmiles, "polly-general-v1")
        if bucket < 8:
            train.append(record)
        elif bucket == 8:
            guard.append(record)
        else:
            audit.append(record)
    return train, guard, audit


def _split_polyurethane(
    records: Sequence[PolymerRecord],
) -> tuple[list[PolymerRecord], list[PolymerRecord], list[PolymerRecord]]:
    features, _ = _arrays(records)
    mean = features.mean(axis=0)
    scale = features.std(axis=0)
    scale[scale == 0] = 1.0
    distance = np.sqrt(np.mean(np.square((features - mean) / scale), axis=1))
    test_count = max(1, int(round(len(records) * 0.20)))
    ranked = sorted(range(len(records)), key=lambda index: (-float(distance[index]), records[index].psmiles))
    test_indices = set(ranked[:test_count])
    interior = [record for index, record in enumerate(records) if index not in test_indices]
    test = [record for index, record in enumerate(records) if index in test_indices]
    train = [record for record in interior if stable_bucket(record.psmiles, "polly-pu-v1", 5) != 0]
    validation = [record for record in interior if stable_bucket(record.psmiles, "polly-pu-v1", 5) == 0]
    if not validation:
        raise ValueError("Polyurethane validation split is empty")
    return train, validation, test


def _fit_ridge(
    scaler: StandardScaler,
    general_train: Sequence[PolymerRecord],
    polyurethane_train: Sequence[PolymerRecord],
    alpha: float,
    polyurethane_weight: float,
) -> Ridge:
    combined = list(general_train)
    sample_weight = [1.0] * len(general_train)
    if polyurethane_weight > 0:
        combined.extend(polyurethane_train)
        sample_weight.extend([polyurethane_weight] * len(polyurethane_train))
    x, y = _arrays(combined)
    model = Ridge(alpha=alpha, solver="lsqr")
    model.fit(scaler.transform(x), y, sample_weight=np.asarray(sample_weight))
    return model


def _predict(model: Ridge, scaler: StandardScaler, records: Sequence[PolymerRecord]) -> tuple[np.ndarray, np.ndarray]:
    x, y = _arrays(records)
    transformed = scaler.transform(x)
    prediction = np.einsum("ij,j->i", transformed, np.asarray(model.coef_)) + float(model.intercept_)
    if not np.all(np.isfinite(prediction)):
        raise ValueError("Model produced a non-finite prediction")
    return y, prediction


def _evaluate(model: Ridge, scaler: StandardScaler, records: Sequence[PolymerRecord]) -> Metrics:
    truth, prediction = _predict(model, scaler, records)
    return regression_metrics(truth, prediction)


def train_transfer_baseline(records: Sequence[PolymerRecord], feature_names: Sequence[str]) -> tuple[dict[str, Any], dict[str, Any]]:
    polyurethane = [record for record in records if record.polymer_class == PU_CLASS]
    general = [record for record in records if record.polymer_class != PU_CLASS]
    if len(polyurethane) < 50:
        raise ValueError("At least 50 polyurethane records are required")

    polyurethane_tg = np.asarray([record.tg_k for record in polyurethane], dtype=np.float64)

    general_train, general_guard, general_audit = _split_general(general)
    pu_train, pu_validation, pu_ood_test = _split_polyurethane(polyurethane)

    x_general_train, _ = _arrays(general_train)
    scaler = StandardScaler().fit(x_general_train)

    alpha_candidates: list[dict[str, Any]] = []
    for alpha in BASE_ALPHA_GRID:
        candidate = _fit_ridge(scaler, general_train, [], alpha, 0.0)
        guard_metrics = _evaluate(candidate, scaler, general_guard)
        alpha_candidates.append({"alpha": alpha, "general_guard": _metric_dict(guard_metrics), "model": candidate})
    selected_alpha_entry = min(alpha_candidates, key=lambda entry: entry["general_guard"]["mae_k"])
    selected_alpha = float(selected_alpha_entry["alpha"])
    base_model: Ridge = selected_alpha_entry["model"]
    base_guard = _evaluate(base_model, scaler, general_guard)

    fine_candidates: list[dict[str, Any]] = []
    for weight in PU_WEIGHT_GRID:
        candidate = base_model if weight == 0 else _fit_ridge(
            scaler, general_train, pu_train, selected_alpha, weight
        )
        pu_metrics = _evaluate(candidate, scaler, pu_validation)
        guard_metrics = _evaluate(candidate, scaler, general_guard)
        allowed = guard_metrics.mae_k <= base_guard.mae_k * (1.0 + GENERAL_DEGRADATION_CEILING)
        fine_candidates.append(
            {
                "polyurethane_weight": weight,
                "allowed": allowed,
                "pu_validation": _metric_dict(pu_metrics),
                "general_guard": _metric_dict(guard_metrics),
                "model": candidate,
            }
        )
    allowed_candidates = [candidate for candidate in fine_candidates if candidate["allowed"]]
    selected_fine_entry = min(allowed_candidates, key=lambda entry: entry["pu_validation"]["mae_k"])
    fine_model: Ridge = selected_fine_entry["model"]
    selected_weight = float(selected_fine_entry["polyurethane_weight"])

    base_pu_test = _evaluate(base_model, scaler, pu_ood_test)
    fine_pu_test = _evaluate(fine_model, scaler, pu_ood_test)
    base_general_audit = _evaluate(base_model, scaler, general_audit)
    fine_general_audit = _evaluate(fine_model, scaler, general_audit)
    pu_truth, base_prediction = _predict(base_model, scaler, pu_ood_test)
    _, fine_prediction = _predict(fine_model, scaler, pu_ood_test)

    examples = []
    for record, truth, base_value, fine_value in list(
        zip(pu_ood_test, pu_truth, base_prediction, fine_prediction)
    )[:8]:
        examples.append(
            {
                "psmiles": record.psmiles,
                "truth_k": round(float(truth), 4),
                "base_prediction_k": round(float(base_value), 4),
                "fine_tuned_prediction_k": round(float(fine_value), 4),
            }
        )

    serialized_candidates = [
        {key: value for key, value in candidate.items() if key != "model"} for candidate in fine_candidates
    ]
    model_artifact = {
        "schema_version": 1,
        "target": {"name": "experimental glass-transition temperature", "unit": "K"},
        "input": {"type": "PolyMetriX full-polymer descriptors", "features": list(feature_names)},
        "scaler": {"mean": scaler.mean_.tolist(), "scale": scaler.scale_.tolist()},
        "base_model": {
            "family": "ridge regression",
            "alpha": selected_alpha,
            "intercept": float(base_model.intercept_),
            "coefficients": base_model.coef_.tolist(),
        },
        "fine_tuned_model": {
            "family": "polyurethane-weighted ridge regression",
            "alpha": selected_alpha,
            "polyurethane_weight": selected_weight,
            "intercept": float(fine_model.intercept_),
            "coefficients": fine_model.coef_.tolist(),
        },
    }

    card = {
        "schema_version": 1,
        "model": {
            "name": "Polly Tg transfer baseline",
            "family": "standardized ridge regression with polyurethane-weighted fine-tuning",
            "target": "experimental glass-transition temperature",
            "unit": "K",
            "features": len(feature_names),
        },
        "dataset": {
            "name": "Curated Glass Transition Temperature for Polymers",
            "doi": DATASET_DOI,
            "license": DATASET_LICENSE,
            "md5": DATASET_MD5,
            "records": len(records),
            "polyurethane_records": len(polyurethane),
            "polyurethane_sources": count_values(polyurethane, "source"),
            "polyurethane_reliability": count_values(polyurethane, "reliability"),
            "polyurethane_tg_k": {
                "minimum": round(float(np.min(polyurethane_tg)), 4),
                "first_quartile": round(float(np.quantile(polyurethane_tg, 0.25)), 4),
                "median": round(float(np.median(polyurethane_tg)), 4),
                "third_quartile": round(float(np.quantile(polyurethane_tg, 0.75)), 4),
                "maximum": round(float(np.max(polyurethane_tg)), 4),
            },
            "geometry_targets": {
                "available": False,
                "missing": [
                    "3D atomic coordinates",
                    "temperature-indexed molecular trajectories",
                    "interatomic distances in angstrom",
                    "density or radial-distribution targets",
                ],
            },
        },
        "splits": {
            "general_train": len(general_train),
            "general_guard": len(general_guard),
            "general_audit": len(general_audit),
            "polyurethane_train": len(pu_train),
            "polyurethane_validation": len(pu_validation),
            "polyurethane_ood_test": len(pu_ood_test),
            "polyurethane_ood_rule": "20% farthest from the polyurethane descriptor centroid; labels unused",
        },
        "selection": {
            "base_alpha": selected_alpha,
            "polyurethane_weight": selected_weight,
            "general_guard_degradation_ceiling": GENERAL_DEGRADATION_CEILING,
            "candidates": serialized_candidates,
        },
        "evaluation": {
            "polyurethane_ood_test": {
                "base": _metric_dict(base_pu_test),
                "fine_tuned": _metric_dict(fine_pu_test),
                "mae_change_k": round(fine_pu_test.mae_k - base_pu_test.mae_k, 6),
            },
            "general_polymer_audit": {
                "base": _metric_dict(base_general_audit),
                "fine_tuned": _metric_dict(fine_general_audit),
                "mae_change_k": round(fine_general_audit.mae_k - base_general_audit.mae_k, 6),
            },
        },
        "scientific_questions": {
            "meaningful_downstream_task": "partial: held-out polyurethane Tg prediction",
            "disorder_and_unusual_conditions": "not answered: descriptor-space OOD is not physical disorder",
            "physical_stability": "not answered: no energy, force or dynamics model",
            "fine_tuning_tradeoff": "measured on a sealed general-polymer audit split",
            "reproducibility": "data DOI, checksum, deterministic splits, command and model coefficients recorded",
        },
        "limitations": [
            "All 123 polyurethane records come from the GREA source and carry the black reliability label.",
            "The target is Tg only; no formulation, cure, morphology or measurement-condition fields are modeled.",
            "The model uses precomputed descriptors and cannot predict directly from a new formulation.",
            "The OOD split measures descriptor distance, not disorder, temperature extremes or thermoset stability.",
            "Columns containing the word distance are graph descriptors, not 3D interatomic distances.",
            "Tg can anchor a qualitative softening regime, but this dataset cannot train an angstrom-distance predictor.",
            "This benchmark is not suitable for formulation, processing, safety or experimental decisions.",
        ],
        "reproducibility": {
            "command": "window-light-polymer-train",
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scikit_learn": sklearn.__version__,
            "split_seed": "SHA-256 salts polly-general-v1 and polly-pu-v1",
        },
        "examples": examples,
    }
    return model_artifact, card
