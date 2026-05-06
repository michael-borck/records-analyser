from typing import Any

import pandas as pd


def profile_dataframe(df: pd.DataFrame) -> dict[str, Any]:
    """Statistical profile of a DataFrame."""
    if df.empty:
        return {"rows": 0, "columns": 0, "column_profiles": {}, "sample": []}

    column_profiles: dict[str, Any] = {}
    for col in df.columns:
        series = df[col]
        missing = int(series.isna().sum())
        profile: dict[str, Any] = {
            "dtype": str(series.dtype),
            "missing": missing,
            "missing_pct": round(missing / len(series) * 100, 1),
        }

        if pd.api.types.is_numeric_dtype(series):
            valid = series.dropna()
            profile.update({
                "type": "numeric",
                "min": float(valid.min()) if not valid.empty else None,
                "max": float(valid.max()) if not valid.empty else None,
                "mean": round(float(valid.mean()), 4) if not valid.empty else None,
                "median": round(float(valid.median()), 4) if not valid.empty else None,
                "std": round(float(valid.std()), 4) if not valid.empty else None,
                "q25": round(float(valid.quantile(0.25)), 4) if not valid.empty else None,
                "q75": round(float(valid.quantile(0.75)), 4) if not valid.empty else None,
            })
        else:
            top = series.value_counts().head(5)
            profile.update({
                "type": "categorical",
                "unique": int(series.nunique()),
                "top_values": {str(k): int(v) for k, v in top.items()},
            })

        column_profiles[str(col)] = profile

    sample = df.head(5).fillna("").astype(str).to_dict(orient="records")

    return {
        "rows": len(df),
        "columns": len(df.columns),
        "column_profiles": column_profiles,
        "sample": sample,
    }


def profile_raw(obj: Any) -> dict[str, Any]:
    """Structural profile of a non-tabular Python object (dict, list)."""
    if isinstance(obj, dict):
        return {
            "type": "object",
            "keys": len(obj),
            "key_names": list(obj.keys())[:20],
        }
    if isinstance(obj, list):
        return {
            "type": "array",
            "length": len(obj),
            "element_type": type(obj[0]).__name__ if obj else "unknown",
        }
    return {"type": type(obj).__name__}
