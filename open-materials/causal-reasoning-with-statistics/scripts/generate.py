#!/usr/bin/env python3
"""Generate an entirely synthetic, deterministic psychology teaching study.

No external dependencies. The unobserved fatigue variable and both potential
outcomes stay in the generator; the public CSV resembles an observed study.
"""
import csv
import hashlib
import random
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = 20260912
N = 2400
OUT = ROOT / "data" / "psychology_memory_training.csv"


def generate():
    rng = random.Random(SEED)
    rows = []
    for i in range(1, N + 1):
        baseline = 50 + 10 * rng.gauss(0, 1)
        fatigue = rng.gauss(0, 1)  # Unrecorded in the analyst's CSV.
        propensity = 1 / (1 + pow(2.718281828459045, -(-0.20 + 0.12 * (baseline - 50))))
        treatment = int(rng.random() < propensity)
        engagement_noise = rng.gauss(0, 0.7)
        help_noise = rng.gauss(0, 0.55)
        outcome_noise = rng.gauss(0, 3.0)
        # Under do(treatment=t), engagement changes by 1.2; memory changes
        # by 0.8 + 1.2*1.0 = 2.0 points for every synthetic individual.
        engagement = 1.2 * treatment + engagement_noise
        help_seeking = 1.3 * treatment + 1.15 * fatigue + help_noise
        outcome = (50 + 0.70 * (baseline - 50) + 0.8 * treatment
                   + engagement - 3.0 * fatigue + outcome_noise)
        rows.append((i, baseline, treatment, engagement, help_seeking, outcome))
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUT)
    args = parser.parse_args()
    target = args.output
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(("person_id", "baseline_memory", "training", "engagement_after",
                         "help_seeking_after", "memory_after"))
        for row in generate():
            writer.writerow([row[0]] + [f"{v:.8f}" if isinstance(v, float) else v
                                        for v in row[1:]])
    print("CAUSAL_DATA_GENERATE_OK", "rows=2400", "seed=20260912",
          "sha256=" + hashlib.sha256(target.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
