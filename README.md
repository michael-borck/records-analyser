# records-analyser

Profiles structured data files and returns row counts, column statistics, schema inference, missing value counts, and sample rows.

Part of the [analyser family](#the-analyser-family).

## Install

```bash
pip install records-analyser
```

Requires Python 3.11+.

## Usage

### Python

```python
from records_analyser import RecordsAnalyser

result = RecordsAnalyser().analyse("survey.csv")

profile = result["profile"]
print(f"Rows: {profile['rows']}, Columns: {profile['columns']}")
for col, info in profile["column_profiles"].items():
    print(f"  {col}: {info['type']}, missing={info['missing']}")
```

### CLI

```bash
# Human-readable summary
records-analyser analyse data.csv

# SQLite — profiles all tables
records-analyser analyse results.db

# Machine-readable JSON
records-analyser analyse data.xlsx --json

# Start the HTTP server
records-analyser serve --port 8003
```

### HTTP API

```bash
curl -X POST http://localhost:8003/analyse \
  -F "file=@data.csv"
```

## Supported formats

| Format | Extensions |
|---|---|
| CSV / TSV | `.csv` `.tsv` |
| Excel | `.xlsx` `.xls` |
| Parquet | `.parquet` |
| SQLite | `.sqlite` `.db` `.sqlite3` |
| JSON | `.json` |
| YAML | `.yaml` `.yml` |
| XML | `.xml` |

JSON and YAML files that look like configuration objects (not arrays of records) include a warning suggesting [document-analyser](https://github.com/michael-borck/document-analyser) for prose content.

## Output

```json
{
  "format": "csv",
  "file_path": "/path/to/survey.csv",
  "file_size": 4096,
  "profile": {
    "rows": 150,
    "columns": 4,
    "column_profiles": {
      "age": {
        "type": "numeric",
        "min": 18.0, "max": 72.0, "mean": 34.2,
        "median": 32.0, "std": 11.4,
        "q25": 25.0, "q75": 42.0,
        "missing": 2, "missing_pct": 1.3
      },
      "country": {
        "type": "categorical",
        "unique": 12,
        "top_values": {"Australia": 45, "USA": 38},
        "missing": 0, "missing_pct": 0.0
      }
    },
    "sample": [{"age": 28, "country": "Australia"}]
  }
}
```

SQLite results include a `tables` key with one profile per table.

## The analyser family

Low-level analysis tools. Each accepts files directly and returns structured JSON. Build your own UI or pipeline on top.

| Package | Handles |
|---|---|
| [speech-analyser](https://github.com/michael-borck/speech-analyser) | audio and video files — transcript and speech metrics |
| [video-analyser](https://github.com/michael-borck/video-analyser) | video files — frames, scenes, and visual quality |
| [document-analyser](https://github.com/michael-borck/document-analyser) | PDF, DOCX, PPTX, TXT — text and readability |
| [code-analyser](https://github.com/michael-borck/code-analyser) | source code — style, complexity, and quality metrics |
| [records-analyser](https://github.com/michael-borck/records-analyser) | CSV, Excel, SQLite, Parquet, JSON — data profiling |
| [auto-analyser](https://github.com/michael-borck/auto-analyser) | any file — detects format and routes to the right tool |

## Licence

MIT
