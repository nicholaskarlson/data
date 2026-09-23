#!/usr/bin/env python3
"""Primary worked analysis: OLS with HC1 standard errors, from raw CSV only."""
import csv
import hashlib
import json
import platform
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/psychology_memory_training.csv"
RESULT = ROOT / "expected-results/psychology_memory_training_verified_results.json"
SPECS = {
    "naive": ["training"],
    "baseline_adjusted": ["training", "baseline_memory"],
    "collider_adjusted": ["training", "baseline_memory", "help_seeking_after"],
    "mediator_adjusted": ["training", "baseline_memory", "engagement_after"],
}


def compute():
    with DATA.open(newline="", encoding="utf-8") as f:
        rows = [{key: float(value) for key, value in r.items()} for r in csv.DictReader(f)]
    n = len(rows)
    if n != 2400 or any(len(r) != 6 for r in rows):
        raise ValueError("unexpected row or column count")
    values = np.array([[r[k] for k in ("training", "baseline_memory", "help_seeking_after",
                                        "engagement_after", "memory_after")] for r in rows])
    estimates = {}
    for name, predictors in SPECS.items():
        x = np.array([[1.0] + [r[p] for p in predictors] for r in rows])
        y = np.array([r["memory_after"] for r in rows])
        beta = np.linalg.lstsq(x, y, rcond=None)[0]
        resid = y - x @ beta
        bread = np.linalg.inv(x.T @ x)
        meat = x.T @ (x * (resid * resid)[:, None])
        covariance = (n / (n - x.shape[1])) * bread @ meat @ bread  # HC1
        se = float(np.sqrt(covariance[1, 1]))
        b = float(beta[1])
        estimates[name] = {"estimate": round(b, 6), "se_hc1": round(se, 6),
                           "ci95_lower": round(b - 1.96 * se, 6),
                           "ci95_upper": round(b + 1.96 * se, 6)}
    a = values[:, 0]
    b = values[:, 1]
    quintile_cuts = np.quantile(b, [0, .2, .4, .6, .8, 1])
    rates = []
    for j in range(5):
        members = (b >= quintile_cuts[j]) & (b <= quintile_cuts[j+1] if j == 4 else b < quintile_cuts[j+1])
        rates.append(round(float(a[members].mean()), 6))
    return {
        "title": "Deterministic synthetic memory-training study; not evidence about people",
        "dataset_sha256": hashlib.sha256(DATA.read_bytes()).hexdigest(),
        "generator_seed": 20260912,
        "n": n,
        "n_training": int(a.sum()),
        "baseline_difference_training_minus_comparison": round(float(b[a == 1].mean() - b[a == 0].mean()), 6),
        "baseline_quintile_training_rates": rates,
        "known_simulation_total_effect": 2.0,
        "known_simulation_controlled_direct_effect": 0.8,
        "estimates": estimates,
        "interval_method": "OLS HC1 sandwich standard errors; normal 1.96 multiplier",
        "identification_note": "The numerical known truth comes from the generator, not the analyst CSV.",
        "primary_environment": {"python": platform.python_version(), "numpy": np.__version__},
    }


def main():
    output = compute()
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("CAUSAL_PRIMARY_ANALYSIS_OK", "n=" + str(output["n"]),
          "baseline_adjusted=" + str(output["estimates"]["baseline_adjusted"]["estimate"]))


if __name__ == "__main__":
    main()
