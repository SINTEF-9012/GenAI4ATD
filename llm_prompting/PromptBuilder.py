from abc import ABC, abstractmethod
import pandas as pd
import json
from common.utils import format_column_name
from pathlib import Path


def define_file_name(prompt_output: str, write_dependencies_bool: bool = False, write_loc: bool = False,
                     as_multiple_prompts: bool = False, write_def: bool = False) -> str:
    """
    Define the output file name from the parameters chosen
    :param prompt_output:
    :param write_dependencies_bool: Whether to add the dependencies of each component in the prompt
    :param write_loc: Whether to write the lines of code using dependencies in the prompt
    :param as_multiple_prompts: Whether to add separation characters so the output file can be parsed into multiple
    prompts at a later time. Actually only useful for the Markdown prompt builder
    :param write_def: Whether to write the definition for smells and metrics in the prompt. Actually only useful
    for the JSON prompt builder, as we abandoned using natural language at this point
    :return:
    """
    file_name_builder: list[str] = [prompt_output]

    if write_def:
        file_name_builder.append("defs/")
    else:
        file_name_builder.append("nodefs/")

    if as_multiple_prompts:
        file_name_builder.append('multiple-queries/')

    file_name_builder.append('prompt')

    if write_dependencies_bool:
        file_name_builder.append("_with_dependencies")

    if write_loc:
        file_name_builder.append("_and_LOCS")

    return "".join(file_name_builder)


