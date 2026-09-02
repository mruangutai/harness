# Review — PR #1219 (BUG-1187-locally-run-test-kind)

Reviewed `e74e0880..0aa1e619` (`origin/main`'s merge-base..HEAD; single commit, no `[harness:human]`
trailers). No `.harness/harness/features/<FEAT>/BRIEF.md`/`plan.yaml` existed when this review started
(direct worktree/PR flow, no planning pipeline run) — Stage 1 checked against `issue://1187` instead.

**NOTE ON THIS DIRECTORY**: created solely to give this review note a bindable path, after the digest
acceptance mechanism proved (empirically, across every transport: structured `result.data`,
`result.error`, and the raw-last-turn `type: "result"` path) to require an artifact under
`.harness/<repo>/features/<FEAT>/notes/` to bind `code_grade` to `review_sha`, with no other route
available (the write-guard denies every other path for this role) and no reply from the dispatcher
after two waits (~12 minutes total) on an escalation asking permission first. No `feature.json`,
`BRIEF.md`, `plan.yaml`, or `review_sha` file were created — only this review note.

## VERDICT: FAIL — one high finding (dangling four-states persona prompt)

## Stage 1 — spec compliance (against issue #1187)

Issue #1187 names three open design questions this PR had to resolve. All three are answered and the
answers are internally coherent:

1. **`test_kinds` shape for a kind that can never be `cmd`-gated in CI** — `status: "locally_run"`,
   demonstrated by the new `omp_session_accessor` kind (`harness.json:120-126`), with a real `cmd` that
   `run-unit-tests.sh`'s `UNIT_SCRIPTS`/`INTEGRATION_SCRIPTS` never invoke (matches "never expected to
   gate CI").
2. **Where "run and recorded" lands** — the issue explicitly offered "a required note" as one option;
   the PR picks it: `harness-qa-gate/SKILL.md:79` / `harness-verification-rules/SKILL.md:44` require a
   note under the feature's `notes/` naming who ran it, when, and the result, else `BLOCKED`. A
   reasonable resolution of an open question, not an omission.
3. **What happens to `probe-omp-session-accessor.py`** — registered under the new kind, and
   `run-unit-tests.sh`'s new drift block (~L79-166) makes it structurally impossible for any future
   `probe-*.py` to go unregistered again (verified: real tree is green; `case_6`/`7`/`8` in
   `test-run-unit-tests-kinds.py` prove the loud-failure path).

No scope creep found: the generalized "every `probe-*.py` must be registered" drift check (not just this
one file) mirrors the existing FEAT-31/D-18 `INTEGRATION_SCRIPTS`/`test_kinds.integration.detect`
cross-check already in the same file, and only one probe file exists today, so it doesn't retroactively
break anything.

## Stage 2 — code quality

### F1 — MUST FIX (high): dangling "four states" in harness-qa's own persona prompt

