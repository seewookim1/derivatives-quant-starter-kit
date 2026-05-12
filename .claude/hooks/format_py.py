#!/usr/bin/env python3
"""PostToolUse hook: ruff format + ruff check --fix on edited .py files."""
import json
import subprocess
import sys


def main():
    payload = json.load(sys.stdin)
    file_path = payload.get("tool_input", {}).get("file_path", "")
    if not file_path.endswith(".py"):
        return

    for cmd in [
        ["ruff", "format", file_path],
        ["ruff", "check", "--fix", file_path],
    ]:
        result = subprocess.run(cmd, capture_output=True, text=True)
        # ruff check exits 1 when it finds fixable issues (not an error)
        if result.returncode not in (0, 1):
            print(result.stderr, file=sys.stderr)
            sys.exit(result.returncode)


if __name__ == "__main__":
    main()
