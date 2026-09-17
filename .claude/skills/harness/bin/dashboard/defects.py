"""Escaped-defect KPI sourced from local git history."""
from datetime import datetime, timezone
from pathlib import Path
import re
from subprocess import run

import kpi


_SOURCING_RULE = (
    "BUG-NN feature units first added in the selected window and Revert commits are counted; "
    "subjects beginning with fix are excluded because they are usually within-feature repairs."
)
_BUG_UNIT = re.compile(r"BUG-\d+\Z")


def escaped(project_root: Path, window: str, generated_at=None) -> dict:
    """Return escaped defects in the requested KPI window."""
    root = Path(project_root).resolve()
    generated = generated_at or datetime.now(timezone.utc)
    start, end = kpi.resolve_window(window, generated)
    try:
        items = _bug_units(root, start, end) + _reverts(root, start, end)
    except RuntimeError as error:
        return _unavailable(window, str(error))
    return {
        "count": len(items),
        "items": items,
        "window": window,
        "sourcing_rule": _SOURCING_RULE,
    }


def _bug_units(root: Path, start: datetime | None, end: datetime) -> list[dict]:
    items = []
    for feature_dir in sorted((root / ".harness").glob("*/features/BUG-*")):
        if not feature_dir.is_dir() or not _BUG_UNIT.fullmatch(feature_dir.name):
            continue
        date, subject = _first_addition(root, feature_dir.relative_to(root))
        if _in_window(date, start, end):
            items.append({
                "kind": "bug_unit",
                "id": feature_dir.name,
                "date": date.isoformat().replace("+00:00", "Z"),
                "subject": subject,
            })
    return items


def _reverts(root: Path, start: datetime | None, end: datetime) -> list[dict]:
    output = _git(root, ["log", "--format=%H%x09%aI%x09%s"])
    items = []
    for line in output.splitlines():
        commit_id, date, subject = line.split("\t", maxsplit=2)
        point = _parse_date(date)
        if subject.startswith("Revert ") and _in_window(point, start, end):
            items.append({
                "kind": "revert",
                "id": commit_id,
                "date": point.isoformat().replace("+00:00", "Z"),
                "subject": subject,
            })
    return items


def _first_addition(root: Path, feature_dir: Path) -> tuple[datetime, str]:
    output = _git(root, ["log", "--diff-filter=A", "--format=%aI%x09%s", "-1", "--", str(feature_dir)])
    date, subject = output.strip().split("\t", maxsplit=1)
    return _parse_date(date), subject


def _git(root: Path, arguments: list[str]) -> str:
    result = run(
        ["git", "-C", str(root), *arguments],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "git history cannot be read")
    if not result.stdout.strip():
        raise RuntimeError("git history cannot be read")
    return result.stdout


def _in_window(point: datetime, start: datetime | None, end: datetime) -> bool:
    return point <= end and (start is None or point >= start)


def _parse_date(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _unavailable(window: str, reason: str) -> dict:
    return {
        "count": None,
        "items": [],
        "window": window,
        "sourcing_rule": _SOURCING_RULE,
        "unavailable": {"count": f"git history cannot be read: {reason}"},
    }
