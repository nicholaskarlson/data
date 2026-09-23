#!/usr/bin/env python3
"""Primary NumPy analysis for Unit 5 observational standardization and IPW."""

import csv
import hashlib
import json
import math
import platform
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "unit5_hypertension_coaching.csv"
RESULT = ROOT / "expected-results" / "unit5_hypertension_coaching_verified_results.json"
CLINICS = ("Harbor", "Mesa", "River")
Z = 1.96
KNOWN_EFFECT_FORMULA = "-4.2 - 0.85 * ((baseline_sbp - 137) / 10)"
KNOWN_SAMPLE_ATE = -4.226560549403
KNOWN_PARTICIPANT_ATT = -4.328182504372


def read_rows():
    rows = []
    with DATA.open(newline="", encoding="utf-8") as stream:
        for raw in csv.DictReader(stream):
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
    return rows


def covariate_vector(row):
    return [
        (row["baseline_sbp"] - 137.0) / 10.0,
        (row["age_years"] - 54.0) / 10.0,
        row["current_smoker"],
        row["taking_bp_medication"],
        row["transport_barrier"],
        float(row["clinic"] == "Mesa"),
        float(row["clinic"] == "River"),
    ]


def known_individual_effect(row):
    """Return the generator-defined effect, used only for a teaching audit."""
    return -4.2 - 0.85 * ((row["baseline_sbp"] - 137.0) / 10.0)


def propensity_matrix(rows):
    return np.asarray([[1.0] + covariate_vector(row) for row in rows], dtype=float)


def outcome_matrix(rows, assignment=None, interaction=True):
    matrix = []
    for row in rows:
        treatment = row["joined_coaching"] if assignment is None else float(assignment)
        baseline10 = (row["baseline_sbp"] - 137.0) / 10.0
        values = [1.0, treatment] + covariate_vector(row)
        if interaction:
            values.append(treatment * baseline10)
        matrix.append(values)
    return np.asarray(matrix, dtype=float)


def ols_hc1(x, y):
    beta = np.linalg.lstsq(x, y, rcond=None)[0]
    residuals = y - x @ beta
    bread = np.linalg.inv(x.T @ x)
    meat = x.T @ (x * (residuals * residuals)[:, None])
    covariance = len(y) / (len(y) - x.shape[1]) * bread @ meat @ bread
    return beta, covariance


def contrast_record(estimate, se):
    return {
        "estimate": round(float(estimate), 6),
        "se": round(float(se), 6),
        "ci95_lower": round(float(estimate - Z * se), 6),
        "ci95_upper": round(float(estimate + Z * se), 6),
    }


def logistic_fit(x, treatment):
    beta = np.zeros(x.shape[1], dtype=float)
    for _ in range(100):
        linear = np.clip(x @ beta, -35.0, 35.0)
        probability = 1.0 / (1.0 + np.exp(-linear))
        weights = probability * (1.0 - probability)
        information = x.T @ (x * weights[:, None])
        score = x.T @ (treatment - probability)
        step = np.linalg.solve(information, score)
        beta = beta + step
        if np.max(np.abs(step)) < 1e-12:
            break
    else:
        raise RuntimeError("propensity model failed to converge")
    probability = 1.0 / (1.0 + np.exp(-np.clip(x @ beta, -35.0, 35.0)))
    return beta, np.clip(probability, 1e-9, 1.0 - 1e-9)


def ipw_hajek_with_sandwich(x, treatment, outcome, probability):
    n, p = x.shape
    treated_weight = treatment / probability
    control_weight = (1.0 - treatment) / (1.0 - probability)
    mean_treated = np.sum(treated_weight * outcome) / np.sum(treated_weight)
    mean_control = np.sum(control_weight * outcome) / np.sum(control_weight)

    u = np.zeros((n, p + 2), dtype=float)
    u[:, :p] = x * (treatment - probability)[:, None]
    u[:, p] = treated_weight * (outcome - mean_treated)
    u[:, p + 1] = control_weight * (outcome - mean_control)

    sensitivity = np.zeros((p + 2, p + 2), dtype=float)
    sensitivity[:p, :p] = x.T @ (x * (probability * (1.0 - probability))[:, None]) / n
    sensitivity[p, :p] = np.mean(
        (treated_weight * (1.0 - probability) * (outcome - mean_treated))[:, None] * x,
        axis=0,
    )
    sensitivity[p, p] = np.mean(treated_weight)
    sensitivity[p + 1, :p] = -np.mean(
        (control_weight * probability * (outcome - mean_control))[:, None] * x,
        axis=0,
    )
    sensitivity[p + 1, p + 1] = np.mean(control_weight)
    variability = (u.T @ u) / n
    inverse = np.linalg.inv(sensitivity)
    covariance = inverse @ variability @ inverse.T / n
    gradient = np.zeros(p + 2)
    gradient[p] = 1.0
    gradient[p + 1] = -1.0
    se = math.sqrt(float(gradient @ covariance @ gradient))
    return mean_treated - mean_control, se, mean_treated, mean_control, treated_weight, control_weight


