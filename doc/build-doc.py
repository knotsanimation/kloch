import os
import shutil
import subprocess
import sys
from pathlib import Path

THISDIR = Path(__file__).parent

SRCDIR = THISDIR / "source"
BUILDIR = THISDIR / "build"

shutil.rmtree(BUILDIR, ignore_errors=True)

COMMAND = [
    "sphinx-build",
    "-M",
    "html",
    str(SRCDIR),
    str(BUILDIR),
]
COMMAND += sys.argv[1:]

ENVIRON = dict(os.environ)
PYTHONPATH = f"{ENVIRON.get('PYTHONPATH', '')}{os.pathsep}{THISDIR.parent}"
PYTHONPATH = PYTHONPATH.lstrip(os.pathsep)
ENVIRON["PYTHONPATH"] = PYTHONPATH

subprocess.check_call(COMMAND, cwd=THISDIR, env=ENVIRON)
print(f"documentation generated in '{BUILDIR}'")
url = "file:///" + str(Path(BUILDIR / "html" / "index.html").as_posix())
print(f"html at '{url}'")
