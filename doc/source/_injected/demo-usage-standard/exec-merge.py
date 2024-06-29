from pathlib import Path

import kloch

THISDIR = Path(".", "source", "_injected", "demo-usage-standard").absolute()

profile_path = THISDIR / "profile-b.yml"
profile = kloch.read_profile_from_file(profile_path, profile_locations=[THISDIR])
profile = profile.get_merged_profile()
print(kloch.serialize_profile(profile))
