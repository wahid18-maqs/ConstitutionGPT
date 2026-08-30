"""FastAPI application entrypoint for ConstituteAI."""

import json
import logging
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from backend.api.routes.auth import router as auth_router
from backend.api.routes.chat import router as chat_router
from backend.api.routes.feedback import router as feedback_router
from backend.api.routes.share import router as share_router
from backend.api.routes.sources import router as sources_router
from backend.config import ALLOWED_ORIGINS, LOCALHOST_ORIGIN_REGEX


class JsonFormatter(logging.Formatter):
	def format(self, record):
		return json.dumps({
			"timestamp": datetime.now(timezone.utc).isoformat(),
			"level": record.levelname,
			"logger": record.name,
			"message": record.getMessage(),
			**getattr(record, "structured", {}),
		})


def configure_logging():
	handler = logging.StreamHandler()
	handler.setFormatter(JsonFormatter())
	root_logger = logging.getLogger()
	root_logger.handlers.clear()
	root_logger.addHandler(handler)
	root_logger.setLevel(logging.INFO)


configure_logging()
logger = logging.getLogger(__name__)


app = FastAPI()
app.state.conversation_histories = {}
app.add_middleware(
	CORSMiddleware,
	allow_origins=list(ALLOWED_ORIGINS),
	allow_origin_regex=LOCALHOST_ORIGIN_REGEX,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(feedback_router)
app.include_router(share_router)
app.include_router(sources_router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
	logger.warning(
		"request validation failed",
		extra={"structured": {"path": request.url.path, "status_code": 422}},
	)
	return JSONResponse(status_code=422, content={"detail": "Invalid request"})


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
	logger.warning(
		"request failed",
		extra={
			"structured": {
				"path": request.url.path,
				"status_code": exc.status_code,
			}
		},
	)
	return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
	logger.exception(
		"unhandled request failure",
		extra={"structured": {"path": request.url.path, "status_code": 500}},
	)
	return JSONResponse(status_code=500, content={"detail": "Internal server error"})
