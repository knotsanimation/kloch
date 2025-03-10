from pathlib import Path
import sys
import subprocess

THISDIR = Path(".", "source", "_injected", "demo-fileformat").absolute()

result = subprocess.run(
    [
        sys.executable,
        "-m",
        "kloch",
        "resolve",
        "knots:echoes",
        "--profile_roots",
        str(THISDIR),
        "--skip-context-filtering",
    ],
    capture_output=True,
    text=True,
)
print(result.stdout)
