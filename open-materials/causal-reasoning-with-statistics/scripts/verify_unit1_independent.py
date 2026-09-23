#!/usr/bin/env python3
"""Independently recompute Unit 1 from raw CSV with the standard library."""
import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data" / "unit1_library_interface_ab.csv"
EXPECTED = ROOT / "expected-results" / "unit1_library_interface_verified_results.json"
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
    y = [float(row["task_score"]) for row in rows]
    n, p = len(x), len(x[0])
    gram = [[sum(row[j] * row[k] for row in x) for k in range(p)] for j in range(p)]
    rhs = [sum(row[j] * outcome for row, outcome in zip(x, y)) for j in range(p)]
    beta = solve(gram, rhs)
    treatment_inverse_row = solve(gram, [float(j == 1) for j in range(p)])
    variance = n / (n - p) * sum(
        (outcome - sum(coefficient * value for coefficient, value in zip(beta, row))) ** 2
        * sum(weight * value for weight, value in zip(treatment_inverse_row, row)) ** 2
        for row, outcome in zip(x, y)
    )
    se = math.sqrt(variance)
    return beta[1], se, beta[1] - 1.96 * se, beta[1] + 1.96 * se


def check(actual, expected, label):
    if abs(actual - expected) > TOLERANCE:
        raise SystemExit(f"CAUSAL_UNIT1_NUMERIC_ERROR {label}: {actual} != {expected}")


def main():
    with CSV.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
    if hashlib.sha256(CSV.read_bytes()).hexdigest() != expected["dataset_sha256"]:
        raise SystemExit("CAUSAL_UNIT1_NUMERIC_ERROR dataset digest")
    if len(rows) != expected["n"] or len(rows) != 1800:
        raise SystemExit("CAUSAL_UNIT1_NUMERIC_ERROR row count")
    checks = 2
    specs = {
        "unadjusted_itt": ["redesigned_interface"],
        "baseline_adjusted_itt": ["redesigned_interface", "baseline_search_skill", "difficult_task"],
        "click_score_association": ["clicks_during_task"],
    }
    for name, predictors in specs.items():
        fresh = ols_hc1(rows, predictors)
        for key, value in zip(("estimate", "se_hc1", "ci95_lower", "ci95_upper"), fresh):
            check(value, expected["estimates"][name][key], f"{name}.{key}")
            checks += 1
    redesigned = [row for row in rows if row["redesigned_interface"] == "1"]
    standard = [row for row in rows if row["redesigned_interface"] == "0"]
    if len(redesigned) != expected["n_redesigned"]:
        raise SystemExit("CAUSAL_UNIT1_NUMERIC_ERROR assignment count")
    checks += 1
    for group, key in ((standard, "mean_score_standard"), (redesigned, "mean_score_redesigned")):
        check(sum(float(row["task_score"]) for row in group) / len(group), expected[key], key)
        checks += 1
    baseline_difference = (
        sum(float(row["baseline_search_skill"]) for row in redesigned) / len(redesigned)
        - sum(float(row["baseline_search_skill"]) for row in standard) / len(standard)
    )
    check(baseline_difference, expected["baseline_difference_redesigned_minus_standard"],
          "baseline difference")
    x = [float(row["clicks_during_task"]) for row in rows]
    y = [float(row["task_score"]) for row in rows]
    xbar, ybar = sum(x) / len(x), sum(y) / len(y)
    correlation = sum((a-xbar)*(b-ybar) for a, b in zip(x, y)) / math.sqrt(
        sum((a-xbar)**2 for a in x) * sum((b-ybar)**2 for b in y)
    )
    check(correlation, expected["click_score_correlation"], "click-score correlation")
    if expected["known_simulation_assignment_effect"] != 4.0:
        raise SystemExit("CAUSAL_UNIT1_NUMERIC_ERROR generator effect record")
    checks += 3
    print(f"CAUSAL_UNIT1_INDEPENDENT_OK checks={checks} n={len(rows)}")


if __name__ == "__main__":
    main()
