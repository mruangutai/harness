#!/usr/bin/env python3
"""Unit floor for gh-sync.py's Build-entry seams (T-11, BUG-1309, DEC-217's Over clause).
Cases each aimed at a state or observable the T-02/T-03/T-04 integration blocks in
tests/integration/test-gh-sync.py cannot construct (see this task's plan.yaml intent for the
case-by-case cross-check against all five integration files). Mutation-based discrimination
proof lives outside this file (throwaway scripts, never the real gh-sync.py) and is recorded in
this task's receipt.

python3 stdlib only. In-process load of the hyphenated gh-sync.py
(tests/unit/test-gh-cost-log.py:291).

    ./test-gh-sync-build-entry.py    -> exit 0 all pass, 1 otherwise
"""
import contextlib
import io
import itertools
import json
import os
import re
import sys
import tempfile
from unittest import mock

from unit_support import load_script
from check_support import Checks
from feature_record import binding as record_binding, evidence as record_evidence
from feature_record import schema as record_schema

gh_sync = load_script("gh-sync.py")

C = Checks()
check = C.check


def feat_dir(tmp, name):
    d = os.path.join(tmp, ".harness", "harness", "features", name)
    os.makedirs(d, exist_ok=True)
    return d


def github_block(build_entry, milestone=None, parent=None):
    """The closed `github` key set {milestone, parent, attached, issues, source_issues,
    build_entry}, varying only what a case sets."""
    return {"milestone": milestone, "parent": parent, "attached": [], "issues": {},
            "source_issues": [], "build_entry": build_entry}


def base_doc(feature_id, github=None):
    """A schema-valid feature.json: the seven required top-level keys, `github` added only
    where the case wants one."""
    doc = {
        "feature_id": feature_id,
        "branch": "none",
        "pr": None,
        "review_sha": "none",
        "cycles_used": 0,
        "max_total_cycles": 1,
        "runs": [],
    }
    if github is not None:
        doc["github"] = github
    return doc


