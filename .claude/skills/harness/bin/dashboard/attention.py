"""Attention derivation over the disk collector's work items (FEAT-53 T-24, D-25).

Pure: reads the selected source copy's files, never the network, and takes `now` as an
argument so every rule is testable against a fixed clock. Thresholds come from the
`dashboard` block of harness.json and are validated, never defaulted.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path

import artifact_accessors
import harness_yaml

ORDER = ("needs-you", "blocked", "stalled", "over-budget", "running", "stale")
TERMINAL_STATIONS = frozenset({"done", "abandoned"})
_THRESHOLD_KEYS = ("stalled_minutes", "stale_days", "over_budget_remaining_cycles")


@dataclass(frozen=True)
class Thresholds:
    stalled_minutes: int
    stale_days: int
    over_budget_remaining_cycles: int


@dataclass(frozen=True)
class Attention:
    state: str | None
    reasons: tuple[str, ...]
    relevant_at: datetime | None

    def to_dict(self):
        return {"state": self.state, "reasons": list(self.reasons),
                "relevant_at": self.relevant_at.isoformat() if self.relevant_at else None}


def thresholds(config: dict) -> Thresholds:
    """The validated `dashboard` block; a missing or malformed value is an error, never a default."""
    block = config.get("dashboard") if isinstance(config, dict) else None
    if not isinstance(block, dict):
        raise ValueError("harness.json has no dashboard block — run upgrade-config.py to install it")
    values = {}
    for key in _THRESHOLD_KEYS:
        value = block.get(key)
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError(f"dashboard.{key} must be a positive integer, got {value!r}")
        values[key] = value
    return Thresholds(**values)


def rank(items, now: datetime, limits: Thresholds):
    """(item, attention) pairs in D-25 order: state precedence, oldest relevant write, id."""
    pairs = [(item, derive(item, now, limits)) for item in items]
    far_future = datetime.max.replace(tzinfo=timezone.utc)

    def key(pair):
        item, attention = pair
        position = ORDER.index(attention.state) if attention.state in ORDER else len(ORDER)
        return (position, attention.relevant_at or far_future, item.id)
    return sorted(pairs, key=key)


def derive(item, now: datetime, limits: Thresholds) -> Attention:
    if item.error is not None:
        return Attention(None, (f"source error: {item.error}",), None)
    if item.kind == "grilling":
        if item.grilling_status == "open":
            return Attention("needs-you", ("grilling note is open",), _stat_time(Path(item.source_path)))
        return Attention(None, (), None)
    if item.kind not in ("feature", "bug"):
        return Attention(None, (), None)
    return _feature_attention(item, now, limits)


@dataclass(frozen=True)
class _Activity:
    """The selected copy's run status and write times, read once per item."""
    run_status: str | None
    live_at: datetime | None      # newest of STATE.md and the current run's state.yaml
    newest_at: datetime | None    # newest of every governed file


def _activity(source):
    run_status, run_state_at = _current_run_state(source)
    state_md_at = _stat_time(source / "STATE.md")
    live_at = _latest(state_md_at, run_state_at)
    newest_at = _latest(live_at, _stat_time(source / "plan.yaml"), _stat_time(source / "feature.json"))
    return _Activity(run_status, live_at, newest_at)


def _run_states(activity, now, limits):
    """(states, reasons) contributed by the current run: blocked, stalled or running."""
    if activity.run_status == "blocked":
        return ["blocked"], ["current run is blocked"]
    if activity.run_status != "running":
        return [], []
    idle = now - activity.live_at if activity.live_at is not None else None
    if idle is not None and idle >= timedelta(minutes=limits.stalled_minutes):
        return ["stalled"], [f"running with no state write for {_minutes(idle)} min"]
    return ["running"], ["current run is running"]


def _stale(activity, now, limits):
    if activity.newest_at is None:
        return False
    return now - activity.newest_at >= timedelta(days=limits.stale_days)


def _budget_and_stale(item, activity, states, now, limits):
    """(states, reasons) for over-budget, then stale only when nothing else applies."""
    extra_states, reasons = [], []
    if _over_budget(item, limits):
        extra_states.append("over-budget")
        reasons.append(f"cycles {item.cycles_used}/{item.max_total_cycles}")
    if not states and not extra_states and _stale(activity, now, limits):
        extra_states.append("stale")
        reasons.append(f"no write for {(now - activity.newest_at).days} days")
    return extra_states, reasons


def _feature_attention(item, now, limits):
    if item.station in TERMINAL_STATIONS:
        return Attention(None, (), None)
    source = Path(item.source_path)
    activity = _activity(source)
    reasons = _needs_you_reasons(source, activity.run_status)
    states = ["needs-you"] if reasons else []
    for more_states, more_reasons in (_run_states(activity, now, limits),
                                      _budget_and_stale(item, activity, states, now, limits)):
        states += more_states
        reasons += more_reasons
    state = min(states, key=ORDER.index) if states else None
    relevant = activity.newest_at if state in ("stale", None) else activity.live_at or activity.newest_at
    return Attention(state, tuple(reasons), relevant)


def _needs_you_reasons(source, run_status):
    reasons = []
    if run_status == "awaiting_user":
        reasons.append("current run is awaiting the operator")
    questions = _open_questions(source / "STATE.md")
    if questions:
        reasons.append(f"{questions} open question(s) in STATE.md")
    if _approval_pending(source / "plan.yaml"):
        reasons.append("plan approval is pending")
    return reasons


def _over_budget(item, limits):
    if item.cycles_used is None or item.max_total_cycles is None:
        return False
    return item.max_total_cycles - item.cycles_used <= limits.over_budget_remaining_cycles


def _current_run_state(source):
    document = artifact_accessors.load_feature_json(source / "feature.json")
    runs = document.get("runs") if isinstance(document, dict) else None
    current = next((run for run in reversed(runs or []) if isinstance(run, dict)), None)
    if not current or not isinstance(current.get("id"), str):
        return None, None
    state_path = source / "runs" / current["id"] / "state.yaml"
    try:
        state = harness_yaml.load_file(str(state_path))
    except Exception:
        return None, None
    status = state.get("status") if isinstance(state, dict) else None
    return (status if isinstance(status, str) else None), _stat_time(state_path)


def _open_questions(state_md):
    try:
        lines = state_md.read_text(encoding="utf-8").splitlines()
    except OSError:
        return 0
    inside, count = False, 0
    for line in lines:
        if line.startswith("## "):
            inside = line.strip() == "## Open Questions"
            continue
        if inside and line.lstrip().startswith("- ") and line.strip().lower() not in ("- none", "- none."):
            count += 1
    return count


def _approval_pending(plan_path):
    try:
        plan = harness_yaml.load_file(str(plan_path))
    except Exception:
        return False
    approval = plan.get("approval") if isinstance(plan, dict) else None
    return isinstance(approval, dict) and approval.get("status") == "pending"


def _stat_time(path):
    try:
        return datetime.fromtimestamp(os.stat(path).st_mtime, tz=timezone.utc)
    except OSError:
        return None


def _latest(*times):
    known = [t for t in times if t is not None]
    return max(known) if known else None


def _minutes(delta):
    return int(delta.total_seconds() // 60)
