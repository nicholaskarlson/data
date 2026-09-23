# Independent base-R recomputation for Unit 2 from the raw CSV.
args <- commandArgs(trailingOnly=TRUE)
stopifnot(length(args) == 1)
resource <- normalizePath(args[[1]])
data <- read.csv(file.path(resource, "data", "unit2_multisite_workshop_offer.csv"))
data$site <- factor(data$site, levels=c("Cedar", "Lake", "Ridge"))
stopifnot(nrow(data) == 2400, sum(data$workshop_offer) == 1184,
          sum(data$attended_workshop) == 585)

hc1_row <- function(fit, term) {
  X <- model.matrix(fit)
  residual <- residuals(fit)
  bread <- solve(crossprod(X))
  covariance <- (nrow(X)/(nrow(X)-ncol(X))) * bread %*%
    crossprod(X, X * as.numeric(residual^2)) %*% bread
  estimate <- unname(coef(fit)[[term]])
  se <- sqrt(covariance[term, term])
  list(values=c(estimate, se, estimate-1.96*se, estimate+1.96*se), variance=se^2)
}

fits <- list(
  sample_itt = lm(wellbeing_after ~ workshop_offer, data=data),
  site_adjusted_itt = lm(wellbeing_after ~ workshop_offer + site, data=data),
  baseline_site_adjusted_itt = lm(wellbeing_after ~ workshop_offer + baseline_stress + site, data=data),
  naive_attendance_association = lm(wellbeing_after ~ attended_workshop, data=data)
)
terms <- c(sample_itt="workshop_offer", site_adjusted_itt="workshop_offer",
           baseline_site_adjusted_itt="workshop_offer",
           naive_attendance_association="attended_workshop")
anchors <- list(
  sample_itt = c(1.723641, 0.268508, 1.197365, 2.249917),
  site_adjusted_itt = c(1.922637, 0.261464, 1.410168, 2.435106),
  baseline_site_adjusted_itt = c(1.719254, 0.229042, 1.270332, 2.168176),
  naive_attendance_association = c(3.164665, 0.303601, 2.569606, 3.759723)
)
for (name in names(fits)) {
  fresh <- hc1_row(fits[[name]], terms[[name]])$values
  stopifnot(all(abs(fresh - anchors[[name]]) < 0.000002))
  cat(sprintf("R_CAUSAL_UNIT2_%s estimate=%.6f se_hc1=%.6f ci95=[%.6f,%.6f]\n",
              name, fresh[1], fresh[2], fresh[3], fresh[4]))
}

site_anchors <- list(
  Cedar=c(1.390710, 0.357001, 0.690988, 2.090431),
  Lake=c(1.473700, 0.479943, 0.533013, 2.414388),
  Ridge=c(3.935818, 0.620620, 2.719403, 5.152234)
)
sample_weights <- c(Cedar=0.50, Lake=0.30, Ridge=0.20)
target_weights <- c(Cedar=0.25, Lake=0.35, Ridge=0.40)
observed_sample_weights <- table(data$site) / nrow(data)
stopifnot(all(abs(observed_sample_weights - sample_weights) < 0.000002))
site_offer_counts <- tapply(data$workshop_offer, data$site, sum)
stopifnot(all(site_offer_counts == c(Cedar=557, Lake=365, Ridge=262)))
site_offer_rates <- site_offer_counts / table(data$site)
stopifnot(all(abs(site_offer_rates - c(Cedar=0.464167, Lake=0.506944,
                                       Ridge=0.545833)) < 0.000002))
sample_estimate <- 0
sample_variance <- 0
target_estimate <- 0
target_variance <- 0
for (site_name in names(site_anchors)) {
  selected <- data[data$site == site_name,]
  audit <- hc1_row(lm(wellbeing_after ~ workshop_offer, data=selected), "workshop_offer")
  stopifnot(all(abs(audit$values - site_anchors[[site_name]]) < 0.000002))
  sample_estimate <- sample_estimate + sample_weights[[site_name]] * audit$values[1]
  sample_variance <- sample_variance + sample_weights[[site_name]]^2 * audit$variance
  target_estimate <- target_estimate + target_weights[[site_name]] * audit$values[1]
  target_variance <- target_variance + target_weights[[site_name]]^2 * audit$variance
}
sample_se <- sqrt(sample_variance)
sample_standardized <- c(sample_estimate, sample_se, sample_estimate-1.96*sample_se,
                         sample_estimate+1.96*sample_se)
sample_anchor <- c(1.924629, 0.260769, 1.413522, 2.435735)
stopifnot(all(abs(sample_standardized - sample_anchor) < 0.000002))
cat(sprintf("R_CAUSAL_UNIT2_sample_site_standardized_itt estimate=%.6f se_hc1=%.6f ci95=[%.6f,%.6f]\n",
            sample_standardized[1], sample_standardized[2],
            sample_standardized[3], sample_standardized[4]))
target_se <- sqrt(target_variance)
target <- c(target_estimate, target_se, target_estimate-1.96*target_se,
            target_estimate+1.96*target_se)
target_anchor <- c(2.437800, 0.312746, 1.824818, 3.050782)
stopifnot(all(abs(target - target_anchor) < 0.000002))
cat(sprintf("R_CAUSAL_UNIT2_target_standardized_itt estimate=%.6f se_hc1=%.6f ci95=[%.6f,%.6f]\n",
            target[1], target[2], target[3], target[4]))
pooled_estimate <- unname(coef(fits$sample_itt)[["workshop_offer"]])
decomposition <- c(sample_standardized[1] - pooled_estimate,
                   target[1] - sample_standardized[1],
                   target[1] - pooled_estimate)
decomposition_anchor <- c(0.200987, 0.513171, 0.714159)
stopifnot(all(abs(decomposition - decomposition_anchor) < 0.000002))
cat(sprintf("R_CAUSAL_UNIT2_STANDARDIZATION_DECOMPOSITION pooled_to_sample=%.6f sample_to_target=%.6f pooled_to_target=%.6f\n",
            decomposition[1], decomposition[2], decomposition[3]))
cat("R_CAUSAL_UNIT2_INDEPENDENT_OK", R.version.string, "\n")
