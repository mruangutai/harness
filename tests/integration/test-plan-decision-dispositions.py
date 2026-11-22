#!/usr/bin/env python3
"""FEAT-2229 SC-01..SC-03: forward-only decision dispositions, end to end through the CLI.

Every case runs the real plan-merge.py against an isolated temporary checkout (team-config
manifest, harness.json era, segment DECISIONS.md + DECISIONS-INDEX.md, a sibling BRIEF), with
the inherited Harness root/persona environment removed. Covered:

  * `check` on an eligible pending draft: the six mandatory failures each alone (missing
    block, unindexed dec, keep/amend on STRUCK, clause not in the decision's own section,
    unresolved successor, no task owning DECISIONS.md), the valid controls, and served-segment
    authority selection;
  * the era: both sides of activation and the exact boundary, null and missing configuration,
    malformed era and draft instants, approved/landed history, undated legacy drafts;
  * the writer: `apply` creation stamps drafted_at once and refuses a caller's; set-key and
    apply refuse every rewrite/insert/null of drafted_at with complete plan bytes unchanged, on
    both merge rendering paths; ordinary edits keep the stamp or its absence.
"""
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

import yaml

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
BIN_DIR = os.path.join(ROOT, ".claude", "skills", "harness", "bin")
CLI = os.path.join(BIN_DIR, "plan-merge.py")
ENV = {k: v for k, v in os.environ.items()
       if k not in ("CLAUDE_PROJECT_DIR", "HARNESS_PROJECT_DIR", "HARNESS_AGENT_TYPE")}
RESULTS = []

ERA = "2026-11-21T12:00:00Z"
BEFORE_ERA = "2026-11-21T11:59:59Z"
AFTER_ERA = "2026-11-21T12:00:01Z"
_UNSET = object()

DECISIONS_MD = """# Decision Log

## DEC-10 — Ten

The ten clause is here.
A `marked` **clause** stays verbatim.

### DEC-10 detail

Detail under ten.

## DEC-11 — Eleven

Only eleven says this.

## DEC-12 — Twelve

Twelve was struck.

## DEC-13 — Thirteen

Thirteen was struck in title case.
"""

DECISIONS_INDEX = """<!-- index-contract v1 -->
# DECISIONS — index

- DEC-10 @3 [plan] refs:  :: Ten rules.
- DEC-11 @13 [plan] refs:  :: Eleven rules.
- DEC-12 @17 [plan] refs: DEC-188 :: STRUCK under DEC-188: twelve is gone.
- DEC-13 @21 [plan] refs: DEC-188 :: Struck under DEC-188: thirteen is gone.
"""

SERVED_DECISIONS_MD = "# Kaya log\n\n## DEC-50 — Fifty\n\nFifty is served.\n"
SERVED_INDEX = "# index\n\n- DEC-50 @3 [plan] refs:  :: Fifty.\n"

DOCS_REL = ".harness/harness/docs/DECISIONS.md"


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok)))
    print(f"{'PASS' if ok else 'FAIL'} {name}" + ("" if ok else f" :: {detail}"))


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def read_bytes(path):
    with open(path, "rb") as fh:
        return fh.read()


def run(*argv, cli=CLI, env=None):
    return subprocess.run([sys.executable, cli, *argv], capture_output=True, text=True,
                          env=env or ENV)


def make_root(era=ERA, segment="harness"):
    """A checkout `check --root` resolves against; `era` _UNSET omits the key (pre-adoption).
    The checkout sits at <base>/harness so a served segment's workspace can be its sibling."""
    root = os.path.join(os.path.realpath(tempfile.mkdtemp(prefix="plan-dispositions-")), "harness")
    write(os.path.join(root, ".harness", "team-config.yaml"),
          "schema_version: 1\nteams:\n  - name: eng\n    members:\n"
          "      - name: harness-backend-dev\n        domain:\n"
          "          - { path: src/**, upsert: true }\n")
    config = {"schema_version": 2}
    if era is not _UNSET:
        config["decision_dispositions_era_start"] = era
    write(os.path.join(root, ".harness", "harness.json"), json.dumps(config))
    write(os.path.join(root, DOCS_REL), DECISIONS_MD)
    write(os.path.join(root, ".harness", "harness", "docs", "DECISIONS-INDEX.md"), DECISIONS_INDEX)
    write(os.path.join(root, "src", "a.py"), "def foo():\n    return 1\n")
    feat = os.path.join(root, ".harness", segment, "features", "FEAT-99-fixture")
    write(os.path.join(feat, "BRIEF.md"), "# BRIEF\n\n## Success criteria\n\n- SC-01: a\n")
    return root, os.path.join(feat, "plan.yaml")


