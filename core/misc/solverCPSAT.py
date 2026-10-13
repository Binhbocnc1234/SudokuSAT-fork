import time
from ortools.sat.python import cp_model

def solveSudokuCPSAT(grid):
    solverStart = time.perf_counter()
    timeoutBenchmark = 20

    N = len(grid)
    subN = int(N ** 0.5)

    model = cp_model.CpModel()

    cells = {}

    for row in range(N):
        for col in range(N):
            if grid[row][col] != 0: cells[row,col] = grid[row][col]

            else: cells[row, col] = model.new_int_var(1, N, f'cell_{row}_{col}')

    for i in range(N):
        model.add_all_different([cells[i, j] for j in range(N)])
        model.add_all_different([cells[j, i] for j in range(N)])

    for offsetR in range(subN):
        for offsetC in range(subN):
            block = [cells[offsetR * subN + subR, offsetC * subN + subC]
                    for subR in range(subN) for subC in range(subN)]

            model.add_all_different(block)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = timeoutBenchmark

    status = solver.Solve(model)

    solverTime = (time.perf_counter() - solverStart)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return {"status": "COMPLETED", "solvingTime": solverTime}
    return {"status": "TIMEOUT", "solvingTime": solverTime}
    
    