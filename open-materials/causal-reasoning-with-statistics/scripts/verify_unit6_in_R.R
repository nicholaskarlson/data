#!/usr/bin/env Rscript
# Independent base-R audit for Unit 6 difference-in-differences and ITS.

args <- commandArgs(trailingOnly=TRUE)
resource <- if (length(args) >= 1) args[[1]] else "."
path <- file.path(resource, "data", "unit6_youth_crisis_policy.csv")
d <- read.csv(path, stringsAsFactors=FALSE)
outcome <- "youth_emergency_transports_per_10000"
t_cluster_23 <- 2.06865761
t_hac_30 <- 2.042272456
tolerance <- 0.000002

stopifnot(nrow(d) == 864)
stopifnot(length(unique(d$municipality_id)) == 24)
stopifnot(all(table(d$municipality_id) == 36))
stopifnot(all(table(d$month_index) == 24))
stopifnot(length(unique(d$municipality_id[d$early_adopter == 1])) == 12)
stopifnot(all(d$relative_month == d$month_index - 19))
stopifnot(all(d$regional_hotline_active == as.integer(d$month_index >= 19)))
stopifnot(all(d$policy_active == d$early_adopter * as.integer(d$month_index >= 19)))
stopifnot(all(is.finite(d[[outcome]])))
for (region_name in c("North", "East", "South", "West")) {
  region_rows <- d[d$region == region_name, ]
  stopifnot(length(unique(region_rows$municipality_id)) == 6)
  stopifnot(length(unique(region_rows$municipality_id[region_rows$early_adopter == 1])) == 3)
}

cluster_fit <- function(data, target_name) {
  formula_text <- paste(
    outcome, "~", target_name,
    "+ factor(municipality_id) + factor(month_index)"
  )
  fit <- lm(as.formula(formula_text), data=data)
  x <- model.matrix(fit)
  residual <- residuals(fit)
  bread <- solve(crossprod(x))
  meat <- matrix(0, ncol(x), ncol(x))
  groups <- unique(data$municipality_id)
  for (group in groups) {
    index <- which(data$municipality_id == group)
    score <- crossprod(x[index, , drop=FALSE], residual[index])
    meat <- meat + score %*% t(score)
  }
  n <- nrow(x)
  p <- ncol(x)
  g <- length(groups)
  correction <- g / (g - 1) * (n - 1) / (n - p)
  covariance <- correction * bread %*% meat %*% bread
  position <- match(target_name, colnames(x))
  estimate <- unname(coef(fit)[position])
  se <- sqrt(covariance[position, position])
  c(estimate, se, estimate - t_cluster_23 * se, estimate + t_cluster_23 * se)
}

its_fit <- function(series, target_position, lag=3) {
  month <- 1:36
  post <- as.numeric(month >= 19)
  x <- cbind(
    intercept=1,
    time=month - 18,
    post=post,
    time_after=pmax(0, month - 18),
    season_sin=sin(2 * pi * (month - 1) / 12),
    season_cos=cos(2 * pi * (month - 1) / 12)
  )
  beta <- solve(crossprod(x), crossprod(x, series))
  residual <- as.vector(series - x %*% beta)
  bread <- solve(crossprod(x))
  scores <- x * residual
  meat <- crossprod(scores)
  for (distance in 1:lag) {
    weight <- 1 - distance / (lag + 1)
    cross <- crossprod(
      scores[(distance + 1):nrow(scores), , drop=FALSE],
      scores[1:(nrow(scores) - distance), , drop=FALSE]
    )
    meat <- meat + weight * (cross + t(cross))
  }
  covariance <- nrow(x) / (nrow(x) - ncol(x)) * bread %*% meat %*% bread
  estimate <- unname(beta[target_position])
  se <- sqrt(covariance[target_position, target_position])
  c(estimate, se, estimate - t_hac_30 * se, estimate + t_hac_30 * se)
}

pre <- d[d$month_index <= 18, ]
pre$placebo_active <- pre$early_adopter * as.integer(pre$month_index >= 13)
pre$early_month_slope <- pre$early_adopter * (pre$month_index - 9.5)

early_series <- aggregate(
  d[[outcome]][d$early_adopter == 1],
  list(month=d$month_index[d$early_adopter == 1]), mean
)$x
comparison_series <- aggregate(
  d[[outcome]][d$early_adopter == 0],
  list(month=d$month_index[d$early_adopter == 0]), mean
)$x

fresh <- list(
  did_twfe_clustered=cluster_fit(d, "policy_active"),
  preperiod_placebo_did=cluster_fit(pre, "placebo_active"),
  preperiod_differential_slope=cluster_fit(pre, "early_month_slope"),
  early_series_its_level_change_hac=its_fit(early_series, 3),
  early_series_its_slope_change_hac=its_fit(early_series, 4),
  comparison_series_its_level_change_hac=its_fit(comparison_series, 3)
)

expected <- list(
  did_twfe_clustered=c(-1.808693, 0.149853, -2.118689, -1.498698),
  preperiod_placebo_did=c(0.153581, 0.199282, -0.258665, 0.565828),
  preperiod_differential_slope=c(0.004573, 0.014379, -0.025171, 0.034318),
  early_series_its_level_change_hac=c(-2.812829, 0.114648, -3.046973, -2.578686),
  early_series_its_slope_change_hac=c(0.006255, 0.007797, -0.009669, 0.022178),
  comparison_series_its_level_change_hac=c(-1.007804, 0.187107, -1.389928, -0.625679)
)

for (name in names(expected)) {
  stopifnot(all(abs(fresh[[name]] - expected[[name]]) <= tolerance))
  cat(sprintf(
    "R_CAUSAL_UNIT6_%s estimate=%.6f se=%.6f ci95=[%.6f,%.6f]\n",
    name, fresh[[name]][1], fresh[[name]][2], fresh[[name]][3], fresh[[name]][4]
  ))
}

group_mean <- function(early, post) {
  mean(d[[outcome]][d$early_adopter == early & as.integer(d$month_index >= 19) == post])
}
means <- c(
  early_pre=group_mean(1, 0),
  early_post=group_mean(1, 1),
  comparison_pre=group_mean(0, 0),
  comparison_post=group_mean(0, 1)
)
early_change <- means["early_post"] - means["early_pre"]
comparison_change <- means["comparison_post"] - means["comparison_pre"]
did_from_means <- early_change - comparison_change
its_level_difference <- fresh$early_series_its_level_change_hac[1] - fresh$comparison_series_its_level_change_hac[1]
stopifnot(abs(did_from_means - expected$did_twfe_clustered[1]) <= tolerance)
stopifnot(abs(its_level_difference - (-1.805026)) <= tolerance)
stopifnot(abs(expected$did_twfe_clustered[1] - its_level_difference - (-0.003667)) <= tolerance)

cat(sprintf(
  "R_CAUSAL_UNIT6_DECOMPOSITION early_change=%.6f comparison_change=%.6f did=%.6f its_level_difference=%.6f\n",
  early_change, comparison_change, did_from_means, its_level_difference
))
cat("R_CAUSAL_UNIT6_INDEPENDENT_OK", R.version.string, "\n")
