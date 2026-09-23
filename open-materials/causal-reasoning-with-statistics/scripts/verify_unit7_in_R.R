#!/usr/bin/env Rscript
# Independent base-R audit for Unit 7 regression discontinuity and IV.

args <- commandArgs(trailingOnly=TRUE)
resource <- if (length(args) >= 1) args[[1]] else "."
rd <- read.csv(file.path(resource, "data", "unit7_tutoring_cutoff.csv"), stringsAsFactors=FALSE)
iv <- read.csv(file.path(resource, "data", "unit7_tutoring_encouragement.csv"), stringsAsFactors=FALSE)
z_975 <- 1.959963985
tolerance <- 0.000002

stopifnot(nrow(rd) == 2600)
stopifnot(nrow(iv) == 3000)
stopifnot(sum(iv$encouragement_assignment) == 1500)
stopifnot(all(rd$tutoring_eligible == as.integer(rd$diagnostic_score < 60)))
stopifnot(all(abs(rd$centered_score - (rd$diagnostic_score - 60)) <= tolerance))
stopifnot(!any(rd$diagnostic_score == 60))

hc1 <- function(fit) {
  x <- model.matrix(fit)
  residual <- residuals(fit)
  bread <- solve(crossprod(x))
  meat <- crossprod(x, x * residual^2)
  n <- nrow(x)
  p <- ncol(x)
  n / (n - p) * bread %*% meat %*% bread
}

rd_fit <- function(data, outcome, cutoff, bandwidth) {
  local <- data[abs(data$diagnostic_score - cutoff) <= bandwidth, ]
  local$x <- local$diagnostic_score - cutoff
  local$below <- as.integer(local$x < 0)
  fit <- lm(as.formula(paste(outcome, "~ below + x + below:x")), data=local)
  covariance <- hc1(fit)
  estimate <- unname(coef(fit)["below"])
  se <- sqrt(covariance["below", "below"])
  c(estimate, se, estimate - z_975 * se, estimate + z_975 * se, nrow(local))
}

difference_fit <- function(data, variable) {
  z <- data$encouragement_assignment
  values <- data[[variable]]
  mean1 <- mean(values[z == 1])
  mean0 <- mean(values[z == 0])
  p <- mean(z)
  influence <- ifelse(z == 1, (values - mean1) / p, -(values - mean0) / (1 - p))
  se <- sqrt(sum(influence^2) / (nrow(data) * (nrow(data) - 1)))
  list(estimate=mean1 - mean0, se=se, influence=influence, mean1=mean1, mean0=mean0)
}

as_interval <- function(estimate, se) {
  c(estimate, se, estimate - z_975 * se, estimate + z_975 * se)
}

rd_primary <- rd_fit(rd, "end_term_math_score", 60, 6)
rd_baseline <- rd_fit(rd, "baseline_gpa", 60, 6)
rd_placebo <- rd_fit(rd, "end_term_math_score", 70, 5)
rd_expected <- list(
  primary=c(3.916504, 0.606807, 2.727184, 5.105823, 1197),
  baseline=c(0.016336, 0.038664, -0.059444, 0.092117, 1197),
  placebo=c(-0.923789, 0.824922, -2.540606, 0.693028, 634)
)
stopifnot(all(abs(rd_primary - rd_expected$primary) <= tolerance))
stopifnot(all(abs(rd_baseline - rd_expected$baseline) <= tolerance))
stopifnot(all(abs(rd_placebo - rd_expected$placebo) <= tolerance))

bandwidth_expected <- list(
  `4`=c(4.407065, 0.739792, 2.957099, 5.857031, 825),
  `6`=c(3.916504, 0.606807, 2.727184, 5.105823, 1197),
  `8`=c(3.713136, 0.523436, 2.687220, 4.739053, 1499),
  `10`=c(3.584986, 0.471738, 2.660397, 4.509575, 1776)
)
for (bandwidth in c(4, 6, 8, 10)) {
  fresh <- rd_fit(rd, "end_term_math_score", 60, bandwidth)
  stopifnot(all(abs(fresh - bandwidth_expected[[as.character(bandwidth)]]) <= tolerance))
}

local_density <- rd[abs(rd$centered_score) <= 2, ]
below <- sum(local_density$centered_score < 0)
above <- sum(local_density$centered_score >= 0)
density_z <- (below - above) / sqrt(below + above)
density_p <- 2 * pnorm(-abs(density_z))
stopifnot(below == 191)
stopifnot(above == 202)
stopifnot(abs(below / above - 0.945545) <= tolerance)
stopifnot(abs(density_z - (-0.554877)) <= tolerance)
stopifnot(abs(density_p - 0.578979) <= tolerance)

# Exact anchors are inserted after the deterministic data and primary record are built.
reduced <- difference_fit(iv, "end_term_math_score")
first <- difference_fit(iv, "tutoring_received")
wald <- reduced$estimate / first$estimate
wald_influence <- (reduced$influence - wald * first$influence) / first$estimate
wald_se <- sqrt(sum(wald_influence^2) / (nrow(iv) * (nrow(iv) - 1)))

stopifnot(all(abs(as_interval(reduced$estimate, reduced$se) - c(
  2.938372, 0.306779, 2.337096, 3.539648
)) <= tolerance))
stopifnot(all(abs(as_interval(first$estimate, first$se) - c(
  0.572667, 0.014502, 0.544243, 0.601090
)) <= tolerance))
stopifnot(all(abs(as_interval(wald, wald_se) - c(
  5.131034, 0.515759, 4.120165, 6.141903
)) <= tolerance))
stopifnot(abs(reduced$mean1 - 85.728952) <= tolerance)
stopifnot(abs(reduced$mean0 - 82.790580) <= tolerance)
stopifnot(abs(first$mean1 - 0.684667) <= tolerance)
stopifnot(abs(first$mean0 - 0.112000) <= tolerance)
stopifnot(abs(sum(c(first$mean0, first$estimate, 1 - first$mean1)) - 1) <= tolerance)
stopifnot(abs((first$estimate / first$se)^2 - 1559.378814) <= 0.000002)
stopifnot(abs(4.2 - 4.2) <= tolerance)
stopifnot(abs(5.2 - 5.2) <= tolerance)

cat(sprintf(
  "R_CAUSAL_UNIT7_RD estimate=%.6f se=%.6f ci95=[%.6f,%.6f] n_local=%d\n",
  rd_primary[1], rd_primary[2], rd_primary[3], rd_primary[4], as.integer(rd_primary[5])
))
cat(sprintf(
  "R_CAUSAL_UNIT7_RD_BASELINE estimate=%.6f se=%.6f ci95=[%.6f,%.6f]\n",
  rd_baseline[1], rd_baseline[2], rd_baseline[3], rd_baseline[4]
))
cat(sprintf(
  "R_CAUSAL_UNIT7_RD_PLACEBO estimate=%.6f se=%.6f ci95=[%.6f,%.6f]\n",
  rd_placebo[1], rd_placebo[2], rd_placebo[3], rd_placebo[4]
))
cat(sprintf(
  "R_CAUSAL_UNIT7_IV first_stage=%.6f reduced_form=%.6f wald=%.6f wald_se=%.6f first_stage_f=%.3f\n",
  first$estimate, reduced$estimate, wald, wald_se, (first$estimate / first$se)^2
))
cat("R_CAUSAL_UNIT7_INDEPENDENT_OK", R.version.string, "\n")
