from camelsplit import camelsplit


def format_column_name(column_name: str) -> str:
    """
    Format column names, that uses camelCase or snake_case to natural language, with spaces
    :param column_name:
    :return: The formatted column name
    """
    column_name_split = column_name.split("_")
    return " ".join(camelsplit(column_name_split[0]))
