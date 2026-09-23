# Independent base-R recomputation for Unit 1 from the raw CSV.
args <- commandArgs(trailingOnly=TRUE)
stopifnot(length(args) == 1)
resource <- normalizePath(args[[1]])
data <- read.csv(file.path(resource, "data", "unit1_library_interface_ab.csv"))
stopifnot(nrow(data) == 1800, sum(data$redesigned_interface) == 921)

hc1_row <- function(fit, term) {
  X <- model.matrix(fit)
  residual <- residuals(fit)
  bread <- solve(crossprod(X))
  covariance <- (nrow(X)/(nrow(X)-ncol(X))) * bread %*%
    crossprod(X, X * as.numeric(residual^2)) %*% bread
  estimate <- unname(coef(fit)[[term]])
  se <- sqrt(covariance[term, term])
  c(estimate, se, estimate-1.96*se, estimate+1.96*se)
}

fits <- list(
  unadjusted_itt = list(lm(task_score ~ redesigned_interface, data=data), "redesigned_interface"),
  baseline_adjusted_itt = list(lm(task_score ~ redesigned_interface + baseline_search_skill + difficult_task, data=data), "redesigned_interface"),
  click_score_association = list(lm(task_score ~ clicks_during_task, data=data), "clicks_during_task")
)
anchors <- list(
  unadjusted_itt = c(3.932705, 0.345501, 3.255522, 4.609888),
  baseline_adjusted_itt = c(3.687350, 0.279556, 3.139420, 4.235280),
  click_score_association = c(-1.362345, 0.063840, -1.487473, -1.237218)
)
for (name in names(fits)) {
  fresh <- hc1_row(fits[[name]][[1]], fits[[name]][[2]])
  stopifnot(all(abs(fresh - anchors[[name]]) < 0.000002))
  cat(sprintf("R_CAUSAL_UNIT1_%s estimate=%.6f se_hc1=%.6f ci95=[%.6f,%.6f]\n",
              name, fresh[1], fresh[2], fresh[3], fresh[4]))
}
stopifnot(abs(mean(data$baseline_search_skill[data$redesigned_interface == 1]) -
              mean(data$baseline_search_skill[data$redesigned_interface == 0]) - 0.406792) < 0.000002)
stopifnot(abs(cor(data$clicks_during_task, data$task_score) - (-0.452156)) < 0.000002)
cat("R_CAUSAL_UNIT1_INDEPENDENT_OK", R.version.string, "\n")
