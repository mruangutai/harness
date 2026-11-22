#!/usr/bin/env python3
"""FEAT-2229 SC-01: the `decisions_affected:` row shape contract.

`harness_yaml.validate_plan_doc` is the one schema home (FEAT-41 HIGH-1), so the shape is
tested there directly: a list of mappings with exactly dec, disposition, clause, successor and
reason; absence stays legal so older plans keep loading. The writer half runs the real
plan-merge.py CLI: set-key and apply carry rows losslessly, and a refused malformed row leaves
the plan byte-identical (no partial write).
"""
import os
import shutil
import subprocess
import sys
import tempfile

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
BIN_DIR = os.path.join(ROOT, ".claude", "skills", "harness", "bin")
sys.path.insert(0, BIN_DIR)

import harness_yaml  # noqa: E402
import yaml  # noqa: E402

CLI = os.path.join(BIN_DIR, "plan-merge.py")
ENV = {k: v for k, v in os.environ.items()
       if k not in ("CLAUDE_PROJECT_DIR", "HARNESS_PROJECT_DIR", "HARNESS_AGENT_TYPE")}
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok)))
    print(f"{'PASS' if ok else 'FAIL'} {name}" + ("" if ok else f" :: {detail}"))


TASK = {"id": "T-01", "title": "t", "change_type": "logic", "execution_mode": "main-session-direct",
        "files": ["a.py"], "verify": "true", "intent": "do it"}


def row(**over):
    base = {"dec": "DEC-12", "disposition": "keep", "clause": "a clause", "successor": "none",
            "reason": "one line"}
    base.update(over)
    return base


def doc_with(value, present=True):
    doc = {"feature": "FEAT-99-fixture", "approval": {"status": "pending"}, "tasks": [dict(TASK)]}
    if present:
        doc["decisions_affected"] = value
    return doc


def schema_error(doc):
    try:
        harness_yaml.validate_plan_doc(doc, "<test>")
    except harness_yaml.PlanSchemaError as exc:
        return str(exc)
    return None


def expect_legal(name, doc):
    err = schema_error(doc)
    check(name, err is None, err)


def expect_illegal(name, doc, needle):
    err = schema_error(doc)
    check(name, err is not None and needle in err, err)


def case_block_types():
    expect_legal("absent decisions_affected stays legal (older plans load)", doc_with(None, False))
    expect_legal("explicit empty list is a legal claim", doc_with([]))
    expect_illegal("a mapping block is refused", doc_with({"dec": "DEC-1"}), "decisions_affected")
    expect_illegal("a null block is refused", doc_with(None), "decisions_affected")
    expect_illegal("a string row is refused", doc_with(["DEC-1 keep"]), "decisions_affected[0]")
    expect_illegal("a list row is refused", doc_with([[row()]]), "decisions_affected[0]")


def case_keys():
    for key in ("dec", "disposition", "clause", "successor", "reason"):
        bad = row()
        del bad[key]
        expect_illegal(f"a row missing {key} is refused", doc_with([bad]), key)
    expect_illegal("a sixth key is refused", doc_with([row(task="T-01")]), "task")


def case_dispositions():
    expect_legal("keep with successor none", doc_with([row()]))
    for disp in ("amend", "strike"):
        expect_legal(f"{disp} naming a D id", doc_with([row(disposition=disp, successor="D-01")]))
        expect_legal(f"{disp} naming a DEC id", doc_with([row(disposition=disp, successor="DEC-300")]))
        expect_illegal(f"{disp} with successor none is refused",
                       doc_with([row(disposition=disp, successor="none")]), "successor")
        expect_illegal(f"{disp} with a free-text successor is refused",
                       doc_with([row(disposition=disp, successor="later")]), "successor")
    expect_illegal("keep naming a successor is refused", doc_with([row(successor="D-01")]), "successor")
    expect_illegal("an unknown disposition is refused", doc_with([row(disposition="retire")]),
                   "disposition")
    expect_illegal("a title-case disposition is refused", doc_with([row(disposition="Keep")]),
                   "disposition")


def case_dec_and_clause_values():
    expect_illegal("a non-DEC dec is refused", doc_with([row(dec="D-01")]), "dec")
    expect_illegal("a lowercase dec is refused", doc_with([row(dec="dec-12")]), "dec")
    expect_illegal("an empty clause is refused", doc_with([row(clause="")]), "clause")
    expect_illegal("a whitespace clause is refused", doc_with([row(clause="   ")]), "clause")
    expect_illegal("a non-string clause is refused", doc_with([row(clause=12)]), "clause")
    expect_legal("a clause keeps its markdown verbatim", doc_with([row(clause="`x` is **y**;")]))


