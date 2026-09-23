#!/usr/bin/env python3
"""Primary NumPy synthesis calculations for Unit 10."""

import hashlib
import json
import math
import platform
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
UNIT5_DATA = ROOT / "data" / "unit5_hypertension_coaching.csv"
UNIT5_RESULT = ROOT / "expected-results" / "unit5_hypertension_coaching_verified_results.json"
RESULT = ROOT / "expected-results" / "unit10_cross_case_synthesis_verified_results.json"
Z_975 = 1.959963985
Z_80 = 0.841621234
DELTA_U = 0.5
GAMMA_SCENARIOS = (0.0, -2.0, -3.0, -6.0)
PLANNING_SD = 7.1
CLUSTER_SIZE = 50
PLANNED_CLUSTERS = 48
TARGET_MDE = 1.5
ICC_SCENARIOS = (0.0, 0.05, 0.10, 0.20)


def rounded(value):
    return round(float(value), 6)


def even_ceiling(value):
    integer = math.ceil(value)
    return integer if integer % 2 == 0 else integer + 1


def canonical_record_sha256(record):
    """Hash substantive Unit 5 content without its machine-specific environment."""
    canonical = {key: value for key, value in record.items() if key != "primary_environment"}
    payload = json.dumps(canonical, indent=2, sort_keys=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def compute():
    unit5 = json.loads(UNIT5_RESULT.read_text(encoding="utf-8"))
    preferred = unit5["estimates"]["outcome_regression_standardized_ate"]
    estimate = float(preferred["estimate"])
    lower = float(preferred["ci95_lower"])
    upper = float(preferred["ci95_upper"])
    truth = float(unit5["known_simulation_sample_ate"])

    sensitivity = {}
    for gamma in GAMMA_SCENARIOS:
        bias = DELTA_U * gamma
        sensitivity[f"{gamma:.1f}"] = {
            "delta_u": DELTA_U,
            "gamma_u": gamma,
            "assumed_omitted_confounding_bias": rounded(bias),
            "sensitivity_adjusted_estimate": rounded(estimate - bias),
            "shifted_ci95_lower": rounded(lower - bias),
            "shifted_ci95_upper": rounded(upper - bias),
        }

    gamma_to_truth = (estimate - truth) / DELTA_U
    gamma_to_null = estimate / DELTA_U
    precision = {}
    multiplier = 2.0 * (Z_975 + Z_80) * PLANNING_SD
    for rho in ICC_SCENARIOS:
        design_effect = 1.0 + (CLUSTER_SIZE - 1) * rho
        effective_n = PLANNED_CLUSTERS * CLUSTER_SIZE / design_effect
        mde = multiplier / math.sqrt(effective_n)
        required = even_ceiling((multiplier / TARGET_MDE) ** 2 * design_effect / CLUSTER_SIZE)
        precision[f"{rho:.2f}"] = {
            "assumed_icc": rho,
            "design_effect": rounded(design_effect),
            "effective_sample_size_at_48_clusters": rounded(effective_n),
            "mde_at_48_clusters": rounded(mde),
            "required_even_clusters_for_mde_at_most_1_5": required,
        }

    result = {
        "title": "Unit 10 cross-case sensitivity and precision synthesis",
        "source_unit5_dataset": UNIT5_DATA.name,
        "source_unit5_dataset_sha256": hashlib.sha256(UNIT5_DATA.read_bytes()).hexdigest(),
        "source_unit5_result_sha256": hashlib.sha256(UNIT5_RESULT.read_bytes()).hexdigest(),
        "source_unit5_result_canonical_sha256": canonical_record_sha256(unit5),
        "sensitivity_model": "bias = delta_u * gamma_u; adjusted estimate = reported estimate - bias",
        "sensitivity_input": {
            "estimate": estimate,
            "se": preferred["se"],
            "ci95_lower": lower,
            "ci95_upper": upper,
            "negative_control_association": unit5["estimates"]["negative_control_adjusted_association"]["estimate"],
            "hidden_simulation_sample_ate": truth,
        },
        "sensitivity_scenarios": sensitivity,
        "hidden_calibration": {
            "gamma_u_at_delta_0_5_to_reach_hidden_truth": rounded(gamma_to_truth),
            "gamma_u_at_delta_0_5_to_reach_null": rounded(gamma_to_null),
            "reported_minus_hidden_truth": rounded(estimate - truth),
        },
        "precision_design": {
            "outcome_scale": "follow-up systolic blood pressure in mmHg",
            "planning_sd": PLANNING_SD,
            "participants_per_cluster": CLUSTER_SIZE,
            "planned_total_clusters": PLANNED_CLUSTERS,
            "equal_allocation": True,
            "target_mde": TARGET_MDE,
            "two_sided_alpha": 0.05,
            "power": 0.80,
            "z_975": Z_975,
            "z_80": Z_80,
            "formula": "MDE = 2 * (z_975 + z_80) * SD / sqrt(J*m/[1+(m-1)*ICC])",
        },
        "precision_scenarios": precision,
        "reproducibility_ladder": [
            "rerun the same code and data",
            "recompute with independent Python and base R",
            "regenerate deterministic data and verify checksums",
            "directly replicate in a new sample",
            "conceptually replicate with a different design and bias structure",
        ],
        "cross_case_rule": (
            "Triangulation compares evidence with meaningfully different bias structures and compatible "
            "questions; it does not average unlike estimands or relabel repeated specifications as replication."
        ),
        "interpretation_note": (
            "Sensitivity intervals are algebraic shifts conditional on fixed delta_u and gamma_u; they do not "
            "include uncertainty about those parameters. Precision calculations use a normal approximation and "
            "assumed ICC values and omit cluster degrees of freedom, attrition, unequal cluster sizes, "
            "covariate-adjustment gains, and uncertainty in planning inputs."
        ),
        "primary_environment": {"python": platform.python_version(), "numpy": np.__version__},
    }
    return result


def main():
    output = compute()
    RESULT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "CAUSAL_UNIT10_PRIMARY_OK",
        f"adjusted_gamma_minus3={output['sensitivity_scenarios']['-3.0']['sensitivity_adjusted_estimate']}",
        f"mde_icc_010={output['precision_scenarios']['0.10']['mde_at_48_clusters']}",
    )


if __name__ == "__main__":
    main()
