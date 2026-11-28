#!/usr/bin/env python3
"""Unit floor for `gh-sync.py abandon --close-sources` (BUG-2161 T-01).

Drives the REAL planner (`_abandon_plan`), executor (`_apply_abandon_plan`) and `cmd_abandon`
in-process. Every external write is intercepted at the module's own seams — `gh_try`, `_place`,
`ensure_labels`, `_record_station`, `_prune_abandoned_runs` — and appended to ONE ordered event
list, so a case asserts what was written, in what order, with which arguments. No corpus lookup
is modelled: confirmation, not discovery, is the guard (BUG-2161 D-01).

python3 stdlib only. gh-sync.py loads through unit_support.load_script.
End-to-end subprocess coverage with the fake gh lives in tests/integration/test-gh-sync-abandon.py.

    ./test-gh-sync-abandon-sources.py    -> exit 0 all pass, 1 otherwise
"""
from unit_support import load_script

import contextlib
import io
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from unittest import mock

from check_support import Checks

gh_sync = load_script("gh-sync.py")

C = Checks()
check = C.check
REPO = "implentio/fake"
BOARD = {"intercepted": "every card write goes through the patched _place"}
FEAT = "FEAT-9200-case"


def feat_dir(tmp, name):
    d = os.path.join(tmp, ".harness", "harness", "features", name)
    os.makedirs(d, exist_ok=True)
    return d


def write_plan(d, name, station="building", sources=()):
    Path(d, "plan.yaml").write_text(
        f"schema: plan/1\nfeature: {name}\nstatus: {station}\n"
        f"source_issues: [{', '.join(str(n) for n in sources)}]\n"
        "station_only: true\ntasks: []\n", encoding="utf-8")


def write_feature(d, name, github):
    doc = {"feature_id": name, "branch": "none", "pr": None, "review_sha": "none",
           "cycles_used": 0, "max_total_cycles": 1, "runs": [], "github": github}
    Path(d, "feature.json").write_text(json.dumps(doc, indent=2), encoding="utf-8")


def opened_github(mirror=()):
    return {"milestone": 7, "parent": 40, "attached": ["T-01"], "issues": {"T-01": 41},
            "source_issues": list(mirror)}


def unopened_github(mirror=()):
    return {"milestone": None, "parent": None, "attached": [], "issues": {},
            "source_issues": list(mirror)}


def reason_file(tmp):
    p = os.path.join(tmp, "reason.txt")
    Path(p).write_text("the operator's signed reason", encoding="utf-8")
    return p


def snap(d):
    return tuple(Path(d, f).read_bytes() for f in ("plan.yaml", "feature.json"))


class Seams:
    """Replace the module's external seams with recorders; restore on exit.

    `fail` is a list of substrings: a `gh_try` call whose joined argv contains one returns
    (False, 'boom'), so a write failure is observable without a subprocess."""

    def __init__(self, fail=(), station_ok=True):
        self.events = []
        self.fail = list(fail)
        self.station_ok = station_ok

    def _gh_try(self, args):
        self.events.append(("gh", list(args)))
        if any(s in " ".join(args) for s in self.fail):
            return (False, "boom")
        return (True, "")

    def __enter__(self):
        fakes = {
            "gh_try": self._gh_try,
            "_place": lambda board, repo, num, station, **kw: (
                self.events.append(("place", num, station)) or True),
            "ensure_labels": lambda repo, labels: self.events.append(("labels", sorted(labels))),
            "_record_station": lambda d, station: (
                self.events.append(("station", station)) or self.station_ok),
            "_prune_abandoned_runs": lambda d, dry_run=False: self.events.append(
                ("prune", dry_run)),
        }
        self._stack = contextlib.ExitStack()
        for name, fake in fakes.items():
            self._stack.enter_context(mock.patch.object(gh_sync, name, fake))
        return self

    def __exit__(self, *exc):
        return self._stack.__exit__(*exc)

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

    def before(self, p, q):
        """True when an event matching p and one matching q both exist, p's first."""
        i, j = self.index(p), self.index(q)
        return i is not None and j is not None and i < j

    def writes(self):
        return [e for e in self.events if e[0] in ("gh", "place", "station")]


