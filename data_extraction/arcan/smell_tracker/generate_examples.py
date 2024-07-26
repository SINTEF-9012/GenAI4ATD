import json


def generate_examples_from_file(path: str, number_of_examples=10):
    """
    Write an example file from an existing smell tracker file.
    :param path: The path to the smell tracker file
    :param number_of_examples: The amount of examples to retrieve
    """
    smell_tracker = json.load(open(path, "r"))

    example_smell: list = generate_examples(smell_tracker, number_of_examples)

    example_file = open(path + "_example.json", "w")
    example_file.write(json.dumps(example_smell))


def generate_examples(smell_tracker: list, number_of_examples=10) -> list:
    """
    Retrieve examples from a list of smells tracked across versions.
    :param smell_tracker: The list containing the smells tracked across versions
    :param number_of_examples: The amount of examples to retrieve
    :return: The list of examples
    """
    examples: list = []

    for s in smell_tracker:
        if detect_var(s):  # The smells that are interesting for examples are the smells that varied or appeared
            examples.append(s)
            number_of_examples -= 1
            if number_of_examples == 0:
                break

    return examples


def detect_var(smell: dict) -> bool:
    """
    Detect if a smell has varied or appeared between any of the versions we analysed
    :param smell:
    :return: Whether the smell has varied or appeared
    """
    if len(smell["characteristics_by_version"]) > 1:
        return smell["characteristics_by_version"][1]["ATDI_var"]["variation"] == "UP" or \
            smell["characteristics_by_version"][1]["ATDI_var"]["variation"] == "DOWN"
    else:
        if "ATDI_var" in smell["characteristics_by_version"][0]:
            return smell["characteristics_by_version"][0]["ATDI_var"]["variation"] == "NEW"
