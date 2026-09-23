#!/usr/bin/env Rscript

# Independent base-R verification of the v1.0 revision addenda.
#
# Base R cannot reproduce Python's pseudo-random stream, so this script does not
# replay the Unit 5 generator. It audits the estimation instead: it refits the
# latent-engagement gap from the published Unit 5 file plus the replayed
# engagement column, and recomputes the Unit 9 expected misclassification
# contrast from the generator's documented cell risks and error rates.

args <- commandArgs(trailingOnly = TRUE)
stopifnot(length(args) == 1)
resource <- normalizePath(args[[1]])
tolerance <- 0.000002

# ---------------------------------------------------------------- Unit 9 ----
cell_n <- c(1000, 400, 800, 400, 500, 400, 200, 300)
control_risk <- c(0.42, 0.28, 0.39, 0.25, 0.36, 0.23, 0.34, 0.20)
risk_difference <- c(0.10, 0.16, 0.12, 0.18, 0.14, 0.20, 0.16, 0.22)
sensitivity_program <- 0.91
sensitivity_comparison <- 0.82
specificity_program <- 0.84
specificity_comparison <- 0.90

weight <- cell_n / sum(cell_n)
risk_program <- control_risk + risk_difference
expected_program <- sum(weight * (risk_program * sensitivity_program +
                                  (1 - risk_program) * (1 - specificity_program)))
expected_comparison <- sum(weight * (control_risk * sensitivity_comparison +
                                     (1 - control_risk) * (1 - specificity_comparison)))
expected_difference <- expected_program - expected_comparison
hidden_difference <- sum(weight * risk_program) - sum(weight * control_risk)
expected_excess <- expected_difference - hidden_difference

stopifnot(
  abs(expected_comparison - 0.341920) < tolerance,
  abs(expected_program - 0.520750) < tolerance,
  abs(expected_difference - 0.178830) < tolerance,
  abs(hidden_difference - 0.145000) < tolerance,
  abs(expected_excess - 0.033830) < tolerance
)

# --------------------------------------------------------------- Unit 10 ----
unit5 <- read.csv(file.path(resource, "data", "unit5_hypertension_coaching.csv"))
replay <- read.csv(file.path(resource, "data", "unit10_latent_engagement_replay.csv"))
stopifnot(nrow(unit5) == nrow(replay))
order_index <- match(unit5$participant_id, replay$participant_id)
stopifnot(!any(is.na(order_index)))

frame <- data.frame(
  u = replay$latent_engagement[order_index],
  a = as.numeric(unit5$joined_coaching),
  b10 = (unit5$baseline_sbp - 137) / 10,
  age10 = (unit5$age_years - 54) / 10,
  smoker = as.numeric(unit5$current_smoker),
  medication = as.numeric(unit5$taking_bp_medication),
  transport = as.numeric(unit5$transport_barrier),
  mesa = as.numeric(unit5$clinic == "Mesa"),
  river = as.numeric(unit5$clinic == "River")
)

fit <- lm(u ~ a + b10 + age10 + smoker + medication + transport + mesa + river + a:b10,
          data = frame)
under_one <- frame
under_zero <- frame
under_one$a <- 1
under_zero$a <- 0
delta <- mean(predict(fit, under_one) - predict(fit, under_zero))

structural_gamma <- -2.2
contribution <- structural_gamma * delta
reported_estimate <- -6.141777
hidden_sample_ate <- -4.226561
adjusted <- reported_estimate - contribution
remaining <- adjusted - hidden_sample_ate

stopifnot(
  abs(delta - 0.672803) < tolerance,
  abs(contribution - (-1.480166)) < tolerance,
  abs(adjusted - (-4.661611)) < tolerance,
  abs(remaining - (-0.435050)) < tolerance
)

cat(sprintf(
  "R_CAUSAL_ADDENDA expected_self_report_rd=%.6f expected_excess=%.6f delta=%.6f adjusted=%.6f remaining=%.6f\n",
  expected_difference, expected_excess, delta, adjusted, remaining))
cat("R_CAUSAL_ADDENDA_OK", R.version.string, "\n")
