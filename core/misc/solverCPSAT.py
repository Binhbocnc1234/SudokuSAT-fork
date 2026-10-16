import time
from ortools.sat.python import cp_model

def solveSudokuCPSAT(grid):
    
    timeoutBenchmark = 20

    N = len(grid)
    subN = int(N ** 0.5)

    status = "TIMEOUT"
    encTime = 0.0
    solverTime = 0.0
    startTime = time.perf_counter()

    try:
        # ENCODING
        encStart = time.perf_counter()

        model = cp_model.CpModel()
        cells = {}

        for row in range(N):
            for col in range(N):
                cells[row, col] = model.new_int_var(1, N, f'cell_{row}_{col}')

                if grid[row][col] != 0: model.add(cells[row, col] == grid[row][col]) 

        for i in range(N):
            model.add_all_different([cells[i, j] for j in range(N)])
            model.add_all_different([cells[j, i] for j in range(N)])

        for offsetR in range(subN):
            for offsetC in range(subN):
                block = [
                    cells[offsetR * subN + subR, offsetC * subN + subC]
                    for subR in range(subN) 
                    for subC in range(subN)
                ]

                model.add_all_different(block)
                
        encTime = time.perf_counter() - encStart

        # SOLVING
        remainingTime = timeoutBenchmark - encTime

        #If encoding has alr exceeded benchmark, return TIMEOUT immediately.
        if remainingTime <= 0:
            status = "TIMEOUT"
            solverTime = 0.0

        else:
            solverStart = time.perf_counter()

            solver = cp_model.CpSolver()
            # solver's benchmark is the remaining time, ensuring both progresses falls under timeoutbenchmark
            solver.parameters.max_time_in_seconds = remainingTime
            solver.parameters.log_search_progress = False

            
            status = solver.Solve(model)

            solverTime = (time.perf_counter() - solverStart)

            if cp_status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                status = "SAT"

            elif cp_status == cp_model.INFEASIBLE:
                status = "UNSAT"

            else:

                status = "TIMEOUT"
    
    except Exception as e:
        status = "ERROR"

    return {
        "status": status,
        "encTime": encTime,
        "solverTime": solverTime
    }
    
    