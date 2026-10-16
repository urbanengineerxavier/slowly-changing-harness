from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel

from shared_tools import read_url, search_web, write_to_sheet

agent = Agent(
    OpenAIChatModel("gpt-4o-mini"),
    system_prompt=(
        "You are a stock research agent. Use search_web and read_url to gather data. "
        "Once you have researched all stocks, call write_to_sheet once with all rows as a batch."
    ),
)
agent.tool_plain(search_web)
agent.tool_plain(read_url)
agent.tool_plain(write_to_sheet)

result = agent.run_sync(
    "Research 5 high-growth tech stocks. For each: ticker, current price, P/E ratio, "
    "trailing 12M revenue in millions, one-line analyst view. Write all findings to the tracker sheet."
)
print(result.output)
