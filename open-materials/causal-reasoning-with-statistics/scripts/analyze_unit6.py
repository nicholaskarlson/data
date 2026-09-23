#!/usr/bin/env python3
"""Primary NumPy analysis for Unit 6 difference-in-differences and ITS."""

import csv
import hashlib
import json
import platform
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "unit6_youth_crisis_policy.csv"
RESULT = ROOT / "expected-results" / "unit6_youth_crisis_policy_verified_results.json"
OUTCOME = "youth_emergency_transports_per_10000"
T_CLUSTER_23 = 2.06865761
T_HAC_30 = 2.042272456


def read_rows():
    rows = []
    with DATA.open(newline="", encoding="utf-8") as stream:
        for raw in csv.DictReader(stream):
            rows.append(
                {
                    "municipality_id": raw["municipality_id"],
                    "region": raw["region"],
                    "month_index": int(raw["month_index"]),
                    "relative_month": int(raw["relative_month"]),
                    "early_adopter": int(raw["early_adopter"]),
                    "regional_hotline_active": int(raw["regional_hotline_active"]),
                    "policy_active": int(raw["policy_active"]),
                    OUTCOME: float(raw[OUTCOME]),
                }
            )
    return rows


def twfe_matrix(rows, target):
    municipalities = sorted({row["municipality_id"] for row in rows})
    months = sorted({row["month_index"] for row in rows})
    return np.asarray(
        [
            [1.0, float(row[target])]
            + [float(row["municipality_id"] == name) for name in municipalities[1:]]
            + [float(row["month_index"] == month) for month in months[1:]]
            for row in rows
        ],
        dtype=float,
    )


def cluster_fit(rows, target):
    x = twfe_matrix(rows, target)
    y = np.asarray([row[OUTCOME] for row in rows], dtype=float)
    beta = np.linalg.lstsq(x, y, rcond=None)[0]
    residual = y - x @ beta
    bread = np.linalg.inv(x.T @ x)
    meat = np.zeros((x.shape[1], x.shape[1]))
    clusters = sorted({row["municipality_id"] for row in rows})
    for cluster in clusters:
        indices = [index for index, row in enumerate(rows) if row["municipality_id"] == cluster]
        score = x[indices].T @ residual[indices]
        meat += np.outer(score, score)
    n, p, groups = len(rows), x.shape[1], len(clusters)
    correction = groups / (groups - 1) * (n - 1) / (n - p)
    covariance = correction * bread @ meat @ bread
    return float(beta[1]), float(np.sqrt(covariance[1, 1]))


def record(estimate, se, critical):
    return {
        "estimate": round(estimate, 6),
        "se": round(se, 6),
        "ci95_lower": round(estimate - critical * se, 6),
        "ci95_upper": round(estimate + critical * se, 6),
    }


def monthly_group_means(rows, early_adopter):
    return np.asarray(
        [
            np.mean(
                [
                    row[OUTCOME]
                    for row in rows
                    if row["early_adopter"] == early_adopter
                    and row["month_index"] == month
                ]
            )
            for month in range(1, 37)
        ],
        dtype=float,
    )


def its_fit(series, lag=3):
    month = np.arange(1.0, 37.0)
    post = (month >= 19).astype(float)
    time_after = np.maximum(0.0, month - 18.0)
    x = np.column_stack(
        [
            np.ones(36),
            month - 18.0,
            post,
            time_after,
            np.sin(2.0 * np.pi * (month - 1.0) / 12.0),
            np.cos(2.0 * np.pi * (month - 1.0) / 12.0),
        ]
    )
    beta = np.linalg.lstsq(x, series, rcond=None)[0]
    residual = series - x @ beta
    bread = np.linalg.inv(x.T @ x)
    scores = x * residual[:, None]
    meat = scores.T @ scores
    for distance in range(1, lag + 1):
        weight = 1.0 - distance / (lag + 1.0)
        cross = scores[distance:].T @ scores[:-distance]
        meat += weight * (cross + cross.T)
    covariance = len(series) / (len(series) - x.shape[1]) * bread @ meat @ bread
    return beta, covariance


