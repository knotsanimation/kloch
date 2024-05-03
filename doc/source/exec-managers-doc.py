"""
Build an automatic rst documentation including a table from a dataclass object.

All the information is extracted from the code of the dataclass.
"""

import dataclasses
import typing
from typing import Type

import kenvmanager.managers


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
) -> list[RowType]:
    required = "yes" if required else "no"

    if hasattr(field.type, "__metadata__"):
        doc = list(field.type.__metadata__)
        ftype = field.type.__origin__
    else:
        doc = [""]
        ftype = field.type

    ftype = str(ftype).replace("typing.", "")

    row1 = (f" ``{field.name}`` ", " **required** ", f" {required} ")
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


def document_manager(manager: Type[kenvmanager.managers.PackageManagerBase]) -> str:
    lines = []
    lines += [manager.name(), "_" * len(manager.name())]
    lines += [""] + manager.doc() + [""]

    fields = dataclasses.fields(manager)

    fields_table: list[RowType] = []
    for field in fields:
        required = field.name in manager.required_fields
        fields_table += create_field_table(field=field, required=required)

    header_table = [
        ("-", "-", "-"),
        (" ≻ parent ", f" :managers:{manager.name()} ", ""),
        ("-", "-", "-"),
        (" ∨ key ", "", ""),
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
    for manager in kenvmanager.managers.get_available_managers_classes():
        print(document_manager(manager))


main()
