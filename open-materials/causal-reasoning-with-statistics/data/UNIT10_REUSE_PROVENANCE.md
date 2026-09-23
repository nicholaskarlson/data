# Unit 10 reuse and planning provenance

Unit 10 creates no new participant-level dataset. Its residual-confounding
sensitivity analysis reads the committed Unit 5 result record and reuses the
deterministic Unit 5 hypertension-coaching CSV. The record stores SHA-256
digests for both inputs, so a changed source cannot silently retain the same
Unit 10 result.

The precision example is a prospective design exercise, not a reanalysis of
Unit 4 and not evidence about an actual intraclass correlation. It rounds the
Unit 5 outcome-regression residual scale upward to a planning standard
deviation of 7.1 mmHg, assumes 50 participants per cluster, equal allocation,
two-sided alpha 0.05, power 0.80, and ICC scenarios 0.05, 0.10, and 0.20.
Those ICCs are design inputs selected to expose sensitivity. They are not
estimated from any book dataset.

The cross-case synthesis uses the verified claims and limitations already
printed in Units 5, 6, 7, and 9. It does not pool their estimates because the
interventions, outcomes, populations, and estimands differ. Matching, Unit 4
ICC/design-effect and cluster-robust diagnostics, and a genuine Unit 6
event-study remain separately reviewable hardening decisions.
