import json


def generate_examples_from_file(path: str, number_of_examples=10):
    smell_tracker = json.load(open(path, "r"))

    example_smell: list = generate_examples(smell_tracker, number_of_examples)

    example_file = open(path + "_example.json", "w")
    example_file.write(json.dumps(example_smell))


def generate_examples(smell_tracker: list, number_of_examples=10):
    examples: list = []

    for s in smell_tracker:
        if detect_var(s):
            examples.append(s)
            number_of_examples -= 1
            if number_of_examples == 0:
                break

    return examples


def detect_var(smell):
    if len(smell["characteristics_by_version"]) > 1:
        return smell["characteristics_by_version"][1]["ATDI_var"]["variation"] == "UP" or \
            smell["characteristics_by_version"][1]["ATDI_var"]["variation"] == "DOWN"
    else:
        if "ATDI_var" in smell["characteristics_by_version"][0]:
            return smell["characteristics_by_version"][0]["ATDI_var"]["variation"] == "NEW"
