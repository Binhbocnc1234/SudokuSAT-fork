import argparse
import csv
import os
import time

from solver import solveSudokuPySAT
from core.generateSudokuProblem import generateRandomSudoku
from core.sudokuBuilder import getAvailableEncoders, getEncoderByName
from core.verifySolution import isValidSolution

from core.misc.solverCPSAT import solveSudokuCPSAT
from core.misc.solverGurobi import solveSudokuGurobi
from core.misc.solverCplexMIP import solveSudokuCplexMIP
from core.misc.solverCplexCP import solveSudokuCplexCP


CSV_HEADERS = [
    "experiment", "gridSize", "cluesRatio", "seed", "method", "encoder", "satSolver", "status", "valid",
    "totalVar", "auxVar", "numClauses", "encTimeMs", "solveTimeMs", "totalTimeMs"
]

PARADIGMS = {
    "CP-SAT": solveSudokuCPSAT,
    "CPLEX-CP": solveSudokuCplexCP,
    "Gurobi": solveSudokuGurobi,
    "CPLEX-MIP": solveSudokuCplexMIP
}


def buildRuns(args):
    """
    List the (method, encoder, satSolver, solve function) combinations of one experiment.
    A solve function maps (grid, timeLimit) to the result dict of its solver module.
    """
    runs = []

    if args.experiment == "encoders":
        for enc in getAvailableEncoders():
            if args.encoders and enc["name"] not in args.encoders: continue
            runs.append(("SAT", enc["name"], args.sat_solvers[0],
                         lambda g, t, e=enc: solveSudokuPySAT(g, e["func"], args.sat_solvers[0], t)))

    elif args.experiment == "solvers":
        enc = getEncoderByName(args.encoders[0] if args.encoders else "Commander")
        for name in args.sat_solvers:
            runs.append(("SAT", enc["name"], name,
                         lambda g, t, n=name: solveSudokuPySAT(g, enc["func"], n, t)))

    else:
        enc = getEncoderByName(args.encoders[0] if args.encoders else "Commander")
        for name in args.sat_solvers:
            runs.append(("SAT", enc["name"], name,
                         lambda g, t, n=name: solveSudokuPySAT(g, enc["func"], n, t)))
        for name, func in PARADIGMS.items():
            runs.append((name, "", "", lambda g, t, f=func: f(g, t)))

    return runs


def main():
    parser = argparse.ArgumentParser(description="Benchmark SAT encodings, SAT solvers and CP/ILP solvers on Sudoku.")
    parser.add_argument("experiment", choices=["encoders", "solvers", "paradigms"])
    parser.add_argument("--sizes", type=int, nargs="+", default=[9, 16, 25, 36])
    parser.add_argument("--instances", type=int, default=10, help="Puzzles per size; seeds 0..instances-1")
    parser.add_argument("--clues", type=float, default=0.35, help="Fraction of cells given as clues")
    parser.add_argument("--timeout", type=float, default=60.0, help="Seconds per run, encoding included")
    parser.add_argument("--encoders", nargs="*", default=[], help="Encoder names; the first one is used by solvers/paradigms")
    parser.add_argument("--sat-solvers", nargs="+", default=["glucose3"], help="PySAT solver names")
    parser.add_argument("--out", required=True, help="CSV file; rows are appended")
    args = parser.parse_args()

    runs = buildRuns(args)
    fileExists = os.path.isfile(args.out)

    with open(args.out, "a", newline="", encoding="utf-8") as csvFile:
        writer = csv.DictWriter(csvFile, fieldnames=CSV_HEADERS)
        if not fileExists: writer.writeheader()

        for N in args.sizes:
            for seed in range(args.instances):
                # Every method of one experiment solves the same puzzles.
                puzzle, _ = generateRandomSudoku(N, args.clues, seed)

                for method, encoder, satSolver, solve in runs:
                    wallStart = time.perf_counter()
                    res = solve(puzzle, args.timeout)
                    wallTime = time.perf_counter() - wallStart

                    valid = res["board"] is not None and isValidSolution(puzzle, res["board"])
                    if res["status"] == "SAT" and not valid:
                        raise RuntimeError(f"{method}/{encoder}/{satSolver} returned an invalid board for N={N}, seed={seed}")

                    writer.writerow({
                        "experiment": args.experiment, "gridSize": N, "cluesRatio": args.clues, "seed": seed,
                        "method": method, "encoder": encoder, "satSolver": satSolver,
                        "status": res["status"], "valid": valid,
                        "totalVar": res.get("totalVar", ""), "auxVar": res.get("auxVar", ""),
                        "numClauses": res.get("numClauses", ""),
                        "encTimeMs": f"{res['encTime'] * 1000:.3f}",
                        "solveTimeMs": f"{res['solveTime'] * 1000:.3f}",
                        "totalTimeMs": f"{wallTime * 1000:.3f}"
                    })
                    csvFile.flush()

                    print(f"N={N:2d} seed={seed} {method:9s} {encoder:10s} {satSolver:10s} "
                          f"{res['status']:10s} {wallTime * 1000:10.1f} ms", flush=True)


if __name__ == "__main__":
    main()
