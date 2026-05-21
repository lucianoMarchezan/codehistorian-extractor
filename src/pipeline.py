from pathlib import Path

from src.models import (
    ProjectEntry,
    ProjectMetadata
)

from src.normalization.serializer import JSONLSerializer

from src.parsers.python_parser import PythonParser

from src.utils import (
    detect_language,
    iter_source_files,
    stable_id
)


class ExtractionPipeline:

    def __init__(self, output_file):

        self.serializer = JSONLSerializer(output_file)

    def run(self, project_root: str):

        project_root = Path(project_root)

        language = detect_language(project_root)

        parser = self._get_parser(language)

        project = ProjectEntry(
            entry_id=project_root.name,

            project=ProjectMetadata(
                name=project_root.name,
                language=language,
                repository_url=""
            )
        )

        for file_path in iter_source_files(project_root, language):

            try:
                source_file = parser.extract(
                    file_path,
                    project_root
                )

                if source_file.functions:
                    project.sources.append(source_file)

            except Exception as e:
                print(f"Failed parsing {file_path}: {e}")

        self.serializer.write(project)

    def _get_parser(self, language):

        if language == "python":
            return PythonParser()

        raise NotImplementedError(language)