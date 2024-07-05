from pathlib import Path

import kloch

THISDIR = Path(".", "source", "_injected", "demo-usage-basics").absolute()

cli = kloch.get_cli(["list", "--profile_roots", str(THISDIR)])
cli.execute()
