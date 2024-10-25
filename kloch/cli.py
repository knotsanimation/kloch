import abc
import argparse
import copy
import inspect
import json
import logging
import logging.handlers
import os
import re
import runpy
import sys
import tempfile
import textwrap
from pathlib import Path
from typing import List
from typing import Optional

import kloch
from kloch.launchers import get_available_launchers_serialized_classes
from kloch.launchers import BaseLauncher
from kloch.launchers import BaseLauncherSerialized
from kloch.session import SessionDirectory

LOGGER = logging.getLogger(__name__)

_ARGS_USER_COMMAND_DEST = "command"


class BaseParser:
    """
    The root parser who's all subparsers use as base.

    All arguments defined here are accessible by subparsers.

    Args:
        args: user command line argument already parsed by argparse
    """

    def __init__(self, args: argparse.Namespace, config: kloch.KlochConfig):
        self._args: argparse.Namespace = args
        self._config = config

    @property
    def debug(self) -> bool:
        """
        True to execute the CLI in debug mode. Usually with more verbose logging.
        """
        return self._args.debug

    @property
    def _profile_roots(self) -> List[Path]:
        """
        One or multiple filesystem path to existing directory containing profile file.
        The paths are append to the global profile roots variable.
        """
        return [Path(path) for path in self._args.profile_roots]

    @property
    def profile_roots(self) -> List[Path]:
        """
        One or multiple filesystem path to existing directory containing profile file.
        The paths are append to the global profile roots variable.
        """
        return self._config.profile_roots + self._profile_roots

    @property
    def session_root(self) -> Optional[Path]:
        return self._config.cli_session_dir

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
            "--profile_roots",
            nargs="*",
            default=[],
            help=cls._profile_roots.__doc__,
        )
        parser.set_defaults(func=cls)

    def _get_merged_profile(self, profile_identifiers: List[str]):
        """
        Merge each profile with its base then merge all of them from left to right.
        """
        profile_locations = self.profile_roots

        profiles = []
        for profile_id in profile_identifiers:
            profile_paths = kloch.get_profile_file_path(
                profile_id,
                profile_locations=profile_locations,
            )
            if len(profile_paths) >= 2:
                print(
                    f"ERROR | Found multiple profile with identifier '{profile_id}' "
                    f": {profile_paths}.",
                    file=sys.stderr,
                )
                sys.exit(1)

            if not profile_paths:
                print(
                    f"ERROR | No profile found with identifier '{profile_id}'.",
                    file=sys.stderr,
                )
                sys.exit(1)

            profile_path = profile_paths[0]
            LOGGER.debug(f"reading profile '{profile_path}'")
            try:
                profile = kloch.read_profile_from_file(
                    profile_path,
                    profile_locations=profile_locations,
                )
            except (
                kloch.filesyntax.ProfileAPIVersionError,
                kloch.filesyntax.ProfileInheritanceError,
            ) as error:
                print(
                    f"ERROR | '{error}'.",
                    file=sys.stderr,
                )
                sys.exit(1)

            profile = profile.get_merged_profile()
            profiles.append(profile)

        profile = profiles.pop(-1)
        for base_profile in profiles:
            profile.inherit = base_profile
            profile = profile.get_merged_profile()

        return profile


