from functools import partial
from pysat.card import EncType

from core.encoderCustom import eoBinomial, eoBinary, eoProduct, eoCommander
from core.encoderPySATDefault import eoDefault

from core.generateSudokuClauses import generateSudokuClauses

# Pairwise, Binary, Product and Commander are implemented in core/encoderCustom.py.
# Sequential Counter and Ladder come from pysat.card.CardEnc.
ENCODER_FACTORY = {
    0: {
        "id": 0,
        "name": "Pairwise",
        "func": lambda grid: generateSudokuClauses(grid, eoBinomial)
    },

    1: {
        "id": 1,
        "name": "Binary",
        "func": lambda grid: generateSudokuClauses(grid, eoBinary)
    },

    2: {
        "id": 2,
        "name": "Sequential",
        "func": lambda grid: generateSudokuClauses(grid, partial(eoDefault, encType=EncType.seqcounter))
    },

    3: {
        "id": 3,
        "name": "Product",
        "func": lambda grid: generateSudokuClauses(grid, eoProduct)
    },

    4: {
        "id": 4,
        "name": "Commander",
        "func": lambda grid: generateSudokuClauses(grid, eoCommander)
    },

    5: {
        "id": 5,
        "name": "Ladder",
        "func": lambda grid: generateSudokuClauses(grid, partial(eoDefault, encType=EncType.ladder))
    }
}

def getAvailableEncoders():
    return list(ENCODER_FACTORY.values())

def getEncoderByName(name):
    for enc in ENCODER_FACTORY.values():
        if enc["name"] == name:
            return enc

    raise KeyError(f"Unknown encoder '{name}'. Available: {[e['name'] for e in ENCODER_FACTORY.values()]}")
