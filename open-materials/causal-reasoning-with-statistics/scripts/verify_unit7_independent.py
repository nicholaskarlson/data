#!/usr/bin/env python3
"""Independently recompute Unit 7 with the Python standard library."""

import csv
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RD_CSV = ROOT / "data" / "unit7_tutoring_cutoff.csv"
IV_CSV = ROOT / "data" / "unit7_tutoring_encouragement.csv"
EXPECTED = ROOT / "expected-results" / "unit7_thresholds_encouragements_verified_results.json"
Z_975 = 1.959963985
TOLERANCE = 0.000002


def solve(matrix, vector):
    size = len(vector)
    augmented = [list(matrix[index]) + [vector[index]] for index in range(size)]
    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(augmented[row][column]))
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        scale = augmented[column][column]
        if abs(scale) < 1e-12:
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


def hc1_target(x, y, target=1):
    p = len(x[0])
    gram = [[sum(row[j] * row[k] for row in x) for k in range(p)] for j in range(p)]
    rhs = [sum(row[j] * value for row, value in zip(x, y)) for j in range(p)]
    beta = solve(gram, rhs)
    residual = [
        value - sum(coefficient * item for coefficient, item in zip(beta, row))
        for row, value in zip(x, y)
    ]
    bread_row = solve(gram, [float(index == target) for index in range(p)])
    influence = [
        residual_value * sum(left * right for left, right in zip(bread_row, row))
        for row, residual_value in zip(x, residual)
    ]
    variance = len(x) / (len(x) - p) * sum(value * value for value in influence)
    return beta[target], math.sqrt(variance)


def rd_fit(rows, outcome, cutoff, bandwidth):
    selected = [row for row in rows if abs(row["diagnostic_score"] - cutoff) <= bandwidth]
    x = []
    y = []
    for row in selected:
        centered = row["diagnostic_score"] - cutoff
        below = float(centered < 0)
        x.append([1.0, below, centered, below * centered])
        y.append(row[outcome])
    estimate, se = hc1_target(x, y)
    return estimate, se, len(selected)


def difference_in_means(rows, variable):
    group1 = [row[variable] for row in rows if row["encouragement_assignment"] == 1]
    group0 = [row[variable] for row in rows if row["encouragement_assignment"] == 0]
    mean1 = sum(group1) / len(group1)
    mean0 = sum(group0) / len(group0)
    p = len(group1) / len(rows)
    influence = []
    for row in rows:
        value = row[variable]
        if row["encouragement_assignment"] == 1:
            influence.append((value - mean1) / p)
        else:
            influence.append(-(value - mean0) / (1.0 - p))
    se = math.sqrt(sum(value * value for value in influence) / (len(rows) * (len(rows) - 1)))
    return mean1 - mean0, se, influence, mean1, mean0


def check(actual, expected, label):
    if abs(actual - expected) > TOLERANCE:
        raise SystemExit(f"CAUSAL_UNIT7_NUMERIC_ERROR {label}: {actual} != {expected}")


def check_record(actual, expected, label):
    estimate, se = actual
    values = {
        "estimate": estimate,
        "se": se,
        "ci95_lower": estimate - Z_975 * se,
        "ci95_upper": estimate + Z_975 * se,
    }
    for key, value in values.items():
        check(value, expected[key], f"{label}.{key}")
    return 4


