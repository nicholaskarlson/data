#!/usr/bin/env python3
"""Build the deterministic public reader-assets ZIP."""

from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path, PurePosixPath

from release_common import RELEASE_ID, ROOT, sha256


ARCHIVE_ROOT = f"nekpress-jamovi-companion-{RELEASE_ID}"
EXTRA_MEMBERS = (
    "RELEASE_MANIFEST.json",
    "data/SHA256SUMS",
    "expected-results/SHA256SUMS",
    "figures/SHA256SUMS",
)


def add_bytes(archive: zipfile.ZipFile, name: str, data: bytes) -> None:
    info = zipfile.ZipInfo(name, date_time=(2026, 9, 3, 0, 0, 0))
    info.compress_type = zipfile.ZIP_STORED
    info.create_system = 3
    info.external_attr = (0o100644 & 0xFFFF) << 16
    archive.writestr(info, data)


parser = argparse.ArgumentParser()
parser.add_argument(
    "--output",
    type=Path,
    default=ROOT / f"dist/nekpress-jamovi-companion-{RELEASE_ID}.zip",
)
args = parser.parse_args()

manifest = json.loads((ROOT / "RELEASE_MANIFEST.json").read_text(encoding="utf-8"))
members = sorted({record["path"] for record in manifest["files"]} | set(EXTRA_MEMBERS))
args.output.parent.mkdir(parents=True, exist_ok=True)

with zipfile.ZipFile(args.output, "w") as archive:
    for relative in members:
        source = ROOT / relative
        add_bytes(
            archive,
            str(PurePosixPath(ARCHIVE_ROOT) / PurePosixPath(relative)),
            source.read_bytes(),
        )

with zipfile.ZipFile(args.output) as archive:
    names = archive.namelist()
    expected = [str(PurePosixPath(ARCHIVE_ROOT) / PurePosixPath(path)) for path in members]
    if names != expected:
        raise SystemExit("Built release archive has an unexpected member inventory")
    if any(info.is_dir() or info.file_size > 25 * 1024 * 1024 for info in archive.infolist()):
        raise SystemExit("Built release archive contains an invalid member")

print(f"PUBLIC_RELEASE_BUNDLE_BUILT={args.output.resolve()}")
print(f"PUBLIC_RELEASE_BUNDLE_SHA256={sha256(args.output)}")
