"""
Variables whose values doesn't change during application runtime.
"""

from typing import List

_KLOCH_CONFIG_PREFIX = "KLOCH_CONFIG"


class Environ:
    """
    Environment variables used across the application.
    """

    CONFIG_PATH = f"{_KLOCH_CONFIG_PREFIX}_PATH"
    """
    Environment variable that must specify a file path to an existing configuration file.
    """

    CONFIG_LAUNCHER_PLUGINS = f"{_KLOCH_CONFIG_PREFIX}_launcher_plugins".upper()

    CONFIG_CLI_LOGGING_PATHS = f"{_KLOCH_CONFIG_PREFIX}_cli_logging_paths".upper()

    CONFIG_CLI_LOGGING_FORMAT = f"{_KLOCH_CONFIG_PREFIX}_cli_logging_format".upper()

    CONFIG_CLI_LOGGING_DEFAULT_LEVEL = (
        f"{_KLOCH_CONFIG_PREFIX}_cli_logging_default_level".upper()
    )

    CONFIG_CLI_SESSION_PATH = f"{_KLOCH_CONFIG_PREFIX}_cli_session_path".upper()

    CONFIG_CLI_SESSION_LIFETIME = f"{_KLOCH_CONFIG_PREFIX}_cli_lifetime".upper()

    CONFIG_PROFILE_ROOTS = f"{_KLOCH_CONFIG_PREFIX}_profile_roots".upper()

    @classmethod
    def list_all(cls) -> List[str]:
        """
        Return all environment variables supported by the application.
        """
        return [
            obj
            for obj_name, obj in vars(cls).items()
            if not obj_name.startswith("__")
            and isinstance(obj, str)
            and obj.startswith("KLOCH")
        ]
