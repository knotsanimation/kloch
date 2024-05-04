import abc
import contextlib
import dataclasses
import logging
import os
from pathlib import Path
from typing import Annotated
from typing import Any
from typing import ClassVar
from typing import Optional
from typing import Type
from typing import Union

from kenvmanager.filesyntax import refacto_dict

LOGGER = logging.getLogger(__name__)


@contextlib.contextmanager
def _patch_environ(**environ):
    """
    Temporarily change ``os.environ`` and restore it once finished.
    """
    old_environ = dict(os.environ)
    os.environ.update(environ)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(old_environ)


def _resolve_env_var(src_str: str) -> str:
    """
    Resolve environment variable pattern in the given string.

    Using ``os.path.expandvars``.
    """
    # temporary remove escape character
    new_str = src_str.replace("$$", "##tmp##")
    # environment variable expansion
    new_str = os.path.expandvars(new_str)
    # restore escaped character
    new_str = new_str.replace("##tmp##", "$")
    return new_str


def _resolve_path(src_str: str) -> str:
    """
    Ensure the path is system compliant if it looks like one.
    """
    if not Path(src_str).exists():
        return src_str
    return str(Path(src_str).resolve())


@dataclasses.dataclass
class BaseLauncher:
    """
    An "abstract" dataclass that describe how to start a software environment session.
    """

    # XXX: all fields defined MUST specify a default value (else inheritance issues)
    #   instead add them to the `required_fields` class variable.

    # XXX: all fields are automatically extracted in the static doc, you must
    #   typing.Annotated to add string metadata that is used as description (list of lines).

    environ: Annotated[
        dict[str, Union[str, list[str]]],
        "mapping of environment variable to set before starting the environment.",
        "",
        "The value can either be a regular string or a list of string.",
        "The list of string has each item joined using the system path separator [2]_.",
        "All values have environment variables expanded with ``os.expandvars`` [1]_. "
        "You can escape the expansion by doubling the ``$`` like ``$$``",
        "",
        "If the variable value is an existing path at resolve time, then it is normalized for the system (correct slashes) [4]_.",
    ] = dataclasses.field(default_factory=dict)
    """
    Mapping of environment variables to set when starting the environment.
    """

    required_fields: ClassVar[list[str]] = []
    """
    List of dataclass field that are required to build the instance from a dict object.
    
    "Required" imply they have a non-empty value.
    """

    def __post_init__(self):
        for field in dataclasses.fields(self):
            if field.name in self.required_fields and not getattr(self, field.name):
                raise ValueError(f"Missing required field '{field.name}'")

    @classmethod
    @abc.abstractmethod
    def name(cls) -> str:
        """
        A unique name among all subclasses.
        """
        return ".base"

    @classmethod
    @abc.abstractmethod
    def summary(cls) -> str:
        """
        Short one-line summary of what is this instance. Used for user documentation.

        Standard rst formatting can be used.
        """
        return "An abstract launcher that whose purpose is to be merged with other launchers."

    @classmethod
    @abc.abstractmethod
    def doc(cls) -> list[str]:
        """
        Extended documentation describing this launcher purpose. For user documentation.

        Standard rst formatting can be used.

        Returns:
            a list of text lines
        """
        return [
            "This launcher is never launched and is simply merged with other launchers defined in the profile."
        ]

    @abc.abstractmethod
    def execute(self, tmpdir: Path, command: Optional[list[str]] = None) -> int:
        """
        Start the given environment and execute this python session.

        Optionally execute the given command in the environment.

        Args:
            tmpdir: filesystem path to an existing temporary directory
            command: optional list of command line arguments

        Returns:
            The exit code of the execution. 0 if successfull, else imply failure.
        """
        pass

    def get_resolved_environ(self) -> dict[str, str]:
        """
        Get the ``environ`` field resolved to be ready to use.
        """
        # TODO see if its worth to make it part of LaunchersSerialized token resolving

        def process_pair(key: str, value: str):
            if isinstance(value, list):
                value = [_resolve_path(_resolve_env_var(str(path))) for path in value]
                value = os.pathsep.join(value)
            else:
                value = _resolve_path(_resolve_env_var(str(value)))

            # reverted by context manager, we need it so a variable defined after
            # another one can reuse that first one.
            os.environ[key] = value
            return key, value

        with _patch_environ():
            return refacto_dict(self.environ, callback=process_pair)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the instance to a python dict object.
        """
        as_dict = dataclasses.asdict(self)
        # remove optional keys that don't have a value
        as_dict = {
            key: value
            for key, value in as_dict.items()
            if key or key in self.required_fields
        }
        return as_dict

    @classmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> "BaseLauncher":
        """
        Generate an instance from a python dict object with a specific structure.
        """
        return cls(**src_dict)


def get_available_launchers_classes() -> list[Type[BaseLauncher]]:
    """
    Get all list of available launcher classes that are registred.
    """
    return [BaseLauncher] + BaseLauncher.__subclasses__()


def get_launcher_class(name: str) -> Optional[Type[BaseLauncher]]:
    """
    Get the launcher class which match the given unique name.
    """
    for sub_class in get_available_launchers_classes():
        if sub_class.name() == name:
            return sub_class
    return None
