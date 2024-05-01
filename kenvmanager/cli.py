import abc
import argparse
import json
import logging
import os
import sys
import tempfile
from pathlib import Path

import kenvmanager

LOGGER = logging.getLogger(__name__)


class BaseParser:
    """
    The root parser who's all subparsers use as base.

    All arguments defined here are accessible by subparsers.

    Args:
        args: user command line argument already parsed by argparse
    """

    def __init__(self, args):
        self._args: argparse.Namespace = args

    @property
    def debug(self) -> bool:
        """
        True to execute the CLI in debug mode. Usually with more verbose logging.
        """
        return self._args.debug

    @abc.abstractmethod
    def execute(self):
        """
        Arbitrary code that must be executed when the user ask this command.
        """
        raise NotImplementedError()

    @classmethod
    def add_to_parser(cls, parser: argparse.ArgumentParser):
        """
        Configure the given argparse ArgumentParser.
        """
        parser.add_argument("--debug", action="store_true", help=cls.debug.__doc__)
        parser.set_defaults(func=cls)


class RunParser(BaseParser):
    """
    A "run" sub-command.
    """

    @property
    def manager(self) -> str:
        """
        The name of a package manager to use in the provided environment profile.
        Only required if the profile define more than one package manager profile.
        """
        return self._args.manager

    @property
    def profile_id(self) -> str:
        """
        Identifier of an existing environment profile.
        """
        return self._args.profile_id

    @property
    def command(self) -> list[str]:
        """
        A command to execute in the environment that is launched by the given profile.
        """
        return self._args.command

    def execute(self):
        profile_path = kenvmanager.get_profile_file_path(self.profile_id)
        if not profile_path:
            raise ValueError(
                f"No profile found with associated identifier {self.profile_id}."
            )

        print(f"Reading profile {profile_path} ...")
        profile = kenvmanager.read_profile_from_file(profile_path)
        managers = profile.get_manager_profiles()
        if len(managers) > 1 or self.manager:
            if not self.manager:
                raise ValueError(
                    f"More than one package manager defined in profile "
                    f"<{self.profile_id}>: you need to specify a manager name with --manager"
                )

            managers = [
                manager for manager in managers if manager.name() == self.manager
            ]
            if not managers:
                raise ValueError(
                    f"No package manager with name <{self.manager}> "
                    f"found in profile <{self.profile_id}>"
                )

        manager = managers[0]
        command = self.command or None

        print(f"starting package manager {manager.name()}")
        LOGGER.debug(f"executing manager={manager} with command={command}")
        LOGGER.debug(f"os.environ={json.dumps(dict(os.environ), indent=4)}")

        with tempfile.TemporaryDirectory(
            prefix=f"{kenvmanager.__name__}-{manager.name()}",
            ignore_cleanup_errors=True,
        ) as tmpdir:
            sys.exit(manager.execute(tmpdir=Path(tmpdir), command=command))

    @classmethod
    def add_to_parser(cls, parser: argparse.ArgumentParser):
        super().add_to_parser(parser)
        parser.add_argument(
            "profile_id",
            type=str,
            help=cls.profile_id.__doc__,
        )
        parser.add_argument(
            "--manager",
            type=str,
            help=cls.manager.__doc__,
        )
        parser.add_argument(
            "--N0",
            dest="command",
            nargs="*",
            help=argparse.SUPPRESS,
        )


class ListParser(BaseParser):
    """
    A "list" sub-command.
    """

    def execute(self):
        print(
            f"Parsing environment variable {kenvmanager.KENV_PROFILE_PATH_ENV_VAR} ..."
        )

        profile_locations = kenvmanager.get_profile_locations()
        profile_locations_txt = [str(path) for path in profile_locations]
        print(
            f"Searching {len(profile_locations)} locations: {profile_locations_txt} ..."
        )

        profile_paths = kenvmanager.get_all_profile_file_paths(profile_locations)
        profiles: list[kenvmanager.EnvironmentProfileFileSyntax] = []

        for path in profile_paths:
            try:
                profile = kenvmanager.read_profile_from_file(path)
            except Exception as error:
                print(f"WARNING: {path}: {error}", file=sys.stderr)
                continue
            profiles.append(profile)

        profile_ids = [profile.identifier for profile in profiles]
        profile_ids_txt = ":\n- " + "\n- ".join(profile_ids) if profile_ids else "."
        message = f"Found {len(profile_ids)} valid profiles{profile_ids_txt}"
        print(message)

    @classmethod
    def add_to_parser(cls, parser: argparse.ArgumentParser):
        super().add_to_parser(parser)


def getCli(argv=None) -> BaseParser:
    parser = argparse.ArgumentParser(
        "kenv",
        description=(
            "A custom environment manager for rez.\n"
            "Allow to create an environment to launch software using pre-defined configurations."
        ),
    )
    BaseParser.add_to_parser(parser)
    subparsers = parser.add_subparsers(required=True)

    subparser = subparsers.add_parser(
        "run",
        help="Start an interactive environment session.",
    )
    RunParser.add_to_parser(subparser)

    subparser = subparsers.add_parser(
        "list",
        help="List all available profiles.",
    )
    ListParser.add_to_parser(subparser)

    argv = argv or sys.argv[1:]
    args = parser.parse_args(argv)
    return args.func(args)
