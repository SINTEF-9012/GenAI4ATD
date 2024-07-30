import os


def get_paths_main_packages(repo_path: str, language: str) -> list:
    """
    Return a list of the main and test packages folders inside a repository
    :param repo_path:
    :param language: JAVA or CSHARP
    :return: A list of the main and test packages
    """
    paths_main_packages: list = []

    if language == "JAVA":
        for root, dirs, files in os.walk(repo_path):
            for name in dirs:
                if ((os.path.join(root, name).endswith(os.path.join("main", "java"))) or
                        (os.path.join(root, name).endswith(os.path.join("test", "java")))):
                    paths_main_packages.append(os.path.join(root, name))
    else:
        raise AttributeError("Language unsupported")

    return paths_main_packages


def convert_component_to_path(component: str, language: str, is_unit: bool) -> str:
    """
    Convert a component ie "org.myproject.mypackage.MyClass" to a proper path
    :param component:
    :param language: JAVA or CSHARP
    :param is_unit: Whether the component is unit or a container
    :return: The path to the component
    """
    unit_path: str = component.replace(".", os.path.sep)

    if is_unit:
        if language == "JAVA":
            unit_path += ".java"
        elif language == "CSHARP":
            unit_path += ".cs"

    return unit_path


def get_full_path(component: str, repo_path: str, language: str, is_unit: bool, paths_main_packages: list) -> str:
    """
    Get the full path of a component
    :param component:
    :param repo_path:
    :param language: JAVA or CSHARP
    :param is_unit: Whether the component is unit or a container
    :param paths_main_packages: A list of the main and test packages
    :return: The full path to the component
    """
    component = convert_component_to_path(component, language, is_unit)

    for main_package in paths_main_packages:
        if (os.path.isfile(os.path.join(main_package, component)) or
                os.path.isdir(os.path.join(main_package, component))):
            return os.path.join(main_package, component)


def get_unit_list_from_container_list(containers: str, repo_path: str, language: str,
                                      paths_main_packages) -> list:
    """
    Retrieve all the unit contained in the containers from the list
    :param containers:
    :param repo_path:
    :param language: JAVA or CSHARP
    :param paths_main_packages: A list of the main and test packages
    :return: The list of all the units
    """
    container_list = get_components_as_list(containers)
    unit_list: list = []

    for container in container_list:
        container_path: str = get_full_path(container, repo_path, language, False, paths_main_packages)
        if container_path is not None:
            for file in os.listdir(container_path):
                unit_list.append(os.path.join(container_path, file))

    return unit_list


def get_components_as_list(components: str) -> list:
    """
    Convert a string of components ie "[org.myproject.mypackage.MyClass, org.myproject.mypackage.MyOtherClass]" to a
    proper list
    :param components:
    :return: The list of components
    """
    components = components.replace(" ", "")
    components = components[1:-1]
    return components.split(",")


def get_components_as_paths_list(components: str, repo_path: str, language: str, is_unit: bool,
                                 paths_main_packages: list) -> list:
    """
    Return a list of the paths to the components given in parameter
    :param components:
    :param repo_path:
    :param language: JAVA or CSHARP
    :param is_unit: Whether the components are units or containers
    :param paths_main_packages: A list of the main and test packages
    :return:
    """
    components_list = get_components_as_list(components)
    paths_list: list = []

    for component in components_list:
        paths_list.append(get_full_path(component, repo_path, language, is_unit, paths_main_packages))

    return paths_list
