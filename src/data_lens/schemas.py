from typing import Any

from pydantic import BaseModel


class DataAnalysis(BaseModel):
    format: str
    file_path: str
    file_size: int
    warning: str | None = None
    profile: dict[str, Any] | None = None
    tables: dict[str, Any] | None = None


class HealthResponse(BaseModel):
    status: str
    version: str
    uptime: float
