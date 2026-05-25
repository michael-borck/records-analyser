from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from lens_contract import add_contract_routes, add_cors, add_rate_limit, upload_tempfile

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
# CORS — env-driven: RECORDS_ANALYSER_MODE=desktop (Electron) or RECORDS_ANALYSER_ALLOWED_ORIGINS.
add_cors(app, env_prefix="RECORDS_ANALYSER")
# Opt-in rate limiting — RECORDS_ANALYSER_RATE_LIMIT_ENABLED=true (needs the [ratelimit] extra).
add_rate_limit(app, env_prefix="RECORDS_ANALYSER")


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
