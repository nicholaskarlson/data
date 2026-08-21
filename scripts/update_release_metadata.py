#!/usr/bin/env python3
"""Regenerate release checksums after an intentional reader-asset change."""

from __future__ import annotations

import json
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


def write_hash_manifest(path: Path, members: tuple[str, ...]) -> None:
    lines = [f"{sha256(ROOT / member)}  {member}" for member in sorted(members)]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


for relative in payload_paths():
    if not (ROOT / relative).is_file():
        raise SystemExit(f"Missing release payload before metadata update: {relative}")

write_hash_manifest(ROOT / "data/SHA256SUMS", data_paths())
write_hash_manifest(ROOT / "expected-results/SHA256SUMS", result_paths())
write_hash_manifest(ROOT / "figures/SHA256SUMS", figure_paths())

manifest = {
    "schema_version": "1.0",
    "release_id": RELEASE_ID,
    "release_date": RELEASE_DATE,
    "public_repository_base_main_sha": PUBLIC_BASE_SHA,
    "assets": {
        "dataset_count": len(STUDIES),
        "dictionary_count": len(STUDIES),
        "verified_result_count": len(STUDIES),
        "essential_figure_count": len(FIGURES),
        "prepared_session_file_count": 0,
    },
    "platform_validation": {
        "ubuntu": "representative workflow exercised",
        "windows": "release-candidate instructions; representative validation pending",
        "macos": "release-candidate instructions; representative validation pending",
    },
    "files": [
        {
            "path": relative,
            "bytes": (ROOT / relative).stat().st_size,
            "sha256": sha256(ROOT / relative),
        }
        for relative in payload_paths()
    ],
}
(ROOT / "RELEASE_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

print("PUBLIC_RELEASE_METADATA_UPDATED")
