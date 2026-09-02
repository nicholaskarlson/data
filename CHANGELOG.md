# Changelog

## psychology-statistics-practice-materials-v1.1 — 2026-09-03

- Embedded the reserved version DOI `10.5281/zenodo.22262048` in the editable DOCX, print-ready PDF, resource README, and public landing page.
- Corrected the internally inconsistent wording of Solution 4.7 while preserving its verified values and substantive conclusion.
- Clarified that the displayed rounded inputs in Solution 9.11 give an upper confidence limit of `0.128`, whereas the unrounded verified calculation gives `0.129`; the inferential conclusion is unchanged.
- Clarified the Tukey scale in Problem and Solution 11.15: the half-width is `(3.357 / √2) × 1.781 = 4.227`, equivalently `3.357 × √(63.418 / 40)`.
- Added a dependency-free numerical audit that independently recomputes 112 checks from the three raw CSV studies and the two summary-defined teaching variants; both `make audit` and the complete `make verify` gate run it.
- Preserved the 11-unit structure, 232 practice problems, 232 fully worked solutions, four-book guide, four Amazon links, and four bibliography entries.

## psychology-statistics-practice-materials-v1.0 — 2026-09-02

- Published *Psychology Statistics Practice Materials with Jamovi: Model Choice, Worked Solutions, and Scientific Evidence* as a CC BY 4.0 open educational resource.
- Added one PDF and one editable DOCX containing 11 units, 232 practice problems, and 232 fully worked solutions.
- Corrected the canonical Version 1.0 PDF and DOCX after the initial public upload inadvertently used the pre-four-book export; the current 145-page edition includes the optional-reading guide, four public Amazon links, and four bibliography entries.
- Added checksums, suggested attribution, repository and Discussion links, and prominent synthetic-data and privacy guidance.
- Added the resource to the existing GitHub Pages landing page without replacing the established dataset design or changing the immutable `reader-assets-v1.0.2` payload.

## reader-assets-v1.0.2 — 2026-08-22

- Recorded complete Ubuntu representative validation, including the Study 06 two-line profile plot, export, save, complete application close, file-browser reopen, output persistence, and final source-checksum checks.
- Corrected Study 06 sphericity evidence to match jamovi Desktop's mixed-design output: Mauchly's W = .752, Greenhouse-Geisser epsilon = .801, and corrected df = 1.603 and 131.428.
- Preserved all 12 datasets, all 12 dictionaries, and all six committed figures byte-for-byte.
- Preserved immutable `reader-assets-v1` and `reader-assets-v1.0.1` releases.

## reader-assets-v1.0.1 — 2026-08-21

- Corrected Ubuntu status to partial: application launch and Study 02 CSV import were observed, while the representative matrix remains pending.
- Kept Windows and macOS instructions explicitly release-candidate pending representative validation.
- Preserved the 12 datasets, 12 dictionaries, 12 verified result records, and six committed figures from immutable `reader-assets-v1`.

## reader-assets-v1 — 2026-08-21

- Published 12 deterministic synthetic CSV datasets and 12 data dictionaries.
- Published verified result records, SHA-256 manifests, and the analysis matrix.
- Added a cross-platform CSV-first quick-start guide.
- Added six seeded, source-generated explanatory figures used by the text-first edition.
- Replaced the preliminary structure check with an exact release verifier and deterministic bundle builder.

## 0.1.0

- Created the initial public companion repository structure.