def closed_issue(n):
    return lambda e: e[0] == "gh" and f"issues/{n}" in " ".join(e[1]) and "state=closed" in e[1]


def call_abandon(d, reason, **kw):
    """cmd_abandon with stdout/stderr captured. Returns (out, err, exit_code)."""
    out, err = io.StringIO(), io.StringIO()
    code = None
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            gh_sync.cmd_abandon(d, REPO, BOARD, reason, **kw)
        except SystemExit as e:
            code = e.code
    return out.getvalue(), err.getvalue(), code


def abandon(github, sources=(), station="building", seams=None, **kw):
    """One fresh feature directory, abandoned under recording seams.

    Returns (seams, out, err, exit_code, reason_path)."""
    with tempfile.TemporaryDirectory() as tmp:
        d = feat_dir(tmp, FEAT)
        write_plan(d, FEAT, station=station, sources=sources)
        write_feature(d, FEAT, github)
        reason = reason_file(tmp)
        with Seams(**(seams or {})) as s:
            out, err, code = call_abandon(d, reason, **kw)
    return s, out, err, code, reason


# --- planner ------------------------------------------------------------------------------------
REC = {**opened_github(), "build_entry": None}

base_plan = gh_sync._abandon_plan(REC)
with_sources = gh_sync._abandon_plan(REC, [51, 52])
src_lines = [line for kind, num, line in with_sources if num in (51, 52)]
check("AS-01 planner: opted-in sources join the SAME plan list, a comment and a close line each; "
      "the default plan has no source entry",
      len(src_lines) == 4 and not any(n in (51, 52) for _k, n, _l in base_plan)
      and [e for e in with_sources if e[1] not in (51, 52)] == base_plan,
      repr(with_sources))
check("AS-02 planner: each source close line names not_planned, abandoned and the backlog",
      [n for kind, n, _l in with_sources if kind == "source"] == [51, 52]
      and all(all(w in line for w in ("not_planned", "abandoned", "backlog"))
              for kind, num, line in with_sources if kind == "source"),
      repr(with_sources))

# A source that IS a task issue still gets the reason once but closes once; one that IS the
# parent is already commented and closed as the parent.
overlap = gh_sync._abandon_plan(REC, [40, 41, 51])
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
        plan = gh_sync._abandon_plan(REC, [51, 52])
        gh_sync._apply_abandon_plan(plan, REC, REPO, reason, lambda n, w: s.events.append(
            ("close", n, w)))
    comments = [a for a in s.gh() if a[:2] == ["issue", "comment"]]
    check("AS-04 executor: every comment, parent and both sources, passes the unchanged original "
          "reason-file argument",
          [int(a[2]) for a in comments] == [40, 51, 52]
          and all(a[-2:] == ["--body-file", reason] for a in comments),
          repr(comments))
    check("AS-05 executor: sources close with the target label 'source', in plan order",
          [e for e in s.events if e[0] == "close"]
          == [("close", 41, "issue"), ("close", 40, "parent"), ("close", 51, "source"),
              ("close", 52, "source")],
          repr(s.events))

# --- cmd_abandon: dry run -------------------------------------------------------------------------
s, out, err, code, reason = abandon(opened_github(), [51, 52], yes=False, close_sources=True)
check("AS-06 dry run with --close-sources lists both sources and writes nothing",
      "source #51" in out and "source #52" in out
      and "would ensure the abandoned label exists" in out
      and s.writes() == [] and ("station", "abandoned") not in s.events,
      out + repr(s.events))

