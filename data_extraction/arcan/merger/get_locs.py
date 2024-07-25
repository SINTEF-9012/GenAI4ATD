import linecache
import os
import common.file_management as file_management


def get_locs_all_locations(locations_list_str: str, unit: str, path_main_packages: list, language: str) -> list:
    """
    Retrieve the lines of codes using a dependencies in a unit using a location_list
    :param locations_list_str: LocationList as in Arcan output (component-dependencies.csv)
    :param unit:
    :param path_main_packages:
    :param language: JAVA or CSHARP
    :return:
    """
    if language != "JAVA" and language != "CSHARP":
        raise AttributeError("Language unsupported")

    unit_path: str = file_management.convert_component_to_path(unit, language, True)

    locations_list: list = locations_list_str.split(";")
    loc_list: list = []

    for d in locations_list:
        dependency_tuple: tuple = extract_from_location(d)

        loc_list.append(
            (dependency_tuple[0], get_locs_one_location(dependency_tuple[1], path_main_packages, unit_path)))

    return loc_list


def extract_from_location(location: str) -> tuple[str, list]:
    """
    Extract the type of dependency and the lines number from a location string
    :param location: Location as in Arcan output (component-dependencies.csv)
    :return: The type of dependency and a list of lines number
    """
    result: list = location.split("#")
    dependency_name: str = result[0]
    lines: list = list(map(int, result[1:3]))
    return dependency_name, lines


def get_locs_one_location(lines_number: list, path_main_packages: list, unit_path: str) -> str:
    """
    Retrieve the lines of code at a specific location
    :param lines_number:
    :param path_main_packages:
    :param unit_path:
    :return: The lines of code
    """
    lines: str = ""

    for main_package in path_main_packages:
        if os.path.isfile(main_package + unit_path):
            for i in range(lines_number[1] - lines_number[0] + 1):
                lines += linecache.getline(main_package + unit_path, lines_number[0] + i)

    return lines
