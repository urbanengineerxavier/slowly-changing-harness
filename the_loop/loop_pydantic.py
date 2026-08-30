from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from shared_tools import search_web, read_url, write_file

agent = Agent(OpenAIChatModel("gpt-4o-mini"), system_prompt="You are a financial research agent.")

agent.tool_plain(search_web)
agent.tool_plain(read_url)
agent.tool_plain(write_file)

result = agent.run_sync("Research Nvidia's latest earnings, find analyst reactions, write a one-page brief to nvidia_brief2.md")
print(result.output)