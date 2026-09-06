#!/usr/bin/env python3
"""THE STANDING PIN GUARD (FEAT-55 T-01, intent section 13).

Asserts that .harness/harness/docs/DECISIONS.md and
.claude/skills/harness/references/github-mirror.md carry an IDENTICAL copy of the sentence
describing whether a target repository supports native Issue Types, through explicit create
opt-in. This is a SECOND FILE, not an assertion group inside test-issue-types.py, because
test-issue-types.py's own verify (T-02) requires it GREEN, and T-02 lands long before either
documentation task (T-11 writes DECISIONS.md, T-12 writes github-mirror.md) does — folding this
assertion into that file would make T-02's gate unpassable for a reason that has nothing to do
with T-02.

run-unit-tests.sh globs tests/unit/test-*.py, so this file runs in the STANDING unit suite
forever (D-08): T-12's own verify stops running the moment review_sha pins, but the duplicated
row does not stop existing, and this is what keeps it honest after that.

RED until T-11 and T-12 both write the row. THREE separate failures, each reporting on its own:
  - the row is MISSING from DECISIONS.md
  - the row is MISSING from github-mirror.md
  - the two extracted rows are DRIFTED (present in both, but not identical)
A single equality comparison is not enough: with the row absent from both files, two absent
values compare equal and the guard would pass on exactly the state it exists to catch. Presence
is asserted first, per file, then equality — and the row's full text is never hard-coded here as
a third copy, because the pin is that the two FILES agree, not that either matches a copy kept
here.

    ./test-issue-types-pin.py    -> exit 0 all pass, 1 otherwise
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
import re
import sys

FAILS = 0

DECISIONS_PATH = _anchor_os.path.join(_anchor_root, ".harness", "harness", "docs", "DECISIONS.md")
MIRROR_PATH = _anchor_os.path.join(
    _anchor_root, ".claude", "skills", "harness", "references", "github-mirror.md")

PIN_PATTERN = re.compile(
    r"whether a target repository supports native Issue Types.*?explicit create opt-in",
    re.DOTALL)


def check(name, cond, detail=""):
    global FAILS
    if cond:
        print(f"ok    {name}")
    else:
        FAILS += 1
        print(f"FAIL  {name}" + (f"\n        {detail}" if detail else ""))


def extract_pin(path):
    if not _anchor_os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        text = f.read()
    m = PIN_PATTERN.search(text)
    return m.group(0) if m else None


_decisions_pin = extract_pin(DECISIONS_PATH)
_mirror_pin = extract_pin(MIRROR_PATH)

check(f"MISSING PIN: {DECISIONS_PATH} carries the row",
      _decisions_pin is not None, f"pattern not found in {DECISIONS_PATH}")
check(f"MISSING PIN: {MIRROR_PATH} carries the row",
      _mirror_pin is not None, f"pattern not found in {MIRROR_PATH}")

if _decisions_pin is not None and _mirror_pin is not None:
    check("DRIFTED PIN: the two extracted rows are identical",
          _decisions_pin == _mirror_pin,
          f"DECISIONS.md={_decisions_pin!r} github-mirror.md={_mirror_pin!r}")
else:
    check("DRIFTED PIN: the two extracted rows are identical", False,
          "skipped — at least one pin is missing, see the MISSING PIN failures above")

print(f"\n{'ALL PASSED' if not FAILS else str(FAILS) + ' FAILED'}")
sys.exit(1 if FAILS else 0)
