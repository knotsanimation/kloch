from pathlib import Path

import kloch

THISDIR = Path(".", "source", "_injected", "demo-usage-basics").absolute()

cli = kloch.get_cli(["list", "--profile_paths", str(THISDIR)])
cli.execute()
