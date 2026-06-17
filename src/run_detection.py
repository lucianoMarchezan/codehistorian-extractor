import argparse
from src.config import *
from src.clone_detection.sentence_transformers_detector import evaluate_sentence_transformer


def main():

    parser = argparse.ArgumentParser(
        description="Run clone detection evaluation on function pairs CSV."
    )

    parser.add_argument(
        "--csv",
        type=str,
        required=True,
        help="Path to function pairs CSV file"
    )

    parser.add_argument(
        "--models",
        type=str,
        nargs="+",
        default=["microsoft/codebert-base", "Salesforce/codet5-base"],
        help="List of SentenceTransformer model names"
    )

    args = parser.parse_args()

    csv_file = args.csv

    for model_name in args.models:
        print(f"\nEvaluating model: {model_name} on {csv_file}")

        results = evaluate_sentence_transformer(model_name, csv_file)

        print(results)


if __name__ == "__main__":
    main()