def task(tid, files):
    return {"id": tid, "title": "t", "change_type": "logic",
            "execution_mode": "main-session-direct", "traces": ["SC-01"], "files": files,
            "verify": "true", "intent": "do it"}


OWNER = task("T-02", [DOCS_REL])


def plan_text(rows=_UNSET, drafted=ERA, status="pending", tasks=None, extra=None):
    doc = {"schema": "plan/1", "feature": "FEAT-99-fixture", "approval": {"status": status}}
    if status == "approved":
        doc["approval"].update({"approved_by": "x", "date": "2026-11-21"})
    if drafted is not _UNSET:
        doc["drafted_at"] = drafted
    doc.update(extra or {})
    doc["decisions"] = [{"id": "D-01", "choice": "c", "because": "b"}]
    if rows is not _UNSET:
        doc["decisions_affected"] = rows
    doc["tasks"] = tasks if tasks is not None else [task("T-01", ["src/a.py"]), OWNER]
    return yaml.safe_dump(doc, sort_keys=False, allow_unicode=True)


def row(dec="DEC-10", disposition="keep", clause="The ten clause is here.", successor="none"):
    return {"dec": dec, "disposition": disposition, "clause": clause, "successor": successor,
            "reason": "because"}


def _served_checkout(root):
    """The fleet serving org/kaya and kaya's paired code worktree (the #2064 fixture shape);
    returns the code worktree."""
    workspace = os.path.join(os.path.dirname(root), "workspace")
    write(os.path.join(root, ".harness", "factory", "fleet.yaml"),
          yaml.safe_dump({"schema": "factory-fleet/1", "workspace_root": workspace,
                          "repos": [{"name": "org/kaya", "default_branch": "main"}]}))
    code = os.path.join(workspace, "kaya", ".claude", "worktrees", "kaya", "FEAT-99-fixture")
    gitdir = os.path.join(workspace, "kaya", ".git", "worktrees", "FEAT-99-fixture")
    write(os.path.join(gitdir, "gitdir"), os.path.join(code, ".git") + "\n")
    write(os.path.join(code, ".git"), f"gitdir: {gitdir}\n")
    write(os.path.join(code, "src", "a.py"), "def foo():\n    return 1\n")
    return code


def run_check(text, era=ERA, segment="harness", setup=None):
    root, plan = make_root(era, segment)
    try:
        write(plan, text)
        if setup:
            setup(root)
        argv, env = ["check", "--file", plan, "--root", root], None
        if segment != "harness":
            argv += ["--code-root", _served_checkout(root)]
            # The resolver answers from the fixture's manifest and fleet, as test-plan-merge's
            # #2064 cases do; the live checkout's fleet would not know this workspace.
            env = dict(ENV, HARNESS_PROJECT_DIR=root)
        r = run(*argv, env=env)
        return r.returncode, r.stdout + r.stderr
    finally:
        shutil.rmtree(os.path.dirname(root), ignore_errors=True)


def expect_pass(name, text, **kw):
    rc, out = run_check(text, **kw)
    check(name, rc == 0, out)


def expect_fail(name, text, needles, **kw):
    rc, out = run_check(text, **kw)
    fails = [line for line in out.splitlines() if line.startswith("FAIL")]
    check(name, rc == 1 and all(any(n in line for line in fails) for n in needles), out)


# --- check: the mandatory failures and their controls ------------------------------------


def case_valid_controls():
    expect_pass("explicit empty list passes", plan_text([]))
    expect_pass("keep with the clause in its own section passes", plan_text([row()]))
    expect_pass("a markdown clause matches verbatim",
                plan_text([row(clause="A `marked` **clause** stays verbatim.")]))
    expect_pass("a clause under a deeper subheading is still the decision's section",
                plan_text([row(clause="Detail under ten.")]))
    expect_pass("amend to this plan's D id passes",
                plan_text([row(disposition="amend", successor="D-01")]))
    expect_pass("strike to an indexed DEC passes",
                plan_text([row(dec="DEC-11", disposition="strike", clause="Only eleven says this.",
                               successor="DEC-10")]))
    expect_pass("strike of a STRUCK decision is permitted",
                plan_text([row(dec="DEC-12", disposition="strike", clause="Twelve was struck.",
                               successor="D-01")]))


