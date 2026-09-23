#!/usr/bin/env python3
"""Generate the deterministic synthetic Unit 9 multisite replication."""

import argparse
import csv
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "data" / "unit9_multisite_replication.csv"
SEED = 20261002

CELLS = (
    ("Cedar", 0, 1000, 0.42, 0.10, 0.12),
    ("Cedar", 1, 400, 0.28, 0.16, 0.10),
    ("Lake", 0, 800, 0.39, 0.12, 0.15),
    ("Lake", 1, 400, 0.25, 0.18, 0.13),
    ("Ridge", 0, 500, 0.36, 0.14, 0.10),
    ("Ridge", 1, 400, 0.23, 0.20, 0.15),
    ("Harbor", 0, 200, 0.34, 0.16, 0.08),
    ("Harbor", 1, 300, 0.20, 0.22, 0.17),
)
SITE_OBSERVATION_SHIFT = {"Cedar": 0.02, "Lake": 0.00, "Ridge": -0.02, "Harbor": -0.04}


def generate_rows():
    rng = random.Random(SEED)
    rows = []
    participant = 0
    for site, high_distress, cell_n, control_risk, risk_difference, _ in CELLS:
        allocation = [0] * (cell_n // 2) + [1] * (cell_n // 2)
        rng.shuffle(allocation)
        for assigned in allocation:
            participant += 1
            true_risk = control_risk + assigned * risk_difference
            true_improvement = int(rng.random() < true_risk)
            observation_probability = (
                0.90
                + 0.03 * assigned
                - 0.08 * high_distress
                + SITE_OBSERVATION_SHIFT[site]
            )
            outcome_observed = int(rng.random() < observation_probability)
            if true_improvement:
                sensitivity = 0.82 + 0.09 * assigned
                self_report = int(rng.random() < sensitivity)
            else:
                specificity = 0.90 - 0.06 * assigned
                self_report = int(rng.random() >= specificity)
            rows.append(
                {
                    "participant_id": f"MR{participant:04d}",
                    "site": site,
                    "baseline_high_distress": high_distress,
                    "program_assignment": assigned,
                    "blinded_outcome_observed": outcome_observed,
                    "blinded_improvement": true_improvement if outcome_observed else "",
                    "self_report_improvement": self_report,
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
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print("CAUSAL_UNIT9_DATA_OK", f"rows={len(rows)}", f"seed={SEED}")


if __name__ == "__main__":
    main()
