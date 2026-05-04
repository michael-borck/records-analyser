"""CLI entry point for data-lens.

Usage:
  datalens analyse data.csv
  datalens analyse data.xlsx --json
  datalens serve
  datalens serve --port 8002 --host 0.0.0.0
"""

import json
import os
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

    serve = sub.add_parser("serve", help="Start the FastAPI HTTP server")
    serve.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("DATA_LENS_PORT", "8002")),
        help="Port to listen on (default: DATA_LENS_PORT or 8002)",
    )
    serve.add_argument(
        "--host",
        default=os.getenv("DATA_LENS_HOST", "127.0.0.1"),
        help="Host to bind (default: DATA_LENS_HOST or 127.0.0.1)",
    )
    serve.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload (development only)",
    )

    args = parser.parse_args()

    if args.command == "analyse":
        _cmd_analyse(args)
    elif args.command == "serve":
        _cmd_serve(args)


def _cmd_analyse(args) -> None:
    from .data_lens import DataLens
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

    data = result
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


def _cmd_serve(args) -> None:
    import uvicorn
    uvicorn.run(
        "data_lens.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    main()
