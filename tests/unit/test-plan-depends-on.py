#!/usr/bin/env python3
"""BUG-201 / REQ-01 / REQ-02 — every `depends_on` entry must name a task id present
in the SAME plan document.

Scope, ruled by the operator and reaffirmed three times: referential integrity ONLY.
NO self-dependency check, NO cycle detection, NO ordering policy. These cases assert
on the ids and the `depends_on` field name only, never on the rest of a message's
wording.
"""
from unit_support import ROOT  # noqa: F401 — must precede the bin imports below
import glob
import os
import re
import sys
import tempfile

try:
    import yaml
    import artifact_accessors
    import feature_corpus
    import harness_yaml
except ModuleNotFoundError:
    print("test-plan-depends-on: harness_yaml is not importable from this interpreter "
          "(PyYAML missing?) — treating as a hard failure, not a skip.")
    sys.exit(1)

from check_support import Checks

C = Checks()
check = C.check


# --- fixtures -----------------------------------------------------------------

_NOKEY = object()  # sentinel: "do not set the depends_on key at all"


def _task(tid, depends_on=_NOKEY):
    """A single legal plan task carrying every REQUIRED_TASK_FIELDS field, plus
    `depends_on` if `depends_on` is not the sentinel default. ONE helper so a later
    change to REQUIRED_TASK_FIELDS breaks one place, not N fixtures.
    """
    t = {
        "id": tid,
        "title": f"title {tid}",
        "change_type": "bugfix",
        "execution_mode": "team",
        "files": ["a.py"],
        "verify": "true",
        "intent": "do the thing",
    }
    if depends_on is not _NOKEY:
        t["depends_on"] = depends_on
    return t


def _doc(*tasks):
    return {"tasks": list(tasks)}


def _validate(doc):
    """Call validate_plan_doc and return the raised exception, or None if it
    returned cleanly. NEVER call validate_plan_doc bare in a case body: an
    unguarded raise would abort the whole suite and silently skip every later
    case while still looking like a partial pass.
    """
    try:
        harness_yaml.validate_plan_doc(doc, "fixture")
        return None
    except Exception as e:  # noqa: BLE001 — deliberately broad, see docstring
        return e


def expect_ok(name, doc):
    exc = _validate(doc)
    check(name, exc is None, f"unexpectedly raised {exc!r}")


def expect_reject(name, doc, *needles, extra=lambda s: True):
    """One PlanSchemaError whose message holds every needle and passes `extra`."""
    exc = _validate(doc)
    msg = str(exc)
    check(name,
          isinstance(exc, harness_yaml.PlanSchemaError)
          and all(n in msg for n in needles) and extra(msg),
          f"got {exc!r}" if exc is not None else "no exception raised")


# A quoted single character, e.g. 'T' or "0" — the shape a message would contain
# if a buggy implementation iterated a bare-string depends_on's CHARACTERS instead
# of rejecting the non-list shape, and reported each character as a phantom
# missing id (case 5).
_SINGLE_CHAR_ID_RE = re.compile(r"['\"][^'\"\s]['\"]")


# --- 1. a single dangling edge is rejected, naming both ends ------------------
expect_reject("a depends_on entry naming an absent task id is rejected, naming both ids",
              _doc(_task("T-01"), _task("T-02", depends_on=["T-99"])), "T-02", "T-99")

# --- 2. THE PAIRED ALLOW: the same shape naming a task that DOES exist --------
# Without this case a deny-everything implementation would pass case 1.
expect_ok("a depends_on entry naming a task id present in the same plan is accepted",
          _doc(_task("T-01"), _task("T-02", depends_on=["T-01"])))

# --- 3. two dangling edges in one document: exactly one exception, both named -
expect_reject("two dangling edges in one document raise ONE exception naming BOTH (D-02)",
              _doc(_task("T-01"),
                   _task("T-02", depends_on=["T-98"]),
                   _task("T-03", depends_on=["T-99"])),
              "T-98", "T-99")

# --- 4. depends_on absent, None, and [] are all accepted ----------------------
expect_ok("depends_on absent is accepted", _doc(_task("T-01")))
expect_ok("depends_on: null is accepted", _doc(_task("T-01", depends_on=None)))
expect_ok("depends_on: [] is accepted", _doc(_task("T-01", depends_on=[])))

# --- 5. depends_on given as a bare string, not a list --------------------------
expect_reject("a bare-string depends_on is rejected, naming the task id and the field, "
              "with no single-character phantom id from iterating the string",
              _doc(_task("T-01"), _task("T-02", depends_on="T-01")),
              "T-02", "depends_on", extra=lambda s: not _SINGLE_CHAR_ID_RE.search(s))

