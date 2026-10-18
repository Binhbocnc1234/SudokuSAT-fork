import random

def generateRandomSudoku(N=9, cluesRatio=0.35, seed=None):
    """
    Generate a random N x N Sudoku puzzle that is guaranteed to be satisfiable.

    A complete board is built from the canonical pattern, then its bands, stacks, rows inside
    a band, columns inside a stack and the symbols are shuffled. Every shuffle preserves validity,
    so the hidden solution is a valid Sudoku. The puzzle may have more than one solution.

    :param N: Board size, a perfect square (9, 16, 25, ...)
    :param cluesRatio: Fraction of the N*N cells that keep their value
    :param seed: Seed of the generator, so every method can be run on the same puzzle
    :return: (puzzle, solution), both N x N lists where 0 marks an empty cell
    """
    rng = random.Random(seed)
    subN = int(N ** 0.5)

    def pattern(r, c):
        return (subN * (r % subN) + r // subN + c) % N

    def shuffle(s):
        return rng.sample(s, len(s))

    rBase = range(subN)
    rows = [g * subN + r for g in shuffle(rBase) for r in shuffle(rBase)]
    cols = [g * subN + c for g in shuffle(rBase) for c in shuffle(rBase)]
    nums = shuffle(range(1, N + 1))

    solution = [[nums[pattern(r, c)] for c in cols] for r in rows]

    numCells = N * N
    numHoles = numCells - int(numCells * cluesRatio)

    puzzle = [row[:] for row in solution]
    for h in rng.sample(range(numCells), numHoles):
        puzzle[h // N][h % N] = 0

    return puzzle, solution
