# records-analyser — basic usage

Structured data profiling for tabular records (CSV, Excel, Parquet, SQLite, JSON/YAML/XML).

## Install

```bash
pip install records-analyser
```

## CLI

```bash
records-analyser data.csv

# raw JSON
records-analyser data.csv --json
```

## Python

```python
from records_analyser import RecordsAnalyser

result = RecordsAnalyser().analyse("data.csv")
print(result["format"], result["file_size"])
print(result["profile"]["rows"], result["profile"]["columns"])
```

## HTTP

```bash
records-analyser serve --port 8003

curl -F file=@data.csv http://localhost:8003/analyse
```
