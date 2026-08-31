#!/usr/bin/env python3
"""Fail closed unless the public reader-assets release is complete and exact."""

from __future__ import annotations

import csv
import json
import re
import struct
import sys
from pathlib import Path

from release_common import (
    CITATION_VERSION,
    FIGURES,
    PLATFORM_VALIDATION,
    PUBLIC_BASE_SHA,
    RELEASE_DATE,
    RELEASE_ID,
    ROOT,
    STUDIES,
    data_paths,
    figure_paths,
    payload_paths,
    result_paths,
    sha256,
)


MARKER = "NEKPRESS_JAMOVI_COMPANION_RELEASE_VERIFY_OK"
CANONICAL_URL = (
    "https://github.com/nicholaskarlson/"
    "nekpress-psychology-methods-statistics-jamovi-companion"
)
READER_URL = "https://github.com/nicholaskarlson/data"
SKIP_DIRS = {".git", ".venv", "__pycache__", "build", "dist"}
REQUIRED_PROJECT_PATHS = {
    ".github/DISCUSSION_TEMPLATE/ideas-and-teaching-feedback.yml",
    ".github/DISCUSSION_TEMPLATE/using-the-datasets.yml",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/ISSUE_TEMPLATE/data_question.yml",
    ".github/ISSUE_TEMPLATE/errata_report.yml",
    ".github/ISSUE_TEMPLATE/jamovi_output_mismatch.yml",
    ".github/workflows/verify.yml",
    ".gitattributes",
    ".gitignore",
    "ANALYSIS_MATRIX.md",
    "CHANGELOG.md",
    "CITATION.cff",
    "CODE_OF_CONDUCT.md",
    "COMMUNITY.md",
    "CONTRIBUTING.md",
    "ERRATA.md",
    "LICENSE",
    "Makefile",
    "QUICK_START.md",
    "README.md",
    "RELEASE_MANIFEST.json",
    "SECURITY.md",
    "SUPPORT.md",
    "data/README.md",
    "data/PROVENANCE.md",
    "data/SHA256SUMS",
    "expected-results/SHA256SUMS",
    "figures/README.md",
    "figures/SHA256SUMS",
    "releases/README.md",
    "scripts/build_release_bundle.py",
    "scripts/check_public_companion_release.py",
    "scripts/release_common.py",
    "scripts/update_release_metadata.py",
}

EXPECTED_DISCUSSION_FORMS = {
    "ideas-and-teaching-feedback.yml": {
        "feedback_area",
        "idea",
        "teaching_use",
        "current_material",
        "scope",
        "privacy",
    },
    "using-the-datasets.yml": {
        "topic",
        "file_name",
        "published_location",
        "question",
        "steps_tried",
        "scope",
        "privacy",
    },
}

EXPECTED_ISSUE_LABELS = {
    ".github/ISSUE_TEMPLATE/data_question.yml": "companion-files",
    ".github/ISSUE_TEMPLATE/errata_report.yml": "errata",
    ".github/ISSUE_TEMPLATE/jamovi_output_mismatch.yml": "jamovi-output",
}


