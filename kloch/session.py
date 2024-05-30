import logging
import socket
import time
import uuid
from pathlib import Path

LOGGER = logging.getLogger(__name__)


class SessionDirectory:
    """
    Manage the filesystem directory to store data during a kloch launcher session.

    Most of the data stored is arbitrary and generated depending on the launcher.
    """

    def __init__(self, path: Path):
        self.path: Path = path
        """
        Filesystem path to an existing directory.
        """

        self.timestamp_path = self.path / ".timestamp"
        """
        A file containing the timestamp at which the session was created.
        """

        self.profile_path = self.path / "profile.yml"
        """
        A file which contain the merged profile used to start the session.
        """

    @property
    def identifier(self) -> str:
        return self.path.name

    @property
    def timestamp(self) -> int:
        return int(self.timestamp_path.read_text())

    @classmethod
    def initialize(cls, root: Path) -> "SessionDirectory":
        """
        Generate a new unique session directory on the filesystem.

        This function should be safe to be executed from different thread on the same machine
        at the same time.
        """
        if not root.exists():
            LOGGER.debug(f"mkdir('{root}')")
            root.mkdir()

        timestamp = time.time()
        identifier: str = f"{timestamp}-{socket.gethostname()}-{uuid.uuid4()}"

        path = root / identifier
        LOGGER.debug(f"mkdir('{path}')")
        path.mkdir()

        instance = cls(path)

        LOGGER.debug(f"touch('{instance.timestamp_path}')")
        instance.timestamp_path.write_text(str(timestamp))
        return instance
