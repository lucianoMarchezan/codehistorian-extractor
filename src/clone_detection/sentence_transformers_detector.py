from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim  
import torch, json
from pathlib import Path    
from src.utils.transformer_test_loader import get_loader
from codebleu import calc_codebleu
from src.config import * 


def evaluate_sentence_transformer(model_name, csv_file):

    folder_name = model_name.split("/")[-1]
    model_dir = Path(MODELS_PATH) / folder_name

    # Load model
    if not model_dir.exists() or not _model_is_valid(model_dir):
        print(f"Model directory {model_dir} does not exist or is invalid.")
        return

    model = SentenceTransformer(str(model_dir), device=DEVICE)

    # Load CSV pairs
    loader = get_loader(csv_path=csv_file)

    # Evaluate
    filename = Path(csv_file).name
    dataset_name = filename.replace("_function_pairs.csv", "") 
    parts = dataset_name.split("_")
    language = parts[1] if len(parts) > 1 else "unknown"
    print(f"Starting evaluation for {model_name} on {dataset_name}")
    detailed_entries = _evaluate_model(model, loader, language=language)
    # Save results
    _save_individual_results(
        entries=detailed_entries,
        dataset=dataset_name,
        model=model_name, 
        language=language,
        file_name=f"{dataset_name}_detailed_results.json"
    )

    print(f"Evaluation completed for model: {model_name}")


def _evaluate_model(model, loader, language="unknown"):

    detailed_entries = []

    total_batches = len(loader)

    with torch.no_grad():
        for batch_idx, (texts_a, texts_b, pair_ids) in enumerate(loader, start=1):

            emb1 = model.encode(texts_a, convert_to_tensor=True)
            emb2 = model.encode(texts_b, convert_to_tensor=True)

            sims = cos_sim(emb1, emb2).diagonal()

            for i in range(len(pair_ids)):

                codebleu_score = _compute_codebleu(
                    texts_a[i],
                    texts_b[i],
                    language
                )

                detailed_entries.append({
                    "pair_id": f"{pair_ids[i][0]}::{pair_ids[i][1]}",
                    "sim": sims[i].item(),
                    "codebleu": codebleu_score
                })

            progress = int(100 * batch_idx / total_batches)
            if progress % 5 == 0 or batch_idx == total_batches:
                print(
                    f"Evaluation progress: {batch_idx}/{total_batches} "
                    f"batches ({progress}%)"
                )

    return detailed_entries


def _model_is_valid(model_dir: Path) -> bool:
    """Check if SentenceTransformer model folder has all necessary files."""
    required_files = ["config.json", "modules.json", "tokenizer_config.json"]
    return all((model_dir / f).exists() for f in required_files)
 



def _save_individual_results(entries: list, model: str, dataset: str, language: str, file_name: str):

    output_dir = Path(RESULTS_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / file_name

    new_results = [
        {
            "model": model,
            "dataset": dataset, 
            "language": language,
            "pair_id": e["pair_id"],
            "sim": e["sim"],
            "codebleu": e["codebleu"]
        }
        for e in entries
    ]

    if json_path.exists():
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
            if not isinstance(existing, list):
                existing = []
        except json.JSONDecodeError:
            existing = []
    else:
        existing = []

    existing.extend(new_results)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=4, ensure_ascii=False)

    print(f"Detailed results saved to: {json_path}")


def _compute_codebleu(code_a: str, code_b: str, language: str) -> float:
    """
    Compute CodeBLEU between two functions.
    """

    try:
        score = calc_codebleu([code_a], [code_b], lang=language)
        return score["codebleu"]

    except Exception as e:
        print(f"CodeBLEU failed ({language}): {e}")
        return None