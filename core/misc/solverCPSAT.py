import time
from ortools.sat.python import cp_model

from core.misc.candidates import computeCandidates, sudokuUnits


def solveSudokuCPSAT(grid, timeLimit=60.0, threads=1):
    """
    Solve the Sudoku problem with Google OR-Tools CP-SAT, one AllDifferent per row, column and sub-grid.

    :return: dict with status, encTime and solveTime in seconds, and the board (None unless SAT)
    """
    N = len(grid)

    encStart = time.perf_counter()
    model = cp_model.CpModel()
    candidates = computeCandidates(grid)

    cells = {}
    for (r, c), values in candidates.items():
        cells[r, c] = model.new_int_var_from_domain(cp_model.Domain.FromValues(values), f"cell_{r}_{c}")

    for unit in sudokuUnits(N):
        unitVars = [cells[cell] for cell in unit if cell in cells]
        if len(unitVars) > 1:
            model.add_all_different(unitVars)
    encTime = time.perf_counter() - encStart

    result = {"status": "TIMEOUT", "encTime": encTime, "solveTime": 0.0, "board": None}
    remainingTime = timeLimit - encTime
    if remainingTime <= 0:
        return result

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = remainingTime
    solver.parameters.num_workers = threads

    solveStart = time.perf_counter()
    cpStatus = solver.solve(model)
    result["solveTime"] = time.perf_counter() - solveStart

    if cpStatus in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        result["status"] = "SAT"
        board = [row[:] for row in grid]
        for (r, c), var in cells.items():
            board[r][c] = solver.value(var)
        result["board"] = board
    elif cpStatus == cp_model.INFEASIBLE:
        result["status"] = "UNSAT"

    return result
