import subprocess
import sys
import traceback

from pathlib import Path
from typing import Optional
from typing import Union

import docutils.nodes
import docutils.statemachine
from docutils.parsers.rst import Directive
from docutils.parsers.rst import directives
from sphinx.application import Sphinx
from sphinx.util.typing import ExtensionMetadata


DIRECTIVE_NAME = "exec-inject"


class ExecutionError(RuntimeError):
    pass


def execute_python_code(code: Union[str, Path]) -> str:
    command = [sys.executable]
    if isinstance(code, Path):
        command.append(str(code))
    else:
        command += ["-c", code.encode("utf-8")]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise ExecutionError(
            f"# Error while executing code in subprocess:\n"
            f"__stdout__:{result.stdout}\n"
            f"__stderr__:{result.stderr}"
        )

    result_text = result.stdout or "" + result.stderr or ""
    return result_text


def generate_error_nodes(
    source_file_path: Path,
    line: int,
    code_content: Optional[Union[str, Path]] = None,
):
    nodes = [None]
    pnode = docutils.nodes.paragraph
    nodes += [
        pnode(
            text=(
                f"With directive {DIRECTIVE_NAME} in {Path(source_file_path).name}:{line}"
            )
        )
    ]
    if code_content:
        nodes += [docutils.nodes.literal_block(code_content, code_content)]
    traceback_txt = traceback.format_exc()
    nodes += [docutils.nodes.literal_block(traceback_txt, traceback_txt)]
    return [docutils.nodes.error(*nodes)]


class ExecDirective(Directive):
    """
    Execute the given python code and inject its stdout output directly in the rst document.

    Optionally load the python code from a given file.
    """

    has_content = True
    option_spec = {
        "filename": directives.path,
    }

    @property
    def filename(self) -> Optional[Path]:
        return Path(self.options["filename"]) if "filename" in self.options else None

    def run(self):
        tab_width = self.options.get(
            "tab-width", self.state.document.settings.tab_width
        )
        source_file_path = self.state_machine.input_lines.source(
            self.lineno - self.state_machine.input_offset - 1
        )

        filepath = self.filename

        try:
            if filepath:
                if not filepath.is_absolute():
                    filepath = Path(source_file_path).parent / filepath
                code_content = filepath
            else:
                code_content = "\n".join(self.content)

            try:
                text = execute_python_code(code_content)
            except ExecutionError as error:
                self.reporter.error(
                    f"{DIRECTIVE_NAME} directive failed to complete.",
                    line=self.lineno,
                )
                return generate_error_nodes(source_file_path, self.lineno, code_content)
            lines = docutils.statemachine.string2lines(
                text,
                tab_width,
                convert_whitespace=True,
            )
        except Exception as error:
            self.reporter.error(
                f"{DIRECTIVE_NAME} directive failed to complete.",
                line=self.lineno,
            )
            return generate_error_nodes(source_file_path, self.lineno)

        self.state_machine.insert_input(lines, source_file_path)
        return []


def setup(app: Sphinx) -> ExtensionMetadata:
    app.add_directive(DIRECTIVE_NAME, ExecDirective)
    return {
        "version": "0.2",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
