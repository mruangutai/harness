#!/usr/bin/env python3
"""Unit floor for `gh-sync.py abandon --close-sources` (BUG-2161 T-01).

Drives the REAL planner (`_abandon_plan`), executor (`_apply_abandon_plan`) and `cmd_abandon`
in-process. Every external write is intercepted at the module's own seams — `gh_try`, `_place`,
`ensure_labels`, `_record_station`, `_prune_abandoned_runs` — and appended to ONE ordered event
list, so a case asserts what was written, in what order, with which arguments. No corpus lookup
is modelled: confirmation, not discovery, is the guard (BUG-2161 D-01).

python3 stdlib only. importlib loading and reporting follow tests/unit/test-gh-sync-build-entry.py.
End-to-end subprocess coverage with the fake gh lives in tests/integration/test-gh-sync-abandon.py.

    ./test-gh-sync-abandon-sources.py    -> exit 0 all pass, 1 otherwise
"""
import contextlib
import importlib.util
import io
import json
import os
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / ".claude" / "skills" / "harness" / "bin"
sys.path.insert(0, str(BIN))

_spec = importlib.util.spec_from_file_location("_ghs_abandon_sources", str(BIN / "gh-sync.py"))
gh_sync = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gh_sync)

failures = []
REPO = "implentio/fake"
BOARD = {"intercepted": "every card write goes through the patched _place"}


def check(name, ok, detail=""):
    print("PASS" if ok else "FAIL", name, detail if not ok else "")
    if not ok:
        failures.append(name)


def feat_dir(tmp, name):
    d = os.path.join(tmp, ".harness", "harness", "features", name)
    os.makedirs(d, exist_ok=True)
    return d


def write_plan(d, name, station="building", sources=()):
    with open(os.path.join(d, "plan.yaml"), "w", encoding="utf-8") as f:
        f.write(f"schema: plan/1\nfeature: {name}\nstatus: {station}\n"
                f"source_issues: [{', '.join(str(n) for n in sources)}]\n"
                "station_only: true\ntasks: []\n")


