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

# Case-sensitive on purpose, same reasoning as SCHEDULE_PATTERN below: every
# genuine top-level Part heading in this source is rendered ALL-CAPS
# ("PART III"); every mixed-case "Part III..." is a mid-sentence
# cross-reference (e.g. "Part III during emergencies...", "Part II of the
# First Schedule to the Constitution...") -- empirically confirmed against
# every match in the corpus. Under re.IGNORECASE these cross-references
# were being mistaken for real Part headings, which (among other things)
# wrongly reset Schedule-boundary tracking mid-Schedule.
PART_PATTERN = re.compile(r"^\s*PART\s+([IVXLCDM]+A?)\b")
ARTICLE_PATTERN = re.compile(
	r"(?<![A-Za-z])(?<!article )(?<!articles )(?:\d+\s+)?(?:\[\s*)?"
	r"([0-9]{1,3}[A-Z]?)(?:\s*\])?\.\s+"
	r"([A-Z][^\n]*?)(?=\s*(?:—|--|$))"
)
ARTICLE_REFERENCE_PATTERN = re.compile(r"\barticles?\s+([0-9]{1,3}[A-Z]?)\b", re.IGNORECASE)
CLAUSE_PATTERN = re.compile(r"(?<!\w)\(([0-9]+|[a-z])\)\s+")
EXPLICIT_CLAUSE_PATTERN = re.compile(r"\bclause\s*\(?\s*([0-9]+|[a-z])\s*\)?", re.IGNORECASE)
PAGE_PATTERN = re.compile(r"^\s*([0-9]{1,4})\s*$")

# This exact front-matter/body divider appears (a small handful of times, as
# a cover-page title) before the source's own front matter -- a full table
# of contents that itself lists every real Part I..XXII in order (which is
# what makes a naive "Part numbers only move forward" check insufficient on
# its own: the ToC walks the whole sequence once before the real body walks
# it again) -- and then a final time immediately before the real Preamble
# and Part I. Everything up to and including the LAST occurrence is treated
# as front matter and excluded from article/Part/Schedule tracking.
FRONT_MATTER_END_PATTERN = re.compile(r"^\s*THE\s+CONSTITUTION\s+OF\s+INDIA\s*$", re.MULTILINE)

# Genuine Schedule HEADINGS are always rendered in ALL CAPS in this source
# ("SIXTH SCHEDULE") — every mixed-case "Sixth Schedule"/"First Schedule" in
# the corpus is a mid-sentence cross-reference or footnote, never a real
# heading (verified against every match in the document). No re.IGNORECASE
# here on purpose: that's what makes the distinction reliable.
# The optional "(?:\d*\[\s*)?" prefix tolerates the amendment-footnote
# marker this source actually renders real headings with — e.g. the real
# heading is literally "1[FIRST SCHEDULE", "1[NINTH SCHEDULE", etc. Without
# this, nearly every real Schedule heading in the document is missed
# entirely (confirmed: First, Fourth, Ninth, Tenth, Eleventh, and Twelfth
# Schedule all follow this exact "<digit>[<NAME> SCHEDULE" shape).
SCHEDULE_PATTERN = re.compile(
	r"^\s*(?:\d*\[\s*)?(FIRST|SECOND|THIRD|FOURTH|FIFTH|SIXTH|SEVENTH|EIGHTH|NINTH|TENTH|ELEVENTH|TWELFTH)\s+SCHEDULE\b"
)

# The Constitution's 22 real top-level Parts, in document order. A genuine
# top-level Part heading only ever appears once and the sequence only ever
# moves forward. Several Schedules have their own internal "PART A/B/C/D"
# or even "PART I"/"PART II" sub-headings (e.g. the Sixth Schedule's tribal
# areas table) that are lexically identical to a real top-level Part
# heading -- same ALL-CAPS rendering, sometimes even the same roman
# numeral. The only reliable way to tell them apart is this ordering: a
# Schedule's internal "PART I" shows up long after the real Part XXII was
# already reached, so it fails a forward-only sequence check that a
# genuine next top-level Part always passes.
_TOP_LEVEL_PART_SEQUENCE = [
	"I", "II", "III", "IV", "IVA", "V", "VI", "VII", "VIII", "IX", "IXA",
	"X", "XI", "XII", "XIII", "XIV", "XIVA", "XV", "XVI", "XVII", "XVIII",
	"XIX", "XX", "XXI", "XXII",
]
_TOP_LEVEL_PART_INDEX = {name: index for index, name in enumerate(_TOP_LEVEL_PART_SEQUENCE)}


