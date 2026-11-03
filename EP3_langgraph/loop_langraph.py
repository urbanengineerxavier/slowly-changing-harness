from typing import Annotated

from langchain_openai import ChatOpenAI
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

from shared_tools import read_url, search_web, write_to_sheet

model = ChatOpenAI(model="gpt-4o-mini")
model_with_tools = model.bind_tools([search_web, read_url, write_to_sheet])

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

# Box 1: call the LLM
def llm_node(state: AgentState):
    response = model_with_tools.invoke(state["messages"])
    return {"messages": [response]}

# Box 2: execute whatever tool the LLM called
tools = ToolNode([search_web, read_url, write_to_sheet])

# Build the graph
graph = StateGraph(AgentState)
graph.add_node("llm",   llm_node)
graph.add_node("tools", tools)

graph.add_edge(START, "llm")
graph.add_conditional_edges("llm", tools_condition)  # has tool calls? -> tools, else -> END
graph.add_edge("tools", "llm")                       # loop back after every tool run

app = graph.compile()

# print(app.get_graph().draw_mermaid()) # draw the graph in mermaid format

result = app.invoke({
    "messages": [
        (
            "system",
            "You are a stock research agent. Use search_web and read_url to gather data. "
            "Once you have researched all stocks, call write_to_sheet once with all rows as a batch.",
        ),
        (
            "user",
            "Research 5 high-growth tech stocks. For each: ticker, current price, P/E ratio, "
            "trailing 12M revenue in millions, one-line analyst view. Write all findings to the tracker sheet.",
        ),
    ]
})

print(result["messages"][-1].content)
