"""Embed processed chunks and upsert them into Pinecone."""

import argparse
import json
from pathlib import Path

from backend.services.pinecone import PineconeService


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CHUNKS_DIR = PROJECT_ROOT / "data" / "processed" / "chunks"
METADATA_DIR = PROJECT_ROOT / "data" / "processed" / "metadata"
DEFAULT_NAMESPACE = "constitution"
UPSERT_BATCH_SIZE = 96


def _metadata_path(chunk_path: Path) -> Path:
	return METADATA_DIR / chunk_path.relative_to(CHUNKS_DIR)


def _load_records(chunk_path: Path) -> list[dict]:
	metadata_path = _metadata_path(chunk_path)
	if not metadata_path.exists():
		raise FileNotFoundError(f"Metadata file not found: {metadata_path}")
	chunks = [json.loads(line) for line in chunk_path.read_text(encoding="utf-8").splitlines()]
	metadata = [json.loads(line) for line in metadata_path.read_text(encoding="utf-8").splitlines()]
	metadata_by_id = {record["chunk_id"]: record for record in metadata}
	if len(metadata_by_id) != len(metadata) or len(chunks) != len(metadata):
		raise ValueError(f"Chunk/metadata count mismatch for {chunk_path}")
	return [
		{"chunk": chunk, "metadata": metadata_by_id[chunk["chunk_id"]]}
		for chunk in chunks
	]


def _pinecone_metadata(metadata: dict) -> dict:
	"""Remove nulls while retaining populated schema fields and review flags."""
	return {key: value for key, value in metadata.items() if value is not None}


def _build_records(records: list[dict], source_name: str) -> list[dict]:
	"""Build Pinecone text records for server-side integrated embedding."""
	return [
		{
			"_id": f"{source_name}:{record['chunk']['chunk_id']}",
			"text": record["chunk"]["text"],
			**_pinecone_metadata(record["metadata"]),
		}
		for record in records
	]


def index_chunks(dry_run: bool = False, namespace: str = DEFAULT_NAMESPACE) -> int:
	"""Embed every chunk and optionally upsert the resulting vectors."""
	chunk_files = sorted(CHUNKS_DIR.rglob("*.jsonl"))
	if not chunk_files:
		print(f"No chunk files found in {CHUNKS_DIR}")
		return 0
	service = None if dry_run else PineconeService()
	total = 0
	for chunk_path in chunk_files:
		relative_source = str(chunk_path.relative_to(CHUNKS_DIR).with_suffix(""))
		records = _build_records(_load_records(chunk_path), relative_source)
		if service:
			for start in range(0, len(records), UPSERT_BATCH_SIZE):
				service.upsert_records(records[start:start + UPSERT_BATCH_SIZE], namespace=namespace)
		total += len(records)
		print(f"Prepared {len(records)} records from {chunk_path}")
	print(f"{'Dry run prepared' if dry_run else 'Upserted'} {total} records")
	return total


def main() -> None:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("--dry-run", action="store_true", help="embed and validate without Pinecone writes")
	parser.add_argument("--namespace", default=DEFAULT_NAMESPACE)
	args = parser.parse_args()
	index_chunks(dry_run=args.dry_run, namespace=args.namespace)


if __name__ == "__main__":
	main()
