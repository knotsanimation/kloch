import logging
import os
from pathlib import Path
from typing import Optional

import yaml

from ._profile import LaunchersSerialized
from ._profile import EnvironmentProfile


LOGGER = logging.getLogger(__name__)


KENV_PROFILE_PATH_ENV_VAR: str = "KENV_PROFILE_PATHS"
"""
Name of the user-editable environment variable to add profile locations.
"""

_PROFILE_LOCATIONS_INTERNAL: list[Path] = []

KENV_PROFILE_MAGIC = "kloch_profile"
KENV_PROFILE_VERSION = 2


def is_file_environment_profile(file_path: Path) -> bool:
    """
    Return True if the given file is an Environment Profile.

    Args:
        file_path: filesystem path to an existing file
    """
    if not file_path.suffix == ".yml":
        return False

    with file_path.open("r", encoding="utf-8") as file:
        content = yaml.safe_load(file)

    if not content:
        return False

    return content.get("__magic__", "").startswith(KENV_PROFILE_MAGIC)


def add_profile_location(location: Path):
    """
    Add a location where profile can be found.

    Locations added thorugh here are appended to the environment defined locations.

    Args:
        location: filesystem path to an existing directory.
    """
    global _PROFILE_LOCATIONS_INTERNAL
    if location in _PROFILE_LOCATIONS_INTERNAL:
        return
    _PROFILE_LOCATIONS_INTERNAL.append(location)


def get_profile_locations() -> list[Path]:
    """
    Get the user-defined directories where profile are stored.

    Returns:
         list of filesystem path to directory that might exist
    """
    locations = os.getenv(KENV_PROFILE_PATH_ENV_VAR)
    if not locations and not _PROFILE_LOCATIONS_INTERNAL:
        return []

    if locations:
        locations = [
            Path(location).absolute() for location in locations.split(os.pathsep)
        ]
        locations += _PROFILE_LOCATIONS_INTERNAL
    else:
        locations = list(_PROFILE_LOCATIONS_INTERNAL)

    return locations


def get_all_profile_file_paths(locations: Optional[list[Path]] = None) -> list[Path]:
    """
    Get all the environment-profile file paths as registred by the user.

    Args:
        locations: list of filesystem path to directory that might exist
    """
    locations = locations or get_profile_locations()
    return [
        path
        for location in locations
        for path in location.glob("*.yml")
        if is_file_environment_profile(path)
    ]


def _get_profile_identifier(file_path: Path) -> str:
    with file_path.open("r", encoding="utf-8") as file:
        asdict: dict = yaml.safe_load(file)
    return asdict["identifier"]


def get_profile_file_path(profile_id: str) -> Optional[Path]:
    """
    Get the filesystem location to the profile with the given name.

    Returns:
        filesystem path to an existing file or None if not found.
    """
    profile_paths = get_all_profile_file_paths()
    profiles: list[Path] = [
        path for path in profile_paths if _get_profile_identifier(path) == profile_id
    ]
    if len(profiles) > 1:
        raise RuntimeError(
            f"Found multiple profile with the same name {profile_id}. "
            f"Ensure all name in your profile file are unique."
        )
    if not profiles:
        return None

    return profiles[0]


def read_profile_from_file(
    file_path: Path,
    check_resolved: bool = True,
) -> EnvironmentProfile:
    """
    Generate an instance from a serialized file on disk.

    Args:
        file_path: filesystem path to an existing file
        check_resolved: if True, run additional sanity check on the profile file
    """
    with file_path.open("r", encoding="utf-8") as file:
        asdict: dict = yaml.safe_load(file)

    profile_version = int(asdict["__magic__"].split(":")[-1])
    if not profile_version == KENV_PROFILE_VERSION:
        raise SyntaxError(
            f"Cannot read profile with version <{profile_version}> while current "
            f"API version is <{KENV_PROFILE_VERSION}>."
        )
    del asdict["__magic__"]

    base_name: Optional[str] = asdict.get("base", None)
    if base_name:
        base_path = get_profile_file_path(base_name)
        if not base_path:
            raise ValueError(f"Base profile {base_name} was not found.")
        base_profile = read_profile_from_file(base_path)
        asdict["base"] = base_profile

    launchers = LaunchersSerialized(asdict["launchers"])
    if check_resolved:
        # discard output but ensure it doesn't raise error
        launchers.unserialize()
    asdict["launchers"] = launchers

    profile = EnvironmentProfile.from_dict(asdict)

    return profile


def serialize_profile(profile: EnvironmentProfile) -> str:
    """
    Convert the instance to a serialized dictionnary intended to be written on disk.
    """
    asdict = {"__magic__": f"{KENV_PROFILE_MAGIC}:{KENV_PROFILE_VERSION}"}
    asdict.update(profile.to_dict())

    base_profile: Optional[EnvironmentProfile] = asdict.get("base", None)
    if base_profile:
        base_path = get_profile_file_path(base_profile.identifier)
        if not base_path:
            raise ValueError(
                f"Base profile {base_profile.identifier} is not registred on disk."
            )
        asdict["base"] = base_profile.identifier

    # remove custom class wrapper
    asdict["launchers"] = dict(asdict["launchers"])

    return yaml.dump(asdict, sort_keys=False)


def write_profile_to_file(
    profile: EnvironmentProfile,
    file_path: Path,
    # TODO rename param to check_valid_id
    check_valid_name: bool = True,
) -> Path:
    """
    Convert the instance to a serialized file on disk.

    Args:
        profile: profile instance to write to disk
        file_path:
            filesystem path to a file that might exist.
            parent location is expected to exist.
        check_valid_name:
            if True, ensure the identifier of the profile is unique
    """
    if check_valid_name:
        # expected to raise if more than one profile has the same name
        get_profile_file_path(profile.identifier)

    serialized = serialize_profile(profile)

    file_path.write_text(serialized)
    return file_path
