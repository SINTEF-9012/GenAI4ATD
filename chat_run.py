import argparse
import os.path

import llm_prompting.chat_llm as chat_llm
import llm_prompting.extract_prompts as extract_prompts
import llm_prompting.chat_converter as chat_converter

parser = argparse.ArgumentParser(prog="chat runner",
                                 description="Run a chat with a LLM through Ollama based on a prompt")
parser.add_argument("input", help="input file (the prompt or list of prompts)")
parser.add_argument("output", help="output directory", default="genai4atdOutput/chats-output/")
parser.add_argument("api_url", help="Ollama api url")
parser.add_argument("model", help="LLM model")
parser.add_argument("--json", help="indicate that the prompt(s) are in json format (incompatible with -evo)",
                    action="store_true")
parser.add_argument("-def", "--definitions",
                    help="write the definitions of the metrics as defined by Arcan (incompatible with -evo)",
                    action="store_true")
parser.add_argument("-evo", "--evolution",
                    help="indicate that the prompts are from an evolution analysis (incompatible with --json and -def)",
                    action="store_true")

args = parser.parse_args()

input_path: str = args.input
output_path: str = args.output
api_url: str = args.api_url
model: str = args.model
json: bool = args.json
definitions: bool = args.definitions
evo: bool = args.evolution

if (json and evo) or (definitions and evo):
    raise ValueError("incompatible arguments")

if json:
    prompts_list = extract_prompts.extract_prompts_json(input_path, definitions)
    output_path = os.path.join(output_path, "chats-single-version", "json")
elif evo:
    prompts_list = extract_prompts.extract_prompts_evo(input_path)
    output_path = os.path.join(output_path, "chats-evo")
else:
    prompts_list = extract_prompts.extract_prompts_nl(input_path)
    output_path = os.path.join(output_path, "chats-single-version", "nl")

if definitions:
    output_path = os.path.join(output_path, "v2")
else:
    output_path = os.path.join(output_path, "v1")

chat_file = chat_llm.chat(api_url, model, prompts_list, output_path)

chat_converter.chat_converter(chat_file)
