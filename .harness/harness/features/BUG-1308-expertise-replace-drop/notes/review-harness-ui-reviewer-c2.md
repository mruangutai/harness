# UI/output-contract review — BUG-1308 — cycle 2 — pinned sha 48d2285b

## Verdict
PASS with one advisory (non-gating) finding. No REQ is violated, no exit code or byte-identity
behaviour regresses. Cycle-1's four VL findings remain closed. One new message-accuracy gap
(UI-01, low) is worth fixing but does not gate — the tool still refuses safely (exit 12) on the
input class it names.

## Measured census (not predicted)
`git diff --name-status origin/main..48d2285b` — **43 files changed** (all read via `git show
48d2285be7770a7e630b0a11c8136a55b2d351e3:<path>`, never a plain worktree read). Classified: 1
Python source, 2 Python test files, 1 skill doc, 3 harness-doc files, 36 feature-bookkeeping
files (BRIEF/STATE/feature.json/plan.yaml/notes/observations). Extension census
(`html|css|scss|tsx|jsx|vue|svelte|less`) over the full changed-path list: **0 matches — 0
rendered UI surfaces.** `DESIGN.md` check: `git cat-file -e 48d2285b:.harness/harness/features/
BUG-1308-expertise-replace-drop/DESIGN.md` → does not exist at the pin. Mode A/B graphical review
stays out of scope by direct measurement. This cycle's remit is the one surface the dispatch
names explicitly: the CLI's operator-facing output contract.

**Live execution was not possible this cycle** — `bash-write-guard` blocks every bash file write
for this role, including a `mktemp -d` scratch copy (tested: `touch` inside `/tmp` succeeds,
`tee`/redirect-to-file inside `/tmp` is BLOCKED with "harness-ui-reviewer is READ-ONLY"). All
findings below are a source-level trace of `expertise-merge.py`'s literal control flow, not a
captured runtime transcript. Recorded per this role's "known limit" — a dimension needing actual
execution is not verified by source-reading alone; I traced Python semantics precisely enough to
be confident in the *result*, but flag the method distinction explicitly.

## Per-file conclusions (all seven named)

1. **`.claude/skills/harness/bin/expertise-merge.py`** — see Findings below. `_validate_target_
   section` (:182–194): `MISSING TARGET`/`AMBIGUOUS TARGET` (10/11) each name section+id+reason
   per REQ-04/REQ-05, and the two `AMBIGUOUS TARGET` call sites (`:236–241` base-duplicate,
   `:283–288` proposal-duplicate) carry **distinct** `reason=` text, so no two different Step-B
   failures collide on one line. Stream discipline: `cmd_apply`/`cmd_ops` both send only the
   destination refusal (exit 9) to stderr and every in-band refusal (6/7/8/10/11/12) to stdout —
   `cmd_ops`'s own docstring states this ("same destination refusal (exit 9, stderr) … refusal
   lines to stdout") and the code matches it exactly in both functions. **Stream consistency
   between `apply` and `ops`: confirmed consistent, measured not assumed.**

2. **`tests/unit/test-expertise-ops.py`** — `case_u19` (VL-02 regression) exercises only a
   **truthy** non-string target (`["P-50", "x"]`); no case constructs a **falsy** non-string
   target (`0`, `False`, `[]`, `{}`) or an empty-but-present string target/section to check
   message-text accuracy — this is the untested combination behind UI-01.

3. **`tests/integration/test-expertise-merge.py`** — `case23` (non-string target through the CLI)
   has the identical gap: `["P-50", "x"]` only, same untested combination as (2).

4. **`.claude/skills/harness-distill/SKILL.md`** — `git diff 4c76f0f5..48d2285b` on this path is
   empty; no change in the fix cycle. Cycle-1's read (contract vocabulary vs `op: merge` refusal)
   stands unchanged.

5. **`.harness/harness/docs/SPEC.md` §5.3** — fix-cycle diff is a pure line-citation shift
   (`:484-533`→`:524-573` etc.) after the new validators inserted lines above; every cited range
   checked against the current function bodies and lands correctly. The refusal table's MALFORMED
   OPS row now also covers "gives an `entry` or `target` that is not a single-line string" — loose
   but defensible coverage of the isinstance branch; the table does not claim message-text
   accuracy for the missing-vs-falsy case, so it isn't itself wrong, only silent on the gap.

6. **`.harness/harness/docs/DECISIONS.md`** DEC-219 — no change in the fix-cycle diff; cycle-1's
   full read stands, no drift.

7. **`.harness/harness/docs/DECISIONS-INDEX.md`** — no change in the fix-cycle diff; cycle-1's
   read stands.

## Findings

- **UI-01** (severity: low, advisory — not gating) — `expertise-merge.py:182-191`
  (`_validate_target_section`). `if not target: _malformed(index, "missing required key
  target")` fires on **any falsy value**, not only a truly-absent key, and unconditionally
  precedes the `isinstance` check added by this fix cycle at `:186-187`. Concrete scenario: an op
  payload `{"op": "replace", "target": 0, "section": "Patterns", "entry": "x"}` — `target` **is
  present**, its value is simply the wrong type — exits 12 with `MALFORMED OPS op index=0:
  missing required key target`, which misstates the actual violation (a type mismatch, not an
  absent key) and is indistinguishable, by that line's text alone, from an op that omits `target`
  entirely. The identical collapse applies to `section` at `:189-190` for a falsy section value.
  Traced via Python `if not x` semantics (true for `None`, `""`, `0`, `False`, `[]`, `{}`) against
  the literal branch order; not runtime-captured this cycle (see census note above). No REQ names
  MALFORMED OPS message-text granularity (REQ-04/05 govern MISSING TARGET/AMBIGUOUS TARGET only),
  the exit code and byte-identity guarantee (REQ-06) both hold regardless, so this does not gate.
  Nature: **bug** — worth a one-line reorder (`isinstance` check before the truthiness check) plus
  a unit case with a falsy non-string target/section, but out of this cycle's remit to fix.

## Accessibility / theme parity
N/A — batch CLI stdout/stderr text, no colour-only state encoding, no rendered surface, no themes.

## Provenance
`git status --porcelain` — empty (confirmed after review, no HEAD move, no edits to
plan.yaml/BRIEF.md/STATE.md/feature.json, no source touched). Every source claim above cites
`git show 48d2285be7770a7e630b0a11c8136a55b2d351e3:<path>` output; the fix-cycle-scoped claims
additionally cite `git diff 4c76f0f5..48d2285b -- <path>`.

## Open questions
None blocking.
