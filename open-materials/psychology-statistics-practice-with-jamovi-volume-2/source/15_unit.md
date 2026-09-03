# Unit 15: Single-Case Designs and Nonoverlap

*Open educational resource licensed CC BY 4.0. All research scenarios are fictional and all datasets are synthetic. Complete the problems before consulting the worked solutions.*

## Unit Purpose

A single-case design does not have a small sample. It has a different unit. Forty-two daily observations of one person are forty-two measurements of one case, and the comparison runs within a series rather than between people. The evidence comes from the pattern of level, trend, variability, and overlap across phases, and its credibility comes from replication across cases. This unit develops the habit of reading a series before summarising it, computing a nonoverlap statistic by hand so that its meaning is unmistakable, and refusing to convert repeated observations of one person into a between-groups test.

## Learning Objectives

After completing this unit, a learner should be able to:

- identify the case in a single-case design and explain why the number of observations is not the number of independent units;
- read a phase series for level, trend, variability, and immediacy of change;
- explain why a declining baseline strengthens some claims and weakens others;
- compute nonoverlap of all pairs by hand, including the half-credit tie rule, and state what it does and does not measure;
- describe an ordinal outcome with frequencies and medians, and mark any mean as supplemental;
- reject a between-groups test applied to repeated observations of one case, and name the assumption it violates; and
- state the generalization boundary that one case imposes no matter how clean the series looks.

## Decision Map

Ask these questions in order:

1. What is the scientific question, and whose behaviour is it about?
2. What is the case, and how many cases are there?
3. What are the phases, how long is each, and in what order did they occur?
4. What does each series look like in level, trend, variability, and immediacy at the phase change?
5. What is the measurement level of each outcome, and which summaries are permitted by it?
6. What nonoverlap or level-change summary answers the question, and what does it leave out?
7. What does the design identify, what is the claim ceiling, and what evidence should come next?

## Study Files

The primary dataset is `study_11_single_case_habit_tracking.csv`. The teaching variant is not a different file; it is the same data analysed with a model that does not fit, so that its output can be examined and rejected.

| Study | Data structure | Primary outcomes | Unit role |
| --- | --- | --- | --- |
| Study 11 | One case, 42 consecutive days in three phases of 14 | Daily habit count; daily stress rating | Complete single-case series with phase structure |
| Study 11A | The same 28 days from the baseline and intervention phases | Daily habit count; daily stress rating | Days treated as if they were independent people; the model to reject |

The phases run in order: baseline on days 1 to 14, intervention on days 15 to 28, and maintenance on days 29 to 42. `habit_count` is a daily count. `stress_rating` is an ordinal daily self-rating with observed values from 1 to 8, where higher values indicate more stress.

## Plausible Research Scenarios

The scenarios create decisions rather than documenting real research. At each Pause and Decide, stop reading and write an answer, reason, and confidence rating.

### Plausible Research Scenario: One Person, Forty-Two Days

*This is a fictional research scenario created for teaching. Every referenced dataset is synthetic; it does not describe a real study or real participants.*

A fictional student works with a counsellor on a daily routine. For two weeks the student records, without changing anything, how many target habits they complete each day and how stressed they felt on a one-to-eight rating. That is the baseline phase. For the next two weeks the student follows a structured routine the counsellor designed; that is the intervention phase. For a final two weeks the structured supports are withdrawn but the student continues recording; that is the maintenance phase.

The research question is: **did the student's habit completion and stress ratings change when the routine was introduced, and did any change persist when the supports were removed?**

The case is the student. There is one of them. The forty-two rows are forty-two occasions on which that one student was measured, and consecutive days are related: a good day tends to follow a good day.

#### Pause and Decide

Before reading further, name the case, state how many independent units the design contains, decide what you would look at first if you could see only one thing, and write the strongest claim an A-B design with a maintenance phase could support. Then say what a very large statistical result would and would not add.

#### Why This Model?

The primary analysis is visual and descriptive: a chronological plot of each series with the phase changes marked, supported by phase-level summaries of level, trend, and variability, and by a nonoverlap statistic that quantifies how completely the phases separate.

That is the model because the question is about a pattern in one series over time. The interesting features - whether the change was immediate, whether it held, whether the baseline was already moving - live in the sequence, and every one of them is destroyed by summarising each phase as a single mean.

