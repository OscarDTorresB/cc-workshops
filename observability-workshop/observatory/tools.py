"""The three mock "observability tools", as plain Python functions.

These are the heart of the platform. They are used in two places:

  * the Streamlit UI panels call them directly (a human investigating by hand), and
  * once the agent is implemented, its custom-tool handlers call the *same* functions.

That dual use is the whole point: every tool is available with or without the agent.
Nothing here talks to Claude — these are pure, deterministic functions over the mock
data in ``mockdata.py``.
"""

from __future__ import annotations

import re
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

from . import mockdata

_INCIDENT_LOG = Path(__file__).resolve().parent.parent / "logs" / "incident.log"


def load_incident_log() -> str:
    """Read the fixed mock incident log shipped with the workshop."""
    return _INCIDENT_LOG.read_text() if _INCIDENT_LOG.exists() else ""

# ---- shared helpers ---------------------------------------------------------

_LINE_RE = re.compile(
    r"^(?P<ts>\S+)\s+(?P<level>[A-Z]+)\s+(?P<service>\S+)\s+(?P<rest>.*)$"
)
_UPSTREAM_RE = re.compile(r"upstream=(?P<upstream>\S+)")
_ERROR_RE = re.compile(r'error="(?P<error>[^"]+)"')


def _parse_ts(value: str) -> datetime:
    """Parse an ISO-8601 timestamp, tolerating a trailing 'Z'."""
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _within(timestamp: str, since_minutes: int) -> bool:
    """True if `timestamp` is within `since_minutes` before the incident reference time."""
    now = _parse_ts(mockdata.INCIDENT_NOW)
    return _parse_ts(timestamp) >= now - timedelta(minutes=since_minutes)


# ---- tool 1: analyze_logs ---------------------------------------------------


def analyze_logs(log_text: str) -> dict:
    """Summarize a raw log blob: error volume, spike timing, and the affected service.

    Returns a structured dict rather than free text so the agent (and the UI) can
    reason about specific timestamps and dependencies.
    """
    errors: list[dict] = []
    warns = 0
    services_with_errors: Counter[str] = Counter()
    upstreams: Counter[str] = Counter()
    signatures: Counter[str] = Counter()
    timestamps: list[datetime] = []
    parsed = 0

    for raw in log_text.splitlines():
        line = raw.strip()
        if not line:
            continue
        m = _LINE_RE.match(line)
        if not m:
            continue
        parsed += 1
        ts, level, service, rest = (
            m["ts"],
            m["level"],
            m["service"],
            m["rest"],
        )
        try:
            timestamps.append(_parse_ts(ts))
        except ValueError:
            pass

        if level == "WARN":
            warns += 1
        elif level == "ERROR":
            services_with_errors[service] += 1
            up = _UPSTREAM_RE.search(rest)
            if up:
                upstreams[up["upstream"]] += 1
            err = _ERROR_RE.search(rest)
            signatures[err["error"] if err else rest] += 1
            errors.append({"timestamp": ts, "service": service})

    if not parsed:
        return {"error": "No parseable log lines found."}

    # Per-minute error histogram → find when the spike starts and where it peaks.
    per_minute: Counter[str] = Counter()
    for e in errors:
        per_minute[e["timestamp"][:16]] += 1  # 'YYYY-MM-DDTHH:MM'

    spike_start = min((e["timestamp"] for e in errors), default=None)
    peak_minute, peak_count = (per_minute.most_common(1)[0] if per_minute else (None, 0))
    primary_service = (
        services_with_errors.most_common(1)[0][0] if services_with_errors else None
    )
    upstream_dependency = upstreams.most_common(1)[0][0] if upstreams else None

    return {
        "time_range": {
            "start": min(timestamps).isoformat() if timestamps else None,
            "end": max(timestamps).isoformat() if timestamps else None,
        },
        "lines_parsed": parsed,
        "error_count": len(errors),
        "warn_count": warns,
        "affected_service": primary_service,
        "upstream_dependency": upstream_dependency,
        "spike_started_at": spike_start,
        "peak_minute": peak_minute,
        "peak_errors_per_minute": peak_count,
        "top_error_signatures": [
            {"error": sig, "count": n} for sig, n in signatures.most_common(3)
        ],
        "errors_per_minute": dict(sorted(per_minute.items())),
    }


# ---- tool 2: list_deployments ----------------------------------------------


def list_deployments(since_minutes: int = 90) -> list[dict]:
    """Recent deployments within the last `since_minutes` (relative to the incident)."""
    return [d for d in mockdata.DEPLOYMENTS if _within(d["timestamp"], since_minutes)]


# ---- tool 3: git_log --------------------------------------------------------


def git_log(service: str | None = None, since_minutes: int = 120) -> list[dict]:
    """Recent commits within the last `since_minutes`, optionally filtered by service."""
    out = [c for c in mockdata.COMMITS if _within(c["timestamp"], since_minutes)]
    if service:
        out = [c for c in out if c["service"] == service]
    return out
