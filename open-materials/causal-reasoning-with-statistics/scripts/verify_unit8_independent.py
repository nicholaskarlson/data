#!/usr/bin/env python3
"""Independently recompute Unit 8 with the Python standard library."""

import csv
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data" / "unit8_cognitive_training_trial.csv"
EXPECTED = ROOT / "expected-results" / "unit8_cognitive_training_verified_results.json"
Z_975 = 1.959963985
TOLERANCE = 0.000002


def solve(matrix, vector):
    size = len(vector)
    augmented = [list(matrix[index]) + [vector[index]] for index in range(size)]
    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(augmented[row][column]))
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        scale = augmented[column][column]
        if abs(scale) < 1e-12:
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


def hc1_contrast(x, y, weights):
    p = len(x[0])
    gram = [[sum(row[j] * row[k] for row in x) for k in range(p)] for j in range(p)]
    rhs = [sum(row[j] * value for row, value in zip(x, y)) for j in range(p)]
    beta = solve(gram, rhs)
    residual = [
        value - sum(coefficient * item for coefficient, item in zip(beta, row))
        for row, value in zip(x, y)
    ]
    bread_weights = solve(gram, weights)
    influence = [
        error * sum(left * right for left, right in zip(bread_weights, row))
        for row, error in zip(x, residual)
    ]
    variance = len(x) / (len(x) - p) * sum(value * value for value in influence)
    estimate = sum(weight * coefficient for weight, coefficient in zip(weights, beta))
    return estimate, math.sqrt(variance)


def check(actual, expected, label):
    if abs(actual - expected) > TOLERANCE:
        raise SystemExit(f"CAUSAL_UNIT8_NUMERIC_ERROR {label}: {actual} != {expected}")


def check_record(actual, expected, label):
    estimate, se = actual
    values = {
        "estimate": estimate,
        "se": se,
        "ci95_lower": estimate - Z_975 * se,
        "ci95_upper": estimate + Z_975 * se,
    }
    for key, value in values.items():
        check(value, expected[key], f"{label}.{key}")
    return 4


