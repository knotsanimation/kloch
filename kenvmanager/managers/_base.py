import abc
import dataclasses
import importlib
import inspect
import logging
from pathlib import Path
from typing import Any
from typing import Callable
from typing import Optional
from typing import Sequence
from typing import Type
from typing import Union

LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class PackageManagerBase:
    """
    An "abstract" dataclass that describe how a package manager must start a software environment.
    """

    @classmethod
    @abc.abstractmethod
    def name(cls) -> str:
        """
        A unique name among all subclasses.
        """
        pass

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

    @abc.abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """
        Convert the instance to a python dict object.
        """
        pass

    @classmethod
    @abc.abstractmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> "PackageManagerBase":
        """
        Generate an instance from a python dict object with a specific structure.
        """
        pass


def get_package_manager_class(name: str) -> Optional[Type[PackageManagerBase]]:
    """
    Get the PackageManagerBase class that correspond to the given unique name.
    """
    for sub_class in PackageManagerBase.__subclasses__():
        if sub_class.name() == name:
            return sub_class
    return None
