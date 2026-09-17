#!/usr/bin/env python3
"""Append-only blocking-human-touchpoint instrumentation."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess

import brief_approval

_EVENTS = ("approval_request", "escalation", "uat_request")
_NO_EPOCH = (
    "touchpoints were not tracked in this project - no .harness/metrics/"
    "instrumented_at epoch exists, so no count here is a measurement"
)
_NO_START = (
    "touchpoints cannot be dated for this feature - it has neither an approval date in its "
    "BRIEF.md nor a commit that added its directory, so pre-instrumentation and "
    "post-instrumentation cannot be told apart"
)
_NEVER_TRACKED = (
    "this feature predates touchpoint instrumentation in this project - touchpoints "
    "were never tracked for it"
)

_run = subprocess.run


def record(project_root: Path, feature_id: str, event: str, note: str | None = None) -> None:
    """Append one valid touchpoint and establish the project epoch once."""
    _validate_event(event)
    _validate_note(note)
    root = Path(project_root).resolve()
    _write_epoch(root)
    path = _touchpoint_path(root, feature_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    value = {"at": _timestamp(), "event": event}
    if note is not None:
        value["note"] = note
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(value, separators=(",", ":")) + "\n")


def instrumentation_epoch(project_root: Path) -> datetime | None:
    """Return the one-time instrumentation instant, if this project has one."""
    path = _epoch_path(Path(project_root))
    if not path.is_file():
        return None
    return _parse_timestamp(path.read_text(encoding="utf-8").splitlines()[0])


def feature_start(project_root: Path, feature_id: str) -> datetime | None:
    """Return the feature approval instant, falling back to its first directory commit."""
    root = Path(project_root).resolve()
    feature_dir = _feature_dir(root, feature_id)
    approved_on, _reason = brief_approval.approval_date(feature_dir)
    if approved_on is not None:
        return datetime.fromisoformat(approved_on).replace(tzinfo=timezone.utc)
    return _first_feature_commit(root, feature_dir)


def count(project_root: Path, feature_id: str) -> tuple[int | None, str | None]:
    """Return the complete touchpoint count or its specific unavailability reason."""
    root = Path(project_root).resolve()
    epoch = instrumentation_epoch(root)
    if epoch is None:
        return None, _NO_EPOCH
    started = feature_start(root, feature_id)
    if started is None:
        return None, _NO_START
    path = _touchpoint_path(root, feature_id)
    entries = _line_count(path)
    if started.date() < epoch.date():
        return None, _preinstrumentation_reason(entries)
    return entries, None


def _write_epoch(root: Path) -> None:
    path = _epoch_path(root)
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_timestamp() + "\n", encoding="utf-8")


def _epoch_path(root: Path) -> Path:
    return root / ".harness" / "metrics" / "instrumented_at"

def _feature_dir(root: Path, feature_id: str) -> Path:
    matches = sorted(root.glob(f".harness/*/features/{feature_id}"))
    if not matches:
        raise ValueError(f"feature directory not found: {feature_id}")
    return matches[0]


def _touchpoint_path(root: Path, feature_id: str) -> Path:
    return _feature_dir(root, feature_id) / "touchpoints.jsonl"


def _first_feature_commit(root: Path, feature_dir: Path) -> datetime | None:
    relative = feature_dir.relative_to(root)
    result = _run(
        ["git", "-C", str(root), "log", "--diff-filter=A", "--format=%aI", "-1", "--", str(relative)],
        capture_output=True, text=True, check=False,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return None
    try:
        return _parse_timestamp(result.stdout.strip())
    except ValueError:
        return None


def _line_count(path: Path) -> int:
    if not path.is_file():
        return 0
    return len(path.read_text(encoding="utf-8").splitlines())


def _preinstrumentation_reason(entries: int) -> str:
    if entries == 0:
        return _NEVER_TRACKED
    return (
        "this feature started before touchpoint instrumentation in this project - "
        f"the {entries} touchpoints recorded for it after instrumentation began are not a complete count"
    )


def _validate_event(event: str) -> None:
    if event not in _EVENTS:
        raise ValueError("event must be one of approval_request, escalation, uat_request")


def _validate_note(note: str | None) -> None:
    if note is not None and ("\n" in note or "\r" in note):
        raise ValueError("note must be one line")


def _parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _root_from_cwd() -> Path:
    result = _run(
        ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        raise ValueError("current directory is not inside a git repository")
    marker = Path(result.stdout.strip()) / ".harness" / "team-config.yaml"
    if not marker.is_file():
        raise ValueError(f"repository is missing required harness manifest: {marker}")
    return marker.parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    record_parser = commands.add_parser("record")
    count_parser = commands.add_parser("count")
    for command in (record_parser, count_parser):
        command.add_argument("--root", type=Path)
        command.add_argument("--feature", required=True)
    record_parser.add_argument("--event", choices=_EVENTS, required=True)
    record_parser.add_argument("--note")
    args = parser.parse_args()
    root = args.root or _root_from_cwd()
    if args.command == "record":
        record(root, args.feature, args.event, args.note)
        return 0
    value, reason = count(root, args.feature)
    print(value if value is not None else f"unavailable: {reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
