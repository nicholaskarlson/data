#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path.cwd()
MARKER = "NEKPRESS_JAMOVI_COMPANION_SKELETON_CHECK_OK"
CANONICAL_URL = "https://github.com/nicholaskarlson/nekpress-psychology-methods-statistics-jamovi-companion"

REQUIRED_PATHS = [
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/ISSUE_TEMPLATE/data_question.yml",
    ".github/ISSUE_TEMPLATE/errata_report.yml",
    ".github/ISSUE_TEMPLATE/jamovi_output_mismatch.yml",
    ".github/workflows/verify.yml",
    ".gitattributes",
    ".gitignore",
    "CHANGELOG.md",
    "CITATION.cff",
    "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md",
    "ERRATA.md",
    "LICENSE",
    "Makefile",
    "README.md",
    "SECURITY.md",
    "SUPPORT.md",
    "data/README.md",
    "releases/README.md",
    "screenshots/README.md",
]

FORBIDDEN_EXTENSIONS = {".csv", ".omv", ".sav", ".dta", ".sas7bdat", ".xlsx", ".xls", ".png", ".jpg", ".jpeg"}
FORBIDDEN_TEXT = [
    "we will provide " + "homework answers",
    "we will complete " + "assignments",
    "private data " + "analysis service",
]
REQUIRED_PRIVACY_TOKENS = [
    "private data",
    "clinical",
    "restricted",
]
SKIP_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "build",
    "dist",
}


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


missing = [path for path in REQUIRED_PATHS if not (ROOT / path).is_file()]
if missing:
    fail("missing public companion skeleton paths: " + ", ".join(missing))

for path in ROOT.rglob("*"):
    if not path.is_file():
        continue
    relative_parts = path.relative_to(ROOT).parts
    if any(part in SKIP_DIRS for part in relative_parts):
        continue
    relative = path.relative_to(ROOT).as_posix()
    if path.suffix.lower() in FORBIDDEN_EXTENSIONS:
        fail(f"asset file is not allowed in the skeleton: {relative}")
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        fail(f"binary file is not allowed in the skeleton: {relative}")
    lowered = text.lower()
    for token in FORBIDDEN_TEXT:
        if token in lowered:
            fail(f"forbidden support promise found in {relative}: {token}")

readme = (ROOT / "README.md").read_text(encoding="utf-8")
if CANONICAL_URL not in readme and CANONICAL_URL not in (ROOT / "CITATION.cff").read_text(encoding="utf-8"):
    fail("canonical URL must appear in public skeleton README or citation metadata")
for token in REQUIRED_PRIVACY_TOKENS:
    if token not in readme.lower() and token not in (ROOT / "SUPPORT.md").read_text(encoding="utf-8").lower():
        fail(f"public skeleton missing privacy/support token: {token}")

for issue_template in [
    ".github/ISSUE_TEMPLATE/data_question.yml",
    ".github/ISSUE_TEMPLATE/errata_report.yml",
    ".github/ISSUE_TEMPLATE/jamovi_output_mismatch.yml",
]:
    text = (ROOT / issue_template).read_text(encoding="utf-8")
    if "Privacy confirmation" not in text:
        fail(f"issue template lacks privacy confirmation: {issue_template}")

print(MARKER)
