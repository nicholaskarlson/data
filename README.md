# Psychology Research Methods and Statistics by Design with Jamovi Companion

Reader assets for *Psychology Research Methods and Statistics by Design with Jamovi: From Scientific Questions to APA-Style Results and Reproducible Evidence*.

- Publisher: NEKpress.ca
- Author: Nicholas Elliott Karlson
- Reader download: `https://github.com/nicholaskarlson/data`
- Canonical repository: `https://github.com/nicholaskarlson/nekpress-psychology-methods-statistics-jamovi-companion`
- Release line: `reader-assets-v1.0.2`
- Immutable prior releases: `reader-assets-v1` and `reader-assets-v1.0.1`

## Start Here

Readers can use the short address `https://github.com/nicholaskarlson/data` and choose **Code > Download ZIP**, or download individual files from the `data/` directory. Use [QUICK_START.md](QUICK_START.md) to import a CSV into jamovi Desktop on Windows, macOS, or Ubuntu, check its measurement levels, and recreate a chapter workflow. Every exercise starts from a CSV; no prepared session file is required.

The short repository is a verified reader-facing mirror. This longer companion repository remains the canonical technical source and issue tracker; changes originate here and are copied to the short repository only after verification.

## Published Assets

- `data/`: 12 deterministic synthetic CSV datasets, 12 machine-readable dictionaries, provenance, and checksums.
- `expected-results/`: one verified numeric record per study, plus checksums.
- `ANALYSIS_MATRIX.md`: the study-to-chapter and workflow map.
- `figures/generated/`: six seeded, source-generated explanatory figures used by the text-first edition.
- `RELEASE_MANIFEST.json`: the exact release inventory, byte sizes, and SHA-256 hashes.
- `releases/`: instructions for building and validating the reader-assets archive.

Run `make verify` to check the complete release, or `make release` to produce `dist/nekpress-jamovi-companion-reader-assets-v1.0.2.zip`.

## Software Scope

The workflows use official jamovi Desktop. The verified Ubuntu environment reported application release 28.2, bundled modules jmv 28.2.0 and scatr 28.2.0, Flatpak metadata version 2.7.27, and Flatpak commit `3cced0e1e2519185293ddd6df38277edb93f780ee6c645f9658cd87580f9ca21`. Version labels can differ across the application, modules, packaging metadata, and official citation family; see the book’s setup chapter for the full identity note.

Ubuntu representative validation was completed on 22 August 2026. The record confirms the exact release bundle and environment; Study 01 descriptives; Study 02 paired inference; Study 07 correlation and regression; Study 05 factorial ANOVA; the Study 06 parametric mixed repeated-measures ANOVA; the two-line group-by-week plot; and export, save, complete application close, file-browser reopen, output persistence, and final source-checksum checks. The Windows and macOS instructions are designed around the same CSV-first interface but remain release-candidate workflows until representative validation is recorded. Report a reproducible platform difference through an issue rather than assuming that menu wording is identical in every build.

The `reader-assets-v1.0.2` patch records the Ubuntu statistical validation and corrects Study 06 sphericity values to match jamovi's mixed repeated-measures calculation. It preserves the same 12 synthetic datasets, 12 dictionaries, and six committed figures as the immutable `reader-assets-v1` and `reader-assets-v1.0.1` releases; only the Study 06 verified result record and release metadata change.

## Data and Support Boundary

All datasets are synthetic teaching materials. Do not post private data, identifiable data, clinical data, student records, client data, institutional data, thesis data, restricted data, or homework answers.

Use GitHub Issues for reproducible book errors, public companion-file questions, and jamovi Desktop output mismatches. This repository does not provide clinical, legal, medical, or individualized statistical consulting.