def main():
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
    with RD_CSV.open(newline="", encoding="utf-8") as stream:
        rd_reader = csv.DictReader(stream)
        rd_fields = rd_reader.fieldnames
        rd_rows = [
            {
                "applicant_id": row["applicant_id"],
                "diagnostic_score": float(row["diagnostic_score"]),
                "centered_score": float(row["centered_score"]),
                "tutoring_eligible": int(row["tutoring_eligible"]),
                "baseline_gpa": float(row["baseline_gpa"]),
                "end_term_math_score": float(row["end_term_math_score"]),
            }
            for row in rd_reader
        ]
    with IV_CSV.open(newline="", encoding="utf-8") as stream:
        iv_reader = csv.DictReader(stream)
        iv_fields = iv_reader.fieldnames
        iv_rows = [
            {
                "student_id": row["student_id"],
                "encouragement_assignment": int(row["encouragement_assignment"]),
                "tutoring_received": int(row["tutoring_received"]),
                "baseline_math_score": float(row["baseline_math_score"]),
                "end_term_math_score": float(row["end_term_math_score"]),
            }
            for row in iv_reader
        ]

    checks = 0
    if hashlib.sha256(RD_CSV.read_bytes()).hexdigest() != expected["datasets"]["rd"]["sha256"]:
        raise SystemExit("CAUSAL_UNIT7_NUMERIC_ERROR RD digest")
    checks += 1
    if hashlib.sha256(IV_CSV.read_bytes()).hexdigest() != expected["datasets"]["iv"]["sha256"]:
        raise SystemExit("CAUSAL_UNIT7_NUMERIC_ERROR IV digest")
    checks += 1
    if set(rd_fields or []) != {
        "applicant_id", "diagnostic_score", "centered_score", "tutoring_eligible",
        "baseline_gpa", "end_term_math_score",
    }:
        raise SystemExit("CAUSAL_UNIT7_NUMERIC_ERROR RD fields")
    checks += 1
    if set(iv_fields or []) != {
        "student_id", "encouragement_assignment", "tutoring_received",
        "baseline_math_score", "end_term_math_score",
    }:
        raise SystemExit("CAUSAL_UNIT7_NUMERIC_ERROR IV fields")
    checks += 1
    if len(rd_rows) != 2600 or len(iv_rows) != 3000:
        raise SystemExit("CAUSAL_UNIT7_NUMERIC_ERROR row counts")
    checks += 2
    if any(abs(row["centered_score"] - (row["diagnostic_score"] - 60.0)) > 0.000002 for row in rd_rows):
        raise SystemExit("CAUSAL_UNIT7_NUMERIC_ERROR centered score")
    checks += 1
    if any(row["tutoring_eligible"] != int(row["diagnostic_score"] < 60.0) for row in rd_rows):
        raise SystemExit("CAUSAL_UNIT7_NUMERIC_ERROR cutoff rule")
    checks += 1
    if any(row["diagnostic_score"] == 60.0 for row in rd_rows):
        raise SystemExit("CAUSAL_UNIT7_NUMERIC_ERROR cutoff tie")
    checks += 1
    if any(not all(math.isfinite(row[key]) for key in ("diagnostic_score", "baseline_gpa", "end_term_math_score")) for row in rd_rows):
        raise SystemExit("CAUSAL_UNIT7_NUMERIC_ERROR RD nonfinite")
    checks += 1
    if sum(row["encouragement_assignment"] for row in iv_rows) != 1500:
        raise SystemExit("CAUSAL_UNIT7_NUMERIC_ERROR encouragement allocation")
    checks += 1
    if any(row["encouragement_assignment"] not in (0, 1) or row["tutoring_received"] not in (0, 1) for row in iv_rows):
        raise SystemExit("CAUSAL_UNIT7_NUMERIC_ERROR IV binary fields")
    checks += 1
    if any(not all(math.isfinite(row[key]) for key in ("baseline_math_score", "end_term_math_score")) for row in iv_rows):
        raise SystemExit("CAUSAL_UNIT7_NUMERIC_ERROR IV nonfinite")
    checks += 1

    estimates = expected["rd_estimates"]
    primary = rd_fit(rd_rows, "end_term_math_score", 60.0, 6.0)
    baseline = rd_fit(rd_rows, "baseline_gpa", 60.0, 6.0)
    placebo = rd_fit(rd_rows, "end_term_math_score", 70.0, 5.0)
    checks += check_record(primary[:2], estimates["local_linear_discontinuity"], "rd.primary")
    checks += 1
    check(primary[2], estimates["local_linear_discontinuity"]["n_local"], "rd.primary.n_local")
    checks += check_record(baseline[:2], estimates["baseline_gpa_continuity"], "rd.baseline")
    checks += 1
    check(baseline[2], estimates["baseline_gpa_continuity"]["n_local"], "rd.baseline.n_local")
    checks += check_record(placebo[:2], estimates["placebo_cutoff_discontinuity"], "rd.placebo")
    checks += 1
    check(placebo[2], estimates["placebo_cutoff_discontinuity"]["n_local"], "rd.placebo.n_local")

    for bandwidth in (4, 6, 8, 10):
        actual = rd_fit(rd_rows, "end_term_math_score", 60.0, float(bandwidth))
        expected_bandwidth = expected["rd_bandwidth_sensitivity"][str(bandwidth)]
        checks += check_record(actual[:2], expected_bandwidth, f"rd.bandwidth.{bandwidth}")
        check(actual[2], expected_bandwidth["n_local"], f"rd.bandwidth.{bandwidth}.n_local")
        checks += 1

    local = [row for row in rd_rows if abs(row["centered_score"]) <= 2.0]
    below = sum(row["centered_score"] < 0 for row in local)
    above = sum(row["centered_score"] >= 0 for row in local)
    density = expected["rd_density_diagnostic"]
    if below != density["count_immediately_below"] or above != density["count_immediately_above"]:
        raise SystemExit("CAUSAL_UNIT7_NUMERIC_ERROR density counts")
    checks += 2
    z_statistic = (below - above) / math.sqrt(below + above)
    p_value = math.erfc(abs(z_statistic) / math.sqrt(2.0))
    for actual, key in ((below / above, "below_to_above_ratio"), (z_statistic, "normal_approximation_z"), (p_value, "two_sided_p")):
        check(actual, density[key], f"rd.density.{key}")
        checks += 1

    reduced = difference_in_means(iv_rows, "end_term_math_score")
    first = difference_in_means(iv_rows, "tutoring_received")
    checks += check_record(reduced[:2], expected["iv_estimates"]["assignment_itt"], "iv.assignment_itt")
    checks += check_record(reduced[:2], expected["iv_estimates"]["reduced_form"], "iv.reduced_form")
    checks += check_record(first[:2], expected["iv_estimates"]["first_stage"], "iv.first_stage")
    wald = reduced[0] / first[0]
    wald_if = [(left - wald * right) / first[0] for left, right in zip(reduced[2], first[2])]
    wald_se = math.sqrt(sum(value * value for value in wald_if) / (len(iv_rows) * (len(iv_rows) - 1)))
    checks += check_record((wald, wald_se), expected["iv_estimates"]["wald_late"], "iv.wald")
    for actual, key in ((reduced[3], "encouraged"), (reduced[4], "not_encouraged")):
        check(actual, expected["iv_outcome_means"][key], f"iv.outcome_means.{key}")
        checks += 1
    for actual, key in ((first[3], "encouraged"), (first[4], "not_encouraged")):
        check(actual, expected["iv_receipt_rates"][key], f"iv.receipt_rates.{key}")
        checks += 1
    implied = {
        "always_takers": first[4],
        "compliers": first[0],
        "never_takers": 1.0 - first[3],
    }
    for key, value in implied.items():
        check(value, expected["iv_principal_stratum_shares_implied_under_monotonicity"][key], f"iv.strata.{key}")
        checks += 1
    check(sum(implied.values()), 1.0, "iv.strata.sum")
    checks += 1
    check((first[0] / first[1]) ** 2, expected["iv_first_stage_f"], "iv.first_stage_f")
    checks += 1
    if expected["known_simulation_rd_discontinuity"] != 4.2:
        raise SystemExit("CAUSAL_UNIT7_NUMERIC_ERROR RD truth")
    checks += 1
    if expected["known_simulation_complier_effect"] != 5.2:
        raise SystemExit("CAUSAL_UNIT7_NUMERIC_ERROR IV truth")
    checks += 1
    if expected["iv_estimates"]["assignment_itt"] != expected["iv_estimates"]["reduced_form"]:
        raise SystemExit("CAUSAL_UNIT7_NUMERIC_ERROR ITT and reduced form differ")
    checks += 1
    if checks != 81:
        raise SystemExit(f"CAUSAL_UNIT7_NUMERIC_ERROR internal check count {checks}")
    print(
        "CAUSAL_UNIT7_INDEPENDENT_OK",
        f"checks={checks}",
        f"rd_rows={len(rd_rows)}",
        f"iv_rows={len(iv_rows)}",
        f"rd={expected['rd_estimates']['local_linear_discontinuity']['estimate']}",
        f"wald={expected['iv_estimates']['wald_late']['estimate']}",
    )


if __name__ == "__main__":
    main()
