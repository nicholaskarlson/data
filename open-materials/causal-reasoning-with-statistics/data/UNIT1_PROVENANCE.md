# Unit 1 synthetic-data provenance

`unit1_library_interface_ab.csv` is an original synthetic teaching file with 1,800 fictional rows. `scripts/generate_unit1.py` uses Python `random.Random(20260914)` and the fixed equations recorded in `dictionaries/unit1_library_interface_dictionary.json`. No real, copied, reconstructed, pseudonymized, or inferred student record was used.

The generator defines both potential task scores from shared noise and gives every fictional student a 4-point assignment effect. Only the score selected by randomized interface assignment appears in the analyst CSV. Click count is post-assignment behavior, not a treatment or pre-assignment adjustment variable. The primary and independent verifiers read the CSV without importing the generator. Dataset SHA-256: `33127d2292ab8303ab78651ecb6804f47227ee2aef047f55c11b597ad554ebd5`.

The target is the average effect of assignment to the precisely described redesigned versus standard interface in the fictional randomized cohort. A real implementation would require version consistency, verified randomization, valid scoring, outcome completeness, absence of relevant interference, and a separate argument for generalization.
