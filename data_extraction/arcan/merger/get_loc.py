import linecache
import os
import common.file_management as file_management


def get_loc_all_dependencies(location_list: str, unit: str, path_main_packages: list, language: str):
    if language != "JAVA" and language != "CSHARP":
        raise AttributeError("Language unsupported")

    unit_path: str = file_management.convert_unit_to_path(unit, language)

    dependencies_list: list = location_list.split(";")
    loc_list: list = []

    for d in dependencies_list:
        dependency_tuple: tuple = extract_from_location_list(d)

        loc_list.append(
            (dependency_tuple[0], get_loc_one_dependency(dependency_tuple[1], path_main_packages, unit_path)))

    return loc_list


def extract_from_location_list(location_list: str):
    result: list = location_list.split("#")
    dependency_name: str = result[0]
    lines: list = list(map(int, result[1:3]))
    return dependency_name, lines


def get_loc_one_dependency(lines_number: list, path_main_packages: list, unit_path: str):
    lines: str = ""

    for main_package in path_main_packages:
        if os.path.isfile(main_package + unit_path):
            for i in range(lines_number[1] - lines_number[0] + 1):
                lines += linecache.getline(main_package + unit_path, lines_number[0] + i)

    return lines
