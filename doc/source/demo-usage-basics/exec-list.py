from pathlib import Path

import kloch

THISDIR = Path(".", "source", "demo-usage-basics").absolute()


kloch.add_profile_location(THISDIR)
cli = kloch.get_cli(["list"])
cli.execute()
