import json
import os


def chat_converter(chat_path: str):
    chat_json_file = open(chat_path)

    chat_json: list = json.loads(chat_json_file.read())
    chat_md_builder: list = []

    for message in chat_json:
        chat_md_builder.append("  \n## " + message["role"] + "  \n" +
                               message["content"])

    chat_md_file = open(chat_path + ".md", "w")
    chat_md_file.write("".join(chat_md_builder))


def convert_all_chats(directory: str):
    for element in os.listdir(directory):
        element_full_path = os.path.join(directory, element)
        if os.path.isfile(element_full_path) and element_full_path.endswith(".json"):
            chat_converter(element_full_path)
