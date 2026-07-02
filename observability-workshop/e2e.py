"""Headless end-to-end check — no Streamlit UI.

Runs YOUR agent.py against the incident and asserts it finds the culprit. Handy for
verifying your implementation without clicking through the app.

    python e2e.py

Requires ANTHROPIC_API_KEY. To run the reference solution instead of your own code,
change the import below to `import agent_complete as agent`.
"""

import sys

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # noqa: BLE001
    pass

import agent  # your implementation (swap for agent_complete to run the solution)

QUESTION = "Checkout started throwing 500s around 14:32 UTC. What is the root cause?"
EXPECT = ["payments-service", "a1b2c3"]  # the culprit deploy + commit


def main() -> int:
    try:
        agent_id = agent.setup_agent()
        env_id = agent.setup_environment()
        session_id = agent.start_session(agent_id, env_id)
    except NotImplementedError:
        print("Not implemented yet — finish the functions in agent.py first.")
        return 2

    print(f"agent=…{agent_id[-8:]}  env=…{env_id[-8:]}  session=…{session_id[-8:]}\n")

    transcript: list[str] = []
    try:
        for ev in agent.stream_reply(session_id, QUESTION):
            etype = getattr(ev, "type", None)
            if etype == "agent.message":
                txt = "".join(
                    getattr(b, "text", "")
                    for b in (ev.content or [])
                    if getattr(b, "type", None) == "text"
                )
                transcript.append(txt)
                print(txt, end="", flush=True)
            elif etype == "agent.custom_tool_use":
                print(f"\n[tool] {ev.name} {dict(ev.input or {})}")
            elif etype == "session.status_terminated":
                break
            elif etype == "session.status_idle":
                if getattr(getattr(ev, "stop_reason", None), "type", None) == "end_turn":
                    break
    finally:
        try:
            agent.delete_session(session_id)
        except Exception:  # noqa: BLE001 — best-effort cleanup
            pass

    full = "\n".join(transcript).lower()
    missing = [k for k in EXPECT if k.lower() not in full]
    print("\n" + "-" * 60)
    if not missing:
        print("PASS — the agent named the culprit (payments-service / a1b2c3).")
        return 0
    print(f"INCONCLUSIVE — transcript did not mention: {missing}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
