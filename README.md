# data-lens

Structured data profiling for the [prism lens family](https://github.com/michael-borck/prism).

Loads structured data files and returns statistical summaries, schema inference, missing value counts, and sample rows. Supports tabular formats (CSV, XLSX, Parquet), databases (SQLite), and semi-structured formats (JSON, YAML, XML).

## Install

```bash
pip install data-lens
```

Requires Python 3.11+.

## Usage

### Python

```python
from data_lens import DataLens

result = DataLens().analyse("survey.csv")

if result["success"]:
    profile = result["data"]["profile"]
    print(f"Rows: {profile['rows']}, Columns: {profile['columns']}")
    for col, info in profile["column_profiles"].items():
        print(f"  {col}: {info['type']}, missing={info['missing']}")
```

### CLI

```bash
# Human-readable output
data-lens analyse data.csv
data-lens analyse report.db        # profiles all SQLite tables
data-lens analyse config.json      # works, but warns if it looks like config data

# Machine-readable JSON
data-lens analyse data.xlsx --json
```

## Supported formats

| Format | Extensions |
|--------|-----------|
| CSV / TSV | `.csv` `.tsv` |
| Excel | `.xlsx` `.xls` |
| Parquet | `.parquet` |
| SQLite | `.sqlite` `.db` `.sqlite3` |
| JSON | `.json` |
| YAML | `.yaml` `.yml` |
| XML | `.xml` |

JSON and YAML files that look like configuration objects (not arrays of records) include a soft warning suggesting [document-lens](https://github.com/michael-borck/document-lens) for prose content instead.

## Output shape

```json
{
  "success": true,
  "data": {
    "format": "csv",
    "file_path": "/path/to/data.csv",
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
      "sample": [{"age": "28", "country": "Australia"}]
    }
  }
}
```

SQLite results include a `tables` dict with one profile per table.

## Part of the prism family

data-lens is one lens in a family of analysis tools routed by [prism](https://github.com/michael-borck/prism):

- [document-lens](https://github.com/michael-borck/document-lens) — PDFs, DOCX, PPTX, Markdown
- [data-lens](https://github.com/michael-borck/data-lens) — CSV, XLSX, SQLite, JSON, YAML
- [audio-lens](https://github.com/michael-borck/audio-lens) — audio transcription and speech metrics
- [prism](https://github.com/michael-borck/prism) — meta-router: detects format and calls the right lens

## License

MIT
