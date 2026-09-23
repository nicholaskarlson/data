#!/usr/bin/env Rscript

# Independent base-R verification for Unit 8.
args <- commandArgs(trailingOnly = TRUE)
resource <- if (length(args) >= 1) args[[1]] else normalizePath(file.path(dirname(sys.frame(1)$ofile), ".."))
data_path <- file.path(resource, "data", "unit8_cognitive_training_trial.csv")
data <- read.csv(data_path, stringsAsFactors = FALSE)
tolerance <- 0.000002
z975 <- 1.959963985

hc1_fit <- function(x, y) {
  x <- as.matrix(x)
  y <- as.numeric(y)
  beta <- solve(crossprod(x), crossprod(x, y))
  residual <- y - as.vector(x %*% beta)
  bread <- solve(crossprod(x))
  meat <- crossprod(x, x * residual^2)
  n <- nrow(x)
  p <- ncol(x)
  covariance <- n / (n - p) * bread %*% meat %*% bread
  list(beta = beta, covariance = covariance)
}

contrast <- function(fit, weights) {
  weights <- as.numeric(weights)
  estimate <- as.numeric(crossprod(weights, fit$beta))
  se <- sqrt(as.numeric(t(weights) %*% fit$covariance %*% weights))
  c(estimate, se, estimate - z975 * se, estimate + z975 * se)
}

check <- function(actual, expected, label) {
  if (any(abs(actual - expected) > tolerance)) {
    stop(sprintf("R_CAUSAL_UNIT8_ERROR %s: %s != %s", label,
                 paste(actual, collapse = ","), paste(expected, collapse = ",")))
  }
}

stopifnot(nrow(data) == 3200)
stopifnot(identical(names(data), c(
  "participant_id", "training_assignment", "baseline_memory_score",
  "baseline_high_anxiety", "strategy_use_score", "followup_memory_score"
)))
stopifnot(all(data$training_assignment %in% c(0, 1)))
stopifnot(all(data$baseline_high_anxiety %in% c(0, 1)))
stopifnot(!anyNA(data))
allocation <- with(data, table(baseline_high_anxiety, training_assignment))
stopifnot(all(allocation == matrix(c(960, 640, 960, 640), nrow = 2)))
stopifnot(abs(mean(data$baseline_high_anxiety) - 0.4) <= tolerance)

a <- data$training_assignment
b <- data$baseline_memory_score
w <- data$baseline_high_anxiety
m <- data$strategy_use_score
y <- data$followup_memory_score
n <- nrow(data)

naive <- hc1_fit(cbind(1, a), y)
total <- hc1_fit(cbind(1, a, b, w, a * w), y)
first <- hc1_fit(cbind(1, a, b, w), m)
conditioned <- hc1_fit(cbind(1, a, b, w, a * w, m), y)

results <- list(
  unadjusted_assignment_itt = contrast(naive, c(0, 1)),
  baseline_adjusted_standardized_total_effect = contrast(total, c(0, 1, 0, 0, mean(w))),
  total_effect_low_anxiety = contrast(total, c(0, 1, 0, 0, 0)),
  total_effect_high_anxiety = contrast(total, c(0, 1, 0, 0, 1)),
  assignment_by_anxiety_interaction = contrast(total, c(0, 0, 0, 0, 1)),
  assignment_effect_on_strategy_use = contrast(first, c(0, 1, 0, 0)),
  mediator_conditioned_assignment_contrast = contrast(conditioned, c(0, 1, 0, 0, mean(w), 0)),
  strategy_outcome_conditional_association = contrast(conditioned, c(0, 0, 0, 0, 0, 1))
)

expected <- list(
  unadjusted_assignment_itt = c(4.965623, 0.354450, 4.270914, 5.660332),
  baseline_adjusted_standardized_total_effect = c(5.046857, 0.270686, 4.516323, 5.577391),
  total_effect_low_anxiety = c(5.649883, 0.350549, 4.962820, 6.336946),
  total_effect_high_anxiety = c(4.142318, 0.425958, 3.307457, 4.977180),
  assignment_by_anxiety_interaction = c(-1.507565, 0.551648, -2.588776, -0.426353),
  assignment_effect_on_strategy_use = c(7.051006, 0.226065, 6.607926, 7.494086),
  mediator_conditioned_assignment_contrast = c(0.298119, 0.256514, -0.204639, 0.800877),
  strategy_outcome_conditional_association = c(0.673484, 0.017477, 0.639229, 0.707738)
)
for (name in names(expected)) check(results[[name]], expected[[name]], name)

legacy_product <- results$assignment_effect_on_strategy_use[1] *
  results$strategy_outcome_conditional_association[1]
legacy_total_minus_conditioned <-
  results$baseline_adjusted_standardized_total_effect[1] -
  results$mediator_conditioned_assignment_contrast[1]
check(legacy_product, 4.748738, "legacy product of coefficients")
check(legacy_total_minus_conditioned, 4.748738, "legacy total minus conditioned")
check(legacy_product - 3.15, 1.598738, "legacy excess over hidden component")

check(mean(y[a == 1]), 71.980487, "outcome mean assigned")
check(mean(y[a == 0]), 67.014864, "outcome mean comparison")
check(mean(m[a == 1]), 46.337810, "mediator mean assigned")
check(mean(m[a == 0]), 39.310749, "mediator mean comparison")
check(5.65 * 0.6 + 4.15 * 0.4, 5.05, "known average total effect")
check(2.5 * 0.6 + 1.0 * 0.4, 1.9, "known average controlled direct effect")
check(0.45 * 7.0, 3.15, "known mediated component")

cat(sprintf(
  "R_CAUSAL_UNIT8_TOTAL estimate=%.6f se=%.6f low=%.6f high=%.6f interaction=%.6f\n",
  results$baseline_adjusted_standardized_total_effect[1],
  results$baseline_adjusted_standardized_total_effect[2],
  results$total_effect_low_anxiety[1], results$total_effect_high_anxiety[1],
  results$assignment_by_anxiety_interaction[1]
))
cat(sprintf(
  "R_CAUSAL_UNIT8_MEDIATION first_stage=%.6f conditioned=%.6f mediator_association=%.6f\n",
  results$assignment_effect_on_strategy_use[1],
  results$mediator_conditioned_assignment_contrast[1],
  results$strategy_outcome_conditional_association[1]
))
cat(sprintf(
  "R_CAUSAL_UNIT8_LEGACY product=%.6f total_minus_conditioned=%.6f excess_over_hidden_component=%.6f\n",
  legacy_product, legacy_total_minus_conditioned, legacy_product - 3.15
))
cat("R_CAUSAL_UNIT8_INDEPENDENT_OK", R.version.string, "\n")
