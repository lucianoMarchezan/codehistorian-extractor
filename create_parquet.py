from pathlib import Path

import ijson
import pandas as pd


# Paths

RESULTS_DIR = Path("results")
PARQUET_FILE = RESULTS_DIR / "results.parquet"


# Generation type

def get_generation_type(prefix):
    """Determine the generation type from the file index."""

    remainder = prefix % 3

    if remainder == 0:
        return "no_llm"

    if remainder == 1:
        return "llm"

    return "agentic"


# Main

def main():

    print("=" * 60)
    print("Creating dataset")
    print("=" * 60)

    print(f"Results directory: {RESULTS_DIR.resolve()}")
    print(f"Parquet file:      {PARQUET_FILE.resolve()}")
    print()

    print("Creating Parquet file...")
    print()

    rows = []

    # Find JSON files

    files = sorted(
        [
            f
            for f in RESULTS_DIR.glob("*_detailed_results.json")
            if f.name.split("_")[0].isdigit()
        ],
        key=lambda f: int(f.name.split("_")[0])
    )

    print(f"Found {len(files)} JSON files")
    print()

    # Process files

    for i, file in enumerate(files, start=1):

        print("-" * 60)

        # File index

        try:
            prefix = int(file.name.split("_")[0])

        except ValueError:
            print(
                f"WARNING: Could not determine index "
                f"from {file.name}"
            )
            continue

        # Project name
        #
        # Example:
        #
        # 0058_django-import-export_django-import-export_
        # 0d4340f02582_detailed_results.json
        #
        # becomes:
        #
        # django-import-export_django-import-export

        project = "_".join(
            file.stem.split("_")[1:-3]
        )

        # Generation type

        generation_type = get_generation_type(prefix)

        print(
            f"[{i}/{len(files)}] "
            f"{file.name}"
        )

        print(f"  index:            {prefix}")
        print(f"  generation type:  {generation_type}")
        print(f"  project:          {project}")

        # Read JSON

        count = 0

        try:

            with open(file, "rb") as f:

                for item in ijson.items(f, "item"):

                    rows.append({
                        "pair_id": item["pair_id"],
                        "file": file.name,
                        "file_index": prefix,
                        "generation_type": generation_type,
                        "project": project,
                        "model": item["model"],
                        "language": item["language"],
                        "sim": item["sim"],
                        "codebleu": item["codebleu"],
                    })

                    count += 1

        except Exception as e:

            print(
                f"ERROR while processing "
                f"{file.name}:"
            )

            print(e)
            raise

        print(f"  rows:             {count}")
        print(f"  total rows:       {len(rows)}")


    # Create DataFrame

    print()
    print("=" * 60)
    print("Creating DataFrame")
    print("=" * 60)

    print(f"Total rows: {len(rows)}")

    df = pd.DataFrame(rows)

    print(f"Shape: {df.shape}")
    print()

    # Safety check

    if df.empty:

        raise RuntimeError(
            "No rows were read from the JSON files. "
            "The Parquet file will not be created."
        )

    print("Data types:")
    print(df.dtypes)


    # Generation type summary

    print()
    print("=" * 60)
    print("Generation types")
    print("=" * 60)

    print(
        df["generation_type"]
        .value_counts()
        .sort_index()
    )


    # Project summary

    print()
    print("=" * 60)
    print("Projects")
    print("=" * 60)

    print(
        f"Number of projects: "
        f"{df['project'].nunique()}"
    )


    # Languages

    print()
    print("=" * 60)
    print("Languages")
    print("=" * 60)

    print(df["language"].value_counts())


    # Write Parquet

    print()
    print("=" * 60)
    print("Writing Parquet")
    print("=" * 60)

    try:

        df.to_parquet(
            PARQUET_FILE,
            index=False
        )

    except Exception as e:

        print("ERROR while writing Parquet:")
        print(e)
        raise

    print(
        f"Saved to: "
        f"{PARQUET_FILE.resolve()}"
    )


    # Final summary

    print()
    print("=" * 60)
    print("FINAL DATASET")
    print("=" * 60)

    print(f"Shape: {df.shape}")
    print()

    print("Generation types:")

    print(
        df["generation_type"]
        .value_counts()
        .sort_index()
    )

    print()
    print("Projects:")

    print(
        f"{df['project'].nunique()}"
    )

    print()
    print("Languages:")

    print(
        df["language"].value_counts()
    )

    print()
    print("First rows:")

    print(df.head())

    print()
    print("=" * 60)
    print("DONE")
    print("=" * 60)


# Entry point

if __name__ == "__main__":
    main()