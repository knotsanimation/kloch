from kloch.launchers._context import _FIELDS_MAPPING

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


def generate_table():
    fields_table: list[RowType] = []
    for prop_name, field in _FIELDS_MAPPING.items():
        field_doc = field.metadata["doc"]
        fields_table += [
            (
                f" ``{prop_name}`` ",
                f" {field_doc['value']} ",
                f" {field_doc['description']} ",
            ),
            ("-", "-", "-"),
        ]

    header_table = [
        ("-", "-", "-"),
        (" property name ", " property value ", " description "),
        ("=", "=", "="),
    ]
    table = header_table + fields_table

    col_lens = [max([len(row[index]) for row in table]) for index in range(3)]

    table = [enforce_col_length(row, col_lens) for row in table]
    table = unify_columns(table)

    return "\n".join(table)


print(generate_table())
