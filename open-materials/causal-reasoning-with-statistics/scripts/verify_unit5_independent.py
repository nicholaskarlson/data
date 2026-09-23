#!/usr/bin/env python3
"""Independently recompute Unit 5 from raw CSV data using only the standard library."""

import csv
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data" / "unit5_hypertension_coaching.csv"
EXPECTED = ROOT / "expected-results" / "unit5_hypertension_coaching_verified_results.json"
TOLERANCE = 0.000002
Z = 1.96
KNOWN_EFFECT_FORMULA = "-4.2 - 0.85 * ((baseline_sbp - 137) / 10)"


def solve(matrix, vector):
    size = len(vector)
    augmented = [list(matrix[index]) + [vector[index]] for index in range(size)]
    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(augmented[row][column]))
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        scale = augmented[column][column]
        if abs(scale) < 1e-12:
            raise ValueError("singular system")
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


def inverse(matrix):
    size = len(matrix)
    columns = [solve(matrix, [float(row == column) for row in range(size)]) for column in range(size)]
    return [[columns[column][row] for column in range(size)] for row in range(size)]


def matmul(left, right):
    return [
        [sum(left_value * right[k][column] for k, left_value in enumerate(row))
         for column in range(len(right[0]))]
        for row in left
    ]


def transpose(matrix):
    return [list(column) for column in zip(*matrix)]


def quadratic(vector, matrix):
    return sum(
        vector[row] * matrix[row][column] * vector[column]
        for row in range(len(vector))
        for column in range(len(vector))
    )


def check(actual, expected, label):
    if abs(actual - expected) > TOLERANCE:
        raise SystemExit(f"CAUSAL_UNIT5_NUMERIC_ERROR {label}: {actual} != {expected}")


def covariates(row):
    return [
        (row["baseline_sbp"] - 137.0) / 10.0,
        (row["age_years"] - 54.0) / 10.0,
        row["current_smoker"],
        row["taking_bp_medication"],
        row["transport_barrier"],
        float(row["clinic"] == "Mesa"),
        float(row["clinic"] == "River"),
    ]


def propensity_rows(rows):
    return [[1.0] + covariates(row) for row in rows]


def outcome_rows(rows, assignment=None, interaction=True):
    output = []
    for row in rows:
        treatment = row["joined_coaching"] if assignment is None else float(assignment)
        values = [1.0, treatment] + covariates(row)
        if interaction:
            values.append(treatment * (row["baseline_sbp"] - 137.0) / 10.0)
        output.append(values)
    return output


def ols_hc1(x, y):
    n, p = len(x), len(x[0])
    gram = [[sum(row[j] * row[k] for row in x) for k in range(p)] for j in range(p)]
    rhs = [sum(row[j] * value for row, value in zip(x, y)) for j in range(p)]
    beta = solve(gram, rhs)
    residuals = [
        value - sum(coefficient * item for coefficient, item in zip(beta, row))
        for row, value in zip(x, y)
    ]
    bread = inverse(gram)
    meat = [
        [sum(error * error * row[j] * row[k] for row, error in zip(x, residuals)) for k in range(p)]
        for j in range(p)
    ]
    covariance = matmul(matmul(bread, meat), bread)
    correction = n / (n - p)
    covariance = [[correction * value for value in row] for row in covariance]
    return beta, covariance


def record(estimate, se):
    return estimate, se, estimate - Z * se, estimate + Z * se


def logistic_fit(x, treatment):
    p = len(x[0])
    beta = [0.0] * p
    for _ in range(100):
        probability = []
        for row in x:
            linear = max(-35.0, min(35.0, sum(value * coefficient for value, coefficient in zip(row, beta))))
            probability.append(1.0 / (1.0 + math.exp(-linear)))
        information = [
            [sum(row[j] * row[k] * pr * (1.0 - pr) for row, pr in zip(x, probability)) for k in range(p)]
            for j in range(p)
        ]
        score = [
            sum(row[j] * (assignment - pr) for row, assignment, pr in zip(x, treatment, probability))
            for j in range(p)
        ]
        step = solve(information, score)
        beta = [value + increment for value, increment in zip(beta, step)]
        if max(abs(value) for value in step) < 1e-12:
            break
    else:
        raise SystemExit("CAUSAL_UNIT5_NUMERIC_ERROR propensity convergence")
    probability = []
    for row in x:
        linear = max(-35.0, min(35.0, sum(value * coefficient for value, coefficient in zip(row, beta))))
        probability.append(min(1.0 - 1e-9, max(1e-9, 1.0 / (1.0 + math.exp(-linear)))))
    return beta, probability


