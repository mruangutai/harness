"""Project-root-scoped KPI core."""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import statistics
import subprocess

import artifact_accessors
import brief_approval
import defects
import grading
import harness_yaml

_SCHEMA = "kpi/1"
_NOT_IMPLEMENTED = "not yet implemented"
_NO_SHIP = "no ship record for this feature"


def compute(project_root: Path, window: str, generated_at=None) -> dict:
    """Compute the first KPI payload solely from the supplied project root."""
    root = Path(project_root).resolve()
    generated = _as_utc(generated_at or datetime.now(timezone.utc))
    start, end = resolve_window(window, generated)
    records = _trend_records(root)
    default_branch = _default_branch(root)
    features = [_feature(path, root, records, default_branch) for path in _feature_dirs(root)]
    selected = [item for item in features if _in_window(item["shipped_at"], start, end)]
    return {
        "schema": _SCHEMA,
        "project": {"root": str(root), "name": root.name},
        "window": window,
        "generated_at": _timestamp(generated),
        "features": selected,
        "aggregate": _aggregate(selected, root, window, generated),
        "trend": {"points": [], "unavailable": {"points": _NOT_IMPLEMENTED}},
    }


def resolve_window(token: str, generated_at: datetime) -> tuple[datetime | None, datetime]:
    """Return the inclusive window bounds relative to the supplied generation time."""
    end = _as_utc(generated_at)
    if token == "all":
        return None, end
    if token == "30d":
        return end - timedelta(days=30), end
    if token == "90d":
        return end - timedelta(days=90), end
    raise ValueError("window must be one of 30d, 90d, all")


def _feature_dirs(root: Path) -> list[Path]:
    return sorted(path.parent for path in root.glob(".harness/*/features/*/feature.json"))


def _feature(feature_dir: Path, root: Path, records: dict, default_branch: str | None) -> dict:
    document = json.loads((feature_dir / "feature.json").read_text(encoding="utf-8"))
    unavailable = _plan_unavailability(feature_dir)
    approved_on, approval_reason = brief_approval.approval_date(feature_dir)
    if approval_reason is not None:
        unavailable["approved_on"] = approval_reason
    shipped_at = records.get(document["feature_id"])
    if shipped_at is None:
        unavailable["shipped_at"] = _NO_SHIP
    cycle_time = _cycle_time(approved_on, shipped_at)
    if cycle_time is None:
        unavailable["cycle_time_days"] = approval_reason or _NO_SHIP
    insertions, deletions, files_changed, diff_reason = _change_size(root, default_branch, document["branch"])
    if diff_reason is not None:
        unavailable["insertions"] = diff_reason
        unavailable["deletions"] = diff_reason
        unavailable["files_changed"] = diff_reason
    return {
        "feature_id": document["feature_id"],
        "approved_on": approved_on,
        "shipped_at": shipped_at,
        "cycle_time_days": cycle_time,
        "runs": len(document["runs"]),
        "cycles_used": document["cycles_used"],
        "max_total_cycles": document["max_total_cycles"],
        "insertions": insertions,
        "deletions": deletions,
        "files_changed": files_changed,
        "touchpoints": None,
        "unavailable": unavailable,
    }


def _plan_unavailability(feature_dir: Path) -> dict:
    try:
        artifact_accessors.load_plan(feature_dir / "plan.yaml")
    except harness_yaml.PlanSchemaError as error:
        return {"plan": str(error)}
    except harness_yaml.YamlParseError as error:
        return {"plan": str(error)}
    return {}


def _trend_records(root: Path) -> dict:
    path = root / ".harness" / "metrics" / "trend.jsonl"
    if not path.is_file():
        return {}
    records = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        if record.get("schema") == "trend/1":
            records[record["feature_id"]] = record.get("shipped_at")
    return records


def _default_branch(root: Path) -> str | None:
    result = subprocess.run(
        ["git", "symbolic-ref", "--short", "refs/remotes/origin/HEAD"], cwd=root,
        capture_output=True, text=True, check=False,
    )
    if result.returncode != 0 or not result.stdout.startswith("origin/"):
        return None
    return result.stdout.strip().removeprefix("origin/")


def _change_size(root: Path, default_branch: str | None, branch: str) -> tuple[int | None, int | None, int | None, str | None]:
    if default_branch is None:
        return None, None, None, "project default branch is unavailable"
    result = subprocess.run(
        ["git", "diff", "--numstat", f"{default_branch}...{branch}"], cwd=root,
        capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        return None, None, None, "feature branch is unavailable"
    insertions, deletions, names = 0, 0, set()
    for line in result.stdout.splitlines():
        added, removed, name = line.split("\t", 2)
        insertions += int(added)
        deletions += int(removed)
        names.add(name)
    return insertions, deletions, len(names), None


def _cycle_time(approved_on: str | None, shipped_at: str | None) -> float | None:
    if approved_on is None or shipped_at is None:
        return None
    return (_parse_timestamp(shipped_at) - datetime.fromisoformat(approved_on).replace(tzinfo=timezone.utc)).total_seconds() / 86400


def _aggregate(features: list[dict], root: Path, window: str, generated_at: datetime) -> dict:
    measurements = [item["cycle_time_days"] for item in features if item["cycle_time_days"] is not None]
    excluded = len(features) - len(measurements)
    return {
        "throughput": _throughput(measurements, excluded),
        "rework": {
            "cycles_used": sum(item["cycles_used"] for item in features),
            "max_total_cycles": sum(item["max_total_cycles"] for item in features),
            "unavailable": {},
        },
        "touchpoints": _unimplemented(),
        "escaped_defects": defects.escaped(root, window, generated_at),
        "grading": grading.distribution(root),
        "attribution": _unimplemented(),
        "unavailable": {},
    }


def _throughput(measurements: list[float], excluded: int) -> dict:
    unavailable = {}
    if excluded:
        unavailable["excluded_features"] = f"{excluded} features lack a ship record or approval date"
    return {
        "median_cycle_time_days": statistics.median(measurements) if measurements else None,
        "measured_features": len(measurements),
        "excluded_features": excluded,
        "unavailable": unavailable,
    }


def _unimplemented() -> dict:
    return {"value": None, "unavailable": {"value": _NOT_IMPLEMENTED}}


def _in_window(shipped_at: str | None, start: datetime | None, end: datetime) -> bool:
    if shipped_at is None:
        return start is None
    point = _parse_timestamp(shipped_at)
    return point <= end and (start is None or point >= start)


def _parse_timestamp(value: str) -> datetime:
    return _as_utc(datetime.fromisoformat(value.replace("Z", "+00:00")))


def _as_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def _timestamp(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")
