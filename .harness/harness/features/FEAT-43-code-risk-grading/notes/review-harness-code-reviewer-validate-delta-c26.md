# Code review — FEAT-43 cycle 26 — B21 hold-and-fix delta

**Reviewed:** `e12d53b16e49e7c4d9332c5e290e6bdbc806251f..cd8dae476607704fd3d2b874150aae9f814292d2`
**Verdict:** PASS (advisory notes only, none gating)

**BLUF:** The one authorized behavioral commit (`cd8dae4`) touches exactly one file,
`test-code-grade.py`, +68/-0, adding the two named tests, both registered in `main()`. `code_grade.py`
is byte-identical at both pins (git blob hash match). Both mutations named in the ruling now fail a
**named assertion** (not a crash) — I ran both myself and reproduced the operator's/orchestrator's
claimed output verbatim, then restored byte-identically. All five focused suites pass at exit 0. No
`must_fix`. One pre-existing low/advisory comment-drift finding (carried from c25, untouched by this
delta) and one new low/advisory finding about what the qualname-collision test's docstring claims
versus what its assertion actually observes — neither changes behaviour or gates.

## Stage 1 — spec compliance

**Scope.** `git diff --stat e12d53b1 cd8dae47` shows 12 files touched across the full range, but only
`cd8dae4` ("test: bind the two spec-traced branches the suite could not see") is the reviewed
behavioral commit, and its own diff is exactly one file:
`.claude/skills/harness/bin/test-code-grade.py`, 68 insertions, 0 deletions (`git diff` on that commit
alone; confirmed 0 deletion lines outside the diff header). The other 11 file changes belong to two
earlier "chore" commits already in the range (`b18e915` "record the FEAT-43 cycle-25 T-01 closure...",
`4540b58` "record the FEAT-43 final pre-ship state...") — `STATE.md`, `feature.json`,
`answers/Q9-...md`, five `notes/*-c25.md` files, `notes/uat-sc11-c21.md`, and
`observations/harness-backend-dev.md`, all under this feature's own bookkeeping tree. None touch
application source. `feature.json`'s appearance is the orchestrator-bookkeeping case the dispatch
named explicitly; I extend the same classification to the other ten for the same reason (feature-tree
notes/state/answers, not code) — noted, not reviewed as source, no scope-creep finding.

**Production code untouched.** `git diff e12d53b1 cd8dae47 -- code_grade.py` is empty. Blob hash at
both pins: `43a360718045e7e8371960a6292841fa92566bf9` (identical). SHA-256 of the working-tree file:
`10b5e883...564cb6`. No production change, whitespace or otherwise.

**Both tests registered.** `main()`'s checks tuple lists `check_docstring_only_rename_not_gated` and
`check_method_qualname_collision_pre_images` at `test-code-grade.py:653-654`.

**Fixture correctness — `check_docstring_only_rename_not_gated` (`:480`).** Base has `documented()`
with docstring "Original text."; head renames it to `renamed()` with docstring "Rewritten text.".
Traced `_resolve_pre_image` (`code_grade.py:391`): `before_names.get(record.qualname)` is checked
**first** and returns immediately on a name match, never reaching the hash-fallback branch that
depends on `_strip_docstring`. A docstring-only edit **without** a rename keeps the qualname stable,
so resolution short-circuits on the name lookup and never exercises `_strip_docstring` — proving
nothing under either mutation. The rename is what forces the miss at `_resolve_pre_image:392-393` and
the fall-through to the hash comparison at `:394-395`, which is where `_strip_docstring` (`:347`,
called via `_hash_body:355`) actually matters. Confirmed by trace and by running the mutation (below).

