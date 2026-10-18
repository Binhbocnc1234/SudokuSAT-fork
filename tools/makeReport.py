"""
Turn the CSV files in results/ into the LaTeX table rows that paper/ includes.

Run: .venv/bin/python tools/makeReport.py
"""
import csv
import os
import statistics
from collections import defaultdict

ROOT = os.path.join(os.path.dirname(__file__), "..")
RESULTS = os.path.join(ROOT, "results")
TABLES = os.path.join(ROOT, "paper", "tables")

# A run that did not return a board counts as this many seconds when a median is taken,
# so a median falls on TIMEOUT when more than half of the runs failed.
UNSOLVED = float("inf")


def readRows(name):
    with open(os.path.join(RESULTS, name), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def groupBy(rows, key):
    groups = defaultdict(list)
    for row in rows:
        groups[key(row), int(row["gridSize"])].append(row)
    return groups


def summarize(runs):
    """
    :return: (solved count, run count, median total seconds)
    """
    totals = [float(r["totalTimeMs"]) / 1000 if r["status"] == "SAT" else UNSOLVED for r in runs]
    return sum(r["status"] == "SAT" for r in runs), len(runs), statistics.median(totals)


def formatSeconds(value):
    if value == UNSOLVED: return "TO"
    if value < 0.01: return f"{value:.4f}"
    if value < 10: return f"{value:.3f}"
    return f"{value:.1f}"


def writeTimeTable(groups, methods, sizes, fileName, specialStatus=None):
    """
    One row per method, one column per size; a cell is "median total time (solved/runs)".
    The fastest median of each column is bold.
    """
    lines = []
    best = {}
    for N in sizes:
        medians = [summarize(groups[m, N])[2] for m in methods if (m, N) in groups]
        best[N] = min(medians) if medians else None

    for m in methods:
        cells = []
        for N in sizes:
            runs = groups.get((m, N))
            if not runs:
                cells.append("--")
                continue
            statuses = {r["status"] for r in runs}
            if specialStatus and statuses == {specialStatus}:
                cells.append("SL")
                continue
            solved, total, median = summarize(runs)
            # A median that falls on a refused run is a size limit, not a timeout.
            text = "SL" if specialStatus in statuses and median == UNSOLVED else formatSeconds(median)
            if median == best[N] and median != UNSOLVED: text = f"\\textbf{{{text}}}"
            cells.append(f"{text} ({solved}/{total})")
        lines.append(f"{m} & " + " & ".join(cells) + r" \\")

    with open(os.path.join(TABLES, fileName), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main():
    os.makedirs(TABLES, exist_ok=True)

    rows = readRows("encoders.csv")
    encoders = list(dict.fromkeys(r["encoder"] for r in rows))
    sizes = sorted({int(r["gridSize"]) for r in rows})
    groups = groupBy(rows, lambda r: r["encoder"])
    writeTimeTable(groups, encoders, sizes, "encoderTime.tex")

    if os.path.isfile(os.path.join(RESULTS, "solvers.csv")):
        rows = readRows("solvers.csv")
        solvers = list(dict.fromkeys(r["satSolver"] for r in rows))
        sizes = sorted({int(r["gridSize"]) for r in rows})
        writeTimeTable(groupBy(rows, lambda r: r["satSolver"]), solvers, sizes, "solverTime.tex")

    if os.path.isfile(os.path.join(RESULTS, "paradigms.csv")):
        rows = readRows("paradigms.csv")
        label = lambda r: f"SAT ({r['satSolver']})" if r["method"] == "SAT" else r["method"]
        methods = list(dict.fromkeys(label(r) for r in rows))
        sizes = sorted({int(r["gridSize"]) for r in rows})
        groups = groupBy(rows, label)
        writeTimeTable(groups, methods, sizes, "paradigmTime.tex", specialStatus="SIZE_LIMIT")

    print(f"Wrote tables to {TABLES}")


if __name__ == "__main__":
    main()