def write_feature(d, name, github):
    doc = {"feature_id": name, "branch": "none", "pr": None, "review_sha": "none",
           "cycles_used": 0, "max_total_cycles": 1, "runs": [], "github": github}
    with open(os.path.join(d, "feature.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2)


def opened_github(mirror=()):
    return {"milestone": 7, "parent": 40, "attached": ["T-01"], "issues": {"T-01": 41},
            "source_issues": list(mirror)}


def unopened_github(mirror=()):
    return {"milestone": None, "parent": None, "attached": [], "issues": {},
            "source_issues": list(mirror)}


def reason_file(tmp):
    p = os.path.join(tmp, "reason.txt")
    open(p, "w", encoding="utf-8").write("the operator's signed reason")
    return p


class Seams:
    """Replace the module's external seams with recorders; restore on exit.

    `fail` is a list of substrings: a `gh_try` call whose joined argv contains one returns
    (False, 'boom'), so a write failure is observable without a subprocess."""

    NAMES = ("gh_try", "_place", "ensure_labels", "_record_station", "_prune_abandoned_runs")

    def __init__(self, fail=(), station_ok=True):
        self.events = []
        self.fail = list(fail)
        self.station_ok = station_ok

    def __enter__(self):
        self._saved = {n: getattr(gh_sync, n) for n in self.NAMES}

        def gh_try(args):
            self.events.append(("gh", list(args)))
            if any(s in " ".join(args) for s in self.fail):
                return (False, "boom")
            return (True, "")

        gh_sync.gh_try = gh_try
        gh_sync._place = lambda board, repo, num, station, **kw: (
            self.events.append(("place", num, station)) or True)
        gh_sync.ensure_labels = lambda repo, labels: self.events.append(("labels", sorted(labels)))
        gh_sync._record_station = lambda d, station: (
            self.events.append(("station", station)) or self.station_ok)
        gh_sync._prune_abandoned_runs = lambda d, dry_run=False: self.events.append(
            ("prune", dry_run))
        return self

    def __exit__(self, *exc):
        for n, fn in self._saved.items():
            setattr(gh_sync, n, fn)
        return False

    # --- views over the ordered event list -------------------------------------------------
    def gh(self):
        return [e[1] for e in self.events if e[0] == "gh"]

    def targets(self, verb):
        """Issue numbers a `gh issue <verb>` / close PATCH was made against."""
        out = []
        for args in self.gh():
            if verb == "close" and args[:3] == ["api", "-X", "PATCH"] and "state=closed" in args \
                    and "/issues/" in args[3]:
                out.append(int(args[3].rsplit("/", 1)[1]))
            elif verb in ("comment", "edit") and args[:2] == ["issue", verb]:
                out.append(int(args[2]))
        return out

    def index(self, pred):
        return next((i for i, e in enumerate(self.events) if pred(e)), None)

    def writes(self):
        return [e for e in self.events if e[0] in ("place", "station")] + [
            ("gh", a) for a in self.gh()]


def call_abandon(d, reason, **kw):
    """cmd_abandon with stdout/stderr captured. Returns (out, err, exit_code, TypeError-or-None).

    TypeError is reported separately so an UNSUPPORTED OPTION (the pre-change shape of a
    `close_sources=` call) is never confused with missing source/unopened behaviour."""
    out, err = io.StringIO(), io.StringIO()
    code, type_error = None, None
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            gh_sync.cmd_abandon(d, REPO, BOARD, reason, **kw)
        except SystemExit as e:
            code = e.code
        except TypeError as e:
            type_error = e
    return out.getvalue(), err.getvalue(), code, type_error


def opt_note(type_error):
    return f"UNSUPPORTED-OPTION: {type_error}" if type_error else ""


# --- planner ------------------------------------------------------------------------------------
REC = {"milestone": 7, "parent": 40, "attached": ["T-01"], "issues": {"T-01": 41},
       "source_issues": [], "build_entry": None}

base_plan = gh_sync._abandon_plan(REC)
try:
    with_sources = gh_sync._abandon_plan(REC, [51, 52])
    planner_err = None
except TypeError as e:
    with_sources, planner_err = [], e
src_lines = [line for kind, num, line in with_sources if num in (51, 52)]
check("AS-01 planner: opted-in sources join the SAME plan list, a comment and a close line each; "
      "the default plan has no source entry",
      len(src_lines) == 4 and not any(n in (51, 52) for _k, n, _l in base_plan)
      and [e for e in with_sources if e[1] not in (51, 52)] == base_plan,
      opt_note(planner_err) or repr(with_sources))
check("AS-02 planner: each source close line names not_planned, abandoned and the backlog",
      [n for kind, n, _l in with_sources if kind == "source"] == [51, 52]
      and all(all(w in line for w in ("not_planned", "abandoned", "backlog"))
              for kind, num, line in with_sources if kind == "source"),
      opt_note(planner_err) or repr(with_sources))

# A source that IS a task issue still gets the reason once but closes once; one that IS the
# parent is already commented and closed as the parent.
try:
    overlap = gh_sync._abandon_plan(REC, [40, 41, 51])
except TypeError as e:
    overlap = []
check("AS-03 planner: a source that is a task issue gets its own reason comment and is closed "
      "once; a source that is the parent is not planned twice",
      [(k, n) for k, n, _l in overlap if k in ("source", "source_comment")]
      == [("source_comment", 41), ("source_comment", 51), ("source", 51)]
      and sum(1 for k, n, _l in overlap if n == 41 and k == "issue") == 1
      and sum(1 for _k, n, _l in overlap if n == 40) == 2,
      repr(overlap))

# --- executor: the same list the dry run printed is the list applied -----------------------------
with tempfile.TemporaryDirectory() as tmp:
    reason = reason_file(tmp)
    with Seams() as s:
        try:
            plan = gh_sync._abandon_plan(REC, [51, 52])
            gh_sync._apply_abandon_plan(plan, REC, REPO, reason, lambda n, w: s.events.append(
                ("close", n, w)))
            exec_err = None
        except TypeError as e:
            exec_err = e
    comments = [a for a in s.gh() if a[:2] == ["issue", "comment"]]
    check("AS-04 executor: every comment, parent and both sources, passes the unchanged original "
          "reason-file argument",
          [int(a[2]) for a in comments] == [40, 51, 52]
          and all(a[-2:] == ["--body-file", reason] for a in comments),
          opt_note(exec_err) or repr(comments))
    check("AS-05 executor: sources close with the target label 'source', in plan order",
          [e for e in s.events if e[0] == "close"]
          == [("close", 41, "issue"), ("close", 40, "parent"), ("close", 51, "source"),
              ("close", 52, "source")],
          opt_note(exec_err) or repr(s.events))

# --- cmd_abandon: dry run -------------------------------------------------------------------------
with tempfile.TemporaryDirectory() as tmp:
    d = feat_dir(tmp, "FEAT-9201-dry")
    write_plan(d, "FEAT-9201-dry", sources=[51, 52])
    write_feature(d, "FEAT-9201-dry", opened_github())
    reason = reason_file(tmp)
    with Seams() as s:
        out, err, code, te = call_abandon(d, reason, yes=False, close_sources=True)
    check("AS-06 dry run with --close-sources lists both sources and writes nothing",
          te is None and "source #51" in out and "source #52" in out
          and "would ensure the abandoned label exists" in out
          and s.writes() == [] and ("station", "abandoned") not in s.events,
          opt_note(te) or out + repr(s.events))

# --- cmd_abandon: the flag decides, and a positive pairs every absence ----------------------------
for label, kw, expect_sources in (
        ("--yes without --close-sources", {"yes": True}, False),
        ("--yes with --close-sources", {"yes": True, "close_sources": True}, True)):
    with tempfile.TemporaryDirectory() as tmp:
        d = feat_dir(tmp, "FEAT-9202-flags")
        write_plan(d, "FEAT-9202-flags", sources=[51, 52])
        write_feature(d, "FEAT-9202-flags", opened_github())
        reason = reason_file(tmp)
        with Seams() as s:
            out, err, code, te = call_abandon(d, reason, **kw)
        closed = s.targets("close")
        if expect_sources:
            check(f"AS-07 {label}: both sources closed, commented and labelled with the original "
                  "reason-file argument",
                  te is None and {51, 52} <= set(closed)
                  and s.targets("comment").count(51) == 1 and s.targets("edit").count(52) == 1
                  and [a for a in s.gh() if a[:3] == ["issue", "comment", "51"]][0][-2:]
                  == ["--body-file", reason], opt_note(te) or repr(s.gh()))
            check("AS-08 close-sources: each source's backlog write follows its own close",
                  all(s.index(lambda e, n=n: e == ("place", n, "backlog")) is not None
                      and s.index(lambda e, n=n: e[0] == "gh" and f"issues/{n}" in " ".join(e[1])
                                  and "state=closed" in e[1])
                      < s.index(lambda e, n=n: e == ("place", n, "backlog")) for n in (51, 52)),
                  repr(s.events))
        else:
            check(f"AS-09 {label}: ZERO source comment, close, label or board write, while the "
                  "parent and task ARE disposed",
                  te is None and {40, 41} <= set(closed) and not ({51, 52} & set(closed))
                  and not ({51, 52} & set(s.targets("comment")))
                  and not ({51, 52} & set(s.targets("edit")))
                  and not any(e[0] == "place" and e[1] in (51, 52) for e in s.events),
                  opt_note(te) or repr(s.events))

# --- GC-01: a plan.yaml source that is ALSO the task issue or the parent gets ZERO writes without
# --- --close-sources, whatever else it is recorded as; the rest of the feature is still disposed --
def touches(s, n):
    """True when ANY intercepted write names issue #n: a gh call, or a board placement."""
    pat = re.compile(r"\bissues/%d\b" % n)
    for e in s.events:
        if e[0] == "place" and e[1] == n:
            return True
        if e[0] == "gh" and ((e[1][:2] in (["issue", "comment"], ["issue", "edit"])
                              and e[1][2] == str(n)) or any(pat.search(a) for a in e[1])):
            return True
    return False


for alias_label, alias, other in (("source/task alias", 41, 40), ("source/parent alias", 40, 41)):
    for run_label, kw in (("--yes", {"yes": True}), ("dry run", {"yes": False})):
        with tempfile.TemporaryDirectory() as tmp:
            d = feat_dir(tmp, "FEAT-9220-alias")
            write_plan(d, "FEAT-9220-alias", sources=[alias, 52])
            write_feature(d, "FEAT-9220-alias", opened_github())
            reason = reason_file(tmp)
            with Seams() as s:
                out, err, code, te = call_abandon(d, reason, **kw)
        gap = [l for l in out.splitlines() if f"#{alias}" in l and "--close-sources" in l
               and not l.startswith("gh-sync: would ")]
        check(f"GC-01 {alias_label}, {run_label}, no --close-sources: ZERO writes name #{alias}, "
              "and the skip is reported as a gap naming the flag",
              te is None and not touches(s, alias) and not touches(s, 52) and len(gap) == 1,
              opt_note(te) or out + repr(s.events))
        if kw["yes"]:
            check(f"GC-01 {alias_label}, --yes: the non-aliased entry #{other} IS still disposed "
                  "and the station is recorded",
                  other in s.targets("close") and ("station", "abandoned") in s.events,
                  repr(s.events))

    with tempfile.TemporaryDirectory() as tmp:
        d = feat_dir(tmp, "FEAT-9221-alias-pos")
        write_plan(d, "FEAT-9221-alias-pos", sources=[alias, 52])
        write_feature(d, "FEAT-9221-alias-pos", opened_github())
        reason = reason_file(tmp)
        with Seams() as s:
            out, err, code, te = call_abandon(d, reason, yes=True, close_sources=True)
    check(f"GC-01 {alias_label}, --close-sources --yes: #{alias} is commented once, closed once "
          "and reseated once, and no gap is reported",
          te is None and s.targets("comment").count(alias) == 1
          and s.targets("close").count(alias) == 1
          and s.events.count(("place", alias, "backlog")) == 1
          and not any(f"#{alias}" in l and "--close-sources" in l for l in out.splitlines()),
          opt_note(te) or repr(s.events))

# --- F1: a refused station write must not prune runs/ ------------------------------------------------
for label, station_ok, plan_station, prunes in (
        ("station write refused", False, "building", False),
        ("station write recorded", True, "building", True),
        ("station already abandoned", False, "abandoned", True)):
    with tempfile.TemporaryDirectory() as tmp:
        d = feat_dir(tmp, "FEAT-9222-prune")
        write_plan(d, "FEAT-9222-prune", station=plan_station)
        write_feature(d, "FEAT-9222-prune", unopened_github())
        reason = reason_file(tmp)
        with Seams(station_ok=station_ok) as s:
            out, err, code, te = call_abandon(d, reason, yes=True)
    check(f"F1 {label}: runs/ pruned = {prunes}" + ("" if prunes else
          ", and the gap is reported"),
          te is None and (("prune", False) in s.events) == prunes
          and (prunes or ("runs/" in out and "not pruned" in out)),
          opt_note(te) or out + repr(s.events))

# --- a second ACTIVE feature citing the same source does not change the target set ----------------
with tempfile.TemporaryDirectory() as tmp:
    d = feat_dir(tmp, "FEAT-9203-mine")
    write_plan(d, "FEAT-9203-mine", sources=[51, 52])
    write_feature(d, "FEAT-9203-mine", opened_github(mirror=[51, 52]))
    other = feat_dir(tmp, "FEAT-9204-other-active")
    write_plan(other, "FEAT-9204-other-active", sources=[52, 77])
    write_feature(other, "FEAT-9204-other-active", opened_github(mirror=[52, 77]))
    mine_plan = open(os.path.join(d, "plan.yaml"), "rb").read()
    mine_json = open(os.path.join(d, "feature.json"), "rb").read()
    other_before = (open(os.path.join(other, "plan.yaml"), "rb").read(),
                    open(os.path.join(other, "feature.json"), "rb").read())
    reason = reason_file(tmp)
    with Seams() as s:
        out, err, code, te = call_abandon(d, reason, yes=True, close_sources=True)
    sources_closed = {n for n in s.targets("close") if n not in (40, 41)}
    check("AS-10 a source cited by another active feature is still disposed, and only THIS "
          "plan's sources are targeted — never the other feature's #77",
          te is None and sources_closed == {51, 52} and 77 not in s.targets("comment")
          and not any(e[0] == "place" and e[1] == 77 for e in s.events),
          opt_note(te) or repr(sorted(sources_closed)))
    check("AS-11 neither feature's plan.yaml source list nor feature.json mirror is mutated",
          open(os.path.join(d, "plan.yaml"), "rb").read() == mine_plan
          and open(os.path.join(d, "feature.json"), "rb").read() == mine_json
          and (open(os.path.join(other, "plan.yaml"), "rb").read(),
               open(os.path.join(other, "feature.json"), "rb").read()) == other_before,
          "bytes differ")

# --- plan.yaml is authoritative over a stale mirror ----------------------------------------------
with tempfile.TemporaryDirectory() as tmp:
    d = feat_dir(tmp, "FEAT-9205-stale")
    write_plan(d, "FEAT-9205-stale", sources=[51])
    write_feature(d, "FEAT-9205-stale", opened_github(mirror=[99]))
    reason = reason_file(tmp)
    with Seams() as s:
        out, err, code, te = call_abandon(d, reason, yes=True, close_sources=True)
    check("AS-12 plan.yaml's source list wins over a stale feature.json mirror",
          te is None and 51 in s.targets("close") and 99 not in s.targets("close")
          and 99 not in s.targets("comment"), opt_note(te) or repr(s.gh()))

# --- unopened record ------------------------------------------------------------------------------
with tempfile.TemporaryDirectory() as tmp:
    d = feat_dir(tmp, "FEAT-9206-unopened")
    write_plan(d, "FEAT-9206-unopened", sources=[])
    write_feature(d, "FEAT-9206-unopened", unopened_github())
    reason = reason_file(tmp)
    with Seams() as s:
        out, err, code, te = call_abandon(d, reason, yes=True)
    check("AS-13 unopened, no sources, --yes: no SKIP; records abandoned THEN prunes, with no "
          "remote write and no label creation",
          te is None and code is None and "SKIP" not in out
          and s.events == [("station", "abandoned"), ("prune", False)],
          opt_note(te) or f"code={code} out={out!r} events={s.events}")

with tempfile.TemporaryDirectory() as tmp:
    d = feat_dir(tmp, "FEAT-9207-unopened-src")
    write_plan(d, "FEAT-9207-unopened-src", sources=[51, 52])
    write_feature(d, "FEAT-9207-unopened-src", unopened_github())
    reason = reason_file(tmp)
    with Seams() as s:
        out, err, code, te = call_abandon(d, reason, yes=True, close_sources=True)
    check("AS-14 unopened with plan-only sources: both disposed, then station, then prune",
          te is None and {51, 52} <= set(s.targets("close"))
          and s.index(lambda e: e == ("station", "abandoned")) is not None
          and s.index(lambda e: e == ("station", "abandoned"))
          < s.index(lambda e: e == ("prune", False))
          and s.index(lambda e: e[0] == "gh" and "issues/52" in " ".join(e[1])
                      and "state=closed" in e[1]) < s.index(lambda e: e[0] == "station"),
          opt_note(te) or repr(s.events))

# --- already abandoned ------------------------------------------------------------------------------
with tempfile.TemporaryDirectory() as tmp:
    d = feat_dir(tmp, "FEAT-9208-reentry")
    write_plan(d, "FEAT-9208-reentry", station="abandoned", sources=[51])
    write_feature(d, "FEAT-9208-reentry", unopened_github())
    reason = reason_file(tmp)
    with Seams() as s:
        out, err, code, te = call_abandon(d, reason, yes=True, close_sources=True)
    check("AS-15 re-entry at abandoned: the station is NOT rewritten, the source IS disposed, "
          "and runs/ is still pruned",
          te is None and ("station", "abandoned") not in s.events
          and 51 in s.targets("close") and ("prune", False) in s.events,
          opt_note(te) or repr(s.events))

# --- failure continuation -------------------------------------------------------------------------
with tempfile.TemporaryDirectory() as tmp:
    d = feat_dir(tmp, "FEAT-9209-fail")
    write_plan(d, "FEAT-9209-fail", sources=[51, 52])
    write_feature(d, "FEAT-9209-fail", unopened_github())
    reason = reason_file(tmp)
    with Seams(fail=["issues/51 "]) as s:
        out, err, code, te = call_abandon(d, reason, yes=True, close_sources=True)
    check("AS-16 a failed source close is reported and never stops the next source or the "
          "station and prune",
          te is None and "could not close source #51" in err and "#51 did not close" in out
          and 52 in s.targets("close") and ("place", 52, "backlog") in s.events
          and ("place", 51, "backlog") not in s.events
          and s.events[-2:] == [("station", "abandoned"), ("prune", False)],
          opt_note(te) or f"err={err!r} out={out!r}")

with tempfile.TemporaryDirectory() as tmp:
    d = feat_dir(tmp, "FEAT-9210-fail2")
    write_plan(d, "FEAT-9210-fail2", sources=[51, 52])
    write_feature(d, "FEAT-9210-fail2", unopened_github())
    reason = reason_file(tmp)
    with Seams(fail=["issue comment 51", "issue edit 51 "]) as s:
        out, err, code, te = call_abandon(d, reason, yes=True, close_sources=True)
    check("AS-17 a failed source comment and label are each named, and the card is still "
          "reseated and the later source disposed",
          te is None and "reason not posted on source #51" in err
          and "#51 closed but not labelled" in err and ("place", 51, "backlog") in s.events
          and 52 in s.targets("edit") and ("station", "abandoned") in s.events,
          opt_note(te) or f"err={err!r}")

# --- reporter honesty: sources received the reason although no parent is recorded -------------------
with tempfile.TemporaryDirectory() as tmp:
    d = feat_dir(tmp, "FEAT-9211-report")
    write_plan(d, "FEAT-9211-report", sources=[51])
    write_feature(d, "FEAT-9211-report", unopened_github())
    reason = reason_file(tmp)
    with Seams() as s:
        out, err, code, te = call_abandon(d, reason, yes=True, close_sources=True)
    check("AS-18 the reporters say 'reason posted on source #51' and never claim the reason went "
          "unposted when a source received it",
          te is None and "reason posted on source #51" in out
          and "reason not posted" not in out, opt_note(te) or out)

with tempfile.TemporaryDirectory() as tmp:
    d = feat_dir(tmp, "FEAT-9212-report-none")
    write_plan(d, "FEAT-9212-report-none", sources=[])
    write_feature(d, "FEAT-9212-report-none", unopened_github())
    reason = reason_file(tmp)
    with Seams() as s:
        out, err, code, te = call_abandon(d, reason, yes=True)
    check("AS-19 with no comment target at all, the gap line still says the reason was not posted",
          te is None and "no parent recorded — reason not posted" in out, opt_note(te) or out)

# --- direct callers keep the old signature -----------------------------------------------------------
with tempfile.TemporaryDirectory() as tmp:
    d = feat_dir(tmp, "FEAT-9213-legacy")
    write_plan(d, "FEAT-9213-legacy", sources=[51])
    write_feature(d, "FEAT-9213-legacy", opened_github())
    reason = reason_file(tmp)
    with Seams() as s:
        out, err, code, te = call_abandon(d, reason, yes=True)
    check("AS-20 an existing direct caller (no close_sources argument) still disposes parent and "
          "task and touches no source",
          te is None and {40, 41} <= set(s.targets("close")) and 51 not in s.targets("close"),
          repr(s.events))

print(f"\n{len(failures)} FAILED" if failures else "\nALL PASSED")
sys.exit(1 if failures else 0)
