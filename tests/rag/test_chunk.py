"""Unit tests for article and clause boundary extraction."""

import unittest
from pathlib import Path

from scripts.chunk import MetadataContext, _metadata_for_chunk, _scan_lines


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

	def test_multi_article_chunk_is_explicitly_flagged(self):
		metadata = _metadata_for_chunk(
			"14. Equality before law. —Text. 15. Prohibition of discrimination. —Text.",
			MetadataContext(part="III", page=37),
			Path("constitution/source.txt"),
		)
		self.assertEqual(metadata["articles"], ["14", "15"])
		self.assertTrue(metadata["metadata_extraction_failed"])
		self.assertTrue(any("multiple article headers" in warning for warning in metadata["metadata_warnings"]))


if __name__ == "__main__":
	unittest.main()
