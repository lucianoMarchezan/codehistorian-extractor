from pathlib import Path
import pandas as pd
import ijson


# Paths
RESULTS_DIR = Path("../../results")
PARQUET_FILE = RESULTS_DIR / "results.parquet"


def get_generation_type(prefix):
    """Determine the generation type from the file index."""
    if prefix >= 68:
        return "llm"
    elif prefix % 2 == 0:
        return "no_llm"
    else:
        return "agentic"


def main():

    print("=" * 60)
    print("Creating dataset")
    print("=" * 60)

    print(f"Results directory: {RESULTS_DIR.resolve()}")
    print(f"Parquet file:      {PARQUET_FILE.resolve()}")
    print()

    # Load existing Parquet
    if PARQUET_FILE.exists():

        print(f"Loading existing {PARQUET_FILE.name}...")

        try:
            df = pd.read_parquet(PARQUET_FILE)
        except Exception as e:
            print(f"ERROR while loading Parquet:")
            print(e)
            raise

        print("Parquet loaded successfully.")
        print()

    # Create Parquet from JSON files
    else:

        print("Creating Parquet file...")
        print()

        rows = []

        files = sorted(
            RESULTS_DIR.glob("*_detailed_results.json"),
            key=lambda f: int(f.name.split("_")[0])
        )

        print(f"Found {len(files)} JSON files")
        print()

        for i, file in enumerate(files, start=1):

            print("-" * 60)

            try:
                prefix = int(file.name.split("_")[0])
            except ValueError:
                print(f"WARNING: Could not determine index from {file.name}")
                continue

            project = "_".join(file.stem.split("_")[1:-2])

            generation_type = get_generation_type(prefix)

            print(
                f"[{i}/{len(files)}] "
                f"{file.name}"
            )
            print(f"  index:            {prefix}")
            print(f"  generation type:  {generation_type}")
            print(f"  project:          {project}")

            count = 0

            try:

                with open(file, "rb") as f:

                    for item in ijson.items(f, "item"):

                        rows.append({
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
                print(f"ERROR while processing {file.name}:")
                print(e)
                raise

            print(f"  rows:             {count}")
            print(f"  total rows:       {len(rows)}")

        print()
        print("=" * 60)
        print("Creating DataFrame")
        print("=" * 60)

        print(f"Total rows: {len(rows)}")

        df = pd.DataFrame(rows)

        print(f"Shape: {df.shape}")
        print()
        print("Data types:")
        print(df.dtypes)

        print()
        print("=" * 60)
        print("Generation types")
        print("=" * 60)

        print(df["generation_type"].value_counts())

        print()
        print("=" * 60)
        print("Writing Parquet")
        print("=" * 60)

        try:
            df.to_parquet(PARQUET_FILE, index=False)
        except Exception as e:
            print("ERROR while writing Parquet:")
            print(e)
            raise

        print(f"Saved to: {PARQUET_FILE.resolve()}")

    # Final summary
    print()
    print("=" * 60)
    print("FINAL DATASET")
    print("=" * 60)

    print(f"Shape: {df.shape}")
    print()

    print("Generation types:")
    print(df["generation_type"].value_counts())

    print()
    print("Projects:")
    print(df["project"].nunique())

    print()
    print("Languages:")
    print(df["language"].value_counts())

    print()
    print("First rows:")
    print(df.head())

    print()
    print("=" * 60)
    print("DONE")
    print("=" * 60)


if __name__ == "__main__":
    main()