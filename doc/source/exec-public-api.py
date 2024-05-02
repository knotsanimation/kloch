import inspect
import types

import kenvmanager


output = {
    "functions": [],
    "classes": [],
    "modules": [],
    "other": [],
}

print("import kenvmanager")
for obj_name in sorted(kenvmanager.__all__):
    if not hasattr(kenvmanager, obj_name):
        output["other"].append((obj_name, ""))

    obj = getattr(kenvmanager, obj_name)
    doc = ""
    if hasattr(obj, "__doc__"):
        doc = obj.__doc__.lstrip(" ").lstrip("\n")
        doc = doc.split("\n")
        doc = doc[0].lstrip(" ")

    if isinstance(obj, types.FunctionType):
        obj_name = obj_name + "(...)"
        output["functions"].append((obj_name, doc))
    elif inspect.isclass(obj):
        obj_name = obj_name + "(...)"
        output["classes"].append((obj_name, doc))
    elif inspect.ismodule(obj):
        output["modules"].append((obj_name, doc))
    else:
        output["other"].append((obj_name, doc))

for category, content_list in output.items():
    print(f'\n""" {category} """')
    for content in content_list:
        print(f"kenvmanager.{content[0]}")
        doc = content[1]
        if doc:
            print(f"# {doc}")
        print("")
