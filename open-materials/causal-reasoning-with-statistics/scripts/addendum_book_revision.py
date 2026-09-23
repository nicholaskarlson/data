#!/usr/bin/env python3
"""Primary NumPy path for the two quantities added in the book's v1.0 revision.

1. Unit 9: what the cell-standardized self-report contrast estimates in
   expectation under the generator's differential misclassification.
2. Unit 10: the generator's structural confounding contribution, obtained by
   replaying the Unit 5 data-generating process and recovering the latent
   engagement variable that the published CSV does not contain.

Both are hidden-simulator quantities disclosed for teaching audit only. The
replay writes data/unit10_latent_engagement_replay.csv so that the independent
Python and base-R paths can recheck the estimation without re-running Python's
pseudo-random number stream, which base R cannot reproduce.
"""

import csv
import importlib.util
import json
import platform
import random
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
UNIT5_CSV = ROOT / "data" / "unit5_hypertension_coaching.csv"
REPLAY_CSV = ROOT / "data" / "unit10_latent_engagement_replay.csv"
UNIT9_RECORD = ROOT / "expected-results" / "unit9_multisite_replication_verified_results.json"
UNIT10_RECORD = ROOT / "expected-results" / "unit10_cross_case_synthesis_verified_results.json"
RESULT = ROOT / "expected-results" / "book_revision_addenda_verified_results.json"

REPLAY_TOLERANCE = 1e-6


def load_module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# --------------------------------------------------------------------------
# Unit 9: expected self-report contrast under differential misclassification
# --------------------------------------------------------------------------
def unit9_expected_contrast():
    generator = load_module("generate_unit9")
    record = json.loads(UNIT9_RECORD.read_text(encoding="utf-8"))
    sensitivity = record["known_simulation_self_report_sensitivity"]
    specificity = record["known_simulation_self_report_specificity"]

    total = sum(cell[2] for cell in generator.CELLS)
    expected_program = 0.0
    expected_comparison = 0.0
    truth_program = 0.0
    truth_comparison = 0.0
    for _site, _high, cell_n, control_risk, risk_difference, _rate in generator.CELLS:
        weight = cell_n / total
        risk_1 = control_risk + risk_difference
        risk_0 = control_risk
        expected_program += weight * (
            risk_1 * sensitivity["program"] + (1.0 - risk_1) * (1.0 - specificity["program"]))
        expected_comparison += weight * (
            risk_0 * sensitivity["comparison"] + (1.0 - risk_0) * (1.0 - specificity["comparison"]))
        truth_program += weight * risk_1
        truth_comparison += weight * risk_0

    realized = record["estimates"]["sample_standardized_self_report"]["risk_difference"]
    hidden = record["known_simulation_sample_primary_effect"]["risk_difference"]
    assert abs(truth_program - truth_comparison - hidden) < 1e-9, "cell table disagrees with record"
    return {
        "expected_self_report_risk_comparison": round(expected_comparison, 6),
        "expected_self_report_risk_program": round(expected_program, 6),
        "expected_self_report_risk_difference": round(expected_program - expected_comparison, 6),
        "hidden_blinded_risk_difference": round(truth_program - truth_comparison, 6),
        "expected_excess_of_self_report_contrast": round(
            (expected_program - expected_comparison) - (truth_program - truth_comparison), 6),
        "realized_self_report_risk_difference": round(realized, 6),
        "sensitivity": sensitivity,
        "specificity": specificity,
        "note": ("The realized contrast lands near the hidden blinded value in this one sample. "
                 "In expectation the self-report contrast overstates it. One realization does not "
                 "estimate a repeated-sampling quantity."),
    }


