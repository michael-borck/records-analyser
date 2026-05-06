"""CLI entry point for records-analyser.

Usage:
  records-analyser data.csv
  records-analyser data.xlsx --json
  records-analyser results.db
  records-analyser serve
  records-analyser serve --port 8003 --host 0.0.0.0
"""

import json
import os
import sys
from pathlib import Path


def main() -> None:
    import argparse

    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        _main_serve(sys.argv[2:])
        return

    parser = argparse.ArgumentParser(
        prog="records-analyser",
        description="Structured data profiling",
    )
    parser.add_argument("file", type=Path, help="Data file to profile")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Output raw JSON")
    _cmd_analyse(parser.parse_args())


def _main_serve(argv: list[str]) -> None:
    import argparse
    parser = argparse.ArgumentParser(prog="records-analyser serve", description="Start the HTTP server")
    parser.add_argument("--port", type=int, default=int(os.getenv("DATA_LENS_PORT", "8003")))
    parser.add_argument("--host", default=os.getenv("DATA_LENS_HOST", "127.0.0.1"))
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload (development only)")
    _cmd_serve(parser.parse_args(argv))


def _cmd_analyse(args) -> None:
    from .records_analyser import DataLens
    from .exceptions import DataLensError

    try:
        result = DataLens().analyse(args.file)
    except DataLensError as e:
        if args.as_json:
            print(json.dumps({"error": str(e)}, indent=2, default=str), file=sys.stderr)
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.as_json:
        print(json.dumps(result, indent=2, default=str))
        return

    print(f"Format:    {result['format']}")
    print(f"File size: {result['file_size']:,} bytes")

    if result.get("warning"):
        print(f"Warning:   {result['warning']}")

    if "tables" in result:
        print(f"Tables:    {', '.join(result['tables'].keys())}")
        for name, profile in result["tables"].items():
            print(f"\n  [{name}] {profile['rows']} rows x {profile['columns']} columns")
    elif "profile" in result:
        profile = result["profile"]
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


def _cmd_serve(args) -> None:
    import uvicorn
    uvicorn.run(
        "records_analyser.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    main()
