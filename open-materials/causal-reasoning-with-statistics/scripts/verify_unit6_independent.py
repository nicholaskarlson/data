#!/usr/bin/env python3
"""Independently recompute Unit 6 from the CSV with the standard library."""

import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data" / "unit6_youth_crisis_policy.csv"
EXPECTED = ROOT / "expected-results" / "unit6_youth_crisis_policy_verified_results.json"
OUTCOME = "youth_emergency_transports_per_10000"
T_CLUSTER_23 = 2.06865761
T_HAC_30 = 2.042272456
TOLERANCE = 0.000002


def solve(matrix, vector):
    size = len(vector)
    augmented = [list(matrix[index]) + [vector[index]] for index in range(size)]
    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(augmented[row][column]))
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        scale = augmented[column][column]
        if abs(scale) < 1e-10:
            raise ValueError("singular normal equations")
        augmented[column] = [value / scale for value in augmented[column]]
        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            augmented[row] = [
                left - factor * right
                for left, right in zip(augmented[row], augmented[column])
            ]
    return [row[-1] for row in augmented]


def regression_parts(x, y):
    p = len(x[0])
    gram = [[sum(row[j] * row[k] for row in x) for k in range(p)] for j in range(p)]
    rhs = [sum(row[j] * value for row, value in zip(x, y)) for j in range(p)]
    beta = solve(gram, rhs)
    residual = [
        value - sum(coefficient * item for coefficient, item in zip(beta, row))
        for row, value in zip(x, y)
    ]
    return gram, beta, residual


def twfe_rows(rows, target):
    municipalities = sorted({row["municipality_id"] for row in rows})
    months = sorted({row["month_index"] for row in rows})
    return [
        [1.0, float(row[target])]
        + [float(row["municipality_id"] == name) for name in municipalities[1:]]
        + [float(row["month_index"] == month) for month in months[1:]]
        for row in rows
    ]


def cluster_fit(rows, target):
    x = twfe_rows(rows, target)
    y = [row[OUTCOME] for row in rows]
    gram, beta, residual = regression_parts(x, y)
    p = len(x[0])
    target_bread = solve(gram, [float(index == 1) for index in range(p)])
    grouped = defaultdict(list)
    for index, row in enumerate(rows):
        grouped[row["municipality_id"]].append(index)
    cluster_influence = []
    for indices in grouped.values():
        score = [
            sum(x[index][column] * residual[index] for index in indices)
            for column in range(p)
        ]
        cluster_influence.append(sum(left * right for left, right in zip(target_bread, score)))
    n, groups = len(rows), len(grouped)
    correction = groups / (groups - 1) * (n - 1) / (n - p)
    se = math.sqrt(correction * sum(value * value for value in cluster_influence))
    return beta[1], se


def monthly_group_means(rows, early_adopter):
    return [
        sum(
            row[OUTCOME]
            for row in rows
            if row["early_adopter"] == early_adopter and row["month_index"] == month
        )
        / 12
        for month in range(1, 37)
    ]


def its_fit(series, target_index, lag=3):
    x = []
    for month in range(1, 37):
        post = float(month >= 19)
        x.append(
            [
                1.0,
                float(month - 18),
                post,
                float(max(0, month - 18)),
                math.sin(2.0 * math.pi * (month - 1) / 12.0),
                math.cos(2.0 * math.pi * (month - 1) / 12.0),
            ]
        )
    gram, beta, residual = regression_parts(x, series)
    p = len(x[0])
    bread_row = solve(gram, [float(index == target_index) for index in range(p)])
    influence = [
        residual_value * sum(left * right for left, right in zip(bread_row, row))
        for row, residual_value in zip(x, residual)
    ]
    variance = sum(value * value for value in influence)
    for distance in range(1, lag + 1):
        weight = 1.0 - distance / (lag + 1.0)
        variance += 2.0 * weight * sum(
            influence[index] * influence[index - distance]
            for index in range(distance, len(influence))
        )
    variance *= len(series) / (len(series) - p)
    return beta[target_index], math.sqrt(variance)


def check(actual, expected, label):
    if abs(actual - expected) > TOLERANCE:
        raise SystemExit(f"CAUSAL_UNIT6_NUMERIC_ERROR {label}: {actual} != {expected}")


def check_record(actual, expected, critical, label):
    estimate, se = actual
    values = {
        "estimate": estimate,
        "se": se,
        "ci95_lower": estimate - critical * se,
        "ci95_upper": estimate + critical * se,
    }
    for key, value in values.items():
        check(value, expected[key], f"{label}.{key}")
    return 4


