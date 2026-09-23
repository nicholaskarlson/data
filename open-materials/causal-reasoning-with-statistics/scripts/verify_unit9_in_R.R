#!/usr/bin/env Rscript

# Independent base-R verification for Unit 9.
args <- commandArgs(trailingOnly = TRUE)
resource <- if (length(args) >= 1) args[[1]] else normalizePath(file.path(dirname(sys.frame(1)$ofile), ".."))
data <- read.csv(file.path(resource, "data", "unit9_multisite_replication.csv"), stringsAsFactors = FALSE, na.strings = "")
tolerance <- 0.000002
z975 <- 1.959963985

target <- c("Cedar|0"=.12, "Cedar|1"=.10, "Lake|0"=.15, "Lake|1"=.13,
            "Ridge|0"=.10, "Ridge|1"=.15, "Harbor|0"=.08, "Harbor|1"=.17)
truth0 <- c("Cedar|0"=.42, "Cedar|1"=.28, "Lake|0"=.39, "Lake|1"=.25,
            "Ridge|0"=.36, "Ridge|1"=.23, "Harbor|0"=.34, "Harbor|1"=.20)
truthrd <- c("Cedar|0"=.10, "Cedar|1"=.16, "Lake|0"=.12, "Lake|1"=.18,
             "Ridge|0"=.14, "Ridge|1"=.20, "Harbor|0"=.16, "Harbor|1"=.22)

check <- function(actual, expected, label) {
  if (any(abs(actual - expected) > tolerance)) {
    stop(sprintf("R_CAUSAL_UNIT9_ERROR %s: %s != %s", label,
                 paste(actual, collapse=","), paste(expected, collapse=",")))
  }
}

effect_record <- function(r0, r1, v0, v1) {
  rd <- r1 - r0
  se <- sqrt(v0 + v1)
  rr <- r1 / r0
  se_log <- sqrt(v1 / r1^2 + v0 / r0^2)
  c(r0, r1, rd, se, rd-z975*se, rd+z975*se, rr,
    exp(log(rr)-z975*se_log), exp(log(rr)+z975*se_log))
}

standardized <- function(weights, field, observed_only) {
  r <- matrix(NA_real_, nrow=2, ncol=length(weights), dimnames=list(c("0","1"), names(weights)))
  v <- r
  for (key in names(weights)) {
    pieces <- strsplit(key, "\\|")[[1]]
    for (arm in 0:1) {
      keep <- data$site == pieces[1] & data$baseline_high_distress == as.integer(pieces[2]) & data$program_assignment == arm
      if (observed_only) keep <- keep & data$blinded_outcome_observed == 1
      values <- data[[field]][keep]
      values <- values[!is.na(values)]
      r[as.character(arm), key] <- mean(values)
      v[as.character(arm), key] <- mean(values) * (1-mean(values)) / length(values)
    }
  }
  mr <- c(sum(weights*r["0",]), sum(weights*r["1",]))
  mv <- c(sum(weights^2*v["0",]), sum(weights^2*v["1",]))
  effect_record(mr[1], mr[2], mv[1], mv[2])
}

stopifnot(nrow(data) == 4000)
stopifnot(identical(names(data), c("participant_id", "site", "baseline_high_distress",
  "program_assignment", "blinded_outcome_observed", "blinded_improvement", "self_report_improvement")))
stopifnot(all(data$site %in% c("Cedar", "Lake", "Ridge", "Harbor")))
stopifnot(all(data$baseline_high_distress %in% c(0,1)))
stopifnot(all(data$program_assignment %in% c(0,1)))
stopifnot(all(data$blinded_outcome_observed %in% c(0,1)))
stopifnot(all(data$self_report_improvement %in% c(0,1)))
stopifnot(all(is.na(data$blinded_improvement) == (data$blinded_outcome_observed == 0)))

