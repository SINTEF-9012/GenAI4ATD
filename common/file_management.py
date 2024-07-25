import platform
import os

if platform.system() == "Windows":
    separator: str = "\\"
else:
    separator: str = "/"


def get_paths_main_packages(repo_path: str, language: str):
    paths_main_packages: list = []

    if language == "JAVA":
        for root, dirs, files in os.walk(repo_path):
            for name in dirs:
                if ((os.path.join(root, name).endswith(os.path.join("main", "java"))) or
                        (os.path.join(root, name).endswith(os.path.join("test", "java")))):
                    paths_main_packages.append(os.path.join(root, name) + separator)
    else:
        raise AttributeError("Language unsupported")

    return paths_main_packages


def convert_component_to_path(component: str, language: str, is_unit: bool):
    unit_path: str = component.replace(".", separator)

    if is_unit:
        if language == "JAVA":
            unit_path += ".java"
        elif language == "CSHARP":
            unit_path += ".cs"

    return unit_path


def get_full_path(component: str, repo_path: str, language: str, is_unit: bool):
    component = convert_component_to_path(component, language, is_unit)
    path_main_packages: list = get_paths_main_packages(repo_path, language)
    for main_package in path_main_packages:
        if os.path.isfile(main_package + component) or os.path.isdir(main_package + component):
            return main_package + component


def get_unit_list_from_container_list(containers: str, repo_path: str, language: str):
    container_list = get_components_as_list(containers)
    unit_list: list = []

    for container in container_list:
        container_path: str = get_full_path(container, repo_path, language, False)
        if container_path is not None:
            for file in os.listdir(container_path):
                unit_list.append(os.path.join(container_path, file))

    return unit_list


def get_components_as_list(components: str):
    components = components.replace(" ", "")
    components = components[1:-1]
    return components.split(",")


def get_components_as_paths_list(components: str, repo_path: str, language: str, is_unit: bool):
    components_list = get_components_as_list(components)
    paths_list: list = []

    for component in components_list:
        paths_list.append(get_full_path(component, repo_path, language, is_unit))

    return paths_list
