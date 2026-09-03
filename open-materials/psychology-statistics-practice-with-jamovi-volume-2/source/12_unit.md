# PART IV

## Outcomes that are not means

\newpage

# Unit 12: Categorical Outcomes and Association

*Open educational resource licensed CC BY 4.0. All research scenarios are fictional and all datasets are synthetic. Complete the problems before consulting the worked solutions.*

## Unit Purpose

When the outcome is a category rather than a quantity, there is no mean to estimate and no difference to report on the outcome's scale. The analysis compares an observed pattern of counts with the pattern that independence would produce, and the effect size describes the strength of that departure. This unit develops the habit of identifying the case, the outcome's measurement level, the direction of conditioning, and the quantity a categorical analysis can and cannot deliver.

## Learning Objectives

After completing this unit, a learner should be able to:

- recognize when an outcome is categorical and state why a mean comparison is unavailable rather than merely inadvisable;
- compute an expected count from row, column, and grand totals and explain what independence means in that formula;
- distinguish row percentages, column percentages, and total percentages, and choose the one that answers the question;
- identify which cells drive a chi-square statistic and describe the pattern in words;
- separate the test statistic, which depends on sample size, from the effect size, which does not;
- state the expected-count condition and what to do when it fails; and
- keep a causal claim inside what the assignment mechanism supports, even when the analysis is correct.

## Decision Map

Ask these questions in order:

1. What is the scientific question, and is the outcome a quantity or a category?
2. What are the cases, and does each case contribute exactly one observation to the table?
3. Which variable is the grouping variable and which is the outcome, and does the question ask about the distribution of the outcome within groups?
4. What pattern of counts would independence produce, and are the expected counts large enough to trust the reference distribution?
5. What does the observed departure look like, cell by cell, in words?
6. What effect size describes the strength of association, separately from the sample size?
7. What does the assignment mechanism identify, what is the claim ceiling, and what evidence should come next?

## Study Files