# --- cmd_abandon: the flag decides, and a positive pairs every absence ----------------------------
for label, kw, expect_sources in (
        ("--yes without --close-sources", {"yes": True}, False),
        ("--yes with --close-sources", {"yes": True, "close_sources": True}, True)):
    s, out, err, code, reason = abandon(opened_github(), [51, 52], **kw)
    closed = s.targets("close")
    if expect_sources:
        check(f"AS-07 {label}: both sources closed, commented and labelled with the original "
              "reason-file argument",
              {51, 52} <= set(closed)
              and s.targets("comment").count(51) == 1 and s.targets("edit").count(52) == 1
              and [a for a in s.gh() if a[:3] == ["issue", "comment", "51"]][0][-2:]
              == ["--body-file", reason], repr(s.gh()))
        check("AS-08 close-sources: each source's backlog write follows its own close",
              all(s.before(closed_issue(n), lambda e, n=n: e == ("place", n, "backlog"))
                  for n in (51, 52)),
              repr(s.events))
    else:
        check(f"AS-09 {label}: ZERO source comment, close, label or board write, while the "
              "parent and task ARE disposed",
              {40, 41} <= set(closed) and not ({51, 52} & set(closed))
              and not ({51, 52} & set(s.targets("comment")))
              and not ({51, 52} & set(s.targets("edit")))
              and not any(e[0] == "place" and e[1] in (51, 52) for e in s.events),
              repr(s.events))

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
        s, out, err, code, reason = abandon(opened_github(), [alias, 52], **kw)
        gap = [l for l in out.splitlines() if f"#{alias}" in l and "--close-sources" in l
               and not l.startswith("gh-sync: would ")]
        check(f"GC-01 {alias_label}, {run_label}, no --close-sources: ZERO writes name #{alias}, "
              "and the skip is reported as a gap naming the flag",
              not touches(s, alias) and not touches(s, 52) and len(gap) == 1,
              out + repr(s.events))
        if kw["yes"]:
            check(f"GC-01 {alias_label}, --yes: the non-aliased entry #{other} IS still disposed "
                  "and the station is recorded",
                  other in s.targets("close") and ("station", "abandoned") in s.events,
                  repr(s.events))

    s, out, err, code, reason = abandon(opened_github(), [alias, 52], yes=True, close_sources=True)
    check(f"GC-01 {alias_label}, --close-sources --yes: #{alias} is commented once, closed once "
          "and reseated once, and no gap is reported",
          s.targets("comment").count(alias) == 1
          and s.targets("close").count(alias) == 1
          and s.events.count(("place", alias, "backlog")) == 1
          and not any(f"#{alias}" in l and "--close-sources" in l for l in out.splitlines()),
          repr(s.events))

# --- F1: a refused station write must not prune runs/ ------------------------------------------------
for label, station_ok, plan_station, prunes in (
        ("station write refused", False, "building", False),
        ("station write recorded", True, "building", True),
        ("station already abandoned", False, "abandoned", True)):
    s, out, err, code, reason = abandon(unopened_github(), station=plan_station,
                                        seams={"station_ok": station_ok}, yes=True)
    check(f"F1 {label}: runs/ pruned = {prunes}" + ("" if prunes else
          ", and the gap is reported"),
          (("prune", False) in s.events) == prunes
          and (prunes or ("runs/" in out and "not pruned" in out)),
          out + repr(s.events))

# --- a second ACTIVE feature citing the same source does not change the target set ----------------
with tempfile.TemporaryDirectory() as tmp:
    d = feat_dir(tmp, "FEAT-9203-mine")
    write_plan(d, "FEAT-9203-mine", sources=[51, 52])
    write_feature(d, "FEAT-9203-mine", opened_github(mirror=[51, 52]))
    other = feat_dir(tmp, "FEAT-9204-other-active")
    write_plan(other, "FEAT-9204-other-active", sources=[52, 77])
    write_feature(other, "FEAT-9204-other-active", opened_github(mirror=[52, 77]))
    mine_before, other_before = snap(d), snap(other)
    reason = reason_file(tmp)
    with Seams() as s:
        out, err, code = call_abandon(d, reason, yes=True, close_sources=True)
    sources_closed = {n for n in s.targets("close") if n not in (40, 41)}
    check("AS-10 a source cited by another active feature is still disposed, and only THIS "
          "plan's sources are targeted — never the other feature's #77",
          sources_closed == {51, 52} and 77 not in s.targets("comment")
          and not any(e[0] == "place" and e[1] == 77 for e in s.events),
          repr(sorted(sources_closed)))
    check("AS-11 neither feature's plan.yaml source list nor feature.json mirror is mutated",
          snap(d) == mine_before and snap(other) == other_before, "bytes differ")

