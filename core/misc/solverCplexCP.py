import os
import sys
import time

from docplex.cp.model import CpoModel
from docplex.cp.utils import CpoException

from core.misc.candidates import computeCandidates, sudokuUnits

# The pip package "cplex" ships the CP Optimizer binary next to the Python interpreter.
CPO_EXECUTABLE = os.path.join(os.path.dirname(sys.executable), "cpoptimizer")


def solveSudokuCplexCP(grid, timeLimit=60.0, threads=1):
    """
    Solve the Sudoku problem with IBM CPLEX CP Optimizer (docplex.cp), one AllDifferent per unit.

    :return: dict with status, encTime and solveTime in seconds, and the board (None unless SAT).
             status is SIZE_LIMIT when the CP Optimizer Community Edition refuses the search space.
    """
    N = len(grid)

    encStart = time.perf_counter()
    candidates = computeCandidates(grid)
    model = CpoModel(name="Sudoku_CplexCP")

    cells = {}
    for (r, c), values in candidates.items():
        cells[r, c] = model.integer_var(domain=values, name=f"cell_{r}_{c}")

    for unit in sudokuUnits(N):
        unitVars = [cells[cell] for cell in unit if cell in cells]
        if len(unitVars) > 1:
            model.add(model.all_diff(unitVars))
    encTime = time.perf_counter() - encStart

    result = {"status": "TIMEOUT", "encTime": encTime, "solveTime": 0.0, "board": None}
    remainingTime = timeLimit - encTime
    if remainingTime <= 0:
        return result

    solveStart = time.perf_counter()
    try:
        solution = model.solve(TimeLimit=remainingTime, Workers=threads, LogVerbosity="Quiet",
                               execfile=CPO_EXECUTABLE)
    except CpoException as e:
        if "size limit" in str(e).lower():
            result["status"] = "SIZE_LIMIT"
            return result
        raise
    result["solveTime"] = time.perf_counter() - solveStart

    status = solution.get_solve_status()
    if solution.is_solution():
        result["status"] = "SAT"
        board = [row[:] for row in grid]
        for (r, c), var in cells.items():
            board[r][c] = solution.get_value(var)
        result["board"] = board
    elif status == "Infeasible":
        result["status"] = "UNSAT"

    return result