def fail(message: str) -> None:
    print(f"PUBLIC_RELEASE_VERIFY_ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_hash_manifest(path: Path) -> dict[str, str]:
    records: dict[str, str] = {}
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        parts = raw.split("  ", 1)
        if len(parts) != 2 or len(parts[0]) != 64:
            fail(f"malformed checksum record at {path.relative_to(ROOT)}:{line_number}")
        digest, relative = parts
        if relative in records:
            fail(f"duplicate checksum path in {path.relative_to(ROOT)}: {relative}")
        records[relative] = digest
    return records


def verify_hash_manifest(path: Path, expected: tuple[str, ...]) -> None:
    records = parse_hash_manifest(path)
    if set(records) != set(expected):
        missing = sorted(set(expected) - set(records))
        extra = sorted(set(records) - set(expected))
        fail(f"checksum inventory mismatch in {path.relative_to(ROOT)}; missing={missing}, extra={extra}")
    for relative, expected_digest in records.items():
        target = ROOT / relative
        if not target.is_file():
            fail(f"checksum target is missing: {relative}")
        actual = sha256(target)
        if actual != expected_digest:
            fail(f"checksum mismatch for {relative}: expected {expected_digest}, got {actual}")


def png_metadata(path: Path) -> tuple[int, int, float | None]:
    data = path.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n") or len(data) < 33:
        fail(f"not a valid PNG: {path.relative_to(ROOT)}")
    width, height = struct.unpack(">II", data[16:24])
    offset = 8
    dpi = None
    while offset + 12 <= len(data):
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        kind = data[offset + 4 : offset + 8]
        chunk = data[offset + 8 : offset + 8 + length]
        if kind == b"pHYs" and length == 9:
            x_ppm, y_ppm, unit = struct.unpack(">IIB", chunk)
            if unit == 1 and x_ppm == y_ppm:
                dpi = x_ppm * 0.0254
        offset += 12 + length
        if kind == b"IEND":
            break
    return width, height, dpi


def form_fields(text: str) -> dict[str, tuple[str, str]]:
    """Return form fields keyed by id from the constrained GitHub form syntax."""
    fields: dict[str, tuple[str, str]] = {}
    chunks = re.split(r"(?m)^  - type:\s*", text)
    for chunk in chunks[1:]:
        field_type, separator, remainder = chunk.partition("\n")
        if not separator:
            fail("malformed GitHub form field")
        field_type = field_type.strip()
        if field_type == "markdown":
            continue
        match = re.search(r"(?m)^    id:\s*([a-z0-9_-]+)\s*$", remainder)
        if not match:
            fail(f"non-Markdown GitHub form field lacks an id: {field_type}")
        field_id = match.group(1)
        if field_id in fields:
            fail(f"duplicate GitHub form field id: {field_id}")
        fields[field_id] = (field_type, remainder)
    return fields


def verify_privacy_field(relative: str, text: str, fields: dict[str, tuple[str, str]]) -> None:
    privacy = fields.get("privacy")
    if privacy is None:
        fail(f"GitHub form lacks privacy field: {relative}")
    field_type, block = privacy
    if field_type != "checkboxes":
        fail(f"privacy field must use checkboxes: {relative}")
    for required in ("label: Privacy confirmation", "private", "required: true"):
        if required.lower() not in block.lower():
            fail(f"privacy field lacks {required!r}: {relative}")


def verify_discussion_form(relative: str, expected_ids: set[str]) -> None:
    text = (ROOT / relative).read_text(encoding="utf-8")
    if not re.search(r"(?m)^body:\s*$", text):
        fail(f"discussion form lacks top-level body: {relative}")
    fields = form_fields(text)
    if set(fields) != expected_ids:
        fail(
            f"discussion form field inventory differs in {relative}; "
            f"expected={sorted(expected_ids)}, actual={sorted(fields)}"
        )
    if not fields:
        fail(f"discussion form lacks a non-Markdown field: {relative}")
    verify_privacy_field(relative, text, fields)
    scope = fields.get("scope")
    if scope is None or scope[0] != "checkboxes" or "required: true" not in scope[1]:
        fail(f"discussion form lacks required scope confirmation: {relative}")


def verify_reader_support() -> None:
    discussion_dir = ROOT / ".github/DISCUSSION_TEMPLATE"
    actual_forms = {path.name for path in discussion_dir.glob("*.yml")}
    if actual_forms != set(EXPECTED_DISCUSSION_FORMS):
        fail(
            "discussion category form inventory differs; "
            f"expected={sorted(EXPECTED_DISCUSSION_FORMS)}, actual={sorted(actual_forms)}"
        )
    for name, expected_ids in EXPECTED_DISCUSSION_FORMS.items():
        verify_discussion_form(f".github/DISCUSSION_TEMPLATE/{name}", expected_ids)

    for relative, expected_label in EXPECTED_ISSUE_LABELS.items():
        text = (ROOT / relative).read_text(encoding="utf-8")
        fields = form_fields(text)
        verify_privacy_field(relative, text, fields)
        if not re.search(rf"(?m)^  - {re.escape(expected_label)}\s*$", text):
            fail(f"issue form does not declare label {expected_label!r}: {relative}")

    errata_relative = ".github/ISSUE_TEMPLATE/errata_report.yml"
    errata_text = (ROOT / errata_relative).read_text(encoding="utf-8")
    errata_fields = form_fields(errata_text)
    for required_id in ("format", "book_version", "location", "issue", "privacy"):
        if required_id not in errata_fields:
            fail(f"errata form lacks field {required_id!r}")
    for format_name in ("Paperback", "Kindle"):
        if format_name not in errata_fields["format"][1]:
            fail(f"errata form lacks format option {format_name!r}")
    location_block = errata_fields["location"][1].lower()
    for location_term in ("page", "kindle location", "chapter"):
        if location_term not in location_block:
            fail(f"errata location guidance lacks {location_term!r}")

    site_path = ROOT / "docs/index.html"
    if (ROOT / "docs/index.md").exists():
        fail("docs/index.md would compete with the established Pages source")
    site = site_path.read_text(encoding="utf-8")
    major_sections = {
        "start": "Start in three steps",
        "datasets": "The twelve datasets",
        "contents": "What is in the repository",
        "teaching": "Use it in your own teaching",
        "support": "Corrections and reader support",
        "about": "About",
    }
    for section_id, heading in major_sections.items():
        if f'id="{section_id}"' not in site or heading not in site:
            fail(f"Pages site is missing established section {section_id!r}")
    for established_marker in (
        "Twelve datasets. Every result already verified.",
        "Download everything (ZIP)",
        'class="steps"',
        'class="tablewrap"',
        'class="license"',
        'class="about"',
        "@media (prefers-color-scheme: dark)",
    ):
        if established_marker not in site:
            fail(f"Pages site lost established design/content marker: {established_marker}")
    for support_link in (
        "https://github.com/nicholaskarlson/data/blob/main/ERRATA.md",
        "https://github.com/nicholaskarlson/data/issues/new/choose",
        "https://github.com/nicholaskarlson/data/discussions",
        "https://github.com/nicholaskarlson/data/blob/main/COMMUNITY.md",
    ):
        if support_link not in site:
            fail(f"Pages support section lacks link: {support_link}")

    issue_config = (ROOT / ".github/ISSUE_TEMPLATE/config.yml").read_text(
        encoding="utf-8"
    )
    if "https://github.com/nicholaskarlson/data/blob/main/COMMUNITY.md" not in issue_config:
        fail("Issue chooser does not link to the bounded reader-support scope")

    community = (ROOT / "COMMUNITY.md").read_text(encoding="utf-8")
    community_lower = community.lower()
    for required_boundary in (
        "public synthetic",
        "published workflow",
        "homework",
        "private",
        "individualized model selection",
        "individualized statistical consulting",
        "do not post",
    ):
        if required_boundary not in community_lower:
            fail(f"COMMUNITY.md lacks support boundary: {required_boundary}")

    support_surfaces = [
        ROOT / "COMMUNITY.md",
        ROOT / "SUPPORT.md",
        ROOT / "docs/index.html",
        *(ROOT / ".github/ISSUE_TEMPLATE").glob("*.yml"),
        *discussion_dir.glob("*.yml"),
    ]
    support_text = "\n".join(
        path.read_text(encoding="utf-8") for path in support_surfaces
    ).lower()
    forbidden_phrases = (
        "course hub",
        "email us your data",
        "send us your data",
        "upload your private data",
        "share your private data",
        "post your private data",
        "individualized consulting is available",
        "we provide individualized statistical consulting",
        "contact us for individualized model selection",
        "ask us which model to use for your study",
    )
    for forbidden in forbidden_phrases:
        if forbidden in support_text:
            fail(f"forbidden reader-support promise or invitation remains: {forbidden}")


missing = sorted(path for path in REQUIRED_PROJECT_PATHS if not (ROOT / path).is_file())
if missing:
    fail("missing release project paths: " + ", ".join(missing))

verify_reader_support()

for path in ROOT.rglob("*"):
    relative = path.relative_to(ROOT)
    if any(part in SKIP_DIRS for part in relative.parts):
        continue
    if path.is_symlink():
        fail(f"symbolic links are not permitted: {relative.as_posix()}")
    if path.is_file() and path.stat().st_size > 25 * 1024 * 1024:
        fail(f"unexpected file larger than 25 MiB: {relative.as_posix()}")
    if path.is_file() and path.suffix.lower() in {".omv", ".sav", ".dta", ".sas7bdat"}:
        fail(f"prepared or proprietary data file is not permitted: {relative.as_posix()}")

actual_csv = {path.stem for path in (ROOT / "data").glob("study_*.csv")}
actual_dict = {
    path.name.removesuffix("_dictionary.json")
    for path in (ROOT / "data/dictionaries").glob("*.json")
}
actual_results = {
    path.name.removesuffix("_verified_results.json")
    for path in (ROOT / "expected-results").glob("*_verified_results.json")
}
if actual_csv != set(STUDIES):
    fail(f"CSV inventory mismatch: {sorted(actual_csv)}")
if actual_dict != set(STUDIES):
    fail(f"dictionary inventory mismatch: {sorted(actual_dict)}")
if actual_results != set(STUDIES):
    fail(f"verified-result inventory mismatch: {sorted(actual_results)}")

for study, (expected_rows, expected_columns) in STUDIES.items():
    csv_path = ROOT / f"data/{study}.csv"
    dictionary_path = ROOT / f"data/dictionaries/{study}_dictionary.json"
    result_path = ROOT / f"expected-results/{study}_verified_results.json"
    with csv_path.open("r", encoding="utf-8-sig", newline="") as source:
        rows = list(csv.reader(source))
    if not rows or len(rows) - 1 != expected_rows or len(rows[0]) != expected_columns:
        fail(
            f"shape mismatch for {study}: expected {expected_rows}x{expected_columns}, "
            f"got {max(len(rows) - 1, 0)}x{len(rows[0]) if rows else 0}"
        )
    if any(len(row) != expected_columns for row in rows):
        fail(f"ragged CSV rows in {study}")

    dictionary = json.loads(dictionary_path.read_text(encoding="utf-8"))
    if dictionary.get("dataset_id") != study:
        fail(f"dictionary dataset_id mismatch for {study}")
    if dictionary.get("csv_path") != f"data/{study}.csv":
        fail(f"dictionary csv_path mismatch for {study}")
    if dictionary.get("real_participant_data_allowed") is not False:
        fail(f"dictionary must prohibit real participant data for {study}")
    if "synthetic" not in str(dictionary.get("source", "")).lower():
        fail(f"dictionary source is not synthetic for {study}")
    variable_names = [item.get("name") for item in dictionary.get("variables", [])]
    if variable_names != rows[0]:
        fail(f"dictionary variable order differs from CSV header for {study}")

    results = json.loads(result_path.read_text(encoding="utf-8"))
    if results.get("dataset_id") != study or results.get("row_count") != expected_rows:
        fail(f"verified-result identity or row count mismatch for {study}")
    if results.get("dataset_sha256") != sha256(csv_path):
        fail(f"verified-result dataset hash mismatch for {study}")
    if results.get("dictionary_sha256") != sha256(dictionary_path):
        fail(f"verified-result dictionary hash mismatch for {study}")

matrix = (ROOT / "ANALYSIS_MATRIX.md").read_text(encoding="utf-8")
for study in STUDIES:
    if f"`{study}`" not in matrix:
        fail(f"analysis matrix does not contain {study}")

actual_figures = {path.name for path in (ROOT / "figures/generated").glob("*.png")}
if actual_figures != set(FIGURES):
    fail(f"essential-figure inventory mismatch: {sorted(actual_figures)}")
for name in FIGURES:
    width, height, dpi = png_metadata(ROOT / f"figures/generated/{name}")
    if width < 1500 or height < 900:
        fail(f"figure is below the print-size pixel floor: {name} ({width}x{height})")
    if dpi is None or not (295 <= dpi <= 305):
        fail(f"figure does not carry approximately 300 dpi metadata: {name} ({dpi})")

verify_hash_manifest(ROOT / "data/SHA256SUMS", data_paths())
verify_hash_manifest(ROOT / "expected-results/SHA256SUMS", result_paths())
verify_hash_manifest(ROOT / "figures/SHA256SUMS", figure_paths())

manifest = json.loads((ROOT / "RELEASE_MANIFEST.json").read_text(encoding="utf-8"))
fixed = {
    "schema_version": "1.0",
    "release_id": RELEASE_ID,
    "release_date": RELEASE_DATE,
    "public_repository_base_main_sha": PUBLIC_BASE_SHA,
}
for key, expected in fixed.items():
    if manifest.get(key) != expected:
        fail(f"release manifest field {key!r} must equal {expected!r}")
for internal_key in (
    "private_repository_source_main_sha",
    "private_lineage_preservation_tag",
):
    if internal_key in manifest:
        fail(f"internal production field leaked into public release metadata: {internal_key}")
if manifest.get("platform_validation") != PLATFORM_VALIDATION:
    fail(
        "release manifest platform validation must match the conservative "
        f"record: {PLATFORM_VALIDATION}"
    )
assets = manifest.get("assets", {})
expected_assets = {
    "dataset_count": 12,
    "dictionary_count": 12,
    "verified_result_count": 12,
    "essential_figure_count": 6,
    "prepared_session_file_count": 0,
}
if assets != expected_assets:
    fail(f"release manifest asset counts differ: {assets}")
records = manifest.get("files", [])
record_paths = [record.get("path") for record in records]
if record_paths != list(payload_paths()):
    fail("release manifest payload inventory or ordering differs")
for record in records:
    relative = record["path"]
    target = ROOT / relative
    if record.get("bytes") != target.stat().st_size or record.get("sha256") != sha256(target):
        fail(f"release manifest metadata differs for {relative}")

reader_text_paths = [
    ROOT / "README.md",
    ROOT / "QUICK_START.md",
    ROOT / "data/README.md",
    ROOT / "releases/README.md",
]
reader_text = "\n".join(path.read_text(encoding="utf-8") for path in reader_text_paths)
lowered = reader_text.lower()
for forbidden in (
    "public skeleton",
    "no datasets are published yet",
    "windows-only baseline",
    "a prepared session file is mandatory",
    "deterministic figures",
    "deterministic statistical figures",
    "ubuntu workflow has been exercised",
    "representative workflow exercised",
):
    if forbidden in lowered:
        fail(f"obsolete reader-facing phrase remains: {forbidden}")
for required in (
    "windows",
    "macos",
    "ubuntu",
    "release-candidate",
    "fresh csv",
    "private data",
    "clinical",
    "restricted",
    "completed on 22 august 2026",
    "representative validation",
    "complete application close",
    "file-browser reopen",
):
    if required not in lowered:
        fail(f"required scope or safety language is missing: {required}")
if CANONICAL_URL not in reader_text and CANONICAL_URL not in (ROOT / "CITATION.cff").read_text(encoding="utf-8"):
    fail("canonical repository URL is missing")
for reader_path in (ROOT / "README.md", ROOT / "QUICK_START.md"):
    if READER_URL not in reader_path.read_text(encoding="utf-8"):
        fail(f"reader download URL is missing from {reader_path.relative_to(ROOT)}")

citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
if f'version: "{CITATION_VERSION}"' not in citation:
    fail(f"CITATION.cff version must be {CITATION_VERSION}")

print(MARKER)
print(f"datasets={len(STUDIES)}")
print(f"dictionaries={len(STUDIES)}")
print(f"verified_results={len(STUDIES)}")
print(f"essential_figures={len(FIGURES)}")
print("prepared_session_files=0")
print("cross_platform_claim=QUALIFIED")
print("ubuntu_validation=PASSED")
print(f"discussion_category_forms={len(EXPECTED_DISCUSSION_FORMS)}")
print(f"confirmed_issue_form_labels={len(EXPECTED_ISSUE_LABELS)}")
print("reader_support_boundary=PASSED")
