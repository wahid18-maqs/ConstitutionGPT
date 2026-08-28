"""Extract text from source PDFs into the processed data directory."""

from pathlib import Path

from pypdf import PdfReader


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def load_pdf(file_path: Path) -> str:
	"""Read and concatenate the text content of every page in a PDF."""
	reader = PdfReader(file_path)
	text = ""
	for page in reader.pages:
		text += page.extract_text() or ""
	return text


def process_pdf(file_path: Path) -> Path:
	"""Extract one PDF and write its text to the matching processed path."""
	relative_path = file_path.relative_to(RAW_DIR)
	output_path = (PROCESSED_DIR / relative_path).with_suffix(".txt")
	output_path.parent.mkdir(parents=True, exist_ok=True)
	output_path.write_text(load_pdf(file_path), encoding="utf-8")
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
