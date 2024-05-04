import abc
import argparse
import json
import logging
import os
import re
import sys
import tempfile
import textwrap
from pathlib import Path
from typing import Optional

import kenvmanager

LOGGER = logging.getLogger(__name__)

_ARGS_USER_COMMAND_DEST = "command"


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

    @property
    def profile_paths(self) -> list[Path]:
        """
        One or multiple filesystem path to existing directory containing profile file.
        The paths are append to the global profile path variable.
        """
        return [Path(path) for path in self._args.profile_paths]

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
        parser.add_argument(
            "--debug",
            action="store_true",
            help=cls.debug.__doc__,
        )
        parser.add_argument(
            "--profile_paths",
            nargs="*",
            default=[],
            help=cls.profile_paths.__doc__,
        )
        parser.set_defaults(func=cls)


def _get_merged_profile(profile_identifiers: list[str]):
    """
    Merge each profile with its base then merge all of them from left to right.
    """
    profiles = []
    for profile_id in profile_identifiers:
        profile_path = kenvmanager.get_profile_file_path(profile_id)
        if not profile_path:
            raise ValueError(f"No profile with identifier <{profile_id}> found.")
        LOGGER.debug(f"reading profile {profile_path}")
        profile = kenvmanager.read_profile_from_file(profile_path)
        profile = profile.get_merged_profile()
        profiles.append(profile)

    profile = profiles.pop(-1)
    for base_profile in profiles:
        profile.base = base_profile
        profile = profile.get_merged_profile()

    return profile


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
    def profile_ids(self) -> list[str]:
        """
        One or more identifier of existing environment profile(s).
        The profiles are concatenated together from left to right.
        """
        return self._args.profile_ids

    @property
    def command(self) -> list[str]:
        """
        A command to execute in the environment that is launched by the given profile.
        """
        return self._args.command

    def execute(self):
        print(f"loading {len(self.profile_ids)} profiles ...")
        profile = _get_merged_profile(self.profile_ids)

        launchers = profile.launchers.unserialize()
        if len(launchers) > 1 or self.manager:
            if not self.manager:
                raise ValueError(
                    f"More than one launcher defined in profile "
                    f"<{self.profile_ids}>: you need to specify a manager name with --manager"
                )

            launchers = [
                launcher for launcher in launchers if launcher.name() == self.manager
            ]
            if not launchers:
                raise ValueError(
                    f"No launcher with name <{self.manager}> "
                    f"found in profile <{self.profile_ids}>"
                )

        launcher = launchers[0]
        command = self.command or None

        print(f"starting launcher {launcher.name()}")
        LOGGER.debug(f"executing launcher={launcher} with command={command}")
        LOGGER.debug(f"os.environ={json.dumps(dict(os.environ), indent=4)}")

        with tempfile.TemporaryDirectory(
            prefix=f"{kenvmanager.__name__}-{launcher.name()}",
        ) as tmpdir:
            sys.exit(launcher.execute(tmpdir=Path(tmpdir), command=command))

    @classmethod
    def add_to_parser(cls, parser: argparse.ArgumentParser):
        super().add_to_parser(parser)
        parser.add_argument(
            "profile_ids",
            type=str,
            nargs="+",
            help=cls.profile_ids.__doc__,
        )
        parser.add_argument(
            "--manager",
            type=str,
            help=cls.manager.__doc__,
        )
        parser.add_argument(
            "--",
            dest=_ARGS_USER_COMMAND_DEST,
            nargs="*",
            default=[],
            help=(
                "Specify multiple argument to execute in the environment as a single command.\n"
                "MUST be the last argument as anything after is consumed."
            ),
        )


class ListParser(BaseParser):
    """
    A "list" sub-command.
    """

    @property
    def id_filter(self) -> Optional[str]:
        """
        A regex expression to remove profiles whose identifier doesn't match.

        Example: "knots" will match all profile starting by "knots";
        ".*beta.*" will match all profile containing "beta"
        """
        return self._args.id_filter

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
        profiles: list[kenvmanager.EnvironmentProfile] = []

        for path in profile_paths:
            try:
                profile = kenvmanager.read_profile_from_file(path)
            except Exception as error:
                print(f"WARNING: {path}: {error}", file=sys.stderr)
                continue
            profiles.append(profile)

        profile_ids = [profile.identifier for profile in profiles]

        if self.id_filter:
            pattern = re.compile(self.id_filter)
            original_profile_count = len(profile_ids)
            profile_ids = [
                profile_id for profile_id in profile_ids if pattern.match(profile_id)
            ]
            print(
                f"Filter <{self.id_filter}> specified, reduced listed profiles from "
                f"{original_profile_count} to {len(profile_ids)} profiles."
            )

        profile_ids_txt = ":\n- " + "\n- ".join(profile_ids) if profile_ids else "."
        message = f"Found {len(profile_ids)} valid profiles{profile_ids_txt}"
        print(message)

    @classmethod
    def add_to_parser(cls, parser: argparse.ArgumentParser):
        super().add_to_parser(parser)
        parser.add_argument(
            "id_filter",
            type=str,
            nargs="?",
            default=None,
            help=cls.id_filter.__doc__,
        )


class ResolveParser(BaseParser):
    """
    A "resolve" sub-command.
    """

    @property
    def profile_ids(self) -> list[str]:
        """
        One or more identifier of existing environment profile(s).
        The profiles are concatenated together from left to right.
        """
        return self._args.profile_ids

    def execute(self):
        profile = _get_merged_profile(self.profile_ids)
        serialized = kenvmanager.serialize_profile(profile)
        print(serialized)

    @classmethod
    def add_to_parser(cls, parser: argparse.ArgumentParser):
        super().add_to_parser(parser)
        parser.add_argument(
            "profile_ids",
            type=str,
            nargs="+",
            help=cls.profile_ids.__doc__,
        )


class RawFormatter(argparse.HelpFormatter):
    """
    https://stackoverflow.com/a/64102901/13806195
    """

    def _fill_text(self, text, width, indent):
        # Strip the indent from the original python definition that plagues most of us.
        text = textwrap.dedent(text)
        text = textwrap.indent(text, indent)  # Apply any requested indent.
        text = text.splitlines()  # Make a list of lines
        text = [textwrap.fill(line, width) for line in text]  # Wrap each line
        text = "\n".join(text)  # Join the lines again
        return text


def get_cli(argv=None) -> BaseParser:
    """
    Return the command line interface generated from user arguments provided.

    Args:
        argv: source command line argument to use instea dof the usual sys.argv
    """
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
        description=(
            "Launch an environment as described in the given profile.\n\n"
            'Optionally specify a command to execute after the "--" argument:\n'
            '   > %(prog)s some-profile -- echo "hello world"'
        ),
        formatter_class=RawFormatter,
    )
    RunParser.add_to_parser(subparser)

    subparser = subparsers.add_parser(
        "list",
        description="List all available profiles.",
    )
    ListParser.add_to_parser(subparser)

    subparser = subparsers.add_parser(
        "resolve",
        description=(
            "Output the given profile(s) resolved and merged to a single profile."
            "The output is machine parsable as a valid yaml file "
            "(unless you use the --debug flag)."
        ),
    )
    ResolveParser.add_to_parser(subparser)

    argv: list[str] = argv or sys.argv[1:]

    # retrieve the "--" system that allow to specify an arbitrary command to execute
    user_command = None
    if "--" in argv:
        split_index = argv.index("--")
        user_command = argv[split_index + 1 :]
        argv = argv[:split_index]

    args = parser.parse_args(argv)
    setattr(args, _ARGS_USER_COMMAND_DEST, user_command)
    return args.func(args)