def ipw_hajek(x, treatment, outcome, probability):
    n, p = len(x), len(x[0])
    treated_weight = [assignment / pr for assignment, pr in zip(treatment, probability)]
    control_weight = [(1.0 - assignment) / (1.0 - pr) for assignment, pr in zip(treatment, probability)]
    mean_treated = sum(weight * value for weight, value in zip(treated_weight, outcome)) / sum(treated_weight)
    mean_control = sum(weight * value for weight, value in zip(control_weight, outcome)) / sum(control_weight)

    estimating = []
    for row, assignment, value, pr, weight1, weight0 in zip(
        x, treatment, outcome, probability, treated_weight, control_weight
    ):
        estimating.append(
            [item * (assignment - pr) for item in row]
            + [weight1 * (value - mean_treated), weight0 * (value - mean_control)]
        )

    size = p + 2
    sensitivity = [[0.0] * size for _ in range(size)]
    for j in range(p):
        for k in range(p):
            sensitivity[j][k] = sum(
                row[j] * row[k] * pr * (1.0 - pr) for row, pr in zip(x, probability)
            ) / n
        sensitivity[p][j] = sum(
            weight * (1.0 - pr) * (value - mean_treated) * row[j]
            for row, weight, pr, value in zip(x, treated_weight, probability, outcome)
        ) / n
        sensitivity[p + 1][j] = -sum(
            weight * pr * (value - mean_control) * row[j]
            for row, weight, pr, value in zip(x, control_weight, probability, outcome)
        ) / n
    sensitivity[p][p] = sum(treated_weight) / n
    sensitivity[p + 1][p + 1] = sum(control_weight) / n

    variability = [
        [sum(row[j] * row[k] for row in estimating) / n for k in range(size)]
        for j in range(size)
    ]
    sensitivity_inverse = inverse(sensitivity)
    covariance = matmul(matmul(sensitivity_inverse, variability), transpose(sensitivity_inverse))
    covariance = [[value / n for value in row] for row in covariance]
    gradient = [0.0] * size
    gradient[p] = 1.0
    gradient[p + 1] = -1.0
    se = math.sqrt(quadratic(gradient, covariance))
    return mean_treated - mean_control, se, mean_treated, mean_control, treated_weight, control_weight


def quantile(values, probability):
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = int(math.floor(position))
    upper = int(math.ceil(position))
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def sample_variance(values):
    mean = sum(values) / len(values)
    return sum((value - mean) ** 2 for value in values) / (len(values) - 1)


def balance(rows, treated_weight, control_weight):
    names = (
        "baseline_sbp",
        "age_years",
        "current_smoker",
        "taking_bp_medication",
        "transport_barrier",
        "clinic_mesa",
        "clinic_river",
    )
    columns = list(zip(*(covariates(row) for row in rows)))
    treatment = [row["joined_coaching"] for row in rows]
    before, after = {}, {}
    for name, column in zip(names, columns):
        treated_values = [value for value, assignment in zip(column, treatment) if assignment == 1.0]
        control_values = [value for value, assignment in zip(column, treatment) if assignment == 0.0]
        denominator = math.sqrt((sample_variance(treated_values) + sample_variance(control_values)) / 2.0)
        before[name] = (sum(treated_values) / len(treated_values) - sum(control_values) / len(control_values)) / denominator
        weighted_treated_mean = sum(
            weight * value for weight, value, assignment in zip(treated_weight, column, treatment) if assignment == 1.0
        ) / sum(weight for weight, assignment in zip(treated_weight, treatment) if assignment == 1.0)
        weighted_control_mean = sum(
            weight * value for weight, value, assignment in zip(control_weight, column, treatment) if assignment == 0.0
        ) / sum(weight for weight, assignment in zip(control_weight, treatment) if assignment == 0.0)
        after[name] = (weighted_treated_mean - weighted_control_mean) / denominator
    return before, after


def effective_sample_size(weights):
    return sum(weights) ** 2 / sum(value * value for value in weights)


