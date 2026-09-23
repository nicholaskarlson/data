#!/usr/bin/env python3
"""Primary NumPy analysis for Unit 9 missingness, measurement, and transport."""

import csv
import hashlib
import json
import math
import platform
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "unit9_multisite_replication.csv"
RESULT = ROOT / "expected-results" / "unit9_multisite_replication_verified_results.json"
Z_975 = 1.959963985
TARGET_WEIGHTS = {
    "Cedar|0": 0.12, "Cedar|1": 0.10,
    "Lake|0": 0.15, "Lake|1": 0.13,
    "Ridge|0": 0.10, "Ridge|1": 0.15,
    "Harbor|0": 0.08, "Harbor|1": 0.17,
}
TRUTH = {
    "Cedar|0": (0.42, 0.10), "Cedar|1": (0.28, 0.16),
    "Lake|0": (0.39, 0.12), "Lake|1": (0.25, 0.18),
    "Ridge|0": (0.36, 0.14), "Ridge|1": (0.23, 0.20),
    "Harbor|0": (0.34, 0.16), "Harbor|1": (0.20, 0.22),
}


def read_rows():
    with DATA.open(newline="", encoding="utf-8") as stream:
        return [
            {
                "participant_id": row["participant_id"],
                "site": row["site"],
                "baseline_high_distress": int(row["baseline_high_distress"]),
                "program_assignment": int(row["program_assignment"]),
                "blinded_outcome_observed": int(row["blinded_outcome_observed"]),
                "blinded_improvement": None if row["blinded_improvement"] == "" else int(row["blinded_improvement"]),
                "self_report_improvement": int(row["self_report_improvement"]),
            }
            for row in csv.DictReader(stream)
        ]


def effect_record(risk0, risk1, var0, var1):
    rd = risk1 - risk0
    se_rd = math.sqrt(var0 + var1)
    rr = risk1 / risk0
    se_log_rr = math.sqrt(var1 / (risk1 * risk1) + var0 / (risk0 * risk0))
    return {
        "risk_comparison": round(risk0, 6),
        "risk_program": round(risk1, 6),
        "risk_difference": round(rd, 6),
        "risk_difference_se": round(se_rd, 6),
        "risk_difference_ci95_lower": round(rd - Z_975 * se_rd, 6),
        "risk_difference_ci95_upper": round(rd + Z_975 * se_rd, 6),
        "risk_ratio": round(rr, 6),
        "risk_ratio_ci95_lower": round(math.exp(math.log(rr) - Z_975 * se_log_rr), 6),
        "risk_ratio_ci95_upper": round(math.exp(math.log(rr) + Z_975 * se_log_rr), 6),
    }


def standardized(rows, weights, outcome_name, observed_only):
    risks = {0: {}, 1: {}}
    variances = {0: {}, 1: {}}
    counts = {}
    for key in weights:
        site, high = key.split("|")
        high = int(high)
        for arm in (0, 1):
            cell = [
                row for row in rows
                if row["site"] == site
                and row["baseline_high_distress"] == high
                and row["program_assignment"] == arm
                and (not observed_only or row["blinded_outcome_observed"] == 1)
            ]
            values = np.asarray([row[outcome_name] for row in cell], dtype=float)
            risk = float(values.mean())
            risks[arm][key] = risk
            variances[arm][key] = risk * (1.0 - risk) / len(values)
            counts[f"{key}|{arm}"] = len(values)
    marginal = {
        arm: sum(weights[key] * risks[arm][key] for key in weights)
        for arm in (0, 1)
    }
    variance = {
        arm: sum(weights[key] ** 2 * variances[arm][key] for key in weights)
        for arm in (0, 1)
    }
    return effect_record(marginal[0], marginal[1], variance[0], variance[1]), risks, counts


def truth_record(weights):
    risk0 = sum(weights[key] * TRUTH[key][0] for key in weights)
    risk1 = sum(weights[key] * (TRUTH[key][0] + TRUTH[key][1]) for key in weights)
    return {
        "risk_comparison": round(risk0, 6),
        "risk_program": round(risk1, 6),
        "risk_difference": round(risk1 - risk0, 6),
        "risk_ratio": round(risk1 / risk0, 6),
    }


