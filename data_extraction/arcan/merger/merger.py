import pandas as pd
import os
import get_loc as gl
import generate_examples as examples
import common.file_management as file_management


def merger(input_path: str, output_path: str, language: str, repo_path: str, loc: bool, only_first_smell: bool, ex: bool):
    # Data retrieve
    component_metrics = pd.read_csv(input_path + "component-metrics.csv", sep=',')
    component_dependencies = pd.read_csv(input_path + "component-dependencies.csv", sep=',')
    smell_affects = pd.read_csv(input_path + "smell-affects.csv", sep=',')
    smell_characteristics = pd.read_csv(input_path + "smell-characteristics.csv", sep=',')

    # Cleaning
    columns_to_remove = [["versionIndex", "versionDate"],  # common
                         ["simpleName", "ComponentType", "IsNested", "constructType", "filePathReal",
                          "filePathRelative"],
                         # component-metrics
                         ["from", "to"],  # component-dependencies
                         ["vertexLabel"],  # smell-characteristics
                         ["from", "to"]  # smell-affects
                         ]

    component_metrics.drop(columns=columns_to_remove[0] + columns_to_remove[1], inplace=True)
    component_dependencies.drop(columns=columns_to_remove[0] + columns_to_remove[2], inplace=True)
    smell_characteristics.drop(columns=columns_to_remove[0] + columns_to_remove[3], inplace=True)
    smell_affects.drop(columns=columns_to_remove[0] + columns_to_remove[4], inplace=True)

    # Merge
    smells = pd.merge(smell_characteristics, smell_affects, how="inner", left_on=["vertexId", "versionId", "project"],
                      right_on=["fromId", "versionId", "project"])

    componentsFrom = pd.merge(component_metrics, component_dependencies, how="inner",
                              left_on=["vertexId", "versionId", "project"], right_on=["fromId", "versionId", "project"],
                              suffixes=("_componentsFrom", "_componentsFromDependencies"))
    componentsTo = pd.merge(component_metrics, component_dependencies, how="inner",
                            left_on=["vertexId", "versionId", "project"], right_on=["toId", "versionId", "project"],
                            suffixes=("_componentsTo", "_componentsToDependencies"))
    componentsAll = pd.merge(componentsFrom, componentsTo, how="inner", left_on=["edgeId", "versionId", "project"],
                             right_on=["edgeId", "versionId", "project"], suffixes=("_componentsFrom", "_componentsTo"))

    components = pd.merge(componentsAll, smell_affects, how="inner",
                          left_on=["vertexId_componentsFrom", "versionId", "project"],
                          right_on=["toId", "versionId", "project"], suffixes=("_componentsAll", "_smellsAffect"))

    final = pd.merge(smells, components, how="inner", left_on=["edgeId", "versionId", "project"],
                     right_on=["edgeId_smellsAffect", "versionId", "project"], suffixes=("_components", "_smells"))

    # Add LOC
    if loc:
        if repo_path:
            final["Full_LOCS"] = ""
            path_main_package: list = file_management.get_paths_main_packages(repo_path, language)

            for index, row in final.iterrows():
                if not pd.isna(row["LocationList_componentsFrom"]):
                    locs: tuple = gl.get_loc_all_dependencies(row["LocationList_componentsFrom"],
                                                              row["name_componentsFrom"], path_main_package, language)

                    full_locs: str = ""
                    for l in locs:
                        full_locs += l[0] + "#" + l[1] + "~"
                    final.at[index, "Full_LOCS"] = full_locs[:-1]
        else:
            raise AttributeError("missing repo path, use --repo or -r")

    # Keeping only the first smell
    if only_first_smell:
        first_smell = final.iloc[0]["vertexId"]

        for index, row in final.iterrows():
            if row["vertexId"] != first_smell:
                final = final[:index]
                break

    output_file: str = output_path + "-" + os.path.split(input_path)[-1] + "-merged.csv"
    final.to_csv(output_file)

    # Generate examples
    if ex:
        examples.generate(output_file)
