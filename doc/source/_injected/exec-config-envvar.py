import dataclasses

import kloch

fields = dataclasses.fields(kloch.config.KlochConfig)

for field in fields:
    print(f"{field.metadata['environ']}")
