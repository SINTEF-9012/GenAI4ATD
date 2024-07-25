import json
from funcy import omit


def extract_prompts_nl(path_prompts_file: str) -> list:
    """
    Extract prompts from a natural language (Markdown) prompts file. Necessitate that the file was created with the
    as_multiple_prompts parameter.
    :param path_prompts_file:
    :return:
    """
    prompts_file = open(path_prompts_file)

    prompts_str = prompts_file.read()

    return prompts_str.split("  \n" +
                             "====  \n")


def extract_prompts_json(path_prompts_file: str, definitions: bool = False) -> list:
    """
    Extract prompts from a JSON prompts file
    :param path_prompts_file:
    :param definitions:
    :return:
    """
    prompts_file = open(path_prompts_file)

    prompts_json: dict = json.loads(prompts_file.read())

    prompts_list: list = []

    # add the context
    # contrary to the NL version, the context in not written in the prompt file
    prompts_list.append("We are working on the architectural technical debt of a project  \n" +
                        "We already analyzed the project and detected architectural smells using other tools.  \n" +
                        "We will give you a list of the smells we detected and their characteristics, in JSON format." +
                        "There is four type of architectural smells, cyclic dependency, hub-like dependency, " +
                        "unstable dependency and god component, in the following data, 'dependency' will be "
                        "abbreviated as 'Dep'.  \n" +
                        "For each smell, we will give you a list of all the components it affects in the project, "
                        "and metrics about them, still in JSON format.  \n" +
                        "Could you provide an explanation for each smell, and based on the data provided, "
                        "how we could remediate to it ?  ")

    if definitions:
        prompts_list.append(
            "Additionaly we will also provides definitions for specifics metrics and smells characteristics" +
            "These definitions are provided by the documentation of the tool that we used to do the analyses of the "
            "architectural technical debt, " +
            "please use these in your explanations and remediations.  \n" +
            "The following JSON objects will be that, don't try to explain anything, just keep that in mind for when "
            "we will give you the smells to analyze.  \n")

    if definitions:
        prompts_list.append(
            str(prompts_json["smells_def"]) + "," +
            str(prompts_json["smell_characteristics_def"]) + "," +
            str(prompts_json["components_metrics_def"])
        )

    prompts_list.append({
        "project_name": prompts_json["project_name"],
        "language": prompts_json["language"]
    })

    prompts_list.append(
        "Now, we will give the list of smells that we got from the analysis tools, each smell will be a separate "
        "prompt. Keep in mind that we want an explanation, " +
        "but most importantly suggestions on how we could fix these problems. Use the metrics in your reflexion.  \n" +
        "As a reminder, the smells will take the format of a JSON object, with its attribute being its id, type, "
        "components it affects, metrics...")

    for s in prompts_json["smells"]:
        prompts_list.append(s)

    prompts_list.append(
        "Finally, based on your analysis, using all the informations that you have now (characteristics, metrics, "
        "definition), " +
        "order the smells that we presented to you, from the one that we should adress in priority to the ones that "
        "are the less importants.  \n" +
        "Use a format similar to this :  \n" +
        "1. [SMELL_ID] - [SMELL_TYPE] : (explanations...)")

    return prompts_list


def extract_prompts_evo(path_prompts_file: str) -> list:
    """
    Extract prompts from a smell track file
    :param path_prompts_file:
    :return:
    """
    prompts_file = open(path_prompts_file)

    prompts_json: list = json.loads(prompts_file.read())

    prompts_list: list = []

    prompts_list.append(
        "We are working on the architectural technical debt of a project. " +
        "We already analyzed the project and detected architectural smells using another tool. " +
        "There is four type of architectural smells, cyclic dependency, hub-like dependency, unstable dependency" +
        "and god component, in the following data, ‘dependency’ will be abbreviated as ‘Dep’. " +
        "The tool calculate the Architectural Technical Debt Index (ATDI) that represents the amount" +
        "of technical debt this smell represent. We analyzed 10 versions of the project, spaning over " +
        "10 years using the tool. We can see what smells remained, disappeared, or appeared. " +
        "We will give you in JSON format each smell detected, the components it affects, and for each version " +
        "it appears in, how the ATDI evoluted (UP, DOWN or SAME), and if applicable, the git diff of the file " +
        "between these two versions. Based on this data, could you explain us, for it smells, what changes " +
        "in the code caused the ATDI to increase or decrease ?")

    for smell in prompts_json:
        prompts_list.append("Now to the next smell, I will give its characteristics before going " +
                            "through its evolution. Do not analyse before I say 'ANALYSE'")
        prompts_list.append(omit(smell, "characteristics_by_version"))
        for version in smell["characteristics_by_version"]:
            prompts_list.append(omit(version, "ATDI_var"))
            if "ATDI_var" in version:
                prompts_list.append("Now to the next version")
                prompts_list.append(omit(version["ATDI_var"], "diffs"))
                if "diffs" in version["ATDI_var"]:
                    for diff in version["ATDI_var"]["diffs"]:
                        prompts_list.append(diff)
                        prompts_list.append("Now ANALYSE, what changes in the code caused the ATDI " +
                                            "to increase or decrease compared to the previous version ?")

    return prompts_list
