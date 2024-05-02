from pathlib import Path

import kenvmanager

THISDIR = Path(".", "source", "demo-usage").absolute()


kenvmanager.add_profile_location(THISDIR)
cli = kenvmanager.get_cli(["list"])
cli.execute()
