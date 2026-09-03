#!/usr/bin/env python3
"""Recompute Volume 2's teaching results from its pinned CSV inputs.

Like ``verify_resource_numbers.py``, this check intentionally uses only the
Python standard library and the raw CSV files.  It does not read the
repository's ``expected-results`` JSON records, so it is an independent guard
against document or dataset drift: every value asserted below is a value that
appears in the published Volume 2 document.

Volume 2 covers four studies:

* ``study_08_help_seeking_categorical``   - Unit 12, plus two prior-support subsets
* ``study_09_skewed_wellbeing_nonparametric`` - Unit 13, plus the outlier-deleted variant
* ``study_10_developmental_emotion_recognition`` - Unit 14, plus the two-band contrast
* ``study_11_single_case_habit_tracking``  - Unit 15, plus the days-as-people error
"""

from __future__ import annotations

import csv
import math
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RESOURCE = ROOT / "open-materials/psychology-statistics-practice-with-jamovi-volume-2"
DOCX = RESOURCE / (
    "psychology-statistics-practice-materials-with-jamovi-volume-2-open-resource-v1.0.docx"
)
VOLUME = "2"
VERSION = "1.0"
CHECKS = 0


def fail(message: str) -> None:
    print(f"VOLUME2_NUMERIC_AUDIT_ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def check(condition: bool, label: str) -> None:
    global CHECKS
    CHECKS += 1
    if not condition:
        fail(label)


def close(actual: float, expected: float, label: str, tolerance: float = 5e-4) -> None:
    """Compare against a value as printed in the document.

    The document rounds; the tolerance is therefore a printing tolerance rather
    than a numerical one.  Pass a tighter tolerance for values printed to more
    places.
    """
    check(
        math.isclose(actual, expected, rel_tol=0.0, abs_tol=tolerance),
        f"{label}: document says {expected:.12g}, recomputation gives {actual:.12g}",
    )


# --------------------------------------------------------------------------
# small statistical helpers (standard library only)
# --------------------------------------------------------------------------
def average(values: list[float]) -> float:
    return math.fsum(values) / len(values)


def sample_variance(values: list[float]) -> float:
    center = average(values)
    return math.fsum((value - center) ** 2 for value in values) / (len(values) - 1)


def sample_sd(values: list[float]) -> float:
    return math.sqrt(sample_variance(values))


def median(values: list[float]) -> float:
    ordered = sorted(values)
    size = len(ordered)
    middle = size // 2
    if size % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2.0


def quantile(values: list[float], probability: float) -> float:
    """Linear interpolation between order statistics (R type 7)."""
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    low = math.floor(position)
    high = math.ceil(position)
    if low == high:
        return ordered[low]
    return ordered[low] + (position - low) * (ordered[high] - ordered[low])


def beta_continued_fraction(a: float, b: float, x: float) -> float:
    epsilon = 3e-14
    floor = 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < floor:
        d = floor
    d = 1.0 / d
    result = d
    for iteration in range(1, 400):
        even = 2 * iteration
        aa = iteration * (b - iteration) * x / ((qam + even) * (a + even))
        d = 1.0 + aa * d
        if abs(d) < floor:
            d = floor
        c = 1.0 + aa / c
        if abs(c) < floor:
            c = floor
        d = 1.0 / d
        result *= d * c
        aa = -(a + iteration) * (qab + iteration) * x / ((a + even) * (qap + even))
        d = 1.0 + aa * d
        if abs(d) < floor:
            d = floor
        c = 1.0 + aa / c
        if abs(c) < floor:
            c = floor
        d = 1.0 / d
        delta = d * c
        result *= delta
        if abs(delta - 1.0) < epsilon:
            return result
    fail("incomplete-beta continued fraction did not converge")
    raise AssertionError


def regularized_beta(x: float, a: float, b: float) -> float:
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    factor = math.exp(
        math.lgamma(a + b)
        - math.lgamma(a)
        - math.lgamma(b)
        + a * math.log(x)
        + b * math.log1p(-x)
    )
    if x < (a + 1.0) / (a + b + 2.0):
        return factor * beta_continued_fraction(a, b, x) / a
    return 1.0 - factor * beta_continued_fraction(b, a, 1.0 - x) / b


def student_t_cdf(value: float, df: float) -> float:
    x = df / (df + value * value)
    tail = 0.5 * regularized_beta(x, df / 2.0, 0.5)
    return 1.0 - tail if value >= 0.0 else tail


def student_t_ppf(probability: float, df: float) -> float:
    if not 0.0 < probability < 1.0:
        fail(f"t quantile probability outside (0,1): {probability}")
    if probability == 0.5:
        return 0.0
    if probability < 0.5:
        return -student_t_ppf(1.0 - probability, df)
    low, high = 0.0, 1.0
    while student_t_cdf(high, df) < probability:
        high *= 2.0
    for _ in range(200):
        middle = (low + high) / 2.0
        if student_t_cdf(middle, df) < probability:
            low = middle
        else:
            high = middle
    return (low + high) / 2.0


def f_sf(value: float, df1: float, df2: float) -> float:
    x = df1 * value / (df1 * value + df2)
    return 1.0 - regularized_beta(x, df1 / 2.0, df2 / 2.0)


def regularized_lower_gamma(shape: float, x: float) -> float:
    if x <= 0.0:
        return 0.0
    if x < shape + 1.0:
        term = 1.0 / shape
        total = term
        n = shape
        for _ in range(4000):
            n += 1.0
            term *= x / n
            total += term
            if abs(term) < abs(total) * 1e-16:
                break
        return total * math.exp(-x + shape * math.log(x) - math.lgamma(shape))
    tiny = 1e-300
    b = x + 1.0 - shape
    c = 1.0 / tiny
    d = 1.0 / b
    h = d
    for i in range(1, 4000):
        an = -i * (i - shape)
        b += 2.0
        d = an * d + b
        if abs(d) < tiny:
            d = tiny
        c = b + an / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-16:
            break
    upper = math.exp(-x + shape * math.log(x) - math.lgamma(shape)) * h
    return 1.0 - upper


def chi_square_sf(value: float, df: float) -> float:
    return 1.0 - regularized_lower_gamma(df / 2.0, value / 2.0)


def normal_sf(z: float) -> float:
    return 0.5 * math.erfc(z / math.sqrt(2.0))


def average_ranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        shared = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = shared
        i = j + 1
    return ranks


def matrix_inverse(matrix: list[list[float]]) -> list[list[float]]:
    size = len(matrix)
    work = [
        row[:] + [1.0 if i == j else 0.0 for j in range(size)]
        for i, row in enumerate(matrix)
    ]
    for column in range(size):
        pivot_row = max(range(column, size), key=lambda r: abs(work[r][column]))
        work[column], work[pivot_row] = work[pivot_row], work[column]
        pivot = work[column][column]
        if pivot == 0.0:
            fail("singular design matrix")
        work[column] = [value / pivot for value in work[column]]
        for row in range(size):
            if row == column:
                continue
            factor = work[row][column]
            work[row] = [a - factor * b for a, b in zip(work[row], work[column])]
    return [row[size:] for row in work]


def rows(name: str) -> list[dict[str, str]]:
    with (DATA / f"{name}.csv").open(encoding="utf-8", newline="") as source:
        return list(csv.DictReader(source))


def numbers(records: list[dict[str, str]], column: str) -> list[float]:
    return [float(record[column]) for record in records if record[column] != ""]


def holm(p_values: dict[str, float]) -> dict[str, float]:
    ordered = sorted(p_values.items(), key=lambda item: item[1])
    total = len(ordered)
    running = 0.0
    adjusted: dict[str, float] = {}
    for index, (key, value) in enumerate(ordered):
        running = max(running, min(1.0, (total - index) * value))
        adjusted[key] = running
    return adjusted


def contingency(
    records: list[dict[str, str]],
    row_variable: str,
    column_variable: str,
    row_levels: list[str],
    column_levels: list[str],
) -> dict[str, object]:
    observed = {r: {c: 0 for c in column_levels} for r in row_levels}
    for record in records:
        observed[record[row_variable]][record[column_variable]] += 1
    grand = len(records)
    row_totals = {r: sum(observed[r].values()) for r in row_levels}
    column_totals = {c: sum(observed[r][c] for r in row_levels) for c in column_levels}
    statistic = 0.0
    expected = {r: {} for r in row_levels}
    for r in row_levels:
        for c in column_levels:
            e = row_totals[r] * column_totals[c] / grand
            expected[r][c] = e
            statistic += (observed[r][c] - e) ** 2 / e
    df = (len(row_levels) - 1) * (len(column_levels) - 1)
    smaller = min(len(row_levels), len(column_levels))
    return {
        "observed": observed,
        "expected": expected,
        "row_totals": row_totals,
        "column_totals": column_totals,
        "grand": grand,
        "chi_square": statistic,
        "df": df,
        "p": chi_square_sf(statistic, df),
        "cramers_v": math.sqrt(statistic / (grand * (smaller - 1))),
        "minimum_expected": min(
            expected[r][c] for r in row_levels for c in column_levels
        ),
    }


def mann_whitney(first: list[float], second: list[float]) -> dict[str, float]:
    combined = first + second
    ranks = average_ranks(combined)
    n1, n2 = len(first), len(second)
    u1 = math.fsum(ranks[:n1]) - n1 * (n1 + 1) / 2.0
    mean_u = n1 * n2 / 2.0
    counts = Counter(combined)
    tie_term = math.fsum(t**3 - t for t in counts.values())
    n = n1 + n2
    sigma = math.sqrt(n1 * n2 / 12.0 * ((n + 1) - tie_term / (n * (n - 1))))
    if u1 == mean_u:
        z = 0.0
    else:
        z = (u1 - mean_u - math.copysign(0.5, u1 - mean_u)) / sigma
    return {
        "u": u1,
        "z": z,
        "p": 2.0 * normal_sf(abs(z)),
        "rank_biserial": 2.0 * u1 / (n1 * n2) - 1.0,
    }


def nonoverlap(baseline: list[float], comparison: list[float], higher_is_better: bool) -> float:
    total = 0.0
    for b in baseline:
        for c in comparison:
            if c == b:
                total += 0.5
            elif (c > b) == higher_is_better:
                total += 1.0
    return total / (len(baseline) * len(comparison))


# --------------------------------------------------------------------------
# Unit 12 - study_08_help_seeking_categorical
# --------------------------------------------------------------------------
MESSAGES = ["autonomy_message", "belonging_message", "skills_message"]
RESOURCES = ["advisor_meeting", "peer_group", "self_guided_module"]


def audit_unit_12() -> None:
    records = rows("study_08_help_seeking_categorical")
    check(len(records) == 150, "study_08 row count is not 150")

    table = contingency(records, "message_condition", "resource_choice", MESSAGES, RESOURCES)
    observed = table["observed"]
    expected = table["expected"]

    for message in MESSAGES:
        check(table["row_totals"][message] == 50, f"study_08 row total for {message} is not 50")
    for resource, total in (("advisor_meeting", 57), ("peer_group", 42), ("self_guided_module", 51)):
        check(
            table["column_totals"][resource] == total,
            f"study_08 column total for {resource} is not {total}",
        )

    printed_observed = {
        ("autonomy_message", "advisor_meeting"): 14,
        ("autonomy_message", "peer_group"): 13,
        ("autonomy_message", "self_guided_module"): 23,
        ("belonging_message", "advisor_meeting"): 20,
        ("belonging_message", "peer_group"): 22,
        ("belonging_message", "self_guided_module"): 8,
        ("skills_message", "advisor_meeting"): 23,
        ("skills_message", "peer_group"): 7,
        ("skills_message", "self_guided_module"): 20,
    }
    for (message, resource), count in printed_observed.items():
        check(
            observed[message][resource] == count,
            f"study_08 observed count for {message}/{resource} is not {count}",
        )

    printed_expected = {
        "advisor_meeting": 19.0,
        "peer_group": 14.0,
        "self_guided_module": 17.0,
    }
    for message in MESSAGES:
        for resource, value in printed_expected.items():
            close(expected[message][resource], value, f"study_08 expected {message}/{resource}", 5e-9)

    # Solution 12.10 cell contributions
    close(
        (22 - 14.0) ** 2 / 14.0, 4.571, "Solution 12.10 belonging/peer contribution", 5e-4
    )
    close(
        (8 - 17.0) ** 2 / 17.0, 4.765, "Solution 12.10 belonging/self-guided contribution", 5e-4
    )
    close(
        (22 - 14.0) ** 2 / 14.0 + (8 - 17.0) ** 2 / 17.0,
        9.336,
        "Solution 12.10 combined contribution",
        5e-4,
    )

    close(table["chi_square"], 17.765, "Unit 12 chi-square", 5e-4)
    check(table["df"] == 4, "Unit 12 degrees of freedom are not 4")
    close(table["p"], 0.001372, "Unit 12 p value", 5e-6)
    close(table["cramers_v"], 0.243, "Unit 12 Cramer's V", 5e-4)
    close(table["minimum_expected"], 14.0, "Unit 12 minimum expected count", 5e-9)

    # Solution 12.12 percentages
    close(100 * 23 / 50, 46.0, "Solution 12.12 row percentage", 5e-4)
    close(100 * 23 / 51, 45.098, "Solution 12.12 column percentage", 5e-4)

    # Study 08A: prior_support_use == yes
    subset_yes = [r for r in records if r["prior_support_use"] == "yes"]
    check(len(subset_yes) == 58, "Study 08A does not contain 58 rows")
    a = contingency(subset_yes, "message_condition", "resource_choice", MESSAGES, RESOURCES)
    close(a["chi_square"], 7.912, "Study 08A chi-square", 5e-4)
    close(a["p"], 0.095, "Study 08A p value", 5e-4)
    close(a["cramers_v"], 0.261, "Study 08A Cramer's V", 5e-4)
    close(a["minimum_expected"], 4.69, "Study 08A minimum expected count", 5e-3)
    check(min(a["row_totals"].values()) == 17, "Study 08A smallest row total is not 17")
    check(min(a["column_totals"].values()) == 16, "Study 08A smallest column total is not 16")
    close(17 * 16 / 58, 4.69, "Solution 12.8 hand calculation", 5e-3)

    # Study 08B: prior_support_use == no
    subset_no = [r for r in records if r["prior_support_use"] == "no"]
    check(len(subset_no) == 92, "Study 08B does not contain 92 rows")
    b = contingency(subset_no, "message_condition", "resource_choice", MESSAGES, RESOURCES)
    close(b["chi_square"], 12.105, "Study 08B chi-square", 5e-4)
    close(b["p"], 0.017, "Study 08B p value", 5e-4)
    close(b["cramers_v"], 0.256, "Study 08B Cramer's V", 5e-4)
    close(b["minimum_expected"], 7.00, "Study 08B minimum expected count", 5e-3)

    # Balance check reported in Problem 12.16
    balance = contingency(
        records, "message_condition", "prior_support_use", MESSAGES, ["yes", "no"]
    )
    close(balance["chi_square"], 1.068, "Problem 12.16 balance chi-square", 5e-4)
    check(balance["df"] == 2, "Problem 12.16 balance degrees of freedom are not 2")
    close(balance["p"], 0.586, "Problem 12.16 balance p value", 5e-4)
    close(balance["cramers_v"], 0.084, "Problem 12.16 balance Cramer's V", 5e-4)


# --------------------------------------------------------------------------
# Unit 13 - study_09_skewed_wellbeing_nonparametric
# --------------------------------------------------------------------------
APP_GROUPS = ["low", "moderate", "high"]


def kruskal_wallis(groups: dict[str, list[float]], order: list[str]) -> dict[str, object]:
    pooled = [value for key in order for value in groups[key]]
    labels = [key for key in order for _ in groups[key]]
    ranks = average_ranks(pooled)
    n = len(pooled)
    mean_ranks = {
        key: average([ranks[i] for i in range(n) if labels[i] == key]) for key in order
    }
    uncorrected = (
        12.0
        / (n * (n + 1))
        * math.fsum(len(groups[key]) * (mean_ranks[key] - (n + 1) / 2.0) ** 2 for key in order)
    )
    counts = Counter(pooled)
    tie_term = math.fsum(t**3 - t for t in counts.values())
    correction = 1.0 - tie_term / (n**3 - n)
    statistic = uncorrected / correction
    k = len(order)
    return {
        "n": n,
        "mean_ranks": mean_ranks,
        "rank_sums": {
            key: math.fsum(ranks[i] for i in range(n) if labels[i] == key) for key in order
        },
        "uncorrected": uncorrected,
        "tie_correction": correction,
        "h": statistic,
        "df": k - 1,
        "p": chi_square_sf(statistic, k - 1),
        # jamovi's jmv::anovaNP reports H / (N - 1) as epsilon-squared.
        "epsilon_squared": statistic / (n - 1),
        # Preserve the small-sample-adjusted quantity under a distinct label.
        "bias_adjusted_rank_effect_size": (statistic - k + 1) / (n - k),
    }


def audit_unit_13() -> None:
    records = rows("study_09_skewed_wellbeing_nonparametric")
    check(len(records) == 132, "study_09 row count is not 132")

    groups = {
        key: [
            float(r["wellbeing_score"]) for r in records if r["app_use_group"] == key
        ]
        for key in APP_GROUPS
    }
    for key in APP_GROUPS:
        check(len(groups[key]) == 44, f"study_09 group {key} does not contain 44 rows")

    printed = {
        "low": dict(
            mean=56.420, median=55.65, sd=9.461, minimum=26.9, q1=51.800, q3=61.675,
            maximum=78.0, iqr=9.875, flagged=2,
        ),
        "moderate": dict(
            mean=61.834, median=62.10, sd=7.167, minimum=47.9, q1=57.175, q3=66.500,
            maximum=82.3, iqr=9.325, flagged=1,
        ),
        "high": dict(
            mean=49.702, median=49.00, sd=7.479, minimum=31.3, q1=44.775, q3=55.325,
            maximum=65.4, iqr=10.550, flagged=0,
        ),
    }
    for key, values in printed.items():
        data = groups[key]
        close(average(data), values["mean"], f"Unit 13 {key} mean")
        close(median(data), values["median"], f"Unit 13 {key} median")
        close(sample_sd(data), values["sd"], f"Unit 13 {key} SD")
        close(min(data), values["minimum"], f"Unit 13 {key} minimum")
        close(max(data), values["maximum"], f"Unit 13 {key} maximum")
        close(quantile(data, 0.25), values["q1"], f"Unit 13 {key} first quartile")
        close(quantile(data, 0.75), values["q3"], f"Unit 13 {key} third quartile")
        close(
            quantile(data, 0.75) - quantile(data, 0.25),
            values["iqr"],
            f"Unit 13 {key} interquartile range",
        )
        flagged = sum(
            1
            for r in records
            if r["app_use_group"] == key and r["outlier_flag"] == "yes"
        )
        check(
            flagged == values["flagged"],
            f"Unit 13 {key} flagged-observation count is not {values['flagged']}",
        )

    result = kruskal_wallis(groups, APP_GROUPS)
    close(result["rank_sums"]["low"], 3029.0, "Solution 13.9 low rank sum", 5e-9)
    close(result["rank_sums"]["moderate"], 3999.5, "Solution 13.9 moderate rank sum", 5e-9)
    close(result["rank_sums"]["high"], 1749.5, "Solution 13.9 high rank sum", 5e-9)
    close(
        math.fsum(result["rank_sums"].values()),
        132 * 133 / 2,
        "Solution 13.9 rank-sum total",
        5e-9,
    )
    close(result["mean_ranks"]["low"], 68.841, "Unit 13 low mean rank")
    close(result["mean_ranks"]["moderate"], 90.898, "Unit 13 moderate mean rank")
    close(result["mean_ranks"]["high"], 39.761, "Unit 13 high mean rank")
    close(result["uncorrected"], 39.569, "Solution 13.7 uncorrected statistic")
    close(result["tie_correction"], 0.999903, "Solution 13.7 tie correction", 5e-7)
    close(result["h"], 39.573, "Unit 13 Kruskal-Wallis statistic")
    check(result["df"] == 2, "Unit 13 Kruskal-Wallis degrees of freedom are not 2")
    close(result["epsilon_squared"], 0.302, "Unit 13 jamovi epsilon-squared")
    close(
        result["bias_adjusted_rank_effect_size"],
        0.291,
        "Unit 13 bias-adjusted rank effect size",
    )
    check(result["p"] < 0.001, "Unit 13 Kruskal-Wallis p value is not below .001")

    # tie structure quoted in Problem 13.7
    counts = Counter(float(r["wellbeing_score"]) for r in records)
    check(len(counts) == 110, "Problem 13.7 distinct-value count is not 110")
    check(
        sum(1 for value in counts.values() if value > 1) == 16,
        "Problem 13.7 tied-value count is not 16",
    )
    check(max(counts.values()) == 4, "Problem 13.7 largest tie group is not 4")

    pairs = [("low", "moderate"), ("low", "high"), ("moderate", "high")]
    printed_pairs = {
        "low__moderate": dict(u=620.5, z=-2.896, p=0.00378, holm=0.00378, rb=-0.359),
        "low__high": dict(u=1418.5, z=3.756, p=0.000173, holm=0.000346, rb=0.465),
        "moderate__high": dict(u=1694.0, z=6.055, p=1.41e-9, holm=4.22e-9, rb=0.750),
    }
    raw: dict[str, float] = {}
    computed: dict[str, dict[str, float]] = {}
    for first, second in pairs:
        key = f"{first}__{second}"
        computed[key] = mann_whitney(groups[first], groups[second])
        raw[key] = computed[key]["p"]
    adjusted = holm(raw)
    for key, values in printed_pairs.items():
        close(computed[key]["u"], values["u"], f"Unit 13 {key} U", 5e-9)
        close(computed[key]["z"], values["z"], f"Unit 13 {key} z")
        close(computed[key]["rank_biserial"], values["rb"], f"Unit 13 {key} rank-biserial")
        close(computed[key]["p"], values["p"], f"Unit 13 {key} p", abs(values["p"]) * 1e-2 + 5e-6)
        close(adjusted[key], values["holm"], f"Unit 13 {key} Holm p", abs(values["holm"]) * 1e-2 + 5e-6)
    close(2 * 1694.0 / (44 * 44) - 1.0, 0.750, "Solution 13.12 hand calculation", 5e-4)
    close(39.573 / 131, 0.302, "Solution 13.11 jamovi hand calculation", 5e-4)
    close(
        (39.573 - 2) / 129,
        0.291,
        "Solution 13.11 bias-adjusted hand calculation",
        5e-4,
    )
    close(3999.5 / 44, 90.898, "Solution 13.10 hand calculation", 5e-4)

    # the parametric alternative quoted in the unit
    pooled = [v for key in APP_GROUPS for v in groups[key]]
    grand = average(pooled)
    ss_between = math.fsum(
        len(groups[key]) * (average(groups[key]) - grand) ** 2 for key in APP_GROUPS
    )
    ss_within = math.fsum(
        math.fsum((v - average(groups[key])) ** 2 for v in groups[key]) for key in APP_GROUPS
    )
    df_within = len(pooled) - 3
    f_statistic = (ss_between / 2) / (ss_within / df_within)
    check(df_within == 129, "Unit 13 residual degrees of freedom are not 129")
    close(f_statistic, 24.77, "Unit 13 parametric F", 5e-3)
    close(ss_between / (ss_between + ss_within), 0.278, "Unit 13 parametric eta-squared")

    spread = {
        key: [abs(v - median(groups[key])) for v in groups[key]] for key in APP_GROUPS
    }
    spread_pooled = [v for key in APP_GROUPS for v in spread[key]]
    spread_grand = average(spread_pooled)
    bf_between = math.fsum(
        len(spread[key]) * (average(spread[key]) - spread_grand) ** 2 for key in APP_GROUPS
    ) / 2
    bf_within = math.fsum(
        math.fsum((v - average(spread[key])) ** 2 for v in spread[key]) for key in APP_GROUPS
    ) / df_within
    close(bf_between / bf_within, 0.54, "Unit 13 Brown-Forsythe F", 5e-3)
    close(f_sf(bf_between / bf_within, 2, df_within), 0.583, "Unit 13 Brown-Forsythe p", 5e-4)

    # Study 09A: outlier-flagged rows deleted
    kept = [r for r in records if r["outlier_flag"] == "no"]
    check(len(kept) == 129, "Study 09A does not contain 129 rows")
    variant = {
        key: [float(r["wellbeing_score"]) for r in kept if r["app_use_group"] == key]
        for key in APP_GROUPS
    }
    check(
        [len(variant[key]) for key in APP_GROUPS] == [42, 43, 44],
        "Study 09A group sizes are not 42, 43 and 44",
    )
    close(average(variant["low"]), 57.629, "Study 09A low mean")
    close(sample_sd(variant["low"]), 7.755, "Study 09A low SD")
    variant_result = kruskal_wallis(variant, APP_GROUPS)
    close(variant_result["h"], 41.560, "Study 09A Kruskal-Wallis statistic")
    close(variant_result["epsilon_squared"], 0.325, "Study 09A jamovi epsilon-squared")
    close(
        variant_result["bias_adjusted_rank_effect_size"],
        0.314,
        "Study 09A bias-adjusted rank effect size",
    )
    check(
        variant_result["h"] > result["h"],
        "Study 09A statistic is not larger than the complete-file statistic",
    )
    check(
        variant_result["epsilon_squared"] > result["epsilon_squared"],
        "Study 09A effect size is not larger than the complete-file effect size",
    )
    check(
        variant_result["bias_adjusted_rank_effect_size"]
        > result["bias_adjusted_rank_effect_size"],
        "Study 09A bias-adjusted effect is not larger than the complete-file effect",
    )


# --------------------------------------------------------------------------
# Unit 14 - study_10_developmental_emotion_recognition
# --------------------------------------------------------------------------
AGE_BANDS = ["6_7", "8_9", "10_11"]


def audit_unit_14() -> None:
    records = rows("study_10_developmental_emotion_recognition")
    check(len(records) == 144, "study_10 row count is not 144")

    accuracy = {
        key: [float(r["emotion_accuracy"]) for r in records if r["age_group"] == key]
        for key in AGE_BANDS
    }
    vocabulary = {
        key: [float(r["vocabulary_score"]) for r in records if r["age_group"] == key]
        for key in AGE_BANDS
    }
    for key in AGE_BANDS:
        check(len(accuracy[key]) == 48, f"study_10 band {key} does not contain 48 rows")

    printed = {"6_7": (59.354, 6.308), "8_9": (69.300, 7.795), "10_11": (72.360, 7.363)}
    for key, (mean_value, sd_value) in printed.items():
        close(average(accuracy[key]), mean_value, f"Unit 14 {key} accuracy mean")
        close(sample_sd(accuracy[key]), sd_value, f"Unit 14 {key} accuracy SD")

    printed_vocabulary = {"6_7": 41.269, "8_9": 47.967, "10_11": 53.710}
    for key, mean_value in printed_vocabulary.items():
        close(average(vocabulary[key]), mean_value, f"Unit 14 {key} vocabulary mean")

    pooled = [v for key in AGE_BANDS for v in accuracy[key]]
    grand = average(pooled)
    ss_between = math.fsum(
        len(accuracy[key]) * (average(accuracy[key]) - grand) ** 2 for key in AGE_BANDS
    )
    ss_within = math.fsum(
        math.fsum((v - average(accuracy[key])) ** 2 for v in accuracy[key]) for key in AGE_BANDS
    )
    ss_total = ss_between + ss_within
    df_within = 141
    ms_between = ss_between / 2
    ms_within = ss_within / df_within
    f_statistic = ms_between / ms_within
    close(ss_between, 4439.173, "Unit 14 SS between", 5e-3)
    close(ss_within, 7274.354, "Unit 14 SS within", 5e-3)
    close(ss_total, 11713.527, "Unit 14 SS total", 5e-3)
    close(ms_between, 2219.586, "Unit 14 MS between", 5e-3)
    close(ms_within, 51.591, "Unit 14 MS within", 5e-3)
    close(f_statistic, 43.02, "Unit 14 F", 5e-3)
    close(ss_between / ss_total, 0.379, "Unit 14 eta-squared")
    close(
        (ss_between - 2 * ms_within) / (ss_total + ms_within),
        0.369,
        "Unit 14 omega-squared",
    )
    check(f_sf(f_statistic, 2, df_within) < 0.001, "Unit 14 omnibus p is not below .001")

    spread = {
        key: [abs(v - median(accuracy[key])) for v in accuracy[key]] for key in AGE_BANDS
    }
    spread_pooled = [v for key in AGE_BANDS for v in spread[key]]
    spread_grand = average(spread_pooled)
    bf = (
        math.fsum(
            len(spread[key]) * (average(spread[key]) - spread_grand) ** 2 for key in AGE_BANDS
        )
        / 2
    ) / (
        math.fsum(
            math.fsum((v - average(spread[key])) ** 2 for v in spread[key]) for key in AGE_BANDS
        )
        / df_within
    )
    close(bf, 0.77, "Unit 14 Brown-Forsythe F", 5e-3)
    close(f_sf(bf, 2, df_within), 0.467, "Unit 14 Brown-Forsythe p")

    pair_se = math.sqrt(ms_within * (1 / 48 + 1 / 48))
    close(pair_se, 1.466, "Solution 14.11 pairwise standard error")
    critical = student_t_ppf(1 - 0.05 / (2 * 3), df_within)
    printed_pairs = {
        ("6_7", "8_9"): (-9.946, -6.78, -13.498, -6.393, None),
        ("6_7", "10_11"): (-13.006, -8.87, -16.559, -9.454, None),
        ("8_9", "10_11"): (-3.060, -2.09, -6.613, 0.492, 0.116),
    }
    for (first, second), (difference, t_value, lower, upper, bonferroni) in printed_pairs.items():
        observed_difference = average(accuracy[first]) - average(accuracy[second])
        close(observed_difference, difference, f"Unit 14 {first} vs {second} mean difference")
        statistic = observed_difference / pair_se
        close(statistic, t_value, f"Unit 14 {first} vs {second} t", 5e-3)
        close(
            observed_difference - critical * pair_se,
            lower,
            f"Unit 14 {first} vs {second} lower family-wise bound",
        )
        close(
            observed_difference + critical * pair_se,
            upper,
            f"Unit 14 {first} vs {second} upper family-wise bound",
        )
        raw_p = 2 * (1 - student_t_cdf(abs(statistic), df_within))
        if bonferroni is None:
            check(
                min(1.0, 3 * raw_p) < 0.001,
                f"Unit 14 {first} vs {second} Bonferroni p is not below .001",
            )
        else:
            close(
                min(1.0, 3 * raw_p),
                bonferroni,
                f"Unit 14 {first} vs {second} Bonferroni p",
                5e-4,
            )
    raw_third = 2 * (
        1 - student_t_cdf(abs((average(accuracy["8_9"]) - average(accuracy["10_11"])) / pair_se), df_within)
    )
    close(raw_third, 0.039, "Unit 14 third contrast raw p", 5e-4)

    # covariate model
    design = []
    response = []
    for record in records:
        band = record["age_group"]
        design.append(
            [
                1.0,
                1.0 if band == "8_9" else 0.0,
                1.0 if band == "10_11" else 0.0,
                float(record["vocabulary_score"]),
            ]
        )
        response.append(float(record["emotion_accuracy"]))
    k = 4
    n = len(response)
    xtx = [[math.fsum(design[i][a] * design[i][b] for i in range(n)) for b in range(k)] for a in range(k)]
    xty = [math.fsum(design[i][a] * response[i] for i in range(n)) for a in range(k)]
    inverse = matrix_inverse(xtx)
    beta = [math.fsum(inverse[a][b] * xty[b] for b in range(k)) for a in range(k)]
    fitted = [math.fsum(design[i][a] * beta[a] for a in range(k)) for i in range(n)]
    sse = math.fsum((response[i] - fitted[i]) ** 2 for i in range(n))
    sst = math.fsum((y - average(response)) ** 2 for y in response)
    df_residual = n - k
    mse = sse / df_residual
    close(1 - sse / sst, 0.444, "Unit 14 covariate model R-squared")
    close(
        1 - (sse / df_residual) / (sst / (n - 1)),
        0.432,
        "Unit 14 covariate model adjusted R-squared",
    )
    close(mse, 46.540, "Unit 14 covariate model residual mean square", 5e-3)
    model_f = ((sst - sse) / (k - 1)) / mse
    close(model_f, 37.23, "Unit 14 covariate model F", 5e-3)
    check(df_residual == 140, "Unit 14 covariate model residual df is not 140")

    printed_coefficients = {
        0: (45.791, 3.500, 13.08, 38.871, 52.712, None),
        1: (7.745, 1.495, 5.18, 4.788, 10.701, 0.405),
        2: (8.917, 1.722, 5.18, 5.513, 12.321, 0.466),
        3: (0.329, 0.081, 4.04, 0.168, 0.490, 0.315),
    }
    t95 = student_t_ppf(0.975, df_residual)
    response_sd = sample_sd(response)
    for index, (b, se, t_value, lower, upper, standardized) in printed_coefficients.items():
        standard_error = math.sqrt(mse * inverse[index][index])
        close(beta[index], b, f"Unit 14 coefficient {index}")
        close(standard_error, se, f"Unit 14 standard error {index}", 5e-3)
        close(beta[index] / standard_error, t_value, f"Unit 14 t for coefficient {index}", 5e-3)
        close(beta[index] - t95 * standard_error, lower, f"Unit 14 lower bound {index}", 5e-3)
        close(beta[index] + t95 * standard_error, upper, f"Unit 14 upper bound {index}", 5e-3)
        if standardized is not None:
            column = [design[j][index] for j in range(n)]
            close(
                beta[index] * sample_sd(column) / response_sd,
                standardized,
                f"Unit 14 standardized coefficient {index}",
            )

    reduced = [[1.0, row[3]] for row in design]
    xtx_r = [[math.fsum(reduced[i][a] * reduced[i][b] for i in range(n)) for b in range(2)] for a in range(2)]
    xty_r = [math.fsum(reduced[i][a] * response[i] for i in range(n)) for a in range(2)]
    inverse_r = matrix_inverse(xtx_r)
    beta_r = [math.fsum(inverse_r[a][b] * xty_r[b] for b in range(2)) for a in range(2)]
    sse_r = math.fsum(
        (response[i] - math.fsum(reduced[i][a] * beta_r[a] for a in range(2))) ** 2 for i in range(n)
    )
    incremental = ((sse_r - sse) / 2) / mse
    close(incremental, 16.858, "Unit 14 incremental F", 5e-3)
    close((sse_r - sse) / sse_r, 0.194, "Unit 14 incremental partial eta-squared")

    # the vocabulary imbalance quoted in Solution 14.6
    vocabulary_pooled = [v for key in AGE_BANDS for v in vocabulary[key]]
    vocabulary_grand = average(vocabulary_pooled)
    v_between = math.fsum(
        len(vocabulary[key]) * (average(vocabulary[key]) - vocabulary_grand) ** 2
        for key in AGE_BANDS
    )
    v_within = math.fsum(
        math.fsum((v - average(vocabulary[key])) ** 2 for v in vocabulary[key])
        for key in AGE_BANDS
    )
    close((v_between / 2) / (v_within / df_within), 37.36, "Unit 14 vocabulary F", 5e-3)
    close(v_between / (v_between + v_within), 0.346, "Unit 14 vocabulary eta-squared")

    # Solution 14.12 arithmetic and Study 10A
    close(13.006 - 8.917, 4.089, "Solution 14.12 reduction", 5e-4)
    close(100 * (13.006 - 8.917) / 13.006, 31.4, "Solution 14.12 percentage", 5e-2)
    first, second = accuracy["6_7"], accuracy["10_11"]
    difference = average(second) - average(first)
    welch_se = math.sqrt(
        sample_variance(first) / len(first) + sample_variance(second) / len(second)
    )
    welch_df = (sample_variance(first) / len(first) + sample_variance(second) / len(second)) ** 2 / (
        (sample_variance(first) / len(first)) ** 2 / (len(first) - 1)
        + (sample_variance(second) / len(second)) ** 2 / (len(second) - 1)
    )
    close(difference, 13.006, "Study 10A mean difference")
    close(welch_se, 1.400, "Study 10A Welch standard error", 5e-3)
    close(difference / welch_se, 9.29, "Study 10A Welch t", 5e-3)
    close(welch_df, 91.84, "Study 10A Welch degrees of freedom", 5e-2)
    interval = student_t_ppf(0.975, welch_df) * welch_se
    close(difference - interval, 10.23, "Study 10A lower bound", 5e-3)
    close(difference + interval, 15.79, "Study 10A upper bound", 5e-3)
    pooled_sd = math.sqrt(
        ((len(first) - 1) * sample_variance(first) + (len(second) - 1) * sample_variance(second))
        / (len(first) + len(second) - 2)
    )
    correction = 1 - 3 / (4 * (len(first) + len(second) - 2) - 1)
    close(difference / pooled_sd * correction, 1.88, "Study 10A Hedges g", 5e-3)
    close(
        average(vocabulary["10_11"]) - average(vocabulary["6_7"]),
        12.44,
        "Study 10A vocabulary difference",
        5e-3,
    )

    # within-band correlations quoted in Problem 14.16
    def correlation(x: list[float], y: list[float]) -> float:
        mx, my = average(x), average(y)
        return math.fsum((a - mx) * (b - my) for a, b in zip(x, y, strict=True)) / math.sqrt(
            math.fsum((a - mx) ** 2 for a in x) * math.fsum((b - my) ** 2 for b in y)
        )

    for key, value in (("6_7", 0.221), ("8_9", 0.403), ("10_11", 0.322)):
        close(
            correlation(vocabulary[key], accuracy[key]),
            value,
            f"Problem 14.16 within-band correlation for {key}",
        )


# --------------------------------------------------------------------------
# Unit 15 - study_11_single_case_habit_tracking
# --------------------------------------------------------------------------
PHASES = ["baseline", "intervention", "maintenance"]


def audit_unit_15() -> None:
    records = rows("study_11_single_case_habit_tracking")
    check(len(records) == 42, "study_11 row count is not 42")

    def phase(outcome: str, name: str) -> list[float]:
        return [float(r[outcome]) for r in records if r["phase"] == name]

    def days(name: str) -> list[float]:
        return [float(r["case_day"]) for r in records if r["phase"] == name]

    for name in PHASES:
        check(len(phase("habit_count", name)) == 14, f"study_11 phase {name} is not 14 days")

    printed = {
        ("habit_count", "baseline"): dict(median=2.0, q1=2.0, q3=3.0, minimum=1, maximum=4, slope=-0.033, first=3, last=1, mean=2.357, sd=1.008),
        ("habit_count", "intervention"): dict(median=4.0, q1=4.0, q3=5.0, minimum=4, maximum=7, slope=0.068, first=5, last=6, mean=4.786, sd=1.122),
        ("habit_count", "maintenance"): dict(median=5.0, q1=5.0, q3=6.0, minimum=3, maximum=9, slope=-0.095, first=5, last=5, mean=5.500, sd=1.401),
        ("stress_rating", "baseline"): dict(median=6.5, q1=6.0, q3=7.0, minimum=6, maximum=8, slope=-0.062, first=7, last=6, mean=6.571, sd=0.646),
        ("stress_rating", "intervention"): dict(median=4.0, q1=3.0, q3=4.0, minimum=2, maximum=6, slope=-0.160, first=4, last=3, mean=3.786, sd=1.122),
        ("stress_rating", "maintenance"): dict(median=3.0, q1=2.0, q3=3.0, minimum=1, maximum=4, slope=0.077, first=2, last=3, mean=2.786, sd=0.893),
    }
    for (outcome, name), values in printed.items():
        series = phase(outcome, name)
        day_values = days(name)
        close(median(series), values["median"], f"Unit 15 {outcome} {name} median")
        close(quantile(series, 0.25), values["q1"], f"Unit 15 {outcome} {name} Q1")
        close(quantile(series, 0.75), values["q3"], f"Unit 15 {outcome} {name} Q3")
        close(min(series), values["minimum"], f"Unit 15 {outcome} {name} minimum")
        close(max(series), values["maximum"], f"Unit 15 {outcome} {name} maximum")
        close(series[0], values["first"], f"Unit 15 {outcome} {name} first observation")
        close(series[-1], values["last"], f"Unit 15 {outcome} {name} last observation")
        close(average(series), values["mean"], f"Unit 15 {outcome} {name} mean")
        close(sample_sd(series), values["sd"], f"Unit 15 {outcome} {name} SD")
        mx, my = average(day_values), average(series)
        slope = math.fsum(
            (a - mx) * (b - my) for a, b in zip(day_values, series, strict=True)
        ) / math.fsum((a - mx) ** 2 for a in day_values)
        close(slope, values["slope"], f"Unit 15 {outcome} {name} slope")

    frequencies = {
        "baseline": {6: 7, 7: 6, 8: 1},
        "intervention": {2: 2, 3: 3, 4: 6, 5: 2, 6: 1},
        "maintenance": {1: 1, 2: 4, 3: 6, 4: 3},
    }
    for name, table in frequencies.items():
        observed = Counter(int(v) for v in phase("stress_rating", name))
        check(
            dict(observed) == table,
            f"Unit 15 stress frequencies for {name} do not match the printed table",
        )

    close(
        average(phase("habit_count", "intervention")) - average(phase("habit_count", "baseline")),
        2.43,
        "Solution 15.9 habit level change",
        5e-3,
    )
    close(
        average(phase("stress_rating", "intervention")) - average(phase("stress_rating", "baseline")),
        -2.79,
        "Solution 15.9 stress level change",
        5e-3,
    )

    printed_nap = {
        ("habit_count", "intervention", True): 0.959,
        ("habit_count", "maintenance", True): 0.974,
        ("stress_rating", "intervention", False): 0.982,
        ("stress_rating", "maintenance", False): 1.000,
    }
    for (outcome, comparison, higher), value in printed_nap.items():
        close(
            nonoverlap(phase(outcome, "baseline"), phase(outcome, comparison), higher),
            value,
            f"Unit 15 NAP {outcome} baseline to {comparison}",
        )
    close(
        nonoverlap(phase("habit_count", "intervention"), phase("habit_count", "maintenance"), True),
        0.684,
        "Unit 15 NAP habit intervention to maintenance",
    )
    close(
        nonoverlap(phase("stress_rating", "intervention"), phase("stress_rating", "maintenance"), False),
        0.750,
        "Unit 15 NAP stress intervention to maintenance",
    )

    # the pair counts used in Solutions 15.10 and 15.11
    baseline_habit = phase("habit_count", "baseline")
    intervention_habit = phase("habit_count", "intervention")
    habit_ties = sum(1 for a in baseline_habit for b in intervention_habit if a == b)
    habit_better = sum(1 for a in baseline_habit for b in intervention_habit if b > a)
    habit_worse = sum(1 for a in baseline_habit for b in intervention_habit if b < a)
    check(habit_ties == 16, "Solution 15.10 tie count is not 16")
    check(habit_better == 180, "Solution 15.10 favourable-pair count is not 180")
    check(habit_worse == 0, "Solution 15.10 unfavourable-pair count is not 0")
    close((180 + 16 * 0.5) / 196, 0.959, "Solution 15.10 hand calculation")

    baseline_stress = phase("stress_rating", "baseline")
    intervention_stress = phase("stress_rating", "intervention")
    stress_ties = sum(1 for a in baseline_stress for b in intervention_stress if a == b)
    stress_better = sum(1 for a in baseline_stress for b in intervention_stress if b < a)
    stress_worse = sum(1 for a in baseline_stress for b in intervention_stress if b > a)
    check(stress_ties == 7, "Solution 15.11 tie count is not 7")
    check(stress_better == 189, "Solution 15.11 improvement-pair count is not 189")
    check(stress_worse == 0, "Solution 15.11 deterioration-pair count is not 0")
    close((189 + 7 * 0.5) / 196, 0.982, "Solution 15.11 hand calculation")
    check(
        max(baseline_habit) == min(intervention_habit) == 4.0,
        "Problem 15.5 contact point for the habit series is not 4",
    )
    check(
        min(baseline_stress) == 6.0 and max(intervention_stress) == 6.0,
        "Solution 15.14 contact point for the stress series is not 6",
    )
    check(
        min(baseline_stress) > max(phase("stress_rating", "maintenance")),
        "Solution 15.12 requires no overlap between baseline and maintenance stress",
    )

    # Study 11A: the between-groups test that should not have been run
    for outcome, expected_t, expected_d in (
        ("habit_count", 6.02, 2.28),
        ("stress_rating", -8.05, -3.04),
    ):
        first = phase(outcome, "baseline")
        second = phase(outcome, "intervention")
        pooled_sd = math.sqrt(
            ((len(first) - 1) * sample_variance(first) + (len(second) - 1) * sample_variance(second))
            / (len(first) + len(second) - 2)
        )
        standard_error = pooled_sd * math.sqrt(1 / len(first) + 1 / len(second))
        statistic = (average(second) - average(first)) / standard_error
        close(statistic, expected_t, f"Study 11A {outcome} t", 5e-3)
        close(
            (average(second) - average(first)) / pooled_sd,
            expected_d,
            f"Study 11A {outcome} standardized difference",
            5e-3,
        )
        check(
            2 * (1 - student_t_cdf(abs(statistic), 26)) < 0.001,
            f"Study 11A {outcome} p value is not below .001",
        )
    close(1.0664 * math.sqrt(2 / 14), 0.403, "Solution 15.8 approximate standard error", 5e-3)


# --------------------------------------------------------------------------
# document anchors
# --------------------------------------------------------------------------
def docx_text() -> str:
    if not DOCX.is_file():
        fail(f"Volume 2 DOCX is missing: {DOCX}")
    with zipfile.ZipFile(DOCX) as archive:
        document = ElementTree.fromstring(archive.read("word/document.xml"))
    text = " ".join(
        node.text for node in document.iter() if node.tag.endswith("}t") and node.text
    )
    return re.sub(r"\s+", " ", text)


def audit_document_anchors() -> None:
    text = docx_text()
    required = (
        "Psychology Statistics Practice Materials with Jamovi, Volume 2",
        "Categorical, Rank-Based, Quasi-Experimental, and Single-Case Evidence",
        "Problems and Worked Solutions - Version 1.0",
        "Nicholas Elliott Karlson",
        "Creative Commons Attribution 4.0 International",
        "https://github.com/nicholaskarlson/data",
        "synthetic",
        "Optional Books for Deeper Study",
        "Unit 12: Categorical Outcomes and Association",
        "Unit 13: Rank-Based Comparisons and Robust Thinking",
        "Unit 14: Quasi-Experimental Comparison and Covariate Adjustment",
        "Unit 15: Single-Case Designs and Nonoverlap",
        "study_08_help_seeking_categorical",
        "study_09_skewed_wellbeing_nonparametric",
        "study_10_developmental_emotion_recognition",
        "study_11_single_case_habit_tracking",
        # numeric anchors, one per unit
        "17.765",
        "0.243",
        "39.573",
        "0.302",
        "0.291",
        "43.02",
        "8.917",
        "0.959",
        "0.982",
    )
    for fragment in required:
        check(fragment in text, f"Volume 2 DOCX lacks required text: {fragment!r}")

    forbidden = (
        "Volume 3",
        "review edition",
        "not yet public",
        "private repository",
        "unpublished manuscript",
        "TODO",
        "PLACEHOLDER",
    )
    for fragment in forbidden:
        check(
            fragment.lower() not in text.lower(),
            f"Volume 2 DOCX contains private-development language: {fragment!r}",
        )

    problems = set(re.findall(r"Problem 1[2-5]\.(\d+)", text))
    solutions = set(re.findall(r"Solution 1[2-5]\.(\d+)", text))
    check(len(problems) == 24, "Volume 2 DOCX does not contain 24 problem numbers per unit")
    check(len(solutions) == 24, "Volume 2 DOCX does not contain 24 solution numbers per unit")
    for unit in ("12", "13", "14", "15"):
        found = re.findall(rf"Problem {unit}\.(\d+)", text)
        check(
            sorted({int(value) for value in found}) == list(range(1, 25)),
            f"Volume 2 DOCX unit {unit} does not contain problems 1 through 24",
        )
        found = re.findall(rf"Solution {unit}\.(\d+)", text)
        check(
            sorted({int(value) for value in found}) == list(range(1, 25)),
            f"Volume 2 DOCX unit {unit} does not contain solutions 1 through 24",
        )


def main() -> None:
    audit_unit_12()
    audit_unit_13()
    audit_unit_14()
    audit_unit_15()
    audit_document_anchors()
    print("NEKPRESS_VOLUME2_NUMERIC_AUDIT_OK")
    print(f"checks={CHECKS}")
    print("raw_csv_studies=4")
    print("teaching_variants=5")
    print("units=4")
    print("problems=96")
    print("worked_solutions=96")
    print(f"resource_version={VERSION}")
    print(f"volume={VOLUME}")


if __name__ == "__main__":
    main()
