import dataclasses
import http.client
import subprocess
from pathlib import Path
from typing import List
from typing import Optional

from kloch.launchers import BaseLauncher
from kloch.launchers import BaseLauncherSerialized
from kloch.launchers import BaseLauncherFields


@dataclasses.dataclass
class GitCloneLauncher(BaseLauncher):

    name = "git-clone"

    # all field must have a default value, but we make it
    #   required using the bellow `required_fields` class attribute
    remote_url: str = ""

    required_fields = ["remote_url"]

    def execute(self, tmpdir: Path, command: Optional[List[str]] = None):
        # we consider `command` are just extra args to git clone command
        _command = ["git", "clone", self.remote_url] + command
        subprocess.run(_command, env=self.environ, cwd=self.cwd)


@dataclasses.dataclass(frozen=True)
class GitCloneLauncherFields(BaseLauncherFields):

    # field name must be the same as in the BaseLauncher subclass above
    remote_url: str = dataclasses.field(
        # this is the expected key name in the serialized representation
        default="remote-url",
        # this if for automated documentation generation
        metadata={
            "description": "An URL to a valid remote git repository.",
            "required": True,
        },
    )


def does_url_exists(url: str) -> bool:
    connection = http.client.HTTPConnection(url)
    connection.request("HEAD", "")
    return connection.getresponse().status < 400


class GitCloneLauncherSerialized(BaseLauncherSerialized):
    # the class it serialize
    source = GitCloneLauncher

    # we can pick a different name but we keep it similar for simplicity
    identifier = GitCloneLauncher.name

    fields = GitCloneLauncherFields

    # short one line description of the launcher
    summary = "Just clone a repository from a git remote."

    # full documentation of an arbitrary length for the launcher
    description = "From a git remote repository url, git clone it in the current working directory."

    def validate(self):
        super().validate()
        remote_url = self.fields.remote_url
        assert remote_url in self, f"'{remote_url}': missing or empty attribute."
        assert does_url_exists(
            self[remote_url]
        ), f"'{remote_url}': url provided doesn't exists: {self[remote_url]}."

    # we override for type-hint
    def unserialize(self) -> GitCloneLauncher:
        # noinspection PyTypeChecker
        return super().unserialize()
