#!/usr/bin/env python3
"""Independent standard-library recomputation of the v1.0 revision addenda.

Nothing here imports NumPy or the generator modules. The Unit 9 cell table and
the misclassification rates are restated from the unit's own documentation, and
the Unit 10 gap is refitted from the published CSV plus the replayed latent
engagement column with a hand-written solver.
"""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UNIT5_CSV = ROOT / "data" / "unit5_hypertension_coaching.csv"
REPLAY_CSV = ROOT / "data" / "unit10_latent_engagement_replay.csv"
RECORD = ROOT / "expected-results" / "book_revision_addenda_verified_results.json"
TOLERANCE = 0.000002

# site, high distress stratum, cell size, comparison risk, risk difference
CELLS = [
    ("Cedar", 0, 1000, 0.42, 0.10),
    ("Cedar", 1, 400, 0.28, 0.16),
    ("Lake", 0, 800, 0.39, 0.12),
    ("Lake", 1, 400, 0.25, 0.18),
    ("Ridge", 0, 500, 0.36, 0.14),
    ("Ridge", 1, 400, 0.23, 0.20),
    ("Harbor", 0, 200, 0.34, 0.16),
    ("Harbor", 1, 300, 0.20, 0.22),
]
SENSITIVITY = {"comparison": 0.82, "program": 0.91}
SPECIFICITY = {"comparison": 0.90, "program": 0.84}
STRUCTURAL_GAMMA = -2.2


def solve(matrix, vector):
    size = len(vector)
    augmented = [list(matrix[row]) + [vector[row]] for row in range(size)]
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
            augmented[row] = [left - factor * right
                              for left, right in zip(augmented[row], augmented[column])]
    return [augmented[row][-1] for row in range(size)]


def least_squares(design, outcome):
    width = len(design[0])
    normal = [[sum(row[i] * row[j] for row in design) for j in range(width)] for i in range(width)]
    moment = [sum(row[i] * value for row, value in zip(design, outcome)) for i in range(width)]
    return solve(normal, moment)


def close(left, right, label):
    if abs(left - right) > TOLERANCE:
        raise SystemExit("MISMATCH %s: %.9f vs %.9f" % (label, left, right))


def check_unit9(record):
    total = sum(cell[2] for cell in CELLS)
    program = comparison = truth_program = truth_comparison = 0.0
    for _site, _stratum, cell_n, control_risk, difference in CELLS:
        weight = cell_n / total
        risk_1 = control_risk + difference
        program += weight * (risk_1 * SENSITIVITY["program"]
                             + (1.0 - risk_1) * (1.0 - SPECIFICITY["program"]))
        comparison += weight * (control_risk * SENSITIVITY["comparison"]
                                + (1.0 - control_risk) * (1.0 - SPECIFICITY["comparison"]))
        truth_program += weight * risk_1
        truth_comparison += weight * control_risk
    close(program, record["expected_self_report_risk_program"], "unit9 expected program risk")
    close(comparison, record["expected_self_report_risk_comparison"],
          "unit9 expected comparison risk")
    close(program - comparison, record["expected_self_report_risk_difference"],
          "unit9 expected risk difference")
    close(truth_program - truth_comparison, record["hidden_blinded_risk_difference"],
          "unit9 hidden risk difference")
    close((program - comparison) - (truth_program - truth_comparison),
          record["expected_excess_of_self_report_contrast"], "unit9 expected excess")
    return program - comparison


def check_unit10(record):
    engagement = {row["participant_id"]: float(row["latent_engagement"])
                  for row in csv.DictReader(REPLAY_CSV.open(newline="", encoding="utf-8"))}
    design = []
    outcome = []
    baselines = []
    for row in csv.DictReader(UNIT5_CSV.open(newline="", encoding="utf-8")):
        treatment = float(row["joined_coaching"])
        baseline10 = (float(row["baseline_sbp"]) - 137.0) / 10.0
        covariates = [baseline10,
                      (float(row["age_years"]) - 54.0) / 10.0,
                      float(row["current_smoker"]),
                      float(row["taking_bp_medication"]),
                      float(row["transport_barrier"]),
                      1.0 if row["clinic"] == "Mesa" else 0.0,
                      1.0 if row["clinic"] == "River" else 0.0]
        design.append([1.0, treatment] + covariates + [treatment * baseline10])
        outcome.append(engagement[row["participant_id"]])
        baselines.append(baseline10)
    beta = least_squares(design, outcome)
    total = 0.0
    for row, baseline10 in zip(design, baselines):
        under_one = [1.0, 1.0] + row[2:-1] + [baseline10]
        under_zero = [1.0, 0.0] + row[2:-1] + [0.0]
        total += (sum(b * v for b, v in zip(beta, under_one))
                  - sum(b * v for b, v in zip(beta, under_zero)))
    delta = total / len(design)
    close(delta, record["structural_delta_u"], "unit10 structural delta")
    contribution = STRUCTURAL_GAMMA * delta
    close(contribution, record["structural_bias_contribution"], "unit10 bias contribution")
    adjusted = record["reported_estimate"] - contribution
    close(adjusted, record["estimate_after_removing_structural_contribution"],
          "unit10 adjusted estimate")
    close(adjusted - record["hidden_simulation_sample_ate"], record["remaining_discrepancy"],
          "unit10 remaining discrepancy")
    return delta


def main():
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    difference = check_unit9(record["unit9_expected_misclassification"])
    delta = check_unit10(record["unit10_structural_replay"])
    print("CAUSAL_ADDENDA_INDEPENDENT_OK",
          "expected_self_report_rd=%.6f" % difference,
          "structural_delta=%.6f" % delta,
          "tolerance=%g" % TOLERANCE)


if __name__ == "__main__":
    main()
