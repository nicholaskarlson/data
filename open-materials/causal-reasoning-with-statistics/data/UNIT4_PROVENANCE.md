# Unit 4 synthetic-data provenance

`unit4_cluster_sleep_trial.csv` is an original synthetic teaching file with 2,400 fictional students nested in 48 fictional residence floors. `scripts/generate_unit4.py` uses Python `random.Random(20260916)` and the structural equations recorded in `dictionaries/unit4_cluster_sleep_trial_dictionary.json`. No real, copied, reconstructed, pseudonymized, or inferred participant record was used.

Within each of four campus sectors, the generator selects exactly 6 of 12 floors for the sleep-support program. All 50 students on a floor inherit its assignment. The assignment effect built into the simulator is a constant 3 attention-score points, but this hidden parameter is a reproducibility test—not evidence available to an analyst and not a claim about human sleep or attention.

The primary eight-week attention outcome is complete. Sleep-plan use occurs after assignment and includes both nonuse in assigned floors and contamination in comparison floors. The optional sleep diary is also post-assignment: blank `followup_sleep_hours` values occur exactly when `completed_sleep_diary=0`. The diary outcome is secondary and is not substituted for the complete primary outcome.

The preferred ITT analysis aggregates the 2,400 student rows to 48 floor means, preserves the campus-sector blocks, and bases HC1 uncertainty on randomized floors. Individual-row HC1 results are retained only to show why a correct point estimate can have an incorrectly narrow standard error when clustering is ignored. Dataset SHA-256: `bb7193e772ef1669fe6849d06ba95c802305b4d4d2ec97a75683a1763056bdf2`.
