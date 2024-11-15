import dataclasses
import enum
import getpass
import logging
import sys
from typing import Dict
from typing import Optional

LOGGER = logging.getLogger(__name__)


class LauncherPlatform(enum.Flag):
    """
    Operating Systems that a launcher may support.
    """

    linux = enum.auto()
    darwin = enum.auto()
    windows = enum.auto()

    @classmethod
    def current(cls):
        """
        Get the member corresponding to the current runtime operating system.
        """
        current = sys.platform
        if current.startswith("linux"):
            return cls.linux
        if current.startswith("darwin"):
            return cls.darwin
        if current in ("win32", "cygwin"):
            return cls.windows

        raise OSError(f"Unsupported operating system '{current}'")

    def is_linux(self) -> bool:
        return self == self.linux

    def is_mac(self) -> bool:
        return self == self.darwin

    def is_windows(self) -> bool:
        return self == self.windows


_PLATFORM_MAPPING = {
    "linux": LauncherPlatform.linux,
    "windows": LauncherPlatform.windows,
    "mac": LauncherPlatform.darwin,
}
"""
Mapping of serialized platform names to their corresponding enum instance.
"""


@dataclasses.dataclass
class LauncherContext:
    """
    Collection of system-contextual values in which a profile is being parsed.

    You can compare 2 context using the equal comparator however be aware that
    a None value (implies unset) will be considered equal to any other value.

    Example::

         ctx1 = LauncherContext(platform=LauncherPlatform.linux, user="demo")
         ctx2 = LauncherContext(platform=LauncherPlatform.linux, user=None)
         assert ctx1 == ctx2

    """

    platform: Optional[LauncherPlatform] = dataclasses.field(
        default=None,
        metadata={
            "serialized_name": "os",
            "unserialize": lambda v: _PLATFORM_MAPPING[v],
            "doc": {
                "value": f"one of ``{'``, ``'.join(_PLATFORM_MAPPING.keys())}``",
                "description": "name of the operating system",
            },
        },
    )
    """
    name of the operating system
    """

    user: Optional[str] = dataclasses.field(
        default=None,
        metadata={
            "serialized_name": "user",
            "unserialize": str,
            "doc": {
                "value": f"arbitrary string",
                "description": "name of the user",
            },
        },
    )
    """
    name of the current user
    """

    def __str__(self) -> str:
        return f"os={self.platform.name};user={self.user}"

    def __eq__(self, other):
        c = self.__class__
        if not isinstance(other, c):
            raise TypeError(f"Cannot concatenate {c} and {type(other)}")

        for field in dataclasses.fields(c):
            selfvalue = getattr(self, field.name)
            othervalue = getattr(other, field.name)
            # we discard the comparison when a field is not set
            if selfvalue is None or othervalue is None:
                continue

            if selfvalue != othervalue:
                return False

        return True

    @classmethod
    def create_from_system(cls):
        """
        Fill the instance with values retrieved from the current system context.
        """
        return cls(
            platform=LauncherPlatform.current(),
            user=getpass.getuser(),
        )


_FIELDS_MAPPING: Dict[str, dataclasses.Field] = {
    field.metadata["serialized_name"]: field
    for field in dataclasses.fields(LauncherContext)
}


_ESCAPE_CHARACTER = "%!TMP}]"


def _escape(source: str) -> str:
    return source.replace("@@", _ESCAPE_CHARACTER)


def _unescape(source: str) -> str:
    return source.replace(_ESCAPE_CHARACTER, "@")


def resolve_context_expression(source: str) -> str:
    """
    Remove the profile context expression from the given source string.
    """
    escaped = _escape(source)
    if "@" not in escaped:
        return _unescape(escaped)
    return _unescape(source.split("@")[0])


def unserialize_context_expression(source: str) -> LauncherContext:
    """
    Generate a profile context based on its serialized expression form.

    The expression take the following pattern::

        .(@key=value)*

    Where ``.`` means any character, ``()*`` means it can be repated multiple times.

    Args:
        source:
            abitrary string which contain an expression to unserialize,
            may be an empty string.

    Returns:
        a new profile context instance (that may be empty).
    """
    escaped = _escape(source)

    if "@" not in escaped:
        return LauncherContext()

    members = escaped.split("@")[1:]
    asdict = {}

    for member in members:
        member = _unescape(member)
        key, value = member.split("=")
        field = _FIELDS_MAPPING.get(key)
        if not field:
            raise KeyError(
                f"Unsupported context key name '{key}'; must one of {_FIELDS_MAPPING}"
            )
        field_name = field.name
        unserialize = field.metadata["unserialize"]
        # we explicitly allow a field to be defined multiple time,
        # its last definition will take precedence in value.
        asdict[field_name] = unserialize(value)

    return LauncherContext(**asdict)
