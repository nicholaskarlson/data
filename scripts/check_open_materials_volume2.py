#!/usr/bin/env python3
"""Fail closed unless the CC BY 4.0 Volume 2 release is exact.

This is the Volume 2 counterpart to ``check_open_materials.py``.  It pins the
exact bytes of the two published files, verifies the DOCX package, requires the
public-release text and live hyperlinks, and requires the repository surfaces
that advertise the resource to mention it.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
RESOURCE_DIR = ROOT / "open-materials/psychology-statistics-practice-with-jamovi-volume-2"
DOCX_NAME = (
    "psychology-statistics-practice-materials-with-jamovi-volume-2-open-resource-v1.0.docx"
)
PDF_NAME = (
    "psychology-statistics-practice-materials-with-jamovi-volume-2-open-resource-v1.0.pdf"
)
EXPECTED = {
    DOCX_NAME: (
        113_714,
        "5a506776db2753b4a6080139f2e5ec8be4e98d4fa53787227ea085e83fc21925",
    ),
    PDF_NAME: (
        922_582,
        "2684cf61e0e014d06f04b12d54e2b61ac0250e589b650374a1a1d6032c20d549",
    ),
}
EXPECTED_MEMBERS = {
    "README.md",
    "SHA256SUMS",
    "zenodo-metadata.json",
    DOCX_NAME,
    PDF_NAME,
}
EXPECTED_SOURCE_MEMBERS = {
    "00_front.md",
    "12_unit.md",
    "13_unit.md",
    "14_unit.md",
    "15_unit.md",
    "99_back.md",
    "README.md",
    "build.sh",
    "meta.yaml",
    "meta_docx.yaml",
    "postprocess_docx.py",
    "prepare_markdown.py",
    "validate_publication.py",
}
REPOSITORY_URL = "https://github.com/nicholaskarlson/data"
DISCUSSIONS_URL = f"{REPOSITORY_URL}/discussions"
LICENSE_URL = "https://creativecommons.org/licenses/by/4.0/"

# Volume 1's version DOI is cited by Volume 2 and must remain reachable.
VOLUME_1_DOI = "10.5281/zenodo.22262048"
VOLUME_1_DOI_URL = f"https://doi.org/{VOLUME_1_DOI}"

VOLUME_2_DOI = "10.5281/zenodo.22286929"
VOLUME_2_DOI_URL = f"https://doi.org/{VOLUME_2_DOI}"

BOOK_LINKS = {
    "Psychology Research Methods and Statistics by Design with Jamovi": "https://www.amazon.com/dp/B0HG9VV1JR",
    "Psychological Statistics by Design": "https://www.amazon.com/dp/B0HCMCKR7X",
    "Applied Statistics with Python and R": "https://www.amazon.com/dp/B0H996LF88",
    "Before You Hire a Statistician": "https://www.amazon.com/dp/B0H661RV6B",
}


def fail(message: str) -> None:
    print(f"OPEN_MATERIALS_VOLUME2_VERIFY_ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


if not RESOURCE_DIR.is_dir():
    fail("Volume 2 resource directory is missing")

actual_members = {path.name for path in RESOURCE_DIR.iterdir() if path.is_file()}
if actual_members != EXPECTED_MEMBERS:
    fail(
        "Volume 2 resource inventory differs; "
        f"expected={sorted(EXPECTED_MEMBERS)}, actual={sorted(actual_members)}"
    )

source_dir = RESOURCE_DIR / "source"
actual_source_members = {path.name for path in source_dir.iterdir() if path.is_file()}
if actual_source_members != EXPECTED_SOURCE_MEMBERS:
    fail(
        "Volume 2 source inventory differs; "
        f"expected={sorted(EXPECTED_SOURCE_MEMBERS)}, actual={sorted(actual_source_members)}"
    )

for name, (expected_bytes, expected_hash) in EXPECTED.items():
    path = RESOURCE_DIR / name
    actual_bytes = path.stat().st_size
    if actual_bytes != expected_bytes:
        fail(f"size mismatch for {name}: expected {expected_bytes}, got {actual_bytes}")
    actual_hash = sha256(path)
    if actual_hash != expected_hash:
        fail(f"SHA-256 mismatch for {name}: expected {expected_hash}, got {actual_hash}")

checksum_lines = (RESOURCE_DIR / "SHA256SUMS").read_text(encoding="utf-8").splitlines()
expected_lines = [f"# Version DOI: {VOLUME_2_DOI}"] + [
    f"{digest}  {name}" for name, (_, digest) in EXPECTED.items()
]
if checksum_lines != expected_lines:
    fail("SHA256SUMS does not exactly identify the DOI and two published files")

docx_path = RESOURCE_DIR / DOCX_NAME
try:
    with zipfile.ZipFile(docx_path) as archive:
        if archive.testzip() is not None:
            fail("DOCX contains a corrupt ZIP member")
        required_docx_members = {
            "[Content_Types].xml",
            "word/document.xml",
            "word/settings.xml",
            "word/_rels/document.xml.rels",
            "docProps/core.xml",
        }
        if not required_docx_members.issubset(archive.namelist()):
            fail("DOCX lacks required package members")
        document_xml = archive.read("word/document.xml")
        settings_xml = archive.read("word/settings.xml")
        document_relationships = archive.read("word/_rels/document.xml.rels").decode("utf-8")
        core_properties = archive.read("docProps/core.xml").decode("utf-8")
except zipfile.BadZipFile as exc:
    fail(f"DOCX is not a valid ZIP package: {exc}")

try:
    settings_root = ElementTree.fromstring(settings_xml)
except ElementTree.ParseError as exc:
    fail(f"DOCX settings XML is invalid: {exc}")
if any(node.tag.endswith("}evenAndOddHeaders") for node in settings_root.iter()):
    fail("DOCX retains evenAndOddHeaders and can lose even-page furniture")

try:
    document_root = ElementTree.fromstring(document_xml)
except ElementTree.ParseError as exc:
    fail(f"DOCX document XML is invalid: {exc}")

docx_text = " ".join(
    node.text for node in document_root.iter() if node.tag.endswith("}t") and node.text
)
docx_text = re.sub(r"\s+", " ", docx_text)

required_text = [
    "Psychology Statistics Practice Materials with Jamovi, Volume 2",
    "Categorical, Rank-Based, Quasi-Experimental, and Single-Case Evidence",
    "Problems and Worked Solutions - Version 1.0",
    "Nicholas Elliott Karlson",
    "Creative Commons Attribution 4.0 International",
    REPOSITORY_URL,
    VOLUME_1_DOI_URL,
    "synthetic teaching data",
    "Optional Books for Deeper Study",
    "Unit 12: Categorical Outcomes and Association",
    "Unit 13: Rank-Based Comparisons and Robust Thinking",
    "Unit 14: Quasi-Experimental Comparison and Covariate Adjustment",
    "Unit 15: Single-Case Designs and Nonoverlap",
    # numeric anchors that would move if a dataset or a solution drifted
    "17.765",
    "0.243",
    "39.573",
    "0.302",
    "0.291",
    "0.325",
    "0.314",
    "43.02",
    "8.917",
    "0.959",
    "0.982",
    "About the Author",
    "About This Resource",
    VOLUME_2_DOI_URL,
    *BOOK_LINKS,
]

for required in required_text:
    if required not in docx_text:
        fail(f"DOCX lacks required public-release text: {required!r}")

for forbidden in (
    "Volume 3",
    "review edition",
    "not yet public",
    "private repository",
    "unpublished manuscript",
    "TODO",
    "PLACEHOLDER",
):
    if forbidden.lower() in docx_text.lower():
        fail(f"DOCX contains private-development language: {forbidden!r}")

for unit in ("12", "13", "14", "15"):
    problems = sorted({int(v) for v in re.findall(rf"Problem {unit}\.(\d+)", docx_text)})
    solutions = sorted({int(v) for v in re.findall(rf"Solution {unit}\.(\d+)", docx_text)})
    if problems != list(range(1, 25)):
        fail(f"DOCX unit {unit} does not contain problems 1 through 24")
    if solutions != list(range(1, 25)):
        fail(f"DOCX unit {unit} does not contain solutions 1 through 24")

required_links = [
    REPOSITORY_URL,
    DISCUSSIONS_URL,
    LICENSE_URL,
    VOLUME_1_DOI_URL,
    VOLUME_2_DOI_URL,
    *BOOK_LINKS.values(),
]

for required_link in required_links:
    if required_link not in document_relationships:
        fail(f"DOCX lacks required live hyperlink: {required_link}")

required_properties = [
    "Version 1.0",
    "Nicholas Elliott Karlson",
    "Categorical, Rank-Based, Quasi-Experimental, and Single-Case Evidence",
    "CC BY 4.0",
    VOLUME_2_DOI,
]

for required_property in required_properties:
    if required_property not in core_properties:
        fail(f"DOCX core properties lack release metadata: {required_property!r}")

pdf_bytes = (RESOURCE_DIR / PDF_NAME).read_bytes()
if not pdf_bytes.startswith(b"%PDF-") or b"%%EOF" not in pdf_bytes[-2048:]:
    fail("PDF does not have a valid header and final EOF marker")

resource_readme = (RESOURCE_DIR / "README.md").read_text(encoding="utf-8")
required_readme = [
    "4 units",
    "96 practice problems",
    "96 fully worked solutions",
    "Optional Books for Deeper Study",
    "Creative Commons Attribution 4.0 International License",
    LICENSE_URL,
    "Version 1.0",
    "make audit-volume2",
    REPOSITORY_URL,
    DISCUSSIONS_URL,
    DOCX_NAME,
    PDF_NAME,
    VOLUME_1_DOI,
    VOLUME_2_DOI,
    "source/",
    "zenodo-metadata.json",
    "study_08_help_seeking_categorical.csv",
    "study_09_skewed_wellbeing_nonparametric.csv",
    "study_10_developmental_emotion_recognition.csv",
    "study_11_single_case_habit_tracking.csv",
]

for required in required_readme:
    if required not in resource_readme:
        fail(f"Volume 2 README lacks required text or link: {required!r}")

source_requirements = {
    "00_front.md": (VOLUME_2_DOI, "Suggested attribution"),
    "13_unit.md": (
        "jamovi epsilon-squared",
        "bias-adjusted rank effect size",
        "0.302",
        "0.291",
        "0.325",
        "0.314",
    ),
    "99_back.md": ("About the Author", "About This Resource", VOLUME_2_DOI),
    "meta.yaml": (VOLUME_2_DOI, "3 September 2026"),
    "meta_docx.yaml": (VOLUME_2_DOI, "3 September 2026"),
    "build.sh": (VOLUME_2_DOI, "UseTaggedPDF", "pdffonts"),
    "postprocess_docx.py": ("evenAndOddHeaders",),
    "validate_publication.py": (
        VOLUME_2_DOI,
        "StructTreeRoot",
        "repeating header row",
        "physical page number",
    ),
}
for relative, markers in source_requirements.items():
    text = (source_dir / relative).read_text(encoding="utf-8")
    for marker in markers:
        if marker not in text:
            fail(f"source/{relative} lacks release marker: {marker!r}")

try:
    zenodo = json.loads((RESOURCE_DIR / "zenodo-metadata.json").read_text(encoding="utf-8"))
except (json.JSONDecodeError, OSError) as exc:
    fail(f"Zenodo metadata is unreadable: {exc}")
expected_zenodo = {
    "doi": VOLUME_2_DOI,
    "upload_type": "lesson",
    "version": "1.0",
    "license": "cc-by-4.0",
    "language": "eng",
    "publication_date": "2026-09-03",
    "imprint_publisher": "NEKpress Research",
}
for field, expected_value in expected_zenodo.items():
    if zenodo.get(field) != expected_value:
        fail(f"Zenodo metadata field {field!r} is not {expected_value!r}")
if zenodo.get("creators") != [{"name": "Karlson, Nicholas Elliott"}]:
    fail("Zenodo metadata creator is not exact")
description = zenodo.get("description", "")
for marker in ("four units", "96 practice problems", "96 fully worked solutions", "synthetic teaching data", "independently verified results"):
    if marker not in description:
        fail(f"Zenodo metadata description lacks {marker!r}")

surface_requirements = {
    "COMMUNITY.md": ("open educational resources", "Volume 2"),
    "SUPPORT.md": ("open practice-materials PDF or DOCX", "Volume 2"),
    "docs/index.html": (
        'id="practice-materials-volume-2"',
        "Four units, 96 problems, and 96 fully worked solutions",
        DOCX_NAME,
        PDF_NAME,
        VOLUME_2_DOI,
        "psychology-statistics-practice-with-jamovi-volume-2/source",
    ),
}
for relative, markers in surface_requirements.items():
    text = (ROOT / relative).read_text(encoding="utf-8")
    for marker in markers:
        if marker not in text:
            fail(f"{relative} lacks Volume 2 marker: {marker!r}")

print("NEKPRESS_OPEN_MATERIALS_VOLUME2_VERIFY_OK")
print("resource=psychology-statistics-practice-materials-with-jamovi-volume-2")
print("version=1.0")
print(f"version_doi={VOLUME_2_DOI}")
print("docx=1")
print("pdf=1")
print("license=CC-BY-4.0")
print("units=4")
print("problems=96")
print("worked_solutions=96")
