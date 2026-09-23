#!/usr/bin/env python3
"""Generate the deterministic Unit 1 library-interface A/B teaching study."""
import argparse
import csv
import hashlib
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = 20260914
N = 1800
OUT = ROOT / "data" / "unit1_library_interface_ab.csv"


def generate():
    rng = random.Random(SEED)
    rows = []
    for person_id in range(1, N + 1):
        baseline_skill = 50 + 10 * rng.gauss(0, 1)
        difficult_task = int(rng.random() < 0.45)
        redesigned = int(rng.random() < 0.50)
        click_noise = rng.gauss(0, 1.5)
        score_noise = rng.gauss(0, 6.0)
        # Both potential task scores share score_noise. The individual effect
        # of assignment to the specified redesigned interface is 4 points.
        score_standard = 70 + 0.35 * (baseline_skill - 50) - 5 * difficult_task + score_noise
        score_redesigned = score_standard + 4.0
        task_score = score_redesigned if redesigned else score_standard
        clicks = (12 - 2.0 * redesigned - 0.08 * (baseline_skill - 50)
                  + 3.0 * difficult_task + click_noise)
        rows.append((person_id, baseline_skill, difficult_task, redesigned, clicks, task_score))
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUT)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(("person_id", "baseline_search_skill", "difficult_task",
                         "redesigned_interface", "clicks_during_task", "task_score"))
        for row in generate():
            writer.writerow([row[0]] + [f"{value:.8f}" if isinstance(value, float) else value
                                        for value in row[1:]])
    digest = hashlib.sha256(args.output.read_bytes()).hexdigest()
    print("CAUSAL_UNIT1_DATA_OK", f"rows={N}", f"seed={SEED}", "sha256=" + digest)


if __name__ == "__main__":
    main()
