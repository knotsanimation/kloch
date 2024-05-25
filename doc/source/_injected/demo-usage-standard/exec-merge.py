from pathlib import Path

import kloch

THISDIR = Path(".", "source", "_injected", "demo-usage-standard").absolute()

profile_path = THISDIR / "profile-b.yml"
kloch.add_profile_location(THISDIR)
profile = kloch.read_profile_from_file(profile_path)
profile = profile.get_merged_profile()
print(kloch.serialize_profile(profile))
