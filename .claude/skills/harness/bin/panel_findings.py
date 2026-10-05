#!/usr/bin/env python3
"""A panel finding's identity, its shape, and whether it holds a signature (FEAT-45 T-09, D-05;
#2095).

The ONE place a panel finding is defined, so the validator lead, pm, plan-merge.py and
check-state.py cannot disagree about what a finding is called, what it may carry, or when it
blocks a signature. python3 stdlib only, no third-party import.

WHY A CONTENT HASH AND NOT A SEQUENTIAL ID. A sequential id is assigned per run, so a
re-run renumbers and a risk acceptance recorded against finding 2 silently starts covering
whatever is second next time. A content hash keeps an unchanged finding's id stable
across runs, so an acceptance survives a re-run, and gives a REWORDED finding a NEW id, so
the old ruling stops applying and check-state.py reports it as a stale risk acceptance.
That failure direction is deliberate and it is closed, not open.

WHY THE SHAPE LIVES HERE (#2095). templates/plan.yaml declared it in a comment and nothing
checked it: set-panel validated id and kind only, so 20 of 47 landed plans grew free keys and a
dozen disposition spellings, and on FEAT-1559 a ruled high finding written as prose read as
OPEN to INV-32 while sign-approval signed past it. The writers refuse a departure and
check-state reports one, through this one function.
"""
import argparse
import hashlib
import re
import sys

_WHITESPACE_RUN = re.compile(r"\s+")


def normalize_summary(summary):
    """Lowercase, collapse every run of whitespace to one space, strip the ends."""
    return _WHITESPACE_RUN.sub(" ", summary.lower()).strip()


def finding_id(reader, summary):
    """PF- followed by the first 32 characters of sha256(reader + '\\n' + normalized). Length 35."""
    normalized = normalize_summary(summary)
    digest_input = f"{reader}\n{normalized}".encode("utf-8")
    digest = hashlib.sha256(digest_input).hexdigest()
    return f"PF-{digest[:32]}"


# templates/plan.yaml's `panel.findings` item, as data. `scope` is carried by a proportionality
# finding only (DEC-228); `resolved_by` by a resolved finding only, naming the plan task that
# resolved it. Risk acceptance is NOT a disposition: it is approval.rulings, written by
# `sign-approval --overrule`, so `disposition` has exactly two values.
SEVERITIES = ("info", "low", "med", "high", "critical", "unrated")
NON_GATING_SEVERITIES = frozenset({"info", "low", "med"})
FINDING_KINDS = ("substance", "form", "proportionality")
PROPORTIONALITY_SCOPES = ("task", "mission")
DISPOSITIONS = ("open", "resolved")
REQUIRED_KEYS = ("id", "severity", "reader", "kind", "summary", "disposition")
FINDING_KEYS = REQUIRED_KEYS + ("scope", "resolved_by")
# The plan panel's reader SLOTS (#2102): `panel.readers[].reader` names one of these, never the
# persona that filled it (scope = code-reviewer, should-not-exist = fable-advisor, design =
# ui-reviewer, goalcheck = pm). A FINDING's `reader` is different: it is the reporting persona,
# as each reviewer's contract writes it, and half of the finding's id, so it is not a slot.
PANEL_READERS = ("should-not-exist", "scope", "design", "goalcheck")


def _enum_fault(finding, key, allowed):
    value = finding.get(key)
    if value in allowed:
        return []
    return [f"{key} {value!r} is not one of {' | '.join(allowed)}"]


def _scope_fault(finding):
    if finding.get("kind") == "proportionality":
        return _enum_fault(finding, "scope", PROPORTIONALITY_SCOPES)
    if "scope" in finding:
        return ["scope is carried by a proportionality finding only"]
    return []


def _resolved_by_fault(finding, task_ids):
    if "resolved_by" not in finding:
        return []
    if finding.get("disposition") != "resolved":
        return ["resolved_by is carried by a resolved finding only"]
    named = str(finding.get("resolved_by") or "").strip()
    if task_ids is not None and named not in task_ids:
        return [f"resolved_by {named!r} names no task in this plan"]
    return []


def shape_faults(finding, task_ids=None):
    """Every way `finding` departs from the template's shape, one line each; [] when it conforms.

    `task_ids` is the plan's task-id set, against which `resolved_by` must resolve; None skips
    that one check, for a caller validating a value before the plan it lands in is read."""
    if not isinstance(finding, dict):
        return ["is not a mapping"]
    missing = [key for key in REQUIRED_KEYS if not str(finding.get(key) or "").strip()]
    faults = [f"is missing {', '.join(missing)}"] if missing else []
    extra = sorted(str(key) for key in finding if key not in FINDING_KEYS)
    if extra:
        faults.append(f"carries {', '.join(extra)}, outside the template's keys "
                      f"({', '.join(FINDING_KEYS)})")
    for key, allowed in (("severity", SEVERITIES), ("kind", FINDING_KINDS),
                         ("disposition", DISPOSITIONS)):
        if key not in missing:
            faults.extend(_enum_fault(finding, key, allowed))
    return faults + _scope_fault(finding) + _resolved_by_fault(finding, task_ids)


def gates_signature(finding, accepted_ids):
    """True when `finding` withholds a signature: not resolved, no current risk acceptance in
    `accepted_ids`, and a severity outside info/low/med — so unrated, absent or unknown fails
    closed, as high does. INV-32 grades a signed plan by this rule and sign-approval refuses by
    it, so the gate and the audit cannot disagree about which finding is open."""
    if str(finding.get("disposition", "")).strip().lower() == "resolved":
        return False
    if str(finding.get("id", "")).strip() in accepted_ids:
        return False
    return str(finding.get("severity", "")).strip().lower() not in NON_GATING_SEVERITIES


def _cli_id(reader, summary):
    if not reader:
        print("panel_findings.py: --reader must not be empty", file=sys.stderr)
        return 2
    if not normalize_summary(summary):
        print("panel_findings.py: --summary must not be empty or whitespace-only", file=sys.stderr)
        return 2
    print(finding_id(reader, summary))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(prog="panel_findings.py")
    subparsers = parser.add_subparsers(dest="command", required=True)
    id_parser = subparsers.add_parser("id", help="print the identity of a panel finding")
    id_parser.add_argument("--reader", required=True)
    id_parser.add_argument("--summary", required=True)

    args = parser.parse_args(argv)
    if args.command == "id":
        return _cli_id(args.reader, args.summary)
    return 2


if __name__ == "__main__":
    sys.exit(main())
