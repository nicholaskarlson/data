# Psychology Research Methods and Statistics by Design with Jamovi Companion

Reader assets for *Psychology Research Methods and Statistics by Design with Jamovi: From Scientific Questions to APA-Style Results and Reproducible Evidence*.

- Publisher: NEKpress.ca
- Author: Nicholas Elliott Karlson
- Canonical repository: `https://github.com/nicholaskarlson/nekpress-psychology-methods-statistics-jamovi-companion`
- Release line: `reader-assets-v1`

## Start Here

Use [QUICK_START.md](QUICK_START.md) to download a CSV, import it into jamovi Desktop on Windows, macOS, or Ubuntu, check its measurement levels, and recreate a chapter workflow. Every exercise starts from a CSV; no prepared session file is required.

## Published Assets

- `data/`: 12 deterministic synthetic CSV datasets, 12 machine-readable dictionaries, provenance, and checksums.
- `expected-results/`: one verified numeric record per study, plus checksums.
- `ANALYSIS_MATRIX.md`: the study-to-chapter and workflow map.
- `figures/generated/`: six seeded, source-generated explanatory figures used by the text-first edition.
- `RELEASE_MANIFEST.json`: the exact release inventory, byte sizes, and SHA-256 hashes.
- `releases/`: instructions for building and validating the reader-assets archive.

Run `make verify` to check the complete release, or `make release` to produce `dist/nekpress-jamovi-companion-reader-assets-v1.zip`.

## Software Scope

The workflows use official jamovi Desktop. The verified Ubuntu environment reported application release 28.2, bundled modules jmv 28.2.0 and scatr 28.2.0, Flatpak metadata version 2.7.27, and Flatpak commit `3cced0e1e2519185293ddd6df38277edb93f780ee6c645f9658cd87580f9ca21`. Version labels can differ across the application, modules, packaging metadata, and official citation family; see the book’s setup chapter for the full identity note.

The Windows and macOS instructions are designed around the same CSV-first interface but remain release-candidate workflows until representative validation is recorded. Report a reproducible platform difference through an issue rather than assuming that menu wording is identical in every build.

## Data and Support Boundary

All datasets are synthetic teaching materials. Do not post private data, identifiable data, clinical data, student records, client data, institutional data, thesis data, restricted data, or homework answers.

Use GitHub Issues for reproducible book errors, public companion-file questions, and jamovi Desktop output mismatches. This repository does not provide clinical, legal, medical, or individualized statistical consulting.