def case_missing_block():
    expect_fail("an eligible draft without decisions_affected fails", plan_text(),
                ["decisions_affected"])


def case_unindexed_dec():
    expect_fail("an unindexed dec fails with row index and dec",
                plan_text([row(), row(dec="DEC-99", clause="x")]),
                ["decisions_affected[1] DEC-99"])


def case_struck():
    expect_fail("keep on STRUCK fails", plan_text([row(dec="DEC-12", clause="Twelve was struck.")]),
                ["decisions_affected[0] DEC-12", "STRUCK"])
    expect_fail("amend on title-case Struck fails",
                plan_text([row(dec="DEC-13", disposition="amend",
                               clause="Thirteen was struck in title case.", successor="D-01")]),
                ["decisions_affected[0] DEC-13", "STRUCK"])


def case_clause_location():
    expect_fail("a clause from a neighbouring section fails",
                plan_text([row(dec="DEC-11", clause="The ten clause is here.")]),
                ["decisions_affected[0] DEC-11", "clause"])
    expect_fail("a partial clause match fails",
                plan_text([row(clause="The ten clause is here!")]),
                ["decisions_affected[0] DEC-10", "clause"])
    expect_fail("markdown is not normalised away",
                plan_text([row(clause="A marked clause stays verbatim.")]),
                ["decisions_affected[0] DEC-10", "clause"])
    expect_fail("whitespace is not normalised away",
                plan_text([row(clause="The ten  clause is here.")]),
                ["decisions_affected[0] DEC-10", "clause"])


# F2 (validate c1): fenced examples inside DEC-11 impersonate DEC-10's heading — once with a
# plain fence, once with a four-backtick fence whose inner ``` lines must not close it.
FENCED_DECISIONS_MD = """# Decision Log

## DEC-11 — Eleven

Only eleven says this.

```markdown
## DEC-10 — an example heading
Only the example says this.
```

````markdown
```
## DEC-10 — a nested example heading
Nested example only.
```
````

Eleven continues after its examples.

## DEC-10 — Ten

The ten clause is here.
"""


def _fenced_docs(root):
    write(os.path.join(root, DOCS_REL), FENCED_DECISIONS_MD)


def case_fenced_heading_is_not_a_section():
    expect_fail("a clause only in a fenced DEC-10 example fails the DEC-10 row",
                plan_text([row(clause="Only the example says this.")]),
                ["decisions_affected[0] DEC-10", "clause"], setup=_fenced_docs)
    expect_fail("a nested-fence DEC-10 example is still fenced",
                plan_text([row(clause="Nested example only.")]),
                ["decisions_affected[0] DEC-10", "clause"], setup=_fenced_docs)
    expect_pass("the real DEC-10 section's clause passes beside fenced impostors",
                plan_text([row(clause="The ten clause is here.")]), setup=_fenced_docs)
    expect_pass("DEC-11's section runs past its fenced examples",
                plan_text([row(dec="DEC-11", clause="Eleven continues after its examples.")]),
                setup=_fenced_docs)


# F3 (validate c2): a ```python line inside an open ``` fence carries an info string, so it is
# content (CommonMark 4.5), not a closer — the DEC-10 heading after it is still fenced.
INFO_STRING_DECISIONS_MD = """# Decision Log

## DEC-11 — Eleven

```text
```python
## DEC-10 — a spoof heading
Spoof clause after an info-string run.
```

## DEC-10 — Ten

The ten clause is here.
"""


def _info_string_docs(root):
    write(os.path.join(root, DOCS_REL), INFO_STRING_DECISIONS_MD)


def case_info_string_run_does_not_close_a_fence():
    expect_fail("a clause after a ```python run inside an open fence fails the DEC-10 row",
                plan_text([row(clause="Spoof clause after an info-string run.")]),
                ["decisions_affected[0] DEC-10", "clause"], setup=_info_string_docs)
    expect_pass("the real DEC-10 clause passes beside the info-string spoof",
                plan_text([row(clause="The ten clause is here.")]), setup=_info_string_docs)


