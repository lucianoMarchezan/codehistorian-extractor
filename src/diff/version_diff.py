# python version_diff.py version1.jsonl version2.jsonl version_diff.jsonl
import json
import sys
from pathlib import Path


def load_projects(path):
    projects = {}

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            project = json.loads(line)
            projects[project["entry_id"]] = project

    return projects


def function_key(source_file, function, language):
    relative_path = source_file["relative_path"]
    parameters = function.get("parameters", [])
    parameter_count = len(parameters)

    if language == "java":
        name = function.get("qualified_name") or function["name"]
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

            functions[key] = (source_file, function)

    return functions


def create_diff(project_v1, project_v2):
    functions_v1 = collect_functions(project_v1)
    functions_v2 = collect_functions(project_v2)

    added_keys = set(functions_v2) - set(functions_v1)

    diff_project = {
        "entry_id": project_v2["entry_id"],
        "project": project_v2["project"],
        "sources": []
    }

    sources_by_path = {}

    for source_file, function in functions_v2.values():

        key = function_key(
            source_file,
            function,
            project_v2["project"]["language"]
        )

        if key not in added_keys:
            continue

        path = source_file["relative_path"]

        if path not in sources_by_path:
            new_source_file = {
                key: value
                for key, value in source_file.items()
                if key != "functions"
            }

            new_source_file["functions"] = []

            sources_by_path[path] = new_source_file
            diff_project["sources"].append(new_source_file)

        sources_by_path[path]["functions"].append(function)

    return diff_project


def write_project(project, output_file):
    with open(output_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(project, ensure_ascii=False))
        f.write("\n")


def main():

    if len(sys.argv) != 4:
        print(
            "Usage: python version_diff.py "
            "<version1.jsonl> <version2.jsonl> <diff.jsonl>"
        )
        sys.exit(1)

    version1_file = Path(sys.argv[1])
    version2_file = Path(sys.argv[2])
    output_file = Path(sys.argv[3])

    projects_v1 = load_projects(version1_file)
    projects_v2 = load_projects(version2_file)

    print(f"Version 1 projects: {len(projects_v1)}")
    print(f"Version 2 projects: {len(projects_v2)}")

    output_file.unlink(missing_ok=True)

    total_added = 0
    total_projects = 0

    for project_id, project_v2 in projects_v2.items():

        project_v1 = projects_v1.get(project_id)

        if project_v1 is None:
            print(
                f"{project_id}: not present in version 1, "
                "all functions considered added"
            )

            diff_project = project_v2
        else:
            diff_project = create_diff(
                project_v1,
                project_v2
            )

        added = sum(
            len(source_file.get("functions", []))
            for source_file in diff_project.get("sources", [])
        )

        if added == 0:
            print(f"{project_id}: 0 added functions")
            continue

        print(f"{project_id}: {added} added functions")

        write_project(
            diff_project,
            output_file
        )

        total_added += added
        total_projects += 1

    print()
    print(f"Projects with additions: {total_projects}")
    print(f"Total added functions: {total_added}")
    print(f"Output: {output_file}")


if __name__ == "__main__":
    main()
