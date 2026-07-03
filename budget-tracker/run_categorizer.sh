#!/usr/bin/env bash
# Run from anywhere — resolves paths relative to this script's folder.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${PYTHON:-python3}"

if ! command -v "$PYTHON" &>/dev/null; then
  echo "Error: python3 not found. Install Python 3 and retry."
  echo "  macOS: brew install python3"
  exit 1
fi

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <bank_statement.csv> [--month YYYY-MM]"
  echo ""
  echo "Examples:"
  echo "  $0 ~/Downloads/icici_june_2026.csv"
  echo "  $0 ~/Downloads/icici_july_2026.csv --month 2026-07"
  echo ""
  echo "Note: Use python3, not python (macOS 'python' is often Python 2.7)."
  exit 1
fi

exec "$PYTHON" "$SCRIPT_DIR/categorize_transactions.py" "$@"
