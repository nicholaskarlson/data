# Volume 2 publication source

This directory is the public, editable source for *Psychology Statistics Practice Materials with Jamovi, Volume 2: Categorical, Rank-Based, Quasi-Experimental, and Single-Case Evidence*, Version 1.0, DOI `10.5281/zenodo.22286929`.

The source preserves Units 12 through 15 and all five row-filter teaching variants. `00_front.md` and `99_back.md` contain the publication front and back matter. The four numbered Markdown files contain the unit prose, 96 problems, and 96 worked solutions. `meta_docx.yaml` and `meta.yaml` record the publication metadata.

## Rebuild

Run from a checkout that also contains the adjacent Volume 1 DOCX:

```bash
python3 -m pip install python-docx pypdf
sudo apt-get install pandoc libreoffice poppler-utils
./open-materials/psychology-statistics-practice-with-jamovi-volume-2/source/build.sh
```

The builder uses Volume 1's DOCX as its Pandoc style reference, creates one cover page, adds running headers and page-number fields after the cover, marks each table's first row as a repeating header, exports a tagged PDF through LibreOffice, and verifies metadata, structure, live links, font embedding, and core content before atomically replacing the public DOCX and PDF.

The release gate remains `make verify`. The numerical source of truth is `scripts/verify_volume2_numbers.py`; Study 09 distinguishes jamovi epsilon-squared, *H* / (*N* - 1), from the separately named bias-adjusted rank effect size, (*H* - *k* + 1) / (*N* - *k*).
