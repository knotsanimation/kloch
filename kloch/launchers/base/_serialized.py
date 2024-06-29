import abc
import dataclasses
import logging
import os
from pathlib import Path
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from kloch._dictmerge import refacto_dict
from kloch._dictmerge import MergeableDict
from kloch._utils import expand_envvars
from kloch._utils import patch_environ
from ._dataclass import BaseLauncher
from ... import MergeRule

LOGGER = logging.getLogger(__name__)


def _resolve_path(src_str: str) -> str:
    """
    Ensure the path is system compliant if it looks like one.
    """
    try:
        exists = Path(src_str).exists()
    except OSError:
        return src_str

    if not exists:
        return src_str

    return str(Path(src_str).resolve())


def resolve_environ(environ: Dict[str, Union[str, List[str]]]) -> Dict[str, str]:
    """
    Resolve an "environ-like" dict structure to an ``os.environ`` dict structure.
    """

    def process_pair(key: str, value: str):
        if isinstance(value, List):
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


class _MergeableSystemEnviron(MergeableDict):
    @classmethod
    def get_merge_rule(cls, key: str) -> MergeRule:
        # we force to always append the environ keys even if not token
        if cls.resolve_key_tokens(key) == "environ":
            return MergeRule.append
        return super().get_merge_rule(key)


def _get_mergeable_system_environ():
    return _MergeableSystemEnviron({"environ": os.environ.copy()})


# we use a dataclass over enum because we need inheritance
# noinspection PyTypeChecker
@dataclasses.dataclass(frozen=True)
class BaseLauncherFields:
    """
    A mapping of 'dataclass field name': 'corresponding key name in serialized dict'.

    Where the field name is the variable name.
    This implies you can have a different variable string value than the variable name.

    Example: ``config_params="configParams"`` is valid.

    This class is never instanced and all attributes are used at class level.
    """

    # XXX: make sure each field has a type hint when subclassed !!
    # note: fields type hint are types expected in the serialized representation.
    # note: field.metadata is used in the static documentation implying it's rst syntax.

    environ: Dict[str, Union[str, List[str]]] = dataclasses.field(
        default="environ",
        metadata={
            "description": (
                "mapping of environment variable to set before starting the environment.\n"
                "\n"
                "The value can either be a regular string or a list of string.\n"
                "The list of string has each item joined using the system path separator [2]_.\n"
                "\n"
                "- All values have environment variables expanded with ``os.expandvars`` [1]_.\n"
                "  You can escape the expansion by doubling the ``$`` like ``$$``\n"
                "- All values are turned absolute and normalized [4]_ if they are existing paths.\n"
            ),
            "required": False,
        },
    )
    merge_system_environ: bool = dataclasses.field(
        default="merge_system_environ",
        metadata={
            "description": (
                "True to implicitly merge the system environment (from the machine "
                "reading the profile) with the potentially specified ``environ`` field.\n"
                'The system environ is merged as "base" so any key specified in the ``environ`` '
                "will override it."
            ),
            "required": False,
        },
    )

    command: List[str] = dataclasses.field(
        default="command",
        metadata={
            "description": "Arbitrary list of command line arguments to call at the end of the launcher execution.",
            "required": False,
        },
    )
    cwd: str = dataclasses.field(
        default="cwd",
        metadata={
            "description": (
                'Filesystem path to an existing directory to use as "current working directory".\n'
                "\n"
                "- The path will have environment variables expanded with ``os.expandvars`` [1]_. \n"
                "  You can escape the expansion by doubling the ``$`` like ``$$``.\n"
                "  You can also use variables defined in the ``environ`` key.\n"
                "- The path is turned absolute and normalized [4]_.\n"
            ),
            "required": False,
        },
    )

    @classmethod
    def iterate(cls) -> List[dataclasses.Field]:
        """
        Return all the fields defined on this dataclass
        """
        return list(dataclasses.fields(cls))


T = TypeVar("T", bound="BaseLauncherSerialized")


class BaseLauncherSerialized(MergeableDict):
    """
    A BaseLauncher instance as a serialized dict object.

    The dict structure might be invalid and might need resolving, before being
    unserialized to a valid BaseLauncher instance.
    """

    source: Type[BaseLauncher] = BaseLauncher
    """
    The source class this object serialize.
    """

    identifier: str = BaseLauncher.name
    """
    An unique name among serialized launcher that can be use in a dict key: value pair.
    """

    fields: BaseLauncherFields = BaseLauncherFields
    """
    List of all the fields that are serialized.
    """

    # Used for automatically building the static html documentation.
    # All string are in the rst syntax compatible with the static documentation builder.
    summary = (
        "An abstract launcher that whose purpose is to be merged with other launchers."
    )
    description = "This launcher is never launched and is simply merged with other launchers defined in the profile."

    def __add__(self: T, other: T) -> T:
        """
        Returns:
            new instance with deepcopied structure.
        """
        if not isinstance(other, BaseLauncherSerialized):
            raise TypeError(
                f"Cannot concatenate object of type {type(other)} with {type(self)}"
            )
        # XXX: we override so the class type is defined by the right member of the + operation
        return other.__class__(super().__add__(other))

    @abc.abstractmethod
    def validate(self):
        """
        Ensure the dict structure can be resolved to a valid structure than can be unserialized.

        Raise an exeception on any issue.
        """
        environ = self.fields.environ
        if environ in self:
            assert isinstance(self[environ], dict), f"'{environ}': must be a dict."
            for key, value in self[environ].items():
                assert isinstance(key, str), f"'{environ}': key '{key}' must be a str."

        cwd = self.fields.cwd
        if cwd in self:
            assert isinstance(self[cwd], str), f"'{cwd}': must be a str."

        command = self.fields.command
        if command in self:
            assert isinstance(self[command], list), f"'{command}': must be a list."
            for value in self[command]:
                assert isinstance(
                    value, str
                ), f"'{command}': item '{value}' must be str."

    def resolved(self) -> Dict:
        """
        Modify the dict structure, so it can be unserialized properly.
        """
        use_system_environ = self.fields.merge_system_environ

        if self.get(use_system_environ, True):
            base = self.__class__(_get_mergeable_system_environ() + self)
            # need to disable else infinite recursion
            base[use_system_environ] = False
            resolved = base.resolved()
            return resolved

        resolved = super().resolved()

        environ = self.fields.environ
        new_environ = {}
        if environ in self:
            old_environ = self.get(environ, {})
            new_environ = {}
            new_environ.update(resolve_environ(old_environ))
            new_environ = {key: str(value) for key, value in new_environ.items()}
            resolved[environ] = new_environ

        cwd = self.fields.cwd
        if self.get(cwd):
            with patch_environ():
                os.environ.clear()
                os.environ.update(new_environ)
                resolved[cwd] = str(
                    Path((expand_envvars(self[cwd]))).absolute().resolve()
                )

        # mapping of {'serialized key': 'dataclass field name'}
        fields: Dict[str, str] = {
            getattr(self.fields, field.name): field.name
            for field in dataclasses.fields(self.fields)
        }
        # remap serialized key name to dataclass field name
        dst_dict = {fields[key]: value for key, value in resolved.items()}

        return dst_dict

    def unserialize(self) -> BaseLauncher:
        """
        Convert the dict to a valid instance.
        """
        src_dict = self.resolved()
        del src_dict[self.fields.merge_system_environ]
        return self.source.from_dict(src_dict)
