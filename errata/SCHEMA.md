# Errata record format

`errata/errata.json` is the source of truth. `ERRATA.md` is generated from it by
`scripts/build_errata.py` and must never be edited by hand.

```
python3 scripts/build_errata.py           # regenerate ERRATA.md
python3 scripts/build_errata.py --check   # validate, and fail if ERRATA.md is stale
```

## Adding an erratum

Append a record to `records` and regenerate. Ids run `ERR-<year>-<3 digits>` in
the order they are confirmed, not the order they are reported.

```json
{
  "id": "ERR-2026-001",
  "reported": "2026-08-31",
  "category": "numeric",
  "status": "published",
  "work": "Psychology Research Methods and Statistics by Design with Jamovi",
  "edition": "Kindle, first edition, 2026",
  "location": "Chapter 19, Table 19.3, Bonferroni p column",
  "issue": "The p column printed the guillemet '‹ .001' instead of '< .001'.",
  "resolution": "Missing glyph in the monospace face. Face replaced; every table reporting a p value re-checked.",
  "verified_source": "expected-results/study_04_practice_spacing_anova.json",
  "fixed_in": "2nd printing, September 2026",
  "credit": "A. Reader",
  "issue_url": "https://github.com/nicholaskarlson/data/issues/12"
}
```

## Fields

| Field | Required | Notes |
| --- | --- | --- |
| `id` | yes | `ERR-YYYY-NNN`. Never reused, never renumbered. |
| `reported` | yes | ISO date the report arrived, not the date it was fixed. |
| `category` | yes | One of the keys in `categories`. |
| `status` | yes | One of `statuses`. |
| `work` | yes | Which book or companion file. |
| `edition` | no | Format, edition, printing. Matters once a correction ships. |
| `location` | yes | Chapter, table, page, or file and line. |
| `issue` | yes | What was wrong, quoted as printed where possible. |
| `resolution` | yes | What was done, and why it happened if that is informative. |
| `verified_source` | **for `numeric`** | The `expected-results` file the printed value contradicted. |
| `fixed_in` | **for `fixed`/`published`** | The printing or release carrying the correction. |
| `credit` | no | Reporter's name. Omit if they asked to stay anonymous. |
| `issue_url` | no | The public issue, so the trail stays open. |

## Enforced rules

The build fails if any of these is violated:

- ids are well-formed and unique;
- dates are ISO;
- category and status are known;
- a `numeric` erratum names the verified record it contradicts — a claim that a
  printed number was wrong is not accepted without saying which recomputation
  settles it;
- anything marked `fixed` or `published` names the printing that carries the fix;
- `ERRATA.md` matches `errata.json`.

Wire `--check` into CI alongside the existing verification so the page can never
drift from the record.
