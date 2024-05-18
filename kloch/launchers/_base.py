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

from kloch._dictmerge import refacto_dict
from kloch._utils import expand_envvars
from kloch._utils import patch_environ

LOGGER = logging.getLogger(__name__)


def _resolve_path(src_str: str) -> str:
    """
    Ensure the path is system compliant if it looks like one.
    """
    if not Path(src_str).exists():
        return src_str
    return str(Path(src_str).resolve())


def _resolve_environ(environ: dict[str, Union[str, list[str]]]) -> dict[str, str]:
    """
    Resolve an "environ-like" dict structure to an ``os.environ`` dict structure.
    """
    # TODO see if its worth to make it part of LaunchersSerialized token resolving

    def process_pair(key: str, value: str):
        if isinstance(value, list):
            value = [_resolve_path(expand_envvars(str(path))) for path in value]
            value = os.pathsep.join(value)
        else:
            value = _resolve_path(expand_envvars(str(value)))

        # reverted by context manager, we need it so a variable defined after
        # another one can reuse that first one.
        os.environ[key] = value
        return key, value

    with patch_environ():
        return refacto_dict(environ, callback=process_pair)


@dataclasses.dataclass
class BaseLauncher:
    """
    An "abstract" dataclass that describe how to start a software environment session.
    """

    # XXX: all fields defined MUST specify a default value (else inheritance issues)
    #   instead add them to the `required_fields` class variable.

    environ: dict[str, Union[str, list[str]]] = dataclasses.field(default_factory=dict)
    """
    Mapping of environment variables to set when starting the environment.
    
    The developer is reponsible of honoring the field usage in its launcher implementation.
    """

    command: list[str] = dataclasses.field(default_factory=list)
    """
    Arbitrary list of command line arguments to call at the end of the launcher execution.
    
    The developer is reponsible of honoring the field usage in its launcher implementation.
    """

    cwd: Optional[str] = None
    """
    Current working directory.
    
    The developer is reponsible of honoring the field usage in its launcher implementation.
    """

    required_fields: ClassVar[list[str]] = []
    """
    List of dataclass field that are required to build the instance from a dict object.
    
    "Required" imply they have a non-empty value.
    """

    name: ClassVar[str] = ".base"
    """
    A unique name among all subclasses.
    """

    def __post_init__(self):
        for field in dataclasses.fields(self):
            if field.name in self.required_fields and not getattr(self, field.name):
                raise ValueError(
                    f"Missing required field '{field.name}' for instance {self}"
                )

        new_environ = dict(os.environ)
        new_environ.update(_resolve_environ(self.environ))
        self.environ = new_environ

        if self.cwd:
            with patch_environ():
                os.environ.clear()
                os.environ.update(new_environ)
                self.cwd = str(Path((expand_envvars(self.cwd))).absolute().resolve())

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
        if sub_class.name == name:
            return sub_class
    return None
