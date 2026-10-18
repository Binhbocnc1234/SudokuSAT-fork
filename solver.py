import multiprocessing
import time
from threading import Timer

from pysat.solvers import Solver

from core.generateSudokuClauses import decodeModel

# PySAT cannot interrupt these solvers, so they run in a child process that is killed at the limit.
UNINTERRUPTIBLE_SOLVERS = ("cadical", "kissat")


def solveInChild(solverName, clauses, conn):
    loadStart = time.perf_counter()
    solver = Solver(name=solverName, bootstrap_with=clauses)
    loadTime = time.perf_counter() - loadStart

    solveStart = time.perf_counter()
    isSat = solver.solve()
    pureSolveTime = time.perf_counter() - solveStart

    conn.send((isSat, solver.get_model() if isSat else None, loadTime, pureSolveTime))
    solver.delete()


def solveWithKill(solverName, clauses, timeLimit):
    """
    Run solveInChild in a forked process, which shares clauses without copying them.
    :return: (isSat or None on timeout, model, loadTime, pureSolveTime)
    """
    parentConn, childConn = multiprocessing.Pipe(duplex=False)
    process = multiprocessing.get_context("fork").Process(target=solveInChild, args=(solverName, clauses, childConn))
    process.start()

    # Receive before join: a large model fills the pipe and blocks the child until it is read.
    if parentConn.poll(timeLimit):
        outcome = parentConn.recv()
        process.join()
        return outcome

    process.kill()
    process.join()
    return None, None, 0.0, timeLimit


def solveSudokuPySAT(grid, encoderFunc, solverName="glucose3", timeLimit=60.0):
    """
    Solve the Sudoku problem with a PySAT solver.
    The run is TIMEOUT when encoding, loading and solving together exceed timeLimit seconds.

    :param grid: Sudoku grid of size N x N, 0 marks an empty cell
    :param encoderFunc: Function grid -> (clauses, totalVar)
    :param solverName: PySAT solver name, such as glucose3, cadical195, kissat404
    :param timeLimit: Time budget of the whole run, in seconds
    :return: dict with status, sizes, times in seconds and the decoded board (None unless SAT)
    """
    N = len(grid)
    maxVar = N ** 3

    encStart = time.perf_counter()
    clauses, totalVar = encoderFunc(grid)
    encTime = time.perf_counter() - encStart

    stats = {
        "status": "TIMEOUT",
        "totalVar": totalVar,
        "auxVar": totalVar - maxVar,
        "numClauses": len(clauses),
        "encTime": encTime,
        "solveTime": 0.0,
        "pureSolveTime": 0.0,
        "board": None
    }

    remainingTime = timeLimit - encTime
    if remainingTime <= 0:
        return stats

    if solverName.startswith(UNINTERRUPTIBLE_SOLVERS):
        isSat, model, loadTime, stats["pureSolveTime"] = solveWithKill(solverName, clauses, remainingTime)
        stats["solveTime"] = loadTime + stats["pureSolveTime"]
        if isSat is True:
            stats["status"] = "SAT"
            stats["board"] = decodeModel(model, N)
        elif isSat is False:
            stats["status"] = "UNSAT"
        return stats

    loadStart = time.perf_counter()
    solver = Solver(name=solverName, bootstrap_with=clauses)
    loadTime = time.perf_counter() - loadStart
    remainingTime -= loadTime

    if remainingTime > 0:
        # solve_limited returns None when the timer interrupts the search.
        timer = Timer(remainingTime, solver.interrupt)
        timer.start()

        solveStart = time.perf_counter()
        isSat = solver.solve_limited(expect_interrupt=True)
        stats["pureSolveTime"] = time.perf_counter() - solveStart

        timer.cancel()

        if isSat is True:
            stats["status"] = "SAT"
            stats["board"] = decodeModel(solver.get_model(), N)
        elif isSat is False:
            stats["status"] = "UNSAT"

    stats["solveTime"] = loadTime + stats["pureSolveTime"]
    solver.delete()

    return stats
