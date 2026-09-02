#!/usr/bin/env python3
"""Recompute the open resource's teaching results from its pinned CSV inputs.

This check intentionally uses only the Python standard library and the raw CSV
files.  It does not read the repository's expected-results JSON records, so it
provides an independent guard against document or dataset drift.
"""

from __future__ import annotations

import csv
import math
import re
import sys
import zipfile
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from statistics import median
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RESOURCE = ROOT / "open-materials/psychology-statistics-practice-with-jamovi"
DOCX = RESOURCE / "psychology-statistics-practice-materials-with-jamovi-open-resource-v1.1.docx"
DOI = "10.5281/zenodo.22262048"
CHECKS = 0


def fail(message: str) -> None:
    print(f"RESOURCE_NUMERIC_AUDIT_ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def check(condition: bool, label: str) -> None:
    global CHECKS
    CHECKS += 1
    if not condition:
        fail(label)


def close(actual: float, expected: float, label: str, tolerance: float = 5e-10) -> None:
    check(
        math.isclose(actual, expected, rel_tol=tolerance, abs_tol=tolerance),
        f"{label}: expected {expected:.15g}, got {actual:.15g}",
    )


def average(values: list[float]) -> float:
    return math.fsum(values) / len(values)


def sample_variance(values: list[float]) -> float:
    center = average(values)
    return math.fsum((value - center) ** 2 for value in values) / (len(values) - 1)


def sample_sd(values: list[float]) -> float:
    return math.sqrt(sample_variance(values))


def correlation(left: list[float], right: list[float]) -> float:
    left_mean = average(left)
    right_mean = average(right)
    cross = math.fsum(
        (x - left_mean) * (y - right_mean) for x, y in zip(left, right, strict=True)
    )
    left_ss = math.fsum((x - left_mean) ** 2 for x in left)
    right_ss = math.fsum((y - right_mean) ** 2 for y in right)
    return cross / math.sqrt(left_ss * right_ss)


def beta_continued_fraction(a: float, b: float, x: float) -> float:
    max_iterations = 300
    epsilon = 3e-14
    floor = 1e-300
    qab = a + b
    qap = a + 1.0
    qam = a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < floor:
        d = floor
    d = 1.0 / d
    result = d
    for iteration in range(1, max_iterations + 1):
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

        aa = -(a + iteration) * (qab + iteration) * x / (
            (a + even) * (qap + even)
        )
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
    if not 0.0 <= x <= 1.0:
        fail(f"regularized-beta argument outside [0,1]: {x}")
    if x in (0.0, 1.0):
        return x
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
    for _ in range(120):
        middle = (low + high) / 2.0
        if student_t_cdf(middle, df) < probability:
            low = middle
        else:
            high = middle
    return (low + high) / 2.0


def f_cdf(value: float, df1: float, df2: float) -> float:
    x = df1 * value / (df1 * value + df2)
    return regularized_beta(x, df1 / 2.0, df2 / 2.0)


def rows(name: str) -> list[dict[str, str]]:
    path = DATA / f"{name}.csv"
    with path.open(encoding="utf-8", newline="") as source:
        return list(csv.DictReader(source))


def values(records: list[dict[str, str]], column: str) -> list[float]:
    return [float(record[column]) for record in records if record[column] != ""]


def audit_study_02() -> None:
    records = rows("study_02_mindfulness_paired")
    pre = values(records, "mindfulness_pre")
    post = values(records, "mindfulness_post")
    differences = [after - before for before, after in zip(pre, post, strict=True)]

    check(len(records) == 72, "Study 02 row count")
    check(sum(record["practice_minutes"] == "" for record in records) == 4, "Study 02 missing practice count")
    close(average(pre), 43.293055555556, "Study 02 pre mean")
    close(sample_sd(pre), 8.931891372483, "Study 02 pre SD")
    close(average(post), 49.379166666667, "Study 02 post mean")
    close(sample_sd(post), 10.059988204568, "Study 02 post SD")
    close(median(post), 48.35, "Study 02 post median")
    close(average(differences), 6.086111111111, "Study 02 change mean")
    close(median(differences), 6.3, "Study 02 change median")
    close(sample_sd(differences), 4.992820353875, "Study 02 change SD")

    change_mean = average(differences)
    change_sd = sample_sd(differences)
    change_se = change_sd / math.sqrt(len(differences))
    paired_t = change_mean / change_se
    paired_critical = student_t_ppf(0.975, 71)
    close(change_se, 0.588409521579, "Study 02 paired SE")
    close(paired_t, 10.343325333661, "Study 02 paired t")
    close(paired_critical, 1.993943367846, "Study 02 paired critical t")
    close(change_mean - paired_critical * change_se, 4.912855847982, "Study 02 paired CI lower")
    close(change_mean + paired_critical * change_se, 7.259366374240, "Study 02 paired CI upper")
    close(change_mean / change_sd, 1.218972580575, "Study 02 Cohen dz")
    close(correlation(pre, post), 0.868367225806, "Study 02 pre-post correlation")

    corrupted = post.copy()
    maximum_index = corrupted.index(max(corrupted))
    check(corrupted[maximum_index] == 71.4, "Study 02 corruption source maximum")
    original_median = median(corrupted)
    original_middle = sorted(corrupted)[18:54]
    corrupted[maximum_index] = 714.0
    close(average(corrupted), 58.304166666667, "Study 02 corrupted mean")
    close(sample_sd(corrupted), 78.962120420285, "Study 02 corrupted SD")
    close(median(corrupted), original_median, "Study 02 corrupted median unchanged")
    check(sorted(corrupted)[18:54] == original_middle, "Study 02 middle ranks unchanged")

    complete = [
        (
            float(record["practice_minutes"]),
            float(record["mindfulness_post"]) - float(record["mindfulness_pre"]),
        )
        for record in records
        if record["practice_minutes"] != ""
    ]
    x_values = [pair[0] for pair in complete]
    y_values = [pair[1] for pair in complete]
    x_mean = average(x_values)
    y_mean = average(y_values)
    sxx = math.fsum((x - x_mean) ** 2 for x in x_values)
    sxy = math.fsum(
        (x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values, strict=True)
    )
    slope = sxy / sxx
    intercept = y_mean - slope * x_mean
    residuals = [
        y - (intercept + slope * x)
        for x, y in zip(x_values, y_values, strict=True)
    ]
    error_ss = math.fsum(residual * residual for residual in residuals)
    total_ss = math.fsum((y - y_mean) ** 2 for y in y_values)
    slope_se = math.sqrt((error_ss / 66) / sxx)
    slope_t = slope / slope_se
    regression_critical = student_t_ppf(0.975, 66)
    close(slope, -0.085853369686, "Study 02 regression slope")
    close(slope_se, 0.107395468458, "Study 02 regression slope SE")
    close(slope_t, -0.799413335764, "Study 02 regression slope t")
    close(correlation(x_values, y_values), -0.097928015170, "Study 02 regression r")
    close(1.0 - error_ss / total_ss, 0.009589896155, "Study 02 regression R squared")
    close(regression_critical, 1.996564418953, "Study 02 regression critical t")
    close(slope - regression_critical * slope_se, -0.300275340767, "Study 02 slope CI lower")
    close(slope + regression_critical * slope_se, 0.128568601394, "Study 02 slope CI upper")


def audit_study_03() -> None:
    records = rows("study_03_feedback_two_groups")
    grouped = {
        condition: [
            float(record["motivation_score"])
            for record in records
            if record["feedback_condition"] == condition
        ]
        for condition in ("process_feedback", "outcome_feedback")
    }
    process = grouped["process_feedback"]
    outcome = grouped["outcome_feedback"]
    check(len(records) == 96, "Study 03 row count")
    check(len(process) == len(outcome) == 48, "Study 03 group counts")
    close(average(process), 69.341666666667, "Study 03 process mean")
    close(sample_sd(process), 7.802422791572, "Study 03 process SD")
    close(average(outcome), 63.952083333333, "Study 03 outcome mean")
    close(sample_sd(outcome), 7.837036716996, "Study 03 outcome SD")

    n1, n2 = len(process), len(outcome)
    variance1, variance2 = sample_variance(process), sample_variance(outcome)
    difference = average(process) - average(outcome)
    pooled_variance = ((n1 - 1) * variance1 + (n2 - 1) * variance2) / (n1 + n2 - 2)
    pooled_se = math.sqrt(pooled_variance * (1.0 / n1 + 1.0 / n2))
    student_t = difference / pooled_se
    critical = student_t_ppf(0.975, 94)
    close(difference, 5.389583333333, "Study 03 mean difference")
    close(pooled_se, 1.596199561471, "Study 03 pooled SE")
    close(student_t, 3.376509719352, "Study 03 Student t")
    close(2.0 * (1.0 - student_t_cdf(abs(student_t), 94)), 0.001068943999, "Study 03 Student p")
    close(difference - critical * pooled_se, 2.220291686135, "Study 03 Student CI lower")
    close(difference + critical * pooled_se, 8.558874980532, "Study 03 Student CI upper")
    cohen_d = difference / math.sqrt(pooled_variance)
    correction = 1.0 - 3.0 / (4.0 * 94.0 - 1.0)
    close(cohen_d, 0.689227160330, "Study 03 Cohen d")
    close(cohen_d * correction, 0.683713343047, "Study 03 Hedges g")

    welch_se = math.sqrt(variance1 / n1 + variance2 / n2)
    welch_df = (variance1 / n1 + variance2 / n2) ** 2 / (
        (variance1 / n1) ** 2 / (n1 - 1) + (variance2 / n2) ** 2 / (n2 - 1)
    )
    close(welch_se, 1.596199561471, "Study 03 Welch SE")
    close(welch_df, 93.998158238848, "Study 03 Welch df")


def audit_study_04() -> None:
    records = rows("study_04_practice_spacing_anova")
    order = ("massed", "spaced", "interleaved")
    grouped = {
        condition: [
            float(record["retention_score"])
            for record in records
            if record["spacing_condition"] == condition
        ]
        for condition in order
    }
    check(len(records) == 120, "Study 04 row count")
    check(all(len(grouped[key]) == 40 for key in order), "Study 04 group counts")
    expected_means = {"massed": 63.3875, "spaced": 72.3775, "interleaved": 78.32}
    expected_sds = {
        "massed": 8.100591542186,
        "spaced": 7.050604174875,
        "interleaved": 8.655788044232,
    }
    for condition in order:
        close(average(grouped[condition]), expected_means[condition], f"Study 04 {condition} mean")
        close(sample_sd(grouped[condition]), expected_sds[condition], f"Study 04 {condition} SD")

    spaced_decimal = sum(
        Decimal(record["retention_score"])
        for record in records
        if record["spacing_condition"] == "spaced"
    ) / Decimal(40)
    check(
        spaced_decimal.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP) == Decimal("72.378"),
        "Study 04 spaced mean half-up display",
    )

    all_scores = [score for condition in order for score in grouped[condition]]
    grand_mean = average(all_scores)
    ss_between = math.fsum(
        len(grouped[condition]) * (average(grouped[condition]) - grand_mean) ** 2
        for condition in order
    )
    ss_within = math.fsum(
        math.fsum((score - average(grouped[condition])) ** 2 for score in grouped[condition])
        for condition in order
    )
    ss_total = math.fsum((score - grand_mean) ** 2 for score in all_scores)
    ms_between = ss_between / 2
    ms_within = ss_within / 117
    f_value = ms_between / ms_within
    close(ss_between, 4521.506166666662, "Study 04 SS between")
    close(ss_within, 7419.8775, "Study 04 SS within")
    close(ss_total, 11941.383666666667, "Study 04 SS total")
    close(ms_between, 2260.753083333331, "Study 04 MS between")
    close(ms_within, 63.417756410256, "Study 04 MS within")
    close(f_value, 35.648581900442, "Study 04 F")
    close(1.0 - f_cdf(f_value, 2, 117), 8.137890951305159e-13, "Study 04 F p", tolerance=2e-12)
    close(ss_between / ss_total, 0.378641729709, "Study 04 eta squared")
    close((ss_between - 2 * ms_within) / (ss_total + ms_within), 0.366076080642, "Study 04 omega squared")

    pairwise_se = math.sqrt(ms_within * (1.0 / 40 + 1.0 / 40))
    close(pairwise_se, 1.780698688861, "Study 04 pairwise SE")
    differences = {
        "massed-spaced": expected_means["massed"] - expected_means["spaced"],
        "massed-interleaved": expected_means["massed"] - expected_means["interleaved"],
        "spaced-interleaved": expected_means["spaced"] - expected_means["interleaved"],
    }
    expected_t = {
        "massed-spaced": -5.048580119834,
        "massed-interleaved": -8.385753352549,
        "spaced-interleaved": -3.337173232716,
    }
    for label, difference in differences.items():
        close(difference / pairwise_se, expected_t[label], f"Study 04 {label} t")

    q_rounded = 3.357
    half_width = (q_rounded / math.sqrt(2.0)) * pairwise_se
    single_mean_se = math.sqrt(ms_within / 40.0)
    close(single_mean_se, 1.259144118144, "Study 04 single-mean SE")
    close(half_width, 4.226946804608, "Study 04 Tukey half-width")
    close(q_rounded * single_mean_se, half_width, "Study 04 equivalent Tukey scales")
    rounded_intervals = {
        label: (round(difference - half_width, 3), round(difference + half_width, 3))
        for label, difference in differences.items()
    }
    check(rounded_intervals["massed-spaced"] == (-13.217, -4.763), "Study 04 Tukey interval 1")
    check(rounded_intervals["massed-interleaved"] == (-19.159, -10.706), "Study 04 Tukey interval 2 from rounded q")
    check(rounded_intervals["spaced-interleaved"] == (-10.169, -1.716), "Study 04 Tukey interval 3 from rounded q")
    published_intervals = {
        "massed-spaced": (-13.217, -4.763),
        "massed-interleaved": (-19.160, -10.705),
        "spaced-interleaved": (-10.170, -1.715),
    }
    for label, published in published_intervals.items():
        calculated = rounded_intervals[label]
        check(
            all(abs(left - right) <= 0.0011 for left, right in zip(published, calculated, strict=True)),
            f"Study 04 {label} published Tukey interval agrees within displayed-q rounding",
        )

    contrast = 0.5 * expected_means["spaced"] + 0.5 * expected_means["interleaved"] - expected_means["massed"]
    contrast_se = math.sqrt(ms_within * (0.25 / 40 + 0.25 / 40 + 1.0 / 40))
    critical = student_t_ppf(0.975, 117)
    close(contrast, 11.96125, "Study 04 planned contrast")
    close(contrast_se, 1.542130301040, "Study 04 contrast SE")
    close(contrast / contrast_se, 7.756316046664, "Study 04 contrast t")
    close(contrast - critical * contrast_se, 8.907141748449, "Study 04 contrast CI lower")
    close(contrast + critical * contrast_se, 15.015358251551, "Study 04 contrast CI upper")