@dataclass
class MetadataContext:
	article: str | None = None
	clause: str | None = None
	part: str | None = None
	page: int | None = None
	schedule: str | None = None
	in_schedule: bool = False


def _metadata_for_chunk(text: str, context: MetadataContext, source_path: Path) -> dict:
	"""Build the Section 5 metadata shape, trusting the segment-level context.

	Chunks are pre-segmented at article/Schedule boundaries before this is
	called (see `_segment_by_context`), so — unlike the old heuristic, which
	re-derived `article` from an independent, Schedule-blind regex scan of
	each chunk's own raw text and would happily overwrite a correct context
	with whatever numbered-list item a Schedule paragraph happened to
	contain — this trusts the caller's `context` directly. It still re-scans
	the chunk's own text, but only as a diagnostic cross-check: if a chunk
	unexpectedly still contains an article-shaped header that doesn't match
	its segment's article, that's flagged for review, never silently used
	to override the trusted context.
	"""
	warnings = []
	article = None if context.in_schedule else context.article

	if not context.in_schedule:
		local_headers = {match.group(1).upper() for match in ARTICLE_PATTERN.finditer(text)}
		unexpected = local_headers - ({article} if article else set())
		if unexpected:
			warnings.append(
				f"chunk also contains article-shaped header(s) beyond its segment's "
				f"article ({article!r}): {', '.join(sorted(unexpected))}"
			)

	if context.in_schedule:
		category = "schedule"
	elif "preamble" in text.lower():
		category = "preamble"
	elif article:
		category = "article"
	else:
		category = "constitutional_text"

	if article is None and not context.in_schedule:
		warnings.append("article could not be identified")
	if context.page is None:
		warnings.append("page could not be identified")

	return {
		"article": article,
		"clause": context.clause,
		"part": context.part,
		"schedule": context.schedule,
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


def _front_matter_end(text: str) -> int:
	"""Offset where the source's front matter (title page, table of
	contents, abbreviations list) ends and the real Preamble/Part I begins.
	0 if the marker isn't found (nothing is excluded)."""
	matches = list(FRONT_MATTER_END_PATTERN.finditer(text))
	return matches[-1].end() if matches else 0


def _scan_lines(text: str) -> list[tuple[int, MetadataContext]]:
	"""Record metadata context (including Schedule state) at each line offset."""
	contexts = []
	context = MetadataContext()
	offset = 0
	front_matter_end = _front_matter_end(text)
	# How far along the real, forward-only top-level Part sequence we've
	# progressed so far (-1 = none yet). See _TOP_LEVEL_PART_SEQUENCE.
	last_real_part_index = -1
	for line in text.splitlines(keepends=True):
		if offset < front_matter_end:
			# Front matter (title page / table of contents / abbreviations
			# list) walks the same Part numbering the real body does -- it's
			# excluded entirely rather than tracked, both because it isn't
			# real constitutional text and because letting it run would
			# exhaust the forward-only Part sequence check below before the
			# real body even begins.
			contexts.append((offset, MetadataContext(**context.__dict__)))
			offset += len(line)
			continue

		part_match = PART_PATTERN.match(line)
		schedule_match = SCHEDULE_PATTERN.match(line)
		clause_match = CLAUSE_PATTERN.match(line)
		page_match = PAGE_PATTERN.match(line)

		if part_match:
			part_index = _TOP_LEVEL_PART_INDEX.get(part_match.group(1).upper())
			if part_index is not None and part_index >= last_real_part_index:
				last_real_part_index = part_index
				context.part = part_match.group(1).upper()
				context.in_schedule = False
				context.schedule = None
			# else: matches a real Part identifier out of forward sequence
			# (e.g. a Schedule's own internal "PART I"/"PART II" table, or a
			# roman numeral that isn't one of the 22 real Parts at all,
			# like a Schedule's "PART C"/"PART D") -- a Schedule-internal
			# sub-heading, not a real top-level Part; ignored for boundary
			# tracking purposes.

		if schedule_match:
			context.in_schedule = True
			context.schedule = schedule_match.group(1).upper()
			context.article = None
			context.clause = None

		if not context.in_schedule:
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


def _segment_by_context(
	text: str, contexts: list[tuple[int, MetadataContext]]
) -> list[tuple[int, int, MetadataContext]]:
	"""Split text into runs that each stay within one article (or one
	Schedule), so no downstream chunk can ever span two different articles
	or cross a Schedule boundary. This is what fixes a chunk conflating
	multiple articles at the source, rather than papering over it with a
	secondary "articles" list that retrieval would have to know to check.
	"""
	def key(context: MetadataContext) -> tuple:
		# `schedule` must be part of the segmentation key on its own --
		# `in_schedule` alone stays True continuously across a
		# Schedule-to-Schedule transition (e.g. Second Schedule directly
		# into Third Schedule), so without this, one giant segment would
		# span multiple different Schedules and every chunk in it would be
		# stamped with whichever schedule name happened to be current at
		# that segment's start, not its own real content.
		return (context.article, context.in_schedule, context.schedule)

	if not contexts:
		return [(0, len(text), MetadataContext())]
	segments = []
	seg_start, seg_context = contexts[0]
	for offset, context in contexts[1:]:
		if key(context) != key(seg_context):
			if offset > seg_start:
				segments.append((seg_start, offset, seg_context))
			seg_start, seg_context = offset, context
	if seg_start < len(text):
		segments.append((seg_start, len(text), seg_context))
	return segments


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


def process_text_file(
	source_path: Path, chunk_size: int = 1000, chunk_overlap: int = 300
) -> tuple[Path, Path, int]:
	"""Chunk one processed text file — segmented by article/Schedule boundary
	first, then windowed within each segment — and write chunk/metadata JSONL.
	"""
	text = source_path.read_text(encoding="utf-8")
	relative_path = source_path.relative_to(PROCESSED_DIR)
	chunk_path = (CHUNKS_DIR / relative_path).with_suffix(".jsonl")
	metadata_path = (METADATA_DIR / relative_path).with_suffix(".jsonl")
	chunk_path.parent.mkdir(parents=True, exist_ok=True)
	metadata_path.parent.mkdir(parents=True, exist_ok=True)

	contexts = _scan_lines(text)
	segments = _segment_by_context(text, contexts)

	chunk_records = []
	metadata_records = []
	index = 0
	for seg_start, seg_end, seg_context in segments:
		segment_text = text[seg_start:seg_end]
		for _, chunk in chunk_text(segment_text, chunk_size, chunk_overlap):
			metadata = _metadata_for_chunk(chunk, seg_context, relative_path)
			chunk_records.append({"chunk_id": index, "text": chunk})
			metadata_records.append({"chunk_id": index, **metadata})
			index += 1

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
	"""Chunk every processed constitution text file below data/processed/constitution/.

	Case-law text has its own chunker (`scripts/chunk_case_law.py`) — this
	one's article/Schedule-boundary logic doesn't apply to judgments, so it
	must not touch `data/processed/case_law/`.
	"""
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("--chunk-size", type=int, default=1000)
	parser.add_argument("--chunk-overlap", type=int, default=300)
	args = parser.parse_args()
	CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
	METADATA_DIR.mkdir(parents=True, exist_ok=True)
	constitution_dir = PROCESSED_DIR / "constitution"
	text_files = sorted(constitution_dir.glob("*.txt")) if constitution_dir.is_dir() else []
	for source_path in text_files:
		chunk_path, metadata_path, count = process_text_file(source_path, args.chunk_size, args.chunk_overlap)
		print(f"Chunked {source_path} -> {chunk_path} and {metadata_path} ({count} chunks)")
	if not text_files:
		print(f"No processed text files found in {constitution_dir}")


if __name__ == "__main__":
	main()
