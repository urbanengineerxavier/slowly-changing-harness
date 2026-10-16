import json
from dotenv import load_dotenv

load_dotenv()

from openai import OpenAI
from shared_tools import search_web, read_url, write_file

client = OpenAI()
tools_schema = [
    {"type": "function", "function": {"name": "search_web", "description": "Search the web", "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}},
    {"type": "function", "function": {"name": "read_url", "description": "Read a webpage", "parameters": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}}},
    {"type": "function", "function": {"name": "write_file", "description": "Write a file", "parameters": {"type": "object", "properties": {"filename": {"type": "string"}, "content": {"type": "string"}}, "required": ["filename", "content"]}}}
]

dispatch = {"search_web": search_web, "read_url": read_url, "write_file": write_file}
messages = [{"role": "user", "content": "Research Nvidia's 2026 earnings, find analyst reactions, write a one-page brief to nvidia_brief.md"}]
turn = 1

while True:
    response = client.chat.completions.create(model="gpt-4o-mini", messages=messages, tools=tools_schema)
    choice = response.choices[0]

    if choice.finish_reason == "stop":
        print(f"Turn {turn}: [end_turn] Done.")
        break

    messages.append(choice.message)
    for tool_call in choice.message.tool_calls:
        args = json.loads(tool_call.function.arguments)
        print(f"Turn {turn}: [tool_call] {tool_call.function.name}({list(args.values())[0][:60]})")
        result = dispatch[tool_call.function.name](**args)
        messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": result})
        turn += 1