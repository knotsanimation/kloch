import logging
import os
from pathlib import Path
from typing import Optional

import yaml

from ._profile import EnvironmentProfileFileSyntax


LOGGER = logging.getLogger(__name__)


KENV_PROFILE_PATH_ENV_VAR = "KENV_PROFILE_PATHS"

KENV_PROFILE_MAGIC = "KenvEnvironmentProfile"
KENV_PROFILE_VERSION = 1


def is_file_environment_profile(file_path: Path) -> bool:
    """
    Return True if the given file is an Environment Profile.
    """
    if not file_path.suffix == ".yml":
        return False

    with file_path.open("r") as file:
        content = yaml.safe_load(file)

    if not content:
        return False

    return content.get("__magic__", "").startswith(KENV_PROFILE_MAGIC)


def get_profile_locations() -> list[Path]:
    locations = os.getenv(KENV_PROFILE_PATH_ENV_VAR)
    if not locations:
        return []

    locations = [Path(location).absolute() for location in locations.split(os.pathsep)]
    return locations


def get_all_profile_file_paths(locations: Optional[list[Path]] = None) -> list[Path]:
    """
    Get all the environment-profile file paths as registred by the user.
    """
    locations = locations or get_profile_locations()
    return [
        path
        for location in locations
        for path in location.glob("*.yml")
        if is_file_environment_profile(path)
    ]


def _get_profile_identifier(file_path: Path) -> str:
    with file_path.open("r") as file:
        asdict: dict = yaml.safe_load(file)
    return asdict["identifier"]


def get_profile_file_path(profile_id: str) -> Optional[Path]:
    """
    Get the filesystem location to the profile with the given name.
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
) -> EnvironmentProfileFileSyntax:
    """
    Generate an instance from a serialized file on disk.
    """
    with file_path.open("r") as file:
        asdict: dict = yaml.safe_load(file)
    del asdict["__magic__"]

    base_name: Optional[str] = asdict.get("base", None)
    if base_name:
        base_path = get_profile_file_path(base_name)
        if not base_path:
            raise ValueError(f"Base profile {base_name} was not found.")
        base_profile = read_profile_from_file(base_path)
        asdict["base"] = base_profile

    profile = EnvironmentProfileFileSyntax.from_dict(asdict)
    if check_resolved:
        # we check the resolved profile doesn't raise errors
        profile.get_manager_profiles()

    return profile


def write_profile_to_file(
    profile: EnvironmentProfileFileSyntax,
    file_path: Path,
    check_valid_name: bool = True,
) -> Path:
    """
    Convert the instance to a serialized file on disk.
    """
    if check_valid_name:
        # expected to raise if more than one profile has the same name
        get_profile_file_path(profile.identifier)

    asdict = profile.to_dict()
    asdict["__magic__"] = f"{KENV_PROFILE_MAGIC}:{KENV_PROFILE_VERSION}"

    base_profile: Optional[EnvironmentProfileFileSyntax] = asdict.get("base", None)
    if base_profile:
        base_path = get_profile_file_path(base_profile.identifier)
        if not base_path:
            raise ValueError(
                f"Base profile {base_profile.identifier} is not registred on disk."
            )
        asdict["base"] = base_profile.identifier

    with file_path.open("w") as file:
        yaml.dump(asdict, file)
    return file_path
