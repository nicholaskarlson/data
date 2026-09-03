# Unit 13: Rank-Based Comparisons and Robust Thinking

*Open educational resource licensed CC BY 4.0. All research scenarios are fictional and all datasets are synthetic. Complete the problems before consulting the worked solutions.*

## Unit Purpose

A rank-based comparison is not a repaired mean comparison. It replaces the observed values with their positions in the combined ordering and asks whether observations from one group tend to sit higher in that ordering than observations from another. The result is a statement about ordering, not about the outcome's scale, and it cannot be reported in the outcome's units without an assumption the test never supplies. This unit develops the habit of choosing a rank method for a stated reason, reporting it on the scale it actually estimates, and refusing to treat outlier deletion as a neutral act.

## Learning Objectives

After completing this unit, a learner should be able to:

- describe a distribution from a five-number summary and say what a mean and a standard deviation conceal;
- explain what replacing values with ranks preserves and what it discards;
- compute a mean rank and check rank sums against their known total;
- state what the Kruskal-Wallis test compares and why it is not a test of medians in general;
- interpret jamovi epsilon-squared, a bias-adjusted rank effect size, and a rank-biserial correlation on the scales they occupy;
- apply and justify a multiplicity adjustment for planned pairwise comparisons;
- recognize that a grouping variable can be ordinal while its pattern is not monotonic; and
- treat the deletion of flagged observations as a modelling decision that must be prespecified and reported.

## Decision Map

Ask these questions in order:

1. What is the scientific question, and does it concern typical values, ordering, or the whole distribution?
2. What are the cases, and does each contribute one independent observation?
3. What does the outcome's distribution look like within each group, before any test is chosen?
4. What is the stated reason for a rank-based method: skew, outliers, unequal spread, an ordinal outcome, or something else?
5. What quantity does the chosen method estimate, and on what scale can it be reported?
6. If the overall test is followed by pairwise comparisons, what family are they in and how is multiplicity handled?
7. What does the design identify, what is the claim ceiling, and what evidence should come next?

## Study Files

