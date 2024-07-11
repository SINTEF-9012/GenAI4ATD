import pandas as pd


def generate(output_path: str):
    output = pd.read_csv(output_path)

    examples_list = []

    examples_done = {"UNIT": ["cyclicDep", "hubLikeDep", "unstableDep", "godComponent"],
                     "CONTAINER": ["cyclicDep", "hubLikeDep", "unstableDep", "godComponent"]}
    for index, row in output.iterrows():
        if row["smellType"] in examples_done[row["AffectedComponentType"]] or row["vertexId"] == smell_id:
            smell_id = row["vertexId"]
            examples_list.append(row)

            if row["smellType"] in examples_done[row["AffectedComponentType"]]:
                examples_done[row["AffectedComponentType"]].remove(row["smellType"])

    examples_table = pd.DataFrame(examples_list, columns=output.columns)
    examples_table.to_csv(output_path + "-examples.csv")
