"""
========================================================================
  THIS IS THE FILE YOU IMPLEMENT IN THE WORKSHOP.
========================================================================

Ship your first Claude Managed Agent. Eight small functions — each is essentially
a single Managed Agents SDK call. Everything else (the incident data, the system
prompt, the tool schemas, the whole UI) is already provided.

The platform's Logs / Deployments / Commits views already work without you. Your job
is to bring the Agent view online: create the agent and its cloud environment, run a
session, answer the agent's tool calls, and resume conversations from the cloud.

Fill in each function (replace `raise NotImplementedError`). The app lights up one
function at a time and tells you which to write next. Stuck or out of time? Copy the
matching function from `agent_complete.py`.

The Managed Agents API is beta — the SDK sets the beta header for you. Auth is the
ANTHROPIC_API_KEY environment variable.
"""

import json

import streamlit as st

import anthropic
from constants import AGENT_NAME, MODEL, SYSTEM_PROMPT, TOOLS
from observatory import tools

# Reads ANTHROPIC_API_KEY from the environment.
client = anthropic.Anthropic()


# ── 1. Agent ────────────────────────────────────────────────────────────────
# What the agent IS: model, system prompt, tools. Create once, reuse forever.
# Hint: client.beta.agents.create(name=AGENT_NAME, model=MODEL, system=SYSTEM_PROMPT, tools=TOOLS).id
@st.cache_resource
def setup_agent() -> str:
    raise NotImplementedError


# ── 2. Environment ────────────────────────────────────────────────────────────
# Where the agent's session container runs, in your Anthropic workspace. Create once.
# Hint: client.beta.environments.create(name=..., config={"type": "cloud", "networking": {"type": "unrestricted"}}).id
@st.cache_resource
def setup_environment() -> str:
    raise NotImplementedError


# ── 3. Start a session ────────────────────────────────────────────────────────
# Bind the agent to the environment. Returns a session id — a durable cloud handle.
# Hint: client.beta.sessions.create(agent=agent_id, environment_id=env_id, title=...).id
def start_session(agent_id: str, env_id: str) -> str:
    raise NotImplementedError


# ── 4. List sessions (resume) ─────────────────────────────────────────────────
# Sessions live in the cloud, not this browser. List an agent's recent sessions so a
# user can reconnect to one. Return the raw session objects (they have .id/.created_at/.status).
# Hint: client.beta.sessions.list(agent_id=agent_id, limit=15, order="desc").data
def list_sessions(agent_id: str) -> list:
    raise NotImplementedError


# ── 5. Load history (resume) ──────────────────────────────────────────────────
# Rebuild a past conversation by replaying the session's server-side event log.
# Return a list of (role, text) pairs, oldest first, where role is "user" or "assistant".
# Hint: client.beta.sessions.events.list(session_id=session_id, order="asc", limit=500).data
#       keep user.message + agent.message events; pull text from event.content blocks.
def load_history(session_id: str) -> list:
    raise NotImplementedError


# ── 6. Stream a reply ─────────────────────────────────────────────────────────
# Open the event stream, send the user's message, and yield events as they arrive.
# When you see an "agent.custom_tool_use" event, run handle_tool() and post the result
# back as a "user.custom_tool_result" event (keyed by the tool-use event's id).
# Hint: with client.beta.sessions.events.stream(session_id=session_id) as stream:
#           client.beta.sessions.events.send(session_id=session_id, events=[{"type": "user.message", ...}])
#           for event in stream: ... yield event
def stream_reply(session_id: str, user_text: str):
    raise NotImplementedError


# ── 7. Answer a tool call ─────────────────────────────────────────────────────
# The cloud agent calls analyze_logs / list_deployments / git_log; you run them HERE,
# on your machine, using the same functions the UI uses. Return a string (JSON).
# Hint: tools.analyze_logs(tools.load_incident_log()), tools.list_deployments(...), tools.git_log(...)
def handle_tool(name: str, args: dict) -> str:
    raise NotImplementedError


# ── 8. Delete a session ───────────────────────────────────────────────────────
# Sessions are real cloud resources — let users clean them up.
# Hint: client.beta.sessions.delete(session_id=session_id)
def delete_session(session_id: str) -> None:
    raise NotImplementedError
