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
class PackageManagerProfileBase:
    """
    A dataclass that describe how a package manager must start a software environment.
    """

    @classmethod
    @abc.abstractmethod
    def name(cls) -> str:
        pass

    @abc.abstractmethod
    def execute(self, command: Optional[list[str]] = None) -> int:
        """
        Start the given environment and execute this python session.

        Optionally execute the given command in the environment.

        Returns:
            The exit code of the execution. 0 if successfull, else imply failure.
        """
        pass

    @abc.abstractmethod
    def to_dict(self) -> dict[str, Any]:
        pass

    @classmethod
    @abc.abstractmethod
    def from_dict(cls, src_dict: dict[str, Any]) -> "PackageManagerProfileBase":
        pass


def get_package_manager_profile_class(
    name: str,
) -> Optional[Type[PackageManagerProfileBase]]:
    for sub_class in PackageManagerProfileBase.__subclasses__():
        if sub_class.name() == name:
            return sub_class
    return None


def enforce_list_path_type(
    src: Sequence[str],
    path_exists: bool = True,
    excludes=None,
) -> list[str]:
    excludes = excludes or []
    converted = []
    for path in src:
        if path not in excludes:
            path = Path(path)
            if path_exists and not path.exists():
                raise ValueError(f"path does not exist: {path}")
        converted.append(str(path))
    return converted


def enforce_int_type(src: Union[str, int]):
    # expected to raise if conversion not possible
    return int(src)


def enforce_callback_type(src: dict[str, str]) -> Callable:
    module_name = src["module"]
    function_name = src["function"]
    user_module = importlib.import_module(module_name)
    callback = getattr(user_module, function_name)
    return callback


def serialize_callback(callback: Callable):
    module = inspect.getmodule(callback).__name__
    function = callback.__name__
    return {"module": module, "function": function}
