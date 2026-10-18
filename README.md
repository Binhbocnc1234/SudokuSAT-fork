# SudokuSAT

Exact solving of generalized N x N Sudoku with SAT (PySAT), compared with CP (OR-Tools CP-SAT, CPLEX CP Optimizer) and ILP (Gurobi, CPLEX MIP). Forked from [Vanillinium/SudokuSAT](https://github.com/Vanillinium/SudokuSAT).

The paper is [paper/main.pdf](paper/main.pdf).

## Setup

```bash
uv venv .venv --python 3.12
uv pip install --python .venv/bin/python -r requirements.txt
export GRB_LICENSE_FILE=/path/to/gurobi.lic
```

Gurobi needs a license file (free for academic use). The `cplex` package is the CPLEX Community Edition: it refuses MIP models above 1000 variables or constraints and CP models whose search space is above 2^1000, and those runs are recorded as `SIZE_LIMIT`.

## Layout

| Path | Holds |
|---|---|
| `core/encoderCustom.py` | Pairwise, Binary, Product and Commander At-Most-One encodings |
| `core/encoderPySATDefault.py` | Sequential Counter and Ladder, through `pysat.card` |
| `core/generateSudokuClauses.py` | The SAT model: Exactly-One over cells, rows, columns and boxes |
| `solver.py` | Runs a PySAT solver with a time limit |
| `core/misc/` | CP-SAT, CPLEX CP, Gurobi and CPLEX MIP models |
| `main.py` | Benchmark command line; one CSV row per run |
| `tools/` | Experiment scripts and `makeReport.py`, which builds the paper's tables |
| `results/` | Raw results of the three experiments |
| `tests/` | Workflow tests |

## Run

```bash
.venv/bin/python -m pytest -q tests
tools/runEncoders.sh
tools/runSolvers.sh Pairwise
tools/runParadigms.sh Pairwise glucose3 kissat404
.venv/bin/python tools/makeReport.py
cd paper && latexmk -pdf main.tex
```

A single benchmark, for example two encodings on five 25 x 25 puzzles:

```bash
.venv/bin/python main.py encoders --encoders Pairwise Commander --sizes 25 --instances 5 --out results/try.csv
```
