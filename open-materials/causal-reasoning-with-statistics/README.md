# Causal Reasoning with Statistics — computational companion

Reader materials for *Causal Reasoning with Statistics: Design, Identification, and
Reproducible Evidence in Psychology and the Social Sciences* (NEKpress Research).

Everything printed as a number in the book can be recomputed from the files in this
directory using free software and no network access. There is nothing to register for
and no account to create.

- Author: Nicholas Elliott Karlson
- Licence: Creative Commons Attribution 4.0 International throughout, with the scripts
  additionally available under the MIT License. See `LICENSE`.
- Provenance of this export: `SOURCE.json`
- File inventory and hashes: `SHA256SUMS`, which lists the 91 files beside it

## What is here

| Directory | Contents |
| --- | --- |
| `data/` | The ten synthetic datasets used by the book, plus per-unit provenance notes and the replayed latent-engagement column that Unit 10 audits |
| `dictionaries/` | One machine-readable data dictionary per dataset |
| `expected-results/` | One verified numeric record per case, plus the record for the two quantities added in the book's revision |
| `scripts/` | The seeded generators, the primary NumPy analyses, the standard-library Python recomputations, and the base-R recomputations |
| `run_all.py` | Runs the whole Python side: regenerate, recompute, compare |
| `run_all.R` | Runs the base-R side |

Every dataset is synthetic. No file describes a real person, clinic, school, municipality
or programme, and none of these studies happened.

## Reproduce the book's numbers

Requirements: Python 3.10 or newer with NumPy (`pip install -r requirements.txt`), and,
for the third path, any recent R. No contributed R packages are needed.

```bash
python3 run_all.py            # stages 1-3 below
Rscript run_all.R             # the base-R path
```

`run_all.py` does three things in order.

1. **Regenerate.** Each dataset is rebuilt from its seeded generator and compared with
   the published CSV. The files must come back byte for byte identical.
2. **Recompute (primary).** Each verified record is rebuilt with the NumPy path and
   compared with the published record. Two kinds of field are compared by rule instead of
   by byte equality, and both are reported: `primary_environment`, which records the
   interpreter and NumPy version that wrote a record, and the Unit 10 field
   `source_unit5_result_sha256`, which is the hash of the Unit 5 record *file* and so moves
   whenever that file's environment line moves. The latter is checked as a pointer: in each
   tree it must equal the hash of the Unit 5 record sitting beside it. The companion also
   records `source_unit5_result_canonical_sha256`, which excludes only the machine-specific
   environment object and therefore must remain identical across machines. Every other
   value must be identical.
3. **Recompute (independent).** A separate standard-library-only implementation, which
   imports neither NumPy nor the generators, recomputes the same quantities and asserts
   agreement with the published records to 2e-06.

Stages 1 and 2 run inside a temporary copy, so this directory is never written to. After a
run, `sha256sum -c SHA256SUMS` still passes and `git status` is still clean.

`run_all.R` is the third path. Each unit's base-R script reads the CSV files, refits the
models with `lm`, and checks its own results against anchors at the same 2e-06 tolerance.

A successful run prints `CAUSAL_REASONING_COMPANION_PYTHON_OK` and
`CAUSAL_REASONING_COMPANION_R_OK`. Any mismatch fails loudly and names the file.

## The two hidden-simulator addenda

Two quantities in the book are properties of the data-generating processes rather than
of the reader CSV files, and they are disclosed only so a reader can audit the teaching
claim. `scripts/addendum_book_revision.py` computes both, and the other two paths check
them.

- **Unit 9.** What the cell-standardized self-report contrast estimates in expectation
  under the generator's differential misclassification: 0.178830, against a hidden
  blinded risk difference of 0.145000. The realized contrast of 0.147500 lands near the
  truth in this one sample, which is a coincidence of sampling rather than evidence that
  the measure is sound.
- **Unit 10.** The structural confounding contribution in the Unit 5 case. Replaying the
  generator recovers the latent engagement variable, whose standardized gap between arms
  after adjustment is 0.672803. With the generator's own coefficient of −2.2 the implied
  bias is −1.480166, leaving an adjusted estimate of −4.661611 against a hidden sample
  effect of −4.226561. Removing the true confounding therefore does not close the gap;
  0.435050 mmHg remains.

One limitation is worth stating plainly. Base R cannot reproduce Python's pseudo-random
stream, so the R script does not replay the generator. It refits the gap from the
published CSV plus the replayed engagement column that the primary path writes to
`data/unit10_latent_engagement_replay.csv`. The primary path proves that the replay
reproduces every observable column of the published Unit 5 file; the R path audits the
estimation that follows.

## What is deliberately not here

This directory holds the computational companion, not the book's production system. It
excludes the manuscript source, the figure-building scripts, the document build and its
validators, the authoring templates, and private project notes. Those live in the
authoring repository and are not needed to reproduce a single printed number.

## Recorded verification

The published records were produced with Python 3.12.14 and NumPy 2.3.5. Every recorded
value is reproduced, to the digit, by Python 3.11.15 with NumPy 2.4.4; only the fields
named in stage 2 above differ. Record your own run below when you verify a release.

| Date | Platform | Python / NumPy | R | Result |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

## Reporting a problem

Open an issue in this repository with the file name, the command you ran, and the output
of the failing check. A reproducible numeric disagreement is a defect and will be
recorded in the errata.
