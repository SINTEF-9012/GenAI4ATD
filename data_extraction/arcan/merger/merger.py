from pathlib import Path

import pandas as pd
import os
import data_extraction.arcan.merger.get_locs as gl
import data_extraction.arcan.merger.generate_examples as examples
import common.file_management as file_management


def merger(input_path: str, output_path: str, language: str, repo_path: str, loc: bool, only_first_smell: bool,
           ex: bool):
    """
    Merge csv files from an Arcan output, write a new csv file to an output folder. Optionally write an examples file.
    :param input_path: Path to the Arcan output directory.
    :param output_path:
    :param language: JAVA or CSHARP
    :param repo_path:
    :param loc: Whether to include the lines of codes using dependencies
    :param only_first_smell: Whether to only include the first smell in the resulting csv file
    :param ex: Whether to write an examples file
    """
    # Retrieving the data
    component_metrics = pd.read_csv(os.path.join(input_path, "component-metrics.csv"), sep=',')
    component_dependencies = pd.read_csv(os.path.join(input_path, "component-dependencies.csv"), sep=',')
    smell_affects = pd.read_csv(os.path.join(input_path, "smell-affects.csv"), sep=',')
    smell_characteristics = pd.read_csv(os.path.join(input_path, "smell-characteristics.csv"), sep=',')

    # Removing the columns that we are not interested in
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

    # Merging the files
    smells = pd.merge(smell_characteristics, smell_affects, how="inner", left_on=["vertexId", "versionId", "project"],
                      right_on=["fromId", "versionId", "project"])

    components_from = pd.merge(component_metrics, component_dependencies, how="inner",
                               left_on=["vertexId", "versionId", "project"],
                               right_on=["fromId", "versionId", "project"],
                               suffixes=("_componentsFrom", "_componentsFromDependencies"))
    components_to = pd.merge(component_metrics, component_dependencies, how="inner",
                             left_on=["vertexId", "versionId", "project"], right_on=["toId", "versionId", "project"],
                             suffixes=("_componentsTo", "_componentsToDependencies"))
    components_all = pd.merge(components_from, components_to, how="inner", left_on=["edgeId", "versionId", "project"],
                              right_on=["edgeId", "versionId", "project"],
                              suffixes=("_componentsFrom", "_componentsTo"))

    components = pd.merge(components_all, smell_affects, how="inner",
                          left_on=["vertexId_componentsFrom", "versionId", "project"],
                          right_on=["toId", "versionId", "project"], suffixes=("_componentsAll", "_smellsAffect"))

    final = pd.merge(smells, components, how="inner", left_on=["edgeId", "versionId", "project"],
                     right_on=["edgeId_smellsAffect", "versionId", "project"], suffixes=("_components", "_smells"))

    # Adding the lines of code
    if loc:
        if repo_path:
            final["Full_LOCS"] = ""
            path_main_package: list = file_management.get_paths_main_packages(repo_path, language)

            for index, row in final.iterrows():
                if not pd.isna(row["LocationList_componentsFrom"]):  # containers don't have a LocationList
                    locs: list = gl.get_locs_all_locations(row["LocationList_componentsFrom"],
                                                           row["name_componentsFrom"], path_main_package, language)

                    full_locs: str = ""
                    for line in locs:
                        full_locs += line[0] + "#" + line[1] + "~"
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

    output_file = Path(os.path.join(output_path, os.path.split(input_path)[-1]) + "-merged.csv")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    final.to_csv(output_file)

    # Generating examples
    if ex:
        examples.generate(str(output_file))
