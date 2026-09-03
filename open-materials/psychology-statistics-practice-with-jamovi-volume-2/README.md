# Psychology Statistics Practice Materials with Jamovi, Volume 2

*Categorical, Rank-Based, Quasi-Experimental, and Single-Case Evidence*

Version 1.0
Nicholas Elliott Karlson
Published 3 September 2026

Version DOI: [10.5281/zenodo.22286929](https://doi.org/10.5281/zenodo.22286929)

This open educational resource contains 4 units, 96 practice problems, and 96 fully worked solutions. It continues the unit numbering of Volume 1: its units are numbered 12 through 15, and its problems are numbered accordingly, so the two volumes can be read as one continuous resource.

Volume 2 covers the material a first psychology statistics course reaches after group means: categorical outcomes and association, rank-based comparisons and robust thinking, quasi-experimental comparison and covariate adjustment, and single-case designs and nonoverlap. Its organising claim is that none of these is a substitute for a method in Volume 1 — each changes the question, not only the procedure.

The front matter includes an **Optional Books for Deeper Study** guide to four published books by Nicholas Elliott Karlson, explaining how each can extend the open material and providing a public Amazon link. The books are optional purchases; the CC BY 4.0 resource is complete and usable on its own. All four books also appear in the resource bibliography.

**Version 1.0, 3 September 2026:** first release. These downloads and checksums are authoritative.

## Download

- [PDF for reading and printing](psychology-statistics-practice-materials-with-jamovi-volume-2-open-resource-v1.0.pdf)
- [Editable DOCX for adaptation](psychology-statistics-practice-materials-with-jamovi-volume-2-open-resource-v1.0.docx)

The research scenarios are fictional and the teaching data are synthetic. No real participant, student, patient, client, clinical, institutional, thesis, or restricted data are included.

## Volume 1

Volume 1, *Psychology Statistics Practice Materials with Jamovi: Model Choice, Worked Solutions, and Scientific Evidence*, contains Units 1 through 11 and 232 problems with worked solutions. It is published under the same license in [the adjacent folder](../psychology-statistics-practice-with-jamovi/) with version DOI [10.5281/zenodo.22262048](https://doi.org/10.5281/zenodo.22262048).

Together the two volumes cover fifteen units, 328 practice problems, and 328 fully worked solutions.

## Companion Data

The public datasets, dictionaries, and verified results are available in this repository:

- [Synthetic CSV datasets](../../data/)
- [Data dictionaries](../../data/dictionaries/)
- [Verified result records](../../expected-results/)
- [Analysis matrix](../../ANALYSIS_MATRIX.md)

This volume specifically names `study_08_help_seeking_categorical.csv`, `study_09_skewed_wellbeing_nonparametric.csv`, `study_10_developmental_emotion_recognition.csv`, and `study_11_single_case_habit_tracking.csv`, all of which are already published in `data/`.

Every teaching variant used in the problems — Study 08A, Study 08B, Study 09A, Study 10A, and Study 11A — is a filter or subset of one of those four files, described exactly in the problem text, so a reader can reproduce it in jamovi Desktop with a row filter and no new file.

| Unit | Study | Central methods |
| --- | --- | --- |
| 12 | `study_08_help_seeking_categorical` | Frequency and contingency tables, chi-square test of independence, expected counts, Cramér's V |
| 13 | `study_09_skewed_wellbeing_nonparametric` | Distribution inspection, Kruskal-Wallis with tie correction, jamovi epsilon-squared, bias-adjusted rank effect size, Mann-Whitney comparisons with Holm adjustment |
| 14 | `study_10_developmental_emotion_recognition` | Grouped descriptives, one-way ANOVA, Bonferroni comparisons, covariate adjustment, quasi-experimental limits |
| 15 | `study_11_single_case_habit_tracking` | Phase descriptives, ordinal frequencies, visual level and trend inspection, nonoverlap of all pairs |

## License and Attribution

The PDF and DOCX are licensed under the [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/) (CC BY 4.0). You may share and adapt them, including commercially, provided that you give appropriate credit, link to the license, and indicate whether changes were made.

Suggested attribution:

> Karlson, Nicholas Elliott. *Psychology Statistics Practice Materials with Jamovi, Volume 2: Categorical, Rank-Based, Quasi-Experimental, and Single-Case Evidence*, Version 1.0, 2026. NEKpress Research. https://doi.org/10.5281/zenodo.22286929. Licensed CC BY 4.0.

## Numerical Verification

Every numerical value printed in this volume's worked solutions is recomputed from the four source CSV files by `scripts/verify_volume2_numbers.py`, including all five summary teaching variants. The script uses only the Python standard library and the raw CSV files; it does not read the repository's `expected-results` records, so it is an independent guard against document or dataset drift.

For Study 09, jamovi epsilon-squared is reported as *H* / (*N* - 1): 0.302 for the complete file and 0.325 for Study 09A. The separately calculated bias-adjusted rank effect size, (*H* - *k* + 1) / (*N* - *k*), is 0.291 and 0.314 respectively. The distinction is explicit in the problems, solutions, summary, verified-result record, and audit anchors.

Run `make audit-volume2` for the focused numerical check or `make verify` for the complete repository gate.

The complete public Markdown source, publication metadata, and hardened builder are in [`source/`](source/). The Zenodo deposit fields are recorded in [`zenodo-metadata.json`](zenodo-metadata.json).

## Integrity

SHA-256 checksums are recorded in [SHA256SUMS](SHA256SUMS):

| File | SHA-256 |
| --- | --- |
| DOCX | `5a506776db2753b4a6080139f2e5ec8be4e98d4fa53787227ea085e83fc21925` |
| PDF | `2684cf61e0e014d06f04b12d54e2b61ac0250e589b650374a1a1d6032c20d549` |

## Questions, Corrections, and Improvements

- Use [GitHub Discussions](https://github.com/nicholaskarlson/data/discussions) for questions, teaching experiences, accessibility suggestions, and ideas.
- Use the structured [Issue Forms](https://github.com/nicholaskarlson/data/issues/new/choose) for a reproducible error or correction.
- Read the repository [community scope](../../COMMUNITY.md) before posting.

When reporting a possible error, include the version, format, unit, page, and problem or solution number. Do not post real participant, student, clinical, institutional, thesis, or restricted data.

## A note on pairwise comparisons after Kruskal-Wallis

Unit 13 reports planned Mann-Whitney comparisons with tie-adjusted variance, a continuity correction, and Holm adjustment applied across the family of three. jamovi's Kruskal-Wallis analysis offers its own built-in pairwise comparison procedure, which is a different method and will produce different numbers. To reproduce the printed values, filter to each pair of groups in turn, request the Mann-Whitney U comparison in the independent-samples analysis, and apply the Holm adjustment across the three resulting *p* values. This is stated in the volume's back matter as well.
