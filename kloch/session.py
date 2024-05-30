import logging
import shutil
import socket
import time
import uuid
from pathlib import Path
from typing import List

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

        self.meta_session_path = self.path / "kloch.session"
        """
        A file indicating the directory is a session and which contains 
        the timestamp at which the session was created.
        """

        self.profile_path = self.path / "profile.yml"
        """
        A file which contain the merged profile used to start the session.
        """

    @property
    def identifier(self) -> str:
        return self.path.name

    @property
    def timestamp(self) -> float:
        return float(self.meta_session_path.read_text())

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
        # XXX: we generate uuid to prevent collision but we shorten it as we
        #   are already pretty safe with the timestamp.
        uuid_ = uuid.uuid4().hex[:8]
        identifier: str = f"{timestamp}-{socket.gethostname()}-{uuid_}"

        path = root / identifier
        LOGGER.debug(f"mkdir('{path}')")
        path.mkdir()

        instance = cls(path)

        LOGGER.debug(f"touch('{instance.meta_session_path}')")
        instance.meta_session_path.write_text(str(timestamp))
        return instance


def get_session_dirs(root: Path) -> List[SessionDirectory]:
    """
    Get all the session directories found in the given root directory.
    """
    return [
        SessionDirectory(path)
        for path in root.glob("*")
        if path.is_dir() and SessionDirectory(path).meta_session_path.exists()
    ]


def clean_outdated_session_dirs(root: Path, lifetime: float) -> List[Path]:
    """
    Iterate through all existing session directories and delete the one which have been created longer than the given lifetime.

    This function should handle file or dirs of the given root which are not sessions.

    Args:
        root: filesystem path to an existing directory.
        lifetime: maximum lifetime in hours of a session directory

    Returns:
        list of directories filesystem path that have been removed
    """
    # convert hours to seconds
    lifetime = lifetime * 3600
    current_time = time.time()
    minimal_lifetime = current_time - lifetime

    removed = []

    for session in get_session_dirs(root=root):

        if session.timestamp > minimal_lifetime:
            continue

        try:
            shutil.rmtree(session.path)
        except Exception as error:
            LOGGER.exception(
                f"failed to remove outdated session dir '{session.path}': {error}"
            )
            continue

        removed.append(session.path)

    return removed
