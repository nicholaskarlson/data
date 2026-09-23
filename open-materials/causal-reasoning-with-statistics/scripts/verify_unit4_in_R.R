# Independent base-R recomputation for Unit 4 from the raw CSV.
args <- commandArgs(trailingOnly=TRUE)
stopifnot(length(args) == 1)
resource <- normalizePath(args[[1]])
data <- read.csv(file.path(resource, "data", "unit4_cluster_sleep_trial.csv"),
                 na.strings="", stringsAsFactors=FALSE)
data$campus_sector <- factor(data$campus_sector,
                             levels=c("North", "East", "South", "West"))
stopifnot(nrow(data) == 2400,
          length(unique(data$residence_floor_id)) == 48,
          sum(data$assigned_sleep_program) == 1200,
          all(!is.na(data$followup_attention_score)),
          all(is.na(data$followup_sleep_hours) == (data$completed_sleep_diary == 0)))

hc1_row <- function(fit, term, critical=1.96) {
  X <- model.matrix(fit)
  residual <- residuals(fit)
  bread <- solve(crossprod(X))
  covariance <- (nrow(X)/(nrow(X)-ncol(X))) * bread %*%
    crossprod(X, X * as.numeric(residual^2)) %*% bread
  estimate <- unname(coef(fit)[[term]])
  se <- sqrt(covariance[term, term])
  c(estimate, se, estimate-critical*se, estimate+critical*se)
}

floor_data <- aggregate(
  cbind(followup_attention_score, baseline_attention_score) ~
    residence_floor_id + campus_sector + assigned_sleep_program,
  data=data,
  FUN=mean
)
floor_data$attention_change <- floor_data$followup_attention_score -
  floor_data$baseline_attention_score
stopifnot(nrow(floor_data) == 48,
          sum(floor_data$assigned_sleep_program) == 24,
          all(table(floor_data$campus_sector,
                    floor_data$assigned_sleep_program) == 6))

fits <- list(
  individual_hc1_itt = lm(
    followup_attention_score ~ assigned_sleep_program + campus_sector,
    data=data
  ),
  floor_blocked_itt = lm(
    followup_attention_score ~ assigned_sleep_program + campus_sector,
    data=floor_data
  ),
  floor_baseline_adjusted_itt = lm(
    followup_attention_score ~ assigned_sleep_program +
      baseline_attention_score + campus_sector,
    data=floor_data
  ),
  floor_change_score_itt = lm(
    attention_change ~ assigned_sleep_program + campus_sector,
    data=floor_data
  ),
  naive_receipt_association = lm(
    followup_attention_score ~ used_sleep_plan +
      baseline_attention_score + campus_sector,
    data=data
  )
)
anchors <- list(
  individual_hc1_itt=c(3.200971, 0.303030, 2.607032, 3.794910),
  floor_blocked_itt=c(3.200971, 1.050484, 1.082469, 5.319474),
  floor_baseline_adjusted_itt=c(3.313365, 0.293411, 2.721238, 3.905492),
  floor_change_score_itt=c(3.270773, 0.480262, 2.302233, 4.239313),
  naive_receipt_association=c(1.778905, 0.247538, 1.293731, 2.264079)
)
critical <- c(individual_hc1_itt=1.96,
              floor_blocked_itt=qt(0.975, 43),
              floor_baseline_adjusted_itt=qt(0.975, 42),
              floor_change_score_itt=qt(0.975, 43),
              naive_receipt_association=1.96)
for (name in names(fits)) {
  term <- if (name == "naive_receipt_association") {
    "used_sleep_plan"
  } else {
    "assigned_sleep_program"
  }
  fresh <- hc1_row(fits[[name]], term, critical[[name]])
  stopifnot(all(abs(fresh - anchors[[name]]) < 0.000002))
  cat(sprintf(
    "R_CAUSAL_UNIT4_%s estimate=%.6f se_hc1=%.6f ci95=[%.6f,%.6f]\n",
    name, fresh[1], fresh[2], fresh[3], fresh[4]
  ))
}

arm_rate <- function(field, assignment) {
  mean(data[data$assigned_sleep_program == assignment, field])
}
receipt <- c(
  usual_information=arm_rate("used_sleep_plan", 0),
  assigned_program=arm_rate("used_sleep_plan", 1)
)
diary <- c(
  usual_information=arm_rate("completed_sleep_diary", 0),
  assigned_program=arm_rate("completed_sleep_diary", 1)
)
baseline_difference <- with(
  floor_data,
  mean(baseline_attention_score[assigned_sleep_program == 1]) -
    mean(baseline_attention_score[assigned_sleep_program == 0])
)
stopifnot(
  all(abs(receipt - c(0.130833, 0.674167)) < 0.000002),
  all(abs(diary - c(0.735833, 0.799167)) < 0.000002),
  round(unname(diff(diary)), 6) == 0.063333,
  abs(baseline_difference - (-0.069802)) < 0.000002
)
cat(sprintf(
  "R_CAUSAL_UNIT4_IMPLEMENTATION receipt=[%.6f,%.6f] diary=[%.6f,%.6f] diary_difference=%.6f\n",
  receipt[1], receipt[2], diary[1], diary[2], diff(diary)
))
cat("R_CAUSAL_UNIT4_INDEPENDENT_OK", R.version.string, "\n")
