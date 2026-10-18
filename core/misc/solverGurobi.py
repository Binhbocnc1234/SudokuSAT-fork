import time

import gurobipy as gurobi
from gurobipy import GRB

from core.misc.candidates import computeCandidates, sudokuUnits


def solveSudokuGurobi(grid, timeLimit=60.0, threads=1):
    """
    Solve the Sudoku problem as a 0-1 ILP feasibility model with Gurobi.
    x[r, c, v] = 1 when empty cell (r, c) takes candidate v.

    :return: dict with status, encTime and solveTime in seconds, and the board (None unless SAT)
    """
    N = len(grid)

    encStart = time.perf_counter()
    candidates = computeCandidates(grid)
    keys = [(r, c, v) for (r, c), values in candidates.items() for v in values]

    model = gurobi.Model("Sudoku_Gurobi")
    model.setParam("OutputFlag", 0)
    model.setParam("Threads", threads)

    x = model.addVars(keys, vtype=GRB.BINARY, name="x")

    for (r, c), values in candidates.items():
        model.addConstr(gurobi.quicksum(x[r, c, v] for v in values) == 1)

    for unit in sudokuUnits(N):
        given = {grid[r][c] for (r, c) in unit if grid[r][c] != 0}
        for v in range(1, N + 1):
            if v not in given:
                model.addConstr(gurobi.quicksum(x[r, c, v] for (r, c) in unit if (r, c, v) in x) == 1)

    model.update()
    encTime = time.perf_counter() - encStart

    result = {"status": "TIMEOUT", "encTime": encTime, "solveTime": 0.0, "board": None}
    remainingTime = timeLimit - encTime
    if remainingTime > 0:
        model.setParam("TimeLimit", remainingTime)

        solveStart = time.perf_counter()
        model.optimize()
        result["solveTime"] = time.perf_counter() - solveStart

        if model.SolCount > 0:
            result["status"] = "SAT"
            board = [row[:] for row in grid]
            for (r, c, v), var in x.items():
                if var.X > 0.5:
                    board[r][c] = v
            result["board"] = board
        elif model.Status == GRB.INFEASIBLE:
            result["status"] = "UNSAT"

    model.dispose()
    return result
