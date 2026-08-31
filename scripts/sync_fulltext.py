"""Populate public.document_chunks
from the same processed chunk JSONL files scripts/index.py embeds into
Pinecone -- this is a full resync, not incremental, since the table is a
search index rebuilt from those files, not a source of truth of its own.
Re-run whenever the underlying corpus changes (new case ingested, etc.).
"""

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.graph.nodes.citations import citation_for  # noqa: E402
from backend.services.supabase import replace_document_chunks  # noqa: E402
from scripts.index import CHUNKS_DIR, _load_records  # noqa: E402


def build_rows() -> list[dict]:
	chunk_files = sorted(CHUNKS_DIR.rglob("*.jsonl"))
	rows = []
	skipped = 0
	for chunk_path in chunk_files:
		for record in _load_records(chunk_path):
			metadata = record["metadata"]
			citation = citation_for(metadata)
			if citation is None:
				# Same guard as retrieval/citation labeling elsewhere: a
				# chunk whose metadata extraction failed (no article/case_id
				# resolvable) can't be attributed to a source, so it can't
				# be surfaced as a Full-Text Search result either.
				skipped += 1
				continue
			rows.append(
				{
					"source_id": citation["source_id"],
					"label": citation["label"],
					"document_type": metadata["document_type"],
					"chunk_text": record["chunk"]["text"],
				}
			)
	if skipped:
		print(f"Skipped {skipped} chunks with no resolvable source_id")
	return rows


def main() -> None:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("--dry-run", action="store_true", help="build rows without writing to Supabase")
	args = parser.parse_args()

	rows = build_rows()
	print(f"Built {len(rows)} rows from {CHUNKS_DIR}")
	if args.dry_run:
		return
	inserted = replace_document_chunks(rows)
	print(f"Synced {inserted} rows into public.document_chunks")


if __name__ == "__main__":
	main()