# F3-I (validate c3, operator ruling 2026-11-21): every CommonMark rule that bears on locating a
# decision's section, one CLI case each. Each fixture is a spoof: misreading the rule selects a
# fake `## DEC-10`, or bleeds a neighbour's text into DEC-10's section.
REAL_TEN = "The ten clause is here."
SPOOF = "Spoof clause."


def _docs(text):
    """A run_check setup writing `text` as the segment's DECISIONS.md."""
    return lambda root: write(os.path.join(root, DOCS_REL), text)


def _spoof_and_control(rule, text):
    """The spoof clause fails the DEC-10 row; the genuine DEC-10 clause passes."""
    setup = _docs(text)
    expect_fail(f"{rule}: the spoof clause fails the DEC-10 row", plan_text([row(clause=SPOOF)]),
                ["decisions_affected[0] DEC-10", "clause"], setup=setup)
    expect_pass(f"{rule}: the genuine DEC-10 clause passes", plan_text([row(clause=REAL_TEN)]),
                setup=setup)


def case_overindented_fence_lines_are_content():
    """Rule 1: a fence closer or opener indented 4+ spaces is content."""
    _spoof_and_control("rule 1 closer", "## DEC-11 — Eleven\n\n```text\n    ```\n"
                       "## DEC-10 — example\n" + SPOOF + "\n```\n\n## DEC-10 — Ten\n\n"
                       + REAL_TEN + "\n")
    _spoof_and_control("rule 1 opener", "## DEC-11 — Eleven\n\n    ```\nEleven text.\n```\n"
                       "## DEC-10 — example\n" + SPOOF + "\n```\n\n## DEC-10 — Ten\n\n"
                       + REAL_TEN + "\n")


def case_heading_indentation_limits():
    """Rule 2: an ATX heading takes 0-3 spaces; 4+ is an indented code line, never a heading —
    both when locating DEC-10 and when ending its section."""
    text = ("## DEC-10 — Ten\n\n" + REAL_TEN + "\n\n    ## DEC-10 — indented code\n"
            "Still ten.\n\n   ## DEC-11 — Eleven\n\nOnly eleven says this.\n")
    setup = _docs(text)
    expect_fail("rule 2: a 3-space DEC-11 heading ends DEC-10's section",
                plan_text([row(clause="Only eleven says this.")]),
                ["decisions_affected[0] DEC-10", "clause"], setup=setup)
    expect_pass("rule 2: a 3-space heading is DEC-11's own heading",
                plan_text([row(dec="DEC-11", clause="Only eleven says this.")]), setup=setup)
    expect_pass("rule 2: a 4-space `## DEC-10` neither starts nor ends a section",
                plan_text([row(clause="Still ten.")]), setup=setup)
    _spoof_and_control("rule 2 spoof", "## DEC-11 — Eleven\n\n    ## DEC-10 — indented code\n"
                       + SPOOF + "\n\n## DEC-10 — Ten\n\n" + REAL_TEN + "\n")


def case_backtick_info_string_cannot_open():
    """Rule 3: a backtick run whose info string holds a backtick is not a fence opener."""
    _spoof_and_control("rule 3", "## DEC-11 — Eleven\n\n```inline `code` span\n```\n"
                       "## DEC-10 — a spoof heading\n" + SPOOF + "\n```\n\n## DEC-10 — Ten\n\n"
                       + REAL_TEN + "\n")


def case_unclosed_fence_runs_to_end():
    """Rule 5: an unclosed fence runs to the end of the file; no heading after it is real."""
    _spoof_and_control("rule 5", "## DEC-10 — Ten\n\n" + REAL_TEN + "\n\n## DEC-11 — Eleven\n\n"
                       "```text\n## DEC-10 — a spoof heading\n" + SPOOF + "\n")


def case_successors():
    expect_fail("an amend to a D id this plan lacks fails",
                plan_text([row(disposition="amend", successor="D-09")]),
                ["decisions_affected[0] DEC-10", "D-09"])
    expect_fail("a strike to an unindexed DEC fails",
                plan_text([row(disposition="strike", successor="DEC-98")]),
                ["decisions_affected[0] DEC-10", "DEC-98"])


