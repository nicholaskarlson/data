#!/usr/bin/env python3
"""Independently verify Unit 10 with the Python standard library."""

import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "unit5_hypertension_coaching.csv"
UNIT5 = ROOT / "expected-results" / "unit5_hypertension_coaching_verified_results.json"
EXPECTED = ROOT / "expected-results" / "unit10_cross_case_synthesis_verified_results.json"
TOL = 0.000002
Z975 = 1.959963985
Z80 = 0.841621234


def check(actual, expected, label):
    if abs(float(actual) - float(expected)) > TOL:
        raise SystemExit(f"CAUSAL_UNIT10_NUMERIC_ERROR {label}: {actual} != {expected}")


def canonical_record_sha256(record):
    canonical = {key: value for key, value in record.items() if key != "primary_environment"}
    payload = json.dumps(canonical, indent=2, sort_keys=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def main():
    unit5 = json.loads(UNIT5.read_text(encoding="utf-8"))
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
    checks = 0
    if hashlib.sha256(DATA.read_bytes()).hexdigest() != expected["source_unit5_dataset_sha256"]:
        raise SystemExit("CAUSAL_UNIT10_NUMERIC_ERROR Unit 5 dataset digest")
    if hashlib.sha256(UNIT5.read_bytes()).hexdigest() != expected["source_unit5_result_sha256"]:
        raise SystemExit("CAUSAL_UNIT10_NUMERIC_ERROR Unit 5 result digest")
    if canonical_record_sha256(unit5) != expected["source_unit5_result_canonical_sha256"]:
        raise SystemExit("CAUSAL_UNIT10_NUMERIC_ERROR Unit 5 canonical result digest")
    checks += 3

    source = unit5["estimates"]["outcome_regression_standardized_ate"]
    for key in ("estimate", "se", "ci95_lower", "ci95_upper"):
        check(source[key], expected["sensitivity_input"][key], "input." + key)
        checks += 1
    check(
        unit5["estimates"]["negative_control_adjusted_association"]["estimate"],
        expected["sensitivity_input"]["negative_control_association"],
        "negative control",
    )
    check(unit5["known_simulation_sample_ate"], expected["sensitivity_input"]["hidden_simulation_sample_ate"], "truth")
    checks += 2

    estimate = source["estimate"]
    for label, gamma in (("0.0", 0.0), ("-2.0", -2.0), ("-3.0", -3.0), ("-6.0", -6.0)):
        bias = 0.5 * gamma
        actual = expected["sensitivity_scenarios"][label]
        for key, value in (
            ("assumed_omitted_confounding_bias", bias),
            ("sensitivity_adjusted_estimate", estimate - bias),
            ("shifted_ci95_lower", source["ci95_lower"] - bias),
            ("shifted_ci95_upper", source["ci95_upper"] - bias),
        ):
            check(value, actual[key], f"{label}.{key}")
            checks += 1
    truth = unit5["known_simulation_sample_ate"]
    calibration = expected["hidden_calibration"]
    check((estimate - truth) / 0.5, calibration["gamma_u_at_delta_0_5_to_reach_hidden_truth"], "gamma to truth")
    check(estimate / 0.5, calibration["gamma_u_at_delta_0_5_to_reach_null"], "gamma to null")
    check(estimate - truth, calibration["reported_minus_hidden_truth"], "reported minus truth")
    checks += 3

    multiplier = 2 * (Z975 + Z80) * 7.1
    for label, rho in (("0.00", 0.0), ("0.05", 0.05), ("0.10", 0.10), ("0.20", 0.20)):
        de = 1 + 49 * rho
        neff = 48 * 50 / de
        mde = multiplier / math.sqrt(neff)
        required = math.ceil((multiplier / 1.5) ** 2 * de / 50)
        if required % 2:
            required += 1
        actual = expected["precision_scenarios"][label]
        for key, value in (
            ("design_effect", de),
            ("effective_sample_size_at_48_clusters", neff),
            ("mde_at_48_clusters", mde),
            ("required_even_clusters_for_mde_at_most_1_5", required),
        ):
            check(value, actual[key], f"{label}.{key}")
            checks += 1
    if len(expected["reproducibility_ladder"]) != 5:
        raise SystemExit("CAUSAL_UNIT10_NUMERIC_ERROR reproducibility ladder")
    checks += 1
    print(
        "CAUSAL_UNIT10_INDEPENDENT_OK",
        f"checks={checks}",
        f"gamma_truth={calibration['gamma_u_at_delta_0_5_to_reach_hidden_truth']}",
        f"clusters_icc_020={expected['precision_scenarios']['0.20']['required_even_clusters_for_mde_at_most_1_5']}",
    )


if __name__ == "__main__":
    main()
