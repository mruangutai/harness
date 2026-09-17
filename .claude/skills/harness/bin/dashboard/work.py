"""Offline disk collection of fleet work for the dashboard operational lane."""
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import os
from pathlib import Path
import re

import artifact_accessors
import brief_approval
import factory_config
import grilling_status
import harness_yaml
import worktree_terminal

_PREFIX = re.compile(r"^(?:FEAT|BUG)-\d+")

_PHASES = ("plan", "build", "validate")
_SQUADS = {"product": "plan", "eng": "build", "validator": "validate"}


@dataclass(frozen=True)
class WorkItem:
    """One serializable work record selected from a complete on-disk source copy."""
    id: str
    kind: str
    segment: str
    display_name: str
    station: str | None
    grilling_status: str | None
    run_status: str | None
    run_started_at: str | None
    run_ended_at: str | None
    elapsed_total: int | None
    elapsed_plan: int | None
    elapsed_build: int | None
    elapsed_validate: int | None
    phase: str | None
    run_count: int | None
    tokens: dict | None
    updated_at: str | None
    cycles_used: int | None
    max_total_cycles: int | None
    main_path: str | None
    worktree_path: str | None
    source_path: str
    error: str | None
    repository: str | None = None
    canonical_path: str | None = None
    checkout_role: str | None = None
    head: str | None = None
    feature_id: str | None = None
    feature_status: str | None = None

    def to_dict(self):
        """Return the JSON-ready representation of this typed record."""
        return asdict(self)


def collect(root: Path | str) -> list[WorkItem]:
    """Collect feature, grilling, and registered-worktree rows from disk."""
    return collect_fleet(root)[0]


def collect_fleet(root: Path | str) -> tuple[list[WorkItem], list[dict]]:
    """Collect fleet rows and configured clones that could not be enumerated."""
    root = Path(root).resolve()
    entries, errors = _registered_worktree_entries(root)
    linked_worktrees = [entry[0] for entry in entries if entry[2] == "linked"]
    classifications = _worktree_classifications(root)
    items = []
    for feature_dir in sorted(root.glob(".harness/*/features/*")):
        if feature_dir.is_dir():
            items.append(_feature_item(root, feature_dir, linked_worktrees))
    feature_worktrees = {Path(item.worktree_path): item.display_name for item in items
                         if item.worktree_path is not None}
    items.extend(_worktree_item(entry, classifications, feature_worktrees) for entry in entries)
    items.extend(_grilling_items(root))
    return sorted(items, key=lambda item: item.id), errors


def _registered_worktree_entries(root: Path) -> tuple[list[tuple[Path, str, str]], list[dict]]:
    entries = _repository_worktree_entries(root, "harness")
    repositories, errors = fleet_repositories(root)
    for repository, workspace in repositories.items():
        if repository != "harness":
            entries.extend(_repository_worktree_entries(workspace, repository))
    unique = {}
    for path, repository, role in entries:
        unique.setdefault(path, (path, repository, role))
    return sorted(unique.values(), key=lambda entry: str(entry[0])), errors


def fleet_repositories(root: Path | str, require_all: bool = True) -> tuple[dict[str, Path], list[dict]]:
    """Return readable fleet roots and configured clones unavailable on disk."""
    root = Path(root).resolve()
    repositories = {"harness": root}
    fleet_path = root / ".harness" / "factory" / "fleet.yaml"
    if not require_all or not fleet_path.is_file():
        return repositories, []
    fleet = artifact_accessors.load_fleet(fleet_path)
    errors = []
    for entry in fleet["repos"]:
        configured = entry["name"]
        repository = factory_config.segment_of(configured)
        workspace = Path(factory_config.workspace_path(fleet, configured))
        if repository in repositories:
            raise ValueError(f"configured repository {repository} cannot be enumerated at {workspace}")
        if workspace.is_dir():
            repositories[repository] = workspace
        else:
            errors.append({
                "repo": repository,
                "path": str(workspace),
                "reason": f"configured repository {repository} cannot be enumerated at {workspace}",
            })
    return repositories, errors


def _repository_worktree_entries(root: Path, repository: str) -> list[tuple[Path, str, str]]:
    return [(Path(path).resolve(), repository, "primary" if i == 0 else "linked")
            for i, path in enumerate(worktree_terminal._worktree_paths(str(root)))]


def _worktree_classifications(root: Path) -> dict[Path, dict]:
    return {Path(record["path"]).resolve(): record
            for record in worktree_terminal.classify_all(str(root))}


def _worktree_item(entry: tuple[Path, str, str], classifications: dict[Path, dict],
                   feature_worktrees: dict[Path, str]) -> WorkItem:
    path, repository, role = entry
    record = classifications.get(path, {})
    feature_id = record.get("feature_id") or feature_worktrees.get(path)
    status = _worktree_status(record, feature_id)
    return WorkItem(
        id=f"worktree:{repository}:{path}", kind="worktree", segment=repository.rsplit("/", 1)[-1],
        display_name=path.name, station=None, grilling_status=None, run_status=None,
        run_started_at=None, run_ended_at=None, elapsed_total=None, elapsed_plan=None,
        elapsed_build=None, elapsed_validate=None, phase=None, run_count=None, tokens=None,
        updated_at=None, cycles_used=None, max_total_cycles=None, main_path=None,
        worktree_path=None, source_path=str(path),
        error=record.get("reason") if record.get("klass") == "unresolved" else None,
        repository=record.get("repo") or repository, canonical_path=str(path),
        checkout_role=role, head=_head_identity(path), feature_id=feature_id,
        feature_status=status,
    )


