"""Citation-accuracy metric: does every source_id the pipeline actually
cited appear in what was actually retrieved? Neither Ragas nor DeepEval
ships this check natively -- it's specific to this project's
anti-fabrication design (backend/graph/nodes/generation.py's
_resolve_citations already drops any model-claimed source_id that isn't
in the retrieved set, so this metric is a runtime regression guard on
that guarantee, not expected to ever fail against the current pipeline).
"""

from deepeval.metrics import BaseMetric


class CitationAccuracyMetric(BaseMetric):
	def __init__(self, threshold: float = 1.0):
		self.threshold = threshold
		self.score = None
		self.success = None
		self.reason = None
		self.error = None

	def measure(self, test_case) -> float:
		try:
			cited = set(test_case.cited_source_ids)
			available = set(test_case.available_source_ids)
			if not cited:
				self.score = 1.0  # nothing cited, nothing to be wrong about
			else:
				self.score = len(cited & available) / len(cited)
			self.success = self.score >= self.threshold
			self.reason = (
				f"{len(cited & available)}/{len(cited)} cited source_ids actually "
				f"appear in retrieved context (cited={sorted(cited)}, "
				f"available={sorted(available)})"
			)
			return self.score
		except Exception as exc:
			self.error = str(exc)
			raise

	async def a_measure(self, test_case) -> float:
		return self.measure(test_case)

	def is_successful(self) -> bool:
		if self.error is not None:
			self.success = False
		return bool(self.success)

	@property
	def __name__(self):
		return "Citation Accuracy"
