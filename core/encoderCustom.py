import math

# Every amoX function appends the At-Most-One clauses of vars to clauses and returns the new
# largest variable ID. Auxiliary variables are numbered from currTopVar + 1.

# Binomial/Pairwise Encoding
# C(n, 2) clauses, 0 auxiliary variables
def amoBinomial(clauses, vars, currTopVar):
    for i in range(len(vars)):
        for j in range(i + 1, len(vars)):
            clauses.append([-vars[i], -vars[j]])

    return currTopVar


# Binary/Bitwise Encoding (Frisch et al.)
# n * ceil(log2 n) clauses, ceil(log2 n) auxiliary variables
def amoBinary(clauses, vars, currTopVar):
    m = len(vars)
    if m <= 1: return currTopVar

    auxNum = math.ceil(math.log2(m))
    auxVars = [currTopVar + i + 1 for i in range(auxNum)]

    # Xi forces the auxiliary bits to spell i in binary, and two distinct indices cannot share
    # one bit pattern, so two true Xi conflict.
    for i, var in enumerate(vars):
        for k in range(auxNum):
            bit = (i >> k) & 1
            clauses.append([-var, auxVars[k] if bit == 1 else -auxVars[k]])

    return currTopVar + auxNum


# Product Encoding (Chen, 2010)
# 2n + O(sqrt n) clauses, 2 sqrt(n) + O(n^(1/4)) auxiliary variables
def amoProduct(clauses, vars, currTopVar):
    m = len(vars)
    if m <= 1: return currTopVar

    # Xi sits at (u, v) of a p x q grid, and Xi -> Ru and Xi -> Cv. Two true Xi differ in their
    # row or their column, so AMO over the rows and AMO over the columns forbid them.
    p = math.ceil(math.sqrt(m))
    q = math.ceil(m / p)

    varsR = [currTopVar + i + 1 for i in range(p)]
    varsC = [currTopVar + p + j + 1 for j in range(q)]
    currTopVar = currTopVar + p + q

    currTopVar = amoProduct(clauses, varsR, currTopVar) if p > 4 else amoBinomial(clauses, varsR, currTopVar)
    currTopVar = amoProduct(clauses, varsC, currTopVar) if q > 4 else amoBinomial(clauses, varsC, currTopVar)

    for x, var in enumerate(vars):
        clauses.append([-var, varsR[x // q]])
        clauses.append([-var, varsC[x % q]])

    return currTopVar


# Commander Encoding (Klieber & Kwon, 2007), group size 3
# About 3n clauses, about n / 2 auxiliary variables over all recursion levels
COMMANDER_GROUP_SIZE = 3

def amoCommander(clauses, vars, currTopVar):
    m = len(vars)
    if m <= COMMANDER_GROUP_SIZE + 1:
        return amoBinomial(clauses, vars, currTopVar)

    commanders = []
    for start in range(0, m, COMMANDER_GROUP_SIZE):
        group = vars[start:start + COMMANDER_GROUP_SIZE]
        currTopVar += 1
        commander = currTopVar
        commanders.append(commander)

        # At most one variable of the group is true, and a true variable raises its commander.
        amoBinomial(clauses, group, currTopVar)
        for var in group:
            clauses.append([-var, commander])

    # At most one commander is true, so at most one group holds a true variable.
    return amoCommander(clauses, commanders, currTopVar)


def makeExactlyOne(amoFunc):
    """
    Build an Exactly-One encoder from an At-Most-One encoder: one ALO clause plus amoFunc.
    """
    def eoFunc(clauses, vars, currTopVar):
        clauses.append(list(vars))
        return amoFunc(clauses, vars, currTopVar)

    return eoFunc


eoBinomial = makeExactlyOne(amoBinomial)
eoBinary = makeExactlyOne(amoBinary)
eoProduct = makeExactlyOne(amoProduct)
eoCommander = makeExactlyOne(amoCommander)