**Fixture correctness — `check_method_qualname_collision_pre_images` (`:511`).** `Alpha.run` returns
`"alpha"`, `Beta.run` returns `"beta"` — different source text, confirmed by reading the fixture.
Measured their actual grades directly through `code_grade.grade_source`: **identical** — grade 5,
cyclomatic 1, cognitive 0, ABC 0.0 for `dispatch`, `Alpha.run`, and `Beta.run` alike (string-literal
content doesn't move any of the three metrics). So the assertion does **not** discriminate a
wrongly-attached pre-image between `Alpha.run` and `Beta.run` themselves — a cross-attachment between
those two would be invisible, since both grade identically either way. What it does discriminate,
confirmed empirically by running the mutation, is the derived symptom on the **third** function in the
fixture: under `_qualname → return name`, `_body_hashes`' `collect()` (`:360-369`) computes bare
(non-dotted) keys for every method, so `Alpha.run` and `Beta.run`'s hash-map entries collide under the
literal key `"run"` and the later one silently overwrites the earlier — which discards the base
top-level function's own `"run"` hash entry too (same key, same collision), because the fixture's
top-level function is *also* named `run` on `base`. That loss is what makes the head-side rename
(`run` → `dispatch`) fail its hash-based pre-image lookup and wrongly land in `gated` instead of
`informational`. This is a real, non-vacuous assertion against `gated_set` (the actual API, not a
helper's return value) and it is what the mutation run below actually breaks — see Stage 2 for the
one advisory note this raises about the docstring's framing.

**Self-grading.** `git diff e12d53b1 cd8dae47 -- test-code-grade.py` shows 0 deletions anywhere in the
file — `SELF_GRADING_ALLOWLIST` and the block comment above it are byte-for-byte unchanged; no entry
was added to excuse either new test. Graded the two new functions directly:
`check_docstring_only_rename_not_gated` — grade 4 (ABC 17.7, cyclomatic 3, cognitive 0), bar 3, PASS.
`check_method_qualname_collision_pre_images` — grade 4 (ABC 19.8, cyclomatic 3, cognitive 0), bar 3,
PASS. Both comfortably above the test-file bar with no allowlist entry needed.

**Measurement 1 confirmed.** `code-grade.py --base 7ccfae8dd7644bc3aaea612dabf4317c0d804f99 --head
cd8dae476607704fd3d2b874150aae9f814292d2`, run from the correct cwd: **exit 0**, **198** `FUNCTION`
records, **12** `REASON REQUIRED` demands, all 12 at `SEVERITY: med` (zero blocking, zero high/critical).
Diffed the 12-name `REASON REQUIRED` set against the same command run at `--head e12d53b1` (the prior
reviewed pin): **byte-identical set** (`main` ×2, `_case_27_owner_manifest`, `test_paths`,
`test_rejected_revisions`, `test_control_paths`, `test_bars_follow_test_kinds`,
`test_diff_and_determinism`, `check_commit_resolution`, `check_changed_function_resolution`,
`check_policy_loading`, `reviewed_python_change`) — unchanged, none appeared or vanished.

**Measurement 2 confirmed.** `code-grade.py code_grade.py`: **exit 0**, **53** functions, grade
distribution 11×grade-4 + 42×grade-5, **zero** below grade 4, all `RESULT: PASS`.

**Mutation binding — empirical, both directions.**
- `_qualname` → `return name`: `python3 test-code-grade.py` → **exit 1** —
  `FAIL qualname collision gated set: expected set(), got {'dispatch'}` /
  `FAIL qualname collision informational set: expected {'Alpha.run', 'Beta.run', 'dispatch'}, got
  {'Alpha.run', 'Beta.run'}`. This is a named `check()` assertion failure with a clean traceback-free
  exit, **not** a `KeyError`/exception abort — the design-constraint concern in the dispatch does not
  apply to this fixture; confirmed, not inferred.
- `_strip_docstring` → `return body`: `python3 test-code-grade.py` → **exit 1** —
  `FAIL docstring-only rename gated set: expected set(), got {'renamed'}` /
  `FAIL docstring-only rename informational set: expected {'renamed'}, got set()`. Matches the
  orchestrator's cited output verbatim.
- Restored both files from a pre-mutation copy after each mutation. SHA-256 of `code_grade.py`
  post-restore: `10b5e883...564cb6` (matches pre-mutation). `git status --porcelain -- code_grade.py
  test-code-grade.py` empty after each restore. `python3 test-code-grade.py` → exit 0 after each
  restore (`PASS test-code-grade`). Re-ran all five focused suites after both restores — all exit 0
  (see below).

**Comment drift (carried finding).** The `SELF_GRADING_ALLOWLIST` range comment at
`test-code-grade.py:~208` still reads "SC-15 section, items 1-12,14,15" and is still stale relative
to items 3/4 removed at c25 — unchanged by this delta (0 deletions in the diff touch that region), so
this finding neither regresses nor resolves. Still low/advisory, still non-gating, per the c25 review.

## Stage 2 — code quality

- **[positive]** Both new tests reuse the file's existing fixture helpers (`_git`, `_write`,
  `_commit`, `check`) verbatim — no new abstraction, no copy-paste divergence, no scope creep beyond
  the two named branches.
- **[positive, fail-open hunt]** Both tests assert the full `gated_set`/`informational` **partition**
  returned by `code_grade.gated_set` (the real public API), not a return value of an internal helper —
  satisfies "asserts the real API, not a proxy" per the ruling's own bar ("a test that passes by
  asserting less is a regression dressed as a fix").
- **[low, advisory, does not gate]** `check_method_qualname_collision_pre_images`'s docstring reads
  "two same-named methods on different classes collide in the body-hash map" as if the test directly
  observes that collision on the two methods themselves. It does not: `Alpha.run` and `Beta.run` grade
  identically (measured: grade 5/5 both ways), so a hypothetical cross-attachment between the two of
  them specifically would be invisible to this assertion. What the test actually — and correctly —
  proves is the *derived* consequence of that same collision: the same-keyed `"run"` overwrite in
  `_body_hashes` also destroys the base top-level function's hash entry, which is what makes the
  `dispatch` rename resolve wrong. The mechanism named in the docstring is real (confirmed by the
  mutation run), but the docstring slightly overclaims which symptom carries the proof. Does not
  affect gating: the assertion is non-vacuous, targets the real API, and is confirmed (not assumed) to
  fail under the exact mutation the ruling names.
- **[low, advisory, carried]** Stale `SELF_GRADING_ALLOWLIST` range comment, unchanged by this delta
  (see Stage 1).

No dead code, no unhandled errors, no fail-open pattern introduced by the +68 lines. Both docstrings
are otherwise accurate to the code they describe.

## Suites (individually, from the worktree, post-restore)

| Suite | Exit |
|---|---|
| `test-code-grade.py` | 0 |
| `test-code-grade-cli.py` | 0 |
| `test-gate-policy.py` | 0 |
| `test-check-plan-routes.py` | 0 |
| `test-validate-digest.py` | 0 |

## What this review did NOT cover

The six closed defects from earlier cycles; the canonical/project-wide test suite; `check-state.sh`;
SC-11's UAT; the eleven non-source bookkeeping files in the full commit range (`STATE.md`,
`feature.json`, `answers/`, `notes/*-c25.md`, `observations/harness-backend-dev.md`) beyond confirming
they are not application source; whether `notes/uat-sc11-c21.md`'s `review_sha` line has been
re-pinned to `cd8dae47` (out of my dispatched checklist; noted only that the file is currently
working-tree-dirty from a concurrent sibling process, not from anything I touched — see below);
editing or committing anything.

## Note on concurrent worktree activity

`git status --porcelain` in this worktree shows tracked modifications to `feature.json`,
`notes/uat-sc11-c21.md`, `observations/harness-pm.md`, and several untracked notes files. These are
being written live by sibling agents (QA, PM goal-check, B21 backend-dev) per the batch context's
"a concurrent product run is refreshing the goal-check" — confirmed none of it is `code_grade.py` or
`test-code-grade.py`, the only two files I mutated and restored. `git -C
/Users/molchairuangutai/GitHub/harness status --porcelain` (the outer repo, not this worktree) shows
only pre-existing untracked (`??`) entries unrelated to this feature — no tracked modification.
