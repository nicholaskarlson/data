#!/usr/bin/env python3
"""Independently recompute Unit 4 from the raw CSV with the standard library."""

import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data" / "unit4_cluster_sleep_trial.csv"
EXPECTED = ROOT / "expected-results" / "unit4_cluster_sleep_trial_verified_results.json"
SECTORS = ("North", "East", "South", "West")
T_CRITICAL = {43: 2.016692199, 42: 2.018081703}
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


def ols_hc1(rows, predictors, outcome, critical):
    x = [[1.0] + [float(row[name]) for name in predictors] for row in rows]
    y = [float(row[outcome]) for row in rows]
    n, p = len(x), len(x[0])
    gram = [[sum(row[j] * row[k] for row in x) for k in range(p)] for j in range(p)]
    rhs = [sum(row[j] * value for row, value in zip(x, y)) for j in range(p)]
    beta = solve(gram, rhs)
    treatment_inverse_row = solve(gram, [float(index == 1) for index in range(p)])
    variance = n / (n - p) * sum(
        (value - sum(coefficient * item for coefficient, item in zip(beta, row))) ** 2
        * sum(weight * item for weight, item in zip(treatment_inverse_row, row)) ** 2
        for row, value in zip(x, y)
    )
    se = math.sqrt(variance)
    return beta[1], se, beta[1] - critical * se, beta[1] + critical * se


def check(actual, expected, label):
    if abs(actual - expected) > TOLERANCE:
        raise SystemExit(f"CAUSAL_UNIT4_NUMERIC_ERROR {label}: {actual} != {expected}")


def enrich(row):
    output = dict(row)
    for index, sector in enumerate(SECTORS[1:], start=1):
        output[f"sector_{index}"] = float(row["campus_sector"] == sector)
    return output


