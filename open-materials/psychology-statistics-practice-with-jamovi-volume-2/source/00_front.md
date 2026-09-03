*Open educational resource licensed CC BY 4.0*

NEKpress Research

**Version DOI:** [10.5281/zenodo.22286929](https://doi.org/10.5281/zenodo.22286929)

\newpage

# License, Attribution, and Community

Copyright © 2026 Nicholas Elliott Karlson. Except where otherwise noted, this work is licensed under the [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/) (CC BY 4.0).

This license permits sharing and adaptation for any purpose, including commercially, provided appropriate credit is given, a license link is supplied, and changes are indicated. This four-unit resource contains synthetic teaching data only; it does not contain evidence about real people.

Do not place real participant, student, client, clinical, institutional, thesis, or restricted data in the repository, Discussions, or support requests related to these materials.

## Source, Feedback, and Suggested Attribution

Repository, source files, synthetic datasets, dictionaries, verified result records, and version history: [https://github.com/nicholaskarlson/data](https://github.com/nicholaskarlson/data).

Questions, corrections, teaching ideas, and suggested improvements are welcome in [GitHub Discussions](https://github.com/nicholaskarlson/data/discussions).

Suggested attribution: Karlson, Nicholas Elliott. *Psychology Statistics Practice Materials with Jamovi, Volume 2: Categorical, Rank-Based, Quasi-Experimental, and Single-Case Evidence*. Version 1.0, 2026. NEKpress Research. [https://doi.org/10.5281/zenodo.22286929](https://doi.org/10.5281/zenodo.22286929). Licensed CC BY 4.0.

## Relationship to Volume 1

Volume 1, *Psychology Statistics Practice Materials with Jamovi: Model Choice, Worked Solutions, and Scientific Evidence*, contains Units 1 through 11 and 232 problems with worked solutions. It is available under the same license at the same repository, with version DOI [https://doi.org/10.5281/zenodo.22262048](https://doi.org/10.5281/zenodo.22262048).

This volume continues that sequence. Its units are numbered 12 through 15 and its problems are numbered accordingly, so a reader may work through both volumes as one continuous resource. Volume 2 does not repeat Volume 1's material and assumes its habits rather than its page numbers.

\newpage

# Contents

This open resource contains four units organized in two parts. Problems and worked solutions are presented together so readers can commit to an answer before consulting the feedback.

- Introduction: When the Familiar Model Does Not Fit
- How to Use These Materials
- Optional Books for Deeper Study
- The Reader's Evidence Checklist

**Part IV: Outcomes that are not means**

- Unit 12: Categorical Outcomes and Association
- Unit 13: Rank-Based Comparisons and Robust Thinking

**Part V: Designs that do not randomize**

- Unit 14: Quasi-Experimental Comparison and Covariate Adjustment
- Unit 15: Single-Case Designs and Nonoverlap

**Back matter**

- Cross-Volume Model-Choice Review
- Verified Result Records and How to Check Your Output
- References

\newpage

# Introduction: When the Familiar Model Does Not Fit

*Four situations that a first course reaches and a first course rarely finishes*

Volume 1 ended by comparing three or more conditions. That is where many first courses stop teaching model choice and start teaching exceptions. The exceptions are treated as a short chapter near the back of the book, usually titled *nonparametric methods* or *other designs*, and they are usually taught as a list of substitutes: use this test when the assumption fails, use that test when the outcome is a category.

That framing is the problem this volume exists to correct.

None of the four situations in these units is a substitution. Each one changes the question, not only the procedure.

**A categorical outcome is not a damaged continuous outcome.** When a participant chooses one of three support resources, there is no mean to estimate. The quantity of interest is a pattern of counts, and the analysis compares an observed pattern with the pattern that independence would produce. Calling a chi-square test "the nonparametric alternative" hides the fact that the estimand changed.

**A rank-based comparison is not a repaired mean comparison.** When a distribution is skewed, a rank method does not compute a more robust mean. It answers a question about the ordering of observations across groups. That question is often the better one, but it is a different one, and its result cannot be reported in the units of the original scale without an argument that nothing in the test supplies.

**A quasi-experimental design does not become an experiment because a covariate was added.** Adjustment changes which comparison the coefficient describes. Whether that change reduces bias or introduces it depends on what the covariate is - and in particular on whether it was caused by the grouping variable, in which case adjusting for it removes part of the very effect being estimated.

**A single-case design does not have a small sample. It has a different unit.** Forty-two daily observations of one person are forty-two measurements of one case. The comparison is within a series, and its credibility comes from replication across cases and from the pattern of level, trend, and overlap - not from a *p* value computed as if the days were people.

Each unit therefore begins one step before the procedure. It asks what the outcome is, what one row represents, what quantity the analysis targets, and what the design permits a reader to conclude. The procedure follows those answers.

## The claim ceiling does not move

Volume 1 introduced the **claim ceiling**: the strongest conclusion the complete evidence record authorizes. Nothing in this volume raises it. A significant chi-square does not make an observed association causal. A rank test does not make a convenience sample representative. An analysis of covariance does not manufacture random assignment. A large nonoverlap statistic does not establish that a routine will work for anyone else.

Three of these four designs are especially prone to a particular failure: the analysis is genuinely more sophisticated than a *t* test, and the added sophistication is quietly transferred to the conclusion. It should not be. Model complexity and identification are independent. A more careful calculation on a design that cannot separate explanations produces a more careful answer to the same limited question.

## What each unit uses

Every problem in this volume rests on a public synthetic dataset with a published data dictionary and an independently recomputed verified result record. Nothing here requires a purchase, a login, or a prepared jamovi session file.

| Unit | Primary dataset | Central methods |
| --- | --- | --- |
| 12 | `study_08_help_seeking_categorical` | Frequency and contingency tables, chi-square test of independence, expected counts, Cramér's V |
| 13 | `study_09_skewed_wellbeing_nonparametric` | Distribution inspection, Kruskal-Wallis with tie correction, jamovi epsilon-squared, bias-adjusted rank effect size, Mann-Whitney comparisons with Holm adjustment |
| 14 | `study_10_developmental_emotion_recognition` | Grouped descriptives, one-way ANOVA, Bonferroni comparisons, covariate adjustment, quasi-experimental limits |
| 15 | `study_11_single_case_habit_tracking` | Phase descriptives, ordinal frequencies, visual level and trend inspection, nonoverlap of all pairs |

Every numerical value printed in the worked solutions of this volume is recomputed from the source CSV files by a public audit script in the same repository. If a number here disagrees with your jamovi output, one of three things is true: your import differs, your options differ, or there is an error worth reporting. All three are worth finding out.

\newpage

# How to Use These Materials

Read the introduction first. This section describes the practice routine, which is the same routine used in Volume 1.

Statistics becomes usable through decisions, not recognition alone. Reading a clear explanation can make a method feel familiar; solving a new case reveals whether the reasoning can be retrieved and transferred.

Each unit moves through six levels. Begin without looking at the solutions. Commit to an answer, mark your confidence, and then compare your reasoning with the worked response. When an answer is wrong, record the cue you missed rather than merely copying the correction.

## The six levels

1. **Recall and recognize:** retrieve the vocabulary and design features.
2. **Predict before clicking:** state what pattern you expect before seeing software output.
3. **Calculate and explain:** connect a small calculation to the model's logic.
4. **Read jamovi output:** locate, translate, and integrate the relevant evidence.
5. **Choose the model:** select one analysis and reject plausible alternatives.
6. **Report and critique:** communicate the result and repair reasoning that exceeds the evidence.

Each unit contains four problems at each level, twenty-four problems in total.

## A useful practice loop

For each problem, write four brief notes: **answer**, **reason**, **confidence**, and **revision**. Reattempt missed problems after a delay. A correct answer that depends on remembering the page is less valuable than a correct answer reached from the design and data structure.

When a solution includes **Study in the Larger Evidence Program**, record what the study adds, what it cannot settle, and which next study would be most informative. This keeps one statistical result in its scientific context.

## Working in jamovi Desktop

Every analysis in this volume can be reproduced in the free jamovi Desktop application on Windows, macOS, or Linux. The units name analysis goals and output fields rather than reproducing pictures of the interface, because interfaces move between releases and platforms while the statistical goal does not.

Begin every exercise from a fresh import of the named CSV. Before running anything, confirm four things: the row count matches the dictionary, each variable carries the intended measurement level, blank cells are understood as missing rather than as zero, and the group order matches the direction stated in the problem. Most disagreements between a reader's output and a verified record are caused by one of those four items.

## Companion data and feedback

The public companion files used by this volume are `study_08_help_seeking_categorical.csv`, `study_09_skewed_wellbeing_nonparametric.csv`, `study_10_developmental_emotion_recognition.csv`, and `study_11_single_case_habit_tracking.csv`, together with their data dictionaries and verified result records. Browse them at [https://github.com/nicholaskarlson/data](https://github.com/nicholaskarlson/data); use [Discussions](https://github.com/nicholaskarlson/data/discussions) for questions and improvements.

## Teaching variants

Several problems refer to a **teaching variant**, written as Study 08A, Study 08B, Study 09A, Study 10A, or Study 11A. Every variant in this volume is a filter or subset of the same public CSV, described exactly in the problem, so a reader can reproduce it in jamovi with a row filter and no new file. Variants exist to prevent model choice from depending on whether a particular result turned out to be favorable.

# Optional Books for Deeper Study

This open resource is complete on its own. The following published books are optional purchases for readers who want fuller conceptual instruction, reproducible code workflows, or guidance for planning real research and consulting relationships.

## Psychology Research Methods and Statistics by Design with Jamovi

This 27-chapter, beginner-friendly guide is the closest conceptual companion to these practice materials. Chapters 22 through 25 cover the four topics in this volume directly: categorical data and chi-square tests, nonparametric methods and robust thinking, quasi-experimental and developmental designs, and single-case and small-*N* designs. It uses the same public synthetic-data ecosystem. [View on Amazon](https://www.amazon.com/dp/B0HG9VV1JR).

## Psychological Statistics by Design

This advanced, code-first psychology guide follows evidence from a research question and data layout through Python analysis, independent R verification, parity checks, and reviewer packets. Its chapters on baseline adjustment and analysis of covariance, and on outcomes whose distribution changes the question, extend Units 14 and 13 respectively. [View on Amazon](https://www.amazon.com/dp/B0HCMCKR7X).

## Applied Statistics with Python and R

This accessible Python-first guide develops a broader applied workflow, using R for optional independent verification and PyStatsV1 as a bridge to a proof-first evidence package. Use it when you want to turn the reasoning practiced here into a reproducible, cross-language workflow. [View on Amazon](https://www.amazon.com/dp/B0H996LF88).

## Before You Hire a Statistician

This guide explains what statistical consulting can and cannot do, what to prepare before contact, how scope, fees, timelines, deliverables, and revisions work, and how privacy, authorship, ethics, and responsibility should be handled. Use it before adapting these exercises to a real study, sharing data, or hiring statistical help. [View on Amazon](https://www.amazon.com/dp/B0H661RV6B).

\newpage

# The Reader's Evidence Checklist

Before accepting a statistical conclusion, ask:

1. What is the scientific question?
2. What are the cases or independent units?
3. How were the constructs measured, and are the scores comparable?
4. How were observations sampled, assigned, exposed, and retained?
5. What estimand does the analysis target?
6. Why does the selected model match the design and dependence structure?
7. What estimate and interval answer the question?
8. Which assumptions and diagnostic evidence matter for that answer?
9. What alternative explanations remain?
10. What is the claim ceiling?
11. What does the study contribute to responsiveness, consistency, or mechanism?
12. What next evidence would most reduce the remaining uncertainty?

Use this checklist before opening jamovi, while reading its output, and again when writing the conclusion. The purpose is not to make every claim timid. It is to make each claim as strong as the evidence permits - and no stronger.

## Two additions for this volume

Four situations in this volume introduce two further questions that Volume 1 did not need.

**13. Does the summary I am about to report exist on the scale I am about to report it on?** A chi-square test produces no mean difference. A rank test produces no difference in the outcome's units. Reporting one anyway is the most common error in these four units.

**14. What is the unit that could be replicated?** In a categorical study it is the participant. In a quasi-experimental comparison it is the group whose selection must be explained. In a single-case design it is the case, and one case cannot support generality no matter how clean its series looks.

\newpage