The primary dataset is `study_08_help_seeking_categorical.csv`. Two teaching variants are subsets of the same file, reproducible in jamovi with a row filter. Public CSV files, dictionaries, and verified result records are available at [https://github.com/nicholaskarlson/data](https://github.com/nicholaskarlson/data).

| Study | Data structure | Primary outcome | Unit role |
| --- | --- | --- | --- |
| Study 08 | 150 participants, 50 in each of three message conditions | Selected support resource, three categories | Balanced randomized comparison of a categorical outcome |
| Study 08A | The 58 participants with `prior_support_use = yes` | Selected support resource | Smaller subset; a below-five expected count and an inconclusive test |
| Study 08B | The 92 participants with `prior_support_use = no` | Selected support resource | Larger subset; same association strength, different conclusion |

## Plausible Research Scenarios

The scenarios create decisions rather than documenting real research. At each Pause and Decide, stop reading and write an answer, reason, and confidence rating. The explanation that follows is feedback on that commitment.

### Plausible Research Scenario: Three Ways of Describing the Same Support Service

*This is a fictional research scenario created for teaching. Every referenced dataset is synthetic; it does not describe a real study or real participants.*

A fictional student services office offers three kinds of support: an advisor meeting, a peer group, and a self-guided module. All three remain available to every student at all times. The office wants to know whether the way the service is described changes which one students choose.

One hundred fifty synthetic students are randomly assigned in equal numbers to see one of three short messages. The autonomy message emphasizes making one's own plan; the belonging message emphasizes that other students use the service; the skills message emphasizes learning a specific technique. Each student then selects exactly one resource. The research question is: **does the distribution of resource choices differ across the three message conditions?**

One student is the independent unit. Each student contributes one row and appears in exactly one cell of a three-by-three table. The outcome, `resource_choice`, is nominal. There is no order among advisor meeting, peer group, and self-guided module, and no numerical spacing between them.

A fourth variable, `prior_support_use`, records whether the student had used the service before. It was measured, not assigned.

#### Pause and Decide

Before reading further, name the case, state the measurement level of the outcome, decide which percentages answer the question, choose the analysis, and state the strongest claim a randomized message assignment could support. Then say what quantity this design cannot produce no matter how large the sample becomes.

#### Why This Model?

A chi-square test of independence compares the observed table of counts with the counts expected if resource choice were unrelated to message condition. That matches a question about whether one categorical distribution differs across levels of another categorical variable.

A one-way analysis of variance is unavailable, not merely inferior: `resource_choice` has no numerical values to average. Recoding the three resources as 1, 2, and 3 and comparing means would impose an order and a spacing that the measurement does not contain, and the resulting number would change if the labels were listed in a different order. A separate two-proportion test for each resource would answer three narrower questions and would inflate the family-wise error rate without ever describing the table as a whole.

Because assignment to message condition was random and balanced, the design supports a causal claim about the effect of message framing on the distribution of choices among the represented students. It does not support a claim about any particular student, about the merits of the resources themselves, or about students at another institution.

#### What Would a Favorable Result Look Like?

The office would hope to see a pattern in which at least one message shifts choices toward a resource the office considers underused, with an effect size large enough to justify changing the wording. Direction and pattern matter more than whether a threshold is crossed.

An inconclusive table can also be scientifically successful. If the messages were delivered faithfully and the sample is adequate, a small association tells the office that wording is not the lever it hoped for, which redirects effort toward the service itself.

#### Best Defensible Claim

**Statistical evidence:** The chi-square analysis estimates whether, and how strongly, the observed distribution of resource choices departs from independence across the three message conditions, and Cramér's V describes the strength of that association on a scale from 0 to 1.

**Causal identification:** Random assignment to message condition supports a causal claim about the message's effect on the distribution of choices among the represented participants.

**Claim ceiling:** The office may claim that message framing changed which resource these students chose. It may not claim that any resource is more effective, that a particular student would have chosen differently, or that the pattern would recur in another population or service context.

#### What Must Be True?

Each student must contribute exactly one observation, and students' choices must not influence one another. The three categories must be exhaustive and mutually exclusive. Expected counts must be large enough for the chi-square reference distribution to be a reasonable approximation. The messages must have been delivered as intended.

#### Defensibility Procedures

Prespecify the table, the outcome, and the effect size before inspecting the counts. Confirm the assignment mechanism and check that the measured covariate is balanced across conditions, which is a check on the randomization rather than a hypothesis test of interest. Report the full table with observed counts, expected counts, and one clearly labelled set of percentages; report chi-square with its degrees of freedom, the *p* value, the effect size, and the minimum expected count.

**Next evidence priority:** If the goal is to increase useful help-seeking rather than to move choices between options, the next study should measure an outcome that reflects benefit, not selection, and should follow students beyond the moment of choice.

#### Claim Audit

Repair this claim before continuing: "The chi-square test proves that the belonging message is the best message." Your repair should distinguish an association in a table from a ranking of options, and a statistically detectable pattern from a practically useful one.

### Plausible Research Scenario: The Same Question in Two Groups of Different Size

*This is a fictional research scenario created for teaching. Every referenced dataset is synthetic; it does not describe a real study or real participants.*

A second analyst asks whether the message effect is present among students who had used the service before and among students who had not. The analyst splits the same file on `prior_support_use` and runs the same three-by-three analysis twice.

Study 08A contains the 58 students who had used the service before. Study 08B contains the 92 who had not. Both are subsets of the same public file and can be reproduced with a row filter.

This split was not planned before the data were inspected, and `prior_support_use` was measured rather than assigned.

#### Pause and Decide

Before reading further, predict what will happen to the chi-square statistic, the *p* value, the effect size, and the minimum expected count in each of the two unequal subsets. Then decide whether a difference in conclusions between the two subsets would be evidence that the message works differently for the two kinds of student.

#### Why This Model?

Within each subset the analysis is the same chi-square test of independence, and it is correctly specified for the same reason as before. What changes is the interpretive status of the comparison *between* subsets.

Comparing two separately computed chi-square tests is not a test of whether the association differs between subsets. A difference in significance is not a significant difference. The question "does the message effect depend on prior use?" is a question about an interaction, and answering it requires a model that includes both variables and their interaction, not two tests read side by side.

#### What Would a Favorable Result Look Like?

The analyst would hope to see a similar association in both subsets, which would suggest the pattern is not confined to one kind of student. Similar effect sizes with different *p* values would be an ordinary consequence of different sample sizes and would not be a finding.

#### Best Defensible Claim

**Statistical evidence:** Each subset analysis estimates the strength of association between message and choice within that subset.

**Causal identification:** Message assignment was random within the whole sample, so the message contrast remains interpretable inside each subset. The comparison between subsets is observational, because prior support use was not assigned.

**Claim ceiling:** The analyst may describe the association within each subset. The analyst may not claim that the effect of the message differs by prior use on the basis of two separate tests, and may not treat a subset chosen after seeing the overall result as a prespecified analysis.

#### What Must Be True?

The subset must be defined by a variable measured before the outcome. Expected counts within each subset must still support the approximation. The reader must be told that the split was exploratory.

#### Defensibility Procedures

Report both subset tables in full, including minimum expected counts. State whether the split was prespecified. If the interaction is the question, fit a model that can answer it and say so. Report effect sizes for both subsets alongside the overall analysis so that a reader can see what changed and what did not.

**Next evidence priority:** A prespecified study powered for the interaction, with prior support use recorded before assignment and treated as a stratifying variable.

#### Claim Audit

Explain why "the message worked for new users but not for returning users" is indefensible when it rests on one subset with *p* = .017 and another with *p* = .095.

## Problems

*Do not consult the solutions until you have recorded an answer, reason, and confidence rating for every attempted item.*

### Level 1: Recall and Recognize

**Problem 12.1 — Name the unavailable quantity**

Study 08 records which of three resources each of 150 students selected. A reviewer asks for "the mean resource choice by condition." Explain what is wrong with the request in terms of measurement level, and name the quantity that is available instead.

**Problem 12.2 — Identify the case and the cell**

How many rows does Study 08 contribute to the three-by-three table, and how many cells does one student occupy? Name the design feature that would break if a student could select two resources.

**Problem 12.3 — State what independence means here**

In a chi-square test of independence, what would it mean, in the language of this study, for `resource_choice` to be independent of `message_condition`? Answer without using the word "significant."

**Problem 12.4 — Degrees of freedom from the table shape**

Study 08's table has three message conditions and three resource categories. State the degrees of freedom and the rule that produces it. Why does the total sample size not appear in that rule?

### Level 2: Predict Before Clicking

**Problem 12.5 — Predict the expected counts**

Every message condition contains exactly 50 students, and 57 students in total chose an advisor meeting. Before running anything, predict the expected count for the autonomy-message and advisor-meeting cell, and state whether the three expected counts in the advisor-meeting column will be equal to one another.

**Problem 12.6 — Predict which cells will dominate**

The belonging-message row contains 22 peer-group choices and 8 self-guided choices; the skills-message row contains 7 peer-group choices and 20 self-guided choices. Each of those cells has an expected count of 14.0 or 17.0. Predict which two cells will contribute most to the chi-square statistic, and explain why a cell 9 below an expectation of 17.0 can contribute more than a cell 8 above an expectation of 14.0.

**Problem 12.7 — Predict the effect of shrinking the sample**

Study 08B contains 92 of the 150 students and shows a similar pattern of percentages. Predict what will happen to the chi-square statistic, the *p* value, and Cramér's V relative to the full sample, and say which of the three is designed to be insensitive to sample size.

**Problem 12.8 — Predict the expected-count problem**

Study 08A contains 58 students. Its smallest row total is 17 and its smallest column total is 16. Predict the smallest expected count in that table and state whether it satisfies the usual condition.

### Level 3: Calculate and Explain

**Problem 12.9 — Compute an expected count**

Using row total 50, column total 42, and grand total 150, compute the expected count for the belonging-message and peer-group cell. Show the formula and explain in one sentence why it is the count implied by independence.

**Problem 12.10 — Compute two cell contributions**

The belonging-message and peer-group cell has an observed count of 22 against an expected count of 14.0. The belonging-message and self-guided cell has an observed count of 8 against an expected count of 17.0. Compute each cell's contribution to the chi-square statistic and state which is larger.

**Problem 12.11 — Recover the effect size**

Study 08's chi-square statistic is 17.765 with a grand total of 150 and a table that is three by three. Compute Cramér's V using V = √(χ² / (N × (k − 1))), where *k* is the smaller of the number of rows and columns. Explain what the denominator is doing.

**Problem 12.12 — Convert a count to the right percentage**

In the autonomy-message row, 23 of 50 students chose the self-guided module, and 51 students chose the self-guided module overall. Compute both the row percentage and the column percentage for that cell, and state which one answers the study's research question.

### Level 4: Read jamovi Output

**Problem 12.13 — Read the contingency table**

The verified contingency table for Study 08 is reproduced below, with observed counts and expected counts in parentheses.

| Message condition | Advisor meeting | Peer group | Self-guided module | Row total |
| --- | --- | --- | --- | --- |
| Autonomy | 14 (19.0) | 13 (14.0) | 23 (17.0) | 50 |
| Belonging | 20 (19.0) | 22 (14.0) | 8 (17.0) | 50 |
| Skills | 23 (19.0) | 7 (14.0) | 20 (17.0) | 50 |
| Column total | 57 | 42 | 51 | 150 |

Describe the pattern in words, naming the resource each message pulled toward and the resource each message pulled away from. Do not use the words "significant" or "caused."

**Problem 12.14 — Read the test line**

jamovi reports χ² = 17.765, df = 4, *p* = .001, Cramér's V = 0.243, with a minimum expected count of 14.0 and no cells below five. Write one sentence reporting the test in APA style and one sentence saying what the effect size adds that the *p* value does not.

**Problem 12.15 — Read the smaller subset**

For Study 08A, jamovi reports χ² = 7.912, df = 4, *p* = .095, Cramér's V = 0.261, minimum expected count 4.69. For Study 08B it reports χ² = 12.105, df = 4, *p* = .017, Cramér's V = 0.256, minimum expected count 7.00. Read the two subset effect sizes together with the full-sample V of 0.243 and state what the comparison shows.

**Problem 12.16 — Read a balance check**

The same file reports a message-condition by prior-support-use table with χ² = 1.068, df = 2, *p* = .586, Cramér's V = 0.084. Explain what this table is being used for, and why a large *p* value here is reassuring while a large *p* value in the main analysis would not be.

### Level 5: Choose the Model

**Problem 12.17 — Choose the analysis for the stated question**

The question is whether the distribution of resource choices differs across the three message conditions, with one categorical choice per student. Choose the analysis and justify it from the data structure. Then reject a one-way analysis of variance on numerically recoded resource choices, and state the specific way that recoding changes the answer.

**Problem 12.18 — Reject the three separate tests**

An analyst proposes running three separate two-proportion tests, one per resource, and reporting whichever is significant. Give two distinct reasons this is indefensible, one about the family of tests and one about what question the table was built to answer.

**Problem 12.19 — Reject the subset conclusion**

An analyst reports that the message "worked" in Study 08B (*p* = .017) but "did not work" in Study 08A (*p* = .095), and concludes that the effect depends on prior support use. Reject that conclusion. Name the analysis that would actually address the question and the design feature that limits it.

**Problem 12.20 — Choose a response to a sparse cell**

Study 08A has a minimum expected count of 4.69, just below the usual threshold. List three defensible responses, and one indefensible one. Explain why deleting the smallest category is the indefensible option.

### Level 6: Report and Critique

**Problem 12.21 — Write the result paragraph**

Using the verified values for Study 08, write a short APA-style results paragraph. Include the table shape, the test statistic with degrees of freedom, the *p* value, the effect size, a one-clause description of the pattern, and the expected-count check.

**Problem 12.22 — Repair a causal overreach**

Repair this sentence: "Because students who saw the belonging message were more likely to choose the peer group, peer support is what students actually need." Your repair should preserve what the design does license.

**Problem 12.23 — Repair a scale error**

Repair this sentence: "The belonging message increased peer-group selection by 8 students on average, χ²(4) = 17.77, *p* = .001." Identify every distinct error. The arithmetic in the sentence is correct.

**Problem 12.24 — Write the limitation that keeps the claim honest**

Study 08 is randomized, correctly analysed, and clearly reported. Write the two-sentence limitation that should still accompany it. One sentence must concern what the outcome measures; the other must concern to whom the result applies.

\newpage

## Solutions

### Level 1 Solutions

**Solution 12.1**

`resource_choice` is nominal. Its values are labels for three distinct options with no order and no numerical spacing, so no arithmetic operation on them is meaningful and no mean exists to estimate. The available quantities are counts and the proportions or percentages derived from them: within each message condition, the proportion of students choosing each resource. Decisive cue: ask whether the halfway point between two values is interpretable. There is no resource halfway between an advisor meeting and a peer group.

**Solution 12.2**

Study 08 contributes 150 rows, one per student, and each student occupies exactly one of the nine cells, so the nine cell counts sum to 150. If a student could select two resources, the counts would exceed the number of students and the cells would no longer be mutually exclusive. The chi-square test of independence assumes each case appears once; a multiple-response question requires a different analysis.

**Solution 12.3**

Independence would mean that knowing which message a student saw tells you nothing about which resource they chose: the percentage choosing an advisor meeting, a peer group, and a self-guided module would be the same in all three message rows, apart from sampling variation. Equivalently, each cell count would be close to the count implied by multiplying its row proportion by its column proportion and by the grand total.

**Solution 12.4**

*df* = (rows − 1) × (columns − 1) = (3 − 1) × (3 − 1) = 4. The rule counts how many cells are free to vary once the row and column totals are fixed: fill in a two-by-two corner of the table and every remaining cell is determined by subtraction. Sample size does not appear because degrees of freedom describe the shape of the table, not how much information it contains. Sample size enters the analysis elsewhere, through the expected counts and therefore through the size of the statistic.

### Level 2 Solutions

**Solution 12.5**

Expected count = 50 × 57 / 150 = 19.0. The three expected counts in the advisor-meeting column are all 19.0, because all three row totals are equal at 50. Equal expected counts within a column are a consequence of the balanced design, not of the result. Transfer cue: expected counts are built from the margins alone and can be written down before any cell is inspected.

**Solution 12.6**

The two dominant cells are belonging with peer group (22 observed against 14.0 expected, a deviation of +8) and belonging with self-guided (8 observed against 17.0 expected, a deviation of −9). The second contributes more, even though its expected count is larger, because each contribution is a squared deviation divided by its own expected count, so both the size of the deviation and the size of the expectation matter. Here 9² / 17.0 = 4.765 exceeds 8² / 14.0 = 4.571: squaring the deviation outweighs the larger divisor.

**Solution 12.7**

With a similar pattern of percentages and roughly two thirds of the cases, the chi-square statistic falls and the *p* value rises. Cramér's V should stay close to its full-sample value, because it is a standardized measure of association that divides the statistic by the sample size. The verified values bear this out: χ² falls from 17.765 to 12.105 and *p* rises from .001 to .017, while V moves only from 0.243 to 0.256. The effect size is the quantity designed to be insensitive to *N*.

**Solution 12.8**

The smallest expected count is the product of the smallest row total and the smallest column total divided by the grand total: 17 × 16 / 58 = 4.69. That falls below the customary minimum of five, so the chi-square approximation is at its limit and the analysis should say so. The condition concerns expected counts, not observed ones; a cell may contain few observations and still be acceptable if its expectation is adequate.

### Level 3 Solutions

**Solution 12.9**

Expected count = row total × column total / grand total = 50 × 42 / 150 = 14.0. Under independence, the proportion choosing a peer group should be the same in every row, so the belonging row's share of the 42 peer-group choices should be its share of the sample, 50 / 150, giving 42 × (50 / 150) = 14.0. The formula is that statement rearranged.

**Solution 12.10**

Peer group: (22 − 14.0)² / 14.0 = 64 / 14.0 = 4.571. Self-guided: (8 − 17.0)² / 17.0 = 81 / 17.0 = 4.765. The self-guided cell contributes slightly more because its deviation is larger, even though its larger expected count divides that deviation more heavily. Together these two cells contribute 9.336 of the 17.765 total, which is why the belonging row is the clearest part of the pattern.

**Solution 12.11**

V = √(17.765 / (150 × (3 − 1))) = √(17.765 / 300) = √0.05922 = 0.243. The denominator is the largest value the chi-square statistic could take in a table of this size and sample: *N* times one less than the smaller table dimension. Dividing by it rescales the statistic onto a 0-to-1 range so that association strength can be compared across tables with different sample sizes and shapes.

**Solution 12.12**

Row percentage = 23 / 50 = 46.0 percent of autonomy-message students chose the self-guided module. Column percentage = 23 / 51 = 45.098 percent of self-guided choosers had seen the autonomy message. The research question asks how choices are distributed *within* each message condition, so the row percentage answers it. The column percentage conditions in the wrong direction; it describes the composition of a group defined by the outcome, which is not what a randomized message assignment is designed to inform.

### Level 4 Solutions

**Solution 12.13**

Students who saw the autonomy message chose the self-guided module more often than independence would imply (23 against 17.0 expected) and chose an advisor meeting less often (14 against 19.0). Students who saw the belonging message chose the peer group markedly more often (22 against 14.0) and the self-guided module markedly less often (8 against 17.0). Students who saw the skills message showed the opposite peer-group pattern (7 against 14.0) and chose an advisor meeting somewhat more often (23 against 19.0). Each message shifted choices toward the resource that most closely matched its framing, and the belonging and skills rows moved in opposite directions on the peer-group option.

#### Study in the Larger Evidence Program: Message Framing and Resource Choice

- **What this study adds:** A randomized estimate of how message framing redistributes choices among three concurrently available resources, with a full table and a standardized association measure.
- **What it cannot settle:** Whether any of the three resources helps, whether a shifted choice improves an outcome the student cares about, or whether the pattern recurs in another service or population.
- **Causal-support role:** Responsiveness evidence for the framing manipulation, because the message was deliberately assigned. It supplies no mechanism evidence and no evidence about benefit.
- **Next evidence priority:** Follow the same randomized framing through to a downstream outcome such as attendance or self-reported benefit, so that the study estimates a consequence rather than a selection.

**Solution 12.14**

Resource choice was associated with message condition, χ²(4, *N* = 150) = 17.77, *p* = .001, Cramér's V = 0.243; no expected count fell below five, with a minimum of 14.0. The effect size adds the strength of the association on a scale that does not depend on the sample size: a V of 0.243 describes a modest but not negligible departure from independence, whereas the *p* value only reports how surprising the table would be under an independence model. Two tables with identical percentages and different sample sizes share an effect size and differ in *p*.

**Solution 12.15**

The three effect sizes are close together: 0.243 in the full sample, 0.256 in the larger subset, and 0.261 in the smaller subset. The *p* values are not: .001, .017, and .095. The comparison shows that the strength of association is essentially stable across the three analyses and that the differences in conclusion are produced by sample size, not by a change in the pattern. Reading the *p* values alone would suggest a finding that appears and disappears; reading the effect sizes shows one pattern estimated with three levels of precision. The Study 08A analysis additionally carries a minimum expected count of 4.69 and should be reported with that qualification.

**Solution 12.16**

The message-condition by prior-support-use table is a randomization check: prior support use was measured before the outcome and was not assigned, so under correct random assignment it should be distributed similarly across the three message conditions. The observed near-independence (V = 0.084) is consistent with assignment having worked. A large *p* value is reassuring here because the null model is what the design is supposed to produce. In the main analysis the null model is what the study is trying to rule out, so a large *p* value there is an absence of evidence rather than evidence of balance. In neither case does a large *p* value prove that the null is exactly true.

### Level 5 Solutions

**Solution 12.17**

A chi-square test of independence on the three-by-three table is the defensible analysis. Each of 150 students contributes one nominal outcome, the grouping variable is nominal with three levels, and the question concerns whether the distribution of the outcome differs across those levels.

A one-way analysis of variance on recoded values is not merely weaker; it answers a question that does not exist. Coding advisor meeting as 1, peer group as 2, and self-guided module as 3 asserts that a peer group is one unit above an advisor meeting and that a self-guided module is exactly as far above a peer group as a peer group is above an advisor meeting. Relabelling the same three categories in a different order produces different means, a different *F*, and possibly a different conclusion from the identical data. A result that changes when the labels are reordered is not a result.

**Solution 12.18**

First, three tests conducted at the same nominal level inflate the family-wise error rate, and selecting the significant one afterwards inflates it further; the reported *p* value would no longer describe the procedure that generated it. Second, the three tests answer three separate questions about individual resources and never address the question the table was built for, which concerns the distribution across all three options simultaneously. A pattern in which one resource gains and another loses is visible in the table and invisible in any single two-proportion test. Prespecified follow-up comparisons after an overall test, with an explicit multiplicity adjustment, are a defensible alternative; choosing among unadjusted tests after seeing them is not.

**Solution 12.19**

The conclusion compares two significance decisions and treats their difference as a finding. It is not: a difference in significance is not a significant difference. The two subset effect sizes are 0.261 and 0.256, which are nearly identical; only the precision differs, because one subset has 58 cases and the other 92. The question "does the message effect depend on prior support use?" is a question about an interaction and requires a model containing message condition, prior support use, and their interaction. Even that analysis is limited here: prior support use was measured rather than assigned, so any interaction it reveals is an observational moderation, and the subgroup split was chosen after the overall result was seen.

**Solution 12.20**

Three defensible responses: report the analysis with the minimum expected count stated so the reader can judge the approximation; use an exact test that does not rely on the large-sample approximation; or collapse categories only if a substantively meaningful grouping exists and the decision is prespecified and reported. A fourth reasonable response is to decline to analyse the subset at all and report the full-sample result, saying that the subset was underpowered.

Deleting the smallest category is indefensible because it discards cases on the basis of the outcome, changes the estimand from "the distribution across three resources" to "the distribution across two," and does so for a reason that has nothing to do with the research question. It also usually improves the *p* value, which makes it a decision the reader cannot distinguish from result shopping.

#### Study in the Larger Evidence Program: The Subgroup Split

- **What this study adds:** A demonstration that the same association, estimated at three sample sizes, yields three different threshold verdicts while the effect size barely moves (V = 0.243, 0.256, 0.261).
- **What it cannot settle:** Whether the message effect genuinely differs between students with and without prior support use. Two separate tests cannot answer that question, and the split was not prespecified.
- **Causal-support role:** None on its own. The message contrast retains its randomized status inside each subset, but the subset contrast is observational.
- **Next evidence priority:** A study powered for the interaction, with prior support use recorded before assignment and used as a stratifying variable rather than as a post hoc split.

### Level 6 Solutions

**Solution 12.21**

One hundred fifty synthetic participants were randomly assigned in equal numbers to one of three message conditions and each selected one of three support resources. Resource choice was associated with message condition, χ²(4, *N* = 150) = 17.77, *p* = .001, Cramér's V = 0.243. The clearest departures from independence occurred in the belonging-message row, where 22 of 50 students chose the peer group against 14.0 expected and 8 chose the self-guided module against 17.0 expected. All expected counts exceeded five, with a minimum of 14.0. Because message condition was randomly assigned, the analysis supports a causal claim about the effect of message framing on the distribution of choices among the represented participants; it does not evaluate the resources themselves.

**Solution 12.22**

Repaired: "Students who saw the belonging message chose the peer group more often than independence would imply, which indicates that the framing of the description influenced selection among the represented participants. The study measured which resource students chose, not whether any resource helped them, so it cannot establish what students need."

The original sentence makes two jumps. It moves from a shift in selection to a claim about benefit, which the outcome never measured, and it moves from an effect of the *message* to a property of the *resource*, when the randomized manipulation was the wording and not the service.

**Solution 12.23**

Three distinct errors. First, a scale error: a chi-square analysis produces no average and no per-student increase, so "increased by 8 students on average" reports a quantity the model never estimated. The 8 is a raw count in a single cell, and the 22-against-14.0 comparison is a departure from an expectation, not a difference in a mean. Second, a granularity error: the chi-square statistic and its *p* value describe the whole table, so attaching them to one cell's pattern implies that a specific cell was tested when it was not. Third, a reporting error: the sentence gives no effect size, no expected-count information, and no table shape, leaving the reader unable to judge either strength or adequacy.

A defensible version reports the cell pattern descriptively and the test at the level it was computed: "Among students who saw the belonging message, 22 of 50 (44.0 percent) chose the peer group, compared with 14.0 expected under independence; across the full table, χ²(4, *N* = 150) = 17.77, *p* = .001, Cramér's V = 0.243."

**Solution 12.24**

"The outcome recorded which resource a student selected immediately after reading one message; it did not record whether the selected resource was attended, completed, or beneficial, so the study estimates a change in choice rather than a change in outcome. The participants are a synthetic sample representing one service context, and the result does not establish that the same framing would redistribute choices in another institution, with a different set of available resources, or at a different point in an academic term."

Both sentences are necessary and they do different jobs. The first bounds the construct: a well-executed randomized study still only measures what the outcome variable measured. The second bounds the population: random assignment supports internal comparison and says nothing about external reach.

\newpage
