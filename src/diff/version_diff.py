# python version_diff.py version1.jsonl version2.jsonl version_diff.jsonl
import json
import sys
from pathlib import Path


def load_project(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    if len(lines) != 1:
        raise ValueError(
            f"Expected exactly one JSONL entry in {path}, "
            f"found {len(lines)}"
        )

    return json.loads(lines[0])


def function_key(source_file, function, language):

    relative_path = source_file["relative_path"]

    parameter_count = len(
        function.get("parameters", [])
    )

    if language == "java":
        name = (
            function.get("qualified_name")
            or function["name"]
        )
    else:
        name = function["name"]

    return (
        relative_path,
        name,
        parameter_count,
    )


def collect_functions(project):

    language = project["project"]["language"]

    functions = {}

    for source_file in project.get("sources", []):

        for function in source_file.get("functions", []):

            key = function_key(
                source_file,
                function,
                language
            )

            functions[key] = (
                source_file,
                function
            )

    return functions


def create_diff(project_v1, project_v2):

    functions_v1 = collect_functions(
        project_v1
    )

    functions_v2 = collect_functions(
        project_v2
    )

    added_keys = (
        set(functions_v2)
        - set(functions_v1)
    )

    diff_project = {
        "entry_id": project_v2["entry_id"],
        "project": project_v2["project"],
        "sources": []
    }

    sources_by_path = {}

    for key in added_keys:

        source_file, function = functions_v2[key]

        path = source_file["relative_path"]

        if path not in sources_by_path:

            new_source_file = {
                key: value
                for key, value in source_file.items()
                if key != "functions"
            }

            new_source_file["functions"] = []

            sources_by_path[path] = new_source_file

            diff_project["sources"].append(
                new_source_file
            )

        sources_by_path[path]["functions"].append(
            function
        )

    return diff_project


def count_functions(project):

    return sum(
        len(source_file.get("functions", []))
        for source_file in project.get("sources", [])
    )


def write_project(project, output_file):

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            json.dumps(
                project,
                ensure_ascii=False
            )
        )

        f.write("\n")


def main():

    if len(sys.argv) != 4:

        print(
            "Usage: python version_diff.py "
            "<version1.jsonl> "
            "<version2.jsonl> "
            "<diff.jsonl>"
        )

        sys.exit(1)

    version1_file = Path(sys.argv[1])
    version2_file = Path(sys.argv[2])
    output_file = Path(sys.argv[3])

    print(f"Version 1: {version1_file}")
    print(f"Version 2: {version2_file}")
    print()

    project_v1 = load_project(
        version1_file
    )

    project_v2 = load_project(
        version2_file
    )

    print(
        f"Project: "
        f"{project_v2['project']['name']}"
    )

    print(
        f"Language: "
        f"{project_v2['project']['language']}"
    )

    functions_v1 = collect_functions(
        project_v1
    )

    functions_v2 = collect_functions(
        project_v2
    )

    print(
        f"Functions in V1: "
        f"{len(functions_v1)}"
    )

    print(
        f"Functions in V2: "
        f"{len(functions_v2)}"
    )

    diff_project = create_diff(
        project_v1,
        project_v2
    )

    added = count_functions(
        diff_project
    )

    print(
        f"Added functions: {added}"
    )

    write_project(
        diff_project,
        output_file
    )

    print()
    print(f"Output: {output_file}")


if __name__ == "__main__":
    main()
