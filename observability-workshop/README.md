# 🔎 Trace the Incident — ship your first Claude Managed Agent

Build a tiny observability platform and bring its AI incident detective online. The platform
ships working: you can inspect logs, deployments, and git history by hand. Your job is to write
the **Managed Agents code** — create the agent and its cloud environment, run a session, answer
its tool calls, and resume conversations from the cloud — so it finds the root cause for you.

## The scenario

At ~14:32 the `checkout` service starts throwing 500s: *"upstream timeout calling
payments-service"*. In the last ~90 minutes three services were deployed and several commits
landed. **Only one change actually explains the incident** — the rest are red herrings. A human
can find it by cross-referencing three tabs. The agent should find it in one question.

## What you build

You implement **one file: [`agent.py`](agent.py)** — eight small functions, each essentially a
single Claude Managed Agents SDK call:

| # | Function | What it does |
|---|----------|--------------|
| 1 | `setup_agent()` | Create the agent (model + system prompt + tools). |
| 2 | `setup_environment()` | Create the **cloud environment** its session runs in. |
| 3 | `start_session()` | Bind agent + environment into a session. |
| 4 | `list_sessions()` | List cloud sessions so you can **resume** one. |
| 5 | `load_history()` | Rebuild a past conversation from the server-side event log. |
| 6 | `stream_reply()` | Stream events; answer `custom_tool_use` with `custom_tool_result`. |
| 7 | `handle_tool()` | Run a tool call locally against the mock data. |
| 8 | `delete_session()` | Clean up the cloud session. |

Each stub has a `# Hint:` line with the near-complete call. The agent's brain — `MODEL`,
`SYSTEM_PROMPT`, and the three `TOOLS` schemas — is **provided** in [`constants.py`](constants.py),
and the tool logic lives in `observatory/tools.py`. Stuck or short on time? Copy the matching
function from [`agent_complete.py`](agent_complete.py).

The Agent tab comes online **one function at a time** — implement `setup_agent()` and it tells
you the next function to write.

## Setup

Work inside a Python environment so the workshop's dependencies stay isolated. Pick whichever
you prefer — [`uv`](https://docs.astral.sh/uv/) (fast) or the built-in `venv`.

**Option A — uv**

```bash
uv venv                                  # creates .venv/
source .venv/bin/activate                # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

**Option B — native Python venv**

```bash
python3 -m venv .venv
source .venv/bin/activate                # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Then, with the environment active:

```bash
export ANTHROPIC_API_KEY=sk-ant-...      # your key (Windows: set / $env:)
streamlit run app.py                     # the one command
```

> Managed Agents is a beta API. The SDK sets the required beta header for you. The agent runs
> on a **cloud environment** provisioned in your Anthropic workspace; the mock tools execute
> locally in this app (they're client-side custom tools).

## Workshop flow

1. **Explore by hand first.** Open the app. In **Logs**, the sample incident is preloaded —
   see the error spike and the affected upstream. Check **Deployments** and **Commits**. Try to
   spot the culprit yourself. This is the "hard way" the agent will automate.
2. **Open the Agent tab.** It's *offline* and tells you the first function to write.
3. **Implement `agent.py`, function by function.** Each stub has a `# Hint:` with the SDK call;
   the panel comes alive as you go (create agent → create env → session picker → chat). Copy from
   `agent_complete.py` if you get stuck.
4. **Start a session and ask.** Click **➕ New session → Open**, then ask
   *"Why did checkout start throwing 500s around 2:30pm?"* Expand the trace to watch it call
   `analyze_logs`, `list_deployments`, and `git_log`, then name **payments-service v2.3.1 /
   commit `a1b2c3`** and rule out the decoys.
5. **Resume from the cloud.** Sessions are stateful and persisted server-side. Reload the app,
   pick your earlier session from the dropdown, and **Open** — `load_history()` replays the whole
   conversation from the event log. Ask a follow-up; the agent still has all its context.

Prefer no UI? Run the same path headless: **`python e2e.py`** (asserts the agent names the culprit).

## How it works

```
constants.py (MODEL, SYSTEM_PROMPT, TOOLS)
        │
        ▼
agent.py: setup_agent() + setup_environment()  ──▶  start_session()  ──▶  stream_reply()
                                                                              │  events
                                                                              ▼
        agent.custom_tool_use  ──▶  handle_tool()  ──▶  observatory/tools.py
                                    (the SAME functions the UI panels call)
                                         │
                                         ▼
                             user.custom_tool_result  ──▶  agent continues
```

- `agent.py` — **you implement this** (the Managed Agents SDK calls).
- `agent_complete.py` — the reference solution.
- `constants.py` — provided: `MODEL`, `SYSTEM_PROMPT`, `TOOLS`.
- `observatory/tools.py` — the three tool functions + `load_incident_log()` (used by UI **and** agent).
- `observatory/mockdata.py` — the incident scenario (deployments + commits).
- `app.py` — the Streamlit UI (provided): manual tabs + the chat panel that drives `agent.py`.
- `e2e.py` — headless verifier.

## Notes

- **Cloud resources.** `setup_agent`/`setup_environment` are `@st.cache_resource`, so they run
  once per app process. Editing `constants.py` (or `agent.py`) and wanting a fresh agent? Restart
  the app, or use the app's menu → *Clear cache*. Delete stray sessions with the 🗑 button (or
  `client.beta.sessions.delete`).
- **`agent_complete.py`.** Same eight functions, filled in — for reference or to unblock yourself.
