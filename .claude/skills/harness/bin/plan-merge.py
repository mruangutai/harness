#!/usr/bin/env python3
"""plan-merge.py — the second plan writer: it adds tasks, replaces the fields a proposal names
on a task that already exists, and deletes one only when it is named and a reason is given
(FEAT-32 T-03, D-01..D-04, DEC-182, DEC-120; FEAT-59 SC-05/SC-07/SC-08).

Reproduces and fixes #628: two whole-file writes to the same plan.yaml, one after another,
silently lose whatever the first one added. This CLI never does a whole-file rewrite of an
existing plan.yaml. It SPLICES TEXT — never re-renders through a YAML dumper (D-03) — keyed on
each task/decision's `id`, under harness_merge.locked_update so the replace stays atomic and the
lock stays the one shared with every other write route in this feature.

    plan-merge.py apply             --file <plan.yaml> --proposal <path or - for stdin>
    plan-merge.py add-tasks         --file <plan.yaml> --proposal <path or - for stdin>
    plan-merge.py set-task-station  --file <plan.yaml> --task T-NN --station <name>
    plan-merge.py set-feature-station --file <plan.yaml> --station <name>
    plan-merge.py set-panel         --file <plan.yaml> --value-file <panel.yaml>
    plan-merge.py record-panel      --file <plan.yaml> --digest <lead digest.md> --cycle N [--last-run <run-dir>]
    plan-merge.py set-lanes         --file <plan.yaml> --value-file <lanes.yaml>
    plan-merge.py set-key           --file <plan.yaml> --key <top-level key> --value-file <value.yaml>
    plan-merge.py check             --file <plan.yaml> --root <checkout root>
    plan-merge.py sign-approval     --file <plan.yaml> --by <name> --date <YYYY-MM-DD> [--overrule PF-ID:<reason>]... [--rework rounds=N,minutes=M --decision <path>]
    plan-merge.py revoke-approval   --file <plan.yaml> --by <name> --reason "<text>"
    plan-merge.py delete-items      --file <plan.yaml> --task T-NN [--task T-NN]... [--decision D-NN]... --reason "<text>"

FEAT-59 (measured on FEAT-54's 23 pre-build runs, BRIEF ## Problem) retired four write
mechanics of this tool's own: `apply` refused any changed field on an existing id (exit 7), so
every plan revision cost one `amend --show`/`--expect-sha256` round trip per field — now the
proposal's fields REPLACE the base's, field by field, logged per field (except a task's
`status`: the station is `set-task-station`'s, and a proposal's value for an existing task is
IGNORED and said so, never laid over the base's); `lanes:` had no write route — `set-lanes`;
`set-panel` re-rendered every finding through the dumper so a diff could
not tell a carried finding from a changed one — both panel verbs now keep the bytes of any
finding whose id and content are unchanged; and pm spent whole runs transcribing a lead digest
into `panel:` — `record-panel` reads the digest itself. `check` resolves every `files:` anchor,
every `execution_agent` route and every `traces:` id before a plan is signed (SC-07), and a
line-number anchor `path:NN` is refused at write (plan_anchors.py). Any verb that changes the
task set or a task field on an APPROVED plan resets approval to `pending` with `reset_at` and
`reset_reason: <verb> <ids>` — `sign-approval` stays the only writer of `approved`.

PER-DOCUMENT COVERAGE, NOT PER-KEY (#1683). `set-lanes` closed "`lanes:` has no writer" for one
key, and the next stale key (`source_issues`, BUG-285) had no route again. `set-key` writes ANY
top-level key — replaced through its own bytes or inserted in template order — except the four
another verb owns for a reason: `approval` (sign-approval, DEC-120), `tasks` and `decisions`
(the union verbs, which reset a signature when the task set changes), and `status`
(set-feature-station). `panel` and `lanes` go through their own validators either way.

CONTROLLED VERBS, ONE WRITE ROUTE (FEAT-41 T-03). Every mutating verb goes through
harness_merge.locked_update and a text splice, and require_destination (exit 9) guards every
path. NEVER-DELETE IS A PROPERTY OF `apply` AND ITS ALIAS, NOT OF THE TOOL: the lock and the
splice are what fix #628 and they hold for every mutating verb, while never deleting a task is a
promise those two verbs alone make — and `delete-items` is the verb that promise left missing.
With `apply` unable to remove, `amend` able to replace ONE field of ONE existing item, and
FEAT-41 T-09's shape gate (#1045) denying every editor and shell write of a plan.yaml to every
author, an operator-ruled scope REMOVAL had no route at all: that is a missing verb, not a
missing permission. So `delete-items` removes WHOLE items from `tasks:` and `decisions:`, by id,
with a reason — never by predicate, never one field, never `approval:`, and never silently. An id
that is not in the plan, an id given twice, a SURVIVING task's `depends_on` still naming a task
that would go (issue #201's own defect), a result that fails the plan schema or does not reload
as the deletion that was computed: each is a loud non-zero refusal naming the concrete value, and
each leaves the file byte-identical. The reason is NEVER written into the plan — it exists so
the refusals can name why one was asked for, and so a caller cannot delete by reflex.

`set-task-station` and `set-feature-station` validate the station against the vocabulary
factory_config declares — MANDATED_STATIONS plus TERMINAL_STATIONS, imported, never respelled —
resolved through the harness.json of the checkout the target plan.yaml belongs to. The check runs
BEFORE the lock is taken, so a refused value never opens the file.

`approval:` has four controlled write paths: `apply` seeds a brand-new plan with the
unsigned `status: pending` mapping, `sign-approval` is the only path that can transition it
to approved or append an attributed risk acceptance to `approval.rulings`, the task-changing
verbs (`apply`, `add-tasks`, `amend --key tasks`, `delete-items --task`) RESET an approved plan
to pending — never the other way — and `revoke-approval` writes that same reset record on an
operator's word when no task changed (#1675: a signature withdrawn without a task-set change
was unrepresentable). Every other verb operating on an existing plan leaves its approval bytes
byte for byte. The main session — nobody else — signs or revokes approval through this tool
rather than by hand. A proposal that carries an approval mapping which PARSES differently from
the base's is a REFUSAL (exit 8), not a silent drop: `apply` must be INCAPABLE of writing a
signature (step 7) and must also NOTICE a caller that tried to sneak one past it (step 7b) —
two different jobs, so two different guards.

The creation exception is deliberately narrower than signing: a proposal cannot choose the pending
mapping's contents, and the tool emits only its fixed status. Without this bootstrap, a newly
created plan cannot later be signed because `sign-approval` correctly refuses to invent a missing
mapping.

Exit codes are the interface:
    0  applied — stdout lists ADDED/PRESERVED ids and REPLACED fields, an IGNORED line per
       proposal `status` on an existing task, an APPROVAL-RESET line when a signed plan was
       voided (verified on reload, never merely reported), an IGNORED-APPROVAL line if the
       proposal carried an approval block, and a final APPLIED line. For `check`: every anchor,
       route and trace resolved
    1  `check` only: at least one anchor, route or trace did not resolve — one FAIL line each
    2  a command line is unusable: `delete-items` with no --task and no --decision, the same id
       twice, or an empty --reason; `sign-approval --rework` without --decision, malformed, or
       with no sibling feature.json; `check --root` without a manifest; `set-key` naming a key
       another verb owns or one that is not a legal key name; or a `files:` entry in the
       line-number form `path:NN`, named (argparse's code, and `amend`'s missing-hash precedent)
    3  an id named by --task or --decision is absent from the plan, or the plan file itself is
       (the message names the ids present, scoped to the list the id was asked for)
    4  the value given to --station is not a legal station (the message lists the legal ones),
       or a requested deletion is not legal: a SURVIVING task's `depends_on` names a task being
       deleted, named pair by pair
    5  a side (base, proposal, key/panel/lanes value, lead digest) failed to parse or failed
       its shape check, or a splice does not reload as the edit that was computed or would make
       a legal plan illegal — for a deletion, that includes a survivor whose own fields moved
    6  the lock could not be acquired within the retry budget (harness_merge)
    7  the same top-level key carries two different loaded values (items no longer conflict:
       a proposal's fields replace the base's)
    8  the proposal's approval mapping parses differently from the base's
    9  --file does not resolve to a plan.yaml this tool owns
    10 `sign-approval` / `revoke-approval` invoked by a governed agent rather than the main session

python3 stdlib plus PyYAML (DEC-171 requires it here). Reads go through harness_yaml.py, same as
every other harness tool (issue #720): a duplicate mapping key refuses here exactly as it would
downstream, instead of merging clean and breaking the next reader. `import yaml` survives ONLY
for `yaml.safe_dump` — harness_yaml.py exposes no serializer, and this file never re-renders a
whole document through one regardless (see D-03 below); it splices bytes and re-parses its own
splice as a self-check.
"""
import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timedelta, timezone

