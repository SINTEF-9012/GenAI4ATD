from camelsplit import camelsplit


def format_column_name(column_name: str):
    column_name_splitted = column_name.split("_")
    return " ".join(camelsplit(column_name_splitted[0]))
