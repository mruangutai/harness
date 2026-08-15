# Code review — FEAT-08-remove-cost-tracking — harness-code-reviewer

## Pin integrity

Reviewed `ae2443d..942505e` (21 commits by `git log --oneline` count, not 22 as the dispatch stated —
noted, not a defect). `HEAD` at review time was `ebea32e3` (one commit ahead of the pinned
`942505e`): `git log --oneline 942505e..ebea32e3` shows exactly one commit, "enter the validate phase
and pin review_sha for the panel," touching only `STATE.md` and `feature.yaml` (`git show --stat`
confirmed) — no source path in scope. `git merge-base --is-ancestor 942505e ebea32e3` confirms
942505e is an ancestor, so nothing in-scope was reordered or dropped. `git status --porcelain` shows
only other panel members' new report files under `.harness/features/FEAT-08-remove-cost-tracking/notes/`
and unrelated dirty files (`perf-review-agent-workflow-2026-08-04.md`, `2026-08-05.md` logs) — none
in a path I reviewed. No `[harness:human]` commits in range. **The tree I reviewed is the pinned
bytes**, confirmed by re-reading source files via `git show 942505e:<path>` throughout, not the
working tree, except where I first proved the two trees identical (`git diff 942505e HEAD -- <path>`
exit 0) before running live commands (`check-state.sh`, `run-unit-tests.sh`, `check-docs.sh`,
`gen-decisions-index.py --stdout`).

## Verdict: PASS

Spec compliance (Stage 1) is unusually thorough and precise — every SC I could mechanically check,
I ran myself, and all passed. Stage 2 found no correctness bugs, no fail-open, and no dangling
references. Findings below are low/info, none gate.

## Stage 1 — spec compliance

Read BRIEF.md and PLAN.md **including `## Amendments`** (A-1, A-2 superseded-by-A-4, A-3, A-4).
Traced every touched file to a task; found no file touched that no task named, and no task whose
files were untouched.