def case_ownership():
    lone = [task("T-01", ["src/a.py"])]
    expect_fail("an amend with no task owning DECISIONS.md fails",
                plan_text([row(disposition="amend", successor="D-01")], tasks=lone),
                ["decisions_affected[0] DEC-10", "DECISIONS.md"])
    expect_pass("a keep needs no owning task", plan_text([row()], tasks=lone))
    by_symbol = lone + [task("T-02", [f"{DOCS_REL}#DEC-10"])]
    expect_pass("a symbol anchor on DECISIONS.md owns it",
                plan_text([row(disposition="amend", successor="D-01")], tasks=by_symbol))
    by_quote = lone + [task("T-02", [{"path": "./" + DOCS_REL, "quote": "Only eleven says this."}])]
    expect_pass("a content anchor (normalised path) on DECISIONS.md owns it",
                plan_text([row(disposition="strike", successor="D-01")], tasks=by_quote))


def case_each_failure_keeps_other_checks():
    text = plan_text([row(dec="DEC-99", clause="x")], tasks=[task("T-01", ["src/missing.py#nope"]),
                                                             OWNER])
    expect_fail("disposition failures sit beside unrelated anchor failures", text,
                ["decisions_affected[0] DEC-99", "T-01 files"])


def _served_docs(root):
    write(os.path.join(root, ".harness", "kaya", "docs", "DECISIONS.md"), SERVED_DECISIONS_MD)
    write(os.path.join(root, ".harness", "kaya", "docs", "DECISIONS-INDEX.md"), SERVED_INDEX)


def case_served_segment_authority():
    served = [task("T-01", ["src/a.py"])]
    expect_pass("a served plan checks against its own segment's decisions",
                plan_text([row(dec="DEC-50", clause="Fifty is served.")], tasks=served),
                segment="kaya", setup=_served_docs)
    expect_fail("a served plan never borrows the harness decision corpus",
                plan_text([row()], tasks=served), ["decisions_affected[0] DEC-10"],
                segment="kaya", setup=_served_docs)


# --- check: the era -----------------------------------------------------------------------


def case_era():
    expect_pass("a draft stamped before activation is not newly refused",
                plan_text(drafted=BEFORE_ERA))
    expect_fail("a draft stamped exactly at activation is eligible", plan_text(drafted=ERA),
                ["decisions_affected"])
    expect_fail("a draft stamped after activation is eligible", plan_text(drafted=AFTER_ERA),
                ["decisions_affected"])
    expect_fail("an offset instant compares as an instant",
                plan_text(drafted="2026-11-21T13:00:00+01:00"), ["decisions_affected"])
    expect_pass("an offset instant before activation is pre-era",
                plan_text(drafted="2026-11-21T12:59:59+01:00"))
    expect_fail("a null era requires the block on every stamped draft",
                plan_text(drafted=BEFORE_ERA), ["decisions_affected"], era=None)
    expect_pass("a missing era key preserves legacy behaviour", plan_text(), era=_UNSET)
    expect_pass("an undated legacy pending draft is not refused", plan_text(drafted=_UNSET),
                era=None)


def case_malformed_instants():
    expect_fail("a malformed era is a diagnostic, never an exemption", plan_text(),
                ["decision_dispositions_era_start"], era="yesterday")
    expect_fail("a date-only era is not an instant", plan_text(), ["decision_dispositions_era_start"],
                era="2026-11-21")
    expect_fail("a malformed drafted_at is a diagnostic", plan_text(drafted="soon"),
                ["drafted_at"])
    expect_fail("a naive drafted_at is a diagnostic", plan_text(drafted="2026-11-21T12:00:00"),
                ["drafted_at"])


def case_history_skipped():
    expect_pass("an approved in-era plan is history, not a draft",
                plan_text(status="approved"))
    expect_pass("a landed plan is history",
                plan_text(status="approved", extra={"status": "done"}))
    expect_pass("an approved plan may drop a quoted clause after signature",
                plan_text([row(clause="No longer in the log.")], status="approved"))


# --- the writer: creation stamp and reservation ---------------------------------------------


def _writer_root():
    root = tempfile.mkdtemp(prefix="plan-dispositions-writer-")
    feat = os.path.join(root, ".harness", "harness", "features", "FEAT-99-fixture")
    os.makedirs(feat)
    return root, os.path.join(feat, "plan.yaml")


def _proposal(root, text):
    path = os.path.join(root, "proposal.yaml")
    write(path, text)
    return path