def main():
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
    with CSV.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames
        rows = [
            {
                "participant_id": row["participant_id"],
                "training_assignment": int(row["training_assignment"]),
                "baseline_memory_score": float(row["baseline_memory_score"]),
                "baseline_high_anxiety": int(row["baseline_high_anxiety"]),
                "strategy_use_score": float(row["strategy_use_score"]),
                "followup_memory_score": float(row["followup_memory_score"]),
            }
            for row in reader
        ]

    checks = 0
    if hashlib.sha256(CSV.read_bytes()).hexdigest() != expected["dataset_sha256"]:
        raise SystemExit("CAUSAL_UNIT8_NUMERIC_ERROR dataset digest")
    checks += 1
    required_fields = {
        "participant_id", "training_assignment", "baseline_memory_score",
        "baseline_high_anxiety", "strategy_use_score", "followup_memory_score",
    }
    if set(fields or []) != required_fields:
        raise SystemExit("CAUSAL_UNIT8_NUMERIC_ERROR fields")
    checks += 1
    if len(rows) != 3200 or expected["n"] != 3200:
        raise SystemExit("CAUSAL_UNIT8_NUMERIC_ERROR row count")
    checks += 1
    if any(
        row["training_assignment"] not in (0, 1)
        or row["baseline_high_anxiety"] not in (0, 1)
        for row in rows
    ):
        raise SystemExit("CAUSAL_UNIT8_NUMERIC_ERROR binary fields")
    checks += 1
    if any(
        not all(math.isfinite(row[key]) for key in (
            "baseline_memory_score", "strategy_use_score", "followup_memory_score"
        ))
        for row in rows
    ):
        raise SystemExit("CAUSAL_UNIT8_NUMERIC_ERROR nonfinite values")
    checks += 1

    allocation = {
        "low_anxiety_training": sum(
            row["baseline_high_anxiety"] == 0 and row["training_assignment"] == 1 for row in rows
        ),
        "low_anxiety_comparison": sum(
            row["baseline_high_anxiety"] == 0 and row["training_assignment"] == 0 for row in rows
        ),
        "high_anxiety_training": sum(
            row["baseline_high_anxiety"] == 1 and row["training_assignment"] == 1 for row in rows
        ),
        "high_anxiety_comparison": sum(
            row["baseline_high_anxiety"] == 1 and row["training_assignment"] == 0 for row in rows
        ),
    }
    if allocation != expected["assignment_counts_by_anxiety"] or allocation != {
        "low_anxiety_training": 960,
        "low_anxiety_comparison": 960,
        "high_anxiety_training": 640,
        "high_anxiety_comparison": 640,
    }:
        raise SystemExit("CAUSAL_UNIT8_NUMERIC_ERROR stratified allocation")
    checks += 4

    a = [float(row["training_assignment"]) for row in rows]
    baseline = [row["baseline_memory_score"] for row in rows]
    anxiety = [float(row["baseline_high_anxiety"]) for row in rows]
    mediator = [row["strategy_use_score"] for row in rows]
    outcome = [row["followup_memory_score"] for row in rows]
    high_share = sum(anxiety) / len(anxiety)
    check(high_share, expected["high_anxiety_share"], "high anxiety share")
    checks += 1

    naive_x = [[1.0, assignment] for assignment in a]
    total_x = [
        [1.0, assignment, base, high, assignment * high]
        for assignment, base, high in zip(a, baseline, anxiety)
    ]
    mediator_x = [
        [1.0, assignment, base, high]
        for assignment, base, high in zip(a, baseline, anxiety)
    ]
    conditioned_x = [
        [1.0, assignment, base, high, assignment * high, strategy]
        for assignment, base, high, strategy in zip(a, baseline, anxiety, mediator)
    ]
    actual = {
        "unadjusted_assignment_itt": hc1_contrast(naive_x, outcome, [0, 1]),
        "baseline_adjusted_standardized_total_effect": hc1_contrast(
            total_x, outcome, [0, 1, 0, 0, high_share]
        ),
        "total_effect_low_anxiety": hc1_contrast(total_x, outcome, [0, 1, 0, 0, 0]),
        "total_effect_high_anxiety": hc1_contrast(total_x, outcome, [0, 1, 0, 0, 1]),
        "assignment_by_anxiety_interaction": hc1_contrast(total_x, outcome, [0, 0, 0, 0, 1]),
        "assignment_effect_on_strategy_use": hc1_contrast(mediator_x, mediator, [0, 1, 0, 0]),
        "mediator_conditioned_assignment_contrast": hc1_contrast(
            conditioned_x, outcome, [0, 1, 0, 0, high_share, 0]
        ),
        "strategy_outcome_conditional_association": hc1_contrast(
            conditioned_x, outcome, [0, 0, 0, 0, 0, 1]
        ),
    }
    for name, values in actual.items():
        checks += check_record(values, expected["estimates"][name], name)

    legacy_product = (
        actual["assignment_effect_on_strategy_use"][0]
        * actual["strategy_outcome_conditional_association"][0]
    )
    legacy_total_minus_conditioned = (
        actual["baseline_adjusted_standardized_total_effect"][0]
        - actual["mediator_conditioned_assignment_contrast"][0]
    )
    check(legacy_product, expected["legacy_product_of_coefficients"], "legacy product")
    check(legacy_total_minus_conditioned, expected["legacy_product_of_coefficients"], "legacy subtraction")
    check(legacy_product - 3.15, 1.598738, "legacy excess over hidden component")
    checks += 3

    for key, selector in (
        ("outcome_assigned", lambda row: row["training_assignment"] == 1),
        ("outcome_comparison", lambda row: row["training_assignment"] == 0),
        ("mediator_assigned", lambda row: row["training_assignment"] == 1),
        ("mediator_comparison", lambda row: row["training_assignment"] == 0),
    ):
        variable = "followup_memory_score" if key.startswith("outcome") else "strategy_use_score"
        values = [row[variable] for row in rows if selector(row)]
        check(sum(values) / len(values), expected["group_means"][key], f"group mean {key}")
        checks += 1

    truth = {
        "known_simulation_average_total_effect": 5.05,
        "known_simulation_total_effect_low_anxiety": 5.65,
        "known_simulation_total_effect_high_anxiety": 4.15,
        "known_simulation_average_controlled_direct_effect": 1.9,
        "known_simulation_strategy_mediated_component": 3.15,
    }
    for key, value in truth.items():
        check(expected[key], value, key)
        checks += 1
    if expected["known_simulation_total_effect_formula"] != "5.65 - 1.5 * baseline_high_anxiety":
        raise SystemExit("CAUSAL_UNIT8_NUMERIC_ERROR total-effect formula")
    if expected["known_simulation_controlled_direct_effect_formula"] != "2.5 - 1.5 * baseline_high_anxiety":
        raise SystemExit("CAUSAL_UNIT8_NUMERIC_ERROR controlled-direct-effect formula")
    checks += 2

    print(
        "CAUSAL_UNIT8_INDEPENDENT_OK",
        f"checks={checks}",
        f"n={len(rows)}",
        f"total={expected['estimates']['baseline_adjusted_standardized_total_effect']['estimate']}",
        f"conditioned={expected['estimates']['mediator_conditioned_assignment_contrast']['estimate']}",
        f"legacy_product={expected['legacy_product_of_coefficients']}",
    )


if __name__ == "__main__":
    main()
