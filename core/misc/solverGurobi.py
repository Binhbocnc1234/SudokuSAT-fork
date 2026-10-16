import time

import gurobipy as gurobi
from gurobipy import GRB


def solveSudokuGurobi(grid):
    
    timeoutBenchmark = 20

    N = len(grid)
    subN = int(N ** 0.5)

    status = "TIMEOUT"
    encTime = 0.0
    solverTime = 0.0

    try:
        # ENCODING
        encStart = time.perf_counter()

        model = gurobi.Model("Sudoku_Gurobi")
        model.setParam('OutputFlag', 0)

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
                        gurobi.quicksum(
                            x[offsetR * subN + subR, offsetC * subN + subC, value] 
                            for subR in range(subN) for subC in range(subN)
                        ) == 1
                    )

        for row in range(N):
            for col in range(N):
                if grid[row][col] != 0:
                    model.addConstr(x[row, col, grid[row][col]] == 1)

        encTime = time.perf_counter() - encStart

        # SOLVING
        remainingTime = timeoutBenchmark - encTime

        if remainingTime <= 0:
            status = "TIMEOUT"
            solverTime = 0.0
        else:
            model.setParam('TimeLimit', remainingTime)

            solverStart = time.perf_counter()

            model.optimize()

            solverTime = (time.perf_counter() - solverStart)

            if model.status == GRB.OPTIMAL: 
                status = "SAT"
            elif model.status == GRB.INFEASIBLE:
                status = "UNSAT"
            elif model.status in (GRB.TIME_LIMIT, GRB.INTERRUPTED):
                status = "TIMEOUT"
            else:
                status = "TIMEOUT"

        model.dispose()
        
    except Exception as e:
        status = "ERROR"

    return {
        "status": status,
        "encTime": encTime,
        "solverTime": solverTime
    }