def write_feature_json(d, doc):
    with open(os.path.join(d, "feature.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2)


def read_feature_json(d):
    with open(os.path.join(d, "feature.json"), encoding="utf-8") as f:
        return json.load(f)


class _Result:
    exit_code = None
    raised = False
    out = err = ""


@contextlib.contextmanager
def _captured():
    """Capture stdout/stderr for the duration of a call, and catch SystemExit."""
    cap, out, err = _Result(), io.StringIO(), io.StringIO()
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            yield cap
    except SystemExit as exc:
        cap.raised, cap.exit_code = True, exc.code
    finally:
        cap.out, cap.err = out.getvalue(), err.getvalue()


# ---------------------------------------------------------------------------
# Read and write side (T-02).

# BE-11: load_recorded normalizes an out-of-enum build_entry, "reopened", to None.
# BE-12: save_recorded of that record DROPS the key entirely — no build_entry in the written
# feature.json, asserted as key absence, never as a falsy value.
with tempfile.TemporaryDirectory() as tmp:
    d = feat_dir(tmp, "FEAT-9101-fixture")
    write_feature_json(d, base_doc("FEAT-9101-fixture", github=github_block("reopened")))
    rec = gh_sync.load_recorded(d)
    check("BE-11 load_recorded normalizes an out-of-enum build_entry to None",
          rec.get("build_entry") is None, repr(rec.get("build_entry")))
    gh_sync.save_recorded(d, rec)
    written = read_feature_json(d)
    check("BE-12 save_recorded of a normalized record drops the build_entry key",
          "build_entry" not in written.get("github", {}), repr(written.get("github")))

# BE-14: record_build_entry upgrades a recorded recovery-required to opened.
with tempfile.TemporaryDirectory() as tmp:
    d = feat_dir(tmp, "FEAT-9103-fixture")
    write_feature_json(d, base_doc("FEAT-9103-fixture", github=github_block("recovery-required")))
    gh_sync.record_build_entry(d, "opened")
    rec2 = gh_sync.load_recorded(d)
    check("BE-14 record_build_entry upgrades a recorded recovery-required to opened",
          rec2.get("build_entry") == "opened", repr(rec2.get("build_entry")))

# A legacy unbound opened mapping (no github.repo) is the owner's own generation: an
# environmental skip on rerun must not downgrade it; a bound feature's absence is not.
for factory, expected in ((None, "opened"), ({"repo": "org/product"}, "recovery-required")):
    with tempfile.TemporaryDirectory() as tmp:
        d = feat_dir(tmp, "FEAT-9105-fixture-legacy")
        doc = base_doc("FEAT-9105-fixture-legacy", github=github_block(
            "opened", milestone=3, parent=7))
        if factory:
            doc["factory"] = factory
        write_feature_json(d, doc)
        with mock.patch.dict(gh_sync._BUILD_ENTRY, repo="acme/widgets"):
            gh_sync.record_build_entry(d, "recovery-required")
        got = gh_sync.load_recorded(d).get("build_entry")
        check(f"legacy opened receipt, factory={factory}: rerun skip leaves {expected}",
              got == expected, repr(got))

# BE-19: skip() armed but feature.json does not exist — records nothing and creates no file.
with tempfile.TemporaryDirectory() as tmp:
    d = feat_dir(tmp, "FEAT-9104-fixture-absent")
    with mock.patch.dict(gh_sync._BUILD_ENTRY, feat_dir=d, remote_written=False), \
            _captured() as cap:
        gh_sync.skip("test message")
    exists = os.path.isfile(os.path.join(d, "feature.json"))
    check("BE-19 skip armed with feature.json absent records nothing and creates no file",
          cap.raised and cap.exit_code == 0 and not exists,
          f"raised={cap.raised} exit={cap.exit_code} exists={exists}")

# ---------------------------------------------------------------------------
# Build-entry preflight (T-04), uniform since FEAT-71: no feature id is exempt.

# A Build start with NO receipt is refused, and a recovery-required one proceeds with the
# merge-refused notice, for EVERY feature id: synthetic ones, plus every feature-id-shaped
# string the feature_record package itself holds as module data — read from the modules, never
# named here, so a reintroduced per-feature exemption table is probed without this file naming
# any real feature.
_held = set()
for _value in [v for m in (record_schema, record_evidence, record_binding) for v in vars(m).values()]:
    if isinstance(_value, (dict, set, frozenset, list, tuple)):
        _held.update(m for m in _value
                     if isinstance(m, str) and re.match(r"^(FEAT|BUG|PR)-[0-9]+", m))
not_refused, not_noticed = [], []
with tempfile.TemporaryDirectory() as tmp:
    for name in ["FEAT-9106-fixture", "BUG-9-x"] + sorted(_held):
        d = feat_dir(tmp, name)
        write_feature_json(d, base_doc(name, {}))
        with _captured() as cap:
            gh_sync._build_entry_preflight(d, {"build_entry": None})
        if not (cap.raised and cap.exit_code == 2 and "no recorded build entry" in cap.out):
            not_refused.append((name, cap.exit_code))
        with _captured() as cap:
            gh_sync._build_entry_preflight(d + "/", {"build_entry": "recovery-required"})
        if cap.raised or "the MERGE is refused until explicit recovery" not in cap.err:
            not_noticed.append(name)
check("BE-31 an absent receipt refuses the Build start for every feature id",
      not_refused == [], f"{len(not_refused)} not refused, e.g. {not_refused[:3]}")
check("BE-32 recovery-required warns that the merge is refused, for every feature id",
      not_noticed == [], f"{len(not_noticed)} exempt, e.g. {not_noticed[:3]}")

# ---------------------------------------------------------------------------
# recover-terminal (T-03).

# BE-25: _recover_terminal_conflict is None when --parent (a STRING, as main() passes it)
# matches the recorded parent via the int() coercion.
got = gh_sync._recover_terminal_conflict({"parent": 1289}, "1289")
check("BE-25 a matching string --parent against the recorded parent is no conflict",
      got is None, repr(got))

# BE-27: conflict is None when --parent is absent, and None when no parent is recorded.
r1 = gh_sync._recover_terminal_conflict({"parent": 1289}, None)
r2 = gh_sync._recover_terminal_conflict({"parent": None}, "5")
check("BE-27 conflict is None with no --parent given, and None with no parent recorded",
      r1 is None and r2 is None, f"r1={r1!r} r2={r2!r}")

# BE-28: milestone and parent both recorded — creates == [] and both adoption lines present.
creates, adoptions = gh_sync._recover_terminal_report({"milestone": 7, "parent": 40}, None)
check("BE-28 milestone and parent recorded yields no creates and both adoption lines",
      creates == []
      and "gh-sync: adopting recorded milestone 7" in adoptions
      and "gh-sync: adopting recorded parent #40" in adoptions,
      f"creates={creates!r} adoptions={adoptions!r}")

# BE-29: neither recorded — creates is exactly the two-line list.
creates, adoptions = gh_sync._recover_terminal_report({"milestone": None, "parent": None}, None)
check("BE-29 neither milestone nor parent recorded yields the exact two-line creates list",
      creates == ["create the milestone", "create the parent"], repr(creates))

# BE-30: a milestone recorded and --parent 9 given — creates is exactly the one adoption line,
# and across all four adoption states no returned line ever mentions a task or a sub-issue.
creates, _ = gh_sync._recover_terminal_report({"milestone": 7, "parent": None}, "9")
no_mentions = True
for milestone, parent in itertools.product((None, 7), (None, 40)):
    c, a = gh_sync._recover_terminal_report({"milestone": milestone, "parent": parent}, None)
    if any("task" in line.lower() or "sub-issue" in line.lower() for line in c + a):
        no_mentions = False
check("BE-30 milestone recorded plus --parent 9 given adopts by number, and no adoption "
      "state ever mentions a task or a sub-issue",
      creates == ["adopt parent #9 (given via --parent)"] and no_mentions,
      f"creates={creates!r} no_mentions={no_mentions}")

sys.exit(C.report())
