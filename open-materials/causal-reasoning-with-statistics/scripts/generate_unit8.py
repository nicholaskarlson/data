#!/usr/bin/env python3
"""Generate the deterministic synthetic Unit 8 cognitive-training trial."""

import argparse
import csv
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "data" / "unit8_cognitive_training_trial.csv"
SEED = 20260929
N = 3200


def generate_rows():
    rng = random.Random(SEED)
    high_anxiety = [0] * 1920 + [1] * 1280
    rng.shuffle(high_anxiety)

    assignment = [0] * N
    for anxiety_group in (0, 1):
        indices = [index for index, value in enumerate(high_anxiety) if value == anxiety_group]
        allocations = [0] * (len(indices) // 2) + [1] * (len(indices) // 2)
        rng.shuffle(allocations)
        for index, allocation in zip(indices, allocations):
            assignment[index] = allocation

    rows = []
    for index, (assigned, anxiety) in enumerate(zip(assignment, high_anxiety), start=1):
        baseline = max(20.0, min(80.0, rng.gauss(50.0, 10.0)))
        self_regulation = rng.gauss(0.0, 1.0)
        strategy_use = (
            40.0
            + 7.0 * assigned
            + 0.18 * (baseline - 50.0)
            - 2.0 * anxiety
            + 4.0 * self_regulation
            + rng.gauss(0.0, 5.0)
        )
        controlled_direct_effect = 2.5 - 1.5 * anxiety
        followup = (
            50.0
            + 0.55 * (baseline - 50.0)
            - 2.0 * anxiety
            + controlled_direct_effect * assigned
            + 0.45 * strategy_use
            + 2.5 * self_regulation
            + rng.gauss(0.0, 6.0)
        )
        rows.append(
            {
                "participant_id": f"CT{index:04d}",
                "training_assignment": assigned,
                "baseline_memory_score": round(baseline, 6),
                "baseline_high_anxiety": anxiety,
                "strategy_use_score": round(strategy_use, 6),
                "followup_memory_score": round(followup, 6),
            }
        )
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    rows = generate_rows()
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    with arguments.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print("CAUSAL_UNIT8_DATA_OK", f"rows={len(rows)}", f"seed={SEED}")


if __name__ == "__main__":
    main()
