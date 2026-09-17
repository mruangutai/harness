"""Append-only, gap-aware dashboard trend persistence."""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path

_SCHEMA = "trend/1"
_PATH = Path(".harness/metrics/trend.jsonl")
_FIELDS = ("cycle_time_days", "runs", "cycles_used", "max_total_cycles", "insertions", "deletions", "files_changed", "touchpoints", "grade", "attribution")


def append(project_root: Path, record: dict) -> None:
    """Append exactly one canonical record, refusing a local duplicate feature."""
    root = Path(project_root).resolve()
    path = root / _PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    prior = path.read_bytes() if path.exists() else b""
    _validate_record(record)
    if record["feature_id"] in _feature_ids(prior):
        raise ValueError(f"duplicate trend record for {record['feature_id']}")
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
    if path.read_bytes()[:len(prior)] != prior:
        raise RuntimeError("trend append disturbed existing bytes")


def read(project_root: Path, window: str, generated_at: datetime) -> dict:
    """Return windowed records, field series, and ISO-week ship counts."""
    root = Path(project_root).resolve()
    path = root / _PATH
    if not path.exists():
        return _empty("trend record file is missing")
    contents = path.read_text(encoding="utf-8")
    if not contents:
        return _empty("trend record file has zero lines")
    records, unavailable = _records(contents)
    start, end = _window(window, generated_at)
    selected = {key: value for key, value in records.items() if _in_window(value, start, end)}
    return {
        "records": selected,
        "unavailable": unavailable,
        "series": _series(selected),
        "weekly": _weekly(selected, records, start, end),
    }


def _validate_record(record: dict) -> None:
    if record.get("schema") != _SCHEMA:
        raise ValueError(f"trend schema must be {_SCHEMA}")
    if not record.get("feature_id"):
        raise ValueError("trend record requires feature_id")
    _timestamp(record["shipped_at"])


def _feature_ids(contents: bytes) -> set[str]:
    identifiers = set()
    for line in contents.splitlines():
        try:
            identifiers.add(json.loads(line).get("feature_id"))
        except json.JSONDecodeError:
            continue
    return identifiers


def _records(contents: str) -> tuple[dict, dict]:
    records, unavailable = {}, {}
    for number, line in enumerate(contents.splitlines(), start=1):
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            unavailable[f"line_{number}"] = "trend record line does not parse"
            continue
        if record.get("schema") != _SCHEMA:
            unavailable[f"line_{number}"] = f"trend record schema is {record.get('schema')!r}, not {_SCHEMA}"
            continue
        if not record.get("feature_id"):
            unavailable[f"line_{number}"] = "trend record has no feature_id"
            continue
        try:
            _timestamp(record["shipped_at"])
        except (KeyError, ValueError):
            unavailable[f"line_{number}"] = "trend record has invalid shipped_at"
            continue
        _atomic_nested(record, unavailable, number)
        prior = records.get(record["feature_id"])
        if prior is None or _timestamp(record["shipped_at"]) > _timestamp(prior["shipped_at"]):
            if prior is not None:
                unavailable[record["feature_id"]] = _duplicate_reason(prior, record)
            records[record["feature_id"]] = record
        else:
            unavailable[record["feature_id"]] = _duplicate_reason(record, prior)
    return records, unavailable


def _atomic_nested(record: dict, unavailable: dict, number: int) -> None:
    for field in ("grade", "attribution"):
        if field not in record or not isinstance(record[field], dict):
            unavailable[f"line_{number}:{field}"] = f"trend record {field} is unavailable as a whole"


def _duplicate_reason(discarded: dict, kept: dict) -> str:
    return f"duplicate feature record discarded: {discarded['shipped_at']} kept {kept['shipped_at']}"


def _window(window: str, generated_at: datetime) -> tuple[datetime | None, datetime]:
    import kpi
    return kpi.resolve_window(window, generated_at)


def _series(records: dict) -> dict:
    output = {}
    for field in _FIELDS:
        points = [{"feature_id": key, "value": record.get(field)} for key, record in records.items()]
        output[field] = {"points": points, "segments": _segments(points)}
    return output


def _weekly(records: dict, all_records: dict, start: datetime | None, end: datetime) -> dict:
    if not all_records:
        return {"points": [], "segments": [], "week_count": 0, "empty_bucket_count": 0, "unavailable": {"weekly": "no ship records exist"}}
    first = _monday(min(_timestamp(item["shipped_at"]) for item in all_records.values())) if start is None else _monday(start)
    last = _monday(end)
    points = [_bucket(first + timedelta(days=7 * offset), records, start, end) for offset in range(((last - first).days // 7) + 1)]
    return {"points": points, "segments": _segments(points), "week_count": len(points), "empty_bucket_count": sum(point["value"] is None for point in points), "unavailable": {}}


def _bucket(week: datetime, records: dict, start: datetime | None, end: datetime) -> dict:
    week_end = week + timedelta(days=7)
    lower, upper = max(week, start) if start else week, min(week_end, end + timedelta(microseconds=1))
    partial = lower != week or upper != week_end
    count = sum(lower <= _timestamp(record["shipped_at"]) < upper for record in records.values())
    point = {"week": week.date().isoformat(), "value": count or None, "partial": partial, "bounds": {"start": _render(lower), "end": _render(upper)}}
    if count == 0:
        point["reason"] = _empty_week_reason(week, lower, upper, partial)
    return point


def _empty_week_reason(week: datetime, lower: datetime, upper: datetime, partial: bool) -> str:
    if partial:
        return f"no ship record between {_render(lower)} and {_render(upper)}, the part of that week inside the window"
    return f"no ship record in the week of {week.date().isoformat()}"


def _segments(points: list[dict]) -> list[list[dict]]:
    segments, current = [], []
    for point in points:
        if point["value"] is None:
            if current:
                segments.append(current)
                current = []
        else:
            current.append(point)
    return segments + ([current] if current else [])


def _empty(reason: str) -> dict:
    return {"records": {}, "unavailable": {"records": reason}, "series": {}, "weekly": {"points": [], "segments": [], "week_count": 0, "empty_bucket_count": 0, "unavailable": {"weekly": reason}}}


def _timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _monday(value: datetime) -> datetime:
    value = value.astimezone(timezone.utc)
    return (value - timedelta(days=value.weekday(), hours=value.hour, minutes=value.minute, seconds=value.second, microseconds=value.microsecond))


def _in_window(record: dict, start: datetime | None, end: datetime) -> bool:
    point = _timestamp(record["shipped_at"])
    return point <= end and (start is None or point >= start)


def _render(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