def effective_sample_size(weights):
    return float(np.sum(weights) ** 2 / np.sum(weights * weights))


def standardized_mean_differences(rows, treated_weight, control_weight):
    names = (
        "baseline_sbp",
        "age_years",
        "current_smoker",
        "taking_bp_medication",
        "transport_barrier",
        "clinic_mesa",
        "clinic_river",
    )
    columns = np.asarray([covariate_vector(row) for row in rows], dtype=float)
    treatment = np.asarray([row["joined_coaching"] for row in rows], dtype=float)
    treated = treatment == 1.0
    control = ~treated
    unweighted = {}
    weighted = {}
    for index, name in enumerate(names):
        values = columns[:, index]
        denominator = math.sqrt(
            (float(np.var(values[treated], ddof=1)) + float(np.var(values[control], ddof=1))) / 2.0
        )
        raw_difference = float(np.mean(values[treated]) - np.mean(values[control]))
        weighted_treated = float(
            np.sum(treated_weight[treated] * values[treated]) / np.sum(treated_weight[treated])
        )
        weighted_control = float(
            np.sum(control_weight[control] * values[control]) / np.sum(control_weight[control])
        )
        unweighted[name] = round(raw_difference / denominator, 6)
        weighted[name] = round((weighted_treated - weighted_control) / denominator, 6)
    return unweighted, weighted


