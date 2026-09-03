#!/usr/bin/env python3
"""Combine the public Markdown source and emit native DOCX page breaks."""

from __future__ import annotations

import argparse
from pathlib import Path


SOURCE_FILES = (
    "00_front.md",
    "12_unit.md",
    "13_unit.md",
    "14_unit.md",
    "15_unit.md",
    "99_back.md",
)
PAGE_BREAK = (
    '```{=openxml}\n'
    '<w:p><w:r><w:br w:type="page"/></w:r></w:p>\n'
    '```'
)


parser = argparse.ArgumentParser()
parser.add_argument("--source-dir", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()

parts: list[str] = []
for filename in SOURCE_FILES:
    path = args.source_dir / filename
    if not path.is_file():
        raise SystemExit(f"SOURCE_ERROR: missing source file: {path}")
    parts.append(path.read_text(encoding="utf-8").rstrip())

combined = "\n\n".join(parts) + "\n"
if combined.count("# Psychology Statistics Practice Materials with Jamovi, Volume 2"):
    raise SystemExit("SOURCE_ERROR: duplicate manual title remains in body Markdown")
if "10.5281/zenodo.22286929" not in combined:
    raise SystemExit("SOURCE_ERROR: reserved DOI is missing from the body Markdown")

args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(combined.replace("\\newpage", PAGE_BREAK), encoding="utf-8")
