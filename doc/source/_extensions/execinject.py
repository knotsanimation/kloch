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
    """
    The python code could not be run sucessfully
    """

    pass


def prefixlines(source: str, prefix: str):
    return "\n".join([prefix + line for line in source.split("\n")])


def execute_python_code(code: Union[str, Path]) -> str:
    """
    Execute the given python code in a python interpreter and return its stdout output.
    """
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
        stdout = result.stdout.strip("\n")
        stderr = result.stderr.strip("\n")
        raise ExecutionError(
            f"# Error while executing code in subprocess:\n"
            f"[__stdout__]\n{prefixlines(stdout, '| ')}\n"
            f"[__stderr__]\n{prefixlines(stderr, '| ')}"
        )

    result_text = result.stdout or "" + result.stderr or ""
    return result_text


def generate_error_nodes(
    source_file_path: Path,
    line: int,
    traceback_txt: str,
    code_content: Optional[Union[str, Path]] = None,
):
    """
    Replace the directive by a traceback block to debug the error that just happened.

    Args:
        source_file_path: path of the rst file with the original directive.
        line: number of the line in the rst file at which the directive is.
        traceback_txt: python formatted traceback to include in the block.
        code_content:
            optional code or file path that the directive try to execute but failed to.
            can be very verbose.
    """
    nodes = [None]
    pnode = docutils.nodes.paragraph
    nodes += [
        pnode(
            text=(
                f"Failed to execute directive {DIRECTIVE_NAME} in {Path(source_file_path).name}:{line}"
            )
        )
    ]
    if code_content:
        nodes += [docutils.nodes.literal_block(code_content, code_content)]
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
        code_content = None

        try:
            if filepath:
                if not filepath.is_absolute():
                    filepath = Path(source_file_path).parent / filepath
                code_content = filepath
            else:
                code_content = "\n".join(self.content)

            text = execute_python_code(code_content)
            lines = docutils.statemachine.string2lines(
                text,
                tab_width,
                convert_whitespace=True,
            )

        except Exception as error:
            self.reporter.error(
                f"{DIRECTIVE_NAME} directive failed to complete:\n"
                f"{prefixlines(str(error), '# ')}",
                line=self.lineno,
            )
            traceback_txt = traceback.format_exc()
            return generate_error_nodes(
                source_file_path=source_file_path,
                line=self.lineno,
                traceback_txt=traceback_txt,
                code_content=code_content,
            )

        self.state_machine.insert_input(lines, source_file_path)
        return []


def setup(app: Sphinx) -> ExtensionMetadata:
    """
    Boilerplate required to be loaded by sphinx.
    """
    app.add_directive(DIRECTIVE_NAME, ExecDirective)
    return {
        "version": "0.2",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
