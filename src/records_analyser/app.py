import os
import tempfile
import time
from importlib.metadata import version
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .records_analyser import RecordsAnalyser
from .exceptions import RecordsAnalyserError
from .schemas import DataAnalysis, HealthResponse
from .manifest import MANIFEST

# Sourced from pyproject.toml at install time so the FastAPI service version
# always matches the installed package — no manual sync required.
_VERSION = version("records-analyser")
_START_TIME = time.time()
_lens = RecordsAnalyser()

app = FastAPI(
    title="records-analyser",
    description="Structured data profiling API",
    version=_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — desktop mode allows any localhost origin (for Electron)
if os.getenv("RECORDS_ANALYSER_MODE") == "desktop":
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=(
            r"^(https?://localhost(:\d+)?"
            r"|https?://127\.0\.0\.1(:\d+)?"
            r"|file://.*"
            r"|null)$"
        ),
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    _origins = os.getenv(
        "RECORDS_ANALYSER_ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:5173",
    ).split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in _origins],
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

# Optional rate limiting — off by default, enable with RECORDS_ANALYSER_RATE_LIMIT_ENABLED=true
if os.getenv("RECORDS_ANALYSER_RATE_LIMIT_ENABLED", "false").lower() == "true":
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.errors import RateLimitExceeded
    from slowapi.util import get_remote_address

    _limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = _limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]


@app.get("/")
async def root() -> dict[str, Any]:
    return {
        "service": "records-analyser",
        "version": _VERSION,
        "status": "running",
        "endpoints": {"health": "/health", "analyse": "/analyse"},
    }


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        version=_VERSION,
        uptime=round(time.time() - _START_TIME, 1),
    )


@app.get("/manifest")
async def manifest() -> dict:
    return MANIFEST


@app.post("/analyse", response_model=DataAnalysis)
async def analyse(
    file: UploadFile = File(..., description="Data file to analyse"),
) -> DataAnalysis:
    suffix = Path(file.filename or "upload").suffix or ".csv"
    content = await file.read()

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        data = _lens.analyse(tmp_path)
        return DataAnalysis(**data)
    except RecordsAnalyserError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        tmp_path.unlink(missing_ok=True)
