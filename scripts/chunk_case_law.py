"""Chunk processed case-law judgment text, preserving paragraph structure."""

import argparse
import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.chunk import chunk_text  # noqa: E402

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
CASE_LAW_PROCESSED_DIR = PROCESSED_DIR / "case_law"
CHUNKS_DIR = PROCESSED_DIR / "chunks" / "case_law"
METADATA_DIR = PROCESSED_DIR / "metadata" / "case_law"

# A standard Supreme Court judgment paragraph: a line starting with a
# paragraph number followed by a period and a space, e.g. "13. This leads".
PARAGRAPH_PATTERN = re.compile(r"(?m)^\s*(\d{1,4})\.\s+")

# A genuinely paragraph-numbered judgment keeps paragraphs page-sized or
# smaller throughout. Older scans (e.g. Maneka Gandhi's 1978 JUDIS text) only
# number a short headnote summary and then run on as unnumbered prose for the
# rest of the opinion — matching against that headnote alone would merge the
# entire remaining judgment into one oversized "paragraph". Treating any
# split with an oversized paragraph as unreliable and falling back to fixed
# windows catches that case.
MAX_PARAGRAPH_CHARS = 6000

# Per-file case metadata that isn't reliably recoverable from body text alone.
CASE_METADATA = {
	"maneka_gandhi_1978": {
		"case_name": "Maneka Gandhi v. Union of India",
		"year": 1978,
		"court": "Supreme Court of India",
	},
	"shreya_singhal_2015": {
		"case_name": "Shreya Singhal v. Union of India",
		"year": 2015,
		"court": "Supreme Court of India",
	},
}


def split_by_paragraph_number(text: str) -> list[str]:
	"""Split judgment text on numbered paragraph markers, if present."""
	matches = list(PARAGRAPH_PATTERN.finditer(text))
	if len(matches) < 3:
		return []
	paragraphs = []
	for index, match in enumerate(matches):
		start = match.start()
		end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
		paragraph = text[start:end].strip()
		if paragraph:
			paragraphs.append(paragraph)
	if any(len(paragraph) > MAX_PARAGRAPH_CHARS for paragraph in paragraphs):
		return []
	return paragraphs


def chunk_case_text(text: str) -> list[str]:
	"""Chunk judgment text by numbered paragraph, falling back to fixed windows."""
	paragraphs = split_by_paragraph_number(text)
	if paragraphs:
		return paragraphs
	return [chunk for _, chunk in chunk_text(text)]


def case_metadata_for(case_id: str) -> dict:
	"""Return the known case metadata for a slug, or a flagged placeholder."""
	if case_id in CASE_METADATA:
		return dict(CASE_METADATA[case_id])
	return {"case_name": None, "year": None, "court": None}


def _metadata_for_chunk(case_id: str, chunk_index: int) -> dict:
	"""Build the Section 5 case-law metadata shape for one chunk."""
	case_info = case_metadata_for(case_id)
	warnings = []
	if case_info["case_name"] is None:
		warnings.append(f"no case metadata registered for '{case_id}'")
	return {
		"case_id": case_id,
		"case_name": case_info["case_name"],
		"year": case_info["year"],
		"court": case_info["court"],
		"category": "constitutional_law",
		"document_type": "case_law",
		"source_type": "case_law",
		"language": "english",
		"source_file": case_id,
		"metadata_extraction_failed": bool(warnings),
		"metadata_warnings": warnings,
	}


def process_case_file(source_path: Path) -> tuple[Path, Path, int]:
	"""Chunk one processed case-law text file and write chunk/metadata JSONL."""
	text = source_path.read_text(encoding="utf-8")
	case_id = source_path.stem
	chunk_path = (CHUNKS_DIR / source_path.name).with_suffix(".jsonl")
	metadata_path = (METADATA_DIR / source_path.name).with_suffix(".jsonl")
	chunk_path.parent.mkdir(parents=True, exist_ok=True)
	metadata_path.parent.mkdir(parents=True, exist_ok=True)

	chunk_records = []
	metadata_records = []
	for index, chunk in enumerate(chunk_case_text(text)):
		chunk_records.append({"chunk_id": index, "text": chunk})
		metadata_records.append({"chunk_id": index, **_metadata_for_chunk(case_id, index)})

	chunk_path.write_text(
		"\n".join(json.dumps(record, ensure_ascii=True) for record in chunk_records) + "\n",
		encoding="utf-8",
	)
	metadata_path.write_text(
		"\n".join(json.dumps(record, ensure_ascii=True) for record in metadata_records) + "\n",
		encoding="utf-8",
	)
	return chunk_path, metadata_path, len(chunk_records)


def main() -> None:
	"""Chunk every processed case-law text file below data/processed/case_law/."""
	parser = argparse.ArgumentParser(description=__doc__)
	parser.parse_args()
	CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
	METADATA_DIR.mkdir(parents=True, exist_ok=True)
	text_files = sorted(CASE_LAW_PROCESSED_DIR.glob("*.txt"))
	for source_path in text_files:
		chunk_path, metadata_path, count = process_case_file(source_path)
		print(f"Chunked {source_path} -> {chunk_path} and {metadata_path} ({count} chunks)")
	if not text_files:
		print(f"No processed case-law text files found in {CASE_LAW_PROCESSED_DIR}")


if __name__ == "__main__":
	main()
