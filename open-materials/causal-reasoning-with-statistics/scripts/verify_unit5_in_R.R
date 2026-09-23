# Independent base-R recomputation for Unit 5 from the raw CSV.
args <- commandArgs(trailingOnly=TRUE)
stopifnot(length(args) == 1)
resource <- normalizePath(args[[1]])
data <- read.csv(file.path(resource, "data", "unit5_hypertension_coaching.csv"),
                 stringsAsFactors=FALSE)
data$clinic <- factor(data$clinic, levels=c("Harbor", "Mesa", "River"))
data$baseline10 <- (data$baseline_sbp - 137) / 10
data$age10 <- (data$age_years - 54) / 10
stopifnot(
  nrow(data) == 3200,
  length(unique(data$participant_id)) == 3200,
  sum(data$joined_coaching) == 1308,
  all(complete.cases(data))
)

hc1 <- function(X, y) {
  fit <- lm.fit(X, y)
  residual <- fit$residuals
  bread <- solve(crossprod(X))
  covariance <- (nrow(X)/(nrow(X)-ncol(X))) * bread %*%
    crossprod(X, X * as.numeric(residual^2)) %*% bread
  list(beta=as.numeric(fit$coefficients), covariance=covariance)
}

record <- function(estimate, se) {
  c(estimate, se, estimate - 1.96*se, estimate + 1.96*se)
}

covariate_matrix <- function(d) {
  cbind(
    baseline_sbp_per_10=d$baseline10,
    age_per_10=d$age10,
    current_smoker=d$current_smoker,
    taking_bp_medication=d$taking_bp_medication,
    transport_barrier=d$transport_barrier,
    clinic_mesa=as.numeric(d$clinic == "Mesa"),
    clinic_river=as.numeric(d$clinic == "River")
  )
}

outcome_matrix <- function(d, assignment=NULL, interaction=TRUE) {
  a <- if (is.null(assignment)) d$joined_coaching else rep(assignment, nrow(d))
  X <- cbind(intercept=1, joined_coaching=a, covariate_matrix(d))
  if (interaction) {
    X <- cbind(X, joined_by_baseline_sbp_per_10=a*d$baseline10)
  }
  X
}

naive_X <- cbind(intercept=1, joined_coaching=data$joined_coaching)
naive_fit <- hc1(naive_X, data$followup_sbp)
naive <- record(naive_fit$beta[2], sqrt(naive_fit$covariance[2,2]))

outcome_X <- outcome_matrix(data)
outcome_fit <- hc1(outcome_X, data$followup_sbp)
gradient <- colMeans(outcome_matrix(data, 1) - outcome_matrix(data, 0))
outcome_estimate <- sum(gradient*outcome_fit$beta)
outcome_se <- sqrt(as.numeric(t(gradient) %*% outcome_fit$covariance %*% gradient))
standardized <- record(outcome_estimate, outcome_se)

propensity_X <- cbind(intercept=1, covariate_matrix(data))
propensity_fit <- glm.fit(propensity_X, data$joined_coaching, family=binomial())
probability <- as.numeric(propensity_fit$fitted.values)
a <- data$joined_coaching
y <- data$followup_sbp
w1 <- a/probability
w0 <- (1-a)/(1-probability)
mu1 <- sum(w1*y)/sum(w1)
mu0 <- sum(w0*y)/sum(w0)

p <- ncol(propensity_X)
n <- nrow(data)
U <- cbind(
  propensity_X * as.numeric(a-probability),
  w1*(y-mu1),
  w0*(y-mu0)
)
A <- matrix(0, p+2, p+2)
A[1:p,1:p] <- crossprod(propensity_X,
                         propensity_X*as.numeric(probability*(1-probability))) / n
A[p+1,1:p] <- colMeans(propensity_X *
  as.numeric(w1*(1-probability)*(y-mu1)))
A[p+1,p+1] <- mean(w1)
A[p+2,1:p] <- -colMeans(propensity_X *
  as.numeric(w0*probability*(y-mu0)))
A[p+2,p+2] <- mean(w0)
B <- crossprod(U)/n
A_inverse <- solve(A)
covariance <- A_inverse %*% B %*% t(A_inverse) / n
contrast <- c(rep(0,p), 1, -1)
ipw_se <- sqrt(as.numeric(t(contrast) %*% covariance %*% contrast))
ipw <- record(mu1-mu0, ipw_se)

negative_X <- outcome_matrix(data, interaction=FALSE)
negative_fit <- hc1(negative_X, data$prior_year_preventive_visits)
negative <- record(negative_fit$beta[2], sqrt(negative_fit$covariance[2,2]))