cell <- paste(data$site, data$baseline_high_distress, sep="|")
counts <- table(cell)
sample_weights <- counts / nrow(data)
allocation <- table(cell, data$program_assignment)
stopifnot(all(allocation[,1] == allocation[,2]))
stopifnot(all(names(target) %in% names(sample_weights)))
check(sum(target), 1, "target sum")
check(max(target/sample_weights[names(target)]), 2.266667, "maximum target/sample ratio")

observed <- data[data$blinded_outcome_observed == 1,]
r0 <- mean(observed$blinded_improvement[observed$program_assignment == 0])
r1 <- mean(observed$blinded_improvement[observed$program_assignment == 1])
v0 <- r0*(1-r0)/sum(observed$program_assignment == 0)
v1 <- r1*(1-r1)/sum(observed$program_assignment == 1)
crude <- effect_record(r0,r1,v0,v1)
sample_primary <- standardized(sample_weights[names(target)], "blinded_improvement", TRUE)
target_primary <- standardized(target, "blinded_improvement", TRUE)
sample_self <- standardized(sample_weights[names(target)], "self_report_improvement", FALSE)

check(crude, c(0.324170,0.459091,0.134921,0.016327,0.102921,0.166922,1.416206,1.301313,1.541244), "crude")
check(sample_primary, c(0.319716,0.457473,0.137757,0.016161,0.106082,0.169433,1.430875,1.315226,1.556694), "sample primary")
check(target_primary, c(0.283330,0.449125,0.165795,0.018008,0.130500,0.201089,1.585164,1.433461,1.752921), "target primary")
check(sample_self, c(0.345000,0.492500,0.147500,0.015366,0.117382,0.177618,1.427536,1.324827,1.538208), "sample self report")

obs0 <- mean(data$blinded_outcome_observed[data$program_assignment == 0])
obs1 <- mean(data$blinded_outcome_observed[data$program_assignment == 1])
check(c(obs0,obs1,obs1-obs0), c(.873,.880,.007), "observation rates")

bounds <- matrix(NA_real_, nrow=2, ncol=2)
for (arm in 0:1) {
  rows <- data[data$program_assignment == arm,]
  successes <- sum(rows$blinded_improvement, na.rm=TRUE)
  missing <- sum(is.na(rows$blinded_improvement))
  bounds[arm+1,] <- c(successes/nrow(rows), (successes+missing)/nrow(rows))
}
check(c(bounds[2,1]-bounds[1,2], bounds[2,2]-bounds[1,1]), c(-.006,.241), "bounds")

sample_truth0 <- sum(sample_weights[names(target)]*truth0)
sample_truth1 <- sum(sample_weights[names(target)]*(truth0+truthrd))
target_truth0 <- sum(target*truth0)
target_truth1 <- sum(target*(truth0+truthrd))
check(c(sample_truth0,sample_truth1,sample_truth1-sample_truth0,sample_truth1/sample_truth0),
      c(.336,.481,.145,1.431548), "sample truth")
check(c(target_truth0,target_truth1,target_truth1-target_truth0,target_truth1/target_truth0),
      c(.3011,.4647,.1636,1.543341), "target truth")

cat(sprintf("R_CAUSAL_UNIT9_PRIMARY sample_rd=%.6f target_rd=%.6f sample_rr=%.6f target_rr=%.6f\n",
            sample_primary[3], target_primary[3], sample_primary[7], target_primary[7]))
cat(sprintf("R_CAUSAL_UNIT9_MISSINGNESS observed=%d rate0=%.6f rate1=%.6f bounds=[%.6f,%.6f]\n",
            nrow(observed), obs0, obs1, bounds[2,1]-bounds[1,2], bounds[2,2]-bounds[1,1]))
cat(sprintf("R_CAUSAL_UNIT9_MEASUREMENT self_report_rd=%.6f blinded_rd=%.6f\n",
            sample_self[3], sample_primary[3]))
cat("R_CAUSAL_UNIT9_INDEPENDENT_OK", R.version.string, "\n")
