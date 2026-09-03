# Cross-Volume Model-Choice Review

The units in this volume are not a list of substitutes for the methods in Volume 1. Each answers a question the earlier methods cannot pose. This table is a review aid for that distinction; it is not a flowchart, and reading down the right-hand column is not a substitute for reading a design.

| The question actually being asked | What one row represents | Defensible analysis | Where it is treated |
| --- | --- | --- | --- |
| How much did a quantity change within the same people? | One person measured twice | Paired comparison of differences | Volume 1, Unit 10 |
| How far apart are two independent group means? | One person in one group | Independent-samples comparison, variance model chosen from the design | Volume 1, Unit 10 |
| How far apart are three or more independent group means? | One person in one group | One-way analysis of variance with a prespecified multiplicity-adjusted family | Volume 1, Unit 11 |
| Does the distribution of a categorical choice differ across groups? | One person, one category | Chi-square test of independence with an association effect size | Unit 12 |
| Do observations in one group tend to sit higher in the ordering than those in another? | One person, one score | Kruskal-Wallis with jamovi epsilon-squared, a bias-adjusted rank effect size, and adjusted pairwise comparisons | Unit 13 |
| How does an outcome differ across groups that were never assigned? | One person in one observed or unassignable group | Group comparison, reported with the identification limit stated | Unit 14 |
| How much of a group difference does not operate through a third variable? | One person, plus the third variable | Covariate-adjusted model, reported as a decomposition and not a correction | Unit 14 |
| Did one person's behaviour change when a condition was introduced? | One occasion for one case | Series inspection with level, trend, variability, and nonoverlap | Unit 15 |

## Four questions that decide most of this volume

**Is the outcome a quantity or a category?** If it is a category, no mean exists and no difference can be reported in the outcome's units. Recoding categories as numbers changes the answer when the labels are reordered, which is the test for whether the recoding was legitimate.

**Is the reason for a rank method the shape of the distribution or something else?** Skew and extreme values are reasons. Unequal spread is not, and a rank method is not a remedy for it. Whatever the reason, state it, and report the result on the scale the method actually estimates.

**Was the grouping variable assigned, observed, or unassignable?** This determines the claim ceiling and nothing in the analysis can change it. An unassignable grouping variable such as age has a permanently lower ceiling, because there is no counterfactual in which the same case occupies a different level at the same moment.

**For every covariate, where does it sit in the causal order?** A common cause measured before both variables is a confounder, and adjusting for it reduces bias. A consequence of the grouping variable is not, and adjusting for it removes part of the effect. The regression output looks identical in both cases; only an argument about the causal order distinguishes them.

\newpage

# Verified Result Records and How to Check Your Output

Every numerical value printed in this volume's worked solutions is recomputed from the source CSV files by a public audit script in the same repository, and every value in the verified result records was independently recomputed from the same files before publication. This section explains how to use those records when your own output disagrees.

## What is published

For each of the four studies used here, the repository contains:

- the synthetic CSV file;
- a machine-readable data dictionary naming every variable's role, measurement level, permitted values, and missing-value policy;
- a verified result record in JSON holding the analysis targets for that study;
- SHA-256 checksums for the data files and the result records; and
- an entry in `ANALYSIS_MATRIX.md` mapping the dataset to its intended workflows and its result fields.

Nothing in that list requires an account, a purchase, or a prepared jamovi session file.

## The four causes of nearly every mismatch

When a number on your screen disagrees with a number in this volume, work through these before reporting an error.

**The import.** Confirm the row count and the column names against the dictionary. Confirm that the file you opened is the one the problem names, and that it was imported fresh rather than restored from a saved session.

**The measurement level.** jamovi guesses a level on import and its guess is sometimes wrong. A grouping variable read as continuous, or an identifier read as nominal and included in an analysis, changes the output without any warning.

**The group order.** A difference has a sign, and the sign depends on which group the software subtracts from which. Every direction in this volume is stated explicitly in the problem; check yours against it before concluding that a value is wrong.

**Missing values.** Blank cells must be treated as missing rather than as zero, and the number of complete cases in your output must match the record.

## When the disagreement survives all four

Then it is worth reporting, and it is worth reporting precisely. Include your operating system, your jamovi release, the dataset filename, the exact analysis and options you selected, the observed value, and the expected value. Use the repository's structured issue forms for a reproducible error and Discussions for a question. Do not attach real participant, student, clinical, institutional, thesis, or restricted data to any report.

## A note on version identity

The verified records for these studies were produced against jamovi Desktop application release 28.2, whose bundled analysis modules report version 28.2.0. The Flatpak metadata field for the same installation reports 2.7.27, and the project's own requested citation family is Version 2.7. These are three labels for one installation and serve different records; none of them contradicts the others. When you report your own environment, give the release your application displays together with your operating system.

## A note on the effect sizes reported after Kruskal-Wallis

