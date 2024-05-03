import abc
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


@dataclasses.dataclass
class PackageManagerBase:
    """
    An "abstract" dataclass that describe how a package manager must start a software environment.
    """

    # XXX: all fields defined MUST specify a default value (else inheritance issues)
    #   instead add them to the `required_fields` class variable.

    # XXX: all fields are automatically extracted in the static doc, you must
    #   typing.Annotated to add string metadata that is used as description (list of lines).

    environ: Annotated[
        dict[str, Union[str, list[str]]],
        "mapping of environment variable to set before starting the environment.",
        "",
        "The value can either be a regular string or a list of string. ",
        "The list of string has each item expanded with ``os.expandvars`` [1]_ and then joined",
        "using the system path separator [2]_.",
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
        One-line documentation for users explaining what is this manager.

        Standard rst formatting can be used.
        """
        return "An abstract manager that whose purpose is to be merged with other managers."

    @classmethod
    @abc.abstractmethod
    def doc(cls) -> list[str]:
        """
        Extended documentation for users explaining what is this manager.

        Standard rst formatting can be used.

        Returns:
            a list of text lines
        """
        return [
            "This manager cannot be used directly and is simply merged with other managers defined in the config."
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
        # TODO see if its worth to make it part of PackageManagersSerialized token resolving

        def process_pair(key: str, value: str):
            if isinstance(value, list):
                value = os.pathsep.join(value)

            value = str(value)
            # temporary remove escape character
            value = value.replace("$$", "##tmp##")
            # environment variable expansion
            value = os.path.expandvars(value)
            # restore escaped character
            value = value.replace("##tmp##", "$")
            return key, value

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


def get_available_managers_classes() -> list[Type[PackageManagerBase]]:
    """
    Get all the PackageManager classes that are registred.
    """
    return [PackageManagerBase] + PackageManagerBase.__subclasses__()


def get_package_manager_class(name: str) -> Optional[Type[PackageManagerBase]]:
    """
    Get the PackageManagerBase class that correspond to the given unique name.
    """
    for sub_class in get_available_managers_classes():
        if sub_class.name() == name:
            return sub_class
    return None
