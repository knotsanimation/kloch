import logging
import sys
import time
from pathlib import Path
from typing import Optional

import kenvmanager

THIS_DIR = Path(__file__).parent.resolve()
REPO_ROOT = THIS_DIR.parent.resolve()


def main(repo_root: Path):

    app_name = f"{kenvmanager.__name__}-v{kenvmanager.__version__}"
    as_one_file = False

    # // read
    start_script_path = repo_root / "kenvmanager" / "__main__.py"
    """
    Filesystem path to an existing python script used to start the application.
    """

    icon_path: Optional[Path] = None
    """
    Filesystem path to an existing .ico file.
    """

    # // write
    workdir = THIS_DIR / ".pyinstaller"
    """
    Working directory for pyinstaller, where it can dump all of its files.
    """

    targetdir = THIS_DIR / "build"
    """
    Build destination.
    """

    command = [
        "--clean",
        "--workpath",
        workdir,
        "--specpath",
        workdir,
        "--distpath",
        targetdir,
        "--name",
        app_name,
        # remove output dir if it exists
        "--noconfirm",
    ]
    # windows and mac-os specific
    if icon_path:
        command += ["--icon", str(icon_path)]
    if as_one_file:
        command += ["--onefile"]
    command += [start_script_path]

    installer_command = list(map(str, command))

    stime = time.time()
    LOGGER.info(f"starting pyinstaller with command={installer_command}")
    # deferred import to avoid PyInstaller to configure logging first
    import PyInstaller.__main__

    PyInstaller.__main__.run(installer_command)
    LOGGER.info(f"finished in {time.time() - stime}s")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="{levelname: <7} | {asctime} [{name}] {message}",
        style="{",
        stream=sys.stdout,
    )
    LOGGER = logging.getLogger(__name__)
    main(REPO_ROOT)
