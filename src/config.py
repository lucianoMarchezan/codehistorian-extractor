import torch
DEFAULT_OUTPUT_JSONL = "output/projects.jsonl" 
RESULTS_DIR = "results/"

DEFAULT_MODE = "all"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MODELS_PATH = "models/"
