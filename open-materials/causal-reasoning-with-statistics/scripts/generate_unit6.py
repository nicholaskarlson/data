#!/usr/bin/env python3
"""Generate the deterministic synthetic Unit 6 municipality-month panel."""

import argparse
import csv
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "data" / "unit6_youth_crisis_policy.csv"
SEED = 20260919
REGIONS = ("North", "East", "South", "West")
N_MONTHS = 36
POLICY_START = 19


def generate_rows():
    rng = random.Random(SEED)
    rows = []
    for municipality_index in range(24):
        municipality_id = f"M{municipality_index + 1:02d}"
        region = REGIONS[municipality_index // 6]
        within_region = municipality_index % 6
        early_adopter = int(within_region < 3)

        # Early adoption is not randomized: early municipalities start somewhat
        # higher. Municipality fixed effects absorb this stable difference.
        municipality_intercept = rng.gauss(0.0, 0.75) + 0.85 * early_adopter
        region_offset = {"North": 0.35, "East": -0.15, "South": 0.20, "West": -0.40}[region]
        innovation = [rng.gauss(0.0, 0.46) for _ in range(N_MONTHS)]
        serial_error = [0.0] * N_MONTHS
        serial_error[0] = innovation[0] / math.sqrt(1.0 - 0.62 ** 2)
        for index in range(1, N_MONTHS):
            serial_error[index] = 0.62 * serial_error[index - 1] + innovation[index]

        for month_index in range(1, N_MONTHS + 1):
            post = int(month_index >= POLICY_START)
            policy_active = early_adopter * post
            relative_month = month_index - POLICY_START
            seasonal = (
                0.58 * math.sin(2.0 * math.pi * (month_index - 1) / 12.0)
                + 0.24 * math.cos(2.0 * math.pi * (month_index - 1) / 12.0)
            )
            common_trend = -0.018 * month_index
            regional_hotline_effect = -1.05 * post
            policy_effect = -1.70 * policy_active
            outcome = (
                12.4
                + municipality_intercept
                + region_offset
                + seasonal
                + common_trend
                + regional_hotline_effect
                + policy_effect
                + serial_error[month_index - 1]
            )
            rows.append(
                {
                    "municipality_id": municipality_id,
                    "region": region,
                    "month_index": month_index,
                    "relative_month": relative_month,
                    "early_adopter": early_adopter,
                    "regional_hotline_active": post,
                    "policy_active": policy_active,
                    "youth_emergency_transports_per_10000": round(float(outcome), 6),
                }
            )
    return rows


def write_rows(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = generate_rows()
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    rows = write_rows(arguments.output)
    print(
        "CAUSAL_UNIT6_DATA_OK",
        f"rows={len(rows)}",
        "municipalities=24",
        f"seed={SEED}",
    )


if __name__ == "__main__":
    main()
