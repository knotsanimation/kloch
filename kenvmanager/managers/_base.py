import abc
import dataclasses
import logging
import os
from pathlib import Path
from typing import Any
from typing import ClassVar
from typing import Optional
from typing import Type
from typing import Union

from kenvmanager.filesyntax import refacto_dict

LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class PackageManagerBase:
    """
    An "abstract" dataclass that describe how a package manager must start a software environment.
    """

    # XXX: all fields defined MUST specify a default value (else inheritance issues)
    #   instead add them to the `required_fields` class variable.

    environ: dict[str, Union[str, list[str]]] = dataclasses.field(default_factory=dict)
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

        def process_pair(key: str, value: str):
            if isinstance(value, list):
                value = [os.path.expandvars(arg) for arg in value]
                value = os.pathsep.join(value)
            return key, str(value)

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
    def from_dict(cls, src_dict: dict[str, Any]) -> "PackageManagerBase":
        """
        Generate an instance from a python dict object with a specific structure.
        """
        return cls(**src_dict)


def get_package_manager_class(name: str) -> Optional[Type[PackageManagerBase]]:
    """
    Get the PackageManagerBase class that correspond to the given unique name.
    """
    for sub_class in [PackageManagerBase] + PackageManagerBase.__subclasses__():
        if sub_class.name() == name:
            return sub_class
    return None