def compute():
    rows = read_rows()
    treatment = np.asarray([row["joined_coaching"] for row in rows], dtype=float)
    outcome = np.asarray([row["followup_sbp"] for row in rows], dtype=float)
    prior_visits = np.asarray([row["prior_year_preventive_visits"] for row in rows], dtype=float)

    naive_x = np.column_stack([np.ones(len(rows)), treatment])
    naive_beta, naive_covariance = ols_hc1(naive_x, outcome)
    naive = contrast_record(naive_beta[1], math.sqrt(float(naive_covariance[1, 1])))

    outcome_x = outcome_matrix(rows)
    outcome_beta, outcome_covariance = ols_hc1(outcome_x, outcome)
    outcome_one = outcome_matrix(rows, assignment=1)
    outcome_zero = outcome_matrix(rows, assignment=0)
    standardized_gradient = np.mean(outcome_one - outcome_zero, axis=0)
    standardized_estimate = float(standardized_gradient @ outcome_beta)
    standardized_se = math.sqrt(
        float(standardized_gradient @ outcome_covariance @ standardized_gradient)
    )
    outcome_standardized = contrast_record(standardized_estimate, standardized_se)

    propensity_x = propensity_matrix(rows)
    propensity_beta, probability = logistic_fit(propensity_x, treatment)
    standardized_mean_joined = float(np.mean(outcome_one @ outcome_beta))
    standardized_mean_not_joined = float(np.mean(outcome_zero @ outcome_beta))
    ipw_estimate, ipw_se, ipw_mean_joined, ipw_mean_not_joined, treated_weight, control_weight = ipw_hajek_with_sandwich(
        propensity_x, treatment, outcome, probability
    )
    ipw = contrast_record(ipw_estimate, ipw_se)

    negative_x = outcome_matrix(rows, interaction=False)
    negative_beta, negative_covariance = ols_hc1(negative_x, prior_visits)
    negative_control = contrast_record(
        negative_beta[1], math.sqrt(float(negative_covariance[1, 1]))
    )

    unweighted_smd, weighted_smd = standardized_mean_differences(
        rows, treated_weight, control_weight
    )
    observed_weight = np.where(treatment == 1.0, treated_weight, control_weight)
    treated_mask = treatment == 1.0
    control_mask = ~treated_mask
    quantiles = np.quantile(probability, [0.01, 0.5, 0.99])
    known_effects = np.asarray([known_individual_effect(row) for row in rows], dtype=float)
    known_sample_ate = float(np.mean(known_effects))
    known_participant_att = float(np.mean(known_effects[treated_mask]))
    if abs(known_sample_ate - KNOWN_SAMPLE_ATE) > 1e-11:
        raise RuntimeError("known simulation sample ATE drift")
    if abs(known_participant_att - KNOWN_PARTICIPANT_ATT) > 1e-11:
        raise RuntimeError("known simulation participant ATT drift")
    reported_sample_ate = round(known_sample_ate, 6)
    reported_bias = {
        "naive_difference": round(naive["estimate"] - reported_sample_ate, 6),
        "outcome_regression_standardized_ate": round(
            outcome_standardized["estimate"] - reported_sample_ate, 6
        ),
        "ipw_hajek_ate": round(ipw["estimate"] - reported_sample_ate, 6),
    }

    return {
        "title": "Unit 5 deterministic voluntary hypertension-coaching study",
        "dataset_sha256": hashlib.sha256(DATA.read_bytes()).hexdigest(),
        "generator_seed": 20260917,
        "n": len(rows),
        "n_joined": int(np.sum(treatment)),
        "participation_rate": round(float(np.mean(treatment)), 6),
        "known_simulation_individual_effect_formula": KNOWN_EFFECT_FORMULA,
        "known_simulation_sample_ate": reported_sample_ate,
        "known_simulation_participant_att": round(known_participant_att, 6),
        "reported_estimate_bias_vs_reported_sample_ate": reported_bias,
        "observed_followup_means": {
            "nonparticipants": round(float(np.mean(outcome[control_mask])), 6),
            "participants": round(float(np.mean(outcome[treated_mask])), 6),
        },
        "estimates": {
            "naive_difference": naive,
            "outcome_regression_standardized_ate": outcome_standardized,
            "ipw_hajek_ate": ipw,
            "negative_control_adjusted_association": negative_control,
        },
        "standardized_outcome_means": {
            "outcome_regression_if_not_joined": round(standardized_mean_not_joined, 6),
            "outcome_regression_if_joined": round(standardized_mean_joined, 6),
            "ipw_nonparticipants": round(float(ipw_mean_not_joined), 6),
            "ipw_participants": round(float(ipw_mean_joined), 6),
        },
        "propensity_score_summary": {
            "minimum": round(float(np.min(probability)), 6),
            "p01": round(float(quantiles[0]), 6),
            "median": round(float(quantiles[1]), 6),
            "p99": round(float(quantiles[2]), 6),
            "maximum": round(float(np.max(probability)), 6),
            "below_0_05": int(np.sum(probability < 0.05)),
            "above_0_95": int(np.sum(probability > 0.95)),
        },
        "weight_diagnostics": {
            "maximum_observed_weight": round(float(np.max(observed_weight)), 6),
            "effective_sample_size_participants": round(
                effective_sample_size(treated_weight[treated_mask]), 6
            ),
            "effective_sample_size_nonparticipants": round(
                effective_sample_size(control_weight[control_mask]), 6
            ),
        },
        "balance": {
            "standardized_mean_differences_before_weighting": unweighted_smd,
            "standardized_mean_differences_after_weighting": weighted_smd,
            "maximum_absolute_before": round(max(abs(value) for value in unweighted_smd.values()), 6),
            "maximum_absolute_after": round(max(abs(value) for value in weighted_smd.values()), 6),
        },
        "propensity_coefficients": {
            name: round(float(value), 8)
            for name, value in zip(
                (
                    "intercept",
                    "baseline_sbp_per_10",
                    "age_per_10",
                    "current_smoker",
                    "taking_bp_medication",
                    "transport_barrier",
                    "clinic_mesa",
                    "clinic_river",
                ),
                propensity_beta,
            )
        },
        "outcome_regression_coefficients": {
            name: round(float(value), 8)
            for name, value in zip(
                (
                    "intercept",
                    "joined_coaching",
                    "baseline_sbp_per_10",
                    "age_per_10",
                    "current_smoker",
                    "taking_bp_medication",
                    "transport_barrier",
                    "clinic_mesa",
                    "clinic_river",
                    "joined_by_baseline_sbp_per_10",
                ),
                outcome_beta,
            )
        },
        "interval_method": (
            "Outcome-regression standardization uses an HC1 covariance and a delta-method linear contrast. "
            "IPW uses normalized arm-specific weights and a stacked propensity-plus-outcome sandwich. "
            "Intervals use 1.96 as an introductory large-sample approximation."
        ),
        "identification_note": (
            "Either adjusted estimate requires consistency, positivity, accurate measurement, and conditional "
            "exchangeability given the prespecified measured covariates. The pre-exposure negative-control "
            "association is retained as evidence that residual confounding remains plausible."
        ),
        "primary_environment": {"python": platform.python_version(), "numpy": np.__version__},
    }


def main():
    output = compute()
    RESULT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "CAUSAL_UNIT5_PRIMARY_OK",
        f"n={output['n']}",
        f"joined={output['n_joined']}",
        f"or={output['estimates']['outcome_regression_standardized_ate']['estimate']}",
        f"ipw={output['estimates']['ipw_hajek_ate']['estimate']}",
        f"truth={output['known_simulation_sample_ate']}",
    )


if __name__ == "__main__":
    main()
