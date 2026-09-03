#!/usr/bin/env python3
"""Validate the authority-bearing ``## Done when`` handoff section."""

from pathlib import Path, PurePosixPath
import re
import stat
import yaml

SECTION = "## Done when"
LEGAL_PREFIXES = ("plan-task:", "brief-sc:", "finding:", "approval:")
FEATURE_RE = re.compile(r"^(?P<prefix>\.harness/[^/]+/features/[^/]+)/")
TASK_RE = re.compile(r"^plan-task:(T-\d+)\.verify$")
SC_RE = re.compile(r"^brief-sc:(SC-\d+)$")
FINDING_RE = re.compile(r"^finding:(.+)#(F-\d+|PF-\d+)$")
APPROVAL_RE = re.compile(r"^approval:(.+)#([^#\n]+)$")

MAX_TARGET_BYTES = 1024 * 1024


def _message(text):
    return f"{text}; follow templates/HANDOFF.md"


def _done_when_indices(lines):
    return [index for index, line in enumerate(lines)
            if re.fullmatch(r"##[ \t]+Done when[ \t]*", line.strip(), re.IGNORECASE)]


def _body(lines, start):
    end = len(lines)
    for index in range(start + 1, len(lines)):
        if re.match(r"^##(?!#)(?:[ \t]|$)", lines[index].strip()):
            end = index
            break
    return lines[start + 1:end]


def _grammar(pointer):
    for pattern in (TASK_RE, SC_RE, FINDING_RE, APPROVAL_RE):
        match = pattern.fullmatch(pointer)
        if match:
            return match
    return None


def _unknown(pointer):
    legal = ", ".join(LEGAL_PREFIXES)
    return _message(f"Authority pointer {pointer!r} is invalid; legal prefixes are {legal}")


def _feature_dir(rel_path, root):
    normalized = Path(rel_path).as_posix()
    match = FEATURE_RE.match(normalized)
    return root / match.group("prefix") if match else None


def _pointer_path(pointer, match):
    if pointer.startswith(("finding:", "approval:")):
        return match.group(1)
    return None


def _unsafe_rel_path(value):
    if value is None:
        return None
    if re.search(r"[\x00-\x1f\x7f]", value):
        return "contains control characters"
    path = PurePosixPath(value)
    if path.is_absolute():
        return "is absolute"
    if ".." in path.parts:
        return "contains traversal"
    if not value.strip() or path == PurePosixPath("."):
        return "is empty"
    return None


def _read_target(path, root):
    root = Path(root).resolve()
    try:
        resolved = path.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise ValueError(f"cannot resolve target: {exc}") from exc
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError("target escapes the project root") from exc
    try:
        mode = resolved.stat().st_mode
        size = resolved.stat().st_size
    except OSError as exc:
        raise ValueError(f"cannot inspect target: {exc}") from exc
    if not stat.S_ISREG(mode):
        raise ValueError("target is not a regular file")
    if size > MAX_TARGET_BYTES:
        raise ValueError(f"target exceeds {MAX_TARGET_BYTES} byte read limit")
    try:
        with resolved.open("r", encoding="utf-8") as handle:
            return handle.read(MAX_TARGET_BYTES + 1)
    except (OSError, UnicodeError) as exc:
        raise ValueError(f"cannot read target: {exc}") from exc


def _contains_token(text, token):
    return re.search(
        rf"(?<![A-Za-z0-9_-]){re.escape(token)}(?![A-Za-z0-9_-])", text
    ) is not None




def _unresolved(pointer, target, detail):
    return _message(f"Authority pointer {pointer!r} is unresolved in {target}: {detail}")


def _resolve_plan(pointer, match, feature_dir, root):
    target = feature_dir / "plan.yaml"
    task_id = match.group(1)
    try:
        doc = yaml.safe_load(_read_target(target, root))
    except (ValueError, yaml.YAMLError) as exc:
        return _unresolved(pointer, target, exc)
    tasks = doc.get("tasks", []) if isinstance(doc, dict) else []
    ok = any(isinstance(task, dict) and task.get("id") == task_id
             and isinstance(task.get("verify"), str) and task["verify"].strip()
             for task in tasks)
    return None if ok else _unresolved(
        pointer, target, f"task {task_id} with non-empty verify was not found")


def _resolve_brief(pointer, match, feature_dir, root):
    target = feature_dir / "BRIEF.md"
    sc_id = match.group(1)
    try:
        lines = _read_target(target, root).splitlines()
    except ValueError as exc:
        return _unresolved(pointer, target, exc)
    ok = any(line.strip().removeprefix("- ").startswith(f"{sc_id}:") for line in lines)
    return None if ok else _unresolved(
        pointer, target, f"success criterion {sc_id} was not found")


