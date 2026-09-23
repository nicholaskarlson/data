# Unit 7 synthetic-data provenance

`unit7_tutoring_cutoff.csv` and `unit7_tutoring_encouragement.csv` are original synthetic teaching datasets generated together by `scripts/generate_unit7.py` with Python `random.Random(20260920)`. No real, copied, reconstructed, pseudonymized, or inferred student record was used. The two files deliberately represent different designs and populations; they are not two analyses of one study.

The cutoff file contains 2,600 fictional tutoring applicants. A pre-tutoring diagnostic score is the running variable, and eligibility changes sharply below the cutoff of 60. The primary analysis prespecifies a bandwidth of 6 score points and fits separate local linear slopes on the two sides with HC1 uncertainty. Bandwidths 4, 6, 8, and 10 are reported as sensitivity analyses. A local count comparison checks for obvious bunching within two points of the cutoff, baseline GPA checks pre-intervention continuity, and a false cutoff of 70 checks for a discontinuity where eligibility does not change. These diagnostics can reveal some threats; they cannot prove the continuity conditions.

The encouragement file contains 3,000 fictional students, exactly 1,500 randomly assigned an encouragement and 1,500 assigned no encouragement. Receipt follows hidden always-taker, complier, and never-taker response types; the generator contains no defiers and gives encouragement no direct outcome effect. The analysis reports the assignment ITT, first stage, reduced form, first-stage F statistic, and Wald ratio with a joint influence-function delta-method standard error. The observed data do not reveal each student's principal stratum. The Wald interpretation therefore remains conditional on relevance, random-assignment independence, exclusion, and monotonicity.

The generator-defined RD discontinuity and complier effect test computational recovery. They are hidden simulator parameters, not analyst evidence and not findings about real tutoring programs. The primary NumPy, standard-library Python, and base-R paths independently reconstruct both designs and their displayed results.

Dataset SHA-256 values:

- `unit7_tutoring_cutoff.csv`: `f1c355714cae927978aeea95641fb7e3d96efa4b1b57f30d27522d7418c87a35`
- `unit7_tutoring_encouragement.csv`: `62f37ff913d10578164601f0c553850528c64750083395bd5d6daabc9637852c`