The primary dataset is `study_09_skewed_wellbeing_nonparametric.csv`. The teaching variant is a subset of the same file, reproducible in jamovi with a row filter on `outlier_flag`. Public CSV files, dictionaries, and verified result records are available at [https://github.com/nicholaskarlson/data](https://github.com/nicholaskarlson/data).

| Study | Data structure | Primary outcome | Unit role |
| --- | --- | --- | --- |
| Study 09 | 132 participants, 44 in each of three app-use groups | Wellbeing score, skewed, with three flagged observations | Complete rank-based comparison |
| Study 09A | The 129 rows with `outlier_flag = no` | Wellbeing score | The consequence of deleting flagged observations |

The variable `outlier_flag` is a teaching flag included in the synthetic file to mark the observations an inattentive analyst is most likely to delete. It is not a statistical verdict and it does not identify errors.

## Plausible Research Scenarios

The scenarios create decisions rather than documenting real research. At each Pause and Decide, stop reading and write an answer, reason, and confidence rating.

### Plausible Research Scenario: Wellbeing Across Three Levels of App Use

*This is a fictional research scenario created for teaching. Every referenced dataset is synthetic; it does not describe a real study or real participants.*

A fictional student wellbeing service surveys 132 students. Each student reports how much they use a wellbeing app - low, moderate, or high - and completes a wellbeing questionnaire scored from roughly 0 to 100. The groups are formed by what students report, not by anything the service assigned.

The wellbeing scores are not symmetric. The low-use group in particular has a long lower tail: its minimum is 26.9 against a first quartile of 51.8, and two of its observations carry the teaching outlier flag. A third flagged observation sits in the moderate group.

The research question is: **do wellbeing scores tend to differ across the three app-use groups?** The word *tend* is deliberate. The team is asking whether students in one group generally sit higher in the ordering of wellbeing scores than students in another, not whether one group's arithmetic mean exceeds another's by a stated number of points.

`app_use_group` is recorded as ordinal, with low below moderate below high. Nothing in the design guarantees that wellbeing changes monotonically across those three levels.

#### Pause and Decide

Before reading further, write down what you expect the distributions to look like from the five-number summaries alone, choose a comparison method and state the reason in one sentence, and predict whether the pattern across the three ordered groups will be monotonic. Then state what quantity your chosen method will and will not produce.

#### Why This Model?

The Kruskal-Wallis test compares the mean ranks of three or more independent groups after replacing all observations with their positions in the combined ordering. That matches a question about whether observations from one group tend to sit higher than observations from another, and it is not disturbed by a long tail in the way that a mean is.

The reason to prefer it here is skew and a small number of extreme low observations, not unequal spread. The three groups' standard deviations are 9.461, 7.167, and 7.479, and a median-centred Brown-Forsythe test gives *F*(2, 129) = 0.54, *p* = .583. Spread is not the problem. Saying so matters, because "the variances were unequal" is the most commonly given and most commonly wrong justification for a rank method.

A one-way analysis of variance is available and would not be absurd. It gives *F*(2, 129) = 24.77, *p* < .001, with eta-squared of 0.278, and it points to the same ordering. The choice between the two is therefore not a choice between a significant and a non-significant result. It is a choice about which quantity to report: a comparison of arithmetic means, which the long lower tail makes a less representative summary of a typical student, or a comparison of orderings, which is insensitive to how far the tail extends.

The Kruskal-Wallis test is often described as a test of medians. It is not, in general. It is a test of whether one group's observations tend to be larger, and it becomes a test about medians only under the additional assumption that the groups' distributions have the same shape and differ only by a shift.

#### What Would a Favorable Result Look Like?

The service would hope to see a clear and interpretable ordering across the three groups, with an effect size large enough to justify further work and pairwise comparisons that locate where the differences sit. A non-monotonic pattern would be more interesting than a monotonic one, because it would rule out the simplest story.

An inconclusive result would still be useful. If wellbeing does not order with reported app use, the service learns that self-reported usage volume is not a promising screening variable.

#### Best Defensible Claim

**Statistical evidence:** The rank-based analysis estimates whether observations in one app-use group tend to sit higher in the combined ordering of wellbeing scores than observations in another. jamovi's epsilon-squared, computed as *H* / (*N* − 1), summarizes the omnibus separation on the rank scale; the separately calculated bias-adjusted rank effect size subtracts the null expectation from *H* before rescaling it.

**Causal identification:** Group membership was reported, not assigned. Nothing in the design separates the effect of app use from the many reasons a student's wellbeing and their app use might move together, including reverse causation: a student whose wellbeing is poor may use the app more.

**Claim ceiling:** The service may describe an observed ordering of wellbeing across self-reported usage groups in this sample. It may not claim that app use changes wellbeing, that reducing use would raise wellbeing, or that the pattern would appear in another sample.

#### What Must Be True?

Each student must contribute one independent observation. The outcome must be at least ordinal, which it is. If the result is to be described as a difference in medians rather than in ordering, the three distributions must have similar shapes - a claim that must be inspected, not assumed.

#### Defensibility Procedures

Inspect the distributions before choosing the method and record what was seen. Prespecify the method, the effect size, the pairwise comparisons, and the multiplicity adjustment. Report group sizes, five-number summaries, the overall test with its degrees of freedom and effect size, and every pairwise comparison in the family - not only the ones that reached a threshold. State the tie handling and the direction convention for the effect size.

**Next evidence priority:** A design that measures app use objectively and follows students over time, so that the temporal order of change can be observed rather than assumed.

#### Claim Audit

Repair this claim before continuing: "High app use lowers wellbeing by about 12 points, *H* = 39.57, *p* < .001." Your repair should identify a scale error, a causal error, and a missing effect size.

### Plausible Research Scenario: The Analyst Who Cleaned the Data

*This is a fictional research scenario created for teaching. Every referenced dataset is synthetic; it does not describe a real study or real participants.*

A second analyst opens the same file, notices the `outlier_flag` column, and deletes the three flagged rows before analysing. Two came from the low-use group and one from the moderate-use group. The high-use group is unchanged. The remaining file, Study 09A, has 129 rows with group sizes of 42, 43, and 44.

The analyst reports the cleaned analysis and does not mention the deletion.

#### Pause and Decide

Before reading further, predict what deleting three low observations from two of three groups will do to the low group's mean, its standard deviation, the overall test statistic, and the effect size. Say explicitly which direction you expect each to move, and then commit to whether you think "cleaning" makes a result more conservative.

#### Why This Model?

The analysis run on Study 09A is the same Kruskal-Wallis test, correctly specified for the reduced file. That is exactly why it is dangerous: nothing in the output announces that the file changed.

The deletion is a modelling decision, not a data-quality repair. The flagged values are inside the plausible range of the instrument, and no measurement error was identified. Removing them changes the estimand from "wellbeing scores among the students surveyed" to "wellbeing scores among the students surveyed excluding those with unusually low scores" - a population defined partly by the outcome.

#### What Would a Favorable Result Look Like?

There is no favorable result here, only an honest one. If deletion is genuinely justified - a documented measurement failure, an ineligible participant, a value outside the instrument's possible range - the justification exists before the analysis and is reported. If it does not, the defensible move is to run the analysis both ways and report both.

#### Best Defensible Claim

**Statistical evidence:** The cleaned analysis estimates the same rank-based quantity on a subset of the sample defined by the outcome variable.

**Causal identification:** Unchanged and still absent; deletion does not improve identification.

**Claim ceiling:** Lower than the original, not higher. A result computed on cases selected partly by their outcome values supports a narrower claim, and the narrowing must be stated.

#### What Must Be True?

For deletion to be defensible, the rule must be prespecified, applied without reference to the result, applied identically to every group, and reported. None of those conditions is met by noticing a flag column and acting on it.

#### Defensibility Procedures

Report the analysis on the complete file as the primary result. Report the deletion as a sensitivity analysis with both statistics visible. State the rule, the number of cases removed, and which groups they came from. Never present a cleaned result as the only result.

**Next evidence priority:** A prespecified data-handling plan written before collection, naming the exclusion rules and the sensitivity analyses that will accompany them.

#### Claim Audit

Explain why "we removed three outliers to be conservative" is not a defensible sentence, using the verified statistics from Study 09 and Study 09A.

\newpage

## Problems

*Do not consult the solutions until you have recorded an answer, reason, and confidence rating for every attempted item.*

### Level 1: Recall and Recognize

**Problem 13.1 — Name what ranking preserves and discards**

Replacing 132 wellbeing scores with their positions in the combined ordering preserves one property of the data and discards another. Name both, and give one consequence of each for interpretation.

**Problem 13.2 — State what the overall test compares**

Complete the sentence precisely: "The Kruskal-Wallis test asks whether ..." Then state the additional condition that would be required before the result could be described as a comparison of medians.

**Problem 13.3 — Identify the design**

Students reported their own app-use level. Name the design, state whether random assignment is present, and name one alternative explanation for an association that this design cannot exclude and that runs in the opposite direction from the obvious one.

**Problem 13.4 — Recognize the effect-size scale**

Study 09 reports jamovi epsilon-squared of 0.302, a bias-adjusted rank effect size of 0.291, and a rank-biserial correlation of 0.750 for one pair. State the range each can take, what value indicates no effect, and what each one summarizes.

### Level 2: Predict Before Clicking

**Problem 13.5 — Predict from the five-number summaries**

The low-use group has minimum 26.9, first quartile 51.8, median 55.65, third quartile 61.675, and maximum 78.0. Predict the shape of this distribution and predict whether its mean will be above or below its median. The verified mean is 56.420. Explain the apparent tension between the long lower whisker and that mean.

**Problem 13.6 — Predict the ordering**

`app_use_group` is ordinal, running low, moderate, high. The verified group medians are 55.65, 62.10, and 49.00 respectively. Predict the order of the three mean ranks and say whether a test for a linear trend across the ordered groups would represent this pattern well.

**Problem 13.7 — Predict the effect of the tie correction**

Among the 132 wellbeing scores there are 110 distinct values; 16 values occur more than once, and the largest group of identical values contains four observations. Predict whether the tie correction will raise or lower the test statistic, and predict roughly how large the adjustment will be.

**Problem 13.8 — Predict the consequence of deletion**

Two of the three flagged observations are low scores in the low-use group, whose median is already the middle of the three. Predict the direction of change in the low group's mean rank, in the overall statistic, and in the effect size when those rows are removed. State your prediction before reading Solution 13.8.

### Level 3: Calculate and Explain

**Problem 13.9 — Check the rank sums**

The three rank sums are 3029.0, 3999.5, and 1749.5. Compute their total and check it against the total of the ranks 1 through 132, which is *N*(*N* + 1) / 2. Explain what this check does and does not verify.

**Problem 13.10 — Compute a mean rank**

The moderate-use group has a rank sum of 3999.5 and 44 members. Compute its mean rank. Compute the mean rank expected if group membership were unrelated to wellbeing, using (*N* + 1) / 2, and state the size and direction of the departure.

**Problem 13.11 — Recover both omnibus rank effect sizes**

Study 09 reports *H* = 39.573 with three groups and 132 observations. First use jamovi's definition, ε² = *H* / (*N* − 1), to compute epsilon-squared. Then use (*H* − *k* + 1) / (*N* − *k*) to compute the bias-adjusted rank effect size. Explain why the second formula subtracts *k* − 1 from *H* before dividing.

**Problem 13.12 — Recover a rank-biserial correlation**

For the moderate-versus-high comparison, *U* = 1694.0 with 44 observations in each group. Using r = 2*U* / (*n*₁*n*₂) − 1, compute the rank-biserial correlation and state, in a sentence a non-statistician could read, what it means about pairs of students.

### Level 4: Read jamovi Output

**Problem 13.13 — Read the grouped descriptives**

| Group | *n* | Mean | Median | SD | Min | Q1 | Q3 | Max | Flagged |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Low | 44 | 56.420 | 55.65 | 9.461 | 26.9 | 51.800 | 61.675 | 78.0 | 2 |
| Moderate | 44 | 61.834 | 62.10 | 7.167 | 47.9 | 57.175 | 66.500 | 82.3 | 1 |
| High | 44 | 49.702 | 49.00 | 7.479 | 31.3 | 44.775 | 55.325 | 65.4 | 0 |

Describe the three distributions in words. Name the one group whose mean and standard deviation are least representative of its typical member, and give the specific numerical evidence.

**Problem 13.14 — Read the overall test**

jamovi reports χ² = 39.573 with df = 2 and *p* < .001 for the Kruskal-Wallis test, with mean ranks of 68.841, 90.898, and 39.761 for the low, moderate, and high groups. Its epsilon-squared is ε² = *H* / (*N* − 1) = 0.302. The separately calculated bias-adjusted rank effect size is (*H* − *k* + 1) / (*N* − *k*) = 0.291. Write one APA-style sentence reporting the test, and one further sentence describing the pattern that the mean ranks show.

**Problem 13.15 — Read the pairwise family**

| Comparison | *U* | *z* | *p* | Holm *p* | Rank-biserial |
| --- | --- | --- | --- | --- | --- |
| Low vs moderate | 620.5 | −2.896 | .00378 | .00378 | −0.359 |
| Low vs high | 1418.5 | 3.756 | .000173 | .000346 | 0.465 |
| Moderate vs high | 1694.0 | 6.055 | $1.41 \times 10^{-9}$ | $4.22 \times 10^{-9}$ | 0.750 |

Read the direction of each comparison from the sign of the rank-biserial correlation, given the convention that a positive value favours the first-named group. State which pair is furthest apart and which is closest, and explain why the Holm-adjusted values differ from the unadjusted ones for two comparisons but not for the third.

**Problem 13.16 — Read the two analyses side by side**

For Study 09, *H* = 39.573, jamovi ε² = 0.302, and the bias-adjusted rank effect size is 0.291, with low-group mean 56.420 and SD 9.461. For Study 09A, after deleting the three flagged rows, *H* = 41.560, jamovi ε² = 0.325, and the bias-adjusted rank effect size is 0.314, with low-group mean 57.629 and SD 7.755. State what happened to each quantity and explain in one sentence why this comparison makes the phrase "removed to be conservative" untenable.

### Level 5: Choose the Model

**Problem 13.17 — Choose the analysis and state the real reason**

Choose the comparison for the stated question and justify it from the inspected distributions. Then explain why "the variances were unequal" would be a false justification in this case, citing the specific evidence.

**Problem 13.18 — Reject the median claim**

An analyst reports: "A Kruskal-Wallis test showed that the median wellbeing score differed across app-use groups." Explain the precise sense in which this is wrong, name the assumption that would make it right, and give a defensible replacement sentence.

**Problem 13.19 — Reject the trend model**

An analyst notes that `app_use_group` is ordinal and proposes replacing the Kruskal-Wallis test with a test for a linear trend across the three ordered levels, arguing that it will have more power. Reject the proposal using the verified mean ranks, and state the circumstance in which the proposal would have been sensible.

**Problem 13.20 — Reject the unadjusted pairwise report**

An analyst runs the three pairwise Mann-Whitney comparisons, reports the two smallest *p* values, and omits the third because "it was in the same direction anyway." Give two distinct reasons this is indefensible, and name what should have been prespecified.

### Level 6: Report and Critique

**Problem 13.21 — Write the result paragraph**

Using the verified values, write a short APA-style results paragraph for Study 09. Include group sizes, a description of the distributions, the overall test with degrees of freedom and effect size, the pairwise family with its adjustment, and the observational limitation.

**Problem 13.22 — Repair a scale error**

Repair this sentence: "Students with high app use scored 12.13 points lower than students with moderate app use, *H*(2) = 39.57, *p* < .001, ε² = 0.30." The arithmetic in the sentence is correct. Explain what is nevertheless wrong and write a version that reports both quantities honestly.

**Problem 13.23 — Repair an undisclosed deletion**

An analyst reports the Study 09A results with no mention of the deletion. Write the two sentences that must be added to the methods and the one sentence that must be added to the results, and explain which of the two reported statistics should be the primary one.

**Problem 13.24 — Write the limitation**

Study 09 is correctly analysed, clearly reported, and observational. Write the three-sentence limitation it requires: one sentence on what the grouping variable is, one on the direction of any causal story, and one on what the rank-based statistics do and do not describe.

\newpage

## Solutions

### Level 1 Solutions

**Solution 13.1**

Ranking preserves the *ordering* of the observations and discards the *distances* between them. The consequence of preserving order is that any monotonic change of scale - adding a constant, multiplying by a positive number, applying a logarithm - leaves the analysis unchanged, so the result does not depend on an arbitrary scoring choice. The consequence of discarding distance is that the analysis cannot report how far apart the groups are on the wellbeing scale. A student 30 points below everyone else and a student 3 points below everyone else occupy the same rank.

**Solution 13.2**

"The Kruskal-Wallis test asks whether observations drawn from one group tend to occupy higher positions in the combined ordering than observations drawn from another." Describing the result as a comparison of medians additionally requires that the three distributions have the same shape and differ only by a location shift. Under that assumption the ordering statement and the median statement coincide; without it they can diverge, and two groups can have identical medians while one group's observations tend to be larger.

**Solution 13.3**

The design is a cross-sectional observational survey with self-reported group membership and no random assignment. Among the alternative explanations it cannot exclude, the most important is reverse causation: a student whose wellbeing is already low may use a wellbeing app more, so app use would be a consequence of low wellbeing rather than a cause of it. The data contain no temporal information that could separate the two directions.

**Solution 13.4**

jamovi epsilon-squared runs from 0 to 1, with 0 indicating no rank separation. The bias-adjusted rank effect size runs up to 1 but can be slightly negative when *H* is smaller than its null expectation; 0 occurs when *H* = *k* − 1. Both summarize omnibus separation on the rank scale rather than variability in wellbeing points. The rank-biserial correlation runs from −1 to +1, with 0 indicating no tendency; it is the difference between the proportion of cross-group pairs favouring the first-named group and the proportion favouring the second. None of the three is expressed in wellbeing points.

### Level 2 Solutions

**Solution 13.5**

The five-number summary shows an asymmetric distribution. The lower whisker is long (55.65 − 26.9 = 28.75) while the upper whisker is shorter (78.0 − 55.65 = 22.35), which indicates a tail extending toward low scores. Within the box, however, the median sits closer to the first quartile (55.65 − 51.8 = 3.85) than to the third (61.675 − 55.65 = 6.025), so the central half of the data leans the other way.

That is the resolution of the apparent tension: the mean of 56.420 lies slightly *above* the median of 55.65 because the right-leaning central mass outweighs the two extreme low observations in this sample. A long tail does not determine the sign of the mean-median difference by itself; it determines how unstable that difference is. Transfer cue: a five-number summary describes shape more reliably than any single comparison of mean and median.

**Solution 13.6**

The mean ranks should order moderate highest, then low, then high - the same order as the medians, because ranking preserves ordering. The verified mean ranks are 90.898, 68.841, and 39.761, confirming it.

A test for a linear trend across low, moderate, high would represent this pattern badly. The pattern rises from low to moderate and then falls sharply to high; a linear trend model would average those two opposite movements into a single slope and could report a weak or absent trend from data showing a strong non-monotonic pattern. Ordinal grouping permits a trend test; it does not justify one.

**Solution 13.7**

The tie correction divides the uncorrected statistic by a quantity slightly less than 1, so it raises the statistic. With only 16 tied values among 110 distinct values and no tie group larger than four, the correction is very small. The verified correction factor is 0.999903, which raises the statistic from 39.569 to 39.573 - a change in the fourth decimal place that alters no conclusion. Reporting the tie handling still matters, because the size of the adjustment is a fact about this dataset and not a general property.

**Solution 13.8**

Removing two low scores from the low group raises that group's mean and mean rank and shortens its lower tail, which reduces its standard deviation. Removing one flagged value from the moderate group changes it slightly. The high group is untouched and remains lowest.

The consequence is that the three groups become *more* separated, not less. The verified values confirm it: the low group's mean rises from 56.420 to 57.629 and its standard deviation falls from 9.461 to 7.755; the overall statistic rises from 39.573 to 41.560; jamovi epsilon-squared rises from 0.302 to 0.325; and the bias-adjusted rank effect size rises from 0.291 to 0.314. Deletion made the finding stronger. Anyone who assumed that removing outliers is a cautious act has just been shown otherwise.

### Level 3 Solutions

**Solution 13.9**

3029.0 + 3999.5 + 1749.5 = 8778.0. The total of the ranks 1 through 132 is 132 × 133 / 2 = 8778. They agree.

The check verifies that every observation received exactly one rank and that tied observations were assigned average ranks summing correctly - in other words, that the ranking step was performed on the intended 132 rows. It does not verify that the groups were assigned correctly, that the right variable was ranked, or that the test statistic was computed properly. It is an arithmetic guard, not a validation of the analysis.

**Solution 13.10**

Mean rank = 3999.5 / 44 = 90.898. Under no association, every group's mean rank would be near the average of all ranks, (*N* + 1) / 2 = 133 / 2 = 66.5. The moderate group sits 24.4 rank positions above that reference, and it sits above it while the high group sits 26.7 below it. The two departures are of similar magnitude in opposite directions, which is the numerical signature of the non-monotonic pattern.

**Solution 13.11**

jamovi ε² = 39.573 / (132 − 1) = 39.573 / 131 = 0.302.

The bias-adjusted rank effect size is (39.573 − 3 + 1) / (132 − 3) = 37.573 / 129 = 0.291. The second formula subtracts *k* − 1 because that is the expected value of *H* when there is no association at all: with *k* groups, the statistic follows approximately a chi-square distribution with *k* − 1 degrees of freedom under the null, and a chi-square variable has expectation equal to its degrees of freedom. Subtracting it centres this adjusted measure at zero when nothing is happening. The two quantities must be named separately rather than assigning both formulas the same label.

**Solution 13.12**

r = 2 × 1694.0 / (44 × 44) − 1 = 3388 / 1936 − 1 = 1.750 − 1 = 0.750.

In plain language: if you pick one student at random from the moderate-use group and one at random from the high-use group, the moderate student has the higher wellbeing score in about 87.5 percent of such pairs and the high student in about 12.5 percent, with ties split. The correlation of 0.750 is the difference between those two proportions. It is a statement about pairs, not about points on the wellbeing scale.

### Level 4 Solutions

**Solution 13.13**

The moderate-use group has the highest scores and the tightest distribution: a median of 62.10, an interquartile range of 9.325, and a minimum of 47.9 that is not far below its box. The high-use group is shifted downward as a whole - its third quartile of 55.325 sits below the moderate group's median - and its spread is similar. The low-use group's box overlaps the other two, but it carries a much longer lower tail, reaching 26.9 against a first quartile of 51.8.

The low-use group's mean and standard deviation are the least representative of its typical member. Its standard deviation of 9.461 is 26 to 32 percent larger than either other group's, yet its interquartile range of 9.875 is *smaller* than the high group's 10.550 and only about 6 percent larger than the moderate group's 9.325. A spread statistic that reacts strongly to the tails and a spread statistic that ignores them point in opposite directions; that disagreement is the diagnostic, and it says the standard deviation is being driven by observations outside the central half of the data.

**Solution 13.14**

Wellbeing scores differed across the three app-use groups, χ²(2, *N* = 132) = 39.57, *p* < .001, jamovi ε² = 0.302 (bias-adjusted rank effect size = 0.291). Mean ranks were highest in the moderate-use group (90.90), intermediate in the low-use group (68.84), and lowest in the high-use group (39.76), so the pattern across the ordered usage levels rises and then falls rather than running in a single direction.

#### Study in the Larger Evidence Program: Wellbeing and Reported App Use

- **What this study adds:** A reproducible rank-based estimate of how wellbeing orders across three self-reported usage levels, together with a demonstration that the pattern is not monotonic.
- **What it cannot settle:** Whether app use affects wellbeing, whether wellbeing affects app use, or whether a third factor produces both. Cross-sectional data contain no temporal ordering.
- **Causal-support role:** Weak consistency evidence at best. No responsiveness evidence is present because nothing was deliberately changed, and no mechanism was measured.
- **Next evidence priority:** Objective usage logging with repeated wellbeing measurement, so that within-person change in usage and in wellbeing can be observed in sequence rather than inferred from one occasion.

**Solution 13.15**

The rank-biserial correlation is negative for low versus moderate (−0.359), so the moderate group sits higher. It is positive for low versus high (0.465) and for moderate versus high (0.750), so the low and moderate groups both sit above the high group.

The moderate and high groups are furthest apart, with a rank-biserial of 0.750 - the largest of the three. The low and moderate groups are closest, with a magnitude of 0.359.

Holm's adjustment multiplies the smallest *p* value by the number of comparisons, the next by one fewer, and so on, taking a running maximum. The largest *p* value in the family is multiplied by one and is therefore unchanged, which is why the low-versus-moderate comparison shows the same value at .004 before and after adjustment. The other two, being smaller, are multiplied by three and two respectively. Holm adjusts every comparison in the family, including the one whose value does not move.

**Solution 13.16**

*H* rose from 39.573 to 41.560. jamovi epsilon-squared rose from 0.302 to 0.325, and the bias-adjusted rank effect size rose from 0.291 to 0.314. The low group's mean rose from 56.420 to 57.629 and its standard deviation fell from 9.461 to 7.755. Every quantity moved in the direction of a larger, tidier, more separated effect.

"Removed to be conservative" is untenable because it claims a direction the numbers contradict. Deleting the flagged observations removed the cases that were pulling the low group down toward the high group, which increased the separation between groups and shrank the within-group variability that the test compares it against. Deletion is not conservative or liberal by nature; its direction depends entirely on where the deleted points sat, which is precisely why the rule must be fixed before anyone looks.

### Level 5 Solutions

**Solution 13.17**

A Kruskal-Wallis test on the three independent groups is the defensible choice, followed by prespecified pairwise Mann-Whitney comparisons with a multiplicity adjustment. The justification is the shape of the outcome: a long lower tail in one group and extreme low values that make the arithmetic mean a poor summary of a typical student. The question is about which group's students tend to score higher, and a rank method estimates exactly that.

"The variances were unequal" would be a false justification. The three standard deviations are 9.461, 7.167, and 7.479, and a median-centred Brown-Forsythe test gives *F*(2, 129) = 0.54, *p* = .583 - no evidence of unequal spread. Two things follow. First, the stated reason must match the inspected evidence, or the reader cannot audit the decision. Second, unequal variance would not have been a reason for a rank method anyway: the Kruskal-Wallis test is not a remedy for heteroscedasticity, and when spreads differ substantially it can detect that difference in spread rather than the difference in location the analyst intended to study.

**Solution 13.18**

The sentence attributes to the test a quantity the test does not target. Kruskal-Wallis compares whether observations in one group tend to sit higher in the combined ordering; medians are not in the statistic. The claim becomes correct only under the additional assumption that the three distributions have the same shape and differ by a location shift - an assumption that must be inspected and stated, and one that the differing tail lengths here make debatable.

Defensible replacement: "Wellbeing scores tended to differ across app-use groups, χ²(2, *N* = 132) = 39.57, *p* < .001, jamovi ε² = 0.302. Group medians were 55.65, 62.10, and 49.00 for the low, moderate, and high groups respectively." The test result and the descriptive medians are both reported, and neither is presented as the other.

**Solution 13.19**

The verified mean ranks are 68.84 for low, 90.90 for moderate, and 39.76 for high. The pattern rises by 22 rank positions and then falls by 51. A linear trend model fitted across the ordered levels would summarise those opposite movements as one slope, and would describe the data badly no matter which slope it produced. A trend test can also lose power precisely where a non-monotonic pattern is strongest, so the appeal to power fails on its own terms.

The proposal would have been sensible if a monotonic dose-response relationship had been the prespecified hypothesis and the inspected data were consistent with it. Choosing a trend test *after* seeing that the grouping variable is ordinal, without checking whether the pattern is monotonic, substitutes a property of the variable's label for a property of the data.

**Solution 13.20**

First, the family of comparisons is defined by the analysis plan, not by the results. Omitting one comparison after seeing it makes the reported Holm adjustment wrong, because Holm's procedure depends on the number of comparisons in the family; two reported values adjusted as if from a family of three are not interpretable as either.

Second, "in the same direction anyway" is a claim about the result, and using it as a reason to omit the comparison means the reporting decision was made after and because of the outcome. A reader cannot then distinguish the reported family from a family selected to look tidy.

What should have been prespecified: which pairwise comparisons would be made, in what direction, with which effect size, and under which multiplicity adjustment - all recorded before the pairwise output was produced.

#### Study in the Larger Evidence Program: The Cleaned Analysis

- **What this study adds:** A concrete demonstration that deleting flagged observations is not a conservative act. Removing three flagged values raised the statistic from 39.573 to 41.560, jamovi epsilon-squared from 0.302 to 0.325, and the bias-adjusted rank effect size from 0.291 to 0.314.
- **What it cannot settle:** Anything the original analysis could not settle. Deletion changes the sample, never the design.
- **Causal-support role:** None. The reduced analysis is observational for exactly the same reasons as the full one, and its population is now defined partly by the outcome.
- **Next evidence priority:** A prespecified data-handling plan written before collection, naming exclusion rules and the sensitivity analyses that will be reported alongside them.

### Level 6 Solutions

**Solution 13.21**

Wellbeing scores were compared across three self-reported app-use groups (*n* = 44 per group). Distributions were asymmetric, with a long lower tail in the low-use group (minimum 26.9 against a first quartile of 51.8), so a rank-based comparison was prespecified. Scores differed across groups, χ²(2, *N* = 132) = 39.57, *p* < .001, jamovi ε² = 0.302 (bias-adjusted rank effect size = 0.291), with mean ranks of 68.84, 90.90, and 39.76 for the low, moderate, and high groups. All three pairwise Mann-Whitney comparisons were conducted with Holm adjustment: moderate exceeded low (*U* = 620.5, *p* = .004, rank-biserial = −0.359 in the low-minus-moderate direction), low exceeded high (*U* = 1418.5, *p* < .001, rank-biserial = 0.465), and moderate exceeded high (*U* = 1694.0, *p* < .001, rank-biserial = 0.750). Ties received average ranks and the tie correction factor was 0.9999. Because app-use group was self-reported rather than assigned, these results describe an observed ordering and do not establish that app use affects wellbeing.

**Solution 13.22**

The arithmetic is right: 61.834 − 49.702 = 12.13. Two things are nevertheless wrong.

The first is a scale mismatch. The 12.13-point figure is a difference between arithmetic means, and it is being reported as though the Kruskal-Wallis statistic tested it. It did not. The rank-based analysis produced no quantity in wellbeing points, and the mean difference it is attached to was never subjected to the test whose statistic follows it.

The second is that attaching a group-level descriptive difference to an omnibus test across three groups implies that this specific pair was tested by that statistic. It was not; the pairwise comparison is a separate analysis with its own result.

Honest version: "Wellbeing scores tended to differ across app-use groups, χ²(2, *N* = 132) = 39.57, *p* < .001, jamovi ε² = 0.302. The moderate-use and high-use groups differed in the prespecified pairwise comparison, *U* = 1694.0, Holm-adjusted *p* < .001, rank-biserial = 0.750; descriptively, their means were 61.83 and 49.70 and their medians 62.10 and 49.00."

**Solution 13.23**

To the methods: "Three observations carrying the file's outlier flag were removed before analysis: two from the low-use group and one from the moderate-use group. The removal rule was applied after the data were inspected and was not prespecified."

To the results: "The analysis of the complete file gave χ²(2, *N* = 132) = 39.57, *p* < .001, jamovi ε² = 0.302 (bias-adjusted rank effect size = 0.291); the analysis after removal gave χ²(2, *N* = 129) = 41.56, *p* < .001, jamovi ε² = 0.325 (bias-adjusted rank effect size = 0.314)."

The complete-file analysis should be the primary result. It estimates the quantity that was defined before anyone looked at the data, on the sample that was actually collected. The reduced analysis is a sensitivity check reported alongside it. Reversing that order would make an unplanned, outcome-dependent exclusion the basis of the headline claim, and would leave the reader unable to see that the exclusion increased the effect.

**Solution 13.24**

"App-use group was self-reported at a single occasion and was not assigned, so the three groups may differ in many ways besides how much they use the app. The design contains no temporal ordering, so it cannot distinguish an effect of app use on wellbeing from an effect of wellbeing on app use, nor from a third factor that influences both. The rank-based statistics describe how the groups order relative to one another and how strongly group membership accounts for that ordering; they do not estimate a difference in wellbeing points, and the group means and medians reported alongside them are descriptive summaries rather than tested quantities."

\newpage