Nonoverlap of all pairs (NAP) is the quantitative summary used here. It takes every possible pairing of one baseline observation with one comparison-phase observation, scores a pair 1 when the comparison observation is better, 0 when it is worse, and 0.5 when the two are tied, and reports the average. It ranges from 0 to 1, with 0.5 meaning complete overlap and 1 meaning that every comparison-phase observation improved on every baseline observation. It is a statement about pairs of days, not about how many habits changed.

The design is an A-B sequence with a follow-up phase. It is the weakest of the standard single-case structures because the change is introduced once and never withdrawn or replicated. Anything that happened at the same time as the routine - a change in term workload, weather, sleep, a resolved worry - remains an alternative explanation for the whole pattern.

#### What Would a Favorable Result Look Like?

The counsellor would hope for an immediate change at the phase boundary, little overlap between phases, a stable or contrary baseline trend, and maintenance values that hold rather than drift back. Direction and pattern matter far more than any single summary number.

An unfavourable or mixed pattern is also informative. A gradual change with a rising baseline would suggest the routine did not add much to something already under way. A change that reverses in maintenance would say the effect depends on the supports remaining in place, which is itself a finding a counsellor can act on.

#### Best Defensible Claim

**Statistical evidence:** The series describe the level, trend, variability, and overlap of one student's habit counts and stress ratings across three phases, and the nonoverlap statistics quantify how completely the phases separate.

**Causal identification:** Weak. The routine was introduced once, at a known time, with no withdrawal and no replication, so any concurrent change remains an alternative explanation.

**Claim ceiling:** The counsellor may describe what happened for this student across these six weeks and note that the change coincided with the routine's introduction. The counsellor may not claim the routine caused the change with any confidence, and may not claim anything at all about another student.

#### What Must Be True?

Measurement must be comparable across all forty-two days: the same definition of a completed habit and the same stress scale, recorded with the same diligence in every phase. Reactivity is a real concern, because the act of recording can itself change behaviour, and it operates from day one. The phase boundaries must be the dates that were planned, not dates chosen afterwards because the series changed there.

#### Defensibility Procedures

Plot both series before computing anything. Record the phase dates and the decision rule that set them in advance. Report level, trend, and variability for each phase, and report the nonoverlap statistic with its tie rule and its direction convention stated. Describe the ordinal stress outcome with frequencies and medians, and mark any mean as supplemental. Report both outcomes whether or not they agree.

**Next evidence priority:** Replicate the same phase structure across several cases with staggered start dates - a multiple-baseline design - so that a change occurring at each case's own phase boundary becomes difficult to explain by a single shared event.

#### Claim Audit

Repair this claim before continuing: "The routine increased habit completion by 2.43 habits per day and works for students with high stress." Your repair should address both the causal language and the population claim, and should say what the 2.43 figure legitimately describes.

### Plausible Research Scenario: The Analyst Who Counted Days as People

*This is a fictional research scenario created for teaching. Every referenced dataset is synthetic; it does not describe a real study or real participants.*

An analyst opens the same file, sees a grouping column with two values in the first twenty-eight rows and a numeric outcome, and runs an independent-samples *t* test comparing baseline days with intervention days. The software produces output without complaint.

The habit comparison gives *t*(26) = 6.02, *p* < .001, with a standardized mean difference of 2.28. The stress comparison gives *t*(26) = −8.05, *p* < .001, with a standardized mean difference of −3.04.

The analyst reports these as the study's inferential results.

#### Pause and Decide

Before reading further, decide what the number 26 in those degrees of freedom is counting, and whether that count corresponds to anything the study actually collected. Then decide whether the very small *p* values make the conclusion stronger or make the error more dangerous.

#### Why This Model?

It is not the model. It is the model to reject, and it is included because it is easy to run, produces impressive output, and is the single most common mistake made with single-case data.

An independent-samples *t* test assumes that every observation is an independent unit drawn from its group. Here the twenty-eight observations are twenty-eight days in the life of one person. They are not independent of one another in two distinct ways: consecutive days are serially related, and all twenty-eight of them come from one individual whose general tendencies are common to every row. The degrees of freedom of 26 asserts that the study contains 28 independent units. It contains one.

The consequence is not that the estimate is meaningless - the mean difference of 2.43 habits per day is a real description of the two phases - but that the standard error, the *t* statistic, and the *p* value are computed from a variability estimate that does not correspond to any replication the study could perform. A *p* value describes how often a result of this size would arise under repeated sampling; here there is nothing to sample.