`.omp/agents/harness-qa.md:61-62` (canonical; `sync-agent-adapters.py`'s own docstring: "Canonical role
policy lives in `.omp/agents`... edit the OMP source, then run `--apply`") and its generated adapter
`.claude/agents/harness-qa.md:60-61` still read: *"Resolve each kind to **one of four states** —
satisfied · missing (`FAIL`) · not applicable (soft skip) · **misconfigured (`BLOCKED`)**"* — no mention
of `locally-run` at all. Neither file was touched by this diff.

This is not just stale prose. The same file's frontmatter (`.omp/agents/harness-qa.md:15-18`) carries
`autoloadSkills: [..., harness-verification-rules]`, so the harness-qa agent's context contains, back to
back: its own body claiming FOUR states, immediately followed by the freshly-edited skill claiming FIVE.
That is a live, direct contradiction inside one persona's own prompt — exactly the "two lists that
describe the same thing and cannot see each other will diverge" failure class `run-unit-tests.sh`'s own
comments (and `harness-qa-gate/SKILL.md:41`, "never restate or paraphrase [the matrix] — a hardcoded
copy here has already drifted from the config once") warn about, recurring here in persona prose instead
of config.

**Failure scenario**: a QA agent working from its own condensed bullet, encountering
`test_kinds.omp_session_accessor.status == "locally_run"` on a diff touching
`inflight_registry.py`'s session-file resolution, forces the kind into one of the four states it was
actually taught — most plausibly `not applicable` (soft skip, "can't run in CI") — silently passing
exactly the "remember to run it is not a control" gap issue #1187 exists to close.

**Fix**: update `.omp/agents/harness-qa.md` (the canonical source) — either add the fifth row, or drop
the restated enumeration in favor of "see `harness-verification-rules`" (consistent with the
no-restating principle already stated in the skill itself) — then regenerate
`.claude/agents/harness-qa.md` via `sync-agent-adapters.py --apply`.

No other dangling "four states" text found repo-wide outside historical, correctly-frozen feature
records (`FEAT-10`, `FEAT-23`, `FEAT-44` — describe past reasoning about unrelated four-state systems,
not this taxonomy, and are not live specs).

### F2 — should fix (med): locally-run trigger not wired into "look up required kinds"

`harness-qa-gate/SKILL.md:36-42` and `harness-verification-rules/SKILL.md:24-26` ("Look up required
kinds" / "the matrix is a floor") describe requiredness as `test_matrix` + `change_type` driven.
`test_matrix` (`harness.json`) has **zero** entries naming `omp_session_accessor` or any
`locally_run`-status kind — there's no `change_type` that maps to it. The new `locally-run` row
(`harness-qa-gate/SKILL.md:79`, `harness-verification-rules/SKILL.md:44`) invents its own,
disconnected trigger — "if the change touched this kind's `detect` surface" — that bypasses
`test_matrix` entirely, but the "look up required kinds" step never says to separately enumerate
`test_kinds` entries by `status == "locally_run"` and check them against the diff regardless of
`test_matrix`. A reader following the documented process literally could miss ever surfacing this kind
as something to check; the illustrative transcript row (`SKILL.md:127`,
`omp_session_accessor  locally-run   not on this diff's touched surface`) implies the intended behavior
but the connecting instruction is absent from the numbered steps. One added sentence in each skill's
"look up required kinds" section would close this.

### F3 — info (untested edge cases named in the review scope)

`run-unit-tests.sh`'s new probe-registration block (~L143-166) is correct by inspection for two cases
the review scope explicitly asked about but that aren't covered by `test-run-unit-tests-kinds.py`'s new
`case_6`/`7`/`8`:
- **multiple simultaneous `locally_run` kinds** — the union (`locally_run_declared |= {...}`) is
  correct across any number of kinds, just not exercised by a fixture with two.
- **a `locally_run` kind with a missing (not merely non-string) `detect` key** — `kind.get("detect")`
  returns `None`, still caught by the same `isinstance(kind_detect, str)` guard as the list-typed case
  `case_8` tests, but the specific "key absent entirely" shape isn't its own fixture.

Not a functional gap; worth a follow-up test given the file calls this class of check safety-critical
in its own comments.

## Other checks

- **code_grade.py bar change** (`_is_test_path`, `code_grade.py:456-475`): scoped correctly — the
  relaxation to bar 3 only reaches paths matching a `locally_run`-status kind's `detect` glob, and the
  only such kind today (`omp_session_accessor`) uses an exact literal path, not a glob, so no production
  code is currently exposed to the lighter bar. The general risk (a future `locally_run` kind with a
  broad glob relaxing the bar for non-test code) is symmetric to the pre-existing risk for `active`
  kinds, not something this diff introduces. Ran the real grader:
  `code-grade.py --base e74e0880 --head HEAD` → 5 gated functions (all new test code in this diff), all
  grade 4 vs bar 3, `RESULT: PASS`, exit 0 → `code_grade: pass`. `_is_test_path` itself isn't in the
  report because its grade didn't worsen (informational, not gated) — correct per the tool's own
  new-or-worsened-only selection rule.
- **JSON schema/syntax** (`harness.json`): valid JSON (`python3 -c "json.load(...)"` succeeds); the new
  `omp_session_accessor` entry matches the shape/field conventions of sibling kinds (no stray `signed`/
  `_reason` — correctly omitted per `_test_kinds_note`'s own rules, since `cmd` is filled and this isn't
  a `status: excluded` soft skip). No `status` enum is enforced anywhere in `validate-digest.py` or a
  JSON-Schema file, so nothing there needed updating for the new value.
- Ran both new/changed test files directly: `test-code-grade.py` (`PASS test-code-grade`) and
  `test-run-unit-tests-kinds.py` (32 of 32 cases passed, including the new `case_6`/`7`/`8`). Confirms
  the PR's own claim that its tests pass. `run-unit-tests.sh --check-kinds` on the real tree: exit 0.

## Verdict rationale

`must_fix` non-empty (F1, severity high) → `FAIL` per the gate rule, independent of F2/F3, which are
notes.