# Hidden generator truth is a teaching audit, not information available to an analyst.
known_effect <- -4.2 - 0.85 * ((data$baseline_sbp - 137) / 10)
known_sample_ate <- mean(known_effect)
known_participant_att <- mean(known_effect[data$joined_coaching == 1])
reported_bias <- c(
  naive_difference=round(naive[1], 6) - round(known_sample_ate, 6),
  outcome_regression_standardized_ate=round(standardized[1], 6) - round(known_sample_ate, 6),
  ipw_hajek_ate=round(ipw[1], 6) - round(known_sample_ate, 6)
)
stopifnot(
  abs(known_sample_ate - (-4.226561)) < 0.000002,
  abs(known_participant_att - (-4.328183)) < 0.000002,
  max(abs(reported_bias - c(-1.095472, -1.915216, -1.921987))) < 0.0000005
)
cat(sprintf(
  "R_CAUSAL_UNIT5_KNOWN_SIMULATION sample_ate=%.6f participant_att=%.6f reported_biases=[%.6f,%.6f,%.6f]\n",
  known_sample_ate, known_participant_att, reported_bias[1], reported_bias[2], reported_bias[3]
))

anchors <- list(
  naive_difference=c(-5.322033, 0.351981, -6.011916, -4.632151),
  outcome_regression_standardized_ate=c(-6.141777, 0.268260, -6.667566, -5.615987),
  ipw_hajek_ate=c(-6.148548, 0.287971, -6.712971, -5.584126),
  negative_control_adjusted_association=c(0.309462, 0.032520, 0.245723, 0.373201)
)
fresh <- list(
  naive_difference=naive,
  outcome_regression_standardized_ate=standardized,
  ipw_hajek_ate=ipw,
  negative_control_adjusted_association=negative
)
for (name in names(fresh)) {
  stopifnot(all(abs(fresh[[name]] - anchors[[name]]) < 0.000002))
  cat(sprintf(
    "R_CAUSAL_UNIT5_%s estimate=%.6f se=%.6f ci95=[%.6f,%.6f]\n",
    name, fresh[[name]][1], fresh[[name]][2], fresh[[name]][3], fresh[[name]][4]
  ))
}

standardized_means <- c(
  outcome_regression_if_not_joined=mean(outcome_matrix(data, 0) %*% outcome_fit$beta),
  outcome_regression_if_joined=mean(outcome_matrix(data, 1) %*% outcome_fit$beta),
  ipw_nonparticipants=mu0,
  ipw_participants=mu1
)
stopifnot(all(abs(standardized_means - c(
  137.272161, 131.130385, 137.264128, 131.115580
)) < 0.000002))

smd <- function(values, treatment, weight1=NULL, weight0=NULL) {
  treated <- treatment == 1
  control <- treatment == 0
  denominator <- sqrt((var(values[treated]) + var(values[control]))/2)
  if (is.null(weight1)) {
    difference <- mean(values[treated]) - mean(values[control])
  } else {
    difference <- weighted.mean(values[treated], weight1[treated]) -
      weighted.mean(values[control], weight0[control])
  }
  difference/denominator
}
covariates <- covariate_matrix(data)
before <- apply(covariates, 2, smd, treatment=a)
after <- apply(covariates, 2, smd, treatment=a, weight1=w1, weight0=w0)
ess <- function(weight) sum(weight)^2/sum(weight^2)
observed_weight <- ifelse(a == 1, w1, w0)
diagnostics <- c(
  propensity_min=min(probability),
  propensity_p01=unname(quantile(probability, 0.01, type=7)),
  propensity_median=median(probability),
  propensity_p99=unname(quantile(probability, 0.99, type=7)),
  propensity_max=max(probability),
  max_weight=max(observed_weight),
  ess_participants=ess(w1[a == 1]),
  ess_nonparticipants=ess(w0[a == 0]),
  max_abs_smd_before=max(abs(before)),
  max_abs_smd_after=max(abs(after))
)
diagnostic_anchors <- c(
  0.062238, 0.102021, 0.424879, 0.725843, 0.814996,
  16.067306, 1001.798038, 1741.614919, 0.557405, 0.018478
)
stopifnot(
  all(abs(diagnostics - diagnostic_anchors) < 0.000002),
  sum(probability < 0.05) == 0,
  sum(probability > 0.95) == 0,
  max(abs(before - c(0.211795, 0.291271, 0.164168, 0.221147,
                     -0.557405, -0.213036, -0.004448))) < 0.000002,
  max(abs(after - c(-0.006196, -0.018478, -0.004903, -0.017264,
                    0.008948, 0.010371, -0.001134))) < 0.000002
)
cat(sprintf(
  "R_CAUSAL_UNIT5_DIAGNOSTICS propensity=[%.6f,%.6f] max_weight=%.6f ess=[%.6f,%.6f] max_abs_smd=[%.6f,%.6f]\n",
  min(probability), max(probability), max(observed_weight),
  ess(w1[a == 1]), ess(w0[a == 0]), max(abs(before)), max(abs(after))
))
cat("R_CAUSAL_UNIT5_INDEPENDENT_OK", R.version.string, "\n")
