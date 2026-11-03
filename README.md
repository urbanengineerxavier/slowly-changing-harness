# slowly-changing-harness

A series of small, self-contained agent scripts. Each episode takes the same basic idea — a loop that lets a model call tools until it's done — and adds one new concept on top. Episodes are independent: you can run any one of them without having run the others.

## Setup

Requires [uv](https://docs.astral.sh/uv/) and Python 3.12+ (pinned in `.python-version`).

1. Install dependencies:
   ```bash
   uv sync
   ```
2. Create a `.env` file in the repo root with:
   ```
   OPENAI_API_KEY=sk-...
   SERPER_API_KEY=...
   ```
   `OPENAI_API_KEY` is used by every script's model calls. `SERPER_API_KEY` powers the `search_web` tool (via [serper.dev](https://serper.dev)) that most episodes share.

All commands below are run from the repo root with `uv run python <path>`. Scripts write their output files (briefs, CSVs) into the directory you run them from — the examples below assume repo root, matching the files already checked in.

---

## Episode 1 — The Loop (`EP1_the_loop/`)

The same basic agent loop, implemented two ways, to show what a framework like pydantic-ai is actually doing for you under the hood.

- **`loop_open_ai.py`** — hand-rolled: raw OpenAI chat completions API, a manual `while True` loop, manual tool-call dispatch, manual message history.
- **`loop_pydantic.py`** — the same task rebuilt with pydantic-ai's `Agent`, which handles the loop, tool dispatch, and history for you.

Both research Nvidia's latest earnings and analyst reactions, then write a one-page brief to a markdown file.

Run:
```bash
uv run python EP1_the_loop/loop_open_ai.py
uv run python EP1_the_loop/loop_pydantic.py
```

What you'll see: turn-by-turn tool-call logging in the terminal (`loop_open_ai.py`) or the agent's final summary (`loop_pydantic.py`), and a `nvidia_brief.md` / `nvidia_brief2.md` file written with the research.

---

## Episode 2 — Permission Gates (`EP2_permission_gates/`)

Same shape of agent, now researching stocks instead of one company, with one sensitive tool: `write_to_sheet`, which appends the agent's findings to a local `stock_research.csv`. The concept here is gating that write behind human approval before it executes — reads (`search_web`, `read_url`) stay free.

- **`loop_without_permission_gates.py`** — baseline. `write_to_sheet` runs the moment the model decides to call it, no questions asked.
- **`loop_permission_gates.py`** — same agent, but `write_to_sheet` is registered with `requires_approval=True`. When the model calls it, the run pauses (`DeferredToolRequests`) instead of executing; the script prints the pending rows as JSON and asks `Approve? (y/n)` in the terminal. A `y` lets the write go through; an `n` reports `ToolDenied` back to the model, which can adapt (try again, or just report its findings without writing).

Run:
```bash
uv run python EP2_permission_gates/loop_without_permission_gates.py
uv run python EP2_permission_gates/loop_permission_gates.py
```

What you'll see: for the gated version, a `[GATE] write_to_sheet` block printing the exact rows about to be written, then a prompt waiting on your `y`/`n` before anything touches disk. Check `stock_research.csv` afterward — rows only appear for calls you approved.

---

## Episode 3 — The Loop, LangGraph (`EP3_langgraph/`)

Same stock-research task as Episode 2, rebuilt on core LangGraph instead of pydantic-ai, no gating — just the bare agent loop as LangGraph's own primitives: a `StateGraph` with an `llm` node, LangGraph's prebuilt `ToolNode`, and `tools_condition` routing between them.

- **`loop_langraph.py`** — `llm_node` calls the model; `tools_condition` sends control to `ToolNode` whenever the last message has tool calls, else to `END`; `ToolNode` runs every tool call it's handed, `write_to_sheet` included, and loops back to `llm`.

Run:
```bash
uv run python EP3_langgraph/loop_langraph.py
```

What you'll see: the agent's final summary, and new rows appended to `stock_research.csv`. Uncomment the `draw_mermaid()` line in the script to print the graph structure instead of running it.
