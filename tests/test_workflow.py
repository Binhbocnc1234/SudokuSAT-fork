import pytest
from pysat.solvers import Solver

from core.generateSudokuProblem import generateRandomSudoku
from core.sudokuBuilder import getAvailableEncoders
from core.verifySolution import isValidSolution
from main import PARADIGMS
from solver import solveSudokuPySAT

ENCODERS = getAvailableEncoders()

# The number of completed 4 x 4 Sudoku grids is 288.
SOLUTIONS_OF_EMPTY_4X4 = 288


@pytest.mark.parametrize("encoder", ENCODERS, ids=[e["name"] for e in ENCODERS])
def test_encoder_keeps_exactly_the_sudoku_solutions(encoder):
    # Too few solutions means the encoding forbids valid boards; too many means AMO leaks.
    N = 4
    clauses, _ = encoder["func"]([[0] * N for _ in range(N)])

    count = 0
    with Solver(name="glucose3", bootstrap_with=clauses) as solver:
        while solver.solve():
            primary = solver.get_model()[:N ** 3]
            solver.add_clause([-lit for lit in primary if lit > 0])
            count += 1

    assert count == SOLUTIONS_OF_EMPTY_4X4


@pytest.mark.parametrize("satSolver", ["glucose3", "kissat404"])
@pytest.mark.parametrize("encoder", ENCODERS, ids=[e["name"] for e in ENCODERS])
def test_sat_pipeline_returns_valid_board(encoder, satSolver):
    puzzle, _ = generateRandomSudoku(16, 0.35, seed=0)
    res = solveSudokuPySAT(puzzle, encoder["func"], satSolver, timeLimit=30)

    assert res["status"] == "SAT"
    assert isValidSolution(puzzle, res["board"])


@pytest.mark.parametrize("name", list(PARADIGMS))
def test_paradigm_returns_valid_board(name):
    # 9 x 9 fits the size limits of the CPLEX Community Edition.
    puzzle, _ = generateRandomSudoku(9, 0.35, seed=0)
    res = PARADIGMS[name](puzzle, 30)

    assert res["status"] == "SAT"
    assert isValidSolution(puzzle, res["board"])
