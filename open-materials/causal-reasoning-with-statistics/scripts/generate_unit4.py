#!/usr/bin/env python3
"""Generate the deterministic Unit 4 blocked cluster-randomized sleep trial."""

import argparse
import csv
import hashlib
import math
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED = 20260916
STUDENTS_PER_FLOOR = 50
SECTORS = ("North", "East", "South", "West")
FLOORS_PER_SECTOR = 12
OUT = ROOT / "data" / "unit4_cluster_sleep_trial.csv"


def logistic(value: float) -> float:
    return 1.0 / (1.0 + math.exp(-value))


def generate():
    rng = random.Random(SEED)
    sector_effect = {"North": 1.0, "East": -0.5, "South": 0.5, "West": -1.0}
    rows = []
    student_number = 0

    for sector in SECTORS:
        treated_positions = set(rng.sample(range(FLOORS_PER_SECTOR), FLOORS_PER_SECTOR // 2))
        for floor_position in range(FLOORS_PER_SECTOR):
            assigned = int(floor_position in treated_positions)
            floor_shock = rng.gauss(0.0, 1.0)
            floor_id = f"{sector[0]}{floor_position + 1:02d}"

            for _ in range(STUDENTS_PER_FLOOR):
                student_number += 1
                motivation = rng.gauss(0.0, 1.0)
                baseline_sleep = (
                    6.8
                    + 0.10 * sector_effect[sector]
                    + 0.22 * floor_shock
                    + 0.35 * motivation
                    + rng.gauss(0.0, 0.7)
                )
                baseline_attention = (
                    65.0
                    + 1.6 * (baseline_sleep - 6.8)
                    + 1.8 * motivation
                    + 1.5 * floor_shock
                    + rng.gauss(0.0, 5.5)
                )

                use_probability = logistic(
                    -2.0
                    + 2.8 * assigned
                    + 0.65 * motivation
                    - 0.25 * (baseline_sleep - 6.8)
                )
                used_sleep_plan = int(rng.random() < use_probability)

                diary_probability = logistic(1.15 + 0.35 * assigned + 0.45 * motivation)
                completed_diary = int(rng.random() < diary_probability)

                followup_attention = (
                    31.0
                    + 0.52 * baseline_attention
                    + 0.9 * (baseline_sleep - 6.8)
                    + 3.0 * assigned
                    + 1.2 * motivation
                    + 2.2 * floor_shock
                    + sector_effect[sector]
                    + rng.gauss(0.0, 5.2)
                )
                followup_sleep = None
                if completed_diary:
                    followup_sleep = (
                        baseline_sleep
                        + 0.35 * assigned
                        + 0.25 * motivation
                        + 0.12 * floor_shock
                        + rng.gauss(0.0, 0.55)
                    )

                rows.append(
                    (
                        f"S{student_number:04d}",
                        sector,
                        floor_id,
                        assigned,
                        baseline_sleep,
                        baseline_attention,
                        used_sleep_plan,
                        completed_diary,
                        followup_sleep,
                        followup_attention,
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
                "student_id",
                "campus_sector",
                "residence_floor_id",
                "assigned_sleep_program",
                "baseline_sleep_hours",
                "baseline_attention_score",
                "used_sleep_plan",
                "completed_sleep_diary",
                "followup_sleep_hours",
                "followup_attention_score",
            )
        )
        for row in rows:
            writer.writerow(
                [
                    row[0],
                    row[1],
                    row[2],
                    row[3],
                    f"{row[4]:.8f}",
                    f"{row[5]:.8f}",
                    row[6],
                    row[7],
                    "" if row[8] is None else f"{row[8]:.8f}",
                    f"{row[9]:.8f}",
                ]
            )
    digest = hashlib.sha256(args.output.read_bytes()).hexdigest()
    print(
        "CAUSAL_UNIT4_DATA_OK",
        f"rows={len(rows)}",
        "floors=48",
        f"seed={SEED}",
        "sha256=" + digest,
    )


if __name__ == "__main__":
    main()
