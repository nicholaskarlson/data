#!/usr/bin/env python3
"""Independently recompute Unit 9 with the Python standard library."""

import csv
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data" / "unit9_multisite_replication.csv"
EXPECTED = ROOT / "expected-results" / "unit9_multisite_replication_verified_results.json"
Z_975 = 1.959963985
TOLERANCE = 0.000002
TARGET = {
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


def check(actual, expected, label):
    if abs(actual - expected) > TOLERANCE:
        raise SystemExit(f"CAUSAL_UNIT9_NUMERIC_ERROR {label}: {actual} != {expected}")


def effect(risk0, risk1, variance0, variance1):
    rd = risk1 - risk0
    se = math.sqrt(variance0 + variance1)
    rr = risk1 / risk0
    se_log = math.sqrt(variance1 / risk1**2 + variance0 / risk0**2)
    return {
        "risk_comparison": risk0,
        "risk_program": risk1,
        "risk_difference": rd,
        "risk_difference_se": se,
        "risk_difference_ci95_lower": rd - Z_975 * se,
        "risk_difference_ci95_upper": rd + Z_975 * se,
        "risk_ratio": rr,
        "risk_ratio_ci95_lower": math.exp(math.log(rr) - Z_975 * se_log),
        "risk_ratio_ci95_upper": math.exp(math.log(rr) + Z_975 * se_log),
    }


def standardized(rows, weights, field, observed_only):
    risks = {0: {}, 1: {}}
    variances = {0: {}, 1: {}}
    counts = {}
    for key in weights:
        site, high_text = key.split("|")
        high = int(high_text)
        for arm in (0, 1):
            cell = [
                row for row in rows
                if row["site"] == site
                and row["baseline_high_distress"] == high
                and row["program_assignment"] == arm
                and (not observed_only or row["blinded_outcome_observed"] == 1)
            ]
            values = [row[field] for row in cell]
            risk = sum(values) / len(values)
            risks[arm][key] = risk
            variances[arm][key] = risk * (1 - risk) / len(values)
            counts[f"{key}|{arm}"] = len(values)
    marginal = {arm: sum(weights[key] * risks[arm][key] for key in weights) for arm in (0, 1)}
    variance = {arm: sum(weights[key] ** 2 * variances[arm][key] for key in weights) for arm in (0, 1)}
    return effect(marginal[0], marginal[1], variance[0], variance[1]), counts


def check_effect(actual, expected, label):
    count = 0
    for key, value in actual.items():
        check(value, expected[key], f"{label}.{key}")
        count += 1
    return count


def main():
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
    with CSV.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames
        rows = [
            {
                "participant_id": row["participant_id"],
                "site": row["site"],
                "baseline_high_distress": int(row["baseline_high_distress"]),
                "program_assignment": int(row["program_assignment"]),
                "blinded_outcome_observed": int(row["blinded_outcome_observed"]),
                "blinded_improvement": None if row["blinded_improvement"] == "" else int(row["blinded_improvement"]),
                "self_report_improvement": int(row["self_report_improvement"]),
            }
            for row in reader
        ]
    checks = 0
    if hashlib.sha256(CSV.read_bytes()).hexdigest() != expected["dataset_sha256"]:
        raise SystemExit("CAUSAL_UNIT9_NUMERIC_ERROR dataset digest")
    checks += 1
    if set(fields or []) != {
        "participant_id", "site", "baseline_high_distress", "program_assignment",
        "blinded_outcome_observed", "blinded_improvement", "self_report_improvement",
    }:
        raise SystemExit("CAUSAL_UNIT9_NUMERIC_ERROR fields")
    checks += 1
    if len(rows) != 4000 or expected["n"] != 4000:
        raise SystemExit("CAUSAL_UNIT9_NUMERIC_ERROR row count")
    checks += 1
    if any(row["site"] not in {"Cedar", "Lake", "Ridge", "Harbor"} for row in rows):
        raise SystemExit("CAUSAL_UNIT9_NUMERIC_ERROR site")
    if any(
        row[key] not in (0, 1)
        for row in rows
        for key in ("baseline_high_distress", "program_assignment", "blinded_outcome_observed", "self_report_improvement")
    ):
        raise SystemExit("CAUSAL_UNIT9_NUMERIC_ERROR binary fields")
    if any((row["blinded_improvement"] is None) != (row["blinded_outcome_observed"] == 0) for row in rows):
        raise SystemExit("CAUSAL_UNIT9_NUMERIC_ERROR missingness rule")
    checks += 3

    sample_counts = {}
    allocation = {}
    for row in rows:
        key = f"{row['site']}|{row['baseline_high_distress']}"
        sample_counts[key] = sample_counts.get(key, 0) + 1
        allocation[f"{key}|{row['program_assignment']}"] = allocation.get(f"{key}|{row['program_assignment']}", 0) + 1
    if sample_counts != expected["sample_cell_counts"]:
        raise SystemExit("CAUSAL_UNIT9_NUMERIC_ERROR cell counts")
    if any(allocation[f"{key}|0"] != allocation[f"{key}|1"] for key in sample_counts):
        raise SystemExit("CAUSAL_UNIT9_NUMERIC_ERROR cell randomization")
    checks += 9
    sample_weights = {key: value / len(rows) for key, value in sample_counts.items()}
    for key in sample_weights:
        check(sample_weights[key], expected["sample_cell_weights"][key], f"sample weight {key}")
        check(TARGET[key], expected["target_cell_weights"][key], f"target weight {key}")
        checks += 2
    check(sum(TARGET.values()), 1.0, "target weight sum")
    check(max(TARGET[key] / sample_weights[key] for key in TARGET), expected["maximum_target_to_sample_weight_ratio"], "maximum transport weight")
    checks += 2

    observed = [row for row in rows if row["blinded_outcome_observed"]]
    values = {arm: [row["blinded_improvement"] for row in observed if row["program_assignment"] == arm] for arm in (0, 1)}
    risks = {arm: sum(values[arm]) / len(values[arm]) for arm in (0, 1)}
    variances = {arm: risks[arm] * (1 - risks[arm]) / len(values[arm]) for arm in (0, 1)}
    actual = {"crude_complete_case_blinded": effect(risks[0], risks[1], variances[0], variances[1])}
    actual["sample_standardized_blinded"], observed_counts = standardized(rows, sample_weights, "blinded_improvement", True)
    actual["target_standardized_blinded"], _ = standardized(rows, TARGET, "blinded_improvement", True)
    actual["sample_standardized_self_report"], _ = standardized(rows, sample_weights, "self_report_improvement", False)
    for name, record in actual.items():
        checks += check_effect(record, expected["estimates"][name], name)
    if observed_counts != expected["observed_counts_by_cell_and_assignment"]:
        raise SystemExit("CAUSAL_UNIT9_NUMERIC_ERROR observed cell counts")
    checks += 16

    observation_rates = {}
    for arm in (0, 1):
        arm_rows = [row for row in rows if row["program_assignment"] == arm]
        observation_rates[str(arm)] = sum(row["blinded_outcome_observed"] for row in arm_rows) / len(arm_rows)
        check(observation_rates[str(arm)], expected["observation_rates_by_assignment"][str(arm)], f"observation rate {arm}")
        checks += 1
    check(observation_rates["1"] - observation_rates["0"], expected["observation_rate_difference"], "observation rate difference")
    checks += 1

    bounds = {}
    for arm in (0, 1):
        arm_rows = [row for row in rows if row["program_assignment"] == arm]
        successes = sum(row["blinded_improvement"] or 0 for row in arm_rows if row["blinded_outcome_observed"])
        missing = sum(not row["blinded_outcome_observed"] for row in arm_rows)
        bounds[arm] = (successes / len(arm_rows), (successes + missing) / len(arm_rows))
    check(bounds[1][0] - bounds[0][1], expected["missing_outcome_risk_difference_bounds"]["worst_case"], "worst bound")
    check(bounds[1][1] - bounds[0][0], expected["missing_outcome_risk_difference_bounds"]["best_case"], "best bound")
    checks += 2

    for weight_name, weights in (("sample", sample_weights), ("target", TARGET)):
        risk0 = sum(weights[key] * TRUTH[key][0] for key in weights)
        risk1 = sum(weights[key] * (TRUTH[key][0] + TRUTH[key][1]) for key in weights)
        truth = expected[f"known_simulation_{weight_name}_primary_effect"]
        for key, value in {
            "risk_comparison": risk0, "risk_program": risk1,
            "risk_difference": risk1 - risk0, "risk_ratio": risk1 / risk0,
        }.items():
            check(value, truth[key], f"{weight_name} truth {key}")
            checks += 1
    if expected["known_simulation_observation_rule"] != "depends only on assignment, site, and baseline_high_distress":
        raise SystemExit("CAUSAL_UNIT9_NUMERIC_ERROR observation rule")
    checks += 1

    print(
        "CAUSAL_UNIT9_INDEPENDENT_OK",
        f"checks={checks}", f"n={len(rows)}", f"observed={len(observed)}",
        f"sample_rd={expected['estimates']['sample_standardized_blinded']['risk_difference']}",
        f"target_rd={expected['estimates']['target_standardized_blinded']['risk_difference']}",
    )


if __name__ == "__main__":
    main()
