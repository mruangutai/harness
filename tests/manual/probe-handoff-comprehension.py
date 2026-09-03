#!/usr/bin/env python3
"""Manually measure whether handoff ``Done when`` facts improve model comprehension.

This stdlib-only probe needs the ``omp`` binary on PATH and live model credentials. It makes
live model calls and can never run in CI. Use ``--dry-run`` to print the work plan without
making a model call or network request. A real run reports evidence only and always exits zero.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODEL = "anthropic/claude-sonnet-5"
ARMS = ("as-written", "done-when-stripped")
QUESTIONS = (
    "What is the one immediate next action?",
    "What exact scope must be completed?",
    "Which authorities define when that action is complete?",
    "What evidence would show that every authority is satisfied?",
)
DONE_WHEN_RE = re.compile(
    r"(?ims)^## Done when\s*$.*?(?=^##(?:\s|$)|\Z)"
)


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("notes", nargs="*", type=Path, help="handoff note paths")
    parser.add_argument("--dry-run", action="store_true", help="print the plan without model calls")
    parser.add_argument("--model", default=MODEL, help="omp model id (default: %(default)s)")
    return parser.parse_args()


def note_paths(requested: list[Path]) -> list[Path]:
    if requested:
        return [path if path.is_absolute() else ROOT / path for path in requested]
    matches = list(ROOT.glob(".harness/harness/features/*/notes/handoff-*.md"))
    return [max(matches, key=lambda path: path.stat().st_mtime_ns)] if matches else []


def done_when_facts(text: str) -> list[str]:
    match = DONE_WHEN_RE.search(text)
    if match is None:
        return []
    lines = (line.strip() for line in match.group().splitlines()[1:])
    return [line.split(":", 1)[1].strip() for line in lines
            if line.startswith(("Scope:", "Authority:")) and ":" in line]


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


def print_plan(paths: list[Path], model: str) -> None:
    print("handoff comprehension probe: DRY RUN")
    print(f"model: {model}")
    print(f"arms: {', '.join(ARMS)}")
    print("questions:")
    for question in QUESTIONS:
        print(f"- {question}")
    print("notes:")
    if not paths:
        print("- (none found)")
    for path in paths:
        print(f"- {path}")
    print(f"planned model calls: {len(paths) * len(ARMS)} (not executed)")


def measure_note(path: Path, omp: str, model: str) -> dict[str, tuple[int, int, bool]]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        print(f"note: {path}\nerror: cannot read note: {exc}")
        return {}

    facts = done_when_facts(text)
    sha = hashlib.sha256(text.encode()).hexdigest()
    print(f"note: {path}")
    print(f"note sha256: {sha}")
    print(f"required facts ({len(facts)}):")
    for fact in facts:
        print(f"- {fact}")

    evidence = {}
    notes = (text, without_done_when(text))
    for label, arm_note in zip(ARMS, notes):
        answer, error = ask(omp, model, arm_note)
        covered = covered_facts(answer, facts)
        complete = bool(facts) and len(covered) == len(facts)
        evidence[label] = (len(covered), len(facts), complete)
        print(f"arm: {label}")
        print(f"coverage: {len(covered)}/{len(facts)}")
        print(f"covers every fact: {'yes' if complete else 'no'}")
        if error:
            print(f"error: {error}")
        missing = [fact for fact in facts if fact not in covered]
        for fact in missing:
            print(f"missing: {fact}")
        print("answer:")
        print(answer or "(no answer)")
    complete_answers = sum(complete for _, _, complete in evidence.values())
    print(f"note complete answers: {complete_answers}/{len(ARMS)}")
    return evidence


def run(paths: list[Path], model: str) -> None:
    print("handoff comprehension probe: REAL RUN")
    print(f"model: {model}")
    print(f"arm labels: {', '.join(ARMS)}")
    omp = shutil.which("omp")
    if omp is None:
        print("error: omp binary is not on PATH; recording empty answers")
        omp = "omp"

    totals = {label: [0, 0, 0] for label in ARMS}
    measured = 0
    for path in paths:
        evidence = measure_note(path, omp, model)
        if not evidence:
            continue
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
