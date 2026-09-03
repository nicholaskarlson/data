# PART V

## Designs that do not randomize

\newpage

# Unit 14: Quasi-Experimental Comparison and Covariate Adjustment

*Open educational resource licensed CC BY 4.0. All research scenarios are fictional and all datasets are synthetic. Complete the problems before consulting the worked solutions.*

## Unit Purpose

Some groups cannot be assigned, even in principle. A child cannot be randomized into an age band, and no improvement in funding, ethics review, or sample size will change that. A quasi-experimental comparison is therefore not an experiment with a missing feature; it is a different kind of study whose claim ceiling is set by what the grouping variable is. Adding a covariate does not raise that ceiling. It changes which comparison the coefficient describes, and whether that change helps depends on where the covariate sits in the causal order. This unit develops the habit of asking what a covariate *is* before asking what adjusting for it does.

## Learning Objectives

After completing this unit, a learner should be able to:

- distinguish a grouping variable that was assigned from one that was observed, and one that cannot be assigned at all;
- read an analysis of variance table and identify the quantity each row contributes;
- distinguish a multiplicity adjustment from a covariate adjustment, both of which are called "adjustment";
- explain what a covariate-adjusted group coefficient estimates and how it differs from the unadjusted difference;
- decide whether adjusting for a variable reduces bias or removes part of the effect of interest, using the causal order rather than the fit statistics;
- check the conditions an analysis of covariance requires, including comparable slopes across groups; and
- write a limitation that names the specific alternative explanations a quasi-experimental design leaves open.

## Decision Map

Ask these questions in order:

1. What is the scientific question, and is the grouping variable assigned, observed, or unassignable?
2. What are the cases, and how many observations does each contribute?
3. What is the unadjusted comparison, and what does it estimate?
4. For each candidate covariate: was it measured before the grouping variable, caused by it, or neither?
5. What quantity would the adjusted coefficient estimate, and is that the quantity the question asked for?
6. What conditions does the adjusted model require, and does the evidence support them?
7. What does the design identify, what is the claim ceiling, and what evidence should come next?

## Study Files

