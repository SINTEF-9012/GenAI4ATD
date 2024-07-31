import os.path
from pathlib import Path

import requests
import json


def chat(api_url: str, model: str, prompts_list: list, output: str) -> str:
    """
    Chat with a LLM model through the Ollama API using a prompts list.
    :param api_url:
    :param model:
    :param prompts_list:
    :param output:
    :return: The output file name
    """
    messages: list = []

    for p in prompts_list:
        messages.append(format_prompt(str(p)))
        response = send_prompt(api_url, model, messages)
        messages.append(response)

    file_name: str = os.path.join(output, "chat.json")

    file = Path(file_name)
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(json.dumps(messages))

    return file_name


def format_prompt(prompt: str) -> dict:
    """
    Format a prompt according to the Ollama API specification at https://github.com/ollama/ollama/blob/main/docs/api.md
    :param prompt:
    :return:
    """
    return {
        "role": "user",
        "content": prompt
    }


def send_prompt(api_url: str, model: str, messages: list):
    """
    Send a prompt to the Ollama API
    :param api_url:
    :param model:
    :param messages: Messages history of the chat
    :return:
    """
    prompt_json = {"model": model, "messages": messages, "stream": False}
    response = requests.post(api_url, json=prompt_json).json()

    return response["message"]
