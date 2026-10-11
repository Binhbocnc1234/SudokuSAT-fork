import csv
import os

from solver import solveSudoku
from core.generateSudokuProblem import generate_random_sudoku as gen
from core.sudokuBuilder import getAvailableEncoders, getEncoderByID

GRID_SAMPLES = {9, 16, 25, 36}
CSV_FILENAME = "benchmark_result.csv"

def exportResult(results, filename=CSV_FILENAME):
    fileExists = os.path.isfile(filename)

    headers = [
        "Grid Size", "Encoder", "Total Variables", "Auxiliary Variables", "Clauses", 
        "Status", "Avg Encoding Time (ms)", "Avg Solving Time (ms)", "Avg Total Time (ms)"
    ]

    with open(filename, mode="a", newline="", encoding="utf-8") as csvFile:
        writer = csv.DictWriter(csvFile, fieldnames=headers)
    
        if not fileExists: writer.writeheader()

        for res in results:
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

def simulation(encoderFunc, encoderName, gridSize, iterations):
    print(f"\n[+] Running simulation {iterations} times | Encoder: {encoderName}")

    totalEncTime = 0.0
    totalSolverTime = 0.0
    sampleStats = None
    
    totalRuns = iterations

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
        "avgEncodingTime": totalEncTime / totalRuns,
        "avgSolvingTime": totalSolverTime / totalRuns,
        "avgTotalTime": (totalEncTime + totalSolverTime) / totalRuns
    }

    return avgStats


if __name__ == "__main__":
    # ---INPUTS---

    # GRID SIZE
    try:
        gridSize = int(input("\n[?] Input grid size (9, 16, 25, 36): "))
    except ValueError:
        gridSize = 9
        print("  -> Invalid input, defaulting to 9.")

    if gridSize not in GRID_SAMPLES:
        print(f"  -> Invalid input, defaulting to 9.")
        gridSize = 9

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

    # SIM AMOUNT
    try:
        numSimulation = int(input("\n[?] Input simulation amount: "))
    except ValueError:
        print("  -> Invalid amount, defaulting to 100 tries.")
        numSimulation = 100


    # ---RUNNING SIM---
    print("\n" + "="*40)
    print("         RUNNING SIMULATION          ")
    print("="*40)

    results = []
    for enc in encSelected:
        res = simulation(
            encoderFunc=enc["func"],
            encoderName=enc["name"],
            gridSize=gridSize,
            iterations=numSimulation
        )
        if res:
            results.append(res)

    # --- RESULT---
    print("\n" + "="*50)
    print("               RESULTS                      ")
    print("="*50)
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

        print("-" * 50)

    # --- EXPORT ---
    print("EXPORTING RESULT TO CSV...")
    exportResult(results)