def _bare_plan(drafted=_UNSET, title="t"):
    """A proposal/plan body without approval (the writer seeds it)."""
    doc = {"schema": "plan/1", "feature": "FEAT-99-fixture"}
    if drafted is not _UNSET:
        doc["drafted_at"] = drafted
    doc["tasks"] = [dict(task("T-01", ["src/a.py"]), title=title)]
    return yaml.safe_dump(doc, sort_keys=False)


def case_creation_stamp():
    root, plan = _writer_root()
    try:
        lo = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
        r = run("apply", "--file", plan, "--proposal", _proposal(root, _bare_plan()))
        hi = datetime.datetime.now(datetime.timezone.utc)
        check("apply creates the plan", r.returncode == 0, r.stdout + r.stderr)
        stamp = (yaml.safe_load(open(plan, encoding="utf-8")) or {}).get("drafted_at") \
            if os.path.exists(plan) else None
        ok = isinstance(stamp, str) and re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", stamp)
        check("creation stamps a timezone-qualified UTC drafted_at", ok, stamp)
        if ok:
            when = datetime.datetime.fromisoformat(stamp)
            check("the stamp is the writer's creation instant", lo <= when <= hi, (lo, stamp, hi))
    finally:
        shutil.rmtree(root, ignore_errors=True)


def case_creation_refuses_backdating():
    root, plan = _writer_root()
    try:
        r = run("apply", "--file", plan,
                "--proposal", _proposal(root, _bare_plan(drafted="2020-01-01T00:00:00Z")))
        check("creation refuses a caller-supplied drafted_at", r.returncode != 0
              and "drafted_at" in r.stdout + r.stderr, r.stdout + r.stderr)
        check("the refused creation writes no file", not os.path.exists(plan))
    finally:
        shutil.rmtree(root, ignore_errors=True)


def case_creation_validates_dispositions():
    """F1 (validate c1): a malformed decisions_affected row is refused at creation, unwritten."""
    root, plan = _writer_root()
    try:
        bad = _bare_plan() + "decisions_affected:\n- dec: DEC-10\n"
        r = run("apply", "--file", plan, "--proposal", _proposal(root, bad))
        check("creation refuses a malformed decisions_affected row",
              r.returncode != 0 and "decisions_affected" in r.stdout + r.stderr,
              r.stdout + r.stderr)
        check("the refused malformed creation writes no file", not os.path.exists(plan))
        good = _bare_plan() + yaml.safe_dump({"decisions_affected": [row()]}, sort_keys=False)
        r = run("apply", "--file", plan, "--proposal", _proposal(root, good))
        check("creation with a valid row still creates", r.returncode == 0 and os.path.exists(plan),
              r.stdout + r.stderr)
    finally:
        shutil.rmtree(root, ignore_errors=True)


STAMPED = ("schema: plan/1\nfeature: FEAT-99-fixture\napproval:\n  status: pending\n"
           "drafted_at: '2026-11-21T12:30:00Z'\n# a comment the writer must keep\n"
           + _bare_plan().split("feature: FEAT-99-fixture\n", 1)[1])
UNDATED = ("schema: plan/1\nfeature: FEAT-99-fixture\napproval:\n  status: pending\n"
           "# a comment the writer must keep\n"
           + _bare_plan().split("feature: FEAT-99-fixture\n", 1)[1])


def _refusal(name, base, argv_for, cli=CLI):
    root, plan = _writer_root()
    try:
        write(plan, base)
        before = read_bytes(plan)
        r = run(*argv_for(root, plan), cli=cli)
        check(f"{name}: refused nonzero", r.returncode != 0 and "drafted_at" in r.stdout + r.stderr,
              r.stdout + r.stderr)
        check(f"{name}: plan bytes identical", read_bytes(plan) == before)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def _set_key(value):
    def argv(root, plan):
        path = os.path.join(root, "value.yaml")
        write(path, yaml.safe_dump(value))
        return ["set-key", "--file", plan, "--key", "drafted_at", "--value-file", path]
    return argv


def _apply(drafted):
    def argv(root, plan):
        return ["apply", "--file", plan, "--proposal", _proposal(root, _bare_plan(drafted=drafted))]
    return argv


ATTEMPTS = (("backdate", "2020-01-01T00:00:00Z"), ("forward-date", "2030-01-01T00:00:00Z"),
            ("null", None))


