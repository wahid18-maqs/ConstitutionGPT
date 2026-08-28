"""Extract text from source PDFs into the processed data directory."""

import re
from pathlib import Path

from pypdf import PdfReader


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
CASE_LAW_DIR = RAW_DIR / "case_law"

# Repeated per-page banner in older JUDIS scans, e.g.
# "http://JUDIS.NIC.IN SUPREME COURT OF INDIA Page 12 of 154". pypdf's page
# extraction runs pages together with no guaranteed newline at the boundary,
# so this can appear mid-line rather than on a line of its own.
JUDIS_BOILERPLATE_PATTERN = re.compile(
	r"\s*http://JUDIS\.NIC\.IN\s+SUPREME COURT OF INDIA\s+Page\s+\d+\s+of\s+\d+\s*",
	re.IGNORECASE,
)

# Repeated per-page break left by Indian Kanoon page printouts: a repeated
# "<Case Title> on <date>" header line immediately followed by the
# "Indian Kanoon - http://..." footer (also runs into the next word with no
# separating whitespace). Matched as one pattern, not two independent line
# patterns, so an unrelated line that happens to end in a date is never
# stripped on its own.
INDIAN_KANOON_PAGE_BREAK_PATTERN = re.compile(
	r"(?m)^.*\bon\s+\d{1,2}\s+\w+,\s+\d{4}\s*\n"
	r"Indian Kanoon - http://indiankanoon\.org/doc/\d+/\s*\d*",
	re.IGNORECASE,
)


def load_pdf(file_path: Path) -> str:
	"""Read and concatenate the text content of every page in a PDF."""
	reader = PdfReader(file_path)
	text = ""
	for page in reader.pages:
		text += page.extract_text() or ""
	return text


def strip_case_law_boilerplate(text: str) -> str:
	"""Remove repeated page-banner/footer text from extracted case-law text."""
	text = JUDIS_BOILERPLATE_PATTERN.sub(" ", text)
	text = INDIAN_KANOON_PAGE_BREAK_PATTERN.sub(" ", text)
	return text


def process_pdf(file_path: Path) -> Path:
	"""Extract one PDF and write its text to the matching processed path."""
	relative_path = file_path.relative_to(RAW_DIR)
	output_path = (PROCESSED_DIR / relative_path).with_suffix(".txt")
	output_path.parent.mkdir(parents=True, exist_ok=True)
	text = load_pdf(file_path)
	if file_path.is_relative_to(CASE_LAW_DIR):
		text = strip_case_law_boilerplate(text)
	output_path.write_text(text, encoding="utf-8")
	return output_path


def main() -> None:
	"""Extract all PDFs found below data/raw/."""
	RAW_DIR.mkdir(parents=True, exist_ok=True)
	PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

	pdf_files = sorted(RAW_DIR.rglob("*.pdf"))
	for pdf_file in pdf_files:
		output_path = process_pdf(pdf_file)
		print(f"Extracted {pdf_file} -> {output_path}")

	if not pdf_files:
		print(f"No PDF files found in {RAW_DIR}")


if __name__ == "__main__":
	main()