**Mechanically re-verified, not relayed** (all commands run by me against the pinned tree or a tree
proven identical to it):
- SC-01: `grep -rln --exclude-dir=worktrees -e cost_usd -e cost-report -e max_cost -e per_feature_usd -e INV-11 .claude/ docs/ .harness/harness.json .harness/team-config.yaml .harness/README.md` → exactly `DECISIONS.md`, `BUILD.md`, `DECISIONS-INDEX.md`, `SPEC.md`. Matches A-4's amended four-survivor set exactly.
- SC-03/SC-11: `check-state.sh` exits 0 (zero `bad`, only pre-existing unrelated `note` lines); `run-unit-tests.sh` exits 0, twelve `PASS` lines (thirteen minus the deleted `test-cost-report.py`), drift detector satisfied not bypassed.
- SC-04: confirmed by reading `validate-digest.py`'s `SCHEMAS["orchestrator"]` — `cost_usd` gone, five required fields.
- SC-05/SC-07: `grep -c max_total_cycles` → `:2` for both configs (byte-identical, untouched per D-10); `grep -c -e cost_model -e per_feature_usd -e per_run_usd -e warn_at_fraction -e _budgets_note` → `:0` for both.
- SC-08/SC-09: `gen-decisions-index.py --stdout | diff - DECISIONS-INDEX.md` exits 0 (hand-written DEC-148 ruling prose survives regeneration); `grep -c 'RULING PENDING'` → 0; DEC-178 entry (**`docs/harness/DECISIONS.md:4881`**, `grep -n '^## DEC-178'`) present once, contains all six required elements (reason, watchdog dropped + why, DEC-148 partial supersession, historical figures kept + 67-measurement, briefing line not replaced + backlog, `cost_usd` removed not aliased) and **no** `**Supersedes DEC-148**` line (D-05 compliance, confirmed by grep).
- SC-10: `check-docs.sh` exits 0.
- SC-12 (`verify: inspection`, `file:line` citation): live-code marker sites all read as required — `.claude/skills/harness/SKILL.md:21` ("costs ~100k tokens"), `:122` ("cost a working day" — shifted two lines by T-06's edit, content verbatim), `:224` ("Cost grows with the square..." — shifted five lines, content verbatim), plus the cycle-budget lines and `harness-team/SKILL.md`'s protected English uses, all read verbatim. The three YAML-fixture `cost:` hits SC-12 also names — `.claude/skills/harness/bin/test-harness-yaml.py:383,418-419`, `test-harness-yaml-corpus.py:214,216,218`, `test-check-domain.py:203,210,212` — are **absent from `git diff --name-only ae2443d..942505e`**: these three files are untouched by construction, so their `cost:` fixtures survive trivially. Both halves of SC-12 hold.
- SC-13: `grep -n -i -e cost .harness/README.md` returns nothing.
- SC-14: every remaining `cost-report.py` mention in `BUILD.md`/`SPEC.md` carries the `(cost-report.py removed — DEC-178)` marker — read every marked site directly, `file:line`s given inline in the BUILD.md/SPEC.md diff review below.
- SC-15 (`verify: inspection`, `file:line` citation): `.claude/agents/harness-orchestrator.md` — zero cost fields in the return template (verified in the diff: `runs: [{ id, squad, verdict, cost_usd }]` → `runs: [{ id, squad, verdict }]`, `cost_usd:` line deleted); `.claude/skills/harness/teams/build.yaml:40` and `review.yaml:16` — `max_cost_usd:` lines deleted, confirmed by direct diff read; `.claude/skills/harness/SKILL.md` — briefing step-2 list's `**cost line**` clause deleted (diff read directly, list otherwise intact). SC-15 holds.
- SC-06 (see below — reproduces exactly, with the caveat already disclosed in-repo).

**SC-06 caveat, independently reproduced, not novel.** `grep -h -e cost_usd -e max_cost_usd .harness/features/*/feature.yaml | wc -l` unrestricted returns 93, not 89; `grep -l '^cost:' .harness/features/*/runs/*/state.yaml | wc -l` returns 69, not 67. Both are **known and already disclosed** — `feature.yaml`'s own `open_questions` (Q5) states: "SC-06's glob over-captures; restricted to FEAT-01..07 its numbers are exactly pm's 89 and 67-of-67." I re-ran restricted to `FEAT-0[1-7]*` and got exactly 89 and 67 — confirmed byte-identical to the `ae2443d` baseline. The unrestricted overshoot is FEAT-08's **own** in-flight `feature.yaml` and two of its own `runs/*/state.yaml` (`plan-product` — a real pre-T-03 metered figure — and `t10r-product`, which still carries the literal `cost: pending_orchestrator` placeholder, the exact stale-cached-rule-surface scenario D-01's trade-off names as accepted; both `runs/` are gitignored, ephemeral, and not part of this diff at all). This is disclosed, not hidden, and matches D-01's accepted trade-off. Not a new finding.

**Spec violation — `mismatch`, low severity, does not gate.** `.claude/skills/harness/bin/test-validate-digest.py`, ref A-4/T-01. The amendment's replacement text says: "Delete the orchestrator fixture that carries `cost_usd: "12.83"` — the payload at `:753`, its comment block, and **the whole `case(...)` call they belong to**." What landed (commit `00f3e03`) removed only the `cost_usd` line and its four-line comment, keeping the `case("orchestrator digest with the reconciled schema", ...)` call itself, which still exercises the BUILD-task-14 schema shape minus cost. On the merits this is a **better** outcome than the literal instruction — deleting the whole case would have dropped that schema-shape assertion for no coverage gain, and the unknown-key-tolerance thinning A-4 already discloses as accepted is unaffected either way (the case's `cost_usd` line was the only thing providing incidental unknown-key coverage; that's gone under both readings). Still, it is a deviation from signed text, which is Stage 1 question 4's job to catch — reported, not waived by me.

**One thing I flag per the dispatch's standing invitation, disposition left to the orchestrator.**
`.harness/features/FEAT-08-remove-cost-tracking/feature.yaml:9-10` carries `cost_usd: "370.53 at
3503d1d..."` and `max_cost_usd: 120` in the feature's own, not-yet-shipped `feature.yaml`. The
`cost_usd` value is self-aware (names T-03 as having deleted the meter) and `max_cost_usd` is a
budget, which REQ-02/REQ-09 forbid surviving anywhere live. Out-of-scope ruling only covers
**shipped** `feature.yaml`; this one isn't. Not mine to disposition — carried as the one genuine
open question below.

## Stage 2 — code quality

No correctness bugs, no fail-open, no dangling references found in the DEC-174 carve-out surfaces
(`check-state.sh`, `validate-digest.py`, both tests) or anywhere else in the diff.

**Fail-open hunt, specific traces:**
- `check-state.sh`'s three INV-11-adjacent removals (rule, `cost_model.rates` hard violation, staleness warning) are clean deletions with no residual branch that could silently accept something it shouldn't — the removed `bad.append`/`warn.append` calls have no surviving caller. The `complete = ...` variable T-02's intent flagged as conditionally-removable was correctly **kept**, because it is genuinely still consumed by INV-15 at `check-state.sh:395` — verified by grepping every `complete` use in the file, not assumed.
- The `cfg`/`cj` parse block T-02 flagged as conditionally-removable was correctly **kept whole**: `cj` has four other live consumers (`test_kinds`, `github.sync`, `gh-config` checks at `:447`, `:448`, `:468`, `:502`, `:503`) — verified by grep, matching the new comment's claim.
- `CHECKPOINT_KEYS` still whitelists `"cost"` (D-03), correctly commented as historical-only; a `state.yaml` with or without a `cost:` block both pass (`test-check-state.py` `case_k`, both directions asserted, both re-run green by me).
- No script anywhere in `bin/` still reads `max_cost_usd`, `per_run_usd`, `per_feature_usd`, `cost_model`, or `warn_at_fraction` (`git grep` returns nothing) — no orphaned consumer, no silent default reactivating a deleted budget.

**Q7 — ruled (this was mine to rule, per `STATE.md`: "Blocked on: nobody — the code-reviewer
rules"), reported here as a finding, not returned as an open question.**

Three comments self-justify by pointing at an ephemeral verification event rather than a permanent
record. Found and quoted directly, not relayed — and the dispatch's framing of where they live was
wrong, corrected below:

1. `.claude/skills/harness/bin/check-state.sh:334` — "Named without its quoted spelling because
   this task's `verify:` counts that spelling."
2. `.claude/skills/harness/bin/validate-digest.py:178-179` — "Named without its literal spelling on
   purpose — this task's `verify:` asserts that spelling appears nowhere in this file."
3. `.claude/skills/harness/bin/test-validate-digest.py:767` — "Named without its literal spelling
   because SC-01's sweep asserts that spelling appears in no file outside the four it enumerates."

**Correction to the dispatch:** these are not "two in the test suite plus one you already found."
One lives in `check-state.sh` and one in `validate-digest.py` — both **production** code, not
tests — and one in `test-validate-digest.py`. `test-check-state.py`'s two reworded INV-11 sites use
a **different**, non-self-referential phrasing ("the removed completed-run invariant made exactly
this a violation") and do not exhibit this pattern at all. Verified by grepping all four files for
`task's verify` and `SC-01's sweep`; zero hits in `test-check-state.py`.

**Ruling: low-severity, non-blocking, but real — a comment that rots on merge, not house style.**
`this task's verify:` and `SC-01's sweep` are deictic pointers to a **one-time, uncommitted** check —
the BRIEF's own `## Verification gaps` section says exactly this of `evidence: command` clauses:
"nothing re-runs them after this feature ships... the surfaces they guard are deleted, not
maintained." Concrete failure scenario: a maintainer six months from now edits `validate-digest.py`
for an unrelated reason, reads "this task's `verify:` asserts that spelling appears nowhere in this
file," and reasonably infers an ongoing, automated check backs that sentence. None does — the grep
that "asserts" it ran once, by hand, during FEAT-08's QA, and no committed test re-runs it. If a
future comment reintroduces the literal string, nothing catches it, and the comment's own claim about
itself is now false. Contrast with the codebase's actual durable-pointer convention — a `DEC-NN`
citation, which resolves forever in `docs/harness/DECISIONS.md`. Non-blocking because the underlying
safety property (removal is safe; unknown keys are ignored) is independently true regardless of the
comment's wording, and comments never gate — but worth a follow-up pass replacing the self-reference
with a `DEC-178` pointer if this file is touched again.

**Minor, info-level:**
- `.claude/skills/harness/SKILL.md` (T-06): a double blank line survives at the join where the
  "Cost never stops work..." paragraph was deleted, between `budgets.max_total_cycles`. and `##
  The question round-trip`. Cosmetic only; not enforced by any linter in this repo.

## Plain-word `cost` sweep — run myself, case-insensitive, `--exclude-dir=worktrees`

Restricted to files this diff actually touches (git-grepped each individually at `942505e`), the
plain word "cost" appears only in already-vetted, in-scope-and-correct locations: `SKILL.md`'s three
protected context-expense lines, `harness-team/SKILL.md`'s protected English uses, `check-state.sh`'s
three legitimate uses (the whitelist comment, an unrelated "costs nothing" idiom, an unrelated
duplication-audit note), `test-check-state.py`'s `case_k` fixture text (all legitimately about the
`cost:` key it tests), and `BUILD.md`/`DECISIONS-INDEX.md`/`SPEC.md`'s historical/marked prose —
every SPEC.md hit matches T-10's fifteen-entry enumerated allow-list, confirmed by running the exact
`verify:` command myself. **No plain-word site was missed** — I found nothing analogous to the two
sites A-3 already caught (both of which are correctly fixed in this diff, re-verified directly:
the worked-briefing-example `Cost` row is gone with exactly one blank line remaining; the
cycle-counter-ownership line no longer carries the dead cost analogy).

## Open questions

- { id: Q1, question: "feature.yaml:9-10 (FEAT-08's own, not-yet-shipped) still carries cost_usd/max_cost_usd — REQ-02/REQ-09 forbid a live max_cost_usd budget anywhere; the out-of-scope ruling only covers shipped feature.yaml. Disposition is the orchestrator's, not mine.", blocking: false }
