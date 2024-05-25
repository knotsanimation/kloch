import logging
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional


import kloch

THIS_DIR = Path(__file__).parent.resolve()
REPO_ROOT = THIS_DIR.parent.resolve()
OVERWRITE_EXISTING = True


def main(repo_root: Path, overwrite_existing: bool = True):
    app_name = f"{kloch.__name__}-v{kloch.__version__}"
    as_one_file = False

    # // read
    start_script_path = repo_root / "kloch" / "__main__.py"
    """
    Filesystem path to an existing python script used to start the application.
    """

    icon_path: Optional[Path] = None
    """
    Filesystem path to an existing .ico or .png file.
    """

    # // write
    workdir = THIS_DIR / ".nuitka"
    """
    Working directory for nuikta, where it can dump all of its files.
    """

    build_dir = THIS_DIR / "build"
    """
    Build destination.
    """

    if as_one_file:
        raise NotImplementedError("Not implemented yet.")

    command = [
        "--verbose",
        "--standalone",
        f"--output-dir={workdir}",
        f"--output-filename={app_name}",
    ]
    # windows specific
    if icon_path:
        command += [f"--windows-icon-from-ico={icon_path}"]

    # always last
    command += [start_script_path]

    installer_command = [sys.executable, "-m", "nuitka"]
    installer_command += list(map(str, command))

    stime = time.time()
    LOGGER.info(f"starting nuitka with command={installer_command}")
    subprocess.run(installer_command, check=True, text=True)

    build_src_dir = workdir / (start_script_path.stem + ".dist")
    build_dst_dir = build_dir / (app_name + "-nuitka")

    if overwrite_existing and build_dst_dir.exists():
        LOGGER.debug(f"removing existing {build_dst_dir}")
        shutil.rmtree(build_dst_dir)

    LOGGER.info("copying build ...")
    shutil.copytree(build_src_dir, build_dst_dir)

    LOGGER.info(f"build finished in {time.time() - stime}s")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="{levelname: <7} | {asctime} [{name}] {message}",
        style="{",
        stream=sys.stdout,
    )
    LOGGER = logging.getLogger(__name__)
    main(REPO_ROOT, OVERWRITE_EXISTING)