#### What Would a Favorable Result Look Like?

None. A more extreme *p* value from this analysis is worse, not better, because it makes an unjustified inference harder for a reader to resist.

#### Best Defensible Claim

**Statistical evidence:** The mean difference between phases is a descriptive summary of one person's series. The test statistic and *p* value do not describe any inference the design supports.

**Causal identification:** Unchanged by the test, and still weak.

**Claim ceiling:** Descriptive only. No inference to a population and no probability statement.

#### What Must Be True?

For the *t* test to be interpretable, days would have to be independent replications, which they are not by construction.

#### Defensibility Procedures

Report the descriptive difference and the nonoverlap statistic. Do not report a between-groups test on days. If a formal inferential treatment is genuinely needed, use a method built for serially dependent single-case data and state its assumptions - and note that with one case the generalization boundary is unchanged whatever method is used.

**Next evidence priority:** Additional cases. Statistical machinery cannot substitute for the replication that single-case designs get from repeating the pattern in new participants.

#### Claim Audit

Explain why "*p* < .001, so the effect is highly reliable" is exactly backwards as a defence of Study 11A.

\newpage

## Problems

*Do not consult the solutions until you have recorded an answer, reason, and confidence rating for every attempted item.*

### Level 1: Recall and Recognize

**Problem 15.1 — Count the units**

Study 11 contains 42 rows. State how many cases it contains, how many observations, and how many independent units are available for generalizing to other students. Explain why the three answers differ.

**Problem 15.2 — Name the design and its weakest feature**

The phases run baseline, intervention, maintenance, with the routine introduced once and never withdrawn. Name the design, and name the feature it lacks that stronger single-case designs use to rule out concurrent explanations.

**Problem 15.3 — State what NAP measures**

Complete the sentence precisely: "Nonoverlap of all pairs reports the proportion of ..." Then state its value under complete overlap and its value when every comparison observation improves on every baseline observation.

**Problem 15.4 — Identify the permitted summaries**

`stress_rating` is recorded as an ordinal daily rating from 1 to 8. State which summaries are directly supported by that measurement level, which require an additional assumption, and name the assumption.

### Level 2: Predict Before Clicking

**Problem 15.5 — Predict overlap from the extremes**

In the habit series, the largest baseline value is 4 and the smallest intervention value is 4. Predict, before computing anything, whether any intervention day is worse than any baseline day, and predict roughly what NAP will be.

**Problem 15.6 — Predict the effect of the tie rule**

Baseline contains two days with a habit count of 4 and intervention contains eight such days. Predict how many of the 196 baseline-intervention pairs are ties, and predict whether the half-credit rule will raise or lower NAP relative to a rule that ignored ties.

**Problem 15.7 — Predict what a declining baseline does**

The baseline slope is −0.033 habits per day for the habit count and −0.062 rating points per day for stress. For each outcome, predict whether a declining baseline strengthens or weakens the claim that the routine produced the change, and explain the asymmetry.

**Problem 15.8 — Predict what the wrong test will show**

The two phase means for habit count are 2.357 and 4.786, with standard deviations near 1.0 and 1.1 and 14 observations each. Predict the approximate *t* statistic from an independent-samples test on days, and predict whether its *p* value will be small. Then state whether a small value would support the study's conclusion.

### Level 3: Calculate and Explain

**Problem 15.9 — Compute a level change**

The baseline habit mean is 2.357 and the intervention habit mean is 4.786; the baseline stress mean is 6.571 and the intervention stress mean is 3.786. Compute both level changes with their signs, and state what the sign means for each outcome given the direction of each scale.

**Problem 15.10 — Compute NAP by hand**

For the habit count, all 196 baseline-intervention pairs fall into three categories: 180 in which the intervention day is higher, 16 ties, and none in which the baseline day is higher. Compute NAP using the half-credit tie rule and show the arithmetic.

**Problem 15.11 — Compute NAP for the ordinal outcome**

For stress, lower is better. Of the 196 baseline-intervention pairs, 189 show improvement, 7 are ties, and none show deterioration. Compute the improvement NAP and explain why the direction convention has to be stated explicitly for this outcome but not for the habit count.

**Problem 15.12 — Convert NAP into a statement about days**