def compute():
    rows = read_rows()
    pre_rows = [dict(row) for row in rows if row["month_index"] <= 18]
    for row in pre_rows:
        row["placebo_active"] = row["early_adopter"] * int(row["month_index"] >= 13)
        row["early_month_slope"] = row["early_adopter"] * (row["month_index"] - 9.5)

    did_estimate, did_se = cluster_fit(rows, "policy_active")
    placebo_estimate, placebo_se = cluster_fit(pre_rows, "placebo_active")
    pretrend_estimate, pretrend_se = cluster_fit(pre_rows, "early_month_slope")
    early_series = monthly_group_means(rows, 1)
    comparison_series = monthly_group_means(rows, 0)
    early_beta, early_covariance = its_fit(early_series)
    comparison_beta, comparison_covariance = its_fit(comparison_series)

    estimates = {
        "did_twfe_clustered": record(did_estimate, did_se, T_CLUSTER_23),
        "preperiod_placebo_did": record(placebo_estimate, placebo_se, T_CLUSTER_23),
        "preperiod_differential_slope": record(pretrend_estimate, pretrend_se, T_CLUSTER_23),
        "early_series_its_level_change_hac": record(
            float(early_beta[2]), float(np.sqrt(early_covariance[2, 2])), T_HAC_30
        ),
        "early_series_its_slope_change_hac": record(
            float(early_beta[3]), float(np.sqrt(early_covariance[3, 3])), T_HAC_30
        ),
        "comparison_series_its_level_change_hac": record(
            float(comparison_beta[2]), float(np.sqrt(comparison_covariance[2, 2])), T_HAC_30
        ),
    }

    means = {}
    for group, label in ((1, "early_adopter"), (0, "not_yet_adopter")):
        for post, period in ((0, "pre"), (1, "post")):
            values = [
                row[OUTCOME]
                for row in rows
                if row["early_adopter"] == group
                and int(row["month_index"] >= 19) == post
            ]
            means[f"{label}_{period}"] = round(float(np.mean(values)), 6)
    means["early_before_after_change"] = round(
        means["early_adopter_post"] - means["early_adopter_pre"], 6
    )
    means["comparison_before_after_change"] = round(
        means["not_yet_adopter_post"] - means["not_yet_adopter_pre"], 6
    )
    means["difference_in_changes"] = round(
        means["early_before_after_change"] - means["comparison_before_after_change"], 6
    )

    its_level_difference = round(float(early_beta[2] - comparison_beta[2]), 6)
    return {
        "title": "Unit 6 deterministic phased municipal youth-crisis policy panel",
        "dataset_sha256": hashlib.sha256(DATA.read_bytes()).hexdigest(),
        "generator_seed": 20260919,
        "n_rows": len(rows),
        "n_municipalities": 24,
        "n_months": 36,
        "n_early_adopters": 12,
        "n_not_yet_adopters": 12,
        "policy_start_month": 19,
        "pre_months": 18,
        "post_months": 18,
        "placebo_start_month": 13,
        "group_period_means": means,
        "estimates": estimates,
        "its_level_change_difference": its_level_difference,
        "did_minus_its_level_change_difference": round(did_estimate - its_level_difference, 6),
        "known_simulation_policy_effect": -1.7,
        "known_simulation_regional_hotline_effect": -1.05,
        "degrees_of_freedom": {
            "clustered_panel_estimates": 23,
            "aggregate_its_estimates": 30,
        },
        "interval_method": (
            "DiD, placebo, and pretrend intervals use municipality-clustered CR1 covariance, "
            "24 clusters, and t(23). Aggregate interrupted-series intervals use a seasonal "
            "segmented regression with Newey-West lag 3, finite-sample scaling, and t(30)."
        ),
        "identification_note": (
            "The DiD coefficient targets the average early-adopter policy effect during months "
            "19-36 if untreated potential-outcome trends would have remained parallel, treatment "
            "versions are consistent, no anticipatory or cross-municipality effects operate, and "
            "the not-yet-adopter series is not differentially affected by other events. The treated-only "
            "ITS does not separate the policy from the same-month regional hotline or other discontinuities."
        ),
        "primary_environment": {"python": platform.python_version(), "numpy": np.__version__},
    }


def main():
    output = compute()
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "CAUSAL_UNIT6_PRIMARY_OK",
        f"rows={output['n_rows']}",
        f"municipalities={output['n_municipalities']}",
        f"did={output['estimates']['did_twfe_clustered']['estimate']}",
    )


if __name__ == "__main__":
    main()