jamovi reports epsilon-squared as *H* / (*N* − 1). For these data, 39.573 / 131 = 0.302. Unit 13 uses that value whenever it names jamovi epsilon-squared, matching the software output learners are asked to read.

The unit also reports a separately named bias-adjusted rank effect size, (*H* − *k* + 1) / (*N* − *k*) = 0.291. That formula subtracts the value the statistic would be expected to take under no association before rescaling it, so the adjusted measure is centred at zero when nothing is happening. The two quantities answer closely related questions and the gap between them shrinks as the sample grows, but they are not interchangeable labels. Report the formula or software definition and do not call the 0.291 quantity jamovi epsilon-squared.

The same caution applies to any effect size whose definition varies between packages. Naming the formula alongside the number costs one clause and removes the ambiguity entirely.

## A note on pairwise comparisons after Kruskal-Wallis

Unit 13 reports planned Mann-Whitney comparisons with tie-adjusted variance, a continuity correction, and Holm adjustment applied across the family of three. jamovi's Kruskal-Wallis analysis offers its own built-in pairwise comparison procedure, which is a different method and will produce different numbers. To reproduce the values printed in Unit 13, filter to each pair of groups in turn, request the Mann-Whitney U comparison in the independent-samples analysis, and apply the Holm adjustment across the three resulting *p* values. Either approach is defensible; reporting one while citing the other is not.

\newpage

# References

American Psychological Association. (2020). *Publication manual of the American Psychological Association* (7th ed.). American Psychological Association.

Brown, M. B., & Forsythe, A. B. (1974). Robust tests for the equality of variances. *Journal of the American Statistical Association, 69*(346), 364-367.

Cramér, H. (1946). *Mathematical methods of statistics*. Princeton University Press.

Holm, S. (1979). A simple sequentially rejective multiple test procedure. *Scandinavian Journal of Statistics, 6*(2), 65-70.

Karlson, N. E. (2026a). *Applied statistics with Python and R: From question to defensible result through reproducible analysis, cross-language verification, and APA-style reporting*. NEKpress Research.

Karlson, N. E. (2026b). *Before you hire a statistician: An honest guide to research analysis, reproducibility, consulting scope, fees, and ethical boundaries*. NEKpress Research.

Karlson, N. E. (2026c). *Psychological statistics by design*. NEKpress Research.

Karlson, N. E. (2026d). *Psychology research methods and statistics by design with jamovi: From scientific questions to APA-style results and reproducible evidence*. NEKpress Research.

Karlson, N. E. (2026e). *Psychology statistics practice materials with jamovi: Model choice, worked solutions, and scientific evidence* (Version 1.1). NEKpress Research. https://doi.org/10.5281/zenodo.22262048

Kruskal, W. H., & Wallis, W. A. (1952). Use of ranks in one-criterion variance analysis. *Journal of the American Statistical Association, 47*(260), 583-621.

Mann, H. B., & Whitney, D. R. (1947). On a test of whether one of two random variables is stochastically larger than the other. *Annals of Mathematical Statistics, 18*(1), 50-60.

Mosteller, F., & Tukey, J. W. (1977). *Data analysis and regression: A second course in statistics*. Addison-Wesley.

Parker, R. I., & Vannest, K. J. (2009). An improved effect size for single-case research: Nonoverlap of all pairs. *Behavior Therapy, 40*(4), 357-367.

Pearson, K. (1900). On the criterion that a given system of deviations from the probable in the case of a correlated system of variables is such that it can be reasonably supposed to have arisen from random sampling. *The London, Edinburgh, and Dublin Philosophical Magazine and Journal of Science, 50*(302), 157-175.

The jamovi project. *jamovi* (Version 2.7) [Computer software]. https://www.jamovi.org

\newpage

# About the Author

Nicholas Elliott Karlson writes open, reproducible materials for teaching research methods and statistics. His work emphasizes model choice, claim limits, synthetic teaching data, independently verified results, and workflows that a reader can inspect from the raw file through the reported conclusion.

# About This Resource

*Psychology Statistics Practice Materials with Jamovi, Volume 2: Categorical, Rank-Based, Quasi-Experimental, and Single-Case Evidence* contains four units, 96 practice problems, and 96 fully worked solutions. It continues the unit numbering of Volume 1 and is licensed under the same Creative Commons Attribution 4.0 International License.

All research scenarios are fictional and all teaching data are synthetic. No real participant, student, patient, client, clinical, institutional, thesis, or restricted data are included, and no result in this resource is evidence about real people.

The synthetic datasets, data dictionaries, verified result records, checksums, and the numerical audit script that recomputes every printed value are published in the same public repository:

**[https://github.com/nicholaskarlson/data](https://github.com/nicholaskarlson/data)**

Version DOI: **[10.5281/zenodo.22286929](https://doi.org/10.5281/zenodo.22286929)**

NEKpress Research