def main():
    with CSV.open(newline="", encoding="utf-8") as stream:
        raw_rows = list(csv.DictReader(stream))
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
    checks = 0

    if hashlib.sha256(CSV.read_bytes()).hexdigest() != expected["dataset_sha256"]:
        raise SystemExit("CAUSAL_UNIT4_NUMERIC_ERROR dataset digest")
    checks += 1
    if len(raw_rows) != expected["n_students"] or len(raw_rows) != 2400:
        raise SystemExit("CAUSAL_UNIT4_NUMERIC_ERROR row count")
    checks += 1

    rows = []
    for raw in raw_rows:
        row = {
            "student_id": raw["student_id"],
            "campus_sector": raw["campus_sector"],
            "residence_floor_id": raw["residence_floor_id"],
            "assigned_sleep_program": float(raw["assigned_sleep_program"]),
            "baseline_sleep_hours": float(raw["baseline_sleep_hours"]),
            "baseline_attention_score": float(raw["baseline_attention_score"]),
            "used_sleep_plan": float(raw["used_sleep_plan"]),
            "completed_sleep_diary": float(raw["completed_sleep_diary"]),
            "followup_sleep_hours": (
                None if raw["followup_sleep_hours"] == "" else float(raw["followup_sleep_hours"])
            ),
            "followup_attention_score": float(raw["followup_attention_score"]),
        }
        rows.append(enrich(row))

    grouped = defaultdict(list)
    for row in rows:
        grouped[row["residence_floor_id"]].append(row)
    if len(grouped) != expected["n_floors"] or len(grouped) != 48:
        raise SystemExit("CAUSAL_UNIT4_NUMERIC_ERROR floor count")
    checks += 1
    if sorted(len(members) for members in grouped.values()) != [50] * 48:
        raise SystemExit("CAUSAL_UNIT4_NUMERIC_ERROR floor sizes")
    checks += 1
    if len({row["student_id"] for row in rows}) != len(rows):
        raise SystemExit("CAUSAL_UNIT4_NUMERIC_ERROR duplicate student ID")
    checks += 1
    if any(not math.isfinite(row["followup_attention_score"]) for row in rows):
        raise SystemExit("CAUSAL_UNIT4_NUMERIC_ERROR missing primary outcome")
    checks += 1
    if any((row["followup_sleep_hours"] is not None) != bool(row["completed_sleep_diary"]) for row in rows):
        raise SystemExit("CAUSAL_UNIT4_NUMERIC_ERROR diary missingness declaration")
    checks += 1

    floors = []
    for floor_id in sorted(grouped):
        members = grouped[floor_id]
        assignments = {row["assigned_sleep_program"] for row in members}
        if len(assignments) != 1:
            raise SystemExit("CAUSAL_UNIT4_NUMERIC_ERROR assignment varies within floor")
        floor = {
            "residence_floor_id": floor_id,
            "campus_sector": members[0]["campus_sector"],
            "assigned_sleep_program": members[0]["assigned_sleep_program"],
            "followup_attention_score": sum(
                row["followup_attention_score"] for row in members
            ) / len(members),
            "baseline_attention_score": sum(
                row["baseline_attention_score"] for row in members
            ) / len(members),
        }
        floor["attention_change"] = floor["followup_attention_score"] - floor["baseline_attention_score"]
        floors.append(enrich(floor))
    checks += 1

    program_floors = [floor for floor in floors if floor["assigned_sleep_program"] == 1.0]
    if len(program_floors) != expected["n_program_floors"] or len(program_floors) != 24:
        raise SystemExit("CAUSAL_UNIT4_NUMERIC_ERROR program floor count")
    checks += 1
    program_students = sum(row["assigned_sleep_program"] == 1.0 for row in rows)
    if program_students != expected["n_program_students"] or program_students != 1200:
        raise SystemExit("CAUSAL_UNIT4_NUMERIC_ERROR program student count")
    checks += 1
    for sector in SECTORS:
        actual_program = sum(
            floor["campus_sector"] == sector and floor["assigned_sleep_program"] == 1.0
            for floor in floors
        )
        actual_control = sum(
            floor["campus_sector"] == sector and floor["assigned_sleep_program"] == 0.0
            for floor in floors
        )
        if (actual_program, actual_control) != (6, 6):
            raise SystemExit(f"CAUSAL_UNIT4_NUMERIC_ERROR {sector} blocked allocation")
        checks += 1

    specs = {
        "individual_hc1_itt": (
            rows,
            ["assigned_sleep_program", "sector_1", "sector_2", "sector_3"],
            "followup_attention_score",
            1.96,
        ),
        "floor_blocked_itt": (
            floors,
            ["assigned_sleep_program", "sector_1", "sector_2", "sector_3"],
            "followup_attention_score",
            T_CRITICAL[43],
        ),
        "floor_baseline_adjusted_itt": (
            floors,
            ["assigned_sleep_program", "baseline_attention_score", "sector_1", "sector_2", "sector_3"],
            "followup_attention_score",
            T_CRITICAL[42],
        ),
        "floor_change_score_itt": (
            floors,
            ["assigned_sleep_program", "sector_1", "sector_2", "sector_3"],
            "attention_change",
            T_CRITICAL[43],
        ),
        "naive_receipt_association": (
            rows,
            ["used_sleep_plan", "baseline_attention_score", "sector_1", "sector_2", "sector_3"],
            "followup_attention_score",
            1.96,
        ),
    }
    for name, spec in specs.items():
        fresh = ols_hc1(*spec)
        for key, value in zip(("estimate", "se", "ci95_lower", "ci95_upper"), fresh):
            check(value, expected["estimates"][name][key], f"{name}.{key}")
            checks += 1

    def rate(field, assignment):
        selected = [row[field] for row in rows if row["assigned_sleep_program"] == assignment]
        return sum(selected) / len(selected)

    for assignment, label in ((0.0, "usual_information"), (1.0, "assigned_program")):
        check(rate("used_sleep_plan", assignment), expected["receipt_rates"][label], f"receipt {label}")
        checks += 1
        check(
            rate("completed_sleep_diary", assignment),
            expected["diary_completion_rates"][label],
            f"diary {label}",
        )
        checks += 1
    diary_completion_difference = (
        rate("completed_sleep_diary", 1.0)
        - rate("completed_sleep_diary", 0.0)
    )
    if (
        round(diary_completion_difference, 6)
        != expected["diary_completion_rate_difference"]
    ):
        raise SystemExit(
            "CAUSAL_UNIT4_NUMERIC_ERROR diary completion difference: "
            f"round({diary_completion_difference}, 6) != "
            f"{expected['diary_completion_rate_difference']}"
        )
    checks += 1
    baseline_difference = (
        sum(floor["baseline_attention_score"] for floor in program_floors) / len(program_floors)
        - sum(
            floor["baseline_attention_score"]
            for floor in floors
            if floor["assigned_sleep_program"] == 0.0
        )
        / 24
    )
    check(baseline_difference, expected["baseline_floor_mean_difference"], "baseline floor difference")
    checks += 1
    if expected["known_simulation_assignment_effect"] != 3.0:
        raise SystemExit("CAUSAL_UNIT4_NUMERIC_ERROR generator effect record")
    checks += 1
    if checks != 41:
        raise SystemExit(f"CAUSAL_UNIT4_NUMERIC_ERROR internal check count {checks}")
    print(f"CAUSAL_UNIT4_INDEPENDENT_OK checks={checks} students={len(rows)} floors={len(floors)}")


if __name__ == "__main__":
    main()