# --- plan.yaml is authoritative over a stale mirror ----------------------------------------------
s, out, err, code, reason = abandon(opened_github(mirror=[99]), [51], yes=True, close_sources=True)
check("AS-12 plan.yaml's source list wins over a stale feature.json mirror",
      51 in s.targets("close") and 99 not in s.targets("close")
      and 99 not in s.targets("comment"), repr(s.gh()))

# --- unopened record ------------------------------------------------------------------------------
# One run serves AS-13 and AS-19: unopened, no sources, --yes, no --close-sources.
s, out, err, code, reason = abandon(unopened_github(), [], yes=True)
check("AS-13 unopened, no sources, --yes: no SKIP; records abandoned THEN prunes, with no "
      "remote write and no label creation",
      code is None and "SKIP" not in out
      and s.events == [("station", "abandoned"), ("prune", False)],
      f"code={code} out={out!r} events={s.events}")
as19_out = out

s, out, err, code, reason = abandon(unopened_github(), [51, 52], yes=True, close_sources=True)
station = lambda e: e == ("station", "abandoned")
check("AS-14 unopened with plan-only sources: both disposed, then station, then prune",
      {51, 52} <= set(s.targets("close"))
      and s.before(station, lambda e: e == ("prune", False))
      and s.before(closed_issue(52), lambda e: e[0] == "station"),
      repr(s.events))

# --- already abandoned ------------------------------------------------------------------------------
s, out, err, code, reason = abandon(unopened_github(), [51], station="abandoned", yes=True,
                                    close_sources=True)
check("AS-15 re-entry at abandoned: the station is NOT rewritten, the source IS disposed, "
      "and runs/ is still pruned",
      ("station", "abandoned") not in s.events
      and 51 in s.targets("close") and ("prune", False) in s.events,
      repr(s.events))

# --- failure continuation -------------------------------------------------------------------------
s, out, err, code, reason = abandon(unopened_github(), [51, 52], seams={"fail": ["issues/51 "]},
                                    yes=True, close_sources=True)
check("AS-16 a failed source close is reported and never stops the next source or the "
      "station and prune",
      "could not close source #51" in err and "#51 did not close" in out
      and 52 in s.targets("close") and ("place", 52, "backlog") in s.events
      and ("place", 51, "backlog") not in s.events
      and s.events[-2:] == [("station", "abandoned"), ("prune", False)],
      f"err={err!r} out={out!r}")

s, out, err, code, reason = abandon(unopened_github(), [51, 52],
                                    seams={"fail": ["issue comment 51", "issue edit 51 "]},
                                    yes=True, close_sources=True)
check("AS-17 a failed source comment and label are each named, and the card is still "
      "reseated and the later source disposed",
      "reason not posted on source #51" in err
      and "#51 closed but not labelled" in err and ("place", 51, "backlog") in s.events
      and 52 in s.targets("edit") and ("station", "abandoned") in s.events,
      f"err={err!r}")

# --- reporter honesty: sources received the reason although no parent is recorded -------------------
s, out, err, code, reason = abandon(unopened_github(), [51], yes=True, close_sources=True)
check("AS-18 the reporters say 'reason posted on source #51' and never claim the reason went "
      "unposted when a source received it",
      "reason posted on source #51" in out and "reason not posted" not in out, out)

check("AS-19 with no comment target at all, the gap line still says the reason was not posted",
      "no parent recorded — reason not posted" in as19_out, as19_out)

# --- direct callers keep the old signature -----------------------------------------------------------
s, out, err, code, reason = abandon(opened_github(), [51], yes=True)
check("AS-20 an existing direct caller (no close_sources argument) still disposes parent and "
      "task and touches no source",
      {40, 41} <= set(s.targets("close")) and 51 not in s.targets("close"),
      repr(s.events))

sys.exit(C.report())
