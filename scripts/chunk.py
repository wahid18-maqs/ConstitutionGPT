"""Chunk processed source text and emit heuristic metadata for each chunk."""

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
CHUNKS_DIR = PROCESSED_DIR / "chunks"
METADATA_DIR = PROCESSED_DIR / "metadata"

PART_PATTERN = re.compile(r"^\s*PART\s+([IVXLCDM]+A?)\b", re.IGNORECASE)
ARTICLE_PATTERN = re.compile(
	r"(?<![A-Za-z])(?<!article )(?<!articles )(?:\d+\s+)?(?:\[\s*)?"
	r"([0-9]{1,3}[A-Z]?)(?:\s*\])?\.\s+"
	r"([A-Z][^\n]*?)(?=\s*(?:—|--|$))"
)
ARTICLE_REFERENCE_PATTERN = re.compile(r"\barticles?\s+([0-9]{1,3}[A-Z]?)\b", re.IGNORECASE)
CLAUSE_PATTERN = re.compile(r"(?<!\w)\(([0-9]+|[a-z])\)\s+")
EXPLICIT_CLAUSE_PATTERN = re.compile(r"\bclause\s*\(?\s*([0-9]+|[a-z])\s*\)?", re.IGNORECASE)
PAGE_PATTERN = re.compile(r"^\s*([0-9]{1,4})\s*$")
SCHEDULE_PATTERN = re.compile(r"^\s*(FIRST|SECOND|THIRD|FOURTH|FIFTH|SIXTH|SEVENTH|EIGHTH|NINTH|TENTH|ELEVENTH|TWELFTH)\s+SCHEDULE\b", re.IGNORECASE)


@dataclass
class MetadataContext:
	article: str | None = None
	clause: str | None = None
	part: str | None = None
	page: int | None = None


def _metadata_for_chunk(text: str, context: MetadataContext, source_path: Path) -> dict:
	"""Build the Section 5 metadata shape and flag weak heuristic matches."""
	warnings = []
	article_matches = list(ARTICLE_PATTERN.finditer(text))
	article_ids = list(dict.fromkeys(match.group(1).upper() for match in article_matches))
	if article_ids:
		middle = len(text) / 2
		primary_match = min(article_matches, key=lambda match: abs(match.start() - middle))
		context = MetadataContext(
			article=primary_match.group(1).upper(),
			clause=None,
			part=context.part,
			page=context.page,
		)
		if len(article_ids) > 1:
			warnings.append(f"multiple article headers in chunk: {', '.join(article_ids)}")
		context_articles = article_ids
	else:
		context_articles = [context.article] if context.article else []
	category = "constitutional_text"
	if "preamble" in text.lower():
		category = "preamble"
	elif "schedule" in text.lower() and context.article is None:
		category = "schedule"
	elif context.article:
		category = "article"
	if context.article is None:
		warnings.append("article could not be identified")
	if context.page is None:
		warnings.append("page could not be identified")

	return {
		"article": context.article,
		"articles": context_articles,
		"clause": context.clause,
		"part": context.part,
		"schedule": None,
		"amendment": None,
		"category": category,
		"document_type": "constitution",
		"source_type": "constitutional_text",
		"language": "english",
		"page": context.page,
		"source_file": str(source_path),
		"metadata_extraction_failed": bool(warnings),
		"metadata_warnings": warnings,
	}


def _scan_lines(text: str) -> list[tuple[int, MetadataContext]]:
	"""Record metadata context at each line offset in the source text."""
	contexts = []
	context = MetadataContext()
	offset = 0
	for line in text.splitlines(keepends=True):
		part_match = PART_PATTERN.match(line)
		article_match = ARTICLE_PATTERN.match(line)
		schedule_match = SCHEDULE_PATTERN.match(line)
		clause_match = CLAUSE_PATTERN.match(line)
		page_match = PAGE_PATTERN.match(line)
		if part_match:
			context.part = part_match.group(1).upper()
		article_matches = list(ARTICLE_PATTERN.finditer(line))
		for article_match in article_matches:
			context.article = article_match.group(1).upper()
			context.clause = None
		if not article_matches and not context.article:
			reference_match = ARTICLE_REFERENCE_PATTERN.search(line)
			if reference_match:
				context.article = reference_match.group(1).upper()
		explicit_clause_match = EXPLICIT_CLAUSE_PATTERN.search(line)
		if explicit_clause_match and context.article:
			context.clause = explicit_clause_match.group(1).lower()
		elif clause_match and context.article:
			context.clause = clause_match.group(1)
		if page_match and int(page_match.group(1)) > 0:
			context.page = int(page_match.group(1))
		if schedule_match:
			context.article = None
			context.clause = None
		contexts.append((offset, MetadataContext(**context.__dict__)))
		offset += len(line)
	return contexts


def _context_at(offset: int, contexts: list[tuple[int, MetadataContext]]) -> MetadataContext:
	"""Return the latest metadata context at a character offset."""
	current = MetadataContext()
	for context_offset, context in contexts:
		if context_offset > offset:
			break
		current = context
	return current


def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 300) -> list[tuple[int, str]]:
	"""Split text into overlapping windows, preferring paragraph boundaries."""
	if chunk_size <= 0 or chunk_overlap < 0 or chunk_overlap >= chunk_size:
		raise ValueError("chunk_size must be positive and chunk_overlap must be smaller")
	chunks = []
	start = 0
	while start < len(text):
		end = min(start + chunk_size, len(text))
		if end < len(text):
			boundary = text.rfind("\n\n", start + chunk_size // 2, end)
			if boundary > start:
				end = boundary
		chunks.append((start, text[start:end].strip()))
		if end >= len(text):
			break
		start = max(end - chunk_overlap, start + 1)
	return [(offset, chunk) for offset, chunk in chunks if chunk]


def process_text_file(source_path: Path) -> tuple[Path, Path, int]:
	"""Chunk one processed text file and write chunk and metadata JSONL files."""
	text = source_path.read_text(encoding="utf-8")
	relative_path = source_path.relative_to(PROCESSED_DIR)
	chunk_path = (CHUNKS_DIR / relative_path).with_suffix(".jsonl")
	metadata_path = (METADATA_DIR / relative_path).with_suffix(".jsonl")
	chunk_path.parent.mkdir(parents=True, exist_ok=True)
	metadata_path.parent.mkdir(parents=True, exist_ok=True)
	contexts = _scan_lines(text)
	chunk_records = []
	metadata_records = []
	for index, (offset, chunk) in enumerate(chunk_text(text)):
		metadata = _metadata_for_chunk(
			chunk, _context_at(offset, contexts), relative_path
		)
		chunk_records.append({"chunk_id": index, "text": chunk})
		metadata_records.append({"chunk_id": index, **metadata})
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
	"""Chunk every processed text file below data/processed/."""
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("--chunk-size", type=int, default=1000)
	parser.add_argument("--chunk-overlap", type=int, default=300)
	args = parser.parse_args()
	CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
	METADATA_DIR.mkdir(parents=True, exist_ok=True)
	text_files = sorted(
		path for path in PROCESSED_DIR.rglob("*.txt") if not path.is_relative_to(CHUNKS_DIR) and not path.is_relative_to(METADATA_DIR)
	)
	for source_path in text_files:
		chunk_path, metadata_path, count = process_text_file(source_path)
		print(f"Chunked {source_path} -> {chunk_path} and {metadata_path} ({count} chunks)")
	if not text_files:
		print(f"No processed text files found in {PROCESSED_DIR}")


if __name__ == "__main__":
	main()
