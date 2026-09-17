"""Commit attribution KPI sourced from harness commit prefixes."""
from datetime import datetime, timezone
from pathlib import Path
import re
import subprocess

import artifact_accessors
import kpi

_PREFIX = re.compile(r"^\[harness:([^]]+)\]")
_TASK = re.compile(r"t-\d+\Z")
_FEATURE = re.compile(r"(?:FEAT|BUG)-\d+\Z")
_BRANCH_FEATURE = re.compile(r"(?:FEAT|BUG)-\d+")
_UNATTRIBUTED = ("no_prefix", "human", "feature_only", "unresolvable_step_id")


def by_tier(project_root: Path, window: str, generated_at=None) -> dict:
    """Return model-tier usage and named unattributed commit buckets."""
    root = Path(project_root).resolve()
    start, end = kpi.resolve_window(window, generated_at or datetime.now(timezone.utc))
    tiers, unattributed = _buckets(root, start, end)
    return _result(tiers, unattributed)


def _buckets(root: Path, start: datetime | None, end: datetime) -> tuple[dict, dict]:
    plans = {}
    tiers = {}
    unattributed = {bucket: 0 for bucket in _UNATTRIBUTED}
    for commit_id, date, subject in _commits(root):
        if _in_window(date, start, end):
            _record(tiers, unattributed, _tier(root, commit_id, subject, plans))
    return tiers, unattributed


def _record(tiers: dict, unattributed: dict, tier: str) -> None:
    if tier in unattributed:
        unattributed[tier] += 1
    else:
        tiers[tier] = tiers.get(tier, 0) + 1


def _result(tiers: dict, unattributed: dict) -> dict:
    attributable = sum(tiers.values())
    total = attributable + sum(unattributed.values())
    return {
        "by_tier": tiers,
        "unattributed": unattributed,
        "attributable_share": attributable / total if total else 0,
        "total_commits": total,
    }


def _commits(root: Path) -> list[tuple[str, datetime, str]]:
    output = _git(root, ["log", "--format=%H%x09%aI%x09%s"])
    return [_commit(line) for line in output.splitlines()]


def _commit(line: str) -> tuple[str, datetime, str]:
    commit_id, value, subject = line.split("\t", maxsplit=2)
    return commit_id, _date(value), subject


def _tier(root: Path, commit_id: str, subject: str, plans: dict) -> str:
    match = _PREFIX.match(subject)
    if match is None:
        return "no_prefix"
    for element in match.group(1).split(","):
        tier = _element_tier(root, commit_id, element.strip(), plans)
        if tier is not None:
            return tier
    return "unresolvable_step_id"


def _element_tier(root: Path, commit_id: str, element: str, plans: dict) -> str | None:
    if element == "human":
        return "human"
    if _FEATURE.fullmatch(element):
        return "feature_only"
    if not _TASK.fullmatch(element):
        return None
    feature_id = _branch_feature(root, commit_id)
    if feature_id is None:
        return None
    plan = _plan(root, feature_id, plans)
    task = next((item for item in plan.get("tasks", []) if item.get("id") == element.upper()), None)
    if task is None:
        return None
    return _model(root, task.get("execution_agent"))


def _branch_feature(root: Path, commit_id: str) -> str | None:
    branches = _git(root, ["branch", "--contains", commit_id, "--format=%(refname:short)"])
    for branch in branches.splitlines():
        match = _BRANCH_FEATURE.search(branch)
        if match is not None:
            return match.group()
    return None


def _plan(root: Path, feature_id: str, plans: dict) -> dict:
    if feature_id not in plans:
        paths = sorted(root.glob(f".harness/*/features/{feature_id}/plan.yaml"))
        plans[feature_id] = artifact_accessors.load_plan(paths[0]) if paths else {}
    return plans[feature_id]


def _model(root: Path, agent: str | None) -> str | None:
    if not agent:
        return None
    path = root / ".claude" / "agents" / f"{agent}.md"
    if not path.is_file():
        return None
    match = re.search(r"^model:\s*(\S+)\s*$", path.read_text(encoding="utf-8"), re.MULTILINE)
    return match.group(1) if match is not None else None


def _git(root: Path, arguments: list[str]) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *arguments],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "git history cannot be read")
    return result.stdout


def _date(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _in_window(point: datetime, start: datetime | None, end: datetime) -> bool:
    return point <= end and (start is None or point >= start)
