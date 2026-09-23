# Unit 2 synthetic-data provenance

`unit2_multisite_workshop_offer.csv` is an original synthetic teaching file with 2,400 fictional rows. `scripts/generate_unit2.py` uses Python `random.Random(20260915)`, fixed site sample sizes, and the structural equations recorded in `dictionaries/unit2_multisite_workshop_dictionary.json`. No real, copied, reconstructed, pseudonymized, or inferred participant record was used.

The generator alone knows who would attend if offered and the site-specific structural effects. The analyst CSV records randomized offer, observed attendance, baseline stress, site, and observed outcome; it contains neither counterfactual attendance nor both potential outcomes. Primary NumPy and independent standard-library verifiers use raw CSV input. Dataset SHA-256: `5cb72926edd601aaeb1288a33c4394cca0a641378b74546cab9020f850c7abf2`.

Within each site, the generator assigns the offer independently with probability 0.50; it does not force exactly half of a site's rows into each arm. The realized offer counts are 557 of 1,200 at Cedar, 365 of 720 at Lake, and 262 of 480 at Ridge. Those chance differences make the raw pooled contrast differ from the recruited-site-share standardized contrast in this dataset.

The recruited-sample estimand is the intention-to-treat effect of the offer. The pooled contrast and the recruited-site-share standardized contrast are alternative estimators of that sample effect. The primary planning estimand instead standardizes site-specific offer effects to fixed target weights 0.25 Cedar, 0.35 Lake, and 0.40 Ridge. That transport step assumes the recruited within-site effects apply to the target within site; randomization alone does not establish it.
