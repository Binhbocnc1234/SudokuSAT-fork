import time

from docplex.mp.model import Model
from docplex.mp.utils import DOcplexLimitsExceeded

from core.misc.candidates import computeCandidates, sudokuUnits


def solveSudokuCplexMIP(grid, timeLimit=60.0, threads=1):
    """
    Solve the Sudoku problem as a 0-1 ILP feasibility model with IBM CPLEX (docplex.mp).
    The model is the one solveSudokuGurobi builds.

    :return: dict with status, encTime and solveTime in seconds, and the board (None unless SAT).
             status is SIZE_LIMIT when the CPLEX Community Edition refuses the model size.
    """
    N = len(grid)

    encStart = time.perf_counter()
    candidates = computeCandidates(grid)
    keys = [(r, c, v) for (r, c), values in candidates.items() for v in values]

    model = Model(name="Sudoku_CplexMIP")
    model.context.cplex_parameters.threads = threads
    x = model.binary_var_dict(keys, name="x")

    for (r, c), values in candidates.items():
        model.add_constraint(model.sum(x[r, c, v] for v in values) == 1)

    for unit in sudokuUnits(N):
        given = {grid[r][c] for (r, c) in unit if grid[r][c] != 0}
        for v in range(1, N + 1):
            if v not in given:
                model.add_constraint(model.sum(x[r, c, v] for (r, c) in unit if (r, c, v) in x) == 1)
    encTime = time.perf_counter() - encStart

    result = {"status": "TIMEOUT", "encTime": encTime, "solveTime": 0.0, "board": None}
    remainingTime = timeLimit - encTime
    if remainingTime > 0:
        model.set_time_limit(remainingTime)

        solveStart = time.perf_counter()
        try:
            solution = model.solve()
        except DOcplexLimitsExceeded:
            result["status"] = "SIZE_LIMIT"
            model.end()
            return result
        result["solveTime"] = time.perf_counter() - solveStart

        if solution is not None:
            result["status"] = "SAT"
            board = [row[:] for row in grid]
            for (r, c, v), var in x.items():
                if solution.get_value(var) > 0.5:
                    board[r][c] = v
            result["board"] = board
        elif "infeasible" in model.solve_details.status.lower():
            result["status"] = "UNSAT"

    model.end()
    return result