The baseline-to-maintenance NAP for stress is 1.000. State exactly what that value means in terms of days, and state what it does not mean about the size of the change.

### Level 4: Read jamovi Output

**Problem 15.13 — Read the phase descriptives**

| Outcome | Phase | *n* | Median | Q1 | Q3 | Min | Max | Slope per day | First | Last |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Habit count | Baseline | 14 | 2.0 | 2.0 | 3.0 | 1 | 4 | −0.033 | 3 | 1 |
| Habit count | Intervention | 14 | 4.0 | 4.0 | 5.0 | 4 | 7 | +0.068 | 5 | 6 |
| Habit count | Maintenance | 14 | 5.0 | 5.0 | 6.0 | 3 | 9 | −0.095 | 5 | 5 |
| Stress rating | Baseline | 14 | 6.5 | 6.0 | 7.0 | 6 | 8 | −0.062 | 7 | 6 |
| Stress rating | Intervention | 14 | 4.0 | 3.0 | 4.0 | 2 | 6 | −0.160 | 4 | 3 |
| Stress rating | Maintenance | 14 | 3.0 | 2.0 | 3.0 | 1 | 4 | +0.077 | 2 | 3 |

Describe the level and trend of each series across the three phases. Name the one phase whose range is noticeably wider than the others and say what that widening might reflect.

**Problem 15.14 — Read the ordinal frequencies**

| Stress rating | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Baseline | 0 | 0 | 0 | 0 | 0 | 7 | 6 | 1 |
| Intervention | 0 | 2 | 3 | 6 | 2 | 1 | 0 | 0 |
| Maintenance | 1 | 4 | 6 | 3 | 0 | 0 | 0 | 0 |

Describe what this table shows that a table of phase means would not. Identify the single value at which the baseline and intervention distributions touch, and say how many days sit there in each phase.

**Problem 15.15 — Read the nonoverlap table**

| Contrast | Outcome | NAP |
| --- | --- | --- |
| Baseline to intervention | Habit count | 0.959 |
| Baseline to maintenance | Habit count | 0.974 |
| Baseline to intervention | Stress (improvement) | 0.982 |
| Baseline to maintenance | Stress (improvement) | 1.000 |
| Intervention to maintenance | Habit count | 0.684 |
| Intervention to maintenance | Stress (improvement) | 0.750 |

Write two sentences describing what this table shows about the introduction of the routine and about what happened after the supports were withdrawn.

**Problem 15.16 — Read the output that should not have been produced**

Study 11A reports *t*(26) = 6.02, *p* < .001, *d* = 2.28 for the habit count, and *t*(26) = −8.05, *p* < .001, *d* = −3.04 for stress. State what the number 26 asserts about the study, state whether that assertion is true, and identify the one quantity in this output that remains a defensible description.

### Level 5: Choose the Model

**Problem 15.17 — Choose the primary analysis**

Choose the primary analysis for the stated question and justify it from the data structure. State what you would present first, what you would present as quantitative support, and what you would refuse to present at all.

**Problem 15.18 — Reject the between-groups test**

Reject the Study 11A analysis. Name the assumption it violates, name two distinct sources of dependence in the data, and explain why a more extreme *p* value makes the error more serious rather than less.

**Problem 15.19 — Reject the transition-day claim**

An analyst writes: "The effect was immediate: habit count went from 1 on the last baseline day to 5 on the first intervention day, a jump of four." Reject the inference from those two days, using the phase distributions. Then state what evidence in the series does legitimately support an immediacy claim.

**Problem 15.20 — Choose the design change that would help most**

Rank these three changes by how much each would strengthen the causal claim, and justify the ranking: extending each phase from 14 days to 28 days; adding a return-to-baseline phase after the intervention; running the same phase structure in four more students with staggered start dates.

### Level 6: Report and Critique

**Problem 15.21 — Write the result paragraph**

Using the verified values, write a results paragraph for Study 11. Include the case and phase structure, the level and trend of both series, the ordinal frequencies for stress, the nonoverlap statistics with the tie rule, and the design limitation.

**Problem 15.22 — Repair a generalization claim**

Repair this sentence: "The structured routine raises habit completion and lowers stress, with NAP values of .96 and .98." Preserve everything the study does support.

**Problem 15.23 — Repair an ordinal-scale report**

