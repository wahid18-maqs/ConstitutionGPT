"""Unit tests for article and clause boundary extraction."""

import unittest
from pathlib import Path

from scripts.chunk import (
	MetadataContext,
	_metadata_for_chunk,
	_scan_lines,
	_segment_by_context,
	chunk_text,
)


class ChunkBoundaryTests(unittest.TestCase):
	def context_after(self, text, marker):
		offset = text.index(marker)
		return next(
			context
			for context_offset, context in reversed(_scan_lines(text))
			if context_offset <= offset
		)

	def test_body_suffixed_article_14_header(self):
		text = "13. Laws inconsistent with rights. —Text.\n14. Equality before law. —The State shall not deny."
		context = self.context_after(text, "14.")
		self.assertEqual(context.article, "14")
		self.assertIsNone(context.clause)

	def test_footnote_prefixed_article_21a_header(self):
		text = "21. Protection of life. —Text.\n2 [21A. Right to education. —The State shall provide."
		context = self.context_after(text, "21A.")
		self.assertEqual(context.article, "21A")
		self.assertIsNone(context.clause)

	def test_article_32_header(self):
		text = "31C. Saving of laws. —Text.\n32. Remedies for enforcement of rights conferred by this Part .—(1) The right to move."
		context = self.context_after(text, "32.")
		self.assertEqual(context.article, "32")

	def test_article_161_header(self):
		text = "160. Governor contingencies. —Text.\n161. Power of Governor to grant pardons, etc., and to suspend, remit sentences .—The Governor shall."
		context = self.context_after(text, "161.")
		self.assertEqual(context.article, "161")

	def test_clause_is_reset_when_article_changes(self):
		text = "14. Equality before law. —Text.\n(1) Every person.\n15. Prohibition of discrimination. —Text."
		contexts = _scan_lines(text)
		clause_offset = text.index("(1)")
		article_14 = next(context for offset, context in contexts if offset == clause_offset)
		article_15 = next(context for offset, context in contexts if offset == text.index("15."))
		self.assertEqual(article_14.article, "14")
		self.assertEqual(article_14.clause, "1")
		self.assertEqual(article_15.article, "15")
		self.assertIsNone(article_15.clause)

	def test_unexpected_second_header_in_a_chunk_is_flagged_not_silently_retagged(self):
		# In the real pipeline, chunking now segments at article boundaries
		# first (see test_chunk.py's segmentation tests below), so this
		# shouldn't normally happen. This exercises the diagnostic fallback
		# directly: if a chunk somehow still contains a second article-shaped
		# header beyond what its trusted segment context says, that must be
		# flagged for review -- never silently used to retag the chunk (that
		# silent-retagging was the root cause of a real bug: a genuine
		# Article 21 chunk got mistagged "article: 22" this way, making
		# Article 21 unreachable via search).
		metadata = _metadata_for_chunk(
			"14. Equality before law. —Text. 15. Prohibition of discrimination. —Text.",
			MetadataContext(article="14", part="III", page=37),
			Path("constitution/source.txt"),
		)
		self.assertEqual(metadata["article"], "14")
		self.assertTrue(metadata["metadata_extraction_failed"])
		self.assertTrue(
			any("article-shaped header" in warning for warning in metadata["metadata_warnings"])
		)


