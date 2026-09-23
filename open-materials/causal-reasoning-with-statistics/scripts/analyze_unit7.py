#!/usr/bin/env python3
"""Primary NumPy analysis for Unit 7 regression discontinuity and IV."""

import csv
import hashlib
import json
import math
import platform
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RD_DATA = ROOT / "data" / "unit7_tutoring_cutoff.csv"
IV_DATA = ROOT / "data" / "unit7_tutoring_encouragement.csv"
RESULT = ROOT / "expected-results" / "unit7_thresholds_encouragements_verified_results.json"
RD_CUTOFF = 60.0
RD_BANDWIDTH = 6.0
PLACEBO_CUTOFF = 70.0
PLACEBO_BANDWIDTH = 5.0
Z_975 = 1.959963985


def read_rd_rows():
    with RD_DATA.open(newline="", encoding="utf-8") as stream:
        return [
            {
                "applicant_id": row["applicant_id"],
                "diagnostic_score": float(row["diagnostic_score"]),
                "centered_score": float(row["centered_score"]),
                "tutoring_eligible": int(row["tutoring_eligible"]),
                "baseline_gpa": float(row["baseline_gpa"]),
                "end_term_math_score": float(row["end_term_math_score"]),
            }
            for row in csv.DictReader(stream)
        ]