Repair this sentence: "Mean stress fell from 6.57 to 3.79, a decrease of 2.79 points on the stress scale." The arithmetic is correct. Identify what must be added or changed for the sentence to be defensible.

**Problem 15.24 — Write the limitation**

Write the four-sentence limitation for Study 11. One sentence must address the number of cases, one the single unreplicated phase change, one measurement reactivity, and one the maintenance phase specifically.

\newpage

## Solutions

### Level 1 Solutions

**Solution 15.1**

One case, 42 observations, and one independent unit for generalization.

The three answers differ because they count different things. The 42 rows are occasions of measurement, and they support a detailed description of how one person's behaviour moved over six weeks. The case is the entity whose behaviour is being described, and there is one. Generalization to other students requires variation across students, and this study contains none, so no number of additional days would create it. Decisive cue: ask what could be replicated. Another day is a repetition within the same case; another student is a replication of the case.

**Solution 15.2**

It is an A-B design with a follow-up or maintenance phase - baseline, intervention, then withdrawal of supports with continued measurement.

What it lacks is replication of the phase change. Stronger single-case designs repeat the introduction and removal of the condition within the same case (a reversal or A-B-A-B design) or stagger the introduction across several cases or settings (a multiple-baseline design). Both work the same way: they make a coincidence explanation harder, because a concurrent event would have to align with each phase change independently. With one change at one time, any event that happened in that same week explains the whole pattern equally well.

**Solution 15.3**

"Nonoverlap of all pairs reports the proportion of all baseline-by-comparison-phase pairs of observations in which the comparison observation is better than the baseline observation, with tied pairs counted as half." Under complete overlap, when the two phases are indistinguishable, it takes the value 0.5. When every comparison observation improves on every baseline observation, it takes the value 1.

**Solution 15.4**

An ordinal rating directly supports frequencies, the median, quartiles, the range, and any rank-based comparison, because all of these depend only on the ordering of the values. A mean, a standard deviation, and a mean difference require the additional assumption that the intervals between consecutive rating points are equal - that the step from 6 to 7 represents the same amount of stress as the step from 2 to 3. That assumption is not established by the scale and should be named whenever such a summary is reported. The verified record for this study marks its stress means and standard deviations as supplemental for exactly this reason.

### Level 2 Solutions

**Solution 15.5**

No intervention day is worse than any baseline day. The largest baseline value equals the smallest intervention value, so the two distributions touch at 4 and nowhere else, and every remaining pair favours the intervention day. NAP will therefore be very close to 1 - short of it only because the pairs at the point of contact are ties. The verified value is 0.959. Transfer cue: comparing the extremes of two phases tells you the shape of the overlap before any statistic is computed.

**Solution 15.6**

Ties occur only where both phases contain the same value, which here is only at 4. With two baseline days and eight intervention days at that value, there are 2 × 8 = 16 tied pairs out of 196.

The half-credit rule lowers NAP relative to a rule that discarded ties and computed the proportion among the remaining pairs, because those 16 pairs would then vanish and the remaining 180 would all favour the intervention, giving 1.000. Half credit treats a tie as evidence of neither improvement nor deterioration, which is the more honest treatment and the reason the rule must be stated when NAP is reported.

**Solution 15.7**

For the habit count, a declining baseline strengthens the claim. Habit completion was drifting slightly downward before the routine began, so an increase afterwards runs against the pre-existing direction and cannot be explained by simple continuation of the baseline trend.

For stress, a declining baseline weakens the claim, because stress was already falling. Some portion of the subsequent decline could be a continuation of what was already under way rather than an effect of the routine.

The asymmetry exists because a baseline trend is only a threat when it points in the same direction as the hoped-for change. The magnitudes matter too: over 14 days the baseline slopes imply drifts of about −0.43 habits and −0.80 rating points across the phase, both small relative to the observed level changes of +2.43 and −2.79, so the stress concern is real but modest.

**Solution 15.8**

With a mean difference of about 2.43, standard deviations near 1.0 and 1.1, and 14 observations per phase, the pooled standard error is roughly 0.40, giving a *t* near 6. The verified value is 6.02 with *p* < .001.

A small *p* value does not support the study's conclusion. It is produced by treating 28 days as 28 independent units, and its smallness is a direct consequence of that error: the more days are recorded, the more independent replications the test believes it has, and the smaller the *p* value becomes - without a single additional student having been observed.

