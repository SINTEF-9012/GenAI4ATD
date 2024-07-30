import argparse
import data_extraction.arcan.smell_tracker.smell_tracker as smell_tracker

parser = argparse.ArgumentParser(prog="arcan prompt builder", description="Track smells across versions")
parser.add_argument("input", help="input file (the arcan output)")
parser.add_argument("output", help="output directory", default="genai4atdOutput/smell-track-output/")
parser.add_argument("repo", help="path to the repository")
parser.add_argument("language", help="programming language (JAVA or CSHARP)")
parser.add_argument("-diffs", "--ATDIVarDiffs",
                    help="write the diffs of the components affected by a smell where there is a ATDI variation",
                    action="store_true")
parser.add_argument("-commits", "--ATDIVarCommitHistory",
                    help="Write the commit history of the components affected by a smell where there is a ATDI "
                         "variation", action="store_true")
parser.add_argument("-f", "--filterCommits",
                    help="When writing the commit history, filter the commit again based on their content relative to"
                         "the type of smell", action="store_true")
parser.add_argument("-o", "--onlyLastVersion", help="keeps only the smells present in the last version",
                    action="store_true")
parser.add_argument("-e", "--examples", help="extract some smell as examples", action="store_true")

args = parser.parse_args()

input_path: str = args.input
output_path: str = args.output
repo_path: str = args.repo
language: str = args.language
atdi_var_diffs: bool = args.ATDIVarDiffs
atdi_commits_history: bool = args.ATDIVarCommitHistory
filter_commits : bool = args.filterCommits
onlyLastVersion: bool = args.onlyLastVersion
examples: bool = args.examples

smell_tracker.main(input_path, output_path, repo_path, language, atdi_var_diffs, atdi_commits_history, filter_commits,
                   only_last_ver=onlyLastVersion, number_of_ver=1000, example=examples)
