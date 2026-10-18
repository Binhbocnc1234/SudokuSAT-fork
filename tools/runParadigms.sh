#!/usr/bin/env bash
# Experiment 3: SAT against CP-SAT, CPLEX CP, Gurobi and CPLEX MIP. Writes results/paradigms.csv.
# GRB_LICENSE_FILE must point to a Gurobi license; the CPLEX pip package is the Community Edition.
set -euo pipefail
cd "$(dirname "$0")/.."
ENCODER="${1:?usage: tools/runParadigms.sh <encoder name> <SAT solver>...}"
shift
rm -f results/paradigms.csv
.venv/bin/python main.py paradigms --encoders "$ENCODER" --sat-solvers "$@" \
    --sizes 9 16 25 36 --instances 10 --clues 0.35 --timeout 60 --out results/paradigms.csv
.venv/bin/python main.py paradigms --encoders "$ENCODER" --sat-solvers "$@" \
    --sizes 49 --instances 5 --clues 0.35 --timeout 60 --out results/paradigms.csv
