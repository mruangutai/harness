# Delta bless — PR #385 /simplify commit, 6296149..d15daa3

**BLUF: PASS.** The extraction is faithful, the M-1 loud-on-unknown property is preserved and
strictly widened (not weakened), the layout_fixtures derivation is order-faithful with no cycle, and
Q3's precision fix lands true without re-violating append-only. One low-severity behavioral drift
found outside the dispatcher's one pre-identified change; no must_fix.

## 1. Extraction equivalence — one unflagged drift found

Cross-checked all 5 causes + MIXED at both call sites (`check-state.sh` INV-27, `layout_migration.py`
`render()`):

- `no-evidence`, `no-rows`: byte-identical wording at both SHAs, both sites.
- `undeclared-segment`: the dispatcher's pre-identified change confirmed — "an UNDECLARED segment"
  (check-state.sh's old wording) → "undeclared segment" (render()'s old, now shared, wording).
- MIXED: `check-state.sh`'s old `_rd = ", ".join(...)` (comma-joined) is exactly what `blame_text()`
  now returns — no change in that branch.
- **`unreadable` / `neither` — render() gains a clause it never had.** At 6296149, `render()`'s
  `CANNOT_VERIFY` block only appended cause wording for `no-evidence`/`no-rows`/`undeclared-segment`
  (three explicit `if`s); `unreadable` and `neither` got no cause sentence at all in `render()` output
  — only the bare `blame()` list. `check-state.sh`'s old `_cv_wording` table, by contrast, already
  had wording for all 5. At d15daa3, `cause_text()` covers all 5 uniformly and `render()` now calls it
  unconditionally for every `CANNOT_VERIFY`, so a direct `layout_migration.py` invocation now also
  prints "a coupled reader could not be read" / "a coupled reader matches neither form" for those two
  causes — text that a bare `render()` call never produced before. This is the natural consequence of
  "the cause table used to live twice" becoming one, and plausibly intended, but it is a real output
  change outside the one drift the dispatch already named and outside item 5's named-crumb list.
  Severity **low**: no test asserts the old omission (case 9/10 only check tag presence, not exact
  wording), and no shipped consumer parses render()'s per-cause clause. Report per P-06 — flagging
  regardless of whether it is beneficial is separate from ruling on the merits.
- Separator convention (" — " → "; readers: ") and render()'s blame-list join format (per-item "; %s
  [%s]" → single "; readers: " comma list) — both match item 5's claimed "; readers: " convention
  surface; applied consistently at both call sites and both verdicts (MIXED, CANNOT_VERIFY).

## 2. Loud-on-unknown (M-1) — total, and no weaker

`cause_text()` is 5 explicit early-`return`s plus one unconditional final `return` (the "unrecognised
cause" sentence) — structurally total, no path returns `None` or falls through empty. Confirmed
strictly no weaker than the old dict-`.get()`-then-`None`-check form, and now applies uniformly at
both call sites (see §1). `_cv_wording`'s dead `_sname` parameter was unused in its own body — nothing
else was lost. `callable(_fmt)` dispatch has no surviving equivalent: `cause_text` is a plain if-chain,
no lambda/str dual-typing, no mis-route risk.

## 3. Q3 precision — lands true, no append-only re-violation

`DECISIONS.md` and `plan.yaml` both replace "the three reader-less causes" with text that correctly
distinguishes `no-rows` (readers=[] "structurally always empty," `layout_migration.py:233`) from
`undeclared-segment` (:236) and `no-evidence` (:246), which pass a real reader list and may or may not
yield an empty `blame()` depending on content. Verified against `scan()`: confirmed. Does not swing to
an overclaim (never says the other four are never reader-less; says blame() "may" be empty for them).
Both sentences trace to `a094dac`, a commit on this branch after `3c75aa6` (main's FEAT-20 ship point,
which has neither string) — confirmed by `git log -S"reader-less causes" --all`. Editing this branch's
own unmerged addition in place does not re-violate M-3's append-only rule, which protects the shipped
base entry (confirmed byte-identical at c2, unchanged here).

## 4. layout_fixtures.py coupling

`FEATURES_READERS`/`DOCS_READERS` derivation preserves `READER_TABLE`'s row order exactly (compared
element-by-element against 6296149's hardcoded lists and d15daa3's `READER_TABLE`). No cycle:
`layout_migration.py` has no import of `layout_fixtures`. Import-time `RuntimeError` on a `STUB`/table
key mismatch is the right altitude — this is exactly the fail-loud-on-drift shape M-1 established, and
both suites (test-check-state.py, test-layout-migration.py) import the module before running, so a
future rename fails both suites immediately rather than silently narrowing coverage. Minor note, not a
finding: the new `import layout_migration as _lm` at module scope means `layout_fixtures` re-executes
`layout_migration.py` under a plain import, separate from the `importlib.util`-loaded instance the
tests hold as `lm` (neither test registers its `load_module()` result in `sys.modules`) — harmless
here since only value-equal data (path strings) crosses that boundary, nothing compares by identity.