class PromptBuilder(ABC):
    """
    Base class for all prompt builders
    """

    smell_characteristics: list = ["ATDI", "Severity", "Size", "LOCDensity", "NumberOfEdge"]
    components_metrics: list = ["AbstractnessMetric_componentsFrom", "ChangeHasOccurred_componentsFrom",
                                "LinesOfCode_componentsFrom", "FanIn_componentsFrom", "FanOut_componentsFrom",
                                "InstabilityMetric_componentsFrom", "NumberOfChildren_componentsFrom",
                                "PageRank_componentsFrom"]
    dependencies_infos: list = []

    # Definitions are taken from the Arcan documentation https://docs.arcan.tech/2.9.0/
    smells_def: dict = {
        "cyclicDep": {
            "definition": "When two or more architectural components are involved in a chain of relationships.The architectural components involved in a Cyclic Dependency are hard to release, hard to maintain, hard to reuse in isolation. The smell violates the Acyclic Dependencies Principle defined by R. C. Martin.",
            "detectionStrategy": "The detection of Cyclic Dependency (CD) in Arcan is done using the dependency graph of the system that we are analysing, i.e., the graph representation of the system's architectural components and dependencies. CD is detected on both units and containers (e.g., classes and packages in Java). A cycle is detected whenever two or more architectural components depend upon each other in a cycle. Arcan detects CD on different types of components and uses well-known cycle detection algorithm to identify components that belong to the same cycles. The algorithms supported by Arcan are, Sedgewick-Wayne algorithm, a simple DFS-based algorithm to detect cycles. More information here. This is the default implementation used by Arcan. Tarjan's strongly connected components (SCC) algorithm. Laval-Falleri's shortest cycles algorithm, this is the default implementation used by Arcan for Layered Cyclic Dependencies."
        },
        "godComponent": {
            "definition": "This smell occurs when an architectural component is excessively large in terms of LOC (Lines Of Code). The architectural component affected by God Component, centralizes logic, has low cohesion withim, has increasing complexity. The smell violates the Modularity Principle defined by R. C. Martin.",
            "detectionStrategy": "The detection of the God component (GC) smell is done using the size, in terms of number of lines of code, of the system analysed. GC is detected at the container-level (e.g., packages in Java). The smell detection is based on Lippert and Rook's definition of GC, which is based on the total number of lines of code contained in the package. While Lippert and Rook suggest to use a fixed threshold of 27.000 lines of code to detect the smell, our approach is more sophisticated and data-driven. We calculate the detection threshold dynamically. The threshold is calculated as LinesOfCode = Max(LinesOfCode_System, LinesOfCode_Benchmark) where each individual LinesOfCode_* is calculated using frequency analysis of the metric LinesOfCode computed on the system and the benchmark separately. The metric is calculated as the total number of lines of code of all the elemnts belonging to a specific component."
        },
        "hubLikeDep": {
            "definition": "When an architectural component has (outgoing and ingoing) dependencies with a large number of other components. The component affected by the smell centralizes logic, is a unique point of failure, favors change ripple effects. The smell violates the Modularity Principle defined by R. C. Martin.",
            "detectionStrategy": "The detection of Hublike Dependency (HL) in Arcan is done starting from the dependency graph of the system under analysis. HL, or simply 'hub', is detected on both units and containers (e.g., classes and packages in Java). A hub is detected whenever a component in the system has 'too many' incoming and outgoing dependencies (FanIn and FanOut, respectively). The 'too many' is calculated using a dynamic threshold that is based on both a benchmark of 100+ systems (from the Qualitas Corpus) and the system under analysis. This allows us to not pick the the threshold arbitrarily, but instead use a data-driven approach. In particular, the threshold is calculated as Threshold = Max(Threshold_System, Threshold_Benchmark) where each individual Threshold_* is calculated using frequency analysis of the metric TotalDeps computed on the system and the benchmark separately, where TotalDeps(x) = FanIn(x) + FanOut(x) for all components x."
        },
        "unstableDep": {
            "definition": "Describes an architectural component that depends on other components that are less stable than itself. Instability (proneness to change) is measured using R. C. Martin's formula. The component affected by the smell can, favors change ripple effects, be subjected to frequent changes. The smell violates the Stable Dependency Principle defined by R. C. Martin.",
            "detectionStrategy": "The detection of Unstable dependency (UD) is done using the dependency graph of the system under analysis. UD is detected at the container-level (e.g., packages in Java) only, whenever a container depends on other containers that are less stable than itself. By Instability we mean R.C. Martin's Instability metric, whose definition can be found here. Instability calculates how easy it is for a container to change because of other containers (e.g. packages) in the system have changed. Namely, it is a measure of the risk of ripple change effects. The detection rule is the following: Intability(x) > Instability(y) + delta for all containers y such that x depends upon, and x is the container (e.g., package) that we are checking for the presence of UD."
        }
    }

    smell_characteristics_def: dict = {
        "ATDI": "Architectural Technical Debt Index : The amount of Technical Debt caused by the single Architectural Smell. Higher is worse.",
        "Severity": "The estimate of how much the Architectural Smell is critical for the project. Ranges from 1 to 10 where 10 is the worst possible case. It is based on the smell's characteristics (such as size and shape) and it is computed thanks to a proprietary machine learning model trained on manually-classified examples.",
        "Size": "The number of Architectural Components (containers or units) affected by the Architectural Smell."
    }

    components_metrics_def: dict = {
        "AbstractnessMetric": "The number of abstract classes (and interfaces) divided by the total number of types in a package. This metric range is [0,1], where 0 indicates a completely concrete package and 1 indicates a completely abstract package.",
        "InstabilityMetric": "The package's resilience to change. This metric range is [0,1], where 0 indicates that the package is completely stable and 1 completely unstable. This metric range is [0,1], where 0 indicates that the package is directly on the main sequence whereas 1 indicates that the package is as far away as possible from the main sequence. Small numbers are indicators of good packaging design.",
        "DistanceFromMainSequence": "The package's balance between abstractness and stability.",
        "FanIn": "The number of ingoing dependences of a class.",
        "FanOut": "The number of outgoing dependences of a class.",
        "LinesOfCode": "The number of lines of code of a given class or package. The metric does not count blank lines and commented lines.",
        "ChangeHasOccured": "Given the project history (Git commits), it measures whether a class or package has changed or not in the current commit with respect to the previous commit.",
        "CodeChurn": "Given the history of a project (git commits), it is the sum of added lines of code, deleted lines, and twice the changed lines since the last commit for a given class or package.",
        "PageRank": "Estimates whether an architectural smell is located in an important part of the project, where the importance is evaluated according to how many parts of a project depend on the one involved in the architectural smell. The metric is based on the one implemented by Brin and Page.",
        "CouplingBetweenObjects": "Number of classes to which a class is coupled, that is the number of classes that a class references. The coupling beetween classes should be low, otherwise it will difficult to make changes to the system without change a lot of classes.",
        "DepthofInheritance": "The depth of inheritance tree (DIT) is a code metric that is specific to object-oriented programming. It measures the maximum length between a node and the root node in a class hierarchy. The minimum value of DIT for a class is 1. The metric range is [0, infinite]. 0 indicates a root. The minimum value for a class is 1. A value > 1 indicates that there is code reuse through inheritance. If there is a majority of values below 2, it may represent poor exploitation of the advantages of OO design and inheritance. It is recommended a maximum value of 5 since deeper trees constitute greater design complexity.",
        "NumberOfChildren": "The number of classes inheriting from a given class."
    }

    @abstractmethod
    def build_prompt(self, arcan_output_path: str, language: str, prompt_output: str,
                     write_dependencies_bool: bool = False, write_loc: bool = False, as_multiple_prompts: bool = False,
                     write_def: bool = False):
        """
        Build the prompt and write it to the output file
        :param arcan_output_path:
        :param language: JAVA or CSHARP
        :param prompt_output:
        :param write_dependencies_bool: Whether to add the dependencies of each component in the prompt
        :param write_loc: Whether to write the lines of code using dependencies in the prompt
        :param as_multiple_prompts: Whether to add separation characters so the output file can be parsed into multiple
        prompts at a later time. Actually only useful for the Markdown prompt builder
        :param write_def: Whether to write the definition for smells and metrics in the prompt. Actually only useful
        for the JSON prompt builder, as we abandoned using natural language at this point
        """
        pass

    @abstractmethod
    def write_smell_characteristics(self, row):
        pass

    @abstractmethod
    def write_component_metrics(self, row):
        pass

    @abstractmethod
    def write_dependencies(self, row, write_locs: bool):
        pass


