from src.extractor_pipeline import ExtractionPipeline
from src.utils.create_function_pairs import create_pairs_csv
import argparse
from src.utils.helper_functions import print_banner
from src.config import *


def main():

    print_banner()

    parser = argparse.ArgumentParser(
        description="Extract functions and generate function pairs."
    )

    parser.add_argument(
        "project_path",
        type=str,
        help="Path to the project root directory"
    )

    parser.add_argument(
        "--output",
        type=str,
        default=DEFAULT_OUTPUT_JSONL,
        help="Output JSONL file"
    )

    parser.add_argument(
        "--pairs-output",
        type=str,
        default="output/",
        help="Output CSV containing function pairs"
    )

    parser.add_argument(
        "--entry-id",
        type=str,
        default=None,
        help="Process only a specific entry_id"
    )

    parser.add_argument(
        "--mode",
        choices=["extract", "pairs", "all"],
        default=DEFAULT_MODE,
        help="Pipeline execution mode"
    )

    args = parser.parse_args()

    if args.mode in ("extract", "all"):
        extractor_pipeline = ExtractionPipeline(
            output_file=args.output
        )
        extractor_pipeline.run(args.project_path)

    if args.mode in ("pairs", "all"):
        create_pairs_csv(
            jsonl_file=args.output,
            output_csv=args.pairs_output,
            entry_id=args.entry_id
        )


if __name__ == "__main__":
    main()