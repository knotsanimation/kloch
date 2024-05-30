"""
Build an automatic rst documentation including a table from a dataclass object.

All the information is extracted from the code of the dataclass.
"""

import dataclasses
from typing import Type

import kloch.launchers


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
    required: bool,
    launcher: Type[kloch.launchers.BaseLauncherSerialized],
) -> list[RowType]:
    field_name = field.default
    field_doc = field.metadata["description"]
    required = "yes" if required else "no"

    doc = field_doc.split("\n")

    # typing.Annotated
    if hasattr(field.type, "__metadata__"):
        ftype = field.type.__origin__
    else:
        ftype = field.type

    ftype = str(ftype).replace("typing.", "")

    rows = [
        (f" .. _format-{launcher.identifier}-{field_name}: ", "", ""),
        (f"", "", ""),
        (f" ``{field_name}`` ", " **required** ", f" {required} "),
        ("-", "-", "-"),
        ("", " **type** ", f" `{ftype}` "),
        ("", "-", "-"),
        ("", " **description** ", f" {doc.pop(0)} "),
    ]

    for doc_line in doc:
        rows += [("", "", f" {doc_line} ")]

    rows += [("-", "-", "-")]
    return rows


def replace_character(src_str: str, character: str, substitution: str) -> str:
    index = src_str.rfind(character, 0, -2)
    return src_str[:index] + substitution + src_str[index + 1 :]


def document_launcher(launcher: Type[kloch.launchers.BaseLauncherSerialized]) -> str:
    lines = []
    lines += [launcher.identifier, "_" * len(launcher.identifier)]
    lines += [""] + [launcher.description] + [""]

    fields_table: list[RowType] = []
    for field in launcher.fields.iterate():
        required = field.metadata["required"]
        fields_table += create_field_table(
            field=field,
            required=required,
            launcher=launcher,
        )

    header_table = [
        ("-", "-", "-"),
        (" ➡parent ", f" :launchers:{launcher.identifier} ", ""),
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
    for launcher in kloch.launchers.get_available_launchers_serialized_classes():
        print(document_launcher(launcher))


main()
