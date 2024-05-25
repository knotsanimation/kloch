import dataclasses

import yaml
import kloch

config = kloch.get_config()
asdict = dataclasses.asdict(config)
asyaml = yaml.dump(asdict).split("\n")
print(f".. code-block:: yaml\n    :caption: kloch-config.yml\n\n")
for line in asyaml:
    print(f"    {line}")
