#!/usr/bin/env python3
"""FEAT-1821 T-05 (SC-08): harness-ui-reviewer Mode B judges from `harness-ui-results/1` evidence,
never from source alone and never from an ad-hoc browser.

Text-contract test in the test-orchestrator-playbook.py convention — the fix IS the text the
agent reads. Each clause below is a rule Mode B must carry; every clause has a mutant: the
section with that clause deleted, or its meaning inverted, must be REJECTED by the same
detector, so a rule cannot be satisfied by a stray token. Mode A and the Output block are
asserted unchanged in shape.
"""
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
AGENT = os.path.join(ROOT, ".omp", "agents", "harness-ui-reviewer.md")


def section(text, heading_prefix):
    lines = text.splitlines()
    start = next(i for i, l in enumerate(lines) if l.startswith(heading_prefix))
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return "\n".join(lines[start:end])


# clause id → (detector regex over Mode B, mutant: (pattern, replacement) that must break it)
CLAUSES = {
    "evidence-schema": (
        r"harness-ui-results/1",
        (r"harness-ui-results/1", "the digest")),
    "reads-results-and-every-webp": (
        r"read(?:s)? `results\.json` and every (?:referenced )?WebP",
        (r"and every (?:referenced )?WebP", "and a representative WebP")),
    "at-pinned-review-sha": (
        r"at the pinned `review_sha`",
        (r"at the pinned `review_sha`", "at the current tip")),
    "against-design-and-prototype": (
        r"against `DESIGN\.md` and the approved prototype",
        (r"and the approved prototype", "")),
    "pin-equality": (
        r"`served_bundle_commit` (?:must )?equal(?:s)? (?:the pinned )?`review_sha`",
        (r"equal(?:s)?", "may differ from")),
    "each-project-rows-both-projects": (
        r"[Ee]ach-project row(?:s)?[^\n]*both configured projects",
        (r"both configured projects", "at least one project")),
    "once-rows-declared-project": (
        r"[Oo]nce row(?:s)?[^\n]*(?:its|the) declared project",
        (r"(?:its|the) declared project", "any project")),
    "complete-id-accounting": (
        r"complete (?:check-)?id accounting",
        (r"complete (?:check-)?id accounting", "spot-checked ids")),
    "inspection-label-fields": (
        r"[Ee]very inspection evidence label[^\n]*route[^\n]*fixture state[^\n]*interaction[^\n]*viewport",
        (r"[Ee]very inspection evidence label", "Any inspection evidence label")),
    "missing-evidence-is-fail": (
        r"[Mm]issing, unreadable, stale, mismatched or incomplete evidence is `?FAIL`?",
        (r"is `?FAIL`?", "is noted as an open question")),
    "rerun-configured-command-only": (
        r"[Rr]erun(?:ning)? (?:is limited to |only |is limited to only )the configured `test_kinds\.ui` command[^\n]*same feature and run",
        (r"only the configured `test_kinds\.ui` command", "any command that renders the page")),
    "no-adhoc-cdp": (
        r"[Nn]ever[^\n]*ad-hoc CDP",
        (r"[Nn]ever([^\n]*ad-hoc CDP)", r"Feel free to use\1")),
    "no-alternate-browser-scripts": (
        r"[Nn]ever[^\n]*alternate browser script",
        (r"alternate browser script", "documented browser script")),
    "traces-every-traced-record": (
        r"every traced record[^\n]*`traced_check_ids`",
        (r"every traced record", "a sample of traced records")),
    "traces-opened-not-just-present": (
        r"open[^\n]*`npx playwright show-trace[^`]*`[^\n]*filmstrip[^\n]*DOM snapshot[^\n]*assertion",
        (r"open([^\n]*`npx playwright show-trace[^`]*`)", r"confirm the file is present\1")),
    "traces-cite-judged-step": (
        r"cite the exact (?:judged )?step",
        (r"cite the exact (?:judged )?step", "summarise the outcome")),
    "traces-still-only-is-fail": (
        r"[Aa] traced check graded from its still[^\n]*(?:is|are) (?:a )?`?FAIL`?",
        (r"(?:is|are) (?:a )?`?FAIL`?", "is acceptable")),
    "source-only-is-not-a-pass": (
        r"[Ss]ource[- ]only (?:reading|assurance|audit)[^\n]*(?:never|not) (?:a )?PASS",
        (r"(?:never|not) (?:a )?PASS", "a PASS")),
}


def check(name, cond, detail=""):
    print(("ok    " if cond else "FAIL  ") + name + (f" — {detail}" if detail and not cond else ""))
    return 0 if cond else 1


def main():
    text = open(AGENT, encoding="utf-8").read()
    mode_b = section(text, "## Mode B")
    failures = 0
    for clause, (pattern, (mut_from, mut_to)) in CLAUSES.items():
        present = re.search(pattern, mode_b) is not None
        failures += check(f"Mode B carries {clause}", present, f"pattern {pattern!r} not found")
        mutant, n = re.subn(mut_from, mut_to, mode_b, count=1)
        failures += check(f"mutant of {clause} is rejected",
                          n == 1 and re.search(pattern, mutant) is None,
                          "mutation did not apply or detector still matched")
    failures += check("the source-only 'Known limit' framing is gone",
                      "you audit SOURCE, not pixels" not in text)
    failures += check("Mode A is unchanged in shape", "## Mode A" in text and "Is it implementable?" in text)
    output = section(text, "## Output")
    for field in ("VERDICT:", "mode:", "in_scope:", "severity_max:", "findings:", "must_fix:",
                  "contract_violations:", "a11y:", "open_questions:", "files_touched:", "expertise_update:"):
        failures += check(f"Output keeps {field}", field in output)
    failures += check("Output carries the evidence pointer", "evidence:" in output)
    print("PASS" if failures == 0 else f"FAILED ({failures})")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