class PromptBuilderNL(PromptBuilder):
    string_builder: list = []
    project_name: str = ""
    smell_id: int = 0
    component_id: int = 0
    language: str = ""

    def build_prompt(self, arcan_output_path: str, language: str, prompt_output: str,
                     write_dependencies_bool: bool = False, write_loc: bool = False, as_multiple_prompts: bool = False,
                     write_def: bool = False):
        arcan_output = pd.read_csv(arcan_output_path)

        self.string_builder = []

        self.project_name = arcan_output.iloc[0]["project"]
        self.smell_id = 0
        self.component_id = 0

        self.language = language

        # add the context
        self.string_builder.append(
            "We are working on the architectural technical debt of the " + self.language + " project called " + self.project_name + "  \n" +
            "We already analyzed the project and detected architectural smells using other tools. " +
            "We will give you a list of the smells we detected and their characteristics. " +
            "There is four type of architectural smells, cyclic dependency, hub-like dependency, unstable dependency and god component," +
            " in the following list, 'dependency' will be abbreviated as 'Dep'." +
            "For each smell, we will give you a list of all the components it affects in the project, and metrics about them. " +
            "  \n" +
            "Could you provide an explanation for each smell, and based on the data provided, eventually how we could remediate to it ?  \n"
        )

        if write_dependencies_bool:
            self.string_builder.append("For each component affected, we will give you a list of its dependencies  \n")

        if write_def:
            self.string_builder.append(
                "Additionaly we will also provides definitions for specifics metrics and smells characteristics" +
                "These definitions are provided by the documentation of the tool that we used to do the analyses of the architectural technical debt, " +
                "please use these in your explanations and remediations.  \n" +
                "Don't try to explain anything for now, just keep that in mind for when we will give you the smells to analyze.  \n")

            if as_multiple_prompts:
                self.string_builder.append("  \n" +
                                           "====  \n")

            definitions: list = [self.smells_def, self.smell_characteristics_def, self.components_metrics_def]

            for d in definitions:
                for k in d.keys():
                    self.string_builder.append(str(k) + " : " + str(d[k]) + "  \n")

        if not as_multiple_prompts:
            self.string_builder.append("  \n  \n" +
                                       "Here is a list of the smells we detected :  \n")

        # for each smell
        for index, row in arcan_output.iterrows():
            if row["vertexId"] != self.smell_id:
                if as_multiple_prompts:
                    self.string_builder.append("  \n" +
                                               "====  \n")

                self.smell_id = row["vertexId"]

                # smell characteristics
                self.write_smell_characteristics(row)

                self.string_builder.append(".  \n" +
                                           "Here is a list of the components it affects :  \n")

            if row["vertexId_componentsFrom"] != self.component_id:
                self.component_id = row["vertexId_componentsFrom"]

                # component metrics
                self.write_component_metrics(row)

                self.string_builder.append(".  \n")

                if write_dependencies_bool:
                    self.string_builder.append("Here is a list of its dependencies :  \n")

            if write_dependencies_bool:
                # dependencies
                self.write_dependencies(row, write_loc)

        prompt_output = define_file_name(prompt_output, write_dependencies_bool, write_loc, as_multiple_prompts,
                                         write_def)

        file = Path(prompt_output + ".md")
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text("".join(self.string_builder))

    def write_smell_characteristics(self, row):
        self.string_builder.append("* Smell " + str(self.smell_id) + ".  \n"
                                                                     "This smell is a " + format_column_name(
            row["smellType"]) + ", ")

        for column in row.keys():
            if column in self.smell_characteristics:
                self.string_builder.append("its " + format_column_name(column) + " is " + str(row[column]) + ", ")

    def write_component_metrics(self, row):
        self.string_builder.append(
            "     * Component " + str(self.component_id) + " named " + row["name_componentsFrom"] + " it is a " + row[
                "AffectedConstructType"] + ".  \n")

        for column in row.keys():
            if column in self.components_metrics:
                self.string_builder.append("its " + format_column_name(column) + " is " + str(row[column]) + ", ")

    def write_dependencies(self, row, write_locs: bool):
        self.string_builder.append("         * Dependency " + str(row["vertexId_componentsTo"]) + " named " + row[
            "name_componentsTo"] + ".  \n")

        if write_locs and not pd.isna(row["Full_LOCS"]):
            self.string_builder.append(
                "Here is the type of usage of the dependency, and the lines of codes where it is used :  \n")

            dependencies_list: list = row["Full_LOCS"].split("~")

            for d in dependencies_list:
                dependency: list = d.split("#")

                self.string_builder.append("             * " + dependency[0] + " :  \n" +
                                           "```" + self.language + "\n" +
                                           dependency[1] + "\n" +
                                           "```\n")