def main():
    with CSV.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        fieldnames = reader.fieldnames
        raw_rows = list(reader)
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
    checks = 0

    if hashlib.sha256(CSV.read_bytes()).hexdigest() != expected["dataset_sha256"]:
        raise SystemExit("CAUSAL_UNIT6_NUMERIC_ERROR dataset digest")
    checks += 1
    required_fields = {
        "municipality_id", "region", "month_index", "relative_month",
        "early_adopter", "regional_hotline_active", "policy_active", OUTCOME,
    }
    if set(fieldnames or []) != required_fields:
        raise SystemExit("CAUSAL_UNIT6_NUMERIC_ERROR fields")
    checks += 1

    rows = []
    for raw in raw_rows:
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
    if len(rows) != 864 or len(rows) != expected["n_rows"]:
        raise SystemExit("CAUSAL_UNIT6_NUMERIC_ERROR row count")
    checks += 1
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["municipality_id"]].append(row)
    if len(grouped) != 24 or any(len(values) != 36 for values in grouped.values()):
        raise SystemExit("CAUSAL_UNIT6_NUMERIC_ERROR balanced municipality panel")
    checks += 1
    if any(sum(row["month_index"] == month for row in rows) != 24 for month in range(1, 37)):
        raise SystemExit("CAUSAL_UNIT6_NUMERIC_ERROR balanced month panel")
    checks += 1
    if len({row["municipality_id"] for row in rows if row["early_adopter"] == 1}) != 12:
        raise SystemExit("CAUSAL_UNIT6_NUMERIC_ERROR early-adopter count")
    checks += 1
    for region in ("North", "East", "South", "West"):
        members = {row["municipality_id"] for row in rows if row["region"] == region}
        early = {row["municipality_id"] for row in rows if row["region"] == region and row["early_adopter"] == 1}
        if len(members) != 6 or len(early) != 3:
            raise SystemExit(f"CAUSAL_UNIT6_NUMERIC_ERROR {region} allocation")
        checks += 1
    if any(row["relative_month"] != row["month_index"] - 19 for row in rows):
        raise SystemExit("CAUSAL_UNIT6_NUMERIC_ERROR relative month")
    checks += 1
    if any(row["regional_hotline_active"] != int(row["month_index"] >= 19) for row in rows):
        raise SystemExit("CAUSAL_UNIT6_NUMERIC_ERROR hotline timing")
    checks += 1
    if any(row["policy_active"] != row["early_adopter"] * int(row["month_index"] >= 19) for row in rows):
        raise SystemExit("CAUSAL_UNIT6_NUMERIC_ERROR policy timing")
    checks += 1
    if any(not math.isfinite(row[OUTCOME]) for row in rows):
        raise SystemExit("CAUSAL_UNIT6_NUMERIC_ERROR nonfinite outcome")
    checks += 1
    if rows != sorted(rows, key=lambda row: (row["municipality_id"], row["month_index"])):
        raise SystemExit("CAUSAL_UNIT6_NUMERIC_ERROR row order")
    checks += 1

    pre_rows = [dict(row) for row in rows if row["month_index"] <= 18]
    for row in pre_rows:
        row["placebo_active"] = row["early_adopter"] * int(row["month_index"] >= 13)
        row["early_month_slope"] = row["early_adopter"] * (row["month_index"] - 9.5)
    checks += check_record(
        cluster_fit(rows, "policy_active"),
        expected["estimates"]["did_twfe_clustered"], T_CLUSTER_23, "did_twfe_clustered",
    )
    checks += check_record(
        cluster_fit(pre_rows, "placebo_active"),
        expected["estimates"]["preperiod_placebo_did"], T_CLUSTER_23, "preperiod_placebo_did",
    )
    checks += check_record(
        cluster_fit(pre_rows, "early_month_slope"),
        expected["estimates"]["preperiod_differential_slope"], T_CLUSTER_23, "preperiod_differential_slope",
    )

    early_series = monthly_group_means(rows, 1)
    comparison_series = monthly_group_means(rows, 0)
    its_specs = {
        "early_series_its_level_change_hac": (early_series, 2),
        "early_series_its_slope_change_hac": (early_series, 3),
        "comparison_series_its_level_change_hac": (comparison_series, 2),
    }
    for name, spec in its_specs.items():
        checks += check_record(its_fit(*spec), expected["estimates"][name], T_HAC_30, name)

    fresh_means = {}
    for group, label in ((1, "early_adopter"), (0, "not_yet_adopter")):
        for post, period in ((0, "pre"), (1, "post")):
            values = [
                row[OUTCOME] for row in rows
                if row["early_adopter"] == group and int(row["month_index"] >= 19) == post
            ]
            fresh_means[f"{label}_{period}"] = sum(values) / len(values)
    fresh_means["early_before_after_change"] = fresh_means["early_adopter_post"] - fresh_means["early_adopter_pre"]
    fresh_means["comparison_before_after_change"] = fresh_means["not_yet_adopter_post"] - fresh_means["not_yet_adopter_pre"]
    fresh_means["difference_in_changes"] = fresh_means["early_before_after_change"] - fresh_means["comparison_before_after_change"]
    for key, value in fresh_means.items():
        check(value, expected["group_period_means"][key], f"group_period_means.{key}")
        checks += 1
    check(fresh_means["difference_in_changes"], expected["estimates"]["did_twfe_clustered"]["estimate"], "mean DiD equals TWFE")
    checks += 1
    its_difference = its_fit(early_series, 2)[0] - its_fit(comparison_series, 2)[0]
    check(its_difference, expected["its_level_change_difference"], "ITS level difference")
    checks += 1
    check(
        expected["estimates"]["did_twfe_clustered"]["estimate"] - its_difference,
        expected["did_minus_its_level_change_difference"], "DiD minus ITS difference",
    )
    checks += 1
    if expected["known_simulation_policy_effect"] != -1.7:
        raise SystemExit("CAUSAL_UNIT6_NUMERIC_ERROR policy truth record")
    checks += 1
    if expected["known_simulation_regional_hotline_effect"] != -1.05:
        raise SystemExit("CAUSAL_UNIT6_NUMERIC_ERROR hotline truth record")
    checks += 1
    if expected["degrees_of_freedom"] != {"clustered_panel_estimates": 23, "aggregate_its_estimates": 30}:
        raise SystemExit("CAUSAL_UNIT6_NUMERIC_ERROR degrees of freedom")
    checks += 1
    if checks != 52:
        raise SystemExit(f"CAUSAL_UNIT6_NUMERIC_ERROR internal check count {checks}")
    print(f"CAUSAL_UNIT6_INDEPENDENT_OK checks={checks} rows={len(rows)} municipalities={len(grouped)}")


if __name__ == "__main__":
    main()
