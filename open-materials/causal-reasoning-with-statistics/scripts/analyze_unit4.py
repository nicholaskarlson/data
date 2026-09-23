#!/usr/bin/env python3
"""Primary NumPy analysis for the Unit 4 cluster-randomized sleep trial."""

import csv
import hashlib
import json
import platform
from collections import defaultdict
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "unit4_cluster_sleep_trial.csv"
RESULT = ROOT / "expected-results" / "unit4_cluster_sleep_trial_verified_results.json"
SECTORS = ("North", "East", "South", "West")
T_CRITICAL = {43: 2.016692199, 42: 2.018081703}


def read_rows():
    rows = []
    with DATA.open(newline="", encoding="utf-8") as stream:
        for raw in csv.DictReader(stream):
            rows.append(
                {
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
            )
    return rows


def sector_dummies(row):
    return [float(row["campus_sector"] == name) for name in SECTORS[1:]]


def ols_hc1(rows, predictors, outcome, critical):
    x = np.array([[1.0] + [row[name] for name in predictors] for row in rows], dtype=float)
    y = np.array([row[outcome] for row in rows], dtype=float)
    beta = np.linalg.lstsq(x, y, rcond=None)[0]
    residuals = y - x @ beta
    bread = np.linalg.inv(x.T @ x)
    meat = x.T @ (x * (residuals * residuals)[:, None])
    covariance = len(rows) / (len(rows) - x.shape[1]) * bread @ meat @ bread
    estimate = float(beta[1])
    se = float(np.sqrt(covariance[1, 1]))
    return {
        "estimate": round(estimate, 6),
        "se": round(se, 6),
        "ci95_lower": round(estimate - critical * se, 6),
        "ci95_upper": round(estimate + critical * se, 6),
    }


def add_model_columns(rows):
    output = []
    for row in rows:
        enriched = dict(row)
        for index, value in enumerate(sector_dummies(row), start=1):
            enriched[f"sector_{index}"] = value
        output.append(enriched)
    return output


def floor_means(rows):
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["residence_floor_id"]].append(row)
    floors = []
    for floor_id in sorted(grouped):
        members = grouped[floor_id]
        floor = {
            "residence_floor_id": floor_id,
            "campus_sector": members[0]["campus_sector"],
            "assigned_sleep_program": members[0]["assigned_sleep_program"],
            "followup_attention_score": float(
                np.mean([row["followup_attention_score"] for row in members])
            ),
            "baseline_attention_score": float(
                np.mean([row["baseline_attention_score"] for row in members])
            ),
        }
        floor["attention_change"] = (
            floor["followup_attention_score"] - floor["baseline_attention_score"]
        )
        floors.append(floor)
    return add_model_columns(floors)


def rate(rows, field, assignment):
    selected = [row[field] for row in rows if row["assigned_sleep_program"] == assignment]
    return float(np.mean(selected))


def compute():
    rows = add_model_columns(read_rows())
    floors = floor_means(rows)
    individual_predictors = ["assigned_sleep_program", "sector_1", "sector_2", "sector_3"]
    floor_predictors = ["assigned_sleep_program", "sector_1", "sector_2", "sector_3"]
    estimates = {
        "individual_hc1_itt": ols_hc1(
            rows, individual_predictors, "followup_attention_score", 1.96
        ),
        "floor_blocked_itt": ols_hc1(
            floors, floor_predictors, "followup_attention_score", T_CRITICAL[43]
        ),
        "floor_baseline_adjusted_itt": ols_hc1(
            floors,
            ["assigned_sleep_program", "baseline_attention_score", "sector_1", "sector_2", "sector_3"],
            "followup_attention_score",
            T_CRITICAL[42],
        ),
        "floor_change_score_itt": ols_hc1(
            floors, floor_predictors, "attention_change", T_CRITICAL[43]
        ),
        "naive_receipt_association": ols_hc1(
            rows,
            ["used_sleep_plan", "baseline_attention_score", "sector_1", "sector_2", "sector_3"],
            "followup_attention_score",
            1.96,
        ),
    }
    receipt_rates = {
        "usual_information": round(rate(rows, "used_sleep_plan", 0.0), 6),
        "assigned_program": round(rate(rows, "used_sleep_plan", 1.0), 6),
    }
    diary_rates_raw = {
        "usual_information": rate(rows, "completed_sleep_diary", 0.0),
        "assigned_program": rate(rows, "completed_sleep_diary", 1.0),
    }
    diary_rates = {
        label: round(value, 6) for label, value in diary_rates_raw.items()
    }
    treatment_floors = [floor for floor in floors if floor["assigned_sleep_program"] == 1.0]
    control_floors = [floor for floor in floors if floor["assigned_sleep_program"] == 0.0]
    baseline_difference = np.mean(
        [floor["baseline_attention_score"] for floor in treatment_floors]
    ) - np.mean([floor["baseline_attention_score"] for floor in control_floors])
    return {
        "title": "Unit 4 deterministic blocked cluster-randomized sleep-program trial",
        "dataset_sha256": hashlib.sha256(DATA.read_bytes()).hexdigest(),
        "generator_seed": 20260916,
        "n_students": len(rows),
        "n_floors": len(floors),
        "students_per_floor": 50,
        "n_program_floors": len(treatment_floors),
        "n_program_students": sum(
            row["assigned_sleep_program"] == 1.0 for row in rows
        ),
        "sector_floor_counts": {
            sector: {
                "program": sum(
                    floor["campus_sector"] == sector
                    and floor["assigned_sleep_program"] == 1.0
                    for floor in floors
                ),
                "usual_information": sum(
                    floor["campus_sector"] == sector
                    and floor["assigned_sleep_program"] == 0.0
                    for floor in floors
                ),
            }
            for sector in SECTORS
        },
        "receipt_rates": receipt_rates,
        "diary_completion_rates": diary_rates,
        "diary_completion_rate_difference": round(
            diary_rates_raw["assigned_program"]
            - diary_rates_raw["usual_information"],
            6,
        ),
        "baseline_floor_mean_difference": round(float(baseline_difference), 6),
        "individual_to_floor_se_ratio": round(
            estimates["individual_hc1_itt"]["se"] / estimates["floor_blocked_itt"]["se"], 6
        ),
        "known_simulation_assignment_effect": 3.0,
        "estimates": estimates,
        "degrees_of_freedom": {
            "floor_blocked_itt": 43,
            "floor_baseline_adjusted_itt": 42,
            "floor_change_score_itt": 43,
        },
        "interval_method": (
            "Individual-level descriptive rows use HC1 and 1.96. Preferred floor-level analyses "
            "use HC1 across 48 randomized floors and two-sided t critical values based on model residual degrees of freedom."
        ),
        "identification_note": (
            "Blocked floor assignment identifies the offer-policy ITT for the synthetic enrolled cohort "
            "under consistency, no cross-floor interference, correct assignment, and complete primary-outcome ascertainment."
        ),
        "primary_environment": {"python": platform.python_version(), "numpy": np.__version__},
    }


def main():
    output = compute()
    RESULT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "CAUSAL_UNIT4_PRIMARY_OK",
        f"students={output['n_students']}",
        f"floors={output['n_floors']}",
        f"itt={output['estimates']['floor_blocked_itt']['estimate']}",
    )


if __name__ == "__main__":
    main()
