"""Application configuration for ConstituteAI."""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / "backend" / ".env")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "constituteai")
PINECONE_NAMESPACE = os.getenv("PINECONE_NAMESPACE", "constitution-v3")
PINECONE_CLOUD = os.getenv("PINECONE_CLOUD", "aws")
PINECONE_REGION = os.getenv("PINECONE_REGION", "us-east-1")
RERANK_ENABLED = os.getenv("RERANK_ENABLED", "false").lower() == "true"
EMBEDDING_MODEL = os.getenv(
	"EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-l6-v2"
)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
ALLOWED_ORIGINS = tuple(
	origin.strip()
	for origin in os.getenv(
		"ALLOWED_ORIGINS",
		"http://localhost:3000,http://localhost:5173,"
		"http://127.0.0.1:3000,http://127.0.0.1:5173",
	).split(",")
	if origin.strip()
)
# Vite picks the next free port (5174, 5175, ...) whenever 5173 is already
# taken, which would otherwise mean editing ALLOWED_ORIGINS by hand every
# time. `VERCEL` is set automatically in every Vercel deployment, so this
# regex only ever applies to local development, never production -
# ALLOWED_ORIGINS above stays the sole, explicit allowlist there.
IS_VERCEL = bool(os.getenv("VERCEL"))
LOCALHOST_ORIGIN_REGEX = None if IS_VERCEL else r"^http://(localhost|127\.0\.0\.1):\d+$"
