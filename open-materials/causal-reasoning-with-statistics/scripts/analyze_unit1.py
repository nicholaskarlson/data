#!/usr/bin/env python3
"""Primary NumPy analysis for the Unit 1 randomized interface study."""
import csv
import hashlib
import json
import platform
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "unit1_library_interface_ab.csv"
RESULT = ROOT / "expected-results" / "unit1_library_interface_verified_results.json"


def ols_hc1(rows, predictors, outcome="task_score"):
    x = np.array([[1.0] + [row[name] for name in predictors] for row in rows])
    y = np.array([row[outcome] for row in rows])
    beta = np.linalg.lstsq(x, y, rcond=None)[0]
    residuals = y - x @ beta
    bread = np.linalg.inv(x.T @ x)
    meat = x.T @ (x * (residuals * residuals)[:, None])
    covariance = len(rows) / (len(rows) - x.shape[1]) * bread @ meat @ bread
    estimate = float(beta[1])
    se = float(np.sqrt(covariance[1, 1]))
    return {"estimate": round(estimate, 6), "se_hc1": round(se, 6),
            "ci95_lower": round(estimate - 1.96 * se, 6),
            "ci95_upper": round(estimate + 1.96 * se, 6)}


def compute():
    with DATA.open(newline="", encoding="utf-8") as stream:
        rows = []
        for raw in csv.DictReader(stream):
            rows.append({name: float(value) for name, value in raw.items()})
    assigned = np.array([row["redesigned_interface"] for row in rows])
    scores = np.array([row["task_score"] for row in rows])
    skills = np.array([row["baseline_search_skill"] for row in rows])
    clicks = np.array([row["clicks_during_task"] for row in rows])
    estimates = {
        "unadjusted_itt": ols_hc1(rows, ["redesigned_interface"]),
        "baseline_adjusted_itt": ols_hc1(
            rows, ["redesigned_interface", "baseline_search_skill", "difficult_task"]
        ),
        "click_score_association": ols_hc1(rows, ["clicks_during_task"]),
    }
    return {
        "title": "Unit 1 deterministic synthetic library-interface A/B study",
        "dataset_sha256": hashlib.sha256(DATA.read_bytes()).hexdigest(),
        "generator_seed": 20260914,
        "n": len(rows),
        "n_redesigned": int(assigned.sum()),
        "mean_score_standard": round(float(scores[assigned == 0].mean()), 6),
        "mean_score_redesigned": round(float(scores[assigned == 1].mean()), 6),
        "baseline_difference_redesigned_minus_standard": round(
            float(skills[assigned == 1].mean() - skills[assigned == 0].mean()), 6
        ),
        "click_score_correlation": round(float(np.corrcoef(clicks, scores)[0, 1]), 6),
        "known_simulation_assignment_effect": 4.0,
        "estimates": estimates,
        "interval_method": "OLS HC1 sandwich standard errors; normal 1.96 multiplier",
        "identification_note": "Random assignment identifies the effect of assignment to this interface in the synthetic cohort; it does not identify an intervention on clicks or transport to another population.",
        "primary_environment": {"python": platform.python_version(), "numpy": np.__version__},
    }


def main():
    output = compute()
    RESULT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("CAUSAL_UNIT1_PRIMARY_OK", f"n={output['n']}",
          f"itt={output['estimates']['unadjusted_itt']['estimate']}")


if __name__ == "__main__":
    main()
