#!/usr/bin/env python3
"""Fail closed unless the public reader-assets release is complete and exact."""

from __future__ import annotations

import csv
import json
import struct
import sys
from pathlib import Path

from release_common import (
    FIGURES,
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
SKIP_DIRS = {".git", ".venv", "__pycache__", "build", "dist"}
REQUIRED_PROJECT_PATHS = {
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


missing = sorted(path for path in REQUIRED_PROJECT_PATHS if not (ROOT / path).is_file())
if missing:
    fail("missing release project paths: " + ", ".join(missing))

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
):
    if required not in lowered:
        fail(f"required scope or safety language is missing: {required}")
if CANONICAL_URL not in reader_text and CANONICAL_URL not in (ROOT / "CITATION.cff").read_text(encoding="utf-8"):
    fail("canonical repository URL is missing")

for issue_template in (
    ".github/ISSUE_TEMPLATE/data_question.yml",
    ".github/ISSUE_TEMPLATE/errata_report.yml",
    ".github/ISSUE_TEMPLATE/jamovi_output_mismatch.yml",
):
    if "Privacy confirmation" not in (ROOT / issue_template).read_text(encoding="utf-8"):
        fail(f"issue template lacks privacy confirmation: {issue_template}")

print(MARKER)
print(f"datasets={len(STUDIES)}")
print(f"dictionaries={len(STUDIES)}")
print(f"verified_results={len(STUDIES)}")
print(f"essential_figures={len(FIGURES)}")
print("prepared_session_files=0")
print("cross_platform_claim=QUALIFIED")
