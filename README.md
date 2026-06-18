# Function Extractor & Clone Detection Pipeline

A multi-language source code analysis pipeline for extracting functions from software repositories and building datasets for clone detection, semantic similarity analysis, and code representation learning.

The system performs end-to-end processing:

1. Extracts functions from source code using AST-based parsers  
2. Serializes structured project data into JSONL  
3. Generates function-pair datasets per project  
4. Evaluates clone similarity using SentenceTransformer models  

--- 

## Supported Languages

- Python
- Java *
- C#

---


## Dataset Structure (JSONL)

Each line corresponds to one project.

```json
{
  "entry_id": "proj_000001",
  "project": {
    "name": "django",
    "language": "python",
    "repository_url": "https://github.com/django/django"
  },
  "sources": [
    {
      "source_id": "src_000001",
      "file_name": "request.py",
      "relative_path": "django/http/request.py",
      "package": "django.http",
      "functions": [
        {
          "function_id": "fn_000001",
          "name": "get_host",
          "qualified_name": "django.http.request.HttpRequest.get_host",
          "signature": "get_host(self)",
          "start_line": 120,
          "end_line": 148,
          "code": {
            "raw": "...",
            "normalized": "..."
          }
        }
      ]
    }
  ]
}
```

---

## Project Structure

```
src/
│
├── main.py                      # Extraction pipeline entry point
├── pipeline.py                 # Core extraction logic
├── models.py                   # Data structures
├── run_detection.py                   # Detection entry point
│
├── utils/
│   ├── helper_functions.py
│   ├── create_function_pairs.py
│
├── parsers/
│   ├── base.py
│   ├── python_parser.py
│
├── normalization/
│   └── serializer.py
│
├── clone_detection/
│   └── sentence_transformers_detector.py
│
output/
results/
```
---

## Language Detection

The pipeline automatically detects the dominant language in a repository using file counts.

Supported extensions:

- .py → Python  
- .java → Java  
- .cs → C#  

--- 

## Running the Pipeline

The extractor/pair creation is done via a single entry point (`src.main`) and supports three execution modes:

- `extract` → only function extraction (JSONL)
- `pairs` → only pair generation (CSV)
- `all` → run full pipeline (extract + pairs)

---

## Running Examples

### 1. Full pipeline (recommended)

Extract + generate pairs:

```bash
python -m src.main tests/calc-test --mode all
```

---

### 2. Only extraction

```bash
python -m src.main tests/calc-test --mode extract
```

Output:
- JSONL dataset in `--output`

---

### 3. Only pair generation

```bash
python -m src.main tests/calc-test --mode pairs
```

Input:
- existing JSONL file (`--output`)

Output:
- function pairs CSV files

---

### 4. Clone Detection Evaluation

This can be run after the pairs files are created

Run embedding-based similarity analysis from the root folder:

```bash
python -m src.run_detection --csv output/calc-test_python_function_pairs.csv
```

Multiple models:

```bash
python -m src.run_detection --csv output/calc-test_python_function_pairs.csv --models microsoft/codebert-base Salesforce/codet5-base
```

# Requirements

* Run `pip install -r requirements.txt` to install required packages -- depending on your Python kernel additional packages may need to be installed
* [MS C++ build tools](https://visualstudio.microsoft.com/pt-br/visual-cpp-build-tools/) -- make sure to install Desktop development with C++ (include Win 10/11 SDK and C++ CMake tools for Windows) -- this is **required by Codebleu**