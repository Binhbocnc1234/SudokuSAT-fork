import csv
import os

from solver import solveSudoku
from core.generateSudokuProblem import generate_random_sudoku as gen

from core.sudokuBuilder import getAvailableEncoders, getEncoderByID
from core.misc.solverCPSAT import solveSudokuCPSAT
from core.misc.solverGurobi import solveSudokuGurobi


GRID_SAMPLES = {9, 16, 25, 36}

# EXPORT
def exportResult(results, mode=2, filename="benchmark_result.csv"):
    fileExists = os.path.isfile(filename)

    if mode == 1:
        headers = [
            "Grid Size", "Method", "Status", 
            "Avg Solving Time (ms)", "Avg Total Time (ms)"
        ]
    
    else: 
        headers = [
            "Grid Size", "Encoder", "Total Variables", "Auxiliary Variables", "Clauses", 
            "Status", "Avg Encoding Time (ms)", "Avg Solving Time (ms)", "Avg Total Time (ms)"
        ]

    with open(filename, mode="a", newline="", encoding="utf-8") as csvFile:
        writer = csv.DictWriter(csvFile, fieldnames=headers)
    
        if not fileExists: writer.writeheader()

        for res in results:
            if mode == 1:
                writer.writerow({
                    "Grid Size": res.get("gridSize"),
                    "Method": res.get("method"),
                    "Status": res.get("status"),
                    "Avg Total Time (ms)": f"{res.get('avgTotalTime', 0):.4f}" if res.get("status") != "TIMEOUT" else "N/A"
                })
                
            else:
                writer.writerow({
                    "Grid Size": res.get("gridSize"),
                    "Encoder": res.get("encoder"),
                    "Total Variables": res.get("totalVar"),
                    "Auxiliary Variables": res.get("auxVar"),
                    "Clauses": res.get("numClauses"),
                    "Status": res.get("status"),
                    "Avg Encoding Time (ms)": f"{res.get('avgEncodingTime', 0):.4f}" if res.get("status") != "TIMEOUT" else "N/A",
                    "Avg Solving Time (ms)": f"{res.get('avgSolvingTime', 0):.4f}" if res.get("status") != "TIMEOUT" else "N/A",
                    "Avg Total Time (ms)": f"{res.get('avgTotalTime', 0):.4f}" if res.get("status") != "TIMEOUT" else "N/A"
                })

    print(f"Results successfully exported to '{filename}'")

# MODE 1: PARADIGM SIMULATION
def simulationParadigm(gridSize, iterations):
    print(f"\n[+] Mode 1: Running Multi-Paradigm Simulation ({iterations} times)")
    

    print("\n" + "="*40)
    print("         RUNNING SIMULATION          ")
    print("="*40)

    productEnc = getEncoderByID([3])[0] # ID 0: Pairwise/Binomial
    
    methods = [
        {"name": "PySAT", "type": "SAT", "func": lambda g: solveSudoku(g, productEnc["func"])},
        {"name": "Google OR-Tools CP-SAT", "type": "CP", "func": lambda g: solveSudokuCPSAT(g)},
        {"name": "Gurobi", "type": "ILP", "func": lambda g: solveSudokuGurobi(g)}
    ]

    paradigmResults = []

    for m in methods:
        print(f" -> Testing Paradigm: {m['name']}...")
        totalSolvingTime = 0.0
        totalOverallTime = 0.0
        isTimeout = False

        for _ in range(iterations):
            currGrid = gen(gridSize)
            res = m["func"](currGrid)

            if not res or res.get("status") == "TIMEOUT":
                isTimeout = True
                break

            if m["type"] == "SAT":
                solveTime = res["solverTime"] * 1000.0
                totalTime = (res["encTime"] + res["solverTime"]) * 1000.0
            else:
                solveTime = res.get("solvingTime", 0.0)
                totalTime = res.get("solvingTime", 0.0)

            totalSolvingTime += solveTime
            totalOverallTime += totalTime

        if isTimeout:
            paradigmResults.append({
                "gridSize": f"{gridSize}x{gridSize}",
                "method": m["name"],
                "status": "TIMEOUT"
            })
        else:
            paradigmResults.append({
                "gridSize": f"{gridSize}x{gridSize}",
                "method": m["name"],
                "status": "COMPLETED",
                "avgTotalTime": totalOverallTime / iterations
            })

    return paradigmResults

