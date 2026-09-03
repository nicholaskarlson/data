#!/usr/bin/env python3
"""Fail closed on Volume 2 publication semantics and accessibility structure."""

from __future__ import annotations

import argparse
import re
import subprocess
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from pypdf import PdfReader


TITLE = "Psychology Statistics Practice Materials with Jamovi, Volume 2"
SUBTITLE = "Categorical, Rank-Based, Quasi-Experimental, and Single-Case Evidence"
DOI = "10.5281/zenodo.22286929"
DOI_URL = f"https://doi.org/{DOI}"
RUNNING_TITLE = TITLE
WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def fail(message: str) -> None:
    raise SystemExit(f"PUBLICATION_VALIDATE_ERROR: {message}")


def validate_docx(path: Path) -> None:
    try:
        with zipfile.ZipFile(path) as archive:
            if archive.testzip() is not None:
                fail("DOCX package is corrupt")
            document_xml = archive.read("word/document.xml")
            settings_xml = archive.read("word/settings.xml")
            relationships = archive.read("word/_rels/document.xml.rels").decode("utf-8")
            core = archive.read("docProps/core.xml").decode("utf-8")
            names = set(archive.namelist())
            footer_bytes = b"".join(
                archive.read(name)
                for name in archive.namelist()
                if name.startswith("word/footer") and name.endswith(".xml")
            )
    except (KeyError, zipfile.BadZipFile) as exc:
        fail(f"DOCX package error: {exc}")

    settings = ET.fromstring(settings_xml)
    if settings.find(f"{{{WORD_NS}}}evenAndOddHeaders") is not None:
        fail("DOCX retains evenAndOddHeaders and can lose even-page furniture")

    root = ET.fromstring(document_xml)
    paragraphs = root.findall(f".//{{{WORD_NS}}}body/{{{WORD_NS}}}p")
    cover_text: list[str] = []
    page_break_seen = False
    for paragraph in paragraphs:
        text = "".join(node.text or "" for node in paragraph.iter(f"{{{WORD_NS}}}t"))
        if not page_break_seen:
            cover_text.append(text)
        if any(
            br.get(f"{{{WORD_NS}}}type") == "page"
            for br in paragraph.iter(f"{{{WORD_NS}}}br")
        ):
            page_break_seen = True
    if not page_break_seen:
        fail("DOCX has no title-page break")
    if sum(text.strip() == TITLE for text in cover_text) != 1:
        fail("DOCX cover does not contain exactly one title")

    all_text = re.sub(
        r"\s+",
        " ",
        " ".join(node.text or "" for node in root.iter(f"{{{WORD_NS}}}t")),
    )
    for required in (
        TITLE,
        SUBTITLE,
        DOI,
        "0.302",
        "0.291",
        "0.325",
        "0.314",
        "About the Author",
        "About This Resource",
    ):
        if required not in all_text:
            fail(f"DOCX lacks required text: {required}")

    for required_link in (
        DOI_URL,
        "https://doi.org/10.5281/zenodo.22262048",
        "https://creativecommons.org/licenses/by/4.0/",
        "https://github.com/nicholaskarlson/data",
    ):
        if required_link not in relationships:
            fail(f"DOCX lacks live hyperlink: {required_link}")

    for required_property in (TITLE, DOI, "Nicholas Elliott Karlson", "CC BY 4.0"):
        if required_property not in core:
            fail(f"DOCX core properties lack: {required_property}")

    if not any(name.startswith("word/header") for name in names):
        fail("DOCX lacks a running-header part")
    if not any(name.startswith("word/footer") for name in names):
        fail("DOCX lacks a page-footer part")
    if b" PAGE " not in footer_bytes:
        fail("DOCX footer lacks a PAGE field")

    tables = root.findall(f".//{{{WORD_NS}}}tbl")
    for index, table in enumerate(tables, 1):
        first_row = table.find(f"{{{WORD_NS}}}tr")
        if first_row is None or first_row.find(
            f"{{{WORD_NS}}}trPr/{{{WORD_NS}}}tblHeader"
        ) is None:
            fail(f"DOCX table {index} lacks a repeating header row")


def validate_pdf(path: Path) -> None:
    reader = PdfReader(path)
    # A normal build is about 70 pages.  Keep a deliberately conservative
    # floor so accidental truncation fails without coupling the gate to line
    # wrapping or LibreOffice's harmless pagination differences.
    if len(reader.pages) < 65:
        fail(f"PDF page count is unexpectedly low: {len(reader.pages)}")
    root = reader.root_object
    if "/StructTreeRoot" not in root:
        fail("PDF lacks a structure tree")
    mark_info = root.get("/MarkInfo") or {}
    if not bool(mark_info.get("/Marked")):
        fail("PDF MarkInfo does not declare tagged content")
    if not root.get("/Lang"):
        fail("PDF lacks a document language")

    metadata = reader.metadata or {}
    metadata_text = " ".join(str(value) for value in metadata.values() if value)
    for required in (TITLE, "Nicholas Elliott Karlson", DOI, "CC BY 4.0"):
        if required not in metadata_text:
            fail(f"PDF metadata lacks: {required}")

    page_text = [page.extract_text() or "" for page in reader.pages]
    first_page = re.sub(r"\s+", " ", page_text[0])
    if first_page.count(TITLE) != 1:
        fail("PDF cover does not contain exactly one title")
    text = "\n".join(page_text)
    if ".X" in text:
        fail("PDF contains a LibreOffice missing-style marker after a link")
    for required in (TITLE, SUBTITLE, DOI, "Unit 12:", "Unit 15:", "About the Author"):
        if required not in text:
            fail(f"PDF text lacks: {required}")

    # pypdf intentionally omits page furniture from extracted page text, so
    # inspect Poppler's layout text for this pagination gate.
    try:
        result = subprocess.run(
            ["pdftotext", "-layout", str(path), "-"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        fail(f"could not inspect PDF page furniture: {exc}")
    rendered_pages = result.stdout.split("\f")
    if rendered_pages and not rendered_pages[-1].strip():
        rendered_pages.pop()
    if len(rendered_pages) != len(reader.pages):
        fail("pdftotext page count differs from the PDF page tree")

    # The physical cover is intentionally unnumbered.  Every subsequent page
    # must carry the running title and a footer equal to its physical page
    # number.  This catches the even-page regression inherited from the Volume
    # 1 reference DOCX as well as missing or stale page fields.
    for page_number, rendered in enumerate(rendered_pages[1:], start=2):
        if RUNNING_TITLE not in rendered:
            fail(f"PDF page {page_number} lacks the running title")
        nonempty_lines = [line.strip() for line in rendered.splitlines() if line.strip()]
        if not nonempty_lines or nonempty_lines[-1] != str(page_number):
            fail(f"PDF page {page_number} lacks its physical page number")

    links: set[str] = set()
    for page in reader.pages:
        for annotation_ref in page.get("/Annots", []):
            annotation = annotation_ref.get_object()
            action = annotation.get("/A")
            if action and action.get("/URI"):
                links.add(str(action["/URI"]))
    for required in (
        DOI_URL,
        "https://doi.org/10.5281/zenodo.22262048",
        "https://creativecommons.org/licenses/by/4.0/",
        "https://github.com/nicholaskarlson/data",
    ):
        if required not in links:
            fail(f"PDF lacks live link annotation: {required}")


parser = argparse.ArgumentParser()
parser.add_argument("docx", type=Path)
parser.add_argument("pdf", type=Path)
args = parser.parse_args()
validate_docx(args.docx)
validate_pdf(args.pdf)
print("VOLUME2_PUBLICATION_VALIDATE_OK")
