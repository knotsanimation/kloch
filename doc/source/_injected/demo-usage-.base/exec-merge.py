from pathlib import Path

import yaml

import kloch

THISDIR = Path(".", "source", "_injected", "demo-usage-.base").absolute()

profile_path = THISDIR / "profile-b.yml"
profile = kloch.read_profile_from_file(profile_path, profile_locations=[THISDIR])
profile = profile.get_merged_profile()
launcher_list = profile.launchers.to_serialized_list()
launcher_list = launcher_list.with_base_merged()
print(yaml.dump(launcher_list.to_dict(), sort_keys=False))
