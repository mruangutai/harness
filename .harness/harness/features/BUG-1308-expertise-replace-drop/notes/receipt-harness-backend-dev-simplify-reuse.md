# SIMPLIFY — REUSE angle — BUG-1308 (expertise-merge.py ops/replace/drop)

BLUF: three small, real reuse findings, all restating logic the pre-existing (REQ-07-protected)
`apply` path already carries. None are safe to apply now without touching `apply`'s own lines, so
all three go to backlog except the one that stays entirely inside the new code. No test-file
duplication findings survive — the apparent overlaps are either the standing repo-wide test
convention or a deliberate independent-oracle design.

## Findings

**F1 — CONFLICT message shape restated (backlog)**
`expertise-merge.py:233-235` (`_resolve_add`, new) rebuilds the exact same three-line message —
`CONFLICT section=… id=…` / `  existing text: …` / `  proposed text: …` — that `cmd_apply`'s
`transform` closure already builds at `expertise-merge.py:434-436` (pre-existing, untouched by this
diff). Cost: the CONFLICT wording now has two independent spellings; a future tweak to one (e.g. a
reader parsing this line, as `test-expertise-merge.py` already does for other message shapes) can
drift from the other silently, and nothing asserts they stay identical. Alternative: a private
`_conflict_lines(section, id, base_text, prop_text)` helper both sites call. Not apply-now: the fix
touches `cmd_apply`'s lines 434-436, which REQ-07 protects (T-01's diff is pure-addition; this
would remove lines from the settled path).

**F2 — CAP EXCEEDED check restated (backlog)**
`expertise-merge.py:310-316` (`_check_caps`, new) re-implements the identical
`for name, cap in CAPS.items(): … CAP EXCEEDED section=… cap=… union_size=…` loop already inline
in `cmd_apply`'s `transform` at `expertise-merge.py:439-444` (pre-existing, untouched). Same cost
shape as F1: two copies of one cap-enforcement rule that must move in lockstep. Alternative:
extract one `_check_caps(merged)` (the new function already has the right shape) and have
`cmd_apply` call it too. Not apply-now for the same REQ-07 reason as F1 — the fix edits the settled
`apply` transform.

**F3 — refusal print-and-exit duplicated inside the new `cmd_ops` itself (apply-now candidate)**
`expertise-merge.py:490-493` and `:525-528` (both new, inside `cmd_ops`) each spell
`except harness_merge.MergeRefusal as refusal: for line in refusal.lines: print(line, …);
sys.exit(refusal.code)` — the identical four-line shape `cmd_apply` already carries twice at
`:406-409` and `:471-474`. Unlike F1/F2, this duplication is entirely inside code this diff adds:
a `_print_refusal_and_exit(refusal, stream=sys.stdout)` helper used by `cmd_ops`'s two sites alone
would not touch a single `cmd_apply` line, so it clears REQ-07. Cost: low (2 call sites, 8 lines →
1 helper + 2 calls) — flagging for completeness, not because it is high-value. Rated apply-now
only because it is the one candidate whose fix never touches the protected path; the lead may
still judge it not worth the ceiling's one slot.

## Declined candidates (considered, not raised)

- **`resolve_ops`'s machinery vs. `compute_union`/`_check_caps` at the call-site level** — the ops
  path could not call `compute_union` itself without changing `apply`'s replace-blind, add-only
  semantics; this is REQ-07 compliance (D-01/D-02 keying), not a finding, per the dispatch's own
  framing.
- **`RESULTS = []` / `def check(name, ok, detail="")` in both test files**
  (`tests/unit/test-expertise-ops.py:27-31`, `tests/integration/test-expertise-merge.py:40-44`) —
  grepped 20+ pre-existing test files under `tests/unit/` and `tests/integration/`; every one
  defines this scaffold locally, none import a shared helper, and no `conftest.py` or
  `*_helpers.py` exists anywhere under `tests/`. This is the standing repo convention, not
  something BUG-1308 introduced — declined.
- **`parse_section_entries`/`_ENTRY_LINE_RE` in the integration test
  (`tests/integration/test-expertise-merge.py:407-423`) vs. importing `expertise-merge.py`'s own
  `ENTRY_RE`** — the file's own docstring states this is a deliberate independent re-implementation
  so the test oracle cannot agree with a bug in the tool's own parser. Correct design, not a
  reuse gap.
- **Unit test's `base_sections`/`op()` fixture builders vs. integration test's
  `write_file`/`write_entries`/`write_ops`** — different testing levels (in-memory dicts feeding a
  pure function vs. on-disk files feeding a subprocess CLI); no importable common shape exists, and
  the two test dirs do not cross-import anywhere in this repo. Declined.
- **`require_expertise_destination` calling `harness_merge.require_destination`** — already correct
  reuse, not a finding.

## Not flaggable (settled per dispatch)

Any fix to F1/F2 that would edit `cmd_apply`'s lines is out of bounds under REQ-07 and is recorded
here as backlog only, per the dispatch's own instruction.
