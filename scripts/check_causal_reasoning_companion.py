#!/usr/bin/env python3
"""Fail closed unless the Causal Reasoning with Statistics companion is intact.

The gate checks four things and nothing else:

1. the directory holds exactly the inventory recorded in ``SHA256SUMS``, with
   matching hashes;
2. the ten datasets, twelve verified records and three computation paths named
   in ``SOURCE.json`` are all present;
3. the anchor numbers printed in the book appear in the verified records, so a
   silent record change cannot pass;
4. the repository surfaces that advertise the resource mention it.

It does not run the analyses. ``make verify-causal`` does that.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESOURCE = ROOT / "open-materials/causal-reasoning-with-statistics"

REQUIRED_TOP_LEVEL = {
    "README.md", "LICENSE", "SOURCE.json", "SHA256SUMS", "requirements.txt",
    "run_all.py", "run_all.R",
}
REQUIRED_DATASETS = {
    "psychology_memory_training.csv",
    "unit1_library_interface_ab.csv",
    "unit2_multisite_workshop_offer.csv",
    "unit4_cluster_sleep_trial.csv",
    "unit5_hypertension_coaching.csv",
    "unit6_youth_crisis_policy.csv",
    "unit7_tutoring_cutoff.csv",
    "unit7_tutoring_encouragement.csv",
    "unit8_cognitive_training_trial.csv",
    "unit9_multisite_replication.csv",
}
# Numbers printed in the book, with the record and path that must carry them.
BOOK_ANCHORS = [
    ("unit1_library_interface_verified_results.json",
     ["estimates", "unadjusted_itt", "estimate"], 3.932705),
    ("unit5_hypertension_coaching_verified_results.json",
     ["known_simulation_sample_ate"], -4.226561),
    ("unit9_multisite_replication_verified_results.json",
     ["estimates", "sample_standardized_self_report", "risk_difference"], 0.1475),
    ("unit10_cross_case_synthesis_verified_results.json",
     ["hidden_calibration", "gamma_u_at_delta_0_5_to_reach_hidden_truth"], -3.830432),
    ("book_revision_addenda_verified_results.json",
     ["unit9_expected_misclassification", "expected_self_report_risk_difference"], 0.17883),
    ("book_revision_addenda_verified_results.json",
     ["unit10_structural_replay", "structural_delta_u"], 0.672803),
    ("book_revision_addenda_verified_results.json",
     ["unit10_structural_replay", "remaining_discrepancy"], -0.43505),
]
ADVERTISING_SURFACES = ["README.md", "Makefile"]
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
TOLERANCE = 1e-9


def fail(problems):
    for problem in problems:
        print("FAIL %s" % problem, file=sys.stderr)
    return 1


def read_manifest():
    entries = {}
    for line in (RESOURCE / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        digest, name = line.split(None, 1)
        entries[name.strip()] = digest
    return entries


def dig(record, path):
    for key in path:
        record = record[key]
    return record


def canonical_record_sha256(record):
    canonical = {key: value for key, value in record.items() if key != "primary_environment"}
    payload = json.dumps(canonical, indent=2, sort_keys=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def main():
    problems = []
    if not RESOURCE.is_dir():
        return fail(["%s is missing" % RESOURCE])

    manifest = read_manifest()
    present = {
        str(path.relative_to(RESOURCE)).replace("\\", "/")
        for path in RESOURCE.rglob("*")
        if path.is_file() and path.name != "SHA256SUMS"
        and "__pycache__" not in path.parts
    }
    for name in sorted(present - set(manifest)):
        problems.append("%s is present but not listed in SHA256SUMS" % name)
    for name in sorted(set(manifest) - present):
        problems.append("%s is listed in SHA256SUMS but missing" % name)
    for name in sorted(present & set(manifest)):
        digest = hashlib.sha256((RESOURCE / name).read_bytes()).hexdigest()
        if digest != manifest[name]:
            problems.append("%s does not match its recorded hash" % name)

    for name in sorted(REQUIRED_TOP_LEVEL):
        if not (RESOURCE / name).is_file():
            problems.append("%s is missing" % name)
    for name in sorted(REQUIRED_DATASETS):
        if not (RESOURCE / "data" / name).is_file():
            problems.append("data/%s is missing" % name)

    scripts = RESOURCE / "scripts"
    if len(list(scripts.glob("verify_*_independent.py"))) < 10:
        problems.append("the independent Python path is incomplete")
    if len(list(scripts.glob("verify_*_in_R.R"))) < 10:
        problems.append("the base-R path is incomplete")
    if len(list(scripts.glob("generate*.py"))) < 9:
        problems.append("the deterministic generators are incomplete")

    for filename, path, expected in BOOK_ANCHORS:
        target = RESOURCE / "expected-results" / filename
        if not target.is_file():
            problems.append("expected-results/%s is missing" % filename)
            continue
        try:
            value = dig(json.loads(target.read_text(encoding="utf-8")), path)
        except (KeyError, TypeError, ValueError):
            problems.append("%s does not contain %s" % (filename, "/".join(path)))
            continue
        if abs(float(value) - expected) > TOLERANCE:
            problems.append("%s %s is %s, the book prints %s"
                            % (filename, "/".join(path), value, expected))

    # provenance must name a real commit, not a placeholder
    try:
        source = json.loads((RESOURCE / "SOURCE.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        problems.append("SOURCE.json is missing or unreadable")
        source = {}
    for field, value in (
            ("exported_from.commit", source.get("exported_from", {}).get("commit", "")),
            ("authoring_commit_to_record_before_release",
             source.get("authoring_commit_to_record_before_release", ""))):
        if not COMMIT_PATTERN.match(str(value)):
            problems.append(
                "SOURCE.json %s is %r, which is not a 40-character commit hash. "
                "This companion is staged, not publishable: record the commit that merged "
                "the addendum scripts and records, refresh SHA256SUMS, and rerun this check."
                % (field, value))
    exported_commit = source.get("exported_from", {}).get("commit", "")
    recorded_commit = source.get("authoring_commit_to_record_before_release", "")
    if exported_commit != recorded_commit:
        problems.append(
            "SOURCE.json names different authoring commits in exported_from.commit and "
            "authoring_commit_to_record_before_release"
        )

    unit5_path = RESOURCE / "expected-results/unit5_hypertension_coaching_verified_results.json"
    unit10_path = RESOURCE / "expected-results/unit10_cross_case_synthesis_verified_results.json"
    try:
        unit5 = json.loads(unit5_path.read_text(encoding="utf-8"))
        unit10 = json.loads(unit10_path.read_text(encoding="utf-8"))
        canonical = canonical_record_sha256(unit5)
        if unit10.get("source_unit5_result_canonical_sha256") != canonical:
            problems.append("the Unit 10 canonical Unit 5 result hash does not match")
        if unit10.get("source_unit5_result_sha256") != hashlib.sha256(
                unit5_path.read_bytes()).hexdigest():
            problems.append("the Unit 10 raw Unit 5 result hash does not point at its file")
    except (OSError, ValueError):
        problems.append("the Unit 5 or Unit 10 verified record is unreadable")

    for surface in ADVERTISING_SURFACES:
        text = (ROOT / surface).read_text(encoding="utf-8")
        if "causal-reasoning-with-statistics" not in text:
            problems.append("%s does not mention the companion" % surface)

    if problems:
        return fail(problems)
    print("NEKPRESS_CAUSAL_REASONING_COMPANION_OK files=%d datasets=%d records=%d"
          % (len(manifest), len(REQUIRED_DATASETS),
             len(list((RESOURCE / "expected-results").glob("*.json")))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