def case_set_key_reservation():
    for label, base in (("stamped", STAMPED), ("undated", UNDATED)):
        for attempt, value in ATTEMPTS:
            _refusal(f"set-key {attempt} on {label} plan", base, _set_key(value))


def case_apply_reservation(cli=CLI, path_label="byte-preserving"):
    for label, base in (("stamped", STAMPED), ("undated", UNDATED)):
        for attempt, value in ATTEMPTS:
            _refusal(f"apply {attempt} on {label} plan ({path_label})", base, _apply(value), cli)


def case_alternate_rendering_path():
    """The safe_dump rendering (PRESERVE_BASE_BYTES off, a copy of the tree) is guarded too."""
    tmp = tempfile.mkdtemp(prefix="plan-dispositions-bin-")
    try:
        # The copy sits at the harness layout under its own manifest, so the copied bin
        # resolves its root from itself, never from the live checkout or the environment.
        write(os.path.join(tmp, ".harness", "team-config.yaml"), "schema_version: 1\nteams: []\n")
        copy = os.path.join(tmp, ".claude", "skills", "harness", "bin")
        shutil.copytree(BIN_DIR, copy, ignore=shutil.ignore_patterns("__pycache__"))
        union = os.path.join(copy, "plan_merge", "union.py")
        source = open(union, encoding="utf-8").read()
        check("the copy carries the rendering switch", "PRESERVE_BASE_BYTES = True" in source)
        write(union, source.replace("PRESERVE_BASE_BYTES = True", "PRESERVE_BASE_BYTES = False"))
        case_apply_reservation(os.path.join(copy, "plan-merge.py"), "safe_dump rendering")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _edit_control(name, base, want_stamp):
    root, plan = _writer_root()
    try:
        write(plan, base)
        r = run("apply", "--file", plan, "--proposal", _proposal(root, _bare_plan(title="t2")))
        check(f"{name}: ordinary apply edit succeeds", r.returncode == 0, r.stdout + r.stderr)
        value = os.path.join(root, "value.yaml")
        write(value, "[]\n")
        r = run("set-key", "--file", plan, "--key", "decisions_affected", "--value-file", value)
        check(f"{name}: ordinary set-key edit succeeds", r.returncode == 0, r.stdout + r.stderr)
        doc = yaml.safe_load(open(plan, encoding="utf-8"))
        check(f"{name}: stamp unchanged or still absent", doc.get("drafted_at", _UNSET) == want_stamp,
              doc.get("drafted_at"))
        text = open(plan, encoding="utf-8").read()
        check(f"{name}: bytes outside the edit preserved",
              "# a comment the writer must keep\n" in text and "title: t2" in text, text)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def case_ordinary_edits():
    _edit_control("stamped plan", STAMPED, "2026-11-21T12:30:00Z")
    _edit_control("undated legacy plan (no backfill)", UNDATED, _UNSET)
    root, plan = _writer_root()
    try:
        write(plan, STAMPED)
        before = read_bytes(plan)
        r = run("apply", "--file", plan,
                "--proposal", _proposal(root, _bare_plan(drafted="2026-11-21T12:30:00Z")))
        check("apply carrying the unchanged stamp is accepted", r.returncode == 0, r.stdout + r.stderr)
        check("an unchanged stamp is preserved, not replaced", read_bytes(plan) == before)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def main():
    for case in (case_valid_controls, case_missing_block, case_unindexed_dec, case_struck,
                 case_clause_location, case_fenced_heading_is_not_a_section,
                 case_info_string_run_does_not_close_a_fence,
                 case_overindented_fence_lines_are_content, case_heading_indentation_limits,
                 case_backtick_info_string_cannot_open, case_unclosed_fence_runs_to_end,
                 case_successors,
                 case_ownership, case_each_failure_keeps_other_checks,
                 case_served_segment_authority, case_era, case_malformed_instants,
                 case_history_skipped, case_creation_stamp, case_creation_refuses_backdating,
                 case_creation_validates_dispositions, case_set_key_reservation,
                 case_apply_reservation, case_alternate_rendering_path, case_ordinary_edits):
        case()
    failed = [name for name, ok in RESULTS if not ok]
    print(f"{len(RESULTS) - len(failed)}/{len(RESULTS)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
