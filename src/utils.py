from pathlib import Path
import hashlib
import uuid


SUPPORTED_EXTENSIONS = {
    ".py": "python",
    ".java": "java",
    ".cs": "csharp"
}


IGNORED_DIRECTORIES = {
    ".git",
    "venv",
    "__pycache__",
    "node_modules",
    "bin",
    "obj",
    "target"
}


def detect_language(project_root: Path) -> str:
    counts = {}

    for ext, lang in SUPPORTED_EXTENSIONS.items():
        counts[lang] = len(list(project_root.rglob(f"*{ext}")))

    return max(counts, key=counts.get)


def iter_source_files(project_root: Path, language: str):

    language_to_extension = {
        "python": ".py",
        "java": ".java",
        "csharp": ".cs"
    }

    extension = language_to_extension[language]

    for path in project_root.rglob(f"*{extension}"):

        if any(part in IGNORED_DIRECTORIES for part in path.parts):
            continue

        yield path


def sha256(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()


def stable_id(value: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, value))

def print_banner():

    banner = r"""
========================================================
   CODE HISTORIAN FUNCTION EXTRACTOR
========================================================

  Multi-language Dataset Extraction Pipeline
  Supported Languages:
    - Python
    - Java
    - C#

========================================================
"""

    print(banner)