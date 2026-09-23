#!/usr/bin/env Rscript

# Independent base-R verification for Unit 10.
args <- commandArgs(trailingOnly = TRUE)
resource <- if (length(args) >= 1) args[[1]] else normalizePath(file.path(dirname(sys.frame(1)$ofile), ".."))
unit5_path <- file.path(resource, "expected-results", "unit5_hypertension_coaching_verified_results.json")
unit10_path <- file.path(resource, "expected-results", "unit10_cross_case_synthesis_verified_results.json")
text <- paste(readLines(unit5_path, warn = FALSE), collapse = "\n")
unit10_text <- paste(readLines(unit10_path, warn = FALSE), collapse = "\n")
number <- function(pattern) {
  hit <- regmatches(text, regexpr(pattern, text, perl = TRUE))
  if (length(hit) == 0 || hit == "") stop(paste("missing Unit 5 field", pattern))
  as.numeric(sub(".*:\\s*", "", hit))
}
section <- function(name) {
  start <- regexpr(paste0('"', name, '"\\s*:\\s*\\{'), text, perl = TRUE)
  if (start < 0) stop(paste("missing section", name))
  rest <- substring(text, start)
  depth <- 0
  chars <- strsplit(rest, "")[[1]]
  begun <- FALSE
  for (i in seq_along(chars)) {
    if (chars[i] == "{") { depth <- depth + 1; begun <- TRUE }
    if (chars[i] == "}") depth <- depth - 1
    if (begun && depth == 0) return(substr(rest, 1, i))
  }
  stop("unterminated section")
}
extract <- function(block, key) {
  hit <- regmatches(block, regexpr(paste0('"', key, '"\\s*:\\s*-?[0-9.]+'), block, perl = TRUE))
  as.numeric(sub(".*:\\s*", "", hit))
}
tolerance <- 0.000002

# The byte hash identifies the exact Unit 5 record read. The canonical hash
# removes only the machine-specific primary_environment object, retaining all
# substantive values. Records are emitted as sorted, two-space-indented JSON,
# so deleting that top-level block reproduces the Python canonical payload.
unit5_lines <- readLines(unit5_path, warn = FALSE)
environment_start <- grep('^  "primary_environment": \\{$', unit5_lines)
stopifnot(length(environment_start) == 1)
depth <- 0L
environment_end <- NA_integer_
for (index in environment_start:length(unit5_lines)) {
  chars <- strsplit(unit5_lines[[index]], "", fixed = TRUE)[[1]]
  depth <- depth + sum(chars == "{") - sum(chars == "}")
  if (depth == 0L) {
    environment_end <- index
    break
  }
}
stopifnot(!is.na(environment_end))
canonical_lines <- unit5_lines[-seq(environment_start, environment_end)]
canonical_file <- tempfile(fileext = ".json")
writeBin(charToRaw(paste(canonical_lines, collapse = "\n")), canonical_file)
canonical_output <- system2("sha256sum", canonical_file, stdout = TRUE, stderr = TRUE)
unlink(canonical_file)
canonical_status <- attr(canonical_output, "status")
stopifnot(is.null(canonical_status) || canonical_status == 0L)
canonical_sha256 <- strsplit(canonical_output[[1]], "[[:space:]]+")[[1]][[1]]
expected_canonical <- regmatches(
  unit10_text,
  regexpr('(?<="source_unit5_result_canonical_sha256": ")[0-9a-f]{64}',
          unit10_text, perl = TRUE)
)
stopifnot(length(expected_canonical) == 1, canonical_sha256 == expected_canonical)

preferred <- section("outcome_regression_standardized_ate")
estimate <- extract(preferred, "estimate")
lower <- extract(preferred, "ci95_lower")
upper <- extract(preferred, "ci95_upper")
truth <- number('"known_simulation_sample_ate"\\s*:\\s*-?[0-9.]+')

delta <- 0.5
gammas <- c(0, -2, -3, -6)
adjusted <- estimate - delta * gammas
stopifnot(abs(adjusted[gammas == -3] - (-4.641777)) < tolerance)
stopifnot(abs((lower - delta * (-3)) - (-5.167566)) < tolerance)
stopifnot(abs((upper - delta * (-3)) - (-4.115987)) < tolerance)
gamma_truth <- (estimate - truth) / delta
gamma_null <- estimate / delta
stopifnot(abs(gamma_truth - (-3.830432)) < tolerance)
stopifnot(abs(gamma_null - (-12.283554)) < tolerance)

z975 <- 1.959963985
z80 <- 0.841621234
sd <- 7.1
m <- 50
J <- 48
rhos <- c(0, .05, .10, .20)
de <- 1 + (m - 1) * rhos
neff <- J * m / de
mde <- 2 * (z975 + z80) * sd / sqrt(neff)
required <- ceiling((2 * (z975 + z80) * sd / 1.5)^2 * de / m)
required <- required + (required %% 2)
stopifnot(max(abs(mde - c(.812057, 1.508329, 1.972480, 2.668692))) < tolerance)
stopifnot(all(required == c(16, 50, 84, 152)))

cat(sprintf("R_CAUSAL_UNIT10_SENSITIVITY_OK adjusted_gamma_minus3=%.6f gamma_to_truth=%.6f\n", adjusted[gammas == -3], gamma_truth))
cat(sprintf("R_CAUSAL_UNIT10_PRECISION_OK mde_icc_010=%.6f required_clusters_icc_020=%d\n", mde[rhos == .10], required[rhos == .20]))
