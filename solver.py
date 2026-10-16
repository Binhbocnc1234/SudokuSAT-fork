from multiprocessing import Process, Queue
import time
from pysat.solvers import Glucose3

def pysatSolverWorker(clauses, resultQueue):
    solver = Glucose3()

    solver.append_formula(clauses)

    solverStart = time.perf_counter()
    solveResult = solver.solve()
    solverTime = time.perf_counter() - solverStart

    solver.delete()

    resultQueue.put((solveResult, solverTime))

def solveSudokuPySAT(grid, encoderFunc):
    """
    Solve the Sudoku problem using Glucose3 PySAT solver.
    TIMEOUT when the solver exceeds a certain benchmark.

    :param grid: Sudoku grid of size N x N
    :param encoderFunc: Encoder function
    """

    # INITIALIZE PARAMS
    startTime = time.perf_counter()

    timeoutBenchmark = 20

    N = len(grid)
    maxVar = N ** 3

    status = "TIMEOUT"
    isSat = None
    clauses = []
    totalVar = 0
    encTime = 0.0
    solverTime = 0.0

    # ENCODING
    encStart = time.perf_counter()
    clauses, totalVar = encoderFunc(grid)
    encTime = time.perf_counter() - encStart

    # SOLVING
    remainingTime = timeoutBenchmark - encTime

    if remainingTime > 0:
        resultQueue = Queue()

        # Initiate a Worker process to isolate PySAT's C++ thread
        p = Process(target=pysatSolverWorker, args=(clauses, resultQueue))
        
        p.start()
        p.join(timeout=remainingTime)  # Wait for a maximum of remainingTime seconds

        if p.is_alive():
            # If time exceeded, Process is still running -> TIMEOUT
            # Force C++ to stop immediately.

            p.terminate()
            p.join()

            status = "TIMEOUT"
            isSat = None
            solverTime = remainingTime

        else:
            if not resultQueue.empty():

                isSat, solverTime = resultQueue.get()
                status = "SAT" if isSat else "UNSAT"

            else:
                status = "ERROR"
                isSat = None

    else:
        # If encoding phase also exceeded -> TIMEOUT
        status = "TIMEOUT"
        isSat = None
        solverTime = 0.0

    totalTime = time.perf_counter() - startTime

    stats = {
        "status" : status,
        "gridSize": f"{N}x{N}",
        "maxVar": maxVar,
        "totalVar": totalVar,
        "auxVar": totalVar - maxVar if totalVar > 0 else 0,
        "numClauses": len(clauses),
        "encTime": encTime,
        "solverTime": solverTime,
        "totalTime": totalTime
    }


    return stats