### Level 3 Solutions

**Solution 15.9**

Habit count: 4.786 − 2.357 = +2.43 habits per day. Stress: 3.786 − 6.571 = −2.79 rating points.

The signs mean opposite things because the scales run in opposite directions. Higher habit counts are the desired outcome, so a positive level change is an improvement. Higher stress ratings are the undesired outcome, so a negative level change is an improvement. Both series therefore moved in the favourable direction, and any statistic reported for stress must have its direction convention stated or a reader cannot tell which sign is good news.

**Solution 15.10**

NAP = (180 × 1 + 16 × 0.5 + 0 × 0) / 196 = (180 + 8) / 196 = 188 / 196 = 0.959.

Every one of the 196 pairs is counted exactly once, so the denominator is the total number of baseline-by-intervention pairings, 14 × 14. The 16 ties contribute 8, which is what pulls the value below 1.

**Solution 15.11**

NAP = (189 × 1 + 7 × 0.5) / 196 = (189 + 3.5) / 196 = 192.5 / 196 = 0.982.

The direction convention has to be stated for stress because improvement means a *lower* value. Without that statement, a reader cannot tell whether 0.982 means that intervention days were mostly lower - which is the intended reading - or mostly higher. For the habit count the desirable direction is upward and coincides with the numerical ordering, so the convention is less likely to be misread, but stating it there too costs nothing and prevents an error when the two outcomes are reported side by side.

**Solution 15.12**

A baseline-to-maintenance NAP of 1.000 for stress means that every one of the 196 pairings of a baseline day with a maintenance day showed the maintenance day at a lower stress rating, with no ties. The two phases do not overlap at all: the lowest baseline rating, 6, is above the highest maintenance rating, 4.

It does not mean the change was large. NAP measures separation, not magnitude. Two phases could separate completely with a difference of one rating point, and they would earn the same 1.000. The magnitude comes from the medians, 6.5 against 3.0, and the frequency table, and it must be reported alongside the nonoverlap statistic rather than inferred from it.

### Level 4 Solutions

**Solution 15.13**

The habit series rises across the three phases: median 2.0 in baseline, 4.0 in intervention, 5.0 in maintenance. Baseline drifts slightly downward (slope −0.033) while intervention drifts slightly upward (+0.068), so the change at the first phase boundary runs against the pre-existing direction. Maintenance holds the higher level with a slight downward slope (−0.095).

The stress series falls across the three phases: median 6.5, then 4.0, then 3.0. Baseline is already declining slightly (−0.062), intervention declines more steeply (−0.160), and maintenance is flat to slightly rising (+0.077), which is consistent with the level settling rather than continuing to fall.

The maintenance habit phase has the widest range, from 3 to 9 against baseline's 1 to 4 and intervention's 4 to 7. That widening could reflect genuinely more variable behaviour once the external structure was removed, a single unusually productive day, or ordinary variation in a 14-day window. A range is driven by two observations, so the phase's quartiles - 5.0 and 6.0, an interquartile range of 1, the same as the other two phases - are the better guide to whether the middle of the distribution has actually spread out. Here it has not.

**Solution 15.14**

The frequency table shows the *shape* of each phase's distribution, not only its centre. Baseline stress occupied only three values, 6, 7, and 8, with no day below 6. Intervention spread across 2 to 6 with a mode at 4. Maintenance occupied 1 to 4 with a mode at 3. Phase means would show three numbers falling; the frequency table additionally shows that the phases are almost disjoint, that baseline had no good days at all rather than a mixture, and that variability changed shape rather than merely shrinking.

Baseline and intervention touch at the single value 6: seven baseline days and one intervention day sit there, which accounts for the 7 tied pairs in the nonoverlap calculation.

#### Study in the Larger Evidence Program: One Student's Routine

- **What this study adds:** A detailed, reproducible description of how one student's habit completion and stress ratings moved across the introduction and withdrawal of a structured routine, with near-complete phase separation on both outcomes.
- **What it cannot settle:** Whether the routine caused the change for this student, and anything at all about any other student.
- **Causal-support role:** Weak responsiveness evidence. Something was deliberately introduced at a known time, which is more than an observational study offers, but the change was not replicated or withdrawn, so a concurrent event explains the pattern equally well.
- **Next evidence priority:** A multiple-baseline design across four or five students with staggered start dates, so that the change must coincide with each case's own phase boundary rather than with one calendar week.

