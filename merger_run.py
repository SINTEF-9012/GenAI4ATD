import argparse
import data_extraction.arcan.merger.merger as merger

parser = argparse.ArgumentParser(prog="arcan merger", description="Merge the csv files that Arcan output")
parser.add_argument("input", help="input directory (the arcan output)")
parser.add_argument("output", help="output directory", default="genai4atdOutput/merger-output/")
parser.add_argument("language", help="programming language (JAVA or CSHARP)")
parser.add_argument("-l", "--loc", help="add the full lines of code where each dependency is used", action="store_true")
parser.add_argument("-r", "--repo", help="path to the repository")
parser.add_argument("-o", "--onlyFirstSmell", help="only output the first smell detected", action="store_true")
parser.add_argument("-e", "--examples", help="extract one smell of each kind", action="store_true")

args = parser.parse_args()

input_path: str = args.input
output_path: str = args.output
language: str = args.language.upper()
repo_path: str = args.repo
loc: bool = args.loc
onlyFirstSmell: bool = args.onlyFirstSmell
ex: bool = args.examples

merger.merger(input_path, output_path, language, repo_path, loc, onlyFirstSmell, ex)
