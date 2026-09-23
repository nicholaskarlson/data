#!/usr/bin/env python3
"""Generate the deterministic synthetic Unit 7 RD and encouragement studies."""

import argparse
import csv
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RD_OUTPUT = ROOT / "data" / "unit7_tutoring_cutoff.csv"
DEFAULT_IV_OUTPUT = ROOT / "data" / "unit7_tutoring_encouragement.csv"
SEED = 20260920
RD_CUTOFF = 60.0


def generate_rd_rows(rng):
    rows = []
    for index in range(2600):
        score = min(79.999999, max(40.000001, rng.gauss(60.0, 10.0)))
        centered = score - RD_CUTOFF
        eligible = int(score < RD_CUTOFF)
        baseline_gpa = 2.75 + 0.025 * centered + rng.gauss(0.0, 0.31)
        untreated = (
            67.0
            + 0.40 * centered
            + 0.012 * centered * centered
            + 1.7 * (baseline_gpa - 2.75)
            + rng.gauss(0.0, 4.9)
        )
        rows.append(
            {
                "applicant_id": f"RD{index + 1:04d}",
                "diagnostic_score": round(score, 6),
                "centered_score": round(centered, 6),
                "tutoring_eligible": eligible,
                "baseline_gpa": round(baseline_gpa, 6),
                "end_term_math_score": round(untreated + 4.2 * eligible, 6),
            }
        )
    return rows


def generate_iv_rows(rng):
    encouragement = [0] * 1500 + [1] * 1500
    rng.shuffle(encouragement)
    rows = []
    for index, assignment in enumerate(encouragement):
        baseline = rng.gauss(65.0, 9.0)
        latent_type = rng.random()
        if latent_type < 0.10:
            principal_stratum = "always-taker"
        elif latent_type < 0.68:
            principal_stratum = "complier"
        else:
            principal_stratum = "never-taker"
        received = int(
            principal_stratum == "always-taker"
            or (principal_stratum == "complier" and assignment == 1)
        )
        untreated = 52.0 + 0.46 * baseline + rng.gauss(0.0, 7.0)
        rows.append(
            {
                "student_id": f"IV{index + 1:04d}",
                "encouragement_assignment": assignment,
                "tutoring_received": received,
                "baseline_math_score": round(baseline, 6),
                "end_term_math_score": round(untreated + 5.2 * received, 6),
            }
        )
    return rows


def write_rows(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rd-output", type=Path, default=DEFAULT_RD_OUTPUT)
    parser.add_argument("--iv-output", type=Path, default=DEFAULT_IV_OUTPUT)
    arguments = parser.parse_args()
    rng = random.Random(SEED)
    rd_rows = generate_rd_rows(rng)
    iv_rows = generate_iv_rows(rng)
    write_rows(arguments.rd_output, rd_rows)
    write_rows(arguments.iv_output, iv_rows)
    print(
        "CAUSAL_UNIT7_DATA_OK",
        f"rd_rows={len(rd_rows)}",
        f"iv_rows={len(iv_rows)}",
        f"seed={SEED}",
    )


if __name__ == "__main__":
    main()
