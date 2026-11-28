#!/usr/bin/env python3
"""feature-record.py — the thin CLI that writes FEAT-59's judgement and spend ledger into
feature.json (SC-15, SC-18, SC-19, SC-21). It parses and dispatches; each verb lives in the
feature_record package, loads the current document, applies exactly its one structured op, and
hands the result to feature_record.write.write_feature_json, which locks, schema-validates the
candidate and atomically replaces the file — or refuses, leaving it byte-for-byte unchanged, and
this CLI prints the refusal lines and exits its code.

VERBS
  run-start     append a runs[] entry with started_at and verdict PENDING; refuses (exit 2)
                when an entry with that id already exists.
  run-end       stamp ended_at, verdict, the lead-reported run cycles, and optionally tokens /
                code_grade on an existing entry; refuses (exit 2) when there is none.
  stamp-tokens  write the host-measured tokens onto the ONE open run (started_at set, ended_at
                absent); refuses (exit 2) when no run or more than one is open (BUG-1724).
  close-run     ONE close-out (BUG-1723): validate-digest.py <run's agent> <digest>, then
                run-end, then plan-merge.py set-task-station when --task/--station are given,
                then judgement (as harness-orchestrator) when --judgement is given, then spend;
                --cycles-used is forwarded to run-end
                — existing subprocess authorities plus the shared atomic run-end transaction;
                the first refusal stops the sequence naming its stage, earlier durable writes stay. Prints ONE
                line on success. Never takes --tokens: the host hook stamps those.
                --refused-return (#2068) closes a run whose lead return the host refused:
                verdict BLOCKED only, and the digest stage inverts — it refuses if the digest
                validates, since that return landed and closes normally. Only close-run can
                create this disposition; run-end can replay an already refused historical run.
  judgement     append one {at, by, kind, decision, reason} to judgements[] (SC-21).
  set-rework    write the operator's one rework ruling (SC-15); --decision must be a file
                under the feature's own directory (refuses exit 2 otherwise).
  raise-cycles  write max_total_cycles AND append the budget_decisions[] record the raise rests
                on (DEC-157); refuses (exit 2) a value that does not raise it, or a --decision
                that is not a file under the feature's own directory.
  set-mission   write mission: patch | plan (SC-01) AND append the `kind: mission` judgement
                deciding it, from --by / --reason, in the same locked write — so a mission
                never exists without the entry check-state.py INV-40 demands (SC-21).
  pin-review    write review_sha as the full id of --sha (default HEAD), resolved in the
                feature's repository; refuses (exit 2), writing nothing, a sha that is not a
                commit (#2167).
  propose-rework read-only: print {rounds, minutes, basis} — the baseline ruling the main
                session shows the operator at signature (patch: 1 round; plan: tasks/3,
                floor 2, cap max_total_cycles; minutes = rounds x budgets.rework_round_minutes).
  spend         read-only: print one JSON object {runs, wall_clock_minutes, tokens, phase,
                rework_minutes, rework_rounds} — the last two are the rework window, from
                the first validate run; the ruling is compared to those, never the whole.
                A round is a `regate` judgement in the window; a window with none counts its
                `fix-` runs instead (#2222).
                Minutes are elapsed time (concurrent runs counted once); tokens are a sum.

THE OPERATOR'S RULINGS ARE MAIN-SESSION-ONLY. set-rework and raise-cycles are gated by
plan-sign-gate.py the way plan-merge.py sign-approval is: an agent's call is refused before it
runs. This CLI adds the second half — `--decision` must resolve to an existing file under the
feature directory — so the record a ruling rests on is a document, not a string INV-39 would
accept on the strength of its own syntax.

TOKENS ARE MEASURED BY THE HOST, OR NULL — THIS TOOL NEVER ESTIMATES (SC-18). Under OMP the
harness hook reads the figure off the orchestrator's task result and runs `stamp-tokens` on the
open run before that run is closed; a bare `run-end` then preserves it (BUG-1724). `run-end
--tokens N` remains the explicit override for a host that reported nothing. A run that reaches
run-end with no figure is written null, and `spend` prints null when no run carries an integer,
so a reader can always tell "unmeasured" from "zero". Wall-clock minutes are likewise a sum of
recorded ended_at - started_at spans, floored to whole minutes; an open run, or one predating
FEAT-59, contributes zero rather than a guess.

CYCLES ARE REPORTED BY THE LEAD, NEVER INFERRED. `run-end --cycles-used C` records C on the
run and adjusts the feature-level total by the difference from that run's prior value. Repeating
the same cycle report leaves the total unchanged while preserving legacy unattributed cycles.

EXIT CODES: 0 on success; 2 for this CLI's own refusals (unknown id, duplicate id, non-raise,
argparse); feature_record.write / harness_merge codes propagate unchanged (11 schema or missing
file, 9 destination, 6 lock). python3 stdlib only.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from feature_record.budget import (  # noqa: E402  (local import, after sys.path fix-up)
    MISSIONS, cmd_pin_review, cmd_propose_rework, cmd_raise_cycles, cmd_set_mission,
    cmd_set_rework)
from feature_record.judgements import (  # noqa: E402
    JUDGEMENT_KINDS, cmd_judgement, cmd_overrule_amendment)
from feature_record.runs import (  # noqa: E402
    cmd_close_run, cmd_record_history, cmd_run_end, cmd_run_start, cmd_stamp_tokens)
from feature_record.spend import cmd_spend  # noqa: E402


def _int_at_least(minimum):
    def parse(raw):
        value = int(raw)
        if value < minimum:
            raise argparse.ArgumentTypeError(f"must be >= {minimum}, got {value}")
        return value
    return parse


def _with_file(p):
    p.add_argument("--file", required=True, help="path to feature.json")
    return p


def _register_run_start(sub):
    p = _with_file(sub.add_parser("run-start", help="append a PENDING runs[] entry"))
    p.add_argument("--id", required=True)
    p.add_argument("--squad", required=True)
    p.add_argument("--agent", help="the agent executing the run (required for new features)")
    p.add_argument("--by", help="the persona judging what this open owes (with --reason)")
    p.add_argument("--reason", help="one line, at most 240 characters, shared by the judgement(s) below")
    p.add_argument("--regate", help="the re-gate decision when the run this one follows is a FAIL "
                                    "(INV-40 b), e.g. 'validate cycle 2'")
    p.add_argument("--succession", choices=("continue", "downgrade", "stop"),
                   help="the decision on the handoff this run succeeds (INV-40 c, INV-43)")
    p.set_defaults(func=cmd_run_start)

    for verb in ("record-cycle-evidence", "record-refusal"):
        p = _with_file(sub.add_parser(verb, help="attach authorized historical provenance"))
        p.add_argument("--id", required=True)
        p.add_argument("--digest", required=True)
        p.add_argument("--evidence", required=True)
        p.add_argument("--by", required=True)
        p.add_argument("--yes", action="store_true", required=True)
        if verb == "record-refusal":
            p.add_argument("--reason", required=True)
        p.set_defaults(func=cmd_record_history)


def _register_run_end(sub):
    p = _with_file(sub.add_parser("run-end", help="close a runs[] entry"))
    p.add_argument("--id", required=True)
    p.add_argument("--verdict", required=True)
    p.add_argument("--cycles-used", required=True, type=_int_at_least(0),
                   help="send-backs REPORTED by this run's lead; never inferred")
    p.add_argument("--tokens", type=_int_at_least(0),
                   help="tokens MEASURED from the transcript; omit when unmeasured (null)")
    p.add_argument("--code-grade", choices=["n_a"], dest="code_grade")
    p.add_argument("--digest", help="authentic target-local evidence for new/changed attribution")
    p.set_defaults(func=cmd_run_end)

    p = _with_file(sub.add_parser("stamp-tokens",
                                  help="write the host-measured tokens onto the ONE open run"))
    p.add_argument("--tokens", required=True, type=_int_at_least(0),
                   help="tokens the host reported for the dispatch this run records")
    p.set_defaults(func=cmd_stamp_tokens)


def _register_close_run(sub):
    p = _with_file(sub.add_parser("close-run",
                                  help="ONE close-out: validate the digest, run-end, optional "
                                       "task station, optional judgement, then print spend"))
    p.add_argument("--id", required=True, help="the run to close")
    p.add_argument("--digest", required=True, help="the lead's digest.md for that run")
    p.add_argument("--verdict", required=True)
    p.add_argument("--cycles-used", required=True, type=_int_at_least(0),
                   help="the lead DIGEST's reported send-back count for this run, forwarded to run-end")
    p.add_argument("--task", help="with --station: the task whose station to set")
    p.add_argument("--station", help="with --task: the station to set")
    p.add_argument("--judgement", help="kind=<kind>,decision=<d>,reason=<r>, recorded as "
                                       "harness-orchestrator")
    p.add_argument("--code-grade", choices=["n_a"], dest="code_grade")
    p.add_argument("--refused-return", action="store_true", dest="refused_return",
                   help="the host refused the lead's final return, so its digest carries no "
                        "valid record: close BLOCKED, refusing if the digest does validate")
    p.add_argument("--evidence", help="target-local authorization for new/changed refused attribution")
    p.add_argument("--by", help="operator authorizing a refused-run attribution")
    p.set_defaults(func=cmd_close_run)


def _register_judgements(sub):
    p = _with_file(sub.add_parser("judgement", help="append one judgement to the ledger"))
    p.add_argument("--by", required=True)
    p.add_argument("--kind", required=True, choices=JUDGEMENT_KINDS)
    p.add_argument("--decision", required=True)
    p.add_argument("--reason", required=True, help="one line, at most 240 characters")
    p.set_defaults(func=cmd_judgement)

    p = _with_file(sub.add_parser("overrule-amendment",
                                  help="mark ONE amendment judgement overruled by the operator"))
    p.add_argument("--at", required=True,
                   help="the amendment's exact `at` timestamp, copied from the ledger")
    p.set_defaults(func=cmd_overrule_amendment)


def _register_budget(sub):
    p = _with_file(sub.add_parser("set-rework", help="write the operator's rework ruling"))
    p.add_argument("--rounds", required=True, type=_int_at_least(0))
    p.add_argument("--minutes", required=True, type=_int_at_least(0))
    p.add_argument("--decision", required=True,
                   help="where the ruling is recorded: a file under the feature directory, "
                        "optionally with a #fragment")
    p.set_defaults(func=cmd_set_rework)

    p = _with_file(sub.add_parser("raise-cycles", help="raise max_total_cycles with its record"))
    p.add_argument("--to", required=True, type=_int_at_least(1))
    p.add_argument("--decision", required=True,
                   help="the recorded user decision: a file under the feature directory, "
                        "optionally with a #fragment")
    p.set_defaults(func=cmd_raise_cycles)


def _register_mission_and_pin(sub):
    p = _with_file(sub.add_parser("set-mission",
                                  help="write the mission and the judgement deciding it"))
    p.add_argument("--mission", required=True, choices=MISSIONS)
    p.add_argument("--by", required=True, help="the persona that judged the mission")
    p.add_argument("--reason", required=True, help="one line, at most 240 characters")
    p.set_defaults(func=cmd_set_mission)

    p = _with_file(sub.add_parser("pin-review",
                                  help="pin review_sha to a commit (default HEAD) as a full id"))
    p.add_argument("--sha", default="HEAD", help="the commit the readers diff; default HEAD")
    p.set_defaults(func=cmd_pin_review)


def _register_spend(sub):
    p = _with_file(sub.add_parser("spend", help="print the feature's measured spend as JSON"))
    p.set_defaults(func=cmd_spend)


def _register_proposal(sub):
    p = _with_file(sub.add_parser("propose-rework",
                                  help="print the baseline rework ruling for signature as JSON"))
    p.set_defaults(func=cmd_propose_rework)


# Verb order is the help order the baseline printed; propose-rework (budget) follows spend.
_REGISTRARS = (_register_run_start, _register_run_end, _register_close_run, _register_judgements,
               _register_budget, _register_mission_and_pin, _register_spend, _register_proposal)


def main():
    parser = argparse.ArgumentParser(prog="feature-record.py")
    sub = parser.add_subparsers(dest="cmd", required=True)
    for register in _REGISTRARS:
        register(sub)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
