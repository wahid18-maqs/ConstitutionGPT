"""Gemini-backed DeepEvalBaseLLM, since DeepEval's metrics default to an
OpenAI judge model and this project uses Gemini throughout. Reuses the
same ChatGoogleGenerativeAI + with_structured_output pattern already
proven in backend/graph/nodes/generation.py, instead of adding
google-generativeai/instructor as new dependencies for a raw-SDK wrapper.
"""

from langchain_google_genai import ChatGoogleGenerativeAI

from backend.config import GEMINI_API_KEY, GEMINI_MODEL
from deepeval.models import DeepEvalBaseLLM


class GeminiJudgeModel(DeepEvalBaseLLM):
	def __init__(self):
		# Free-tier Gemini quota is tight (5 req/min on gemini-2.5-flash) and
		# DeepEval's metrics make several judge calls per question -- a
		# generous max_retries lets LangChain's built-in backoff ride out
		# 429s instead of the metric call failing outright.
		self._model = ChatGoogleGenerativeAI(
			model=GEMINI_MODEL, google_api_key=GEMINI_API_KEY, max_retries=10
		)

	def load_model(self, *args, **kwargs):
		return self._model

	def generate(self, prompt: str, *args, **kwargs) -> str:
		return self.load_model().invoke(prompt).content

	async def a_generate(self, prompt: str, *args, **kwargs) -> str:
		result = await self.load_model().ainvoke(prompt)
		return result.content

	def generate_with_schema(self, prompt: str, *args, schema=None, **kwargs):
		model = self.load_model().with_structured_output(schema) if schema else self.load_model()
		return model.invoke(prompt)

	async def a_generate_with_schema(self, prompt: str, *args, schema=None, **kwargs):
		model = self.load_model().with_structured_output(schema) if schema else self.load_model()
		return await model.ainvoke(prompt)

	def get_model_name(self, *args, **kwargs) -> str:
		return GEMINI_MODEL
