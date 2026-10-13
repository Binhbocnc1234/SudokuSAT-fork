import signal
import time
from pysat.solvers import Glucose3

class TimeoutException(Exception): pass

def timeoutHandler(signum, frame): raise TimeoutException()

def solveSudoku(grid, encoderFunc):
    """
    Solve the Sudoku problem using Glucose3 PySAT solver.
    TIMEOUT when the solver exceeds a certain benchmark.

    :param grid: Sudoku grid of size N x N
    :param encoderFunc: Encoder function
    """

    # INITIALIZE PARAMS
    timeoutBenchmark = 20

    N = len(grid)
    maxVar = N ** 3

    status = "TIMEOUT"
    isSat = None
    clauses = []
    totalVar = 0
    encTime = 0.0
    solverTime = 0.0
    solver = None

    # REGISTERING ALARM SIGNAL FOR BENCHMARK
    signal.signal(signal.SIGALRM, timeoutHandler)

    startTime = time.perf_counter()
    signal.alarm(timeoutBenchmark)

    try:

        encStart = time.perf_counter()
        clauses, totalVar = encoderFunc(grid)
        encTime = time.perf_counter() - encStart

        solver = Glucose3()
        for clause in clauses:
            solver.add_clause(clause)


        solverStart = time.perf_counter()
        solveResult = solver.solve()
        solverTime = time.perf_counter() - solverStart

        isSat = solveResult
        status = "SAT" if isSat else "UNSAT"

    except TimeoutException:
        status = "TIMEOUT"
        isSat = None

        if encTime == 0.0:
            encTime = time.perf_counter() - startTime
            solverTime = 0.0
        else: 
            solverTime = time.perf_counter() - (startTime + encTime)

    finally:
        signal.alarm(0)

        if solver is not None: solver.delete()

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