**Solution 15.15**

Introducing the routine coincided with near-complete separation on both outcomes: nonoverlap of all pairs was .96 for habit count and .98 for stress improvement, with no baseline-intervention pair favouring the baseline day in either series and the shortfall from 1.00 due entirely to tied pairs. Separation was as strong or stronger against the maintenance phase (.974 and 1.000).

After the supports were withdrawn, neither outcome returned toward baseline; both continued to improve modestly, with intervention-to-maintenance NAP values of 0.684 for habit count and 0.750 for stress. Those values are well above 0.5, indicating continued gain, but far below the baseline contrasts, indicating that the two later phases substantially overlap - the maintenance phase is better than the intervention phase on most pairs of days, not on nearly all of them.

**Solution 15.16**

The 26 asserts that the analysis has 28 independent observations from which two group means were estimated. That assertion is not true. The study contains one case measured on 28 occasions; the days are serially related to one another and all share the characteristics of a single person.

The one quantity that remains defensible is the mean difference between phases - 2.43 habits per day and −2.79 rating points - as a *description* of what the two phases looked like for this student. The standardized effect sizes of 2.28 and −3.04 are borderline: they are computed from a within-phase standard deviation that describes day-to-day variability in one person, so they should not be read against benchmarks built for between-person comparisons. The *t* statistics, the degrees of freedom, and the *p* values describe an inference the design cannot support and should not be reported at all.

### Level 5 Solutions

**Solution 15.17**

The primary analysis is a chronological plot of each series with the phase boundaries marked, read for level, trend, variability, and immediacy of change. That is what should be presented first, because every feature that distinguishes a convincing single-case result from an unconvincing one is visible in the sequence and invisible in any summary.

The quantitative support is the set of phase-level summaries - median, quartiles, range, and slope for each phase - together with the nonoverlap statistics with their tie rule and direction conventions stated, and the ordinal frequency table for stress.

What should be refused entirely is any between-groups inferential test on days, and any *p* value or confidence interval presented as if the 42 observations were independent units. Descriptive means for the ordinal stress outcome may be reported but must be marked supplemental with the equal-interval assumption named.

**Solution 15.18**

The violated assumption is independence of observations within groups, which an independent-samples *t* test requires in order for the standard error to describe the variability of the estimate under replication.

Two distinct sources of dependence are present. The first is serial dependence: consecutive days in one person's life are related, so day 8 carries information about day 9, and the effective amount of independent information is smaller than the number of rows. The second is the single case itself: all 28 observations come from one person, so everything stable about that person - their baseline capacity, their scale use, their circumstances that week - is common to every row and is never sampled.

A more extreme *p* value makes the error more serious because the size of the error grows with the number of observations. Recording the same student for 84 days instead of 28 would roughly triple the apparent degrees of freedom and shrink the *p* value further, while adding no new independent unit whatsoever. A result that becomes more impressive as the underlying justification stays constant is a warning, not a confirmation.

**Solution 15.19**

The last baseline day happened to be 1, the minimum value of the entire baseline phase, and the first intervention day was 5, which sits above the intervention median of 4.0, at that phase's third quartile. The apparent jump of four is therefore a comparison of an unusually low day with a fairly typical one, and it exaggerates the change. Comparing the phase medians of 2.0 and 4.0 gives a difference of two, and the level change in means is 2.43. Any two adjacent days can differ by three in a series whose baseline already ranges from 1 to 4.

What legitimately supports an immediacy claim is the behaviour of the whole distribution at the boundary rather than the boundary pair: the intervention phase's minimum, 4, equals the baseline phase's maximum, so from the very first intervention day onward every value sits at or above everything seen in the baseline phase, and no intervention day falls into the baseline range. That is a statement about all 14 days, and it does not depend on which day happened to be last.

**Solution 15.20**

Ranked from most to least helpful.

*Running the same phase structure in four more students with staggered start dates* helps most. It adds independent units, which is the one thing this study entirely lacks, and staggering makes a concurrent-event explanation implausible because the change would have to arrive at each student's own boundary. It addresses both the causal weakness and the generalization boundary.

*Adding a return-to-baseline phase* helps second. It replicates the phase change within the case, so a concurrent event would have to arrive and then depart on schedule. It addresses the causal weakness but adds no new case and so does nothing for generalization, and it may be unacceptable if withdrawing a beneficial routine harms the participant.

