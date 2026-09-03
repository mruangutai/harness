#!/usr/bin/env python3
"""Validate the authority-bearing ``## Done when`` handoff section."""

from pathlib import Path
import re

import yaml

SECTION = "## Done when"
LEGAL_PREFIXES = ("plan-task:", "brief-sc:", "finding:", "approval:")
FEATURE_RE = re.compile(r"^(?P<prefix>\.harness/[^/]+/features/[^/]+)/")
TASK_RE = re.compile(r"^plan-task:(T-\d+)\.verify$")
SC_RE = re.compile(r"^brief-sc:(SC-\d+)$")
FINDING_RE = re.compile(r"^finding:(.+)#(F-\d+|PF-\d+)$")
APPROVAL_RE = re.compile(r"^approval:(.+)#([^#\n]+)$")


def _message(text):
    return f"{text}; follow templates/HANDOFF.md"


def _body(text):
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip().lower() == SECTION.lower():
            end = len(lines)
            for candidate in range(index + 1, len(lines)):
                if lines[candidate].strip().startswith("##"):
                    end = candidate
                    break
            return lines[index + 1:end]
    return None


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


def _contains_token(path, token):
    try:
        text = path.read_text()
    except (OSError, UnicodeError):
        return False
    return re.search(rf"(?<![A-Za-z0-9_-]){re.escape(token)}(?![A-Za-z0-9_-])", text) is not None


def _resolve(pointer, match, feature_dir, root):
    if pointer.startswith("plan-task:"):
        target = feature_dir / "plan.yaml"
        try:
            doc = yaml.safe_load(target.read_text())
        except (OSError, UnicodeError, yaml.YAMLError):
            doc = None
        task_id = match.group(1)
        tasks = doc.get("tasks", []) if isinstance(doc, dict) else []
        ok = any(isinstance(task, dict) and task.get("id") == task_id
                 and isinstance(task.get("verify"), str) and task["verify"].strip()
                 for task in tasks)
        detail = f"task {task_id} with non-empty verify was not found"
    elif pointer.startswith("brief-sc:"):
        target = feature_dir / "BRIEF.md"
        sc_id = match.group(1)
        try:
            lines = target.read_text().splitlines()
        except (OSError, UnicodeError):
            lines = []
        ok = any(line.strip().removeprefix("- ").startswith(f"{sc_id}:") for line in lines)
        detail = f"success criterion {sc_id} was not found"
    elif pointer.startswith("finding:"):
        target = root / match.group(1)
        finding_id = match.group(2)
        ok = _contains_token(target, finding_id)
        detail = f"finding {finding_id} was not found"
    else:
        target = root / match.group(1)
        heading = match.group(2)
        try:
            lines = target.read_text().splitlines()
        except (OSError, UnicodeError):
            lines = []
        ok = any(line.lstrip().startswith("#")
                 and line.lstrip("#").strip().lower() == heading.strip().lower()
                 for line in lines)
        detail = f"heading {heading!r} was not found"
    if ok:
        return None
    return _message(f"Authority pointer {pointer!r} is unresolved in {target}: {detail}")


def problems(rel_path, text, root, resolve):
    """Return one single-line problem for each violation in a handoff note."""
    body = _body(text)
    if body is None:
        return [_message(f"handoff note is missing required section {SECTION}")]

    nonblank = [line.strip() for line in body if line.strip()]
    scopes = [line for line in nonblank if line.startswith("Scope:")]
    authorities = [line for line in nonblank if line.startswith("Authority:")]
    result = []
    if len(scopes) != 1:
        result.append(_message(f"{SECTION} has {len(scopes)} Scope: lines; expected exactly 1"))
    if not 1 <= len(authorities) <= 4:
        result.append(_message(
            f"{SECTION} has {len(authorities)} Authority: lines; expected between 1 and 4"))
    for line in nonblank:
        if not line.startswith(("Scope:", "Authority:")):
            result.append(_message(f"{SECTION} contains unexpected line {line[:60]!r}"))

    parsed = []
    for line in authorities:
        pointer = line[len("Authority:"):].strip()
        match = _grammar(pointer)
        if match is None:
            result.append(_unknown(pointer))
        else:
            parsed.append((pointer, match))
    if not resolve:
        return result

    root = Path(root)
    feature_dir = _feature_dir(rel_path, root)
    if feature_dir is None:
        result.append(_message(
            f"handoff path {rel_path!r} is not inside .harness/<repo>/features/<FEAT>/"))
        return result
    for pointer, match in parsed:
        problem = _resolve(pointer, match, feature_dir, root)
        if problem:
            result.append(problem)
    return result