# --- 6. mixed id types: str() coercion must be applied on BOTH sides ----------
# 6a. integer id 1, referenced as the string "1" (a quoted id, as YAML produces).
expect_ok("6a: integer id 1 referenced as the string \"1\" is accepted",
          _doc(_task(1), _task(2, depends_on=["1"])))

# 6b. the mirror: string ids, referenced with an integer.
expect_ok("6b: string id \"1\" referenced as the integer 1 is accepted",
          _doc(_task("1"), _task("2", depends_on=[1])))

# 6c. integer ids, referencing an id that is genuinely absent — must still redden.
# THE VARIANT THIS CATCHES: an implementation coercing on only ONE side (known
# built from str(t["id"]) while the entry stays raw, or the reverse) accepts every
# same-type document and gives 6a and 6b a PHANTOM dangling-edge rejection instead.
expect_reject("6c: integer ids with a genuinely absent integer dependency (3) is rejected",
              _doc(_task(1), _task(2, depends_on=[3])), "3")


# --- walk(root): shared by cases 7 and 8 (synthetic corpora) and case 9 (the live
# corpus). Returns (files_found, failures) where failures is a list of
# (path, message) for every plan.yaml that raised under artifact_accessors.load_plan.
# The live corpus of a sparse worktree is its own feature plus the main corpus
# (FEAT-1559); a name present here is not walked again at the owner.
def walk(root):
    by_name = {}
    for corpus_root in feature_corpus.corpus_roots(root):
        for path in glob.glob(os.path.join(corpus_root, ".harness", "harness", "features", "*",
                                           "plan.yaml")):
            by_name.setdefault(os.path.basename(os.path.dirname(path)), path)
    paths = sorted(by_name.values())
    failures = []
    for path in paths:
        try:
            artifact_accessors.load_plan(path)
        except Exception as e:  # noqa: BLE001 — every path that raised must be named
            failures.append((path, str(e)))
    return len(paths), failures


def _write_plan(root, fid, depends_on):
    """Write a two-task plan.yaml, built from _task, whose T-02 depends on `depends_on`."""
    feat_dir = os.path.join(root, ".harness", "harness", "features", fid)
    os.makedirs(feat_dir)
    plan = os.path.join(feat_dir, "plan.yaml")
    with open(plan, "w", encoding="utf-8") as fh:
        yaml.safe_dump(_doc(_task("T-01"), _task("T-02", depends_on=[depends_on])), fh,
                       sort_keys=False)
    return plan


# --- 7. NON-VACUITY ON A SYNTHETIC CORPUS (D-04, FEAT-71) ----------------------
# The walk must reach every plan a corpus holds, or case 9's "no failures" over the live corpus
# reads identically to a walk that found nothing. Proven on fixture plans, never on the size of
# the real corpus: an empty or broken walk reports fewer than the three plans written here.
_SYNTHETIC = ("FEAT-90-fixture", "FEAT-91-fixture", "BUG-9-x")
with tempfile.TemporaryDirectory() as _tmp:
    for _fid in _SYNTHETIC:
        _write_plan(_tmp, _fid, "T-01")
    _count_s, _failures_s = walk(_tmp)
    check(f"the walk reaches every synthetic plan ({_count_s} of {len(_SYNTHETIC)}) and all load",
          _count_s == len(_SYNTHETIC) and not _failures_s,
          f"count={_count_s} failures={_failures_s!r}")

# --- 8. THE PAIRED DETECTOR (D-04): the SAME walk must still catch a dangling -
# depends_on. Without this case, a clean walk reads identically to a load_plan that
# had stopped checking anything at all.
with tempfile.TemporaryDirectory() as _tmp:
    _write_plan(_tmp, "FEAT-90-fixture", "T-01")
    _bad_plan = _write_plan(_tmp, "FEAT-XX", "T-99")
    _count_b, _failures_b = walk(_tmp)
    check("the same walk reports exactly one failure naming the throwaway dangling plan",
          _count_b == 2 and len(_failures_b) == 1 and _failures_b[0][0] == _bad_plan,
          f"count={_count_b} failures={_failures_b!r}")

# --- 9. THE LIVE CORPUS (D-04): every real plan.yaml loads ---------------------
# Asserts integrity only, never a size: cases 7 and 8 carry the vacuity guard, so this holds
# for however many features the corpus keeps.
_REPO = os.environ.get("HARNESS_PROJECT_DIR") or os.getcwd()
_count_a, _failures_a = walk(_REPO)
check(f"the live plan corpus loads cleanly ({_count_a} files found)",
      not _failures_a,
      "\n".join(f"{p} — {m}" for p, m in _failures_a))

sys.exit(C.report())
