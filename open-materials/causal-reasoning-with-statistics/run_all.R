#!/usr/bin/env Rscript

# Third computation path: recompute the book's results in base R.
#
# Every script below reads the published CSV files and checks its own results
# against anchors printed in the book, with a tolerance of 2e-06. No contributed
# packages are used, so a plain R installation is enough.
#
# Usage:  Rscript run_all.R           (run from this directory, or pass the path)

args <- commandArgs(trailingOnly = TRUE)
resource <- normalizePath(if (length(args) >= 1) args[[1]] else ".")
scripts <- c(
  "verify_in_R.R",
  "verify_unit1_in_R.R",
  "verify_unit2_in_R.R",
  "verify_unit4_in_R.R",
  "verify_unit5_in_R.R",
  "verify_unit6_in_R.R",
  "verify_unit7_in_R.R",
  "verify_unit8_in_R.R",
  "verify_unit9_in_R.R",
  "verify_unit10_in_R.R",
  "verify_addendum_in_R.R"
)

failures <- character(0)
for (script in scripts) {
  path <- file.path(resource, "scripts", script)
  if (!file.exists(path)) {
    failures <- c(failures, paste(script, "missing"))
    next
  }
  status <- system2("Rscript", c(shQuote(path), shQuote(resource)))
  if (status != 0L) {
    failures <- c(failures, paste(script, "exited", status))
  }
}

if (length(failures) > 0) {
  cat("CAUSAL_REASONING_COMPANION_R_FAILED\n")
  for (line in failures) cat("  ", line, "\n", sep = "")
  quit(status = 1)
}
cat("CAUSAL_REASONING_COMPANION_R_OK paths=", length(scripts), " ",
    R.version.string, "\n", sep = "")
