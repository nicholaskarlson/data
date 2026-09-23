#!/usr/bin/env python3
"""Primary NumPy analysis for the Unit 2 multisite randomized-offer study."""
import csv
import hashlib
import json
import platform
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "unit2_multisite_workshop_offer.csv"
RESULT = ROOT / "expected-results" / "unit2_multisite_workshop_verified_results.json"
SITES = ("Cedar", "Lake", "Ridge")
TARGET_WEIGHTS = {"Cedar": 0.25, "Lake": 0.35, "Ridge": 0.40}


def ols_hc1(rows, predictors, outcome="wellbeing_after"):
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
            "ci95_upper": round(estimate + 1.96 * se, 6),
            "_estimate_raw": estimate, "_variance": float(covariance[1, 1])}


def fixed_weight_summary(site_results, weights):
    estimate = sum(weights[site] * site_results[site][0] for site in SITES)
    variance = sum(weights[site] ** 2 * site_results[site][1] for site in SITES)
    se = variance ** 0.5
    return {
        "estimate": round(estimate, 6), "se_hc1": round(se, 6),
        "ci95_lower": round(estimate - 1.96 * se, 6),
        "ci95_upper": round(estimate + 1.96 * se, 6),
        "_estimate_raw": estimate, "_variance": variance,
    }


def compute():
    with DATA.open(newline="", encoding="utf-8") as stream:
        rows = []
        for raw in csv.DictReader(stream):
            rows.append({
                "person_id": float(raw["person_id"]), "site_name": raw["site"],
                "baseline_stress": float(raw["baseline_stress"]),
                "workshop_offer": float(raw["workshop_offer"]),
                "attended_workshop": float(raw["attended_workshop"]),
                "wellbeing_after": float(raw["wellbeing_after"]),
                "site_lake": float(raw["site"] == "Lake"),
                "site_ridge": float(raw["site"] == "Ridge"),
            })
    offer = np.array([row["workshop_offer"] for row in rows])
    attend = np.array([row["attended_workshop"] for row in rows])
    estimates = {
        "sample_itt": ols_hc1(rows, ["workshop_offer"]),
        "site_adjusted_itt": ols_hc1(
            rows, ["workshop_offer", "site_lake", "site_ridge"]
        ),
        "baseline_site_adjusted_itt": ols_hc1(
            rows, ["workshop_offer", "baseline_stress", "site_lake", "site_ridge"]
        ),
        "naive_attendance_association": ols_hc1(rows, ["attended_workshop"]),
    }
    site_results = {}
    site_raw_results = {}
    for site in SITES:
        selected = [row for row in rows if row["site_name"] == site]
        result = ols_hc1(selected, ["workshop_offer"])
        estimate_raw = result.pop("_estimate_raw")
        variance = result.pop("_variance")
        site_results[site] = result
        site_raw_results[site] = (estimate_raw, variance)
    counts = {site: sum(row["site_name"] == site for row in rows) for site in SITES}
    sample_weights = {site: counts[site] / len(rows) for site in SITES}
    estimates["sample_site_standardized_itt"] = fixed_weight_summary(
        site_raw_results, sample_weights
    )
    estimates["target_standardized_itt"] = fixed_weight_summary(
        site_raw_results, TARGET_WEIGHTS
    )
    decomposition = {
        "pooled_to_sample_site_standardized": round(
            estimates["sample_site_standardized_itt"]["_estimate_raw"]
            - estimates["sample_itt"]["_estimate_raw"], 6
        ),
        "sample_site_to_target_standardized": round(
            estimates["target_standardized_itt"]["_estimate_raw"]
            - estimates["sample_site_standardized_itt"]["_estimate_raw"], 6
        ),
        "pooled_to_target_standardized": round(
            estimates["target_standardized_itt"]["_estimate_raw"]
            - estimates["sample_itt"]["_estimate_raw"], 6
        ),
    }
    for result in estimates.values():
        result.pop("_estimate_raw", None)
        result.pop("_variance", None)
    site_offer_counts = {
        site: sum(row["site_name"] == site and row["workshop_offer"] == 1 for row in rows)
        for site in SITES
    }
    site_offer_rates = {
        site: round(site_offer_counts[site] / counts[site], 6) for site in SITES
    }
    return {
        "title": "Unit 2 deterministic synthetic multisite randomized-offer study",
        "dataset_sha256": hashlib.sha256(DATA.read_bytes()).hexdigest(),
        "generator_seed": 20260915,
        "n": len(rows),
        "n_offered": int(offer.sum()),
        "n_attended": int(attend.sum()),
        "uptake_among_offered": round(float(attend[offer == 1].mean()), 6),
        "site_sample_counts": counts,
        "site_offer_counts": site_offer_counts,
        "site_offer_rates": site_offer_rates,
        "sample_site_weights": sample_weights,
        "target_site_weights": TARGET_WEIGHTS,
        "site_itt_estimates": site_results,
        "estimates": estimates,
        "standardization_decomposition": decomposition,
        "known_simulation_offer_effect_note": "Individual offer effects equal 0.4 plus a site-specific attendance effect for people who would attend if offered; the response type and structural effects are unavailable from the analyst CSV.",
        "interval_method": "OLS HC1 within-site variances; normal 1.96 multiplier; standardized variances are sums of squared fixed sample or target weights times independent site variances",
        "identification_note": "Bernoulli randomization identifies the offer ITT in the recruited sample. The pooled and recruited-site-share standardized contrasts are different realized estimators of that sample effect. Target standardization additionally assumes site-specific effects transport to the stated target site mixture.",
        "primary_environment": {"python": platform.python_version(), "numpy": np.__version__},
    }


def main():
    output = compute()
    RESULT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("CAUSAL_UNIT2_PRIMARY_OK", f"n={output['n']}",
          f"sample_itt={output['estimates']['sample_itt']['estimate']}",
          f"sample_standardized_itt={output['estimates']['sample_site_standardized_itt']['estimate']}",
          f"target_itt={output['estimates']['target_standardized_itt']['estimate']}")


if __name__ == "__main__":
    main()
