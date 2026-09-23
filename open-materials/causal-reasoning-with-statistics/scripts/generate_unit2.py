#!/usr/bin/env python3
"""Generate the deterministic Unit 2 multisite randomized-offer study."""
import argparse
import csv
import hashlib
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = 20260915
OUT = ROOT / "data" / "unit2_multisite_workshop_offer.csv"
SITE_SIZES = {"Cedar": 1200, "Lake": 720, "Ridge": 480}
SITE_STRESS = {"Cedar": -3.0, "Lake": 0.0, "Ridge": 4.0}
SITE_OUTCOME = {"Cedar": 1.5, "Lake": 0.0, "Ridge": -1.0}
SITE_UPTAKE_LOGIT = {"Cedar": -0.65, "Lake": 0.15, "Ridge": 0.85}
SITE_ATTENDANCE_EFFECT = {"Cedar": 2.0, "Lake": 3.5, "Ridge": 5.0}


def logistic(value):
    return 1.0 / (1.0 + math.exp(-value))


def generate():
    rng = random.Random(SEED)
    rows = []
    person_id = 0
    for site, size in SITE_SIZES.items():
        for _ in range(size):
            person_id += 1
            baseline_stress = 50 + SITE_STRESS[site] + 9 * rng.gauss(0, 1)
            offered = int(rng.random() < 0.50)
            latent_uptake_draw = rng.random()
            uptake_probability = logistic(
                SITE_UPTAKE_LOGIT[site] - 0.025 * (baseline_stress - 50)
            )
            would_attend_if_offered = int(latent_uptake_draw < uptake_probability)
            attended = offered * would_attend_if_offered
            outcome_noise = rng.gauss(0, 5.5)
            wellbeing_without_offer = (
                60 - 0.35 * (baseline_stress - 50) + SITE_OUTCOME[site] + outcome_noise
            )
            # The offer has a 0.4-point encouragement component. Attendance's
            # hidden structural effect differs with local implementation.
            wellbeing_after = (wellbeing_without_offer + 0.4 * offered
                               + SITE_ATTENDANCE_EFFECT[site] * attended)
            rows.append((person_id, site, baseline_stress, offered, attended, wellbeing_after))
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUT)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(("person_id", "site", "baseline_stress", "workshop_offer",
                         "attended_workshop", "wellbeing_after"))
        for row in generate():
            writer.writerow([row[0], row[1]] +
                            [f"{value:.8f}" if isinstance(value, float) else value
                             for value in row[2:]])
    digest = hashlib.sha256(args.output.read_bytes()).hexdigest()
    print("CAUSAL_UNIT2_DATA_OK", f"rows={sum(SITE_SIZES.values())}", f"seed={SEED}",
          "sha256=" + digest)


if __name__ == "__main__":
    main()
