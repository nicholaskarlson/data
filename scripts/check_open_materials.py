#!/usr/bin/env python3
"""Fail closed unless the CC BY 4.0 practice-materials release is exact."""

from __future__ import annotations

import hashlib
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
RESOURCE_DIR = ROOT / "open-materials/psychology-statistics-practice-with-jamovi"
DOCX_NAME = "psychology-statistics-practice-materials-with-jamovi-open-resource-v1.1.docx"
PDF_NAME = "psychology-statistics-practice-materials-with-jamovi-open-resource-v1.1.pdf"
EXPECTED = {
    DOCX_NAME: (
        178_036,
        "8fee3c19f931437e7f98b646480c5684c55bb9ff9ca6ab6ae6db04a59b43287b",
    ),
    PDF_NAME: (
        1_590_798,
        "a4851c004fb543edb837c5d87b2dbe05820ffb2be4c8015c4bdc5bf9b1e46727",
    ),
}
EXPECTED_MEMBERS = {"README.md", "SHA256SUMS", DOCX_NAME, PDF_NAME}
REPOSITORY_URL = "https://github.com/nicholaskarlson/data"
DISCUSSIONS_URL = f"{REPOSITORY_URL}/discussions"
LICENSE_URL = "https://creativecommons.org/licenses/by/4.0/"
DOI = "10.5281/zenodo.22262048"
DOI_URL = f"https://doi.org/{DOI}"
BOOK_LINKS = {
    "Psychology Research Methods and Statistics by Design with Jamovi": "https://www.amazon.com/dp/B0HG9VV1JR",
    "Psychological Statistics by Design": "https://www.amazon.com/dp/B0HCMCKR7X",
    "Applied Statistics with Python and R": "https://www.amazon.com/dp/B0H996LF88",
    "Before You Hire a Statistician": "https://www.amazon.com/dp/B0H661RV6B",
}


def fail(message: str) -> None:
    print(f"OPEN_MATERIALS_VERIFY_ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


if not RESOURCE_DIR.is_dir():
    fail("resource directory is missing")

actual_members = {path.name for path in RESOURCE_DIR.iterdir() if path.is_file()}
if actual_members != EXPECTED_MEMBERS:
    fail(
        "resource inventory differs; "
        f"expected={sorted(EXPECTED_MEMBERS)}, actual={sorted(actual_members)}"
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
expected_lines = [f"{digest}  {name}" for name, (_, digest) in EXPECTED.items()]
if checksum_lines != expected_lines:
    fail("SHA256SUMS does not exactly describe the two published files")

docx_path = RESOURCE_DIR / DOCX_NAME
try:
    with zipfile.ZipFile(docx_path) as archive:
        if archive.testzip() is not None:
            fail("DOCX contains a corrupt ZIP member")
        required_docx_members = {
            "[Content_Types].xml",
            "word/document.xml",
            "word/_rels/document.xml.rels",
            "docProps/core.xml",
        }
        if not required_docx_members.issubset(archive.namelist()):
            fail("DOCX lacks required package members")
        document_xml = archive.read("word/document.xml")
        document_relationships = archive.read("word/_rels/document.xml.rels").decode(
            "utf-8"
        )
        core_properties = archive.read("docProps/core.xml").decode("utf-8")
except zipfile.BadZipFile as exc:
    fail(f"DOCX is not a valid ZIP package: {exc}")

try:
    document_root = ElementTree.fromstring(document_xml)
except ElementTree.ParseError as exc:
    fail(f"DOCX document XML is invalid: {exc}")

docx_text = " ".join(
    node.text for node in document_root.iter() if node.tag.endswith("}t") and node.text
)
docx_text = re.sub(r"\s+", " ", docx_text)
for required in (
    "Psychology Statistics Practice Materials with Jamovi",
    "Model Choice, Worked Solutions, and Scientific Evidence",
    "Problems and Worked Solutions - Version 1.1",
    "Nicholas Elliott Karlson",
    "Creative Commons Attribution 4.0 International",
    DOI_URL,
    REPOSITORY_URL,
    "synthetic teaching data",
    "Optional Books for Deeper Study",
    "replacing 71.4 with 714 increases it from 10.060 to 78.962",
    "-0.086 ± 1.997 × 0.107 gives [-0.300, 0.128]",
    "(3.357 / √2) × 1.781 = 4.227",
    *BOOK_LINKS,
):
    if required not in docx_text:
        fail(f"DOCX lacks required public-release text: {required!r}")

for forbidden in (
    "Book 5",
    "review edition",
    "not yet public",
    "private repository",
    "unpublished manuscript",
    "Problems and Worked Solutions - Version 1.0",
):
    if forbidden.lower() in docx_text.lower():
        fail(f"DOCX contains private-development language: {forbidden!r}")

for required_link in (
    REPOSITORY_URL,
    DISCUSSIONS_URL,
    LICENSE_URL,
    DOI_URL,
    *BOOK_LINKS.values(),
):
    if required_link not in document_relationships:
        fail(f"DOCX lacks required live hyperlink: {required_link}")

for required_property in (
    "Version 1.1",
    DOI,
    "Nicholas Elliott Karlson",
    "Model Choice, Worked Solutions, and Scientific Evidence",
):
    if required_property not in core_properties:
        fail(f"DOCX core properties lack release metadata: {required_property!r}")

pdf_bytes = (RESOURCE_DIR / PDF_NAME).read_bytes()
if not pdf_bytes.startswith(b"%PDF-") or b"%%EOF" not in pdf_bytes[-2048:]:
    fail("PDF does not have a valid header and final EOF marker")

resource_readme = (RESOURCE_DIR / "README.md").read_text(encoding="utf-8")
for required in (
    "11 units",
    "232 practice problems",
    "232 fully worked solutions",
    "Optional Books for Deeper Study",
    "Creative Commons Attribution 4.0 International License",
    LICENSE_URL,
    "Version 1.1",
    DOI_URL,
    "make audit",
    REPOSITORY_URL,
    DISCUSSIONS_URL,
    DOCX_NAME,
    PDF_NAME,
):
    if required not in resource_readme:
        fail(f"resource README lacks required text or link: {required!r}")

surface_requirements = {
    "COMMUNITY.md": ("open educational resources", "open practice materials"),
    "SUPPORT.md": ("open practice-materials PDF or DOCX",),
    "docs/index.html": (
        'id="practice-materials"',
        "Eleven units, 232 problems, and 232 fully worked solutions",
        DOCX_NAME,
        PDF_NAME,
    ),
}
for relative, markers in surface_requirements.items():
    text = (ROOT / relative).read_text(encoding="utf-8")
    for marker in markers:
        if marker not in text:
            fail(f"{relative} lacks open-materials marker: {marker!r}")

print("NEKPRESS_OPEN_MATERIALS_VERIFY_OK")
print("resource=psychology-statistics-practice-materials-with-jamovi")
print("version=1.1")
print(f"version_doi={DOI}")
print("docx=1")
print("pdf=1")
print("license=CC-BY-4.0")
print("problems=232")
print("worked_solutions=232")
