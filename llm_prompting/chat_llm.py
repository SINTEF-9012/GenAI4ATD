import requests
import json


def chat(api_url: str, model: str, prompts: list, output: str):
    messages: list = []

    for p in prompts:
        messages.append(format_prompt(str(p)))
        response = send_prompt(api_url, model, messages)
        messages.append(response)

    file_name = output + ".json"

    file = open(file_name, "w")
    file.write(json.dumps(messages))

    return file_name


def format_prompt(prompt: str):
    return {
        "role": "user",
        "content": prompt
    }


def send_prompt(api_url: str, model: str, messages: list):
    prompt_json = {"model": model, "messages": messages, "stream": False}
    response = requests.post(api_url, json=prompt_json).json()

    return response["message"]