def case_reason_and_successor_values():
    expect_illegal("an empty reason is refused", doc_with([row(reason="")]), "reason")
    expect_illegal("a two-line reason is refused", doc_with([row(reason="a\nb")]), "reason")
    expect_illegal("a non-string successor is refused", doc_with([row(successor=None)]), "successor")


def _plan_root():
    root = tempfile.mkdtemp(prefix="disposition-schema-")
    feat = os.path.join(root, ".harness", "harness", "features", "FEAT-99-fixture")
    os.makedirs(feat)
    return root, os.path.join(feat, "plan.yaml")


def run(*argv):
    return subprocess.run([sys.executable, CLI, *argv], capture_output=True, text=True, env=ENV)


PLAN = ("schema: plan/1\nfeature: FEAT-99-fixture\napproval:\n  status: pending\n"
        "drafted_at: '2026-11-21T00:00:00Z'\ntasks:\n- id: T-01\n  title: t\n  change_type: logic\n"
        "  execution_mode: main-session-direct\n  files:\n  - a.py\n  verify: 'true'\n"
        "  intent: do it\n")
ROWS = [row(clause="`quoted` **md**: x"),
        row(dec="DEC-188", disposition="amend", successor="D-01", reason="r: with colon"),
        row(dec="DEC-90", disposition="strike", successor="DEC-300")]


def case_set_key_round_trip():
    root, plan = _plan_root()
    try:
        with open(plan, "w", encoding="utf-8") as fh:
            fh.write(PLAN)
        value = os.path.join(root, "value.yaml")
        with open(value, "w", encoding="utf-8") as fh:
            yaml.safe_dump(ROWS, fh, sort_keys=False)
        r = run("set-key", "--file", plan, "--key", "decisions_affected", "--value-file", value)
        check("set-key writes decisions_affected", r.returncode == 0, r.stdout + r.stderr)
        loaded = harness_yaml.load_file(plan)
        check("set-key round-trips every row losslessly", loaded.get("decisions_affected") == ROWS,
              loaded.get("decisions_affected"))
        before = open(plan, "rb").read()
        with open(value, "w", encoding="utf-8") as fh:
            yaml.safe_dump([row(disposition="amend")], fh)
        r = run("set-key", "--file", plan, "--key", "decisions_affected", "--value-file", value)
        check("set-key refuses a malformed row", r.returncode != 0, r.stdout + r.stderr)
        check("a refused row leaves the plan byte-identical", open(plan, "rb").read() == before)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def case_apply_creation_round_trip():
    root, plan = _plan_root()
    try:
        proposal = os.path.join(root, "proposal.yaml")
        body = PLAN.replace("approval:\n  status: pending\n", "").replace(
            "drafted_at: '2026-11-21T00:00:00Z'\n", "")
        with open(proposal, "w", encoding="utf-8") as fh:
            fh.write(body + yaml.safe_dump({"decisions_affected": ROWS}, sort_keys=False))
        r = run("apply", "--file", plan, "--proposal", proposal)
        check("apply creates a plan carrying rows", r.returncode == 0, r.stdout + r.stderr)
        loaded = harness_yaml.load_file(plan) if os.path.exists(plan) else {}
        check("apply creation round-trips every row losslessly",
              loaded.get("decisions_affected") == ROWS, loaded)
        with open(proposal, "w", encoding="utf-8") as fh:
            fh.write(body + yaml.safe_dump({"decisions_affected": ROWS}, sort_keys=False))
        before = open(plan, "rb").read()
        r = run("apply", "--file", plan, "--proposal", proposal)
        check("re-applying the same rows is a no-op merge", r.returncode == 0
              and open(plan, "rb").read() == before, r.stdout + r.stderr)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def main():
    case_block_types()
    case_keys()
    case_dispositions()
    case_dec_and_clause_values()
    case_reason_and_successor_values()
    case_set_key_round_trip()
    case_apply_creation_round_trip()
    failed = [name for name, ok in RESULTS if not ok]
    print(f"{len(RESULTS) - len(failed)}/{len(RESULTS)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
