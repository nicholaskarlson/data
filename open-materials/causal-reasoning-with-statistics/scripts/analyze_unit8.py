#!/usr/bin/env python3
"""Primary NumPy analysis for Unit 8 mediation and heterogeneity."""

import csv
import hashlib
import json
import math
import platform
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "unit8_cognitive_training_trial.csv"
RESULT = ROOT / "expected-results" / "unit8_cognitive_training_verified_results.json"
Z_975 = 1.959963985


def read_rows():
    with DATA.open(newline="", encoding="utf-8") as stream:
        return [
            {
                "participant_id": row["participant_id"],
                "training_assignment": int(row["training_assignment"]),
                "baseline_memory_score": float(row["baseline_memory_score"]),
                "baseline_high_anxiety": int(row["baseline_high_anxiety"]),
                "strategy_use_score": float(row["strategy_use_score"]),
                "followup_memory_score": float(row["followup_memory_score"]),
            }
            for row in csv.DictReader(stream)
        ]


def hc1_fit(x, y):
    beta = np.linalg.lstsq(x, y, rcond=None)[0]
    residual = y - x @ beta
    bread = np.linalg.inv(x.T @ x)
    meat = x.T @ ((residual * residual)[:, None] * x)
    n, p = x.shape
    covariance = n / (n - p) * bread @ meat @ bread
    return beta, covariance


def contrast(beta, covariance, weights):
    weights = np.asarray(weights, dtype=float)
    estimate = float(weights @ beta)
    se = math.sqrt(float(weights @ covariance @ weights))
    return estimate, se


def record(estimate, se):
    return {
        "estimate": round(estimate, 6),
        "se": round(se, 6),
        "ci95_lower": round(estimate - Z_975 * se, 6),
        "ci95_upper": round(estimate + Z_975 * se, 6),
    }