def _resolve_finding(pointer, match, _feature_dir, root):
    target = root / match.group(1)
    finding_id = match.group(2)
    try:
        ok = _contains_token(_read_target(target, root), finding_id)
    except ValueError as exc:
        return _message(f"Authority pointer {pointer!r} has unsafe target {target}: {exc}")
    return None if ok else _unresolved(
        pointer, target, f"finding {finding_id} was not found")


def _atx_heading_text(line):
    match = re.fullmatch(r"[ \t]{0,3}(#{1,6})[ \t]+(.+?)[ \t]*", line)
    if match is None:
        return None
    return re.sub(r"[ \t]+#+[ \t]*$", "", match.group(2)).strip()


def _resolve_approval(pointer, match, _feature_dir, root):
    target = root / match.group(1)
    heading = match.group(2)
    try:
        lines = _read_target(target, root).splitlines()
    except ValueError as exc:
        return _message(f"Authority pointer {pointer!r} has unsafe target {target}: {exc}")
    wanted = heading.strip().lower()
    ok = any((_atx_heading_text(line) or "").lower() == wanted for line in lines)
    return None if ok else _unresolved(
        pointer, target, f"heading {heading!r} was not found")


RESOLVERS = {
    "plan-task:": _resolve_plan,
    "brief-sc:": _resolve_brief,
    "finding:": _resolve_finding,
    "approval:": _resolve_approval,
}


def _resolve(pointer, match, feature_dir, root):
    prefix = next(prefix for prefix in LEGAL_PREFIXES if pointer.startswith(prefix))
    return RESOLVERS[prefix](pointer, match, feature_dir, root)


def _scope_problems(scopes):
    if len(scopes) != 1:
        return [_message(f"{SECTION} has {len(scopes)} Scope: lines; expected exactly 1")]
    if not scopes[0][len("Scope:"):].strip():
        return [_message(f"{SECTION} Scope: value must be non-empty")]
    return []


def _authority_count_problems(authorities):
    if 1 <= len(authorities) <= 4:
        return []
    return [_message(
        f"{SECTION} has {len(authorities)} Authority: lines; expected between 1 and 4")]


def _line_problems(nonblank):
    unexpected = [line for line in nonblank
                  if not line.startswith(("Scope:", "Authority:"))]
    return [_message(f"{SECTION} contains unexpected line {line[:60]!r}")
            for line in unexpected]


def _order_problems(nonblank, scopes, authorities):
    if not scopes or not authorities:
        return []
    if nonblank.index(scopes[0]) < nonblank.index(authorities[0]):
        return []
    return [_message(f"{SECTION} Scope: line must appear before every Authority: line")]


def _shape_problems(nonblank, scopes, authorities):
    return (_scope_problems(scopes)
            + _authority_count_problems(authorities)
            + _line_problems(nonblank)
            + _order_problems(nonblank, scopes, authorities))


def _parse_authorities(authorities):
    parsed = []
    result = []
    for line in authorities:
        pointer = line[len("Authority:"):].strip()
        match = _grammar(pointer)
        if match is None:
            result.append(_unknown(pointer))
            continue
        unsafe = _unsafe_rel_path(_pointer_path(pointer, match))
        if unsafe:
            result.append(_message(f"Authority pointer {pointer!r} has unsafe target: {unsafe}"))
            continue
        parsed.append((pointer, match))
    return parsed, result


def _resolution_problems(parsed, feature_dir, root):
    result = []
    for pointer, match in parsed:
        try:
            problem = _resolve(pointer, match, feature_dir, root)
        except Exception as exc:
            problem = _message(
                f"Authority pointer {pointer!r} resolver failed closed "
                f"({type(exc).__name__}: {exc})")
        if problem:
            result.append(problem)
    return result


def _classified_lines(body):
    nonblank = [line.strip() for line in body if line.strip()]
    scopes = [line for line in nonblank if line.startswith("Scope:")]
    authorities = [line for line in nonblank if line.startswith("Authority:")]
    return nonblank, scopes, authorities

def _resolve_all(rel_path, parsed, root):
    root = Path(root)
    feature_dir = _feature_dir(rel_path, root)
    if feature_dir is None:
        return [_message(
            f"handoff path {rel_path!r} is not inside .harness/<repo>/features/<FEAT>/")]
    return _resolution_problems(parsed, feature_dir, root)




def problems(rel_path, text, root, resolve):
    """Return one single-line problem for each violation in a handoff note."""
    lines = text.splitlines()
    indices = _done_when_indices(lines)
    if not indices:
        return [_message(f"handoff note is missing required section {SECTION}")]
    if len(indices) != 1:
        return [_message(
            f"handoff note has {len(indices)} {SECTION} sections; expected exactly 1")]
    body = _body(lines, indices[0])
    nonblank, scopes, authorities = _classified_lines(body)
    result = _shape_problems(nonblank, scopes, authorities)
    parsed, grammar_problems = _parse_authorities(authorities)
    result.extend(grammar_problems)
    if resolve:
        result.extend(_resolve_all(rel_path, parsed, root))
    return result