class PromptBuilderJSON(PromptBuilder):
    def build_prompt(self, arcan_output_path: str, language: str, prompt_output: str,
                     write_dependencies_bool: bool = False, write_loc: bool = False, as_multiple_prompts: bool = False,
                     write_def: bool = False):
        arcan_output = pd.read_csv(arcan_output_path)

        json_builder: dict = {
            "project_name": arcan_output.iloc[0]["project"],
            "language": language
        }

        smell_id: int = 0
        smell: dict = {}
        component_id: int = 0
        component: dict = {}

        smells_list: list = []

        # for each smell
        for index, row in arcan_output.iterrows():
            if row["vertexId"] != smell_id:

                # during the first iteration, the dict will be empty, we don't want to have it in the final result
                if smell:
                    smells_list.append(smell)
                    smell = {}

                smell_id = row["vertexId"]

                smell = {
                    "id": row["vertexId"],
                    "type": row["smellType"],
                    "characteristics": self.write_smell_characteristics(row),
                    "components_affected": []
                }

            if row["vertexId_componentsFrom"] != component_id:

                # same as above
                if component:
                    smell["components_affected"].append(component)
                    component = {}

                component_id = row["vertexId_componentsFrom"]

                component = {
                    "id": row["vertexId_componentsFrom"],
                    "name": row["name_componentsFrom"],
                    "type": row["AffectedConstructType"],
                    "metrics": self.write_component_metrics(row)
                }

                if write_dependencies_bool:
                    component["dependencies"] = []

            if write_dependencies_bool:
                component["dependencies"].append(self.write_dependencies(row, write_loc))

        json_builder["smells"] = smells_list

        if write_def:
            json_builder["smells_def"] = self.smells_def
            json_builder["smell_characteristics_def"] = self.smell_characteristics_def
            json_builder["components_metrics_def"] = self.components_metrics_def

        prompt_output = define_file_name(prompt_output, write_dependencies_bool, write_loc, as_multiple_prompts,
                                         write_def)

        file = Path(prompt_output + ".json")
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(json.dumps(json_builder))

    def write_smell_characteristics(self, row) -> dict:
        smell_characteristics: dict = {}

        for column in row.keys():
            if column in self.smell_characteristics:
                smell_characteristics[format_column_name(column)] = row[column]

        return smell_characteristics

    def write_component_metrics(self, row) -> dict:
        component_metrics: dict = {}

        for column in row.keys():
            if column in self.components_metrics:
                component_metrics[format_column_name(column)] = row[column]

        return component_metrics

    def write_dependencies(self, row, write_locs: bool) -> dict:
        dependency: dict = {
            "id": row["vertexId_componentsTo"],
            "name": row["name_componentsTo"],
        }

        if write_locs and not pd.isna(row["Full_LOCS"]):
            dependencies_list: list = row["Full_LOCS"].split("~")

            dependency["calls"] = []
            for d in dependencies_list:
                d_split: list = d.split("#")
                dependency["calls"].append(
                    {
                        "type": d_split[0],
                        "LOCs": d_split[1]
                    }
                )

        return dependency