def compute():
    rows = read_rows()
    a = np.asarray([row["training_assignment"] for row in rows], dtype=float)
    baseline = np.asarray([row["baseline_memory_score"] for row in rows])
    anxiety = np.asarray([row["baseline_high_anxiety"] for row in rows], dtype=float)
    mediator = np.asarray([row["strategy_use_score"] for row in rows])
    outcome = np.asarray([row["followup_memory_score"] for row in rows])
    n = len(rows)
    high_share = float(anxiety.mean())

    beta_naive, covariance_naive = hc1_fit(
        np.column_stack([np.ones(n), a]), outcome
    )
    naive = contrast(beta_naive, covariance_naive, [0, 1])

    total_x = np.column_stack([np.ones(n), a, baseline, anxiety, a * anxiety])
    beta_total, covariance_total = hc1_fit(total_x, outcome)
    total_average = contrast(
        beta_total, covariance_total, [0, 1, 0, 0, high_share]
    )
    total_low = contrast(beta_total, covariance_total, [0, 1, 0, 0, 0])
    total_high = contrast(beta_total, covariance_total, [0, 1, 0, 0, 1])
    interaction = contrast(beta_total, covariance_total, [0, 0, 0, 0, 1])

    mediator_x = np.column_stack([np.ones(n), a, baseline, anxiety])
    beta_mediator, covariance_mediator = hc1_fit(mediator_x, mediator)
    first_stage = contrast(beta_mediator, covariance_mediator, [0, 1, 0, 0])

    conditioned_x = np.column_stack(
        [np.ones(n), a, baseline, anxiety, a * anxiety, mediator]
    )
    beta_conditioned, covariance_conditioned = hc1_fit(conditioned_x, outcome)
    conditioned_average = contrast(
        beta_conditioned,
        covariance_conditioned,
        [0, 1, 0, 0, high_share, 0],
    )
    mediator_association = contrast(
        beta_conditioned, covariance_conditioned, [0, 0, 0, 0, 0, 1]
    )
    legacy_product = first_stage[0] * mediator_association[0]
    legacy_total_minus_conditioned = total_average[0] - conditioned_average[0]
    if round(legacy_product, 6) != 4.748738:
        raise RuntimeError("Unit 8 legacy product-of-coefficients result drifted")
    if abs(legacy_product - legacy_total_minus_conditioned) > 0.000002:
        raise RuntimeError("Unit 8 legacy mediation arithmetic no longer agrees")
    if round(legacy_product - 3.15, 6) != 1.598738:
        raise RuntimeError("Unit 8 legacy hidden-quantity comparison drifted")

    group_means = {
        "outcome_assigned": round(float(outcome[a == 1].mean()), 6),
        "outcome_comparison": round(float(outcome[a == 0].mean()), 6),
        "mediator_assigned": round(float(mediator[a == 1].mean()), 6),
        "mediator_comparison": round(float(mediator[a == 0].mean()), 6),
    }
    truth = {
        "known_simulation_total_effect_formula": "5.65 - 1.5 * baseline_high_anxiety",
        "known_simulation_average_total_effect": 5.05,
        "known_simulation_total_effect_low_anxiety": 5.65,
        "known_simulation_total_effect_high_anxiety": 4.15,
        "known_simulation_controlled_direct_effect_formula": "2.5 - 1.5 * baseline_high_anxiety",
        "known_simulation_average_controlled_direct_effect": 1.9,
        "known_simulation_strategy_mediated_component": 3.15,
    }

    return {
        "title": "Unit 8 deterministic cognitive-training trial",
        "generator_seed": 20260929,
        "dataset_filename": DATA.name,
        "dataset_sha256": hashlib.sha256(DATA.read_bytes()).hexdigest(),
        "n": n,
        "n_training": int(a.sum()),
        "n_comparison": int(n - a.sum()),
        "n_high_anxiety": int(anxiety.sum()),
        "n_low_anxiety": int(n - anxiety.sum()),
        "high_anxiety_share": round(high_share, 6),
        "assignment_counts_by_anxiety": {
            "low_anxiety_training": int(np.sum((anxiety == 0) & (a == 1))),
            "low_anxiety_comparison": int(np.sum((anxiety == 0) & (a == 0))),
            "high_anxiety_training": int(np.sum((anxiety == 1) & (a == 1))),
            "high_anxiety_comparison": int(np.sum((anxiety == 1) & (a == 0))),
        },
        "group_means": group_means,
        "legacy_product_of_coefficients": round(legacy_product, 6),
        "estimates": {
            "unadjusted_assignment_itt": record(*naive),
            "baseline_adjusted_standardized_total_effect": record(*total_average),
            "total_effect_low_anxiety": record(*total_low),
            "total_effect_high_anxiety": record(*total_high),
            "assignment_by_anxiety_interaction": record(*interaction),
            "assignment_effect_on_strategy_use": record(*first_stage),
            "mediator_conditioned_assignment_contrast": record(*conditioned_average),
            "strategy_outcome_conditional_association": record(*mediator_association),
        },
        **truth,
        "interval_method": (
            "All intervals use HC1 heteroskedasticity-consistent covariance and the exact "
            "standard-normal 0.975 quantile. The adjusted total effect and mediator-conditioned "
            "assignment contrast standardize the assignment coefficient over the observed "
            "baseline-anxiety distribution."
        ),
        "identification_note": (
            "Random assignment identifies assignment total effects overall and within the "
            "prespecified baseline-anxiety strata. Strategy use is measured after assignment "
            "and is not randomized. The mediator-conditioned coefficient is therefore reported "
            "as an assumption-dependent descriptive contrast, not an identified controlled or "
            "natural direct effect; latent self-regulation causes both strategy use and outcome."
        ),
        "primary_environment": {"python": platform.python_version(), "numpy": np.__version__},
    }


def main():
    output = compute()
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "CAUSAL_UNIT8_PRIMARY_OK",
        f"total={output['estimates']['baseline_adjusted_standardized_total_effect']['estimate']}",
        f"interaction={output['estimates']['assignment_by_anxiety_interaction']['estimate']}",
        f"conditioned={output['estimates']['mediator_conditioned_assignment_contrast']['estimate']}",
        f"legacy_product={output['legacy_product_of_coefficients']}",
    )


if __name__ == "__main__":
    main()
