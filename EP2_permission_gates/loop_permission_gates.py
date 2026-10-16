import json

from pydantic_ai import Agent, DeferredToolRequests, DeferredToolResults, ToolApproved, ToolDenied
from pydantic_ai.models.openai import OpenAIChatModel

from shared_tools import read_url, search_web, write_to_sheet

agent = Agent(
    OpenAIChatModel("gpt-4o-mini"),
    system_prompt=(
        "You are a stock research agent. Use search_web and read_url to gather data. "
        "Once you have researched all stocks, call write_to_sheet once with all rows as a batch."
    ),
    output_type=[str, DeferredToolRequests],
)
agent.tool_plain(search_web)
agent.tool_plain(read_url)
agent.tool_plain(write_to_sheet, requires_approval=True)

result = agent.run_sync(
    "Research 5 high-growth tech stocks. For each: ticker, current price, P/E ratio, "
    "trailing 12M revenue in millions, one-line analyst view. Write all findings to the tracker sheet."
)

while isinstance(result.output, DeferredToolRequests):
    results = DeferredToolResults()
    denied = False
    for call in result.output.approvals:
        print(f"\n[GATE] {call.tool_name}")
        print(json.dumps(call.args_as_dict(), indent=2))
        approved = input("\nApprove? (y/n): ").strip() == "y"
        if approved:
            results.approvals[call.tool_call_id] = ToolApproved()
        else:
            denied = True
            results.approvals[call.tool_call_id] = ToolDenied("Not approved by user")

    if denied:
        print("\n[GATE] Write denied. Stopping.")
        break

    result = agent.run_sync(
        "Continue", message_history=result.all_messages(), deferred_tool_results=results
    )
else:
    print(result.output)
