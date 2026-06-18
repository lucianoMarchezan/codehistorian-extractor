import json
import csv
import itertools
from pathlib import Path
from src.config import MIN_LOC, MIN_TOKEN_COUNT


def create_pairs_csv(jsonl_file, output_csv):

    output_dir = Path(output_csv)
    output_dir.mkdir(parents=True, exist_ok=True) 
    
    with open(jsonl_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            entry = json.loads(line)

            entry_id = entry["entry_id"]
            lang = entry["project"]["language"]

            functions = _extract_functions_from_entry(entry)

            # APPLY FILTERING HERE
            functions = _filter_functions(functions)

            if len(functions) < 2:
                continue

            # per-entry output file
            entry_file = output_dir / f"{entry_id}_{lang}_function_pairs.csv"
           
            print(f"Creating file: {entry_file.resolve()}")
            with open(entry_file, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)

                writer.writerow([
                    "function_a_id",
                    "entry_a_id",
                    "code_a",
                    "function_b_id",
                    "entry_b_id",
                    "code_b"
                ])

                for func_a, func_b in _generate_pairs(functions):
                    writer.writerow([
                        func_a["function_id"],
                        func_a["entry_id"],
                        func_a["code"],
                        func_b["function_id"],
                        func_b["entry_id"],
                        func_b["code"]
                    ])

            print(f"Created: {entry_file}")


def _filter_functions(functions):
    """
    Remove low-quality / trivial functions based on metrics.
    """

    filtered = []

    for f in functions:
        metrics = f.get("metrics", {})
        
        loc = metrics.get("loc", 0)
        tokens = metrics.get("token_count", 0)
        

        if loc < MIN_LOC:
            continue

        if tokens < MIN_TOKEN_COUNT:
            continue

        filtered.append(f)

    return filtered

def _extract_functions_from_entry(entry):
    """
    Extract all functions from a project entry.
    """
    functions = []

    entry_id = entry["entry_id"]

    for source in entry.get("sources", []):
        for func in source.get("functions", []):
            functions.append({
                "function_id": func["function_id"],
                "entry_id": entry_id,
                "code": func["code"]["normalized"].replace("\\", "\\\\").replace("\n", "\\n").replace("\t", "\\t"),
                "metrics": func.get("metrics", {})
            })

    return functions


def _generate_pairs(functions):
    """
    Generate all unique unordered pairs of functions.
    """
    return itertools.combinations(functions, 2)



 