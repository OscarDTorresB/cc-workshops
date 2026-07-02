"""Trace the Incident — a tiny observability platform (Streamlit UI).

Run it with:   streamlit run app.py

Layout: a left sidebar holds the brand, the live incident status, the navigation,
and (on the Agent view) the session controls. The main area shows one focused view
at a time — Logs, Deployments, Commits, or the Agent.

The Logs / Deployments / Commits views work immediately with the mock data. The Agent
view drives YOUR code in agent.py: it comes online one function at a time as you
implement them, then runs (and resumes) a Claude Managed Agent in the cloud.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

try:  # optional: load ANTHROPIC_API_KEY from a .env file if present
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # noqa: BLE001
    pass

from observatory import tools

st.set_page_config(
    page_title="Trace the Incident",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_css() -> None:
    """Inject assets/style.css as a <style> block.

    Guard: neutralize any literal `</style>` inside the file (e.g. mentioned in a
    comment) so the HTML parser doesn't end the style element early and dump the CSS
    onto the page as text.
    """
    from pathlib import Path

    css_path = Path(__file__).parent / "assets" / "style.css"
    if css_path.exists():
        css = css_path.read_text().replace("</style>", "<\\/style>")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


load_css()

LOG_TEXT = tools.load_incident_log()
SUMMARY = tools.analyze_logs(LOG_TEXT)
HAS_SIGNAL = "error" not in SUMMARY


# --- small helpers -----------------------------------------------------------
def _text_of(content) -> str:
    return "".join(
        getattr(b, "text", "") for b in (content or []) if getattr(b, "type", None) == "text"
    )


def _hhmm(iso_ts: str | None) -> str:
    return iso_ts[11:16] if iso_ts and len(iso_ts) >= 16 else "—"


def page_header(title: str, subtitle: str) -> None:
    st.html(f'<div class="page-head"><h1>{title}</h1><p>{subtitle}</p></div>')


def _style_ops_table(rows: list[dict]):
    """Lightly style a deployments/commits table.

    Returns a pandas Styler that st.dataframe renders directly. We only tint the
    neutral `status` column (green succeeded / red failed / amber pending). We do
    NOT highlight rows by service — that would hand the investigator the culprit.
    """
    df = pd.DataFrame(rows)

    def color_status(value):
        palette = {
            "succeeded": "#34d399",
            "failed": "#f87171",
            "rolled_back": "#f87171",
            "pending": "#fbbf24",
        }
        color = palette.get(str(value).lower())
        return f"color: {color}; font-weight: 600" if color else ""

    styler = df.style
    if "status" in df.columns:
        styler = styler.map(color_status, subset=["status"])
    return styler


# =============================================================================
#  SIDEBAR — brand, live status, navigation
# =============================================================================
NAV = ["Logs", "Deployments", "Commits", "Agent"]
NAV_LABELS = {
    "Logs": "📄  Logs",
    "Deployments": "🚀  Deployments",
    "Commits": "🧬  Commits",
    "Agent": "💬  Ask the agent",
}
st.session_state.setdefault("nav", "Logs")

with st.sidebar:
    st.html(
        '<div class="brand">'
        '<span class="brand__logo">🔎</span>'
        '<div><div class="brand__title">Trace the Incident</div>'
        '<div class="brand__subtitle">Incident Console</div></div>'
        "</div>"
    )

    if HAS_SIGNAL:
        st.html(
            '<div class="status-chip"><span class="dot"></span>'
            f"<div>Active incident<small>{SUMMARY['error_count']} errors · "
            f"spike {_hhmm(SUMMARY['spike_started_at'])}</small></div></div>"
        )
    else:
        st.html(
            '<div class="status-chip ok"><span class="dot"></span>'
            "<div>All clear<small>no error spike detected</small></div></div>"
        )

    st.html('<div class="nav-label">Navigate</div>')
    for item in NAV:
        is_active = st.session_state.nav == item
        if st.button(
            NAV_LABELS[item],
            key=f"nav_{item}",
            width="stretch",
            type="primary" if is_active else "secondary",
        ):
            st.session_state.nav = item
            st.rerun()

nav = st.session_state.nav


# =============================================================================
#  LOGS
# =============================================================================
if nav == "Logs":
    page_header("Logs", "Application logs for the incident window. Find the error spike and what it hit.")

    if "error" in SUMMARY:
        st.warning(SUMMARY["error"])
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Errors", SUMMARY["error_count"])
        c2.metric("Warnings", SUMMARY["warn_count"])
        c3.metric("Spike start", _hhmm(SUMMARY["spike_started_at"]))
        c4.metric("Peak errors/min", SUMMARY["peak_errors_per_minute"])

        if SUMMARY["errors_per_minute"]:
            st.caption("Errors per minute")
            st.bar_chart({"errors": list(SUMMARY["errors_per_minute"].values())})

        if SUMMARY["top_error_signatures"]:
            st.caption("Top error signatures")
            st.table(SUMMARY["top_error_signatures"])

    with st.expander("Raw log", expanded=False):
        st.code(LOG_TEXT or "(empty)", language="text")


# =============================================================================
#  DEPLOYMENTS
# =============================================================================
elif nav == "Deployments":
    page_header("Deployments", "Recent releases across services — one of these may have triggered the incident.")
    since = st.slider("Lookback (minutes)", 15, 240, 90, 15, key="deploy_since")
    rows = tools.list_deployments(since_minutes=since)
    if rows:
        st.html(
            '<div class="legend">'
            '<span><i style="background:#34d399"></i> succeeded</span>'
            '<span><i style="background:#fbbf24"></i> pending</span>'
            '<span><i style="background:#f87171"></i> failed / rolled back</span>'
            "</div>"
        )
        st.dataframe(_style_ops_table(rows), width="stretch", hide_index=True)
    else:
        st.info("No deployments in this window.")


# =============================================================================
#  COMMITS
# =============================================================================
elif nav == "Commits":
    page_header("Commits", "Recent code changes across services. Filter by service to narrow the search.")
    col_a, col_b = st.columns(2)
    svc = col_a.text_input("Filter by service (optional)", key="commit_service").strip()
    since_c = col_b.slider("Lookback (minutes)", 15, 240, 120, 15, key="commit_since")
    rows = tools.git_log(service=svc or None, since_minutes=since_c)
    if rows:
        st.dataframe(_style_ops_table(rows), width="stretch", hide_index=True)
    else:
        st.info("No commits in this window.")


# =============================================================================
#  AGENT  — drives agent.py; comes online one function at a time
# =============================================================================
elif nav == "Agent":
    page_header(
        "Incident detective",
        "An AI agent that correlates logs, deployments, and commits to find the root cause. "
        "It drives your agent.py and comes online as you implement each function.",
    )

    import agent as A  # your file

    def offline(fn: str):
        st.info(
            f"**Agent offline.** Implement `{fn}` in `agent.py` "
            f"(peek at `agent_complete.py` if stuck), then rerun.",
            icon="🛠️",
        )
        st.stop()

    # 1 & 2 — create the agent and its cloud environment (cached: created once).
    try:
        agent_id = A.setup_agent()
    except NotImplementedError:
        offline("setup_agent()")
    try:
        env_id = A.setup_environment()
    except NotImplementedError:
        offline("setup_environment()")

    # 4 — list existing cloud sessions so we can resume one.
    try:
        sessions = A.list_sessions(agent_id)
    except NotImplementedError:
        offline("list_sessions()")

    def _label(s) -> str:
        created = str(getattr(s, "created_at", ""))
        when = created[5:16].replace("T", " ").strip() if len(created) >= 16 else created
        return f"{when} · {getattr(s, 'status', '?')} · …{s.id[-6:]}"

    # --- Session controls live in the sidebar ---------------------------------
    # A clickable history list: click a row to open it (one click, no separate
    # button); the active session is highlighted; the trash deletes that row.
    with st.sidebar:
        st.html('<div class="nav-label">Session</div>')
        st.html(f'<div class="meta-line">agent <code>…{agent_id[-6:]}</code> · env <code>…{env_id[-6:]}</code></div>')

        if st.button("＋  New session", width="stretch", key="new_session"):
            try:
                st.session_state.sid = A.start_session(agent_id, env_id)
            except NotImplementedError:
                offline("start_session()")
            st.session_state.hist = []
            st.rerun()

        sid = st.session_state.get("sid")
        if sessions:
            st.html('<div class="nav-label">Recent</div>')
        for s in sessions:
            open_col, del_col = st.columns([5, 1], vertical_alignment="center")
            if open_col.button(
                _label(s),
                key=f"open_{s.id}",
                width="stretch",
                type="primary" if s.id == sid else "secondary",
            ):
                try:
                    st.session_state.hist = A.load_history(s.id)
                except NotImplementedError:
                    offline("load_history()")
                st.session_state.sid = s.id
                st.rerun()
            if del_col.button("🗑", key=f"del_{s.id}", help="Delete this session"):
                try:
                    A.delete_session(s.id)
                except NotImplementedError:
                    offline("delete_session()")
                if st.session_state.get("sid") == s.id:
                    st.session_state.pop("sid", None)
                    st.session_state.pop("hist", None)
                st.rerun()

    # --- Main area: the conversation -----------------------------------------
    sid = st.session_state.get("sid")
    if not sid:
        st.html(
            '<div class="empty"><b>No session open.</b><br>'
            "Start a <b>New session</b> from the sidebar (or resume an existing one) to begin.</div>"
        )
        st.stop()

    st.caption(f"Session …{sid[-6:]} — persisted in the cloud, not this browser.")
    st.session_state.setdefault("hist", [])

    for role, txt in st.session_state.hist:
        with st.chat_message(role):
            st.markdown(txt)

    question = st.chat_input(
        "Ask about the incident, e.g. 'Why did checkout start throwing 500s around 2:30pm?'"
    )
    if question:
        with st.chat_message("user"):
            st.markdown(question)
        st.session_state.hist.append(("user", question))

        with st.chat_message("assistant"):
            reply, trace = "", []
            try:
                with st.spinner("Investigating in the cloud…"):
                    for ev in A.stream_reply(sid, question):
                        etype = getattr(ev, "type", None)
                        if etype == "agent.message":
                            reply += _text_of(ev.content)
                        elif etype == "agent.custom_tool_use":
                            trace.append(("call", ev.name, dict(ev.input or {})))
                        elif etype == "user.custom_tool_result":
                            trace.append(("result", None, _text_of(ev.content)))
                        elif etype == "session.error":
                            trace.append(
                                ("error", None, getattr(getattr(ev, "error", None), "message", "error"))
                            )
                        elif etype == "session.status_terminated":
                            break
                        elif etype == "session.status_idle":
                            if getattr(getattr(ev, "stop_reason", None), "type", None) == "end_turn":
                                break
            except NotImplementedError:
                offline("stream_reply() / handle_tool()")

            st.markdown(reply or "_(no answer)_")
            if trace:
                with st.expander("How the agent investigated"):
                    for kind, name, payload in trace:
                        if kind == "call":
                            st.markdown(f"**→ called `{name}`** `{payload}`")
                        elif kind == "result":
                            st.code(payload, language="json")
                        elif kind == "error":
                            st.error(payload)

        st.session_state.hist.append(("assistant", reply))