*Extending each phase to 28 days* helps least. Longer phases give more stable estimates of level and trend and make the series easier to read, which is worth something. They add no replication of the phase change and no new case, so the causal claim and the generalization boundary are exactly where they were. This is the change most likely to be mistaken for an improvement in evidence because it increases the number of rows.

#### Study in the Larger Evidence Program: What Replication Would Add

- **What this study adds:** As a single case, it contributes a well-documented instance and a demonstration that phase separation can be near-total on both outcomes.
- **What it cannot settle:** Whether the pattern is attributable to the routine, and whether it would appear in anyone else. Neither gap closes with more days.
- **Causal-support role:** Weak responsiveness evidence from one deliberate, unreplicated introduction.
- **Next evidence priority:** Four or five cases with staggered baselines. If each case's change arrives at that case's own phase boundary, a single concurrent event stops being a credible explanation, and the accumulation of cases begins to address generality.

### Level 6 Solutions

**Solution 15.21**

One student recorded daily habit completion and a daily ordinal stress rating for 42 consecutive days, in three consecutive 14-day phases: baseline, a structured routine, and a maintenance phase in which the supports were withdrawn. Habit count rose across the phases, with medians of 2.0, 4.0, and 5.0 and phase ranges of 1-4, 4-7, and 3-9; the baseline trend was slightly negative (−0.033 per day), so the increase ran against the pre-existing direction. Stress ratings fell, with medians of 6.5, 4.0, and 3.0; baseline ratings occupied only the values 6 to 8, intervention ratings 2 to 6, and maintenance ratings 1 to 4. Nonoverlap of all pairs, with tied pairs credited 0.5, was .96 for habit count and .98 for stress improvement from baseline to intervention, and .97 and 1.00 respectively from baseline to maintenance; intervention-to-maintenance values were .68 and .75. Means and standard deviations for the ordinal stress rating are reported as supplemental summaries and assume equal spacing between adjacent rating points. Because the study involves one case and one unreplicated phase change, these results describe what happened for this student and do not establish that the routine caused the change or that it would produce a similar pattern in anyone else.

**Solution 15.22**

Repaired: "For this student, habit completion rose and stress ratings fell when the structured routine was introduced, with nonoverlap of all pairs of .96 and .98 against the baseline phase. Because the routine was introduced once in a single case, with no withdrawal and no replication in other students, the design cannot establish that the routine produced the change, and the result says nothing about how another student would respond."

The original sentence makes two jumps at once. The present tense - "raises," "lowers" - converts one person's series into a general property of the routine, and the absence of any subject makes the claim about students in general. Both are unsupported by a single unreplicated case, however clean its numbers.

**Solution 15.23**

The arithmetic is right: 6.571 − 3.786 = 2.79. Two things must change.

First, the sentence treats an ordinal rating as an interval scale. A mean of an ordinal variable, and a difference between two such means, require the assumption that the distance from 6 to 7 equals the distance from 2 to 3. That assumption is not established by a self-report rating scale and must be stated when the summary is used.

Second, better summaries are available and should lead. The medians, 6.5 and 4.0, and the frequency distributions convey the change without any additional assumption, and the frequencies convey more: baseline occupied only 6, 7, and 8, while intervention spread from 2 to 6.

Defensible version: "Stress ratings fell from a baseline median of 6.5, with all 14 days between 6 and 8, to an intervention median of 4.0, with days spread from 2 to 6. The corresponding means are 6.57 and 3.79; these are reported as supplemental summaries and assume equal spacing between adjacent points of the ordinal rating scale."

**Solution 15.24**

"The study describes one case, so it provides no basis for expecting a similar pattern in another student, and no increase in the number of recorded days would change that. The routine was introduced once and never withdrawn or reintroduced, so any event coinciding with that single phase boundary - a change in workload, sleep, health, or circumstances during that week - explains the whole pattern as well as the routine does. Because the student recorded both outcomes daily throughout, the act of measurement may itself have influenced the behaviour being measured, and that influence was present in every phase including the baseline. Finally, the maintenance phase shows that the improved level held for two weeks after the supports were withdrawn, which is a short follow-up window and cannot speak to whether the pattern would persist over a term or a year."

\newpage
