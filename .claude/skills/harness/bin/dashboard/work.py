"""Offline disk collection of fleet work for the dashboard operational lane."""
from dataclasses import asdict, dataclass
import os
from pathlib import Path
import re

import artifact_accessors
import factory_config
import grilling_status
import harness_yaml
import worktree_terminal

_PREFIX = re.compile(r"^(?:FEAT|BUG)-\d+")


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
    root = Path(root).resolve()
    entries = _registered_worktree_entries(root)
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
    return sorted(items, key=lambda item: item.id)


def _registered_worktree_entries(root: Path) -> list[tuple[Path, str, str]]:
    entries = _repository_worktree_entries(root, "harness")
    try:
        fleet = artifact_accessors.load_fleet(root / ".harness" / "factory" / "fleet.yaml")
    except Exception:
        fleet = None
    if fleet is not None:
        for entry in fleet["repos"]:
            repository = entry["name"]
            workspace = Path(factory_config.workspace_path(fleet, repository))
            entries.extend(_repository_worktree_entries(workspace, repository))
    unique = {}
    for path, repository, role in entries:
        unique.setdefault(path, (path, repository, role))
    return sorted(unique.values(), key=lambda entry: str(entry[0]))


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
        run_started_at=None, run_ended_at=None, updated_at=None, cycles_used=None,
        max_total_cycles=None, main_path=None, worktree_path=None, source_path=str(path),
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
    return WorkItem(
        id=f"{_kind(name)}:{segment}:{name}", kind=_kind(name), segment=segment,
        display_name=name, station=_station(source), grilling_status=None,
        run_status=run.get("verdict"), run_started_at=run.get("started_at"),
        run_ended_at=run.get("ended_at"), updated_at=_updated_at(document),
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
        run_started_at=None, run_ended_at=None, updated_at=None, cycles_used=None,
        max_total_cycles=None, main_path=main_path, worktree_path=worktree_path,
        source_path=str(source.resolve()), error=f"{source_name}: {error}",
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
            run_started_at=None, run_ended_at=None,
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
