import dataclasses
import logging

import yaml

from kloch.launchers import BaseLauncherSerialized
from kloch.launchers import BaseLauncherFields
from ._dataclass import RezEnvLauncher

LOGGER = logging.getLogger(__name__)


# noinspection PyTypeChecker
@dataclasses.dataclass(frozen=True)
class RezEnvLauncherFields(BaseLauncherFields):
    requires: dict[str, str] = dataclasses.field(
        default="requires",
        metadata={
            "description": "mapping of rez `package name`: `package version`",
            "required": False,
        },
    )
    params: list[str] = dataclasses.field(
        default="params",
        metadata={
            "description": (
                "list of command line arguments passed to rez-env.\n"
                "\n"
                "Check the `rez documentation <https://rez.readthedocs.io/en/stable/commands/rez-env.html>`_.\n"
            ),
            "required": False,
        },
    )
    config: dict = dataclasses.field(
        default="config",
        metadata={
            "description": "content of a valid yaml rez config that is created on the fly before the rez-env.",
            "required": False,
        },
    )


class RezEnvLauncherSerialized(BaseLauncherSerialized):
    source = RezEnvLauncher

    identifier = RezEnvLauncher.name

    fields = RezEnvLauncherFields

    summary = "Start an interactive rez shell using the ``rez-env`` command."
    description = (
        "We generate a rez interactive shell from a list of package requirements.\n"
        "The request if first resolved as a `.rxt` file using ``rez-env --output``\n"
        "and then launched with ``rez-env --input``.\n"
        "\n"
        "The launcher will use a subprocess to start rez-env [3]_.\n"
    )

    def validate(self):
        super().validate()

        params = self.fields.params
        if params in self:
            assert isinstance(self[params], list), f"'{params}': must be a list."
            for item in self[params]:
                assert isinstance(
                    item, str
                ), f"'{params}': value '{item}' must be a str."

        requires = self.fields.requires
        if requires in self:
            assert isinstance(self[requires], dict), f"'{requires}': must be a dict."
            for key, value in self[requires].items():
                assert isinstance(key, str), f"'{requires}': key '{key}' must be a str."
                assert isinstance(
                    value, str
                ), f"'{requires}': value '{value}' must be a str."

        config = self.fields.config
        if config in self:
            assert isinstance(self[config], dict), f"'{config}': must be a dict."
            try:
                yaml.dump(self[config])
            except Exception as error:
                raise AssertionError(
                    f"'{config}': must be serializable to yaml: {error}."
                )

    # we override for type-hint
    def unserialize(self) -> RezEnvLauncher:
        # noinspection PyTypeChecker
        return super().unserialize()