def audit_summary_variants() -> None:
    n = 72
    mean_difference = 0.400
    sd_difference = 5.198
    se = sd_difference / math.sqrt(n)
    t_value = mean_difference / se
    critical = student_t_ppf(0.975, n - 1)
    close(se, 0.612590174768, "Study 02C SE")
    close(t_value, 0.652965092285, "Study 02C t")
    close(2.0 * (1.0 - student_t_cdf(t_value, n - 1)), 0.515887629686, "Study 02C p")
    close(mean_difference - critical * se, -0.821470116186, "Study 02C CI lower")
    close(mean_difference + critical * se, 1.621470116186, "Study 02C CI upper")
    close(mean_difference / sd_difference, 0.076952674106, "Study 02C Cohen dz")

    n1, n2 = 28, 68
    sd1, sd2 = 12.001, 4.992
    difference = 4.0
    welch_se = math.sqrt(sd1 * sd1 / n1 + sd2 * sd2 / n2)
    welch_t = difference / welch_se
    welch_df = (sd1 * sd1 / n1 + sd2 * sd2 / n2) ** 2 / (
        (sd1 * sd1 / n1) ** 2 / (n1 - 1) + (sd2 * sd2 / n2) ** 2 / (n2 - 1)
    )
    welch_critical = student_t_ppf(0.975, welch_df)
    close(welch_se, 2.347378506087, "Study 03A Welch SE")
    close(welch_t, 1.704028553396, "Study 03A Welch t")
    close(welch_df, 30.921111945584, "Study 03A Welch df")
    close(2.0 * (1.0 - student_t_cdf(welch_t, welch_df)), 0.098406802757, "Study 03A Welch p")
    close(difference - welch_critical * welch_se, -0.788005129630, "Study 03A Welch CI lower")
    close(difference + welch_critical * welch_se, 8.788005129630, "Study 03A Welch CI upper")

    pooled_variance = ((n1 - 1) * sd1 * sd1 + (n2 - 1) * sd2 * sd2) / (n1 + n2 - 2)
    pooled_se = math.sqrt(pooled_variance * (1.0 / n1 + 1.0 / n2))
    student_t = difference / pooled_se
    student_critical = student_t_ppf(0.975, n1 + n2 - 2)
    close(pooled_se, 1.726668273433, "Study 03A Student SE")
    close(student_t, 2.316600160868, "Study 03A Student t")
    close(2.0 * (1.0 - student_t_cdf(student_t, 94)), 0.022697950320, "Study 03A Student p")
    close(difference - student_critical * pooled_se, 0.571659666772, "Study 03A Student CI lower")
    close(difference + student_critical * pooled_se, 7.428340333228, "Study 03A Student CI upper")


