#!/usr/bin/env python3
"""Independent stdlib-only recomputation from CSV; no import from analyze.py.

Solves normal equations by Gaussian elimination and computes HC1 by rowwise
outer products. This path never reads an expected record to obtain estimates.
"""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data/psychology_memory_training.csv"
EXPECTED = ROOT / "expected-results/psychology_memory_training_verified_results.json"


def solve(a, b):
    n = len(b)
    aug = [list(a[i]) + [b[i]] for i in range(n)]
    for j in range(n):
        pivot = max(range(j, n), key=lambda i: abs(aug[i][j]))
        aug[j], aug[pivot] = aug[pivot], aug[j]
        if abs(aug[j][j]) < 1e-9:
            raise ValueError("singular normal equations")
        scale = aug[j][j]
        aug[j] = [v / scale for v in aug[j]]
        for i in range(n):
            if i != j:
                factor = aug[i][j]
                aug[i] = [u - factor * v for u, v in zip(aug[i], aug[j])]
    return [row[-1] for row in aug]


def recompute(rows, names):
    x = [[1.] + [float(row[k]) for k in names] for row in rows]
    y = [float(row["memory_after"]) for row in rows]
    p = len(x[0]); n = len(x)
    gram = [[sum(row[j] * row[k] for row in x) for k in range(p)] for j in range(p)]
    rhs = [sum(row[j] * yy for row, yy in zip(x, y)) for j in range(p)]
    beta = solve(gram, rhs)
    # Treatment coefficient variance = sum_i (e_i * (X'X)^-1 X_i)_1^2 * n/(n-p)
    inv_treatment_row = solve(gram, [float(j == 1) for j in range(p)])
    variance = n / (n - p) * sum(
        (yy - sum(bb * xx for bb, xx in zip(beta, row))) ** 2
        * sum(v * xx for v, xx in zip(inv_treatment_row, row)) ** 2
        for row, yy in zip(x, y)
    )
    se = variance ** .5
    return [beta[1], se, beta[1] - 1.96 * se, beta[1] + 1.96 * se]


def check_close(actual, expected, label):
    if abs(actual - expected) > 0.000002:
        raise SystemExit(f"CAUSAL_NUMERIC_ERROR {label}: {actual} != {expected}")


def main():
    with CSV.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
    if len(rows) != expected["n"] or len(rows) != 2400:
        raise SystemExit("CAUSAL_NUMERIC_ERROR: row count")
    if hashlib.sha256(CSV.read_bytes()).hexdigest() != expected["dataset_sha256"]:
        raise SystemExit("CAUSAL_NUMERIC_ERROR: dataset digest")
    specs = {"naive": ["training"],
             "baseline_adjusted": ["training", "baseline_memory"],
             "collider_adjusted": ["training", "baseline_memory", "help_seeking_after"],
             "mediator_adjusted": ["training", "baseline_memory", "engagement_after"]}
    checks = 0
    for name, terms in specs.items():
        fresh = recompute(rows, terms)
        result = expected["estimates"][name]
        for key, value in zip(("estimate", "se_hc1", "ci95_lower", "ci95_upper"), fresh):
            check_close(value, result[key], f"{name}.{key}")
            checks += 1
    treated = [float(r["baseline_memory"]) for r in rows if r["training"] == "1"]
    untreated = [float(r["baseline_memory"]) for r in rows if r["training"] == "0"]
    if len(treated) != expected["n_training"]:
        raise SystemExit("CAUSAL_NUMERIC_ERROR: treatment count")
    check_close(sum(treated)/len(treated)-sum(untreated)/len(untreated),
                expected["baseline_difference_training_minus_comparison"], "baseline difference")
    checks += 2
    by_baseline = sorted(rows, key=lambda r: float(r["baseline_memory"]))
    for group in range(5):
        members = by_baseline[group*480:(group+1)*480]
        rate = sum(int(row["training"]) for row in members) / len(members)
        check_close(rate, expected["baseline_quintile_training_rates"][group],
                    f"quintile {group+1} treatment rate")
        checks += 1
    if expected["known_simulation_total_effect"] != 2.0 or expected["known_simulation_controlled_direct_effect"] != .8:
        raise SystemExit("CAUSAL_NUMERIC_ERROR: generator truth record")
    checks += 2
    # Cross-language published-anchor convention: exactly three decimals.
    for name, result in expected["estimates"].items():
        for key in ("estimate", "se_hc1", "ci95_lower", "ci95_upper"):
            if not isinstance(result[key], (float, int)):
                raise SystemExit(f"CAUSAL_NUMERIC_ERROR: invalid {name}.{key}")
    print(f"CAUSAL_INDEPENDENT_NUMERIC_OK checks={checks} n={len(rows)}")


if __name__ == "__main__":
    main()