# MODE 2: PySAT ENCODER
def simulationSATEncoder(encoderFunc, encoderName, gridSize, iterations):
    print(f"\n[+] Mode 2: Running PySAT Encoder Simulation {iterations} times | Encoder: {encoderName}")

    totalEncTime = 0.0
    totalSolverTime = 0.0
    sampleStats = None

    totalRun = iterations

    while iterations > 0:
        iterations -= 1

        currGrid = gen(gridSize)

        stats = solveSudoku(currGrid, encoderFunc)

        if not stats: return None

        if stats.get("status") == "TIMEOUT":
            print("Encoder TIMEOUT.")

            return {
                "encoder": encoderName,
                "gridSize": stats["gridSize"],
                "totalVar": stats["totalVar"],
                "auxVar": stats["auxVar"],
                "numClauses": stats["numClauses"],
                "status": "TIMEOUT"
            }

        totalEncTime += stats["encTime"]
        totalSolverTime += stats["solverTime"]
        sampleStats = stats

    avgStats = {
        "encoder": encoderName,
        "gridSize": sampleStats["gridSize"],
        "totalVar": sampleStats["totalVar"],
        "auxVar": sampleStats["auxVar"],
        "numClauses": sampleStats["numClauses"],
        "status": "COMPLETED",
        "avgEncodingTime": totalEncTime / totalRun,
        "avgSolvingTime": totalSolverTime / totalRun,
        "avgTotalTime": (totalEncTime + totalSolverTime) / totalRun
    }

    return avgStats


if __name__ == "__main__":
    # --- INPUTS ---
    print("=" * 40)
    print("      INPUT STARTS      ")
    print("=" * 40)

    # MODE SELECTION
    print("Select Mode:")
    print("  [1] Mode 1: Multi-Paradigm Comparison (PySAT / CP-SAT / Gurobi / CPlex)")
    print("  [2] Mode 2: PySAT Encoders Comparison (Default)")

    try:
        mode = int(input("\n[?] Select mode (default=2): ").strip())
    except ValueError:
        mode = 2

    if mode not in (1, 2):
        mode = 2

    if mode == 1: print(f"\n>>> MODE 1: MULTI-PARADIGM COMPARISON <<<")
    else: print(f"\n>>> MODE 2: PYSAT ENCODER COMPARISON <<<")
    # GRID SIZE
    try:
        gridSize = int(input("\n[?] Input grid size (9, 16, 25, 36): "))
    except ValueError:
        gridSize = 9
        print("  -> Invalid input, defaulting to 9.")

    if gridSize not in GRID_SAMPLES:
        print(f"  -> Invalid input, defaulting to 9.")
        gridSize = 9

    # SIM AMOUNT
    try:
        numSimulation = int(input("\n[?] Input simulation amount: "))
    except ValueError:
        print("  -> Invalid amount, defaulting to 50 tries.")
        numSimulation = 50

    # --- RUNNING SIM (MODE 1) ---
    if mode == 1:
        results = simulationParadigm(gridSize, numSimulation)

        print("\n" + "="*40)
        print("               RESULTS                      ")
        print("="*40)
        print(f" Grid Size            : {results[0]['gridSize']}")
        for res in results:
            print(f" - Method          : {res['method']}")
            if res.get("status") == "TIMEOUT":
                print(f"   + Status           : TIMEOUT")
            else:
                print(f"   + Status           : COMPLETED")
                print(f"   + Avg Total Time   : {res['avgTotalTime']:.4f} ms")
            print("-" * 60)

        exportResult(results, mode=1, filename="benchmark_paradigms_result.csv")


    # --- RUNNING SIM (MODE 2) --- 
    else:

        # ENCODER
        encoders = getAvailableEncoders()
        print("\nList of available encoders:")

        for enc in encoders:
            print(f"   [{enc['id']}] {enc['name']}")
        
        print("   [-1] ALL (default)")

        raw = input("\n[?] Input encoder IDs (e.g. '0, 2, 4' or '-1' for all): ").strip()

        selectedID = []
        if raw:
           parts = raw.replace(",", " ").split()

           for p in parts:
                try:
                    selectedID.append(int(p))
                except ValueError:
                    pass

        
        if not selectedID: selectedID = [-1] # default

        encSelected = getEncoderByID(selectedID)

        print("\n" + "="*40)
        print("         RUNNING SIMULATION          ")
        print("="*40)
        
        results = []
        for enc in encSelected:
            res = simulationSATEncoder(
                encoderFunc=enc["func"],
                encoderName=enc["name"],
                gridSize=gridSize,
                iterations=numSimulation
            )
            if res:
                results.append(res)

        # --- RESULT---
        print("\n" + "="*40)
        print("               RESULTS                      ")
        print("="*40)
        print(f" Grid Size            : {res['gridSize']}")

        for res in results:
            print(f" - Encoder            : {res['encoder']}")
            print(f"   + Variable amount  : {res['totalVar']} (Aux: {res['auxVar']})")
            print(f"   + Clause amount    : {res['numClauses']}")
        
            if res.get("status") == "TIMEOUT":
                print(f"   + Status           : TIMEOUT")

            else:
                print(f"   + Avg encoding time: {res['avgEncodingTime'] * 1000:.4f} ms")
                print(f"   + Avg solving time : {res['avgSolvingTime'] * 1000:.4f} ms")
                print(f"   + Avg total time   : {res['avgTotalTime'] * 1000:.4f} ms")

            print("-" * 40)

        # --- EXPORT ---
        print("EXPORTING RESULT TO CSV...")
        exportResult(results)

    
    