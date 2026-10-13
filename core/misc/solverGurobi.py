import time

import gurobipy as gurobi
from gurobipy import GRB


def solveSudokuGurobi(grid):
    solverStart = time.perf_counter()
    timeoutBenchmark = 20

    N = len(grid)
    subN = int(N ** 0.5)

    model = gurobi.Model("Sudoku_Gurobi")
    model.setParam('OutputFlag', 0)
    model.setParam('TimeLimit', 5)

    x = model.addVars(N, N, range(1, N + 1), vtype=GRB.BINARY, name="x")

    for row in range(N):
        for col in range(N):
            model.addConstr(x.sum(row, col, '*') == 1)

    for value in range(1, N + 1):
        for row in range(N):

            model.addConstr(x.sum(row, '*', value) == 1) 
        for col in range(N):

            model.addConstr(x.sum('*', col, value) == 1)  
            
        for offsetR in range(subN):
            for offsetC in range(subN):
                model.addConstr(
                    gurobi.quicksum(x[offsetR * subN + subR, offsetC * subN + subC, value] 
                                for subR in range(subN) for subC in range(subN)) == 1
                )

    for row in range(N):
        for col in range(N):
            if grid[row][col] != 0:
                model.addConstr(x[row, col, grid[row][col]] == 1)

    model.optimize()
    solverTime = (time.perf_counter() - solverStart)

    if model.status == GRB.OPTIMAL:
        return {"status": "COMPLETED", "solvingTime": solverTime}
    return {"status": "TIMEOUT", "solvingTime": solverTime}
