#!/usr/bin/env python3
"""Manually measure whether handoff ``Done when`` facts improve model comprehension.

This stdlib-only probe needs the ``omp`` binary on PATH and live model credentials. It makes
live model calls and can never run in CI. Use ``--dry-run`` to print the work plan without
making a model call or network request. A real run reports evidence only and always exits zero.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import os
import re
import shutil
import stat
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parents[2]
MODEL = "anthropic/claude-sonnet-5"
ARMS = ("as-written", "done-when-stripped")
QUESTIONS = (
    "What is the one immediate next action?",
    "What exact scope must be completed?",
    "Which authorities define when that action is complete?",
    "What evidence would show that every authority is satisfied?",
)
MAX_NOTE_BYTES = 1_048_576


class ValidatedNote(NamedTuple):
    path: Path
    text: str
    mtime_ns: int


DONE_WHEN_RE = re.compile(
    r"(?ims)^## Done when\s*$.*?(?=^##(?:\s|$)|\Z)"
)


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("notes", nargs="*", type=Path, help="handoff note paths")
    parser.add_argument("--dry-run", action="store_true", help="print the plan without model calls")
    parser.add_argument("--model", default=MODEL, help="omp model id (default: %(default)s)")
    return parser.parse_args()


def is_handoff_note(path: Path) -> bool:
    try:
        relative = path.relative_to(ROOT.resolve() / ".harness/harness/features")
    except ValueError:
        return False
    return (
        len(relative.parts) == 3
        and relative.parts[1] == "notes"
        and fnmatch.fnmatchcase(relative.name, "handoff-*.md")
    )


def read_regular_file(path: Path) -> tuple[bytes, int]:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    descriptor = os.open(path, flags)
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise ValueError("target is not a regular file")
        if metadata.st_size > MAX_NOTE_BYTES:
            raise ValueError(f"note exceeds {MAX_NOTE_BYTES} bytes")
        with os.fdopen(descriptor, "rb") as stream:
            descriptor = -1
            payload = stream.read(MAX_NOTE_BYTES + 1)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
    if len(payload) > MAX_NOTE_BYTES:
        raise ValueError(f"note exceeds {MAX_NOTE_BYTES} bytes")
    return payload, metadata.st_mtime_ns


def validate_note(candidate: Path) -> ValidatedNote | None:
    path = candidate if candidate.is_absolute() else ROOT / candidate
    try:
        if path.is_symlink():
            raise ValueError("symlinks are not allowed")
        resolved = path.resolve(strict=True)
        if not is_handoff_note(resolved):
            raise ValueError("path is not a feature handoff note")
        payload, mtime_ns = read_regular_file(path)
        return ValidatedNote(resolved, payload.decode("utf-8"), mtime_ns)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"note: {path}\nerror: refusing note: {exc}")
        return None


def note_paths(requested: list[Path]) -> list[ValidatedNote]:
    candidates = requested or list(
        ROOT.glob(".harness/harness/features/*/notes/handoff-*.md")
    )
    notes = [note for path in candidates if (note := validate_note(path)) is not None]
    if requested or not notes:
        return notes
    return [max(notes, key=lambda note: note.mtime_ns)]


def done_when_facts(text: str) -> list[str]:
    match = DONE_WHEN_RE.search(text)
    if match is None:
        return []
    lines = (line.strip() for line in match.group().splitlines()[1:])
    return [line.split(":", 1)[1].strip() for line in lines
            if line.startswith(("Scope:", "Authority:"))]


def without_done_when(text: str) -> str:
    return DONE_WHEN_RE.sub("", text).rstrip() + "\n"


def prompt(note: str) -> str:
    questions = "\n".join(f"{index}. {question}" for index, question in enumerate(QUESTIONS, 1))
    return (
        "Read the handoff note below and answer this fixed question set. Be concise. When the note "
        "provides a Scope or Authority value, reproduce that value exactly in your answer.\n\n"
        f"{questions}\n\n--- HANDOFF NOTE ---\n{note}\n--- END NOTE ---"
    )


def ask(omp: str, model: str, note: str) -> tuple[str, str]:
    try:
        result = subprocess.run(
            [omp, "-p", prompt(note), "--no-extensions", "--no-skills", "--no-rules",
             "--auto-approve", "--model", model],
            cwd=ROOT, capture_output=True, text=True, timeout=600,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return "", f"model call failed: {exc}"
    if result.returncode:
        detail = (result.stderr or result.stdout).strip().replace("\n", " ")
        return "", f"model call exited {result.returncode}: {detail[-400:]}"
    return result.stdout.strip(), ""


def normalized(text: str) -> str:
    return " ".join(text.casefold().split())


def covered_facts(answer: str, facts: list[str]) -> list[str]:
    haystack = normalized(answer)
    return [fact for fact in facts if normalized(fact) in haystack]


def print_plan(notes: list[ValidatedNote], model: str) -> None:
    print("handoff comprehension probe: DRY RUN")
    print(f"model: {model}")
    print(f"arms: {', '.join(ARMS)}")
    print("questions:")
    for question in QUESTIONS:
        print(f"- {question}")
    print("notes:")
    if not notes:
        print("- (none found)")
    for note in notes:
        print(f"- {note.path}")
    print(f"planned model calls: {len(notes) * len(ARMS)} (not executed)")


def print_note_header(note: ValidatedNote, facts: list[str]) -> None:
    sha = hashlib.sha256(note.text.encode()).hexdigest()
    print(f"note: {note.path}")
    print(f"note sha256: {sha}")
    print(f"required facts ({len(facts)}):")
    for fact in facts:
        print(f"- {fact}")


def measure_arm(
    label: str, text: str, facts: list[str], omp: str, model: str
) -> tuple[int, int, bool]:
    answer, error = ask(omp, model, text)
    covered = covered_facts(answer, facts)
    complete = bool(facts) and len(covered) == len(facts)
    print(f"arm: {label}")
    print(f"coverage: {len(covered)}/{len(facts)}")
    print(f"covers every fact: {'yes' if complete else 'no'}")
    if error:
        print(f"error: {error}")
    for fact in (fact for fact in facts if fact not in covered):
        print(f"missing: {fact}")
    print("answer:")
    print(answer or "(no answer)")
    return len(covered), len(facts), complete


def measure_note(
    note: ValidatedNote, omp: str, model: str
) -> dict[str, tuple[int, int, bool]]:
    facts = done_when_facts(note.text)
    print_note_header(note, facts)
    arm_notes = (note.text, without_done_when(note.text))
    evidence = {
        label: measure_arm(label, text, facts, omp, model)
        for label, text in zip(ARMS, arm_notes)
    }
    complete_answers = sum(complete for _, _, complete in evidence.values())
    print(f"note complete answers: {complete_answers}/{len(ARMS)}")
    return evidence


def run(notes: list[ValidatedNote], model: str) -> None:
    print("handoff comprehension probe: REAL RUN")
    print(f"model: {model}")
    print(f"arm labels: {', '.join(ARMS)}")
    omp = shutil.which("omp")
    if omp is None:
        print("error: omp binary is not on PATH; recording empty answers")
        omp = "omp"

    totals = {label: [0, 0, 0] for label in ARMS}
    measured = 0
    for note in notes:
        evidence = measure_note(note, omp, model)
        measured += 1
        for label, (covered, required, complete) in evidence.items():
            totals[label][0] += covered
            totals[label][1] += required
            totals[label][2] += int(complete)

    print("total evidence:")
    for label in ARMS:
        covered, required, complete = totals[label]
        print(f"arm: {label}; coverage: {covered}/{required}; complete answers: {complete}/{measured}")
    print(f"all complete answers: {sum(values[2] for values in totals.values())}/{measured * len(ARMS)}")


def main() -> int:
    args = arguments()
    paths = note_paths(args.notes)
    if args.dry_run:
        print_plan(paths, args.model)
        return 0
    run(paths, args.model)
    return 0


if __name__ == "__main__":
    sys.exit(main())
