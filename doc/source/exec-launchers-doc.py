"""
Build an automatic rst documentation including a table from a dataclass object.

All the information is extracted from the code of the dataclass.
"""

import dataclasses
from typing import Type

import kloch.launchers
from kloch.filesyntax._doc import LauncherDoc


RowType = tuple[str, str, str]


def enforce_col_length(
    row: tuple[str, str, str],
    lengths: list[int],
) -> RowType:
    # noinspection PyTypeChecker
    return tuple(
        col.ljust(lengths[index], col[-1] if col else " ")
        for index, col in enumerate(row)
    )


def unify_columns(table: list[RowType]) -> list[str]:
    """
    Add the columns separator to return a row string.
    """
    new_table = []
    for row in table:
        sep = "+" if row[-1][-1] in ["-", "="] else "|"
        row = sep + sep.join(row) + sep
        new_table.append(row)
    return new_table


def create_field_table(
    field: dataclasses.Field,
    field_name: str,
    field_doc: str,
    required: bool,
) -> list[RowType]:
    required = "yes" if required else "no"

    doc = field_doc.split("\n")

    # typing.Annotated
    if hasattr(field.type, "__metadata__"):
        ftype = field.type.__origin__
    else:
        ftype = field.type

    ftype = str(ftype).replace("typing.", "")

    row1 = (f" ``{field_name}`` ", " **required** ", f" {required} ")
    row2 = ("-", "-", "-")
    row3 = ("", " **type** ", f" `{ftype}` ")
    row4 = ("", "-", "-")
    row5 = ("", " **description** ", f" {doc.pop(0)} ")
    rows = [row1, row2, row3, row4, row5]

    for doc_line in doc:
        rows += [("", "", f" {doc_line} ")]

    rows += [("-", "-", "-")]
    return rows


def replace_character(src_str: str, character: str, substitution: str) -> str:
    index = src_str.rfind(character, 0, -2)
    return src_str[:index] + substitution + src_str[index + 1 :]


def document_launcher(launcher: Type[kloch.launchers.BaseLauncher]) -> str:
    launcher_doc = LauncherDoc.get_launcher_doc(launcher)

    lines = []
    lines += [launcher.name, "_" * len(launcher.name)]
    lines += [""] + [launcher_doc.description] + [""]

    fields = {field.name: field for field in dataclasses.fields(launcher)}

    fields_table: list[RowType] = []
    for field_name, field_doc in launcher_doc.fields.items():
        required = field_name in launcher.required_fields
        field = fields[field_name]
        fields_table += create_field_table(
            field=field,
            field_name=field_name,
            field_doc=field_doc,
            required=required,
        )

    header_table = [
        ("-", "-", "-"),
        (" ➡parent ", f" :launchers:{launcher.name} ", ""),
        ("-", "-", "-"),
        (" ⬇key ", "", ""),
        ("=", "=", "="),
    ]
    table = header_table + fields_table

    col_lens = [max([len(row[index]) for row in table]) for index in range(3)]

    table = [enforce_col_length(row, col_lens) for row in table]
    table = unify_columns(table)

    table[0] = replace_character(table[0], "+", "-")
    table[1] = replace_character(table[1], "|", " ")
    table[2] = replace_character(table[2], "+", "-")
    table[3] = replace_character(table[3], "|", " ")

    lines += table
    lines += [""]

    return "\n".join(lines)


def main():
    for launcher in kloch.launchers.get_available_launchers_classes():
        print(document_launcher(launcher))


main()