def _worktree_status(record: dict, feature_id: str | None) -> str:
    if record.get("klass") == "terminal":
        return "terminal"
    if record.get("klass") == "exempt_absent" or feature_id is None:
        return "absent"
    return "active"


def _head_identity(path: Path) -> str:
    branch = worktree_terminal._run_git(["symbolic-ref", "--short", "-q", "HEAD"], str(path))
    if branch is not None and branch.returncode == 0 and branch.stdout.strip():
        return branch.stdout.strip()
    commit = worktree_terminal._run_git(["rev-parse", "--short", "HEAD"], str(path))
    suffix = commit.stdout.strip() if commit is not None and commit.returncode == 0 else "unknown"
    return f"detached:{suffix}"

def _feature_item(root: Path, main_dir: Path, worktrees: list[Path]) -> WorkItem:
    segment = main_dir.parent.parent.name
    name = main_dir.name
    worktree = _matching_worktree(main_dir, worktrees)
    selected = _selected_feature_dir(worktree, main_dir, root)
    main_path = str(main_dir.resolve())
    worktree_path = str(worktree) if worktree else None
    return _read_feature(selected, name, segment, main_path, worktree_path)


def _matching_worktree(main_dir: Path, worktrees: list[Path]) -> Path | None:
    exact = _unique_named(worktrees, main_dir.name)
    return exact if exact is not None else _unique_prefix(worktrees, _feature_prefix(main_dir.name))


def _unique_named(paths: list[Path], name: str) -> Path | None:
    return _one_or_none([path for path in paths if path.name == name])


def _unique_prefix(paths: list[Path], prefix: str | None) -> Path | None:
    if prefix is None:
        return None
    return _one_or_none([path for path in paths if path.name.startswith(prefix)])


def _one_or_none(paths: list[Path]) -> Path | None:
    return paths[0] if len(paths) == 1 else None


def _feature_prefix(name: str) -> str | None:
    matched = _PREFIX.match(name)
    return matched.group(0) if matched else None


def _worktree_feature_dir(worktree: Path, main_dir: Path, root: Path) -> Path:
    return worktree / main_dir.relative_to(root)






def _selected_feature_dir(worktree: Path | None, main_dir: Path, root: Path) -> Path:
    candidate = _worktree_feature_dir(worktree, main_dir, root) if worktree else None
    readable = candidate is not None and candidate.is_dir() and os.access(candidate, os.R_OK | os.X_OK)
    return candidate if readable else main_dir
def _read_feature(source: Path, name: str, segment: str, main_path: str,
                  worktree_path: str | None) -> WorkItem:
    try:
        document = artifact_accessors.load_feature_json(source / "feature.json")
        if document is None:
            raise ValueError("feature.json is missing")
    except Exception as error:
        return _feature_error(source, name, segment, main_path, worktree_path, "feature.json", error)
    try:
        return _loaded_feature(source, name, segment, main_path, worktree_path, document)
    except Exception as error:
        return _feature_error(source, name, segment, main_path, worktree_path, "plan.yaml", error)

def _loaded_feature(source: Path, name: str, segment: str, main_path: str,
                    worktree_path: str | None, document: dict) -> WorkItem:
    run = _latest_run(document)
    timing = _timing(source, document)
    return WorkItem(
        id=f"{_kind(name)}:{segment}:{name}", kind=_kind(name), segment=segment,
        display_name=name, station=_station(source), grilling_status=None,
        run_status=run.get("verdict"), run_started_at=run.get("started_at"),
        run_ended_at=run.get("ended_at"), elapsed_total=timing["total"],
        elapsed_plan=timing["plan"], elapsed_build=timing["build"],
        elapsed_validate=timing["validate"], phase=timing["phase"],
        run_count=timing["run_count"], tokens=timing["tokens"], updated_at=_updated_at(document),
        cycles_used=_int_or_none(document.get("cycles_used")),
        max_total_cycles=_int_or_none(document.get("max_total_cycles")),
        main_path=main_path, worktree_path=worktree_path,
        source_path=str(source.resolve()), error=None,
    )


def _feature_error(source: Path, name: str, segment: str, main_path: str,
                   worktree_path: str | None, source_name: str, error: Exception) -> WorkItem:
    return WorkItem(
        id=f"{_kind(name)}:{segment}:{name}", kind=_kind(name), segment=segment,
        display_name=name, station=None, grilling_status=None, run_status=None,
        run_started_at=None, run_ended_at=None, elapsed_total=None, elapsed_plan=None,
        elapsed_build=None, elapsed_validate=None, phase=None, run_count=None, tokens=None,
        updated_at=None, cycles_used=None, max_total_cycles=None, main_path=main_path,
        worktree_path=worktree_path, source_path=str(source.resolve()),
        error=f"{source_name}: {error}",
    )


