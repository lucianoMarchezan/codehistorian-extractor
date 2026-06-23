import json
import csv
import itertools
from pathlib import Path
import faiss
import torch
import numpy as np
from src.embeddings.embeddings_calc import embed_functions, build_index
from src.embeddings import get_tokenizer, get_model
from src.config import *


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
                print(f"Computing embeddings for {len(functions)} functions...")
                stream = embed_functions(functions)
                index = build_index(stream)
                for func_a, func_b in _generate_candidate_pairs(
                    functions,
                    index,
                    k=K_NEAREST
                ):
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

        if _is_getter(f):
            continue

        if _is_setter(f):
            continue

        if is_main_function(f):
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



def _generate_candidate_pairs(functions, index, k=K_NEAREST):

    print(f"Generating candidate pairs for {len(functions)} functions using FAISS...")

    tokenizer = get_tokenizer()
    model = get_model()

    id_map = {int(f["function_id"]): f for f in functions}

    for f in enumerate(functions):

        inputs = tokenizer(
            f["code"],
            return_tensors="pt",
            truncation=True,
            max_length=512
        ).to(model.device)

        with torch.inference_mode():
            outputs = model(**inputs)

        emb = outputs.last_hidden_state[:, 0, :].cpu().numpy().astype("float32")
        faiss.normalize_L2(emb.reshape(1, -1))

        scores, neighbors = index.search(
            emb.reshape(1, -1),
            k + 1
        )

        for j in neighbors[0][1:]:
            func_b = id_map.get(int(j))
            if func_b is None:
                continue

            yield f, func_b



def _is_getter(func):
    return (
        func["name"].startswith(("get", "is"))
        and func["metrics"]["loc"] <= 2
    )

def _is_setter(func):
    return (
        func["name"].startswith("set")
        and func["metrics"]["loc"] <= 2
    )

def is_main_function(func):
    return func["name"].lower() == "main"