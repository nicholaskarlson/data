#!/usr/bin/env python3
"""Generate the deterministic Unit 5 observational hypertension-coaching study."""

import argparse
import csv
import hashlib
import math
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED = 20260917
N = 3200
CLINICS = ("Harbor", "Mesa", "River")
OUT = ROOT / "data" / "unit5_hypertension_coaching.csv"


def logistic(value: float) -> float:
    if value >= 0:
        return 1.0 / (1.0 + math.exp(-value))
    exp_value = math.exp(value)
    return exp_value / (1.0 + exp_value)


def clipped(value: float, lower: float, upper: float) -> float:
    return min(upper, max(lower, value))


def generate():
    rng = random.Random(SEED)
    clinic_shift = {"Harbor": -1.5, "Mesa": 2.0, "River": 0.5}
    clinic_join = {"Harbor": 0.35, "Mesa": -0.30, "River": 0.0}
    rows = []

    for index in range(1, N + 1):
        draw = rng.random()
        clinic = "Harbor" if draw < 0.42 else "Mesa" if draw < 0.76 else "River"
        engagement = rng.gauss(0.0, 1.0)
        age = round(clipped(rng.gauss(54.0, 10.5), 30.0, 78.0), 1)
        smoker_probability = logistic(-0.85 + 0.15 * ((age - 54.0) / 10.0) - 0.20 * engagement)
        current_smoker = int(rng.random() < smoker_probability)
        transport_probability = logistic(
            -1.10
            + (0.55 if clinic == "Mesa" else -0.10 if clinic == "Harbor" else 0.10)
            - 0.18 * engagement
        )
        transport_barrier = int(rng.random() < transport_probability)
        medication_probability = logistic(
            -0.15 + 0.16 * ((age - 54.0) / 10.0) + 0.25 * current_smoker
        )
        taking_medication = int(rng.random() < medication_probability)
        baseline_sbp = (
            137.0
            + 0.36 * (age - 54.0)
            + 5.5 * current_smoker
            - 3.0 * taking_medication
            + clinic_shift[clinic]
            - 1.6 * engagement
            + rng.gauss(0.0, 8.2)
        )

        join_probability = logistic(
            -0.45
            + 0.42 * ((baseline_sbp - 137.0) / 10.0)
            + 0.18 * ((age - 54.0) / 10.0)
            + 0.38 * current_smoker
            + 0.42 * taking_medication
            - 1.25 * transport_barrier
            + clinic_join[clinic]
            + 0.78 * engagement
        )
        joined = int(rng.random() < join_probability)

        prior_visits = clipped(
            1.8
            + 0.48 * engagement
            + 0.30 * taking_medication
            - 0.28 * transport_barrier
            + (0.18 if clinic == "Harbor" else 0.0)
            + rng.gauss(0.0, 0.75),
            0.0,
            5.0,
        )
        treatment_effect = -4.2 - 0.85 * ((baseline_sbp - 137.0) / 10.0)
        followup_sbp = (
            58.0
            + 0.57 * baseline_sbp
            + 0.08 * (age - 54.0)
            + 2.2 * current_smoker
            - 2.1 * taking_medication
            + 0.9 * transport_barrier
            + clinic_shift[clinic]
            - 2.2 * engagement
            + treatment_effect * joined
            + rng.gauss(0.0, 6.8)
        )

        rows.append(
            (
                f"P{index:04d}",
                clinic,
                age,
                baseline_sbp,
                current_smoker,
                taking_medication,
                transport_barrier,
                joined,
                prior_visits,
                followup_sbp,
            )
        )
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUT)
    args = parser.parse_args()
    rows = generate()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(
            (
                "participant_id",
                "clinic",
                "age_years",
                "baseline_sbp",
                "current_smoker",
                "taking_bp_medication",
                "transport_barrier",
                "joined_coaching",
                "prior_year_preventive_visits",
                "followup_sbp",
            )
        )
        for row in rows:
            writer.writerow(
                [
                    row[0],
                    row[1],
                    f"{row[2]:.1f}",
                    f"{row[3]:.8f}",
                    row[4],
                    row[5],
                    row[6],
                    row[7],
                    f"{row[8]:.8f}",
                    f"{row[9]:.8f}",
                ]
            )
    digest = hashlib.sha256(args.output.read_bytes()).hexdigest()
    print(
        "CAUSAL_UNIT5_DATA_OK",
        f"rows={len(rows)}",
        f"seed={SEED}",
        "sha256=" + digest,
    )


if __name__ == "__main__":
    main()