def _kind(name: str) -> str:
    return "bug" if name.startswith("BUG-") else "feature"


def _station(source: Path) -> str | None:
    plan = source / "plan.yaml"
    if not plan.exists():
        return None
    document = harness_yaml.load_file(plan)
    return document.get("status") if isinstance(document, dict) else None


def _latest_run(document: dict) -> dict:
    runs = document.get("runs")
    if not isinstance(runs, list):
        return {}
    return next((run for run in reversed(runs) if isinstance(run, dict)), {})


def _updated_at(document: dict) -> str | None:
    times = []
    for run in document.get("runs", []):
        if isinstance(run, dict):
            times.extend(value for value in (run.get("started_at"), run.get("ended_at"))
                         if isinstance(value, str))
    return max(times) if times else None


def _int_or_none(value) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _timing(source: Path, document: dict) -> dict:
    runs = [run for run in document.get("runs", []) if isinstance(run, dict)]
    approval, _reason = brief_approval.approval_date(source)
    start = _instant(f"{approval}T00:00:00Z") if approval else None
    boundaries = _boundaries(source, runs)
    phase = _phase(boundaries)
    end = _terminal_end(runs) if _station(source) == "done" else _now()
    total = _seconds(start, end)
    elapsed = _phase_elapsed(start, boundaries, phase, end)
    return {"total": total, **elapsed, "phase": phase, "run_count": len(runs),
            "tokens": _tokens(runs)}


def _boundaries(source: Path, runs: list[dict]) -> dict:
    result = {}
    for phase in _PHASES:
        note = source / "notes" / f"handoff-{phase}.md"
        if not note.is_file():
            continue
        match = re.search(r"\bseq-(\d+)\b", note.read_text(encoding="utf-8"))
        if match is None:
            continue
        index = int(match.group(1)) - 1
        if 0 <= index < len(runs):
            result[phase] = _instant(runs[index].get("ended_at"))
    return result


def _phase(boundaries: dict) -> str:
    for phase in _PHASES:
        if phase not in boundaries:
            return phase
    return "done"


def _terminal_end(runs: list[dict]) -> datetime | None:
    for run in reversed(runs):
        end = _instant(run.get("ended_at"))
        if end is not None:
            return end
    return None


def _phase_elapsed(start: datetime | None, boundaries: dict, phase: str,
                   end: datetime | None) -> dict:
    result = {}
    prior = start
    for name in _PHASES:
        boundary = boundaries.get(name)
        if boundary is not None:
            result[name] = _seconds(prior, boundary)
            prior = boundary
        elif name == phase:
            result[name] = _seconds(prior, end)
        else:
            result[name] = None
    return result


def _tokens(runs: list[dict]) -> dict:
    measured = _measured_tokens(runs)
    total_runs = len(runs)
    unmeasured = total_runs - len(measured)
    return {
        "total": sum(measured) if measured else None,
        "measured_runs": len(measured),
        "total_runs": total_runs,
        "unmeasured_runs": unmeasured,
        "by_phase": _tokens_by_phase(runs),
        "presentation": f"unmeasured {unmeasured} of {total_runs} runs",
    }


def _measured_tokens(runs: list[dict]) -> list[int]:
    return [value for run in runs if (value := _int_or_none(run.get("tokens"))) is not None]


def _tokens_by_phase(runs: list[dict]) -> dict:
    return {phase: _phase_tokens(runs, phase) for phase in _PHASES}


def _phase_tokens(runs: list[dict], phase: str) -> int | None:
    values = _measured_tokens([run for run in runs if _SQUADS.get(run.get("squad")) == phase])
    return sum(values) if values else None


def _instant(value) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def _seconds(start: datetime | None, end: datetime | None) -> int | None:
    return int((end - start).total_seconds()) if start is not None and end is not None else None


def _grilling_items(root: Path) -> list[WorkItem]:
    notes = root / ".harness" / "notes"
    items = []
    for path in sorted(notes.glob("grilling-*.md")):
        name = path.stem
        try:
            status, _became = grilling_status.parse(path.read_text(encoding="utf-8"))
            error = None
        except Exception as exc:
            status = None
            error = f"grilling note: {exc}"
        items.append(WorkItem(
            id=f"grilling:harness:{name}", kind="grilling", segment="harness",
            display_name=name, station=None, grilling_status=status, run_status=None,
            run_started_at=None, run_ended_at=None, elapsed_total=None, elapsed_plan=None,
            elapsed_build=None, elapsed_validate=None, phase=None, run_count=None, tokens=None,
            updated_at=_mtime(path), cycles_used=None, max_total_cycles=None,
            main_path=str(path.resolve()), worktree_path=None, source_path=str(path.resolve()),
            error=error,
        ))
    return items


def _mtime(path: Path) -> str | None:
    try:
        return str(path.stat().st_mtime_ns)
    except OSError:
        return None
