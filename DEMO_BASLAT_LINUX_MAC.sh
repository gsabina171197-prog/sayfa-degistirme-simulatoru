#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
PY=python3
command -v "$PY" >/dev/null 2>&1 || PY=python
"$PY" --version
"$PY" -m unittest discover -s tests
"$PY" main.py -f data/ornek.txt -k 3 --step