def docx_text() -> str:
    try:
        with zipfile.ZipFile(DOCX) as archive:
            document_xml = archive.read("word/document.xml")
    except (FileNotFoundError, KeyError, zipfile.BadZipFile) as exc:
        fail(f"cannot read v1.1 DOCX: {exc}")
    try:
        root = ElementTree.fromstring(document_xml)
    except ElementTree.ParseError as exc:
        fail(f"invalid DOCX document XML: {exc}")
    text = " ".join(
        node.text for node in root.iter() if node.tag.endswith("}t") and node.text
    )
    return re.sub(r"\s+", " ", text)


def audit_document_anchors() -> None:
    text = docx_text()
    required = (
        "Problems and Worked Solutions - Version 1.1",
        f"Version DOI: https://doi.org/{DOI}",
        "replacing 71.4 with 714 increases it from 10.060 to 78.962",
        "raises the 72-case mean from 49.379 to 58.304, an increase of 8.925",
        "The median does not move at all",
        "-0.086 ± 1.997 × 0.107 gives [-0.300, 0.128]",
        "unrounded values give [-0.300, 0.129]",
        "(3.357 / √2) × 1.781 = 4.227",
        "√(63.418 / 40) = 1.259",
        "Statistical estimates and conclusions are unchanged",
    )
    for fragment in required:
        check(fragment in text, f"DOCX missing audited text: {fragment!r}")
    forbidden = (
        "The mean moves most",
        "Each interval used the pooled standard error of 1.781",
        "Problems and Worked Solutions - Version 1.0",
    )
    for fragment in forbidden:
        check(fragment not in text, f"DOCX retains superseded text: {fragment!r}")


def main() -> None:
    audit_study_02()
    audit_study_03()
    audit_study_04()
    audit_summary_variants()
    audit_document_anchors()
    print("NEKPRESS_RESOURCE_NUMERIC_AUDIT_OK")
    print(f"checks={CHECKS}")
    print("raw_csv_studies=3")
    print("summary_variants=2")
    print("resource_version=1.1")
    print(f"version_doi={DOI}")


if __name__ == "__main__":
    main()