## 5. No regression outside claimed surface

`--stat` confirms every touched source file maps to a claimed bucket: `check-state.sh` and
`layout_migration.py` (extraction), `layout_fixtures.py` (derivation + guard + softened docstring —
verified true: `case_20`'s scanner does open this file since it isn't `test-*.py`, but zero lines match
its `PREDICATES` tuple so it emits no assertion; "skipped by that scanner" is loose phrasing for a true
outcome), `plan.yaml`/`DECISIONS.md` (Q3), `test-check-state.py` (MARKER_REL/FLEET_TEXT alias removal),
`test-layout-migration.py` (`import stat` removed — confirmed genuinely unused; case 18 variable naming
— no actual reuse added, cosmetic only, no consumer relies on it). No `[harness:human]` commits in
range (`git log -i --grep`/format check, zero matches). Both suites re-run clean: exit 0, all `ok`,
zero `FAIL`/`not ok` lines in either. Confirmed the CI grep contract (`.github/workflows/tests.yml`
greps only the unchanged `examined ...` and `layout: N surface(s) ...` trailer lines) is untouched by
this diff.

## Carried forward, not re-filed

c2's Q2 (no test pins CI/session-entry parity per cause) is weaker now, not resolved: the extraction
removes the *mechanism* of the prior drift (one shared table instead of two), so a future regression
would require re-inlining wording at a call site rather than editing one of two copies. Still no test
asserts that `check-state.sh` actually calls `cause_text`/`blame_text` rather than reimplementing.
Non-blocking, carried forward at reduced severity.

## Rejected candidates

- Separator/join-format change (" — " → "; readers: ", per-item → comma-joined) as a finding — rejected,
  this is item 5's named "; readers: " convention, applied consistently.
- Unrecognised-cause fallback wording difference (mentions "its call sites" vs "check-state.sh") —
  rejected, unreachable defensive path (5 causes are exhaustive per `scan()`), still loud either way.
- Double-import of `layout_migration` via `layout_fixtures`'s plain import — rejected as a finding,
  noted in §4: no identity-dependent comparison crosses that boundary.
- "skipped by that scanner" docstring phrasing — rejected as a finding, substantively true (verified
  in §5); flagged as loose wording only, not gating.
- Case 18 "reusing scan results" framing — rejected, no actual second use of `r_mixed`/`r_cv` in the
  diff; cosmetic variable naming only, no functional claim to falsify.

```yaml
VERDICT: PASS
DIGEST:
  headline: "The /simplify extraction is faithful and the M-1 loud-on-unknown property is preserved and strictly widened; one low-severity output drift found outside the dispatcher's named change (render() now emits cause wording for unreadable/neither, which it never did at 6296149), Q3's precision fix is true and doesn't re-violate append-only, and layout_fixtures's derivation is order-faithful with no import cycle."
  severity_max: low
  findings: 2
  must_fix: []
  spec_violations: []
  reviewed: "6296149..d15daa3"
  human_commits_in_scope: []
  open_questions:
    - { id: Q1, question: "render()'s CANNOT_VERIFY block now unconditionally calls cause_text(), so a bare layout_migration.py invocation emits cause wording for 'unreadable'/'neither' that it never emitted at 6296149. Plausibly intended (single-table consolidation) but not named as a change in the dispatch or the commit's crumb list. Confirm intent.", blocking: false }
    - { id: Q2, question: "c2's parity-coverage advisory (no test asserts check-state.sh actually calls cause_text/blame_text) is weaker post-extraction but still open: nothing pins that INV-27 uses the module's functions rather than a reimplementation.", blocking: false }
  files_touched: [.harness/features/FEAT-20-migration-detector/notes/review-harness-code-reviewer-hygiene-c3.md]
  expertise_update: []
artifact: .harness/features/FEAT-20-migration-detector/notes/review-harness-code-reviewer-hygiene-c3.md
```
