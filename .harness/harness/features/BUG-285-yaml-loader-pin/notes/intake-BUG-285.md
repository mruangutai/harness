# Intake — BUG-285 — the operator's stated intent, and what I measured

BLUF: the operator's stated intent is one test fixture, in one file, pinning that
`gh-sync.py`'s `load_recorded` parses `feature.json` with a JSON parser and not a YAML one.
No production change is expected. Everything in section 1 is the operator's own words; everything
in section 2 I measured myself in this worktree today and cite by line.

## 1. The operator's stated intent — verbatim from the plan dispatch

> Mission: plan.
>
> ## The defect (already diagnosed — issue https://github.com/mruangutai/harness/issues/285)
>
> gh-sync.py's feature.json reader converged on json.load (FEAT-14 fix1, B-5). Swapping json.load back
> to a YAML loader (e.g. yaml.safe_load) still leaves the suite green: tests/integration/test-gh-sync.py
> has no fixture that is valid YAML but INVALID JSON, so nothing pins the reader's actual choice of
> parser. The old comment-tolerance fixture that used to catch this was correctly retired when the
> reader moved off YAML (JSON has no comments, so that fixture stopped meaning anything) — but nothing
> replaced it. Confirmed by grep: zero hits for a YAML-only construct anywhere in that test file's
> feature.json fixtures.
>
> This is advisory, not a live outage: a zero-byte file still refuses via a second guard, so the
> irreversible outcome is already closed. The gap is that only one of two guards is pinned by a test.
>
> ## Scope — keep this tight, do not widen it
>
> One new test fixture in tests/integration/test-gh-sync.py, near the existing T-06 Part C loader
> tests (~line 1395-1425), asserting the reader REJECTS a document that a YAML loader would accept but
> json.load would not — e.g. a document containing a `#` comment, or an unquoted YAML scalar shape
> JSON forbids. No production code change is expected; if the reader already rejects such a fixture,
> the task is to add the fixture and prove it currently passes, which is itself the proof the pin
> holds now that it did not have a test.
>
> Do not touch anything else in gh-sync.py or its other tests. Do not fold in any other backlog item.
>
> ## What "done" looks like
>
> - A new fixture exists that a YAML loader would accept and json.load rejects.
> - The test asserting the reader's rejection of that fixture is proven able to fail: shown red against
>   a mutant copy of the reader with json.load swapped for a YAML loader, then green against the real
>   reader.
> - The full existing test-gh-sync.py suite still passes unchanged.
>
> Write BRIEF.md and plan.yaml for this scope, one task, and return them pending for the operator's
> signature — do not proceed to build without it.

## 2. What I measured in this worktree (orchestrator, 2026-09-09) — not inherited

- The reader is `load_recorded` in `.claude/skills/harness/bin/gh-sync.py:484`. The parse is
  `json.loads(text)` at `:523`, inside a `try` that raises `SystemExit("… does not parse …")` on
  `(ValueError, UnicodeDecodeError)` at `:524-530`. The second guard the operator names is the
  `if not isinstance(doc, dict)` refusal at `:535`.
- Confirming the operator's "advisory, not an outage" claim mechanically: `yaml.safe_load("")`
  returns `None` (measured), so under a YAML loader the zero-byte document falls through the parse
  guard and is caught by the `isinstance` guard at `:535`. The zero-byte case therefore still
  refuses under the mutant — which is exactly why the existing zero-byte fixture
  (`tests/integration/test-gh-sync.py:1470-1473`) cannot detect the loader swap.
- Every existing T-06 Part C / fix1-Part-B fixture is written with `json.dump` or a JSON literal
  (`:1415-1520`), and JSON is a YAML subset, so all of them load identically under either parser.
  The operator's "zero hits for a YAML-only construct" is consistent with what I read.
- A one-token mutant is available and needs no new import: `gh-sync.py:101` already carries
  `import harness_yaml`, whose `load_str(text, where)` (`harness_yaml.py:207`) is a general YAML
  entry point. `json.loads(text)` -> `harness_yaml.load_str(text, path)` is the whole regression.
- Two candidate discriminating fixtures, both measured today: a block-style mapping
  (`feature_id: F1\ngithub:\n  parent: 40\n`) and JSON-with-a-`#`-comment. `yaml.safe_load` returns
  the same dict for both; `json.loads` raises `JSONDecodeError` on both. Either satisfies the
  operator's criterion; the choice is the planner's.
- Route resolution for the one file in scope: `check-domain.py --resolve
  tests/integration/test-gh-sync.py` prints `harness-backend-dev`, `harness-dev-ops`, `harness-qa`
  — a team lane, not main-session-direct.
- `.agents/skills` is a symlink to `.claude/skills` in this checkout (same inode for
  `gh-sync.py`, measured), so there is no second copy of the reader to keep in step. The test file
  resolves `BIN_DIR` from `.claude/skills/harness/bin` (`test-gh-sync.py:29`).

## 3. Open questions for the plan

- None from me. The scope is one file, one task, and the operator has already named the acceptance
  shape (fixture + mutant-red/real-green + suite unchanged).
