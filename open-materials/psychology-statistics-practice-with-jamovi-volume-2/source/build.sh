#!/usr/bin/env bash
# Build publication-grade Volume 2 DOCX and tagged PDF atomically.
set -euo pipefail

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESOURCE_DIR="$(cd "$SOURCE_DIR/.." && pwd)"
VOLUME_1_DIR="$(cd "$RESOURCE_DIR/../psychology-statistics-practice-with-jamovi" && pwd)"
REFERENCE_DOC="$VOLUME_1_DIR/psychology-statistics-practice-materials-with-jamovi-open-resource-v1.1.docx"
DOCX_NAME="psychology-statistics-practice-materials-with-jamovi-volume-2-open-resource-v1.0.docx"
PDF_NAME="psychology-statistics-practice-materials-with-jamovi-volume-2-open-resource-v1.0.pdf"
OUTPUT_DIR="${OUTPUT_DIR:-$RESOURCE_DIR}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

for command_name in pandoc soffice pdfinfo pdftotext pdffonts; do
    if ! command -v "$command_name" >/dev/null 2>&1; then
        echo "BUILD_ERROR: required command not found: $command_name" >&2
        exit 1
    fi
done

if ! "$PYTHON_BIN" -c 'import docx, pypdf' >/dev/null 2>&1; then
    echo "BUILD_ERROR: Python packages python-docx and pypdf are required" >&2
    exit 1
fi

if [[ ! -f "$REFERENCE_DOC" ]]; then
    echo "BUILD_ERROR: Volume 1 reference DOCX is missing: $REFERENCE_DOC" >&2
    exit 1
fi

mkdir -p "$OUTPUT_DIR"
BUILD_DIR="$(mktemp -d "${TMPDIR:-/tmp}/nekpress-volume2-build.XXXXXX")"
LO_PROFILE="$BUILD_DIR/libreoffice-profile"
trap 'rm -rf -- "$BUILD_DIR"' EXIT
mkdir -p "$LO_PROFILE"

"$PYTHON_BIN" "$SOURCE_DIR/prepare_markdown.py" \
    --source-dir "$SOURCE_DIR" \
    --output "$BUILD_DIR/volume2.docx.md"

pandoc \
    "$SOURCE_DIR/meta_docx.yaml" \
    "$BUILD_DIR/volume2.docx.md" \
    --from=markdown+raw_attribute \
    --standalone \
    --reference-doc="$REFERENCE_DOC" \
    --output="$BUILD_DIR/$DOCX_NAME"

"$PYTHON_BIN" "$SOURCE_DIR/postprocess_docx.py" "$BUILD_DIR/$DOCX_NAME"

# SOURCE_DATE_EPOCH removes current-clock drift from LibreOffice metadata.
SOURCE_DATE_EPOCH=1788393600 \
HOME="$LO_PROFILE" \
soffice --headless \
    -env:UserInstallation="file://$LO_PROFILE" \
    --convert-to 'pdf:writer_pdf_Export:{"UseTaggedPDF":{"type":"boolean","value":"true"},"ExportBookmarks":{"type":"boolean","value":"true"}}' \
    --outdir "$BUILD_DIR" \
    "$BUILD_DIR/$DOCX_NAME" >/dev/null

if [[ ! -s "$BUILD_DIR/$PDF_NAME" ]]; then
    echo "BUILD_ERROR: LibreOffice did not create the expected PDF" >&2
    exit 1
fi

"$PYTHON_BIN" "$SOURCE_DIR/validate_publication.py" \
    "$BUILD_DIR/$DOCX_NAME" \
    "$BUILD_DIR/$PDF_NAME"

if ! pdfinfo "$BUILD_DIR/$PDF_NAME" | grep -Eq '^Tagged:[[:space:]]+yes$'; then
    echo "BUILD_ERROR: PDF is not tagged" >&2
    exit 1
fi

if pdffonts "$BUILD_DIR/$PDF_NAME" | awk 'NR > 2 && ($4 != "yes" || $5 != "yes") { bad=1 } END { exit bad ? 0 : 1 }'; then
    echo "BUILD_ERROR: PDF contains a font that is not embedded and subset" >&2
    exit 1
fi

for required_url in \
    'https://doi.org/10.5281/zenodo.22286929' \
    'https://doi.org/10.5281/zenodo.22262048' \
    'https://creativecommons.org/licenses/by/4.0/' \
    'https://github.com/nicholaskarlson/data'; do
    if ! pdfinfo -url "$BUILD_DIR/$PDF_NAME" | grep -Fq "$required_url"; then
        echo "BUILD_ERROR: PDF lacks live URL: $required_url" >&2
        exit 1
    fi
done

# Replace the public artifacts only after every gate passes.
install -m 0644 "$BUILD_DIR/$DOCX_NAME" "$OUTPUT_DIR/$DOCX_NAME"
install -m 0644 "$BUILD_DIR/$PDF_NAME" "$OUTPUT_DIR/$PDF_NAME"

echo "VOLUME2_PUBLICATION_BUILD_OK"
sha256sum "$OUTPUT_DIR/$DOCX_NAME" "$OUTPUT_DIR/$PDF_NAME"
