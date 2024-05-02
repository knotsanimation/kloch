from pathlib import Path

import kenvmanager

THISDIR = Path(".", "source", "demo-usage-standard").absolute()

profile_path = THISDIR / "profile-b.yml"
kenvmanager.add_profile_location(THISDIR)
profile = kenvmanager.read_profile_from_file(profile_path)
profile = profile.get_merged_profile()
print(kenvmanager.serialize_profile(profile))
