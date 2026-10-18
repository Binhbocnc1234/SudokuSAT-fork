def isValidSolution(puzzle, board):
    """
    Check that board is a complete Sudoku that keeps every clue of puzzle.

    :param puzzle: N x N grid, 0 marks an empty cell
    :param board: N x N grid returned by a solver
    :return: True when every row, column and sub-grid holds 1..N exactly once
    """
    N = len(puzzle)
    subN = int(N ** 0.5)
    full = set(range(1, N + 1))

    for r in range(N):
        for c in range(N):
            if puzzle[r][c] != 0 and board[r][c] != puzzle[r][c]:
                return False

    for i in range(N):
        if set(board[i]) != full: return False
        if {board[r][i] for r in range(N)} != full: return False

    for offsetR in range(0, N, subN):
        for offsetC in range(0, N, subN):
            block = {board[offsetR + r][offsetC + c] for r in range(subN) for c in range(subN)}
            if block != full: return False

    return True
