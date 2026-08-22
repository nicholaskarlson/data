# Quick Start: Recreate a Book Workflow from CSV

The book is deliberately CSV-first. You do not need a prepared jamovi session file.

## 1. Download the Reader Assets

Open `https://github.com/nicholaskarlson/data`. Choose **Code > Download ZIP** for the complete reader package, or download the CSV named by the chapter and its matching JSON dictionary from the `data/` directory. Keeping the original filenames makes the chapter cross-references easier to follow.

The short repository is a verified mirror of the canonical technical source at `https://github.com/nicholaskarlson/nekpress-psychology-methods-statistics-jamovi-companion`.

You can verify a downloaded CSV on a command line with:

```bash
sha256sum study_02_mindfulness_paired.csv
```

Compare the value with `data/SHA256SUMS`. Windows users without `sha256sum` can use PowerShell’s `Get-FileHash -Algorithm SHA256`.

## 2. Start jamovi Desktop

- **Windows:** open jamovi Desktop from the Start menu.
- **macOS:** open jamovi Desktop from Applications. If macOS presents a first-launch security prompt, follow Apple’s normal application-opening procedure.
- **Ubuntu:** open jamovi Desktop from the applications menu. A verified Flatpak installation can also be started with `flatpak run org.jamovi.jamovi`.

Ubuntu representative validation was completed on 22 August 2026 with application release 28.2. It covered fresh CSV import, descriptives, paired inference, regression, factorial and mixed repeated-measures ANOVA, a two-line group-by-week plot, export, save, complete application close, file-browser reopen, output persistence, and final source-checksum checks. The Windows and macOS wording below follows the same jamovi Desktop interface but should be treated as release-candidate guidance until representative platform validation is recorded.

## 3. Import a CSV

1. Open jamovi Desktop to a blank workspace.
2. Open the application menu, choose **Open**, and select the option that browses files on your computer. The label may appear as **This PC**, **Computer**, or **Browse** depending on platform and build.
3. Select the downloaded `.csv` file.
4. Confirm that the dataset name and row count match the dictionary and `ANALYSIS_MATRIX.md`.

If a CSV opens in a spreadsheet application instead, return to jamovi Desktop and use its **Open** command rather than double-clicking the file.

## 4. Audit the Variables Before Analysis

1. Compare every imported column name with the dictionary.
2. Confirm the declared measurement level: identifier, nominal, ordinal, or continuous.
3. Correct an imported level only when the dictionary supports the change.
4. Check the missing-value rule and any expected missing count.
5. Confirm group labels and their order before fitting a model.

Do not proceed merely because jamovi Desktop produced output. A reproducible analysis begins with the right variables, types, and ordering.

## 5. Follow the Chapter Workflow

Use the chapter’s numbered **Try It in jamovi** steps. At each **Workflow Checkpoint**:

1. **Do it:** complete the immediately preceding steps from the fresh CSV import.
2. **Check it:** compare roles and options with the dictionary.
3. **Read it:** identify the expected pattern or statistic described in the checkpoint.
4. **Record it:** note the CSV filename, any missing-value or group-order decision, and the result field that answers the research question.

Use the book’s native verified table and the corresponding `expected-results/*_verified_results.json` file as audit targets. Small display-rounding differences are acceptable when the underlying value agrees.

## 6. Save Your Work, If Desired

Saving a local jamovi file can be convenient for your own work, but it is not the public source of truth. A reader should be able to reproduce the workflow from the CSV, dictionary, chapter steps, and verified result record.

## Troubleshooting

- **Wrong measurement level:** compare the variable with the JSON dictionary and change the level in jamovi Desktop.
- **Different group order or sign:** check the factor order and the stated subtraction/reference direction.
- **Different row count:** download the CSV again and verify its SHA-256 hash.
- **Different menu label:** use the equivalent local-file browsing command and report the platform/build wording through an issue.
- **Different statistic:** confirm analysis options, missing-data handling, correction method, and rounding before reporting a mismatch.
