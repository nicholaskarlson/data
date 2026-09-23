# Independent base-R recomputation from raw CSV. The author-side audit passed
# with R 4.1.2 on 2026-09-13; GitHub Actions reruns this script on every change.
args <- commandArgs(trailingOnly=TRUE)
stopifnot(length(args) == 1)
resource <- normalizePath(args[[1]])
data <- read.csv(file.path(resource, "data", "psychology_memory_training.csv"))
stopifnot(nrow(data) == 2400, sum(data$training) > 0)
specs <- list(
  naive = memory_after ~ training,
  baseline_adjusted = memory_after ~ training + baseline_memory,
  collider_adjusted = memory_after ~ training + baseline_memory + help_seeking_after,
  mediator_adjusted = memory_after ~ training + baseline_memory + engagement_after
)
anchors <- list(
  naive = c(8.351586, 0.304550, 7.754669, 8.948504),
  baseline_adjusted = c(1.999533, 0.195065, 1.617206, 2.381859),
  collider_adjusted = c(4.690883, 0.167913, 4.361775, 5.019992),
  mediator_adjusted = c(0.900677, 0.244689, 0.421086, 1.380268)
)
for (name in names(specs)) {
  fit <- lm(specs[[name]], data=data)
  X <- model.matrix(fit)
  resid <- residuals(fit)
  bread <- solve(crossprod(X))
  hc1 <- (nrow(X)/(nrow(X)-ncol(X))) * bread %*%
    crossprod(X, X * as.numeric(resid^2)) %*% bread
  b <- unname(coef(fit)[["training"]])
  se <- sqrt(hc1["training", "training"])
  fresh <- c(b, se, b-1.96*se, b+1.96*se)
  stopifnot(all(abs(fresh - anchors[[name]]) < 0.000002))
  cat(sprintf("R_CAUSAL_%s estimate=%.6f se_hc1=%.6f ci95=[%.6f,%.6f]\n",
              name, b, se, b-1.96*se, b+1.96*se))
}
cat("R_CAUSAL_INDEPENDENT_OK", R.version.string, "\n")
