from src.pipeline import ExtractionPipeline

import argparse

from src.utils import print_banner


def main():
    print_banner()
    parser = argparse.ArgumentParser(
        description="Extract functions from source code projects."
    )

    parser.add_argument(
        "project_path",
        type=str,
        help="Path to the project root directory"
    )

    parser.add_argument(
        "--output",
        type=str,
        default="output/projects.jsonl",
        help="Output JSONL file"
    )

    args = parser.parse_args()

    pipeline = ExtractionPipeline(
        output_file=args.output
    )

    pipeline.run(args.project_path)


if __name__ == "__main__":
    main()