def read_iv_rows():
    with IV_DATA.open(newline="", encoding="utf-8") as stream:
        return [
            {
                "student_id": row["student_id"],
                "encouragement_assignment": int(row["encouragement_assignment"]),
                "tutoring_received": int(row["tutoring_received"]),
                "baseline_math_score": float(row["baseline_math_score"]),
                "end_term_math_score": float(row["end_term_math_score"]),
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


def rd_fit(rows, outcome, cutoff, bandwidth):
    selected = [row for row in rows if abs(row["diagnostic_score"] - cutoff) <= bandwidth]
    centered = np.asarray([row["diagnostic_score"] - cutoff for row in selected])
    below = (centered < 0).astype(float)
    x = np.column_stack([np.ones(len(selected)), below, centered, below * centered])
    y = np.asarray([row[outcome] for row in selected], dtype=float)
    beta, covariance = hc1_fit(x, y)
    return float(beta[1]), float(np.sqrt(covariance[1, 1])), len(selected)


def record(estimate, se):
    return {
        "estimate": round(estimate, 6),
        "se": round(se, 6),
        "ci95_lower": round(estimate - Z_975 * se, 6),
        "ci95_upper": round(estimate + Z_975 * se, 6),
    }


def difference_in_means(rows, variable):
    z = np.asarray([row["encouragement_assignment"] for row in rows], dtype=int)
    values = np.asarray([row[variable] for row in rows], dtype=float)
    mean1 = float(values[z == 1].mean())
    mean0 = float(values[z == 0].mean())
    p = float(z.mean())
    influence = np.where(z == 1, (values - mean1) / p, -(values - mean0) / (1.0 - p))
    se = math.sqrt(float(np.sum(influence * influence)) / (len(rows) * (len(rows) - 1)))
    return mean1 - mean0, se, influence, mean1, mean0


def iv_wald(rows):
    reduced, reduced_se, reduced_if, outcome1, outcome0 = difference_in_means(
        rows, "end_term_math_score"
    )
    first, first_se, first_if, receipt1, receipt0 = difference_in_means(
        rows, "tutoring_received"
    )
    estimate = reduced / first
    influence = (reduced_if - estimate * first_if) / first
    se = math.sqrt(float(np.sum(influence * influence)) / (len(rows) * (len(rows) - 1)))
    return {
        "assignment_itt": record(reduced, reduced_se),
        "reduced_form": record(reduced, reduced_se),
        "first_stage": record(first, first_se),
        "wald_late": record(estimate, se),
        "outcome_means": {"encouraged": round(outcome1, 6), "not_encouraged": round(outcome0, 6)},
        "receipt_rates": {"encouraged": round(receipt1, 6), "not_encouraged": round(receipt0, 6)},
        "first_stage_f": round((first / first_se) ** 2, 6),
    }


def compute():
    rd_rows = read_rd_rows()
    iv_rows = read_iv_rows()
    primary_rd = rd_fit(rd_rows, "end_term_math_score", RD_CUTOFF, RD_BANDWIDTH)
    baseline_rd = rd_fit(rd_rows, "baseline_gpa", RD_CUTOFF, RD_BANDWIDTH)
    placebo_rd = rd_fit(rd_rows, "end_term_math_score", PLACEBO_CUTOFF, PLACEBO_BANDWIDTH)
    bandwidths = {}
    for bandwidth in (4.0, 6.0, 8.0, 10.0):
        estimate, se, n_local = rd_fit(
            rd_rows, "end_term_math_score", RD_CUTOFF, bandwidth
        )
        bandwidths[str(int(bandwidth))] = {
            "n_local": n_local,
            **record(estimate, se),
        }

    local_density = [row for row in rd_rows if abs(row["centered_score"]) <= 2.0]
    below = sum(row["centered_score"] < 0 for row in local_density)
    above = sum(row["centered_score"] >= 0 for row in local_density)
    z_statistic = (below - above) / math.sqrt(below + above)
    p_value = math.erfc(abs(z_statistic) / math.sqrt(2.0))
    iv = iv_wald(iv_rows)
    first_stage = iv["first_stage"]["estimate"]
    receipt0 = iv["receipt_rates"]["not_encouraged"]
    receipt1 = iv["receipt_rates"]["encouraged"]

    return {
        "title": "Unit 7 deterministic tutoring threshold and encouragement studies",
        "generator_seed": 20260920,
        "datasets": {
            "rd": {
                "filename": RD_DATA.name,
                "sha256": hashlib.sha256(RD_DATA.read_bytes()).hexdigest(),
                "n": len(rd_rows),
            },
            "iv": {
                "filename": IV_DATA.name,
                "sha256": hashlib.sha256(IV_DATA.read_bytes()).hexdigest(),
                "n": len(iv_rows),
            },
        },
        "rd_design": {
            "running_variable": "diagnostic_score",
            "cutoff": RD_CUTOFF,
            "eligibility_rule": "tutoring_eligible = 1 when diagnostic_score < 60",
            "prespecified_bandwidth": RD_BANDWIDTH,
            "placebo_cutoff": PLACEBO_CUTOFF,
            "placebo_bandwidth": PLACEBO_BANDWIDTH,
        },
        "rd_estimates": {
            "local_linear_discontinuity": {
                "n_local": primary_rd[2],
                **record(primary_rd[0], primary_rd[1]),
            },
            "baseline_gpa_continuity": {
                "n_local": baseline_rd[2],
                **record(baseline_rd[0], baseline_rd[1]),
            },
            "placebo_cutoff_discontinuity": {
                "n_local": placebo_rd[2],
                **record(placebo_rd[0], placebo_rd[1]),
            },
        },
        "rd_bandwidth_sensitivity": bandwidths,
        "rd_density_diagnostic": {
            "window": 2.0,
            "count_immediately_below": below,
            "count_immediately_above": above,
            "below_to_above_ratio": round(below / above, 6),
            "normal_approximation_z": round(z_statistic, 6),
            "two_sided_p": round(p_value, 6),
        },
        "known_simulation_rd_discontinuity": 4.2,
        "iv_design": {
            "n_encouraged": sum(row["encouragement_assignment"] for row in iv_rows),
            "n_not_encouraged": sum(1 - row["encouragement_assignment"] for row in iv_rows),
            "assignment_probability": 0.5,
        },
        "iv_estimates": {
            key: iv[key]
            for key in ("assignment_itt", "first_stage", "reduced_form", "wald_late")
        },
        "iv_outcome_means": iv["outcome_means"],
        "iv_receipt_rates": iv["receipt_rates"],
        "iv_principal_stratum_shares_implied_under_monotonicity": {
            "always_takers": round(receipt0, 6),
            "compliers": round(first_stage, 6),
            "never_takers": round(1.0 - receipt1, 6),
        },
        "iv_first_stage_f": iv["first_stage_f"],
        "known_simulation_complier_effect": 5.2,
        "interval_method": (
            "RD intervals use local linear regressions with separate slopes, HC1 covariance, "
            "and a normal critical value. Encouragement ITT and first-stage intervals use "
            "randomization-group influence functions; the Wald interval uses the joint "
            "delta-method influence function and a normal critical value."
        ),
        "identification_note": (
            "The sharp RD coefficient identifies a local eligibility effect at score 60 if "
            "potential-outcome regressions and baseline composition are continuous there and "
            "scores are not precisely manipulated. The Wald ratio identifies a complier average "
            "effect if encouragement is relevant, randomized, affects the outcome only through "
            "tutoring receipt, and does not reduce anyone's receipt. Neither estimand is "
            "automatically the population average treatment effect."
        ),
        "primary_environment": {"python": platform.python_version(), "numpy": np.__version__},
    }


def main():
    output = compute()
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "CAUSAL_UNIT7_PRIMARY_OK",
        f"rd={output['rd_estimates']['local_linear_discontinuity']['estimate']}",
        f"first_stage={output['iv_estimates']['first_stage']['estimate']}",
        f"wald={output['iv_estimates']['wald_late']['estimate']}",
    )


if __name__ == "__main__":
    main()
