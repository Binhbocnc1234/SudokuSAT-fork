#!/usr/bin/env bash
# Experiment 1: the six Exactly-One encodings under Glucose3. Writes results/encoders.csv.
set -euo pipefail
cd "$(dirname "$0")/.."
rm -f results/encoders.csv
.venv/bin/python main.py encoders --sizes 9 16 25 36 --instances 10 --clues 0.35 --timeout 60 \
    --sat-solvers glucose3 --out results/encoders.csv
