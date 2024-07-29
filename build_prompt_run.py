import argparse
import os.path
import llm_prompting.PromptBuilder as PromptBuilder

parser = argparse.ArgumentParser(prog="arcan prompt builder", description="Build prompts based on Arcan Merger output")
parser.add_argument("input", help="input file (the arcan merger output)")
parser.add_argument("output", help="output directory", default="genai4atdOutput/prompts-output/")
parser.add_argument("language", help="programming language (JAVA or CSHARP)")
parser.add_argument("-dep", "--dependencies", help="write the components dependencies", action="store_true")
parser.add_argument("-loc", "--linesofcodes", help="write the lines of codes that creates dependencies",
                    action="store_true")
parser.add_argument("-def", "--definitions",
                    help="write the definitions of the metrics as defined by Arcan",
                    action="store_true")
parser.add_argument("-mul", "--multiple", help="as multiple prompt (only for a NL prompt)", action="store_true")
parser.add_argument("--json", help="build the prompt in json format", action="store_true")

args = parser.parse_args()

input_path: str = args.input
output_path: str = args.output
language: str = args.language.upper()
dependencies: bool = args.dependencies
linesofcodes: bool = args.linesofcodes
definitions: bool = args.definitions
multiple: bool = args.multiple
json: bool = args.json

if json and multiple:
    raise ValueError("--json and -mul are incompatible")

if json:
    prompt_builder = PromptBuilder.PromptBuilderJSON()
    os.path.join(output_path, "json")
else:
    prompt_builder = PromptBuilder.PromptBuilderNL()
    os.path.join(output_path, "json")

prompt_builder.build_prompt(input_path, language, output_path, dependencies, linesofcodes, multiple, definitions)