import yaml

BIN_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BIN_DIR)
# The verbs live in the plan_merge package; this file is the one CLI every caller forks and
# the import surface check-state's INV-40 loads `signed_task_hash` from. (FEAT-70)
from plan_merge.amend import AMENDABLE_KEYS, cmd_amend  # noqa: E402
from plan_merge.union import cmd_apply  # noqa: E402
from plan_merge.check import cmd_check  # noqa: E402
from plan_merge.delete import cmd_delete_items  # noqa: E402
from plan_merge.amendments import cmd_record_amendments  # noqa: E402
from plan_merge.panel import cmd_record_panel, cmd_set_key, cmd_set_lanes, cmd_set_panel  # noqa: E402
from plan_merge.approval import cmd_revoke_approval, cmd_sign_approval  # noqa: E402
from plan_merge.stations import cmd_set_feature_station, cmd_set_task_station  # noqa: E402
from plan_merge.approval import signed_task_hash  # noqa: E402,F401  INV-40's import

# EVERY VERB IS A ROW, NOT A PARAGRAPH (FEAT-41 F-05). `main` regressed from grade 4 to 3 on ABC
# alone — cyclomatic 2, cognitive 1, ABC 23.8 — when T-03 turned one verb into five and each one
# added four more registration calls to the same body. There was no logic to simplify: the verb
# set is DATA, and it was written as control flow.
#
# EVERY ARGUMENT OF EVERY VERB IS `required=True`, which is what makes one loop honest rather
# than a lossy compression of five paragraphs. If a verb ever needs an optional argument, this
# table is the wrong shape for it and it gets its own registration — do not add a `required`
# column and keep pretending the rows are uniform.
_FILE = ("--file", "path to the plan.yaml")


