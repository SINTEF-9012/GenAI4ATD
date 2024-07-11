from camelsplit import camelsplit


def format_column_name(column_name: str):
    column_name_splitted = column_name.split("_")
    return " ".join(camelsplit(column_name_splitted[0]))


def get_components_as_list(components: str):
    components = components.replace(" ", "")
    components = components[1:-1]
    return components.split(",")