import json


def generate_examples_from_file(path: str, number_of_examples=10):
    smell_tracker = json.load(open(path, "r"))

    example_smell: list = generate_examples(smell_tracker, number_of_examples)

    example_file = open(path + "_example.json", "w")
    example_file.write(json.dumps(example_smell))


def generate_examples(smell_tracker: list, number_of_examples=10):
    examples: list = []

    for s in smell_tracker:
        if len(s["characteristics_by_version"]) > 1 and (
                s["characteristics_by_version"][1]["ATDI_var"]["variation"] == "UP" or
                s["characteristics_by_version"][1]["ATDI_var"]["variation"] == "DOWN" or
                s["characteristics_by_version"][1]["ATDI_var"]["variation"] == "NEW"):
            examples.append(s)
            number_of_examples -= 1
            if number_of_examples == 0:
                break

    return examples