The primary dataset is `study_10_developmental_emotion_recognition.csv`. The teaching variant is a subset of the same file, reproducible in jamovi with a row filter on `age_group`. Public CSV files, dictionaries, and verified result records are available at [https://github.com/nicholaskarlson/data](https://github.com/nicholaskarlson/data).

| Study | Data structure | Primary outcome | Unit role |
| --- | --- | --- | --- |
| Study 10 | 144 children, 48 in each of three age bands | Emotion recognition accuracy | Three-group quasi-experimental comparison with a covariate |
| Study 10A | The 96 children in the 6-7 and 10-11 bands | Emotion recognition accuracy | Two-group contrast; the covariate imbalance made visible |

## Plausible Research Scenarios

The scenarios create decisions rather than documenting real research. At each Pause and Decide, stop reading and write an answer, reason, and confidence rating.

### Plausible Research Scenario: Emotion Recognition Across Three Age Bands

*This is a fictional research scenario created for teaching. Every referenced dataset is synthetic; it does not describe a real study or real participants.*

A fictional developmental research group tests 144 children on a task that measures how accurately they identify emotional expressions. Forty-eight children are in each of three age bands: 6 to 7, 8 to 9, and 10 to 11 years. Each child completes the task once and contributes one accuracy score. A vocabulary score is also recorded for every child.

The research question is: **how does emotion recognition accuracy differ across these three age bands?**

Age band was not assigned and could not have been. The children arrived at their ages by living, and every difference that accompanies being older - schooling, language, social experience, attention span, familiarity with tests - travels with the grouping variable.

#### Pause and Decide

Before reading further, name the case, state whether the design is experimental, decide what quantity the three-group comparison estimates, and write down what the phrase "the effect of age" could and could not mean here. Then decide, before you see any output, whether you would adjust for vocabulary and say why.

#### Why This Model?

A one-way analysis of variance across the three age bands estimates the differences among the three group means, and prespecified pairwise comparisons with a multiplicity adjustment locate where those differences sit. The model matches the data structure: one score per child, three independent groups, a quantitative outcome.

The model is correctly specified and the design identifies nothing causal. Those two statements are compatible and are the heart of this unit. The analysis estimates how accuracy differs across age bands in the represented sample. It does not isolate a mechanism, because no mechanism was manipulated and none could be.

Multiplicity matters because three pairwise comparisons are a family. The unit uses Bonferroni adjustment, which multiplies each comparison's *p* value by the number of comparisons and widens the confidence intervals to match. The word "adjustment" here means something entirely different from what it will mean in the second scenario, and the difference is worth fixing in mind now: a multiplicity adjustment changes how a family of results is judged, and changes no estimate; a covariate adjustment changes the estimate itself.

#### What Would a Favorable Result Look Like?

The group would hope to see accuracy increasing across the age bands with intervals precise enough to distinguish adjacent bands from one another. A result in which the two older bands cannot be distinguished would also be informative: it would suggest that whatever changes between 6 and 9 has largely finished by 9, which is a substantive finding about the shape of development rather than a failure.

#### Best Defensible Claim

**Statistical evidence:** The analysis estimates differences in mean accuracy across three age bands, with intervals and a multiplicity-adjusted family of pairwise comparisons.

**Causal identification:** None beyond the association. Age band cannot be assigned, so nothing separates chronological age from everything that accompanies it.

**Claim ceiling:** The group may describe how accuracy differs across age bands among the represented children. It may not claim that age *causes* the difference in any sense that isolates age from schooling, language, or experience, and it may not describe the pattern as within-child development, because no child was measured twice.

#### What Must Be True?

Each child contributes one independent score. The task must measure the same construct comparably at all three ages - a stronger requirement than it looks, because an instrument can be harder to understand for younger children in ways unrelated to emotion recognition. For the pooled-variance model, spreads should be reasonably similar and residuals reasonably well behaved.

#### Defensibility Procedures

Prespecify the outcome, the comparisons, and the multiplicity adjustment. Report all three pairwise comparisons with adjusted *p* values and family-wise intervals, not only the ones that cross a threshold. Report the assumption checks. State explicitly that the design is cross-sectional and that age band is not an assigned condition.

**Next evidence priority:** A longitudinal design measuring the same children more than once, which would replace between-child differences with within-child change and would separate age from cohort.

#### Claim Audit

Repair this claim before continuing: "Being older causes a 13-point improvement in emotion recognition." Your repair should address both the causal language and the phrase "improvement," which implies within-child change that this design never observed.

### Plausible Research Scenario: The Analyst Who Controlled for Vocabulary

*This is a fictional research scenario created for teaching. Every referenced dataset is synthetic; it does not describe a real study or real participants.*

A second analyst observes that vocabulary scores differ across the three age bands and that vocabulary correlates with accuracy. Concerned that the age comparison is "confounded by language ability," the analyst adds vocabulary as a covariate and reports the adjusted age coefficients as the corrected result.

The adjusted coefficients are smaller than the unadjusted differences. The analyst reports this as evidence that part of the apparent age effect was really a vocabulary effect.

Study 10A restricts the same file to the youngest and oldest bands so that the two quantities can be compared directly.

#### Pause and Decide

Before reading further, decide what vocabulary *is* in the causal order of this study. Was it measured before age band? Could age band have caused it? Could it have caused age band? Then predict what will happen to the age coefficients after adjustment, and decide in advance whether a reduction would be good news or bad news.

#### Why This Model?

Analysis of covariance is a correctly specified regression model here. It fits, its residuals behave, and its coefficients have small standard errors. None of that tells the analyst whether the coefficients answer the question.

The decisive fact is the causal order. Age can cause vocabulary; vocabulary cannot cause age. Vocabulary is therefore a **consequence of the grouping variable**, not a pre-existing confounder. Adjusting for a consequence removes part of the very effect being estimated. The adjusted age coefficient answers a different question: "how much do accuracy scores differ between age bands among children who happen to have the same vocabulary score?" That is a legitimate question - it is roughly a question about the part of the age difference that does not travel through vocabulary - but it is not the total developmental difference, and it must not be labelled a corrected version of it.

The general rule is worth stating plainly. Adjustment reduces bias when the covariate is a common cause of the grouping variable and the outcome, measured before both. Adjustment introduces bias, or answers a different question, when the covariate is caused by the grouping variable, or is caused by both the grouping variable and the outcome. No fit statistic distinguishes these cases. Only an argument about the causal order does, and that argument comes from subject knowledge, not from the data.

#### What Would a Favorable Result Look Like?

There is no favorable result here, only a correctly labelled one. Reporting both the unadjusted difference and the adjusted coefficient, saying what each estimates, is the outcome to aim for.

#### Best Defensible Claim

**Statistical evidence:** The unadjusted comparison estimates the total difference in accuracy between age bands. The adjusted coefficient estimates the difference remaining after holding vocabulary fixed, which is a different quantity.

**Causal identification:** Adjustment does not create identification. The design is quasi-experimental before and after.

**Claim ceiling:** The analyst may report both quantities and name each. The analyst may not present the adjusted coefficient as a corrected or purified age effect, and may not claim to have removed confounding by adjusting for a variable that age produces.

#### What Must Be True?

For the model to be interpretable at all, the relationship between vocabulary and accuracy should be similar in each age band, so that a single covariate slope is a reasonable summary. That condition can be tested by adding an interaction between age band and vocabulary. Passing the test does not make the adjustment appropriate; it only removes one reason it would be uninterpretable.

#### Defensibility Procedures

State the causal role assumed for every covariate before fitting. Report unadjusted and adjusted estimates together. Report the covariate's own coefficient and the group differences on the covariate, so the reader can see how much the groups differ on it. Test and report the homogeneity of slopes. Never describe an adjusted estimate as the "true" effect.

**Next evidence priority:** A design in which a genuinely manipulable variable is assigned - for example, a task instruction or a training exposure - so that a causal contrast exists to estimate.

#### Claim Audit

Explain why "after controlling for vocabulary, age still has a significant effect" is a misleading sentence in this study even though every number in the underlying model is correct.

\newpage

## Problems

*Do not consult the solutions until you have recorded an answer, reason, and confidence rating for every attempted item.*

### Level 1: Recall and Recognize

**Problem 14.1 — Classify the grouping variable**

Age band in Study 10 is not randomly assigned. Distinguish three cases: a variable that was not assigned but could have been, a variable that was not assigned and could not have been, and a variable that was assigned. Place age band, message condition from Unit 12, and app-use group from Unit 13 into those categories, and say which category has the lowest claim ceiling.

**Problem 14.2 — Name the two adjustments**

This unit uses the word "adjustment" for two different operations. Name both, state what each one changes, and state what each one leaves unchanged.

**Problem 14.3 — State what an ANCOVA coefficient estimates**

Write, in one sentence and without formulas, what the coefficient on `age_10_11` estimates in a model that also contains vocabulary. Then state what it does *not* estimate.

**Problem 14.4 — Recognize the covariate's causal position**

Vocabulary was recorded at the same session as the accuracy task. State whether it could be a common cause of age band and accuracy, whether it could be a consequence of age band, and what follows for the interpretation of an adjusted age coefficient.

### Level 2: Predict Before Clicking

**Problem 14.5 — Predict the direction and rough size**

The three group means for accuracy are 59.354, 69.300, and 72.360 for the 6-7, 8-9, and 10-11 bands. Predict which pairwise contrast will be largest, which will be smallest, and whether the smallest one will survive a Bonferroni adjustment across three comparisons.

**Problem 14.6 — Predict the covariate imbalance**

The three group means for vocabulary are 41.269, 47.967, and 53.710. Predict whether vocabulary is balanced across age bands, and predict what that imbalance implies for how much the age coefficients will move when vocabulary enters the model.

**Problem 14.7 — Predict the direction of the adjustment**

Vocabulary is higher in older bands and is positively related to accuracy. Predict whether adjusting for vocabulary will make the age coefficients larger or smaller than the unadjusted differences, and explain the mechanism in one sentence.

**Problem 14.8 — Predict what adjustment cannot do**

Before seeing any output, state one thing the adjusted model will improve and one thing it cannot improve. Be specific: name a statistic for the first and a design property for the second.

### Level 3: Calculate and Explain

**Problem 14.9 — Complete the ANOVA table**

The between-groups sum of squares is 4439.173 with 2 degrees of freedom; the within-groups sum of squares is 7274.354 with 141 degrees of freedom. Compute both mean squares and the *F* ratio, and state what the denominator mean square represents.

**Problem 14.10 — Compute the effect size and compare two versions**

Using SS-between 4439.173 and SS-total 11713.527, compute eta-squared. The verified omega-squared is 0.369. Explain in one sentence why omega-squared is smaller and which of the two is the less optimistic estimate of the population value.

**Problem 14.11 — Recover a pairwise standard error and statistic**

The pooled within-groups mean square is 51.591 and each group contains 48 children. Compute the standard error of a difference between two group means using SE = √(MS-within × (1/*n*₁ + 1/*n*₂)). Then compute the *t* statistic for the 8-9 versus 10-11 contrast, whose mean difference is −3.060.

**Problem 14.12 — Compare an adjusted and an unadjusted difference**

The unadjusted difference between the 6-7 and 10-11 bands is 13.006 points. The coefficient on `age_10_11` in the model containing vocabulary is 8.917. Compute the reduction in points and as a percentage of the unadjusted difference, and state which of the two numbers answers the question "how much does accuracy differ between six-year-olds and ten-year-olds?"

### Level 4: Read jamovi Output

**Problem 14.13 — Read the ANOVA and its checks**

| Source | SS | df | MS | *F* | *p* | η² | ω² |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Age band | 4439.173 | 2 | 2219.586 | 43.02 | < .001 | 0.379 | 0.369 |
| Residual | 7274.354 | 141 | 51.591 | | | | |

A median-centred Brown-Forsythe test gives *F*(2, 141) = 0.77, *p* = .467, and a Shapiro-Wilk test on the residuals gives *W* = 0.988, *p* = .247. Write one sentence reporting the omnibus result and one sentence stating what the two checks do and do not license.

**Problem 14.14 — Read the pairwise family**

| Contrast | Mean difference | SE | *t* | Raw *p* | Bonferroni *p* | 95% family-wise CI |
| --- | --- | --- | --- | --- | --- | --- |
| 6-7 vs 8-9 | −9.946 | 1.466 | −6.78 | < .001 | < .001 | [−13.498, −6.393] |
| 6-7 vs 10-11 | −13.006 | 1.466 | −8.87 | < .001 | < .001 | [−16.559, −9.454] |
| 8-9 vs 10-11 | −3.060 | 1.466 | −2.09 | .039 | .116 | [−6.613, 0.492] |

Describe what happened to the third contrast and explain why its interval contains zero while its raw *p* value does not exceed .05. State what a reader should conclude about the two older bands.

**Problem 14.15 — Read the covariate model**

| Term | *b* | SE | *t* | *p* | 95% CI | β |
| --- | --- | --- | --- | --- | --- | --- |
| Intercept | 45.791 | 3.500 | 13.08 | < .001 | [38.871, 52.712] | |
| Age 8-9 | 7.745 | 1.495 | 5.18 | < .001 | [4.788, 10.701] | 0.405 |
| Age 10-11 | 8.917 | 1.722 | 5.18 | < .001 | [5.513, 12.321] | 0.466 |
| Vocabulary | 0.329 | 0.081 | 4.04 | < .001 | [0.168, 0.490] | 0.315 |

The model has *R*² = 0.444, adjusted *R*² = 0.432, *F*(3, 140) = 37.23, *p* < .001. The reference band is 6-7. Read the vocabulary coefficient in its own units, then state what the `age_10_11` coefficient of 8.917 describes and how it differs from the 13.006 reported in the previous table.

**Problem 14.16 — Read the slope-homogeneity check**

Adding an age-band by vocabulary interaction to the model gives *F*(2, 138) = 0.67, *p* = .516. The within-band correlations between vocabulary and accuracy are 0.221, 0.403, and 0.322 for the 6-7, 8-9, and 10-11 bands. State what the interaction test licenses, and explain why the three differing correlations are not in conflict with it.

### Level 5: Choose the Model

**Problem 14.17 — Choose the primary analysis**

The question is how accuracy differs across three age bands, with one score per child. Choose the primary analysis and the follow-up procedure, and justify both from the data structure. Then state what you would report as the primary estimate and why.

**Problem 14.18 — Reject the covariate as a correction**

An analyst argues that the adjusted coefficient of 8.917 is the "real" age effect because the unadjusted 13.006 is contaminated by vocabulary. Reject the argument. Your rejection must identify the causal position of vocabulary and say what quantity 8.917 does estimate.

**Problem 14.19 — Reject the reversed adjustment**

A different analyst proposes running the model the other way around: predicting vocabulary from age band while adjusting for emotion accuracy, "to see which one is really driving it." Explain why this cannot arbitrate the question, and name the general error the proposal commits.

**Problem 14.20 — Choose what to do about the third contrast**

The 8-9 versus 10-11 contrast has a raw *p* of .039 and a Bonferroni-adjusted *p* of .116, with a family-wise interval of [−6.613, 0.492]. An analyst proposes reporting the raw *p* value because the comparison "was of primary interest all along." Decide whether that is defensible, state the condition under which it would be, and write the sentence that should be reported either way.

### Level 6: Report and Critique

**Problem 14.21 — Write the result paragraph**

Using the verified values, write an APA-style results paragraph for the unadjusted analysis of Study 10. Include group descriptives, the omnibus test with effect size, the multiplicity-adjusted pairwise family, the assumption checks, and one sentence on what the design permits.

**Problem 14.22 — Write the paragraph that reports both models honestly**

Write the short paragraph that reports the unadjusted and adjusted analyses together. It must name what each quantity estimates, must not describe either as the corrected version of the other, and must include the covariate imbalance across bands.

**Problem 14.23 — Repair a within-child claim**

Repair this sentence: "Emotion recognition improved by 13.01 points between ages six and ten, *F*(2, 141) = 43.02, *p* < .001." Identify every distinct error, including one about what was measured and one about which comparison the statistic refers to.

**Problem 14.24 — Write the quasi-experimental limitation**

Write the three-sentence limitation for Study 10. One sentence must name at least two specific alternative explanations that travel with age band; one must address the cross-sectional structure; one must address the measurement instrument.

\newpage

## Solutions

### Level 1 Solutions

**Solution 14.1**

Message condition in Unit 12 was assigned. App-use group in Unit 13 was not assigned but could in principle be assigned in a different study, since a researcher could allocate people to a usage regimen. Age band in Study 10 was not assigned and cannot be: no procedure allocates a child to being seven.

The lowest claim ceiling belongs to the unassignable variable, and it is lowest in a permanent way. An observational grouping like app use can be raised toward a causal claim by a future randomized study; age band cannot, because there is no counterfactual in which the same child is simultaneously six and ten at one moment. Studies of age therefore change what they estimate - moving to within-child change over time - rather than improving how they estimate the same thing.

**Solution 14.2**

*Multiplicity adjustment* changes the criterion applied to a family of comparisons. It rescales *p* values and widens intervals to control the family-wise error rate. It leaves every point estimate unchanged: the mean difference of −3.060 is the same number before and after Bonferroni.

*Covariate adjustment* changes the estimate itself. Adding vocabulary to the model changes the age coefficient from 13.006 to 8.917 because it is now estimating a different quantity. It says nothing about error rates.

Sharing one English word for these two operations is a persistent source of confusion, and a results section should make clear which is meant.

**Solution 14.3**

The coefficient on `age_10_11` estimates the average difference in accuracy between children in the 10-11 band and children in the 6-7 reference band, among children with the same vocabulary score.

It does not estimate the total difference in accuracy between children of those two ages, because part of that total difference operates through the vocabulary that older children have.

**Solution 14.4**

Vocabulary cannot be a common cause of age band and accuracy, because nothing can cause a child's age. It can be, and in a developmental study almost certainly is, a consequence of age band: older children have larger vocabularies partly because they are older.

What follows is that adjusting for vocabulary conditions on a variable that lies between the grouping variable and the outcome. The adjusted coefficient therefore estimates the portion of the age difference that does not operate through vocabulary, rather than a de-confounded age effect. Calling it "controlling for" a confounder misdescribes both the operation and the result.

### Level 2 Solutions

**Solution 14.5**

The largest contrast is 6-7 versus 10-11, at 72.360 − 59.354 = 13.006 points. The smallest is 8-9 versus 10-11, at 72.360 − 69.300 = 3.060 points. With a standard error near 1.47, the smallest contrast gives a *t* near 2.1, which is around the two-sided .05 boundary unadjusted and will not survive multiplication by three. The verified values confirm it: raw *p* = .039, Bonferroni *p* = .116.

**Solution 14.6**

Vocabulary is strongly unbalanced: 41.269, 47.967, and 53.710, a spread of 12.44 points across bands, and a one-way analysis of variance on vocabulary alone gives *F*(2, 141) = 37.36, *p* < .001, η² = 0.346.

A covariate that differs this much across groups and is related to the outcome will move the group coefficients substantially when it is added. That is a statement about arithmetic, not about correctness: large movement is what happens when the covariate carries much of the same information as the grouping variable, and it is equally consistent with removing confounding and with removing part of the effect.

**Solution 14.7**

The coefficients will get smaller. Older bands have higher vocabulary, and higher vocabulary is associated with higher accuracy, so part of the raw accuracy gap between bands is accompanied by the vocabulary gap. Holding vocabulary fixed removes that accompanying part, leaving a smaller age coefficient. The verified reduction is from 13.006 to 8.917 for the oldest band.

**Solution 14.8**

The adjusted model will improve the residual mean square, and with it the precision of the estimates: the residual mean square falls from 51.591 to 46.540 when vocabulary is added, because vocabulary explains variation that was previously unexplained.

It cannot improve identification. Age band remains unassigned and unassignable after adjustment exactly as before, so no coefficient in the adjusted model is a causal effect of age. A better-fitting model on an unidentified design is a more precise estimate of an associational quantity.

### Level 3 Solutions

**Solution 14.9**

MS-between = 4439.173 / 2 = 2219.586. MS-within = 7274.354 / 141 = 51.591. *F* = 2219.586 / 51.591 = 43.02.

The denominator mean square represents variation among children *within* age bands - differences between children of the same age. It is the yardstick against which between-band variation is judged: the *F* ratio asks how large the differences among band means are relative to the differences among children who share a band.

**Solution 14.10**

η² = 4439.173 / 11713.527 = 0.379.

Omega-squared is smaller (0.369) because it subtracts the variation the between-groups sum of squares would be expected to contain even if the population means were identical. Eta-squared describes the sample and is biased upward as an estimate of the population value; omega-squared corrects for that bias and is the less optimistic of the two. With 48 children per band the correction is small; in a small study the gap can be substantial.

**Solution 14.11**

SE = √(51.591 × (1/48 + 1/48)) = √(51.591 × 0.0416667) = √2.14963 = 1.466.

*t* = −3.060 / 1.466 = −2.087, on 141 degrees of freedom. Note that the standard error uses the pooled within-groups mean square from all three bands, not only the two being compared, which is why every pairwise contrast in this balanced design shares the same standard error of 1.466.

**Solution 14.12**

Reduction = 13.006 − 8.917 = 4.089 points, which is 4.089 / 13.006 = 31.4 percent of the unadjusted difference.

The question "how much does accuracy differ between six-year-olds and ten-year-olds?" is answered by 13.006. That is the total observed difference between the two bands. The 8.917 answers a narrower question about children matched on vocabulary, which is not a group of children that the original question was about. Neither number is wrong; using one to answer the other's question is.

A useful cross-check: restricting the file to those two bands alone (Study 10A) reproduces the same 13.006-point difference, with Welch's *t*(91.84) = 9.29, *p* < .001, 95 percent CI [10.23, 15.79], Hedges' *g* = 1.88. The point estimate is identical because it is the same two group means; only the standard error differs, because the three-group analysis pools within-band variability from all 144 children (SE 1.466) while the two-group analysis uses only the 96 in those bands (SE 1.400), and because the interval reported in the pairwise family is widened for multiplicity while this one is not. Study 10A also makes the covariate imbalance vivid: across those same two bands, vocabulary differs by 12.44 points.

### Level 4 Solutions

**Solution 14.13**

Emotion recognition accuracy differed across the three age bands, *F*(2, 141) = 43.02, *p* < .001, η² = 0.379, ω² = 0.369.

The two checks license the use of the pooled-variance model and the *F* reference distribution: spreads are similar across bands (*F* = 0.77, *p* = .467) and the residuals show no departure from normality worth acting on (*W* = 0.988, *p* = .247). They license nothing about the design. Neither check says anything about whether age band was assigned, whether the task measures the same construct at all three ages, or whether the sample represents any wider population. Assumption checks concern the model; they are silent about identification.

#### Study in the Larger Evidence Program: Age and Emotion Recognition

- **What this study adds:** A precise cross-sectional description of how accuracy differs across three age bands in one sample, with a covariate whose imbalance is documented.
- **What it cannot settle:** Whether the difference reflects maturation, schooling, language, test familiarity, or cohort, and whether any individual child improves - no child was measured twice.
- **Causal-support role:** Consistency evidence only. No responsiveness evidence is possible, because the grouping variable cannot be manipulated.
- **Next evidence priority:** A longitudinal design following the same children across the same age range, which converts between-child differences into within-child change and removes the cohort explanation.

**Solution 14.14**

The third contrast lost its threshold status under multiplicity adjustment: raw *p* = .039 became Bonferroni *p* = .116, and the family-wise 95 percent interval [−6.613, 0.492] includes zero.

There is no contradiction. The interval reported here is a *family-wise* interval, widened by the same adjustment that multiplied the *p* value, so that all three intervals hold simultaneously at 95 percent confidence. An unadjusted 95 percent interval for the same contrast would have been narrower and would have excluded zero, matching the raw *p* value. The interval and the *p* value agree with one another as long as both are adjusted or both are not.

A reader should conclude that the two older bands could not be reliably distinguished within a family of three comparisons, and that the data are compatible with a difference between them of up to about 6.6 points in one direction or about half a point in the other. That is a statement about precision, not a demonstration that the two bands are equivalent.

**Solution 14.15**

The vocabulary coefficient of 0.329 means that among children in the same age band, each additional vocabulary point is associated with about a third of a point more accuracy, with a 95 percent interval of [0.168, 0.490].

The `age_10_11` coefficient of 8.917 describes the difference in accuracy between the 10-11 band and the 6-7 reference band *among children with the same vocabulary score*. The 13.006 in the previous table describes the difference between those same two bands with no such restriction - the total difference between the groups as they actually are.

They differ by 4.089 points because older children have higher vocabulary, so holding vocabulary constant removes part of what distinguishes the bands. The adjusted figure is not a corrected version of the unadjusted one. It is an answer to a different question, and in this study the unadjusted figure is the one that matches the research question as stated.

**Solution 14.16**

The interaction test licenses the use of a single common slope for vocabulary across the three bands: there is no evidence that the vocabulary-accuracy relationship differs by band, *F*(2, 138) = 0.67, *p* = .516. That removes one reason the adjusted coefficients would be uninterpretable.

The three within-band correlations of 0.221, 0.403, and 0.322 are not in conflict with that result. A correlation depends on both the slope and the spreads of the two variables within the band, so correlations can differ while slopes do not. More importantly, three correlations estimated on 48 children each carry substantial sampling error; differences of this size are entirely ordinary under a common underlying slope, which is exactly what the interaction test reports.

Passing this check does not make the adjustment appropriate. It says the model is internally coherent, not that the quantity it estimates is the quantity anyone wanted.

### Level 5 Solutions

**Solution 14.17**

A one-way analysis of variance across the three age bands, followed by all three pairwise comparisons with a prespecified Bonferroni adjustment, is the defensible primary analysis. The structure supports it: one independent score per child, three groups, a quantitative outcome, similar spreads, and well-behaved residuals.

The primary estimates to report are the three mean differences with their family-wise intervals, because they are on the scale of the outcome and answer the question directly. The omnibus *F* is worth reporting as the family's gate, but a reader learns more from −9.946, −13.006, and −3.060 with intervals than from a single *F* of 43.02. The unadjusted differences are the primary estimates because the research question asks how accuracy differs across age bands as they actually are.

**Solution 14.18**

The argument fails on the causal position of the covariate. Vocabulary cannot be a confounder of the age-accuracy relationship, because a confounder must be a common cause of both, and nothing causes a child's age. Vocabulary is a consequence of age. Conditioning on a consequence of the grouping variable removes the portion of the effect that travels through it, so 8.917 is a smaller number not because contamination was removed but because part of the effect was.

What 8.917 does estimate is the difference in accuracy between the 6-7 and 10-11 bands among children with the same vocabulary score - loosely, the part of the age difference that does not operate through vocabulary. That is a defensible quantity to report and can be interesting, particularly to someone asking whether age brings anything beyond language development. It is not the total age difference, and it is not a corrected estimate of it.

The general lesson: "adding a covariate reduced the coefficient, so the covariate was a confounder" is a non-sequitur. Adjusting for a mediator also reduces the coefficient. Adjusting for a collider can increase it, or reverse its sign. The output looks the same in all three cases.

**Solution 14.19**

Reversing the model cannot arbitrate anything, because both models are descriptions of the same joint distribution and neither contains information about direction. Regression is symmetric in that sense: a well-fitting model of accuracy given vocabulary and a well-fitting model of vocabulary given accuracy can both exist, and neither one licenses a claim about which variable acts on which.

In this study the proposal is additionally impossible on its face, because age band cannot be an outcome of anything measured at the same session.

The general error is treating a fitted coefficient as evidence about causal direction. Direction comes from design - what was manipulated, what was measured first, what could not have been caused by what - and from subject-matter argument. Fit statistics can tell you a model describes the data; they cannot tell you the arrow points left rather than right.

**Solution 14.20**

It is defensible only if that contrast was designated the primary comparison *before* the data were examined, and it is then reported as the single primary test with the other two labelled as secondary. Under that plan there is no family of three to adjust for, and the raw *p* value is the correct one.

It is not defensible here. The three comparisons were planned as a family, and selecting one of them as "of primary interest all along" after seeing which one lost its threshold status is a decision made in response to the result. The reported *p* value would then describe a procedure different from the one actually used.

The sentence to report either way is the same, and it does not depend on the threshold: "The 8-9 and 10-11 bands differed by 3.06 points, 95 percent family-wise CI [−6.61, 0.49], Bonferroni-adjusted *p* = .116; the data do not distinguish these two bands within a family of three comparisons, and are compatible with differences ranging from a 6.6-point advantage for the older band to a small advantage for the younger."

#### Study in the Larger Evidence Program: Adjusting for a Consequence

- **What this study adds:** A clean example of a covariate that is caused by the grouping variable rather than confounding it, with both quantities reported: a total difference of 13.006 points and a vocabulary-held-fixed difference of 8.917.
- **What it cannot settle:** Which of the two is the "real" effect of age. That question is malformed; the two estimate different things, and the design identifies neither causally.
- **Causal-support role:** None added by adjustment. A better-fitting model on an unidentified design is a more precise estimate of an association.
- **Next evidence priority:** A design that assigns something manipulable - a task instruction, a training exposure - so that a causal contrast exists to estimate at all.

### Level 6 Solutions

**Solution 14.21**

Emotion recognition accuracy was compared across three age bands with 48 children in each (6-7: *M* = 59.35, *SD* = 6.31; 8-9: *M* = 69.30, *SD* = 7.80; 10-11: *M* = 72.36, *SD* = 7.36). Accuracy differed across bands, *F*(2, 141) = 43.02, *p* < .001, η² = 0.379, ω² = 0.369. In a prespecified family of three pairwise comparisons with Bonferroni adjustment, the 6-7 band scored lower than the 8-9 band by 9.95 points, 95 percent family-wise CI [−13.50, −6.39], adjusted *p* < .001, and lower than the 10-11 band by 13.01 points, CI [−16.56, −9.45], adjusted *p* < .001; the 8-9 and 10-11 bands did not differ reliably, difference 3.06 points, CI [−6.61, 0.49], adjusted *p* = .116. Variances were comparable across bands, Brown-Forsythe *F*(2, 141) = 0.77, *p* = .467, and residuals showed no material departure from normality, *W* = 0.988, *p* = .247. Because age band was neither assigned nor assignable, these results describe cross-sectional differences among the represented children and do not isolate an effect of age.

**Solution 14.22**

"The 6-7 band scored 13.01 points lower than the 10-11 band, 95 percent family-wise CI [−16.56, −9.45]. Vocabulary scores also differed substantially across bands (*M* = 41.27, 47.97, and 53.71 for the three bands, *F*(2, 141) = 37.36, *p* < .001), and vocabulary was positively related to accuracy within bands, *b* = 0.33, 95 percent CI [0.17, 0.49]. In a model containing both, the coefficient for the 10-11 band was 8.92, 95 percent CI [5.51, 12.32], which estimates the difference between the two bands among children with the same vocabulary score rather than the total difference between the bands. Because vocabulary develops with age, it is a consequence of the grouping variable rather than a confounder of it, so the second estimate is reported as a decomposition of the first and not as a correction to it."

**Solution 14.23**

Four distinct errors.

*Within-child change.* "Improved" describes a child getting better over time. No child in this study was measured twice; the design compares different children of different ages at one occasion. The word must go.

*Causal attribution.* "Between ages six and ten" attributes the difference to age, when age band carries schooling, language, test familiarity, and cohort along with it.

*Wrong statistic for the stated quantity.* The 13.01 figure is one pairwise contrast; *F*(2, 141) = 43.02 is the omnibus test across all three bands. Attaching the omnibus statistic to a specific contrast implies that this contrast was what the statistic tested.

*Missing uncertainty and multiplicity.* No interval is given, and no indication that the contrast belongs to a family of three.

Repaired: "Children in the 10-11 band scored 13.01 points higher on the task than children in the 6-7 band, 95 percent family-wise CI [9.45, 16.56], Bonferroni-adjusted *p* < .001 within a family of three comparisons. Because different children were tested at each age, this is a between-group difference rather than observed change within children."

**Solution 14.24**

"Age band was not assigned and could not be, so the comparison carries with it everything that accompanies being older in this sample - among them years of schooling, language development, familiarity with structured testing, and attention span - and the analysis cannot separate chronological age from any of them. The design is cross-sectional, comparing different children at one occasion, so it describes differences between age groups rather than change within children, and it cannot distinguish an age effect from a cohort difference. The task was administered in the same form at all three ages, and if it is harder to understand for the youngest children for reasons unrelated to emotion recognition, part of the observed difference would reflect the instrument rather than the construct."

\newpage
