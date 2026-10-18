def computeCandidates(grid):
    """
    List the values each empty cell can still take: values not given in its row, column or sub-grid.

    The CP and ILP models are built over these candidates only. The SAT model receives the clues as
    unit clauses instead, and unit propagation removes the same values at decision level 0.

    :param grid: N x N grid, 0 marks an empty cell
    :return: dict (row, col) -> list of candidate values, for empty cells only (0-indexed)
    """
    N = len(grid)
    subN = int(N ** 0.5)

    rowUsed = [set() for _ in range(N)]
    colUsed = [set() for _ in range(N)]
    boxUsed = [set() for _ in range(N)]

    for r in range(N):
        for c in range(N):
            v = grid[r][c]
            if v != 0:
                rowUsed[r].add(v)
                colUsed[c].add(v)
                boxUsed[(r // subN) * subN + c // subN].add(v)

    candidates = {}
    for r in range(N):
        for c in range(N):
            if grid[r][c] == 0:
                used = rowUsed[r] | colUsed[c] | boxUsed[(r // subN) * subN + c // subN]
                candidates[r, c] = [v for v in range(1, N + 1) if v not in used]

    return candidates


def sudokuUnits(N):
    """
    Return the 3N units of the board: every row, column and sub-grid as a list of (row, col) cells.
    """
    subN = int(N ** 0.5)
    units = []

    for i in range(N):
        units.append([(i, c) for c in range(N)])
        units.append([(r, i) for r in range(N)])

    for offsetR in range(0, N, subN):
        for offsetC in range(0, N, subN):
            units.append([(offsetR + r, offsetC + c) for r in range(subN) for c in range(subN)])

    return units
