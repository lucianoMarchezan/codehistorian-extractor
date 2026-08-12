import json
import pandas as pd
from pathlib import Path
from IPython.display import display, Code


def find_function_metadata(jsonl_file, function_ids):
    """Find metadata for specified function IDs in a JSONL file."""

    function_ids = set(function_ids)
    found = {}

    with open(jsonl_file, "r", encoding="utf-8") as f:

        for line in f:
            if not line.strip():
                continue

            entry = json.loads(line)

            for source in entry.get("sources", []):
                for function in source.get("functions", []):

                    function_id = function.get("function_id")

                    if function_id in function_ids:
                        found[function_id] = {
                            "function_id": function_id,
                            "name": function.get("name"),
                            "qualified_name": function.get("qualified_name"),
                            "class_name": function.get("class_name"),
                            "file_name": source.get("file_name"),
                            "relative_path": source.get("relative_path"),
                            "package": source.get("package"),
                            "start_line": function.get("start_line"),
                            "end_line": function.get("end_line"),
                        }

                    if len(found) == len(function_ids):
                        return found

    return found


def format_code(code):
    """Convert escaped newlines/tabs to actual formatting."""
    if pd.isna(code):
        return ""

    code = str(code)

    # Convert literal escape sequences from CSV/JSON
    code = code.replace("\\n", "\n")
    code = code.replace("\\t", "\t")

    return code.strip()


def show_qualitative_pair(
    project_name,
    sim_range=(0.0, 1.0),
    codebleu_range=(0.0, 1.0),
    select_by="sim",
    model="microsoft/codebert-base-ft",
    language="python",
):
    """
    Find and display a qualitative clone pair satisfying independent
    cosine-similarity and CodeBLEU ranges.

    Parameters
    ----------
    project_name : str
        Project name.

    sim_range : tuple
        Minimum and maximum cosine similarity.

    codebleu_range : tuple
        Minimum and maximum CodeBLEU.

    select_by : str
        Metric used to select the best pair among candidates.
        Either "sim" or "codebleu".

    model : str
        Embedding model.

    language : str
        Programming language.
    """

    if select_by not in {"sim", "codebleu"}:
        raise ValueError("select_by must be either 'sim' or 'codebleu'")

    # Paths

    results_json = (
        Path("../../results")
        / f"{project_name}_detailed_results.json"
    )

    pairs_file = (
        Path("../../output")
        / f"{project_name}_pairs.csv"
    )

    metadata_jsonl = (
        Path("../../output")
        / f"{project_name}.jsonl"
    )

    # Load similarity results

    with open(results_json, "r", encoding="utf-8") as f:
        results = json.load(f)

    results_df = pd.DataFrame(results)

    results_df = results_df[
        (results_df["model"] == model)
        & (results_df["language"] == language)
        & (results_df["sim"] >= sim_range[0])
        & (results_df["sim"] <= sim_range[1])
        & (results_df["codebleu"] >= codebleu_range[0])
        & (results_df["codebleu"] <= codebleu_range[1])
    ].copy()

    if results_df.empty:
        print("No pair satisfies the specified constraints.")
        print()
        print(f"Cosine similarity: {sim_range}")
        print(f"CodeBLEU:          {codebleu_range}")
        return

    # Select best candidate

    selected = results_df.loc[
        results_df[select_by].idxmax()
    ]

    pair_id = selected["pair_id"]

    function_a_id, function_b_id = pair_id.split("::")

    # Load pair CSV

    pairs_df = pd.read_csv(pairs_file)

    pair = pairs_df[
        (pairs_df["function_a_id"] == function_a_id)
        & (pairs_df["function_b_id"] == function_b_id)
    ]

    if pair.empty:
        raise ValueError(
            f"Pair not found in {pairs_file}:\n{pair_id}"
        )

    pair = pair.iloc[0]

    code_a = format_code(pair["code_a"])
    code_b = format_code(pair["code_b"])

    # Metadata

    metadata = find_function_metadata(
        metadata_jsonl,
        [function_a_id, function_b_id]
    )

    # Print overview

    print("=" * 80)
    print("QUALITATIVE EXAMPLE")
    print("=" * 80)

    print(f"Project:            {project_name}")
    print(f"Model:              {model}")
    print(f"Language:           {language}")
    print(f"Cosine similarity:  {selected['sim']:.6f}")
    print(f"CodeBLEU:           {selected['codebleu']:.6f}")

    print()
    print(f"Pair ID: {pair_id}")

    # Functions

    for label, function_id, code in [
        ("FUNCTION A", function_a_id, code_a),
        ("FUNCTION B", function_b_id, code_b),
    ]:

        info = metadata.get(function_id)

        print()
        print("=" * 80)
        print(label)
        print("=" * 80)

        if info is None:
            print("Metadata not found.")
        else:
            print(f"Function:       {info['name']}")
            print(f"Qualified name: {info['qualified_name']}")
            print(f"Class:          {info['class_name']}")
            print(f"File:           {info['file_name']}")
            print(f"Path:           {info['relative_path']}")
            print(f"Package:        {info['package']}")
            print(f"Lines:          {info['start_line']}--{info['end_line']}")

        print()

        display(
            Code(
                code,
                language=language
            )
        )