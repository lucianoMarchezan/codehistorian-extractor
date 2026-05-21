# Function Extractor Pipeline

A multi-language source code extraction pipeline for building standardized datasets of functions/methods from software repositories.

The pipeline recursively scans projects, extracts functions using AST-based parsing, and serializes the extracted data into a structured JSONL dataset suitable for:

- clone detection
- semantic similarity analysis
- embedding generation
- ML datasets
- code search
- repository mining

Currently supported languages:

- Python
- Java * 
- C#  

---

# Features

- Recursive project traversal
- Multi-language support
- AST-based extraction
- Hierarchical dataset structure
- JSONL serialization
- Stable deterministic IDs
- Function metadata extraction
- Code hashing
- Extensible architecture

---

# Dataset Structure

Each line in the JSONL output represents a single project.

Structure:

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

## Project Structure
```
src/
│
├── main.py
├── pipeline.py
├── utils.py
├── models.py
│
├── parsers/
│   ├── base.py
│   └── python_parser.py
│
├── normalization/
│   └── serializer.py
│
└── output/
```
## Running 
From the root folder: 
```python -m src.main /repos/django --output output/projects.jsonl```
