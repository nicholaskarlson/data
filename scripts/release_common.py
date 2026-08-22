#!/usr/bin/env python3
"""Shared constants and helpers for the public reader-assets release."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RELEASE_ID = "reader-assets-v1.0.2"
RELEASE_DATE = "2026-08-22"
PUBLIC_BASE_SHA = "01b56f25cad425a037cb08c44d76c1a4c2393801"
CITATION_VERSION = "1.0.2"
PLATFORM_VALIDATION = {
    "ubuntu": (
        "passed - representative matrix and export/save/close/reopen "
        "completed 2026-08-22"
    ),
    "windows": "release-candidate instructions; representative validation pending",
    "macos": "release-candidate instructions; representative validation pending",
}

STUDIES = {
    "study_01_foundations_sleep_stress": (120, 5),
    "study_02_mindfulness_paired": (72, 4),
    "study_03_feedback_two_groups": (96, 4),
    "study_04_practice_spacing_anova": (120, 4),
    "study_05_sleep_strategy_factorial": (160, 4),
    "study_06_mood_repeated": (84, 5),
    "study_07_belonging_survey_regression": (180, 5),
    "study_08_help_seeking_categorical": (150, 4),
    "study_09_skewed_wellbeing_nonparametric": (132, 4),
    "study_10_developmental_emotion_recognition": (144, 4),
    "study_11_single_case_habit_tracking": (42, 4),
    "study_12_reporting_handoff_capstone": (60, 4),
}

FIGURES = (
    "fig08_resampling_means.png",
    "fig12_belonging_exam.png",
    "fig20_factorial_interaction.png",
    "fig21_mood_profile.png",
    "fig25_habit_series.png",
    "fig25_stress_series.png",
)

CORE_PAYLOAD = (
    "README.md",
    "QUICK_START.md",
    "ANALYSIS_MATRIX.md",
    "CITATION.cff",
    "LICENSE",
    "data/README.md",
    "data/PROVENANCE.md",
    "figures/README.md",
    "releases/README.md",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def data_paths() -> tuple[str, ...]:
    csvs = tuple(f"data/{study}.csv" for study in STUDIES)
    dictionaries = tuple(
        f"data/dictionaries/{study}_dictionary.json" for study in STUDIES
    )
    return ("data/PROVENANCE.md",) + csvs + dictionaries


def result_paths() -> tuple[str, ...]:
    return tuple(
        f"expected-results/{study}_verified_results.json" for study in STUDIES
    )


def figure_paths() -> tuple[str, ...]:
    return tuple(f"figures/generated/{name}" for name in FIGURES)


def payload_paths() -> tuple[str, ...]:
    return tuple(sorted(set(CORE_PAYLOAD + data_paths() + result_paths() + figure_paths())))