class RunParser(BaseParser):
    """
    A "run" sub-command.
    """

    @property
    def launcher(self) -> str:
        """
        The name of a launcher to use in the provided environment profile.

        Only required if the profile define more than one launcher profile.
        """
        return self._args.launcher

    @property
    def profile_ids(self) -> List[str]:
        """
        One or more identifier of existing environment profile(s).
        The profiles are concatenated together from left to right.
        """
        return self._args.profile_ids

    @property
    def command(self) -> List[str]:
        """
        A command to execute in the environment that is launched by the given profile.
        """
        return self._args.command

    def _execute(self, session_dir: SessionDirectory):
        LOGGER.debug(f"session dir at '{session_dir.path}'")

        plugins_names = self._config.launcher_plugins
        plugins_names_str = (": " + ",".join(plugins_names)) if plugins_names else ""
        LOGGER.debug(f"loading {len(plugins_names)} plugin modules{plugins_names_str}")
        launcher_plugins = kloch.launchers.load_plugin_launchers(
            module_names=plugins_names,
            subclass_type=BaseLauncherSerialized,
        )
        launchers_classes = get_available_launchers_serialized_classes(launcher_plugins)

        print(f"loading {len(self.profile_ids)} profiles ...")
        profile = self._get_merged_profile(self.profile_ids)

        # keep a backup of the merged profile for debugging
        LOGGER.debug(f"writing merged profile to '{session_dir.profile_path}'")
        kloch.write_profile_to_file(
            profile,
            file_path=session_dir.profile_path,
            profile_locations=self.profile_roots,
            check_valid_id=False,
        )

        launchers_dict = profile.launchers
        launchers_list = launchers_dict.to_serialized_list(launchers_classes)
        launchers_list = launchers_list.with_base_merged()
        if len(launchers_list) > 1 or self.launcher:
            if not self.launcher:
                print(
                    f"ERROR | More than one launcher defined in profile "
                    f"<{self.profile_ids}>: you need to specify a launcher name with --launcher",
                    file=sys.stderr,
                )
                sys.exit(1)

            launchers_dict = [
                _launcher
                for _launcher in launchers_list
                if _launcher.name == self.launcher
            ]
            if not launchers_dict:
                print(
                    f"ERROR | No launcher with name <{self.launcher}> "
                    f"found in profile <{self.profile_ids}>",
                    file=sys.stderr,
                )
                sys.exit(1)

        launcher_serial: BaseLauncherSerialized = launchers_list[0]
        launcher_serial.validate()
        launcher: BaseLauncher = launcher_serial.unserialize()
        command = self.command or None

        print(f"starting launcher {launcher.name}")
        LOGGER.debug(f"executing launcher={launcher} with command={command}")
        LOGGER.debug(f"os.environ={json.dumps(dict(os.environ), indent=4)}")

        sys.exit(launcher.execute(tmpdir=session_dir.path, command=command))

    def execute(self):
        session_root = self.session_root
        if session_root is None:
            with tempfile.TemporaryDirectory(prefix=f"{kloch.__name__}") as tmp_dir:
                session_dir = SessionDirectory.initialize(Path(tmp_dir))
                return self._execute(session_dir=session_dir)
        else:
            session_dir = SessionDirectory.initialize(session_root)
            return self._execute(session_dir=session_dir)

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
            "--launcher",
            type=str,
            help=cls.launcher.__doc__,
        )
        parser.add_argument(
            "--",
            dest=_ARGS_USER_COMMAND_DEST,
            nargs="*",
            default=[],
            help=(
                "Specify multiple argument to execute in the environment as a single command.\n"
                "MUST be the last argument as anything after is consumed."
                "If the profile already specify a command, the arguments are appended to the existing command."
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
        profile_locations = self.profile_roots
        profile_locations_txt = [str(path) for path in profile_locations]
        print(
            f"Searching {len(profile_locations)} locations: {profile_locations_txt} ..."
        )

        profile_paths = kloch.get_all_profile_file_paths(profile_locations)
        profiles: List[kloch.EnvironmentProfile] = []

        for path in profile_paths:
            try:
                profile = kloch.read_profile_from_file(path)
            except Exception as error:
                print(f"WARNING | {path}: {error}", file=sys.stderr)
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
    def profile_ids(self) -> List[str]:
        """
        One or more identifier of existing environment profile(s).
        The profiles are concatenated together from left to right.
        """
        return self._args.profile_ids

    def execute(self):
        profile = self._get_merged_profile(self.profile_ids)

        try:
            serialized = kloch.filesyntax.serialize_profile(profile)
        except kloch.filesyntax.ProfileInheritanceError as error:
            print(f"ERROR | {error}", file=sys.stderr)
            sys.exit(1)

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


class PythonParser(BaseParser):
    """
    A "python" sub-command.
    """

    @property
    def file_path(self) -> Path:
        """
        A filesysten path to an existing python file to execute or
        an existing directory that MUST contains a __main__.py file.
        """
        return self._args.file_path

    @property
    def user_args(self) -> List[str]:
        """
        Arbitrary nummber of command line argument passed to the python file.
        """
        return self._args.user_args

    def execute(self):
        LOGGER.debug(f"about to run '{self.file_path}' with args={self.user_args}")
        # we can set it without restoring because we sys.exit anyway
        sys.argv = [str(self.file_path)] + self.user_args

        runpy.run_path(str(self.file_path), run_name="__main__")
        sys.exit()

    @classmethod
    def add_to_parser(cls, parser: argparse.ArgumentParser):
        super().add_to_parser(parser)
        parser.add_argument(
            "file_path",
            type=str,
            help=cls.file_path.__doc__,
        )
        parser.add_argument(
            "user_args",
            type=str,
            nargs="*",
            help=cls.user_args.__doc__,
        )


class PluginsParser(BaseParser):
    """
    A "plugins" sub-command.
    """

    @property
    def launcher_plugins(self) -> List[str]:
        """
        Manually specify the launcher_plugins configuration key instead of using
        the default/user-generated one.

        This is a list of module names.
        """
        return self._args.launcher_plugins

    def execute(self):
        plugins_names = self.launcher_plugins or self._config.launcher_plugins
        plugins_names_str = (": " + ",".join(plugins_names)) if plugins_names else ""
        print(f"about to load {len(plugins_names)} plugin modules{plugins_names_str}")
        launcher_plugins = kloch.launchers.load_plugin_launchers(
            module_names=plugins_names,
            subclass_type=BaseLauncherSerialized,
        )

        issues = kloch.launchers.check_launcher_plugins(launcher_plugins)
        for issue in issues:
            print(f"WARNING | {issue.__class__.__name__}: {issue}", file=sys.stderr)

        launcher_classes = launcher_plugins.launchers
        if launcher_classes:
            print(f"found {len(launcher_classes)} launchers:")
            for launcher in launcher_classes:
                module_path = inspect.getfile(launcher)
                print(
                    f"- {launcher.source.__name__}: {launcher.__name__} (from '{module_path}')"
                )

        sys.exit()

    @classmethod
    def add_to_parser(cls, parser: argparse.ArgumentParser):
        super().add_to_parser(parser)
        parser.add_argument(
            "--launcher_plugins",
            type=str,
            nargs="*",
            help=cls.launcher_plugins.__doc__,
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


def _get_parser() -> argparse.ArgumentParser:
    """
    The argparse ArgumentParser that build the CLI
    """
    parser = argparse.ArgumentParser(
        kloch.__name__,
        description=(
            "Create an environment to launch software using pre-defined configurations."
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

    subparser = subparsers.add_parser(
        "python",
        description=(
            "Execute the given python file with the internal python interpreter."
        ),
    )
    PythonParser.add_to_parser(subparser)

    subparser = subparsers.add_parser(
        "plugins",
        description="List information about the currently registred plugins.",
    )
    PluginsParser.add_to_parser(subparser)
    return parser


def get_cli(argv: Optional[List[str]] = None, config: kloch.KlochConfig = None) -> BaseParser:
    """
    Return the command line interface generated from user arguments provided.

    Args:
        argv: command line arguments; from sys.argv if not provided
        config: the kloch config instance to use for running the cli
    """
    config = config or kloch.get_config()

    parser = _get_parser()

    argv: List[str] = copy.copy(argv) or sys.argv[1:]

    # retrieve the "--" system that allow to specify an arbitrary command to execute
    user_command = None
    if "--" in argv:
        split_index = argv.index("--")
        user_command = argv[split_index + 1 :]
        argv = argv[:split_index]

    # XXX: internal feature for the PythonLauncher. It's ok not having it documented in the CLI.
    if argv and argv[0] and Path(argv[0]).exists():
        argv.insert(0, "python")

    args = parser.parse_args(argv)
    setattr(args, _ARGS_USER_COMMAND_DEST, user_command)
    instance: BaseParser = args.func(args, config)

    # clean old sessions everytime the cli is launched
    if instance.session_root and instance.session_root.exists():
        cleaned = kloch.session.clean_outdated_session_dirs(
            root=instance.session_root,
            lifetime=config.cli_session_dir_lifetime,
        )
        LOGGER.debug(f"removed {len(cleaned)} outdated session dirs")

    return instance


def run_cli(argv: Optional[List[str]] = None):
    """
    Execute the CLI based on the provided user arguments.

    Args:
        argv: command line arguments; from sys.argv if not provided
    """
    config = kloch.get_config()
    cli = kloch.get_cli(argv, config=config)
    log_level = logging.DEBUG if cli.debug else config.cli_logging_default_level

    formatter = logging.Formatter(config.cli_logging_format, style="{")

    logging.root.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setLevel(log_level)
    handler.setFormatter(formatter)
    logging.root.addHandler(handler)

    for log_path in config.cli_logging_paths:
        log_path.parent.mkdir(exist_ok=True)
        handler = logging.handlers.RotatingFileHandler(
            log_path,
            # keep in sync with config option
            maxBytes=262144,
            backupCount=1,
            encoding="utf-8",
        )
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(formatter)
        logging.root.addHandler(handler)

    LOGGER.debug(f"starting {kloch.__name__} v{kloch.__version__}")
    LOGGER.debug(f"retrieved cli with args={cli._args}")

    sys.exit(cli.execute())