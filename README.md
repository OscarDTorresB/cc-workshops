# cc-workshops

Hands-on workshops for teaching and coaching people on how to build with Claude. Each workshop is a small, self-contained project you actually run, not slides. This is a growing collection, and today it holds one workshop.

[![Python](https://img.shields.io/badge/Python-3.9%2B-0E7C86?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-app-0E7C86?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Anthropic](https://img.shields.io/badge/Claude-Managed%20Agents-0E7C86?style=flat-square&logo=anthropic&logoColor=white)](https://www.anthropic.com/)
[![License](https://img.shields.io/badge/License-MIT-0E7C86?style=flat-square)](LICENSE)

## What's inside

### observability-workshop: "Trace the Incident"

Ship your first Claude Managed Agent. You get a tiny observability platform that already works: a Streamlit app with Logs, Deployments, and Commits views over a fixed mock incident. The `checkout` service starts throwing 500s ("upstream timeout calling payments-service"), several services deployed and several commits landed in the last ~90 minutes, and only one change actually explains the outage. A human can find it by cross-referencing three tabs. Your job is to build the agent that finds it in one question.

You implement one file, `agent.py`, as eight small functions, each essentially a single Managed Agents SDK call:

1. `setup_agent()`, create the agent (model, system prompt, tools).
2. `setup_environment()`, create the cloud environment its session runs in.
3. `start_session()`, bind agent and environment into a session.
4. `list_sessions()`, list cloud sessions so you can resume one.
5. `load_history()`, rebuild a past conversation from the server-side event log.
6. `stream_reply()`, stream events and answer `agent.custom_tool_use` with `user.custom_tool_result`.
7. `handle_tool()`, run a tool call locally against the mock data.
8. `delete_session()`, clean up the cloud session.

The agent's brain (`MODEL`, `SYSTEM_PROMPT`, and the three tool schemas) is provided in `constants.py`, the tool logic lives in `observatory/tools.py`, and the Streamlit UI comes online one function at a time as you implement them. A full reference solution sits in `agent_complete.py` if you get stuck.

What it teaches:

- The Claude Managed Agents beta API end to end: `client.beta.agents`, `client.beta.environments`, and `client.beta.sessions`.
- The client-side custom tool loop: the cloud agent requests a tool call, you execute it locally, and you post the result back as a session event.
- Stateful, server-side sessions: list them, resume one, and replay their full event history so the agent keeps its context across app restarts.

See [`observability-workshop/README.md`](observability-workshop/README.md) for the full walkthrough.

## Tech stack

- Python 3.9+
- [`anthropic`](https://pypi.org/project/anthropic/) `>=0.97.0`, the Claude SDK, including the Managed Agents beta
- [`streamlit`](https://streamlit.io/) `>=1.40.0`, the incident-console UI
- [`python-dotenv`](https://pypi.org/project/python-dotenv/) `>=1.0.0`, loads `ANTHROPIC_API_KEY` from a local `.env`

## Getting started

```bash
cd observability-workshop

# Create an isolated environment (uv or the built-in venv both work)
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Provide your key (copy .env.example to .env, or export it)
export ANTHROPIC_API_KEY=sk-ant-...

# Launch the app
streamlit run app.py
```

Prefer the fast path? Swap the venv step for [`uv`](https://docs.astral.sh/uv/):

```bash
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt
```

Then work through the app: explore the incident by hand, open the Agent view, and implement `agent.py` function by function. To run the same path headless (it asserts the agent names the culprit), use:

```bash
python e2e.py
```

Managed Agents is a beta API and the SDK sets the required beta header for you. The agent loop runs on a cloud environment in your Anthropic workspace, while the mock tools execute locally as client-side custom tools.

## Repository structure

```
cc-workshops/
├── LICENSE
├── README.md
└── observability-workshop/
    ├── README.md            # full workshop walkthrough
    ├── agent.py             # YOU implement this (eight SDK functions)
    ├── agent_complete.py    # reference solution
    ├── constants.py         # provided: MODEL, SYSTEM_PROMPT, TOOLS
    ├── app.py               # Streamlit UI (provided)
    ├── e2e.py               # headless verifier
    ├── requirements.txt
    ├── .env.example
    ├── .streamlit/          # dark "incident console" theme
    ├── assets/              # UI styling
    ├── logs/                # the fixed mock incident log
    └── observatory/
        ├── tools.py         # the three tool functions (UI and agent share them)
        └── mockdata.py      # the incident scenario: deployments + commits
```

## License

[MIT](LICENSE), Copyright (c) 2026 Oscar Torres.