def compute():
    rows = read_rows()
    n = len(rows)
    sample_counts = {}
    for row in rows:
        key = f"{row['site']}|{row['baseline_high_distress']}"
        sample_counts[key] = sample_counts.get(key, 0) + 1
    sample_weights = {key: count / n for key, count in sample_counts.items()}

    observed = [row for row in rows if row["blinded_outcome_observed"] == 1]
    arm_values = {
        arm: [row["blinded_improvement"] for row in observed if row["program_assignment"] == arm]
        for arm in (0, 1)
    }
    crude_risks = {arm: float(np.mean(values)) for arm, values in arm_values.items()}
    crude_vars = {
        arm: crude_risks[arm] * (1 - crude_risks[arm]) / len(arm_values[arm])
        for arm in (0, 1)
    }
    crude = effect_record(crude_risks[0], crude_risks[1], crude_vars[0], crude_vars[1])

    sample_primary, cell_risks, observed_counts = standardized(
        rows, sample_weights, "blinded_improvement", True
    )
    target_primary, _, _ = standardized(rows, TARGET_WEIGHTS, "blinded_improvement", True)
    sample_self_report, _, _ = standardized(
        rows, sample_weights, "self_report_improvement", False
    )

    observation_by_arm = {}
    observation_by_cell_arm = {}
    for arm in (0, 1):
        arm_rows = [row for row in rows if row["program_assignment"] == arm]
        observation_by_arm[str(arm)] = round(
            sum(row["blinded_outcome_observed"] for row in arm_rows) / len(arm_rows), 6
        )
    for key in sample_weights:
        site, high = key.split("|")
        for arm in (0, 1):
            cell = [row for row in rows if row["site"] == site and row["baseline_high_distress"] == int(high) and row["program_assignment"] == arm]
            observation_by_cell_arm[f"{key}|{arm}"] = round(
                sum(row["blinded_outcome_observed"] for row in cell) / len(cell), 6
            )

    bounds = {}
    for arm in (0, 1):
        arm_rows = [row for row in rows if row["program_assignment"] == arm]
        successes = sum((row["blinded_improvement"] or 0) for row in arm_rows if row["blinded_outcome_observed"] == 1)
        missing = sum(row["blinded_outcome_observed"] == 0 for row in arm_rows)
        bounds[arm] = (successes / len(arm_rows), (successes + missing) / len(arm_rows))
    worst_case_rd = bounds[1][0] - bounds[0][1]
    best_case_rd = bounds[1][1] - bounds[0][0]

    max_transport_weight = max(TARGET_WEIGHTS[key] / sample_weights[key] for key in TARGET_WEIGHTS)
    result = {
        "title": "Unit 9 deterministic multisite replication",
        "generator_seed": 20261002,
        "dataset_filename": DATA.name,
        "dataset_sha256": hashlib.sha256(DATA.read_bytes()).hexdigest(),
        "n": n,
        "n_program": sum(row["program_assignment"] for row in rows),
        "n_comparison": sum(1 - row["program_assignment"] for row in rows),
        "n_blinded_outcome_observed": len(observed),
        "sample_cell_counts": sample_counts,
        "sample_cell_weights": {key: round(value, 6) for key, value in sample_weights.items()},
        "target_cell_weights": TARGET_WEIGHTS,
        "maximum_target_to_sample_weight_ratio": round(max_transport_weight, 6),
        "observation_rates_by_assignment": observation_by_arm,
        "observation_rate_difference": round(observation_by_arm["1"] - observation_by_arm["0"], 6),
        "observation_rates_by_cell_and_assignment": observation_by_cell_arm,
        "observed_counts_by_cell_and_assignment": observed_counts,
        "estimates": {
            "crude_complete_case_blinded": crude,
            "sample_standardized_blinded": sample_primary,
            "target_standardized_blinded": target_primary,
            "sample_standardized_self_report": sample_self_report,
        },
        "missing_outcome_risk_difference_bounds": {
            "worst_case": round(worst_case_rd, 6),
            "best_case": round(best_case_rd, 6),
        },
        "known_simulation_sample_primary_effect": truth_record(sample_weights),
        "known_simulation_target_primary_effect": truth_record(TARGET_WEIGHTS),
        "known_simulation_observation_rule": "depends only on assignment, site, and baseline_high_distress",
        "known_simulation_self_report_sensitivity": {"comparison": 0.82, "program": 0.91},
        "known_simulation_self_report_specificity": {"comparison": 0.90, "program": 0.84},
        "interval_method": (
            "Wald intervals use the exact standard-normal 0.975 quantile. Standardized risks are "
            "weighted cell-specific binomial risks; risk-difference variance sums arm variances, "
            "and risk-ratio intervals use the log scale. These intervals condition on the fixed "
            "sample or target weights and do not quantify uncertainty about missingness, measurement, "
            "transportability, or the externally specified target composition."
        ),
        "identification_note": (
            "Randomization is exact within site-by-distress cells. Complete-case cell standardization "
            "identifies the recruited-sample assignment effect only if blinded-outcome observation is "
            "independent of the potential outcome within assignment, site, and baseline distress. "
            "Transport additionally requires conditional effect exchangeability between the recruited "
            "sample and target, common intervention and outcome versions, and target support in every cell."
        ),
        "primary_environment": {"python": platform.python_version(), "numpy": np.__version__},
    }
    if round(sum(TARGET_WEIGHTS.values()), 12) != 1.0:
        raise RuntimeError("Unit 9 target weights do not sum to one")
    return result


def main():
    output = compute()
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "CAUSAL_UNIT9_PRIMARY_OK",
        f"sample_rd={output['estimates']['sample_standardized_blinded']['risk_difference']}",
        f"target_rd={output['estimates']['target_standardized_blinded']['risk_difference']}",
        f"self_report_rd={output['estimates']['sample_standardized_self_report']['risk_difference']}",
    )


if __name__ == "__main__":
    main()
