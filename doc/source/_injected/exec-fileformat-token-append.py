import json
from kloch import MergeableDict

base = MergeableDict(
    {
        "rezenv": {
            "+=config": {"quiet": True},
            "requires": {"houdini": "20", "devUtils": "2.1"},
            "environ": {"STATUS": "wip"},
            "roots": ["/d/packages"],
        }
    }
)
top = MergeableDict(
    {
        "rezenv": {
            "+=config": {"quiet": False, "debug": True},
            "requires": {"maya": "2023", "-=devUtils": ""},
            "==environ": {"PROD": "test"},
            "roots": ["/d/prods"],
        }
    }
)
print(json.dumps(base + top, indent=4))
