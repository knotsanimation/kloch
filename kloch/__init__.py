# XXX: any addition/change here need to be update in the doc too
__all__ = [
    "add_profile_location",
    "EnvironmentProfile",
    "filesyntax",
    "get_all_profile_file_paths",
    "get_profile_locations",
    "get_profile_file_path",
    "get_cli",
    "KENV_PROFILE_PATH_ENV_VAR",
    "LaunchersSerialized",
    "read_profile_from_file",
    "serialize_profile",
    "write_profile_to_file",
]

from .cli import get_cli
from . import filesyntax
from .filesyntax import LaunchersSerialized
from .filesyntax import EnvironmentProfile
from .filesyntax import KENV_PROFILE_PATH_ENV_VAR
from .filesyntax import serialize_profile
from .filesyntax import read_profile_from_file
from .filesyntax import write_profile_to_file
from .filesyntax import add_profile_location
from .filesyntax import get_profile_locations
from .filesyntax import get_profile_file_path
from .filesyntax import get_all_profile_file_paths

# keep in sync with pyproject.toml
__version__ = "0.5.0"