# --------------------------------------------------------------------------
# Unit 10: structural replay of the Unit 5 generator
# --------------------------------------------------------------------------
def replay_unit5():
    """Re-run the Unit 5 generator and keep the latent engagement draw."""
    generator = load_module("generate_unit5")
    logistic, clipped = generator.logistic, generator.clipped
    rng = random.Random(generator.SEED)
    clinic_shift = {"Harbor": -1.5, "Mesa": 2.0, "River": 0.5}
    clinic_join = {"Harbor": 0.35, "Mesa": -0.30, "River": 0.0}
    rows = []
    for index in range(1, generator.N + 1):
        draw = rng.random()
        clinic = "Harbor" if draw < 0.42 else "Mesa" if draw < 0.76 else "River"
        engagement = rng.gauss(0.0, 1.0)
        age = round(clipped(rng.gauss(54.0, 10.5), 30.0, 78.0), 1)
        smoker_probability = logistic(-0.85 + 0.15 * ((age - 54.0) / 10.0) - 0.20 * engagement)
        current_smoker = int(rng.random() < smoker_probability)
        transport_probability = logistic(
            -1.10
            + (0.55 if clinic == "Mesa" else -0.10 if clinic == "Harbor" else 0.10)
            - 0.18 * engagement)
        transport_barrier = int(rng.random() < transport_probability)
        medication_probability = logistic(
            -0.15 + 0.16 * ((age - 54.0) / 10.0) + 0.25 * current_smoker)
        taking_medication = int(rng.random() < medication_probability)
        baseline_sbp = (137.0 + 0.36 * (age - 54.0) + 5.5 * current_smoker
                        - 3.0 * taking_medication + clinic_shift[clinic]
                        - 1.6 * engagement + rng.gauss(0.0, 8.2))
        join_probability = logistic(
            -0.45 + 0.42 * ((baseline_sbp - 137.0) / 10.0) + 0.18 * ((age - 54.0) / 10.0)
            + 0.38 * current_smoker + 0.42 * taking_medication - 1.25 * transport_barrier
            + clinic_join[clinic] + 0.78 * engagement)
        joined = int(rng.random() < join_probability)
        prior_visits = clipped(
            1.8 + 0.48 * engagement + 0.30 * taking_medication - 0.28 * transport_barrier
            + (0.18 if clinic == "Harbor" else 0.0) + rng.gauss(0.0, 0.75), 0.0, 5.0)
        treatment_effect = -4.2 - 0.85 * ((baseline_sbp - 137.0) / 10.0)
        followup_sbp = (58.0 + 0.57 * baseline_sbp + 0.08 * (age - 54.0)
                        + 2.2 * current_smoker - 2.1 * taking_medication
                        + 0.9 * transport_barrier + clinic_shift[clinic]
                        - 2.2 * engagement + treatment_effect * joined
                        + rng.gauss(0.0, 6.8))
        rows.append({
            "participant_id": "P%04d" % index,
            "clinic": clinic,
            "age_years": age,
            "baseline_sbp": baseline_sbp,
            "current_smoker": current_smoker,
            "taking_bp_medication": taking_medication,
            "transport_barrier": transport_barrier,
            "joined_coaching": joined,
            "prior_year_preventive_visits": prior_visits,
            "followup_sbp": followup_sbp,
            "latent_engagement": engagement,
        })
    return rows


def check_replay(replayed):
    """The replay must reproduce every published observable column."""
    published = list(csv.DictReader(UNIT5_CSV.open(newline="", encoding="utf-8")))
    if len(published) != len(replayed):
        raise SystemExit("replay row count differs from the published file")
    worst = 0.0
    for left, right in zip(published, replayed):
        if left["participant_id"] != right["participant_id"] or left["clinic"] != right["clinic"]:
            raise SystemExit("replay row order differs from the published file")
        for column in ("age_years", "baseline_sbp", "prior_year_preventive_visits", "followup_sbp"):
            worst = max(worst, abs(float(left[column]) - float(right[column])))
        for column in ("current_smoker", "taking_bp_medication", "transport_barrier",
                       "joined_coaching"):
            if int(left[column]) != int(right[column]):
                raise SystemExit("replay disagrees on %s" % column)
    if worst > REPLAY_TOLERANCE:
        raise SystemExit("replay differs from the published file by %g" % worst)
    return worst