_STATION = ("--station", "one of the six stations, or abandoned")


_PROPOSAL = ("--proposal", "path to the proposed plan.yaml, or - for stdin")


# NEVER-DELETE IS A PROPERTY OF THE FIRST TWO VERBS, NOT OF THE TOOL (FEAT-41 T-03). The lock
# and the splice are what fix #628 and they apply to every verb; never deleting a task is a
# separate promise that `apply` and its alias alone make, which is why they share `cmd_apply`
# verbatim. `delete-items` is what that distinction was always for: it deletes, by id and with
# a reason, through the same lock and the same splice, and it registers itself below rather
# than here because its id flags repeat.
VERBS = (
    ("apply", "merge a proposal into a plan.yaml — adds items, replaces the fields a proposal "
              "names on an existing id, never deletes",
     (_FILE, _PROPOSAL), cmd_apply),
    ("add-tasks", "alias of apply, for callers that only add tasks — identical code path",
     (_FILE, _PROPOSAL), cmd_apply),
    ("set-task-station", "set ONE task's status, by splicing its one line",
     (_FILE, ("--task", "the task id, T-NN"), _STATION), cmd_set_task_station),
    ("set-feature-station", "set or insert the top-level status key",
     (_FILE, _STATION), cmd_set_feature_station),
    ("set-panel", "replace the top-level panel mapping with a validated value, keeping the "
                  "bytes of every unchanged finding",
     (_FILE, ("--value-file", "YAML file holding the replacement panel mapping")), cmd_set_panel),
    ("set-lanes", "replace the top-level lanes mapping with a validated value",
     (_FILE, ("--value-file", "YAML file holding the replacement lanes mapping")), cmd_set_lanes),
    ("set-key", "set or insert ANY top-level key from a YAML value file — except approval, "
                "tasks, decisions and status, which name their own verb",
     (_FILE, ("--key", "the top-level key name"),
      ("--value-file", "YAML file holding the key's replacement value")), cmd_set_key),
    ("revoke-approval", "withdraw a standing signature: approval.status approved -> pending with "
                        "reset_at and reset_reason; main session only",
     (_FILE, ("--by", "the operator withdrawing the signature"),
      ("--reason", "why, one clause; written to approval.reset_reason")), cmd_revoke_approval),
    ("check", "resolve every files: anchor, execution_agent route and traces: id; writes nothing",
     (_FILE, ("--root", "the checkout root anchors and routes resolve against")), cmd_check),
    ("record-amendments", "splice an engineering lead's digest amendments into the named task "
                          "fields and ledger one amendment judgement per entry — compare-and-"
                          "splice on `was`, all-or-nothing across plan.yaml and feature.json",
     (_FILE, ("--digest", "the engineering lead's digest.md — its fenced DIGEST block is parsed")),
     cmd_record_amendments),
)


