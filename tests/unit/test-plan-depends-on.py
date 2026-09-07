#!/usr/bin/env python3
"""BUG-201 / REQ-01 / REQ-02 — every `depends_on` entry must name a task id present
in the SAME plan document.

Scope, ruled by the operator and reaffirmed three times: referential integrity ONLY.
NO self-dependency check, NO cycle detection, NO ordering policy. These cases assert
on the ids and the `depends_on` field name only, never on the rest of a message's
wording.
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
import re
import sys
import glob
import os
import tempfile

try:
    import harness_yaml
except ModuleNotFoundError:
    print("test-plan-depends-on: harness_yaml is not importable from this interpreter "
          "(PyYAML missing?) — treating as a hard failure, not a skip.")
    sys.exit(1)

fails = 0
ran = 0


def check(name, ok, detail=""):
    # Counted, never a frozen literal: a frozen total reddens (or lies) the moment
    # a case is added.
    global fails, ran
    ran += 1
    if ok:
        print(f"  ok  {name}")
    else:
        fails += 1
        print(f"  FAIL {name}")
        if detail:
            for line in str(detail).splitlines():
                print(f"      | {line}")


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


# A quoted single character, e.g. 'T' or "0" — the shape a message would contain
# if a buggy implementation iterated a bare-string depends_on's CHARACTERS instead
# of rejecting the non-list shape, and reported each character as a phantom
# missing id (case 5).
_SINGLE_CHAR_ID_RE = re.compile(r"['\"][^'\"\s]['\"]")


# --- 1. a single dangling edge is rejected, naming both ends ------------------
doc1 = _doc(_task("T-01"), _task("T-02", depends_on=["T-99"]))
exc1 = _validate(doc1)
check("a depends_on entry naming an absent task id is rejected, naming both ids",
      isinstance(exc1, harness_yaml.PlanSchemaError)
      and "T-02" in str(exc1) and "T-99" in str(exc1),
      f"got {exc1!r}" if exc1 is not None else "no exception raised")

# --- 2. THE PAIRED ALLOW: the same shape naming a task that DOES exist --------
# Without this case a deny-everything implementation would pass case 1.
doc2 = _doc(_task("T-01"), _task("T-02", depends_on=["T-01"]))
exc2 = _validate(doc2)
check("a depends_on entry naming a task id present in the same plan is accepted",
      exc2 is None, f"unexpectedly raised {exc2!r}")

# --- 3. two dangling edges in one document: exactly one exception, both named -
doc3 = _doc(_task("T-01"),
            _task("T-02", depends_on=["T-98"]),
            _task("T-03", depends_on=["T-99"]))
exc3 = _validate(doc3)
check("two dangling edges in one document raise ONE exception naming BOTH (D-02)",
      isinstance(exc3, harness_yaml.PlanSchemaError)
      and "T-98" in str(exc3) and "T-99" in str(exc3),
      f"got {exc3!r}" if exc3 is not None else "no exception raised")

# --- 4. depends_on absent, None, and [] are all accepted ----------------------
doc4a = _doc(_task("T-01"))
doc4b = _doc(_task("T-01", depends_on=None))
doc4c = _doc(_task("T-01", depends_on=[]))
exc4a, exc4b, exc4c = _validate(doc4a), _validate(doc4b), _validate(doc4c)
check("depends_on absent is accepted", exc4a is None, f"unexpectedly raised {exc4a!r}")
check("depends_on: null is accepted", exc4b is None, f"unexpectedly raised {exc4b!r}")
check("depends_on: [] is accepted", exc4c is None, f"unexpectedly raised {exc4c!r}")

# --- 5. depends_on given as a bare string, not a list --------------------------
doc5 = _doc(_task("T-01"), _task("T-02", depends_on="T-01"))
exc5 = _validate(doc5)
check("a bare-string depends_on is rejected, naming the task id and the field, "
      "with no single-character phantom id from iterating the string",
      isinstance(exc5, harness_yaml.PlanSchemaError)
      and "T-02" in str(exc5) and "depends_on" in str(exc5)
      and not _SINGLE_CHAR_ID_RE.search(str(exc5)),
      f"got {exc5!r}" if exc5 is not None else "no exception raised")

# --- 6. mixed id types: str() coercion must be applied on BOTH sides ----------
# 6a. integer id 1, referenced as the string "1" (a quoted id, as YAML produces).
doc6a = _doc(_task(1), _task(2, depends_on=["1"]))
exc6a = _validate(doc6a)
check("6a: integer id 1 referenced as the string \"1\" is accepted",
      exc6a is None, f"unexpectedly raised {exc6a!r}")

# 6b. the mirror: string ids, referenced with an integer.
doc6b = _doc(_task("1"), _task("2", depends_on=[1]))
exc6b = _validate(doc6b)
check("6b: string id \"1\" referenced as the integer 1 is accepted",
      exc6b is None, f"unexpectedly raised {exc6b!r}")

# 6c. integer ids, referencing an id that is genuinely absent — must still redden.
# THE VARIANT THIS CATCHES: an implementation coercing on only ONE side (known
# built from str(t["id"]) while the entry stays raw, or the reverse) accepts every
# same-type document and gives 6a and 6b a PHANTOM dangling-edge rejection instead.
doc6c = _doc(_task(1), _task(2, depends_on=[3]))
exc6c = _validate(doc6c)
check("6c: integer ids with a genuinely absent integer dependency (3) is rejected",
      isinstance(exc6c, harness_yaml.PlanSchemaError) and "3" in str(exc6c),
      f"got {exc6c!r}" if exc6c is not None else "no exception raised")


# --- walk(root): shared by case A (the live corpus) and case B (the paired
# detector). Returns (files_found, failures) where failures is a list of
# (path, message) for every plan.yaml that raised under harness_yaml.load_plan.
def walk(root):
    paths = glob.glob(os.path.join(root, ".harness", "harness", "features", "*", "plan.yaml"))
    failures = []
    for path in paths:
        try:
            harness_yaml.load_plan(path)
        except Exception as e:  # noqa: BLE001 — every path that raised must be named
            failures.append((path, str(e)))
    return len(paths), failures


# --- 7. THE LIVE CORPUS (D-04): the walk over every real plan.yaml -----------
# The count floor is the vacuity guard: measured at af859ee8 the corpus was 67
# files, all loading, none dangling. NEVER assert == 67 — features are added.
_REPO = (_anchor_os.environ.get("HARNESS_PROJECT_DIR")
         or _anchor_os.environ.get("CLAUDE_PROJECT_DIR")
         or _anchor_os.getcwd())
_count_a, _failures_a = walk(_REPO)
check(f"the live plan corpus loads cleanly ({_count_a} files found, floor 67)",
      _count_a >= 67 and not _failures_a,
      (f"only {_count_a} files found, floor is 67\n" if _count_a < 67 else "")
      + "\n".join(f"{p} — {m}" for p, m in _failures_a))

# --- 8. THE PAIRED DETECTOR (D-04): the SAME walk must still catch a dangling -
# depends_on. Without this case, case A reads identically to a load_plan that
# had stopped checking anything at all.
with tempfile.TemporaryDirectory() as _tmp:
    _feat_dir = _anchor_os.path.join(_tmp, ".harness", "harness", "features", "FEAT-XX")
    _anchor_os.makedirs(_feat_dir)
    _bad_plan = _anchor_os.path.join(_feat_dir, "plan.yaml")
    with open(_bad_plan, "w", encoding="utf-8") as _fh:
        _fh.write(
            "tasks:\n"
            "  - id: T-01\n"
            "    title: t\n"
            "    change_type: bugfix\n"
            "    execution_mode: team\n"
            "    files: [a.py]\n"
            "    verify: \"true\"\n"
            "    intent: do the thing\n"
            "    depends_on: [T-99]\n"
        )
    _count_b, _failures_b = walk(_tmp)
    check("the same walk reports exactly one failure naming the throwaway dangling plan",
          _count_b == 1 and len(_failures_b) == 1 and _failures_b[0][0] == _bad_plan,
          f"count={_count_b} failures={_failures_b!r}")



print(f"\n{ran - fails}/{ran} checks passed." if fails == 0 else f"\n{fails} of {ran} FAILING.")
sys.exit(1 if fails else 0)