class ScheduleBoundaryRegressionTests(unittest.TestCase):
	"""Regression tests for the schedule/list-number collision bug: real SC
	judgment content was found wrongly tagged article=21/16/etc. because a
	Schedule's own numbered paragraphs or Act-list entries were mistaken for
	article headers."""

	def _chunk_and_tag(self, text: str) -> list[dict]:
		contexts = _scan_lines(text)
		segments = _segment_by_context(text, contexts)
		records = []
		for seg_start, seg_end, seg_context in segments:
			for _, chunk in chunk_text(text[seg_start:seg_end], chunk_size=1000, chunk_overlap=300):
				records.append(_metadata_for_chunk(chunk, seg_context, Path("constitution/source.txt")))
		return records

	def test_sixth_schedule_paragraph_21_is_not_tagged_article_21(self):
		text = (
			"20. Protection in respect of conviction for offences. —(1) No person shall be convicted.\n"
			"1[SIXTH SCHEDULE\n"
			"[Articles 244(2) and 275(1)]\n"
			"Provisions as to the Administration of Tribal Areas.\n"
			"20. Constitution of District Councils. —There shall be a District Council.\n"
			"21. Autonomous districts and autonomous regions.—(1) Subject to the provisions of this "
			"paragraph, the tribal areas in each item of the table shall be an autonomous district.\n"
		)
		records = self._chunk_and_tag(text)
		self.assertTrue(records)
		# The one real article before the Schedule begins is legitimately
		# tagged as such -- only the Schedule's own paragraphs must be exempt.
		self.assertEqual(records[0]["article"], "20")
		self.assertEqual(records[0]["category"], "article")
		schedule_records = records[1:]
		self.assertTrue(schedule_records)
		for record in schedule_records:
			self.assertIsNone(record["article"])
			self.assertEqual(record["category"], "schedule")
			self.assertEqual(record["schedule"], "SIXTH")

	def test_ninth_schedule_act_list_entries_are_not_tagged_as_articles(self):
		text = (
			"1[NINTH SCHEDULE\n"
			"(Article 31B)\n"
			"1. The Bihar Land Reforms Act, 1950 (Bihar Act XXX of 1950).\n"
			"16. The Resettlement of Displaced Persons (Land Acquisition) Act, 1948 (Act LX of 1948).\n"
			"17. Sections 52A to 52G of the Insurance Act, 1938 (Act IV of 1938).\n"
		)
		records = self._chunk_and_tag(text)
		self.assertTrue(records)
		for record in records:
			self.assertIsNone(record["article"])
			self.assertEqual(record["category"], "schedule")
			self.assertEqual(record["schedule"], "NINTH")

	def test_article_21_is_findable_despite_21_21a_22_collision(self):
		# Reproduces the exact real-world collision: Article 21's operative
		# text sits next to 21A and 22's headers. Before the fix, the
		# "closest header to the chunk midpoint" heuristic could tag this
		# whole blob "article: 22", making the real Article 21 text
		# unreachable via an article=21 filter. After the fix, segmentation
		# splits this into one chunk per article, so Article 21 gets its
		# own correctly-tagged chunk.
		text = (
			"20. Protection in respect of conviction for offences. —(1) No person shall be convicted "
			"of any offence except for violation of a law in force at the time.\n"
			"21. Protection of life and personal liberty. —No person shall be deprived of his life or "
			"personal liberty except according to procedure established by law.\n"
			"2 [21A. Right to education. —The State shall provide free and compulsory education to all "
			"children of the age of six to fourteen years in such manner as the State may, by law, determine.]\n"
			"22. Protection against arrest and detention in certain cases. —(1) No person who is "
			"arrested shall be detained in custody without being informed of the grounds for such arrest.\n"
		)
		contexts = _scan_lines(text)
		segments = _segment_by_context(text, contexts)
		records = []
		for seg_start, seg_end, seg_context in segments:
			segment_text = text[seg_start:seg_end]
			for _, chunk in chunk_text(segment_text, chunk_size=1000, chunk_overlap=300):
				records.append((chunk, _metadata_for_chunk(chunk, seg_context, Path("constitution/source.txt"))))

		article_21_chunks = [
			(chunk, meta) for chunk, meta in records
			if meta["article"] == "21" and "personal liberty" in chunk
		]
		self.assertTrue(
			article_21_chunks,
			"Article 21's real text must be reachable in a chunk whose primary article tag is '21'",
		)
		# And it must not be bundled with 21A/22's own header text as one
		# multi-article blob -- each article gets its own chunk now.
		chunk, meta = article_21_chunks[0]
		self.assertNotIn("21A", chunk)
		self.assertNotIn("22.", chunk)
		# metadata_extraction_failed may still be True for an unrelated
		# reason (no page number in this synthetic snippet) -- what actually
		# matters for this regression is that there's no article-collision
		# warning, i.e. this chunk isn't flagged for containing some OTHER
		# article's header too.
		self.assertFalse(
			any("article-shaped header" in warning for warning in meta["metadata_warnings"])
		)


if __name__ == "__main__":
	unittest.main()