def _register_record_panel(sub):
    """ITS OWN REGISTRATION: `--last-run` is optional (it defaults to the digest's run
    directory) and `--cycle` is typed, neither of which the uniform table can express."""
    p = sub.add_parser("record-panel",
                       help="write the panel mapping FROM the validator lead's digest, carrying "
                            "every finding already present byte for byte")
    p.add_argument("--file", required=True, help="path to the plan.yaml")
    p.add_argument("--digest", required=True,
                   help="the validator lead's digest.md — its fenced DIGEST block is parsed")
    p.add_argument("--cycle", required=True, type=int, help="the panel cycle being recorded")
    p.add_argument("--last-run", default=None,
                   help="the run directory name to record; defaults to the digest's parent dir")
    p.set_defaults(func=cmd_record_panel)


def _register_sign_approval(sub):
    p = sub.add_parser("sign-approval", help="the ONLY route that writes the approval mapping")
    p.add_argument("--file", required=True, help="path to the plan.yaml")
    p.add_argument("--by", required=True, help="the signer's name")
    p.add_argument("--date", required=True, help="YYYY-MM-DD")
    p.add_argument(
        "--overrule", action="append", default=[], metavar="FINDING-ID:REASON",
        help="accept a current panel finding's risk; repeat for multiple findings",
    )
    p.add_argument("--rework", default=None, metavar="rounds=N,minutes=M",
                   help="the operator's ONE rework ruling (SC-15), recorded on the sibling "
                        "feature.json as `rework`; needs --decision")
    p.add_argument("--decision", default=None, metavar="PATH",
                   help="where the rework ruling is recorded (feature.json rework.decision)")
    p.set_defaults(func=cmd_sign_approval)


def _register_amend(sub):
    """ITS OWN REGISTRATION, BY THE VERBS TABLE'S OWN INSTRUCTION (BUG-1128).

    That table says: if a verb ever needs an optional argument, the table is the wrong
    shape for it and it gets its own registration — do not add a `required` column and
    keep pretending the rows are uniform. `amend` has three optional arguments, because
    `--show` legitimately takes neither a hash nor a value. So it registers here rather
    than corrupting the uniformity that makes that loop honest.
    """
    p = sub.add_parser("amend", help="replace ONE field of ONE named task or decision, "
                                     "compare-and-swap on its sha256")
    p.add_argument("--file", required=True, help="path to the plan.yaml")
    p.add_argument("--key", required=True,
                   help=f"which list the id lives in: {' | '.join(AMENDABLE_KEYS)}")
    p.add_argument("--id", required=True, help="the item id, T-NN or D-NN")
    p.add_argument("--field", required=True, help="the field to replace, e.g. verify, because")
    p.add_argument("--show", action="store_true",
                   help="print the current field block and its sha256, and write nothing")
    p.add_argument("--expect-sha256", default=None,
                   help="the sha256 --show reported; a replace is refused without it")
    p.add_argument("--value-file", default=None,
                   help="file holding the replacement value; may be multi-line")
    p.add_argument("--yaml-value", action="store_true",
                   help="read/write the value-file as a YAML list or mapping")
    p.set_defaults(func=cmd_amend)


def _register_delete_items(sub):
    """ITS OWN REGISTRATION, BY THE VERBS TABLE'S OWN INSTRUCTION.

    `--task` and `--decision` REPEAT, and neither is required on its own — one of the two is,
    which is a rule no `required=True` column can express. The table says so itself: a verb
    that needs an optional argument gets its own registration rather than a `required` column
    that makes the rows only look uniform. The one-of-two rule is enforced in
    `_requested_deletions`, before the lock, where it can say what was missing.
    """
    p = sub.add_parser("delete-items",
                       help="delete WHOLE tasks and/or decisions by id, with a stated reason")
    p.add_argument("--file", required=True, help="path to the plan.yaml")
    p.add_argument("--task", action="append", default=[], metavar="T-NN",
                   help="a task id to delete; repeat the flag for more")
    p.add_argument("--decision", action="append", default=[], metavar="D-NN",
                   help="a decision id to delete; repeat the flag for more")
    p.add_argument("--reason", required=True,
                   help="why these items are going; printed on the receipt, never written "
                        "into the plan")
    p.set_defaults(func=cmd_delete_items)


def main():
    parser = argparse.ArgumentParser(prog="plan-merge.py")
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name, helptext, arguments, func in VERBS:
        p = sub.add_parser(name, help=helptext)
        for flag, arghelp in arguments:
            p.add_argument(flag, required=True, help=arghelp)
        p.set_defaults(func=func)
    _register_record_panel(sub)
    _register_sign_approval(sub)
    _register_amend(sub)
    _register_delete_items(sub)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
