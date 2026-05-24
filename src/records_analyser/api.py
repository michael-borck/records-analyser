import os
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from lens_contract import add_contract_routes, upload_tempfile

from .records_analyser import RecordsAnalyser
from .exceptions import RecordsAnalyserError
from .schemas import DataAnalysis
from .manifest import MANIFEST

_lens = RecordsAnalyser()

# MANIFEST["version"] is the installed package version (resolved by lens-contract),
# so the FastAPI service version always matches the package — no manual sync.
app = FastAPI(
    title="records-analyser",
    description="Structured data profiling API",
    version=MANIFEST["version"],
    docs_url="/docs",
    redoc_url="/redoc",
)

# GET /health and GET /manifest (the family contract, via lens-contract).
add_contract_routes(app, MANIFEST)

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
        "version": MANIFEST["version"],
        "status": "running",
        "endpoints": {"health": "/health", "analyse": "/analyse"},
    }


@app.post("/analyse", response_model=DataAnalysis)
async def analyse(
    file: UploadFile = File(..., description="Data file to analyse"),
) -> DataAnalysis:
    content = await file.read()
    with upload_tempfile(content, file.filename) as tmp_path:
        try:
            data = _lens.analyse(tmp_path)
            return DataAnalysis(**data)
        except RecordsAnalyserError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
