#!/usr/bin/env bash
# Experiment 2: five PySAT solvers on the encoding that won Experiment 1. Writes results/solvers.csv.
set -euo pipefail
cd "$(dirname "$0")/.."
ENCODER="${1:?usage: tools/runSolvers.sh <encoder name>}"
SOLVERS="minisat22 glucose3 glucose4 cadical195 kissat404"
rm -f results/solvers.csv
.venv/bin/python main.py solvers --encoders "$ENCODER" --sat-solvers $SOLVERS \
    --sizes 9 16 25 36 --instances 10 --clues 0.35 --timeout 60 --out results/solvers.csv
# 49 x 49 runs reach the time limit often, so they use 5 puzzles to bound the experiment length.
.venv/bin/python main.py solvers --encoders "$ENCODER" --sat-solvers $SOLVERS \
    --sizes 49 --instances 5 --clues 0.35 --timeout 60 --out results/solvers.csv
