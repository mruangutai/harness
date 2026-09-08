# REUSE angle — BUG-1480 (c0)

**BLUF:** Two real duplications found, both correctly deferred (not applied). `_checkout_root`
duplicates `_norm`'s comparison core (~4 lines), but a mechanical unifying helper is less clean
than it first looks because the two functions diverge on the null-path guard and the fallback
value — and D-03 already blessed the sibling-helper shape. Land: **defer, correct as-is**. The
test-fixture duplication in `_handoff_worktree_cases` is a cleaner, cheaper reuse opportunity but
is out of reach this pass regardless (DEC-174 suspends the apply on `tests/**` too).

## `_norm` call-site count (per instructions, counted not trusted)

`grep -o '_norm(' check-domain.sh | wc -l` → **16** total occurrences; one is the `def _norm(path):`
line (1114), so **15 call sites**, not eleven: lines 1920, 1926, 1964, 1989, 2057, 2058, 2060,
2061, 2062, 2072, 2087, 2091, 2103 (×1), 2104 (×1), 2232. All 15 predate this diff — the diff adds
zero new `_norm` call sites (it adds `_checkout_root`, a sibling, and changes one `handoff_done_when.problems(...)`
argument that does not call `_norm`). The dispatch's "eleven" undercounts by four; noting the
discrepancy for the record, it does not change either finding below.

## Finding 1 — `_checkout_root` duplicates `_norm`'s comparison core

- **file/line:** `.claude/skills/harness/bin/check-domain.sh:1151-1162` vs `:1114-1149` (`_norm`)
- **summary:** Both bodies do `import harness_boundary as _hb`; `_ck = _hb.checkout_relative(_claimed_abs(path))`;
  `if _ck is not None and _hb.real(_ck[0]) != _hb.real(root): return _ck[N]`; `except Exception: pass`.
  They are **not** byte-identical, though: `_norm` unconditionally computes `rel =
  os.path.relpath(...)` before the `try` and has no null-path guard; `_checkout_root` opens with
  `if not path: return root` and never computes `rel` at all. The fallback return also differs by
  necessity (`rel` vs `root`) — they answer different questions.
- **concrete cost:** the shared four lines (`_hb.checkout_relative` call + the `real(...)`
  comparison) are two spellings that must move together if `harness_boundary.checkout_relative`'s
  contract ever changes (e.g. a third tuple element, or different None handling). Whoever edits
  one and not the other ships a silent divergence.
- **alternative verified as (barely) mechanical:** a private `_checkout_pair(path)` returning
  `(root_or_ck0, rel_or_ck1)` once, with `_norm` reduced to `return _checkout_pair(path)[1]` and
  `_checkout_root` to its null-guard plus `return _checkout_pair(path)[0]`. This does not widen
  `_norm`'s public contract (D-03 stays intact) — but it is not a clean transcription: the
  null-guard has to move to the new wrapper, not the shared body, and the two current fallback
  values (`rel` vs `root`) have to be reconstructed from the pair rather than computed inline,
  which is exactly the kind of "looks mechanical, isn't quite" refactor that invites a fencepost
  mistake in a shape-gate module that must never fail closed.
- **disposition: defer** — the drift risk is low in practice (the two functions sit 35 lines apart,
  reviewed on one screen, and the shared comparison is 4 lines, not 40), while the fix requires a
  DEC-174 enforcement-layer edit to a registered PreToolUse gate for marginal benefit on a change
  explicitly scoped (D-01) as a standalone minimal-scope PR. The duplication is correct here as a
  backlog item, not an apply.

## Finding 2 — test fixture setup duplicated between two handoff-case builders

- **file/line:** `tests/integration/test-check-domain.py:4405-4413` (`_handoff_worktree_cases`,
  new in this diff) vs `:4155-4168` (`_handoff_done_when_fixture`, pre-existing)
- **summary:** `_handoff_worktree_cases` hand-rolls the same feature-fixture shape
  `_handoff_done_when_fixture` already builds — `os.makedirs(notes)`, identical
  `plan.yaml` content (`"tasks:\n  - id: T-03\n    verify: python3 test.py\n"`), identical
  `BRIEF.md` content, and the same `os.path.join(feat, "handoff-build.md")` target — instead of
  calling the existing helper against the worktree root. (It correctly DOES reuse
  `make_linked_worktree`, `_handoff_text`, `_invoke_handoff`, `_record_handoff_result` — verified
  by reading the body; nothing else here was hand-rolled.)
- **concrete cost:** two near-identical plan.yaml/BRIEF.md fixture spellings that must be edited
  in lockstep if the fixture shape changes (e.g. `handoff_done_when.py` starts requiring a new
  BRIEF section or a different task-id format) — the newer, less-visited copy (the worktree one,
  added by this diff) is the one an editor is likeliest to forget.
- **alternative:** `notes, target = _handoff_done_when_fixture(wt_path)` in place of lines
  4405-4413, adjusting the `main_feat` assertion at 4414-4415 to the feature id
  `_handoff_done_when_fixture` already uses (`FEAT-90-fixture`) instead of inventing
  `BUG-1480-wt-fixture`. The extra `team-config.yaml`/`review-fixture.md` writes the helper does
  are harmless no-ops for this case.
- **disposition: defer** — real and cheap, but the apply step is suspended for this whole pass
  (DEC-174: `tests/**` is enforcement-layer, main-session-executed only); nothing in this pass
  applies regardless of merit. Backlog it for the next `tests/integration/test-check-domain.py`
  touch.

## Zero further REUSE findings

Nothing else in the 15+42-line diff re-implements an existing constant, helper, or fixture.
