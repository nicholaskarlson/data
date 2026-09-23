#!/usr/bin/env python3
"""Independently recompute Unit 2 from raw CSV with the standard library."""
import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data" / "unit2_multisite_workshop_offer.csv"
EXPECTED = ROOT / "expected-results" / "unit2_multisite_workshop_verified_results.json"
SITES = ("Cedar", "Lake", "Ridge")
TOLERANCE = 0.000002


def solve(matrix, vector):
    n = len(vector)
    augmented = [list(matrix[i]) + [vector[i]] for i in range(n)]
    for column in range(n):
        pivot = max(range(column, n), key=lambda row: abs(augmented[row][column]))
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        scale = augmented[column][column]
        if abs(scale) < 1e-10:
            raise ValueError("singular normal equations")
        augmented[column] = [value / scale for value in augmented[column]]
        for row in range(n):
            if row == column:
                continue
            factor = augmented[row][column]
            augmented[row] = [left - factor * right
                              for left, right in zip(augmented[row], augmented[column])]
    return [row[-1] for row in augmented]


def ols_hc1(rows, predictors):
    x = [[1.0] + [float(row[name]) for name in predictors] for row in rows]
    y = [float(row["wellbeing_after"]) for row in rows]
    n, p = len(x), len(x[0])
    gram = [[sum(row[j] * row[k] for row in x) for k in range(p)] for j in range(p)]
    rhs = [sum(row[j] * outcome for row, outcome in zip(x, y)) for j in range(p)]
    beta = solve(gram, rhs)
    coefficient_inverse_row = solve(gram, [float(j == 1) for j in range(p)])
    variance = n / (n - p) * sum(
        (outcome - sum(coefficient * value for coefficient, value in zip(beta, row))) ** 2
        * sum(weight * value for weight, value in zip(coefficient_inverse_row, row)) ** 2
        for row, outcome in zip(x, y)
    )
    se = math.sqrt(variance)
    return beta[1], se, beta[1] - 1.96 * se, beta[1] + 1.96 * se, variance


def check(actual, expected, label):
    if abs(actual - expected) > TOLERANCE:
        raise SystemExit(f"CAUSAL_UNIT2_NUMERIC_ERROR {label}: {actual} != {expected}")


def main():
    with CSV.open(newline="", encoding="utf-8") as stream:
        rows = []
        for raw in csv.DictReader(stream):
            raw["site_lake"] = str(int(raw["site"] == "Lake"))
            raw["site_ridge"] = str(int(raw["site"] == "Ridge"))
            rows.append(raw)
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
    if hashlib.sha256(CSV.read_bytes()).hexdigest() != expected["dataset_sha256"]:
        raise SystemExit("CAUSAL_UNIT2_NUMERIC_ERROR dataset digest")
    if len(rows) != expected["n"] or len(rows) != 2400:
        raise SystemExit("CAUSAL_UNIT2_NUMERIC_ERROR row count")
    checks = 2
    specs = {
        "sample_itt": ["workshop_offer"],
        "site_adjusted_itt": ["workshop_offer", "site_lake", "site_ridge"],
        "baseline_site_adjusted_itt": ["workshop_offer", "baseline_stress", "site_lake", "site_ridge"],
        "naive_attendance_association": ["attended_workshop"],
    }
    for name, predictors in specs.items():
        fresh = ols_hc1(rows, predictors)
        for key, value in zip(("estimate", "se_hc1", "ci95_lower", "ci95_upper"), fresh[:4]):
            check(value, expected["estimates"][name][key], f"{name}.{key}")
            checks += 1
    site_fresh = {}
    for site in SITES:
        selected = [row for row in rows if row["site"] == site]
        if len(selected) != expected["site_sample_counts"][site]:
            raise SystemExit(f"CAUSAL_UNIT2_NUMERIC_ERROR {site} sample count")
        checks += 1
        fresh = ols_hc1(selected, ["workshop_offer"])
        site_fresh[site] = (fresh[0], fresh[4])
        for key, value in zip(("estimate", "se_hc1", "ci95_lower", "ci95_upper"), fresh[:4]):
            check(value, expected["site_itt_estimates"][site][key], f"{site}.{key}")
            checks += 1
        offered_at_site = sum(row["workshop_offer"] == "1" for row in selected)
        if offered_at_site != expected["site_offer_counts"][site]:
            raise SystemExit(f"CAUSAL_UNIT2_NUMERIC_ERROR {site} offer count")
        checks += 1
        check(
            offered_at_site / len(selected), expected["site_offer_rates"][site],
            f"{site}.offer_rate",
        )
        checks += 1

    fresh_sample_weights = {
        site: expected["site_sample_counts"][site] / len(rows) for site in SITES
    }
    for site in SITES:
        check(
            fresh_sample_weights[site], expected["sample_site_weights"][site],
            f"{site}.sample_weight",
        )
        checks += 1
    if abs(sum(expected["sample_site_weights"].values()) - 1.0) > 1e-12:
        raise SystemExit("CAUSAL_UNIT2_NUMERIC_ERROR sample weights")
    checks += 1
    if expected["target_site_weights"] != {"Cedar": 0.25, "Lake": 0.35, "Ridge": 0.40}:
        raise SystemExit("CAUSAL_UNIT2_NUMERIC_ERROR declared target weights")
    checks += 1
    if abs(sum(expected["target_site_weights"].values()) - 1.0) > 1e-12:
        raise SystemExit("CAUSAL_UNIT2_NUMERIC_ERROR target weights")
    checks += 1

    standardized_estimates = {}
    for name, weights in (
        ("sample_site_standardized_itt", fresh_sample_weights),
        ("target_standardized_itt", expected["target_site_weights"]),
    ):
        estimate = sum(weights[site] * site_fresh[site][0] for site in SITES)
        standardized_estimates[name] = estimate
        variance = sum(weights[site] ** 2 * site_fresh[site][1] for site in SITES)
        se = math.sqrt(variance)
        fresh = (estimate, se, estimate - 1.96 * se, estimate + 1.96 * se)
        for key, value in zip(("estimate", "se_hc1", "ci95_lower", "ci95_upper"), fresh):
            check(value, expected["estimates"][name][key], f"{name}.{key}")
            checks += 1

    fresh_decomposition = {
        "pooled_to_sample_site_standardized": (
            standardized_estimates["sample_site_standardized_itt"]
            - ols_hc1(rows, ["workshop_offer"])[0]
        ),
        "sample_site_to_target_standardized": (
            standardized_estimates["target_standardized_itt"]
            - standardized_estimates["sample_site_standardized_itt"]
        ),
        "pooled_to_target_standardized": (
            standardized_estimates["target_standardized_itt"]
            - ols_hc1(rows, ["workshop_offer"])[0]
        ),
    }
    for name, value in fresh_decomposition.items():
        check(value, expected["standardization_decomposition"][name], name)
        checks += 1

    offered = [row for row in rows if row["workshop_offer"] == "1"]
    attended = [row for row in rows if row["attended_workshop"] == "1"]
    if len(offered) != expected["n_offered"]:
        raise SystemExit("CAUSAL_UNIT2_NUMERIC_ERROR offer count")
    checks += 1
    if len(attended) != expected["n_attended"]:
        raise SystemExit("CAUSAL_UNIT2_NUMERIC_ERROR attendance count")
    checks += 1
    check(len(attended) / len(offered), expected["uptake_among_offered"], "uptake")
    checks += 1
    print(f"CAUSAL_UNIT2_INDEPENDENT_OK checks={checks} n={len(rows)}")


if __name__ == "__main__":
    main()
