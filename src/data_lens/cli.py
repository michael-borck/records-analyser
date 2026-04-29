"""CLI entry point for data-lens.

Usage:
  data-lens analyse data.csv
  data-lens analyse data.xlsx --json
  data-lens analyse data.db
"""

import json
import sys
from pathlib import Path


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        prog="data-lens",
        description="Structured data profiling",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    analyse = sub.add_parser("analyse", help="Profile a data file")
    analyse.add_argument("file", type=Path, help="Path to data file")
    analyse.add_argument("--json", action="store_true", dest="as_json",
                         help="Output raw JSON")

    args = parser.parse_args()

    if args.command == "analyse":
        from .data_lens import DataLens

        result = DataLens().analyse(args.file)

        if args.as_json:
            if not result["success"]:
                print(json.dumps(result, indent=2, default=str), file=sys.stderr)
                sys.exit(1)
            print(json.dumps(result, indent=2, default=str))
            return

        if not result["success"]:
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)

        data = result["data"]
        print(f"Format:    {data['format']}")
        print(f"File size: {data['file_size']:,} bytes")

        if data.get("warning"):
            print(f"Warning:   {data['warning']}")

        if "tables" in data:
            print(f"Tables:    {', '.join(data['tables'].keys())}")
            for name, profile in data["tables"].items():
                print(f"\n  [{name}] {profile['rows']} rows x {profile['columns']} columns")
        elif "profile" in data:
            profile = data["profile"]
            if "rows" in profile:
                print(f"Shape:     {profile['rows']} rows x {profile['columns']} columns")
                print("\nColumn profiles:")
                for col, info in profile["column_profiles"].items():
                    if info["type"] == "numeric":
                        print(f"  {col}: numeric  min={info['min']}  max={info['max']}  mean={info['mean']}  missing={info['missing']}")
                    else:
                        print(f"  {col}: categorical  unique={info['unique']}  missing={info['missing']}")
            else:
                for k, v in profile.items():
                    print(f"  {k}: {v}")
