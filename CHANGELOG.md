# Changelog

## reader-assets-v1.0.3 — 2026-09-03

- Corrected the Study 09 verified-result definition to match jamovi jmv 28.2.0: epsilon-squared is *H* / (*N* - 1), giving 0.302 for the complete file and 0.325 for the row-filter teaching variant.
- Retained (*H* - *k* + 1) / (*N* - *k*) under the separate label `bias_adjusted_rank_effect_size`, giving 0.291 and 0.314, so the prior calculation remains available without being mislabeled as jamovi output.
- Updated the Study 09 checksum, release manifest, analysis matrix, citation metadata, and deterministic reader-assets bundle while preserving all 12 CSV datasets, all 12 dictionaries, and all six figures byte-for-byte.
- Preserved the immutable `reader-assets-v1`, `reader-assets-v1.0.1`, and `reader-assets-v1.0.2` releases.

## psychology-statistics-practice-materials-volume-2-v1.0 — 2026-09-03

- Published *Psychology Statistics Practice Materials with Jamovi, Volume 2: Categorical, Rank-Based, Quasi-Experimental, and Single-Case Evidence* as a CC BY 4.0 open educational resource.
- Added one PDF and one editable DOCX containing 4 units, 96 practice problems, and 96 fully worked solutions, numbered Units 12 through 15 in continuation of Volume 1.
- Closed the coverage gap between Volume 1 and the standard first-course syllabus: Volume 1 stopped at comparing three or more conditions, leaving `study_08` through `study_11` without open practice material despite having published dictionaries and verified result records.
- Unit 12 uses `study_08_help_seeking_categorical` for contingency tables, the chi-square test of independence, expected counts, and Cramér's V, with two prior-support subsets that hold the effect size near constant while the *p* value moves from .001 to .095.
- Unit 13 uses `study_09_skewed_wellbeing_nonparametric` for Kruskal-Wallis with tie correction, jamovi epsilon-squared, a separately named bias-adjusted rank effect size, and Holm-adjusted Mann-Whitney comparisons. The outlier-deleted variant raises the statistic from 39.573 to 41.560, jamovi epsilon-squared from 0.302 to 0.325, and the bias-adjusted quantity from 0.291 to 0.314.
- Unit 14 uses `study_10_developmental_emotion_recognition` for one-way ANOVA, Bonferroni comparisons, and covariate adjustment, contrasting the total age difference of 13.006 points with the vocabulary-held-fixed coefficient of 8.917 and distinguishing multiplicity adjustment from covariate adjustment.
- Unit 15 uses `study_11_single_case_habit_tracking` for phase descriptives, ordinal frequencies, and nonoverlap of all pairs, including a hand-computed NAP with the half-credit tie rule and an explicit rejection of an independent-samples test applied to 28 days of one case.
- All five teaching variants are filters on the four published CSV files and require no new data file.
- Added a dependency-free numerical audit that independently recomputes 355 checks from the four raw CSV studies and all five teaching variants; `make audit-volume2` and the complete `make verify` gate run it.
- Added a byte-pinned release check with public-release text, live-hyperlink, core-property, tagged-PDF, source-inventory, and repository-surface requirements for version DOI `10.5281/zenodo.22286929`.
- Published the Markdown source, release metadata, and hardened atomic builder, and added the resource to the GitHub Pages landing page, SUPPORT.md, and COMMUNITY.md without altering the Volume 1 release.
- Removed the inherited even/odd header switch from the Volume 1 reference DOCX so every page after the cover carries the Volume 2 running title and its physical page number; the builder and release checks now fail closed on any recurrence.

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
