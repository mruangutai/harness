"""Project-root-scoped KPI core."""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import statistics
import subprocess

import artifact_accessors
import attribution
import brief_approval
import defects
import grading
import harness_yaml
import touchpoints
import trend

_SCHEMA = "kpi/1"
_NOT_IMPLEMENTED = "not yet implemented"
_NO_SHIP = "no ship record for this feature"
_TREND_FIELDS = (
    "cycle_time_days", "runs", "cycles_used", "max_total_cycles",
    "insertions", "deletions", "files_changed", "touchpoints",
    "grade", "attribution",
)



def compute(project_root: Path, window: str, generated_at=None) -> dict:
    """Compute the first KPI payload solely from the supplied project root."""
    root = Path(project_root).resolve()
    generated = _as_utc(generated_at or datetime.now(timezone.utc))
    trend_payload = trend.read(root, window, generated)
    features = _selected_features(root, window, generated, trend_payload["records"])
    return _payload(root, window, generated, features, trend_payload)


def _selected_features(root: Path, window: str, generated: datetime, records: dict) -> list[dict]:
    start, end = resolve_window(window, generated)
    metadata = [_feature_metadata(path, records) for path in _feature_dirs(root)]
    selected = [item for item in metadata if _in_window(item[2], start, end)]
    default_branch = _default_branch(root)
    sizes = _change_sizes(root, default_branch, [document["branch"] for _, document, _, _ in selected])
    return [_feature_from_metadata(path, root, document, record, default_branch, sizes[document["branch"]])
            for path, document, _shipped_at, record in selected]


def _payload(root: Path, window: str, generated: datetime, features: list[dict], trend_payload: dict) -> dict:
    return {
        "schema": _SCHEMA,
        "project": {"root": str(root), "name": root.name},
        "window": window,
        "generated_at": _timestamp(generated),
        "features": features,
        "aggregate": _aggregate(features, root, window, generated),
        "trend": trend_payload,
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


def _feature_metadata(feature_dir: Path, records: dict) -> tuple[Path, dict, str | None, dict | None]:
    document = json.loads((feature_dir / "feature.json").read_text(encoding="utf-8"))
    record = records.get(document["feature_id"])
    return feature_dir, document, record.get("shipped_at") if record else None, record


def _feature(feature_dir: Path, root: Path, records: dict, default_branch: str | None) -> dict:
    path, document, _shipped_at, record = _feature_metadata(feature_dir, records)
    return _feature_from_metadata(path, root, document, record, default_branch,
                                  _change_size(root, default_branch, document["branch"]))


def _feature_from_metadata(feature_dir: Path, root: Path, document: dict, record: dict | None,
                           default_branch: str | None,
                           change_size: tuple[int | None, int | None, int | None, str | None]) -> dict:
    unavailable = _plan_unavailability(feature_dir)
    approved_on, approval_reason = brief_approval.approval_date(feature_dir)
    if approval_reason is not None:
        unavailable["approved_on"] = approval_reason
    shipped_at = record.get("shipped_at") if record else None
    if shipped_at is None:
        unavailable["shipped_at"] = _NO_SHIP
    cycle_time = _cycle_time(approved_on, shipped_at)
    if cycle_time is None:
        unavailable["cycle_time_days"] = approval_reason or _NO_SHIP
    insertions, deletions, files_changed, diff_reason = change_size
    if diff_reason is not None:
        unavailable["insertions"] = diff_reason
        unavailable["deletions"] = diff_reason
        unavailable["files_changed"] = diff_reason
    touchpoint_count, touchpoint_reason = touchpoints.count(root, document["feature_id"])
    if touchpoint_reason is not None:
        unavailable["touchpoints"] = touchpoint_reason
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
        "touchpoints": touchpoint_count,
        "trend": _feature_trend(record),
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


def _feature_trend(record: dict | None) -> dict:
    if record is None:
        return {
            field: None for field in _TREND_FIELDS
        } | {"unavailable": {field: "shipped before metrics existed" for field in _TREND_FIELDS}}
    return {
        field: record.get(field) for field in _TREND_FIELDS
    } | {"unavailable": record.get("unavailable", {})}


def _default_branch(root: Path) -> str | None:
    result = subprocess.run(
        ["git", "symbolic-ref", "--short", "refs/remotes/origin/HEAD"], cwd=root,
        capture_output=True, text=True, check=False,
    )
    if result.returncode != 0 or not result.stdout.startswith("origin/"):
        return None
    return result.stdout.strip().removeprefix("origin/")


def _change_sizes(root: Path, default_branch: str | None, branches: list[str]) -> dict:
    """Resolve each requested branch once, avoiding diffs for absent refs."""
    if default_branch is None:
        unavailable = (None, None, None, "project default branch is unavailable")
        return {branch: unavailable for branch in branches}
    available = _available_branches(root)
    unavailable = (None, None, None, "feature branch is unavailable")
    return {
        branch: _change_size(root, default_branch, branch) if branch in available else unavailable
        for branch in dict.fromkeys(branches)
    }


def _available_branches(root: Path) -> set[str]:
    result = subprocess.run(
        ["git", "for-each-ref", "--format=%(refname)", "refs/heads/", "refs/remotes/"], cwd=root,
        capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        return set()
    available = set()
    for ref in result.stdout.splitlines():
        available.update(_branch_names(ref))
    return available


def _branch_names(ref: str) -> set[str]:
    if ref.startswith("refs/heads/"):
        return {ref.removeprefix("refs/heads/")}
    if not ref.startswith("refs/remotes/"):
        return set()
    remote_ref = ref.removeprefix("refs/remotes/")
    remote, separator, branch = remote_ref.partition("/")
    if not separator or branch == "HEAD":
        return {remote_ref}
    return {remote_ref, branch}
    return available


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
        if added != "-":
            insertions += int(added)
        if removed != "-":
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
        "touchpoints": _touchpoint_aggregate(features),
        "escaped_defects": defects.escaped(root, window, generated_at),
        "grading": grading.distribution(root),
        "attribution": attribution.by_tier(root, window, generated_at),
        "unavailable": {},
    }



def _touchpoint_aggregate(features: list[dict]) -> dict:
    tracked = [item["touchpoints"] for item in features if item["touchpoints"] is not None]
    return {
        "mean": statistics.mean(tracked) if tracked else None,
        "zero_count": sum(value == 0 for value in tracked),
        "not_tracked_count": len(features) - len(tracked),
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
