"""
Reference implementation of agent.py — the eight functions, filled in.

Short on time, or want to check your work? Copy the function you're stuck on into
agent.py. (You can also run the whole solution by importing this module instead of
`agent` — but the workshop is more fun if you write it yourself.)
"""

import json
import uuid

import streamlit as st

import anthropic
from constants import AGENT_NAME, MODEL, SYSTEM_PROMPT, TOOLS
from observatory import tools

client = anthropic.Anthropic()


def _text(content) -> str:
    """Join the text blocks of an event's content list."""
    return "".join(
        getattr(b, "text", "") for b in (content or []) if getattr(b, "type", None) == "text"
    )


# ── 1. Agent ────────────────────────────────────────────────────────────────
@st.cache_resource
def setup_agent() -> str:
    agent = client.beta.agents.create(
        name=AGENT_NAME,
        model=MODEL,
        system=SYSTEM_PROMPT,
        tools=TOOLS,
    )
    return agent.id


# ── 2. Environment ────────────────────────────────────────────────────────────
@st.cache_resource
def setup_environment() -> str:
    env = client.beta.environments.create(
        name=f"incident-workshop-{uuid.uuid4().hex[:8]}",
        config={"type": "cloud", "networking": {"type": "unrestricted"}},
    )
    return env.id


# ── 3. Start a session ────────────────────────────────────────────────────────
def start_session(agent_id: str, env_id: str) -> str:
    session = client.beta.sessions.create(
        agent=agent_id,
        environment_id=env_id,
        title="incident investigation",
    )
    return session.id


# ── 4. List sessions (resume) ─────────────────────────────────────────────────
def list_sessions(agent_id: str) -> list:
    return client.beta.sessions.list(agent_id=agent_id, limit=15, order="desc").data


# ── 5. Load history (resume) ──────────────────────────────────────────────────
def load_history(session_id: str) -> list:
    hist: list[tuple[str, str]] = []
    for ev in client.beta.sessions.events.list(
        session_id=session_id, order="asc", limit=500
    ).data:
        if ev.type == "user.message":
            hist.append(("user", _text(ev.content)))
        elif ev.type == "agent.message":
            txt = _text(ev.content)
            if hist and hist[-1][0] == "assistant":  # merge streamed chunks
                hist[-1] = ("assistant", hist[-1][1] + txt)
            else:
                hist.append(("assistant", txt))
    return hist


# ── 6. Stream a reply ─────────────────────────────────────────────────────────
def stream_reply(session_id: str, user_text: str):
    with client.beta.sessions.events.stream(session_id=session_id) as stream:
        client.beta.sessions.events.send(
            session_id=session_id,
            events=[{"type": "user.message", "content": [{"type": "text", "text": user_text}]}],
        )
        for event in stream:
            if event.type == "agent.custom_tool_use":
                result = handle_tool(event.name, dict(event.input or {}))
                client.beta.sessions.events.send(
                    session_id=session_id,
                    events=[
                        {
                            "type": "user.custom_tool_result",
                            "custom_tool_use_id": event.id,
                            "content": [{"type": "text", "text": result}],
                        }
                    ],
                )
            yield event


# ── 7. Answer a tool call ─────────────────────────────────────────────────────
def handle_tool(name: str, args: dict) -> str:
    if name == "analyze_logs":
        return json.dumps(tools.analyze_logs(tools.load_incident_log()), default=str)
    if name == "list_deployments":
        return json.dumps(
            tools.list_deployments(since_minutes=int(args.get("since_minutes", 90))),
            default=str,
        )
    if name == "git_log":
        return json.dumps(
            tools.git_log(
                service=args.get("service"),
                since_minutes=int(args.get("since_minutes", 120)),
            ),
            default=str,
        )
    return f"unknown tool {name}"


# ── 8. Delete a session ───────────────────────────────────────────────────────
def delete_session(session_id: str) -> None:
    client.beta.sessions.delete(session_id=session_id)