def covariates(row):
    return [(row["baseline_sbp"] - 137.0) / 10.0,
            (row["age_years"] - 54.0) / 10.0,
            float(row["current_smoker"]),
            float(row["taking_bp_medication"]),
            float(row["transport_barrier"]),
            1.0 if row["clinic"] == "Mesa" else 0.0,
            1.0 if row["clinic"] == "River" else 0.0]


def standardized_engagement_gap(rows):
    """g-computation contrast in latent engagement, using the Unit 5 design matrix."""
    design = []
    for row in rows:
        treatment = float(row["joined_coaching"])
        baseline10 = (row["baseline_sbp"] - 137.0) / 10.0
        design.append([1.0, treatment] + covariates(row) + [treatment * baseline10])
    matrix = np.asarray(design, dtype=float)
    outcome = np.asarray([row["latent_engagement"] for row in rows], dtype=float)
    beta = np.linalg.lstsq(matrix, outcome, rcond=None)[0]
    under_one = matrix.copy()
    under_zero = matrix.copy()
    baseline10 = matrix[:, 2]
    under_one[:, 1] = 1.0
    under_one[:, -1] = baseline10
    under_zero[:, 1] = 0.0
    under_zero[:, -1] = 0.0
    return float(np.mean(under_one @ beta - under_zero @ beta))


def unit10_structural_replay():
    rows = replay_unit5()
    worst = check_replay(rows)
    with REPLAY_CSV.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["participant_id", "latent_engagement"])
        for row in rows:
            writer.writerow([row["participant_id"], "%.12f" % row["latent_engagement"]])

    unit10 = json.loads(UNIT10_RECORD.read_text(encoding="utf-8"))
    estimate = unit10["sensitivity_input"]["estimate"]
    hidden = unit10["sensitivity_input"]["hidden_simulation_sample_ate"]
    calibrated = unit10["hidden_calibration"]["gamma_u_at_delta_0_5_to_reach_hidden_truth"]
    structural_gamma = -2.2
    delta = standardized_engagement_gap(rows)
    contribution = structural_gamma * delta
    adjusted = estimate - contribution
    return {
        "replay_max_abs_difference_from_published_csv": float("%.3g" % worst),
        "structural_gamma_u": structural_gamma,
        "structural_delta_u": round(delta, 6),
        "structural_bias_contribution": round(contribution, 6),
        "reported_estimate": estimate,
        "estimate_after_removing_structural_contribution": round(adjusted, 6),
        "hidden_simulation_sample_ate": hidden,
        "remaining_discrepancy": round(adjusted - hidden, 6),
        "calibrated_gamma_u_at_delta_0_5": calibrated,
        "note": ("The calibrated value reaches the hidden effect by construction. Substituting the "
                 "generator's own parameters does not, because the gap also contains finite-sample "
                 "variation and the fitted model's approximation of the generator."),
    }


def main():
    output = {
        "title": "Addenda verified in the book's v1.0 revision",
        "unit9_expected_misclassification": unit9_expected_contrast(),
        "unit10_structural_replay": unit10_structural_replay(),
        "disclosure": ("Hidden simulator quantities, disclosed for teaching audit only. An analyst "
                       "working with the reader CSV alone could not compute them."),
    }
    RESULT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    nine = output["unit9_expected_misclassification"]
    ten = output["unit10_structural_replay"]
    print("CAUSAL_ADDENDA_PRIMARY_OK",
          "python=%s" % platform.python_version(), "numpy=%s" % np.__version__,
          "expected_self_report_rd=%s" % nine["expected_self_report_risk_difference"],
          "structural_delta=%s" % ten["structural_delta_u"],
          "remaining=%s" % ten["remaining_discrepancy"])


if __name__ == "__main__":
    main()