def main():
    with CSV.open(newline="", encoding="utf-8") as stream:
        raw_rows = list(csv.DictReader(stream))
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
    checks = 0
    if hashlib.sha256(CSV.read_bytes()).hexdigest() != expected["dataset_sha256"]:
        raise SystemExit("CAUSAL_UNIT5_NUMERIC_ERROR dataset digest")
    checks += 1
    if len(raw_rows) != expected["n"] or len(raw_rows) != 3200:
        raise SystemExit("CAUSAL_UNIT5_NUMERIC_ERROR row count")
    checks += 1
    if len({row["participant_id"] for row in raw_rows}) != len(raw_rows):
        raise SystemExit("CAUSAL_UNIT5_NUMERIC_ERROR duplicate participant ID")
    checks += 1
    if any(not all(row.values()) for row in raw_rows):
        raise SystemExit("CAUSAL_UNIT5_NUMERIC_ERROR undeclared missing value")
    checks += 1
    if set(row["clinic"] for row in raw_rows) != {"Harbor", "Mesa", "River"}:
        raise SystemExit("CAUSAL_UNIT5_NUMERIC_ERROR clinic levels")
    checks += 1

    rows = []
    for raw in raw_rows:
        rows.append(
            {
                "participant_id": raw["participant_id"],
                "clinic": raw["clinic"],
                "age_years": float(raw["age_years"]),
                "baseline_sbp": float(raw["baseline_sbp"]),
                "current_smoker": float(raw["current_smoker"]),
                "taking_bp_medication": float(raw["taking_bp_medication"]),
                "transport_barrier": float(raw["transport_barrier"]),
                "joined_coaching": float(raw["joined_coaching"]),
                "prior_year_preventive_visits": float(raw["prior_year_preventive_visits"]),
                "followup_sbp": float(raw["followup_sbp"]),
            }
        )
    treatment = [row["joined_coaching"] for row in rows]
    outcome = [row["followup_sbp"] for row in rows]
    prior = [row["prior_year_preventive_visits"] for row in rows]
    if sum(treatment) != expected["n_joined"]:
        raise SystemExit("CAUSAL_UNIT5_NUMERIC_ERROR participant count")
    checks += 1
    check(sum(treatment) / len(treatment), expected["participation_rate"], "participation rate")
    checks += 1
    for assignment, label in ((0.0, "nonparticipants"), (1.0, "participants")):
        values = [value for value, status in zip(outcome, treatment) if status == assignment]
        check(sum(values) / len(values), expected["observed_followup_means"][label], f"mean {label}")
        checks += 1

    naive_x = [[1.0, value] for value in treatment]
    naive_beta, naive_covariance = ols_hc1(naive_x, outcome)
    estimate_records = {
        "naive_difference": record(naive_beta[1], math.sqrt(naive_covariance[1][1]))
    }
    outcome_x = outcome_rows(rows)
    outcome_beta, outcome_covariance = ols_hc1(outcome_x, outcome)
    one = outcome_rows(rows, assignment=1.0)
    zero = outcome_rows(rows, assignment=0.0)
    gradient = [sum(a - b for a, b in zip(column_one, column_zero)) / len(rows)
                for column_one, column_zero in zip(zip(*one), zip(*zero))]
    outcome_estimate = sum(value * coefficient for value, coefficient in zip(gradient, outcome_beta))
    outcome_se = math.sqrt(quadratic(gradient, outcome_covariance))
    estimate_records["outcome_regression_standardized_ate"] = record(outcome_estimate, outcome_se)

    propensity_x = propensity_rows(rows)
    propensity_beta, probability = logistic_fit(propensity_x, treatment)
    standardized_mean_joined = sum(
        sum(item * coefficient for item, coefficient in zip(row, outcome_beta)) for row in one
    ) / len(one)
    standardized_mean_not_joined = sum(
        sum(item * coefficient for item, coefficient in zip(row, outcome_beta)) for row in zero
    ) / len(zero)
    ipw_estimate, ipw_se, ipw_mean_joined, ipw_mean_not_joined, treated_weight, control_weight = ipw_hajek(
        propensity_x, treatment, outcome, probability
    )
    estimate_records["ipw_hajek_ate"] = record(ipw_estimate, ipw_se)

    negative_x = outcome_rows(rows, interaction=False)
    negative_beta, negative_covariance = ols_hc1(negative_x, prior)
    estimate_records["negative_control_adjusted_association"] = record(
        negative_beta[1], math.sqrt(negative_covariance[1][1])
    )
    for name, values in estimate_records.items():
        for key, value in zip(("estimate", "se", "ci95_lower", "ci95_upper"), values):
            check(value, expected["estimates"][name][key], f"{name}.{key}")
            checks += 1

    if expected.get("known_simulation_individual_effect_formula") != KNOWN_EFFECT_FORMULA:
        raise SystemExit("CAUSAL_UNIT5_NUMERIC_ERROR known simulation formula")
    known_effects = [
        -4.2 - 0.85 * ((row["baseline_sbp"] - 137.0) / 10.0)
        for row in rows
    ]
    known_sample_ate = sum(known_effects) / len(known_effects)
    known_participant_att = sum(
        effect for effect, assignment in zip(known_effects, treatment) if assignment == 1.0
    ) / sum(treatment)
    check(known_sample_ate, expected["known_simulation_sample_ate"], "known simulation sample ATE")
    checks += 1
    check(
        known_participant_att,
        expected["known_simulation_participant_att"],
        "known simulation participant ATT",
    )
    checks += 1
    for name in (
        "naive_difference",
        "outcome_regression_standardized_ate",
        "ipw_hajek_ate",
    ):
        bias = round(estimate_records[name][0], 6) - round(known_sample_ate, 6)
        check(
            bias,
            expected["reported_estimate_bias_vs_reported_sample_ate"][name],
            f"reported-estimate bias {name}",
        )
        checks += 1

    standardized_means = {
        "outcome_regression_if_not_joined": standardized_mean_not_joined,
        "outcome_regression_if_joined": standardized_mean_joined,
        "ipw_nonparticipants": ipw_mean_not_joined,
        "ipw_participants": ipw_mean_joined,
    }
    for name, value in standardized_means.items():
        check(value, expected["standardized_outcome_means"][name], f"standardized mean {name}")
        checks += 1

    propensity_values = {
        "minimum": min(probability),
        "p01": quantile(probability, 0.01),
        "median": quantile(probability, 0.50),
        "p99": quantile(probability, 0.99),
        "maximum": max(probability),
    }
    for name, value in propensity_values.items():
        check(value, expected["propensity_score_summary"][name], f"propensity {name}")
        checks += 1
    for name, value in (
        ("below_0_05", sum(pr < 0.05 for pr in probability)),
        ("above_0_95", sum(pr > 0.95 for pr in probability)),
    ):
        if value != expected["propensity_score_summary"][name]:
            raise SystemExit(f"CAUSAL_UNIT5_NUMERIC_ERROR propensity {name}")
        checks += 1

    observed_weight = [
        weight1 if assignment == 1.0 else weight0
        for assignment, weight1, weight0 in zip(treatment, treated_weight, control_weight)
    ]
    treated_observed = [weight for weight, assignment in zip(treated_weight, treatment) if assignment == 1.0]
    control_observed = [weight for weight, assignment in zip(control_weight, treatment) if assignment == 0.0]
    diagnostic_values = {
        "maximum_observed_weight": max(observed_weight),
        "effective_sample_size_participants": effective_sample_size(treated_observed),
        "effective_sample_size_nonparticipants": effective_sample_size(control_observed),
    }
    for name, value in diagnostic_values.items():
        check(value, expected["weight_diagnostics"][name], f"weights {name}")
        checks += 1

    before, after = balance(rows, treated_weight, control_weight)
    for section, actual in (
        ("standardized_mean_differences_before_weighting", before),
        ("standardized_mean_differences_after_weighting", after),
    ):
        for name, value in actual.items():
            check(value, expected["balance"][section][name], f"balance {section}.{name}")
            checks += 1
    check(max(abs(value) for value in before.values()), expected["balance"]["maximum_absolute_before"], "maximum balance before")
    checks += 1
    check(max(abs(value) for value in after.values()), expected["balance"]["maximum_absolute_after"], "maximum balance after")
    checks += 1

    propensity_names = (
        "intercept", "baseline_sbp_per_10", "age_per_10", "current_smoker",
        "taking_bp_medication", "transport_barrier", "clinic_mesa", "clinic_river",
    )
    for name, value in zip(propensity_names, propensity_beta):
        check(value, expected["propensity_coefficients"][name], f"propensity coefficient {name}")
        checks += 1
    outcome_names = (
        "intercept", "joined_coaching", "baseline_sbp_per_10", "age_per_10",
        "current_smoker", "taking_bp_medication", "transport_barrier", "clinic_mesa",
        "clinic_river", "joined_by_baseline_sbp_per_10",
    )
    for name, value in zip(outcome_names, outcome_beta):
        check(value, expected["outcome_regression_coefficients"][name], f"outcome coefficient {name}")
        checks += 1

    if checks != 78:
        raise SystemExit(f"CAUSAL_UNIT5_NUMERIC_ERROR internal check count {checks}")
    print(
        f"CAUSAL_UNIT5_INDEPENDENT_OK checks={checks} n={len(rows)} "
        f"joined={int(sum(treatment))} truth={known_sample_ate:.6f}"
    )


if __name__ == "__main__":
    main()
