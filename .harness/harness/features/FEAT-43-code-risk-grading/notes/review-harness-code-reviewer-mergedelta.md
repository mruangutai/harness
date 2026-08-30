# Merge-delta code review — 1d292c2 (cbdadef + 6d6d1ce)

**BLUF: no blocking defects.** Both hand-resolved conflicts are correct in both locations they
live, the drift-detector programmatically agrees, and `validate-digest.py`'s automatic merge does
NOT interact with FEAT-43's SEC-01 binding, `n_a` decision path, `resolve_reviewed_commit`,
`severity_max` enum, or reviewer schema — the new code lives in a structurally disjoint branch of
`hook_mode()` that never calls `validate()` with anything the merge changed. Item 5's four
combination checks all pass.

## Item 1 — the two hand-resolved conflicts

**(a) `.harness/harness.json` `test_kinds`.** `context-watch` is absent from every detect glob
(`harness.json:118-140`). `integration.detect` explicitly lists `test-code-grade-cli.py`
(`harness.json:119`, confirmed by raw read); `unit.detect`'s catch-all
`.claude/skills/harness/bin/test-*.py` covers `test-code-grade.py`/`test-gate-policy.py`, and
neither name appears in `integration.detect`'s explicit list (verified by direct grep).

**(b) `run-unit-tests.sh` `UNIT_SCRIPTS`/`INTEGRATION_SCRIPTS`.** No `context-watch` entries in
either array (`run-unit-tests.sh:30-31`, raw read). `test-code-grade.py` and `test-gate-policy.py`
sit in `UNIT_SCRIPTS`; `test-code-grade-cli.py` sits in `INTEGRATION_SCRIPTS`.

**Subtle half — kind-drift check, run directly, not adopted:**
```
$ .agents/skills/harness/bin/run-unit-tests.sh --check-kinds
check-kinds: the script arrays and test_kinds.integration.detect agree.
EXIT STATUS: 0
```
This is the script's own built-in comparator (`run-unit-tests.sh:82-131`): every
`INTEGRATION_SCRIPTS` name must appear as the literal path in `integration.detect`, and no
`UNIT_SCRIPTS` name may appear there. Exit 0 over the merged config proves every FEAT-43 test is
registered in the kind whose detect glob actually matches it — matrix coverage is not silently
voided.

**Whole-tree sweep for `context-watch`:** every remaining hit is historical narrative, not live
wiring — `DECISIONS.md`'s own retirement entries (documenting FEAT-44's removal, correctly present
tense), FEAT-31's own archived feature directory (its subject *was* named
`orchestrator-context-watch`), `feature_schema.py`'s exempt task-count map keyed by that feature
ID, `test-orchestrator-playbook.py`'s absence-assertion (`"context-watch.py" not in text`, which
is the test proving absence, not a live reference), and one explanatory comment in
`harness-hooks.ts` about a naming convention. `.claude/settings.json`'s `PostToolUse` hook array
was scanned programmatically (parsed JSON, checked every `hooks[].command` string) — zero
`context-watch` commands registered. `git ls-files | grep -i context-watch` returns only
`FEAT-31-orchestrator-context-watch/` feature-history paths (expected, archived). The only
filesystem trace of the deleted `.py` files is an untracked, gitignored `__pycache__/*.pyc` —
harmless build cruft, confirmed absent from `git ls-files`.

## Item 2 — `validate-digest.py`'s automatic merge (highest-risk item)

Diff `baa96b7e..HEAD` on the file: 27 insertions / 7 deletions, confined entirely to lines
1392–1462 inside `hook_mode()` — the T-09/#551 dispatch-claim release logic (`_reg.release()`,
`_reg.live_children()`, `_reg.release_cmd()`), threading OMP's `harness_feature`/
`harness_agent_id`/`harness_job_id` payload fields through as new keyword arguments. This is
main's own #551 registry work, not a FEAT-43 concern.

**Ruling: NO interaction with SEC-01, the `n_a` path, `resolve_reviewed_commit`,
`severity_max`, or the reviewer schema.** Traced by anchor:

- `resolve_reviewed_commit` (`:541`), `code_grade_bound_to_review` (`:861`, SEC-01's binding),
  `_derived_reviewed_python_change` (`:637`) and the `n_a` branch (`:1137`, inside `validate()`)
  are all called *only* from `validate()`. The merged block never calls `validate()` — it operates
  exclusively on the `inflight_registry` module (`_reg`), imported and used solely for claim
  release/child-liveness, a separate file and separate concern.
- The new locals `_feature`/`_agent_id`/`_job_id` are scoped inside `hook_mode()`'s registry
  branch and are never passed to `validate()`. The call site itself, `errs = validate(agent, text)`
  at `validate-digest.py:1482`, is untouched by the diff — same two positional args as before.
  `feature_dir` (validate's own parameter, an unrelated filesystem-path concept used for
  `_read_review_sha`) still defaults to `None` and self-resolves exactly as before.
- `severity_max`'s `SEV` list (`:36`) and the `reviewer` schema entry (`:194`,
  `{"severity_max": set(SEV), ...}`) are module-level constants the merged code never reads or
  writes.
- Signature check (not requested but load-bearing for "does this crash and silently disable the
  feature"): `inflight_registry.py`'s `release(root, agent=None, feature=None, claim_id=None,
  agent_id=None, job_id=None)`, `live_children(root, dispatcher, now=None, session=None,
  feature=None)`, `release_cmd(root, agent, feature)` all match the merged call sites' keyword
  names exactly — no `TypeError` risk, so no accidental fail-open into "the release step
  swallowed an exception it shouldn't have."
- The two-step "release-then-validate, `return 2` possible before `validate()` runs" control flow
  itself predates this merge (present already at `baa96b7e`, per the diff hunks modifying
  existing lines rather than inserting new blocks) — not a new ordering risk introduced here.

**`test-validate-digest.py` (+3/−1):** the entire diff is inside `run_t09()`'s `claims()` helper
(`:1153-1156`), adapting it to `inflight_registry`'s new `{"claims": [...]}` shape. `run_t09` is
the #551 claim-release test, hundreds of lines away from every SEC-01 test function
(`check_review_sha_binding`, `check_derived_base_range`, `check_no_merge_base`,
`check_unresolvable_default_branch`, etc., all `:1796` onward). Zero overlap — the new assertions
neither constrain nor contradict FEAT-43's. (SEC-01's own behavioural re-run is the security
reviewer's independent job, not duplicated here.)

## Item 5 — the combination

**(a) `severity_max` enum, four templates × two trees, read directly, file by file:**

| File | Line | Enum text |
|---|---|---|
| `.omp/agents/harness-validator-lead.md` | 107 | `severity_max: info\|low\|med\|high\|critical` |
| `.omp/agents/harness-security-reviewer.md` | 94 | `severity_max: none\|low\|med\|high\|critical\|n/a` |
| `.omp/agents/harness-code-reviewer.md` | 85 | `severity_max: none\|low\|med\|high\|critical\|n/a` |
| `.omp/agents/harness-ui-reviewer.md` | 104 | `severity_max: none\|low\|med\|high\|critical\|n/a` |
| `.claude/agents/harness-validator-lead.md` | 102 | `severity_max: info\|low\|med\|high\|critical` |
| `.claude/agents/harness-security-reviewer.md` | 93 | `severity_max: none\|low\|med\|high\|critical\|n/a` |
| `.claude/agents/harness-code-reviewer.md` | 84 | `severity_max: none\|low\|med\|high\|critical\|n/a` |
| `.claude/agents/harness-ui-reviewer.md` | 103 | `severity_max: none\|low\|med\|high\|critical\|n/a` |

All eight present, and each `.omp`/`.claude` pair spells the enum identically. `SEV =
["none","low","med","high","critical"]` (`validate-digest.py:36`) matches the three actual
reviewer templates exactly; `validator-lead`'s `info|…` line is unenforced documentation prose —
`lead`'s digest schema (`validate-digest.py:207-213`) carries no `severity_max` field at all, so
that spelling is not code-gated and is a pre-existing (not merge-introduced) inconsistency, out of
scope for this narrow review.

Confirmed this is survival, not luck: `git diff baa96b7e..HEAD --stat` over `.omp/agents` and
`.claude/agents` shows 15 files in `.omp/agents` each with exactly **`+1` line** — a `blocking:
true` frontmatter key added by main (OMP-native runtime field, e.g. `harness-code-reviewer.md`,
`harness-qa.md`) — and **zero** files touched under `.claude/agents`. The enum body text is
therefore byte-identical to `baa96b7e` in all eight files; the frontmatter schemas differ by
design between the two trees (`.omp` uses `spawns`/`model: '@review'`/`thinking-level`/`blocking`;
`.claude` uses `tools`/`color`/`model: sonnet`/`effort`), so a field present only in `.omp`'s
runtime frontmatter is expected, not drift.

**(b) Adapter sync:**
```
$ python3 .claude/skills/harness/bin/sync-agent-adapters.py --check
EXIT STATUS: 0
```

**(c) `test_kinds` classification SC-17 derives from.** `code-grade.py:48-52` reads
`.harness/harness.json`'s `test_kinds`, matches a file against every kind whose `status ==
"active"` using `detect`/`exclude` fnmatch globs. Both `unit` and `integration` are still
`"status": "active"` post-merge (confirmed in the same JSON dump used for Item 1), and their
`detect` globs are the ones verified intact and drift-free above. SC-17's per-surface bar
(production vs. test) resolves through this same path — intact.

**(d) Reachability sweep.** Main also rewrote `dispatch-guard.sh` (+96/−, mostly rewrite),
`inflight_registry.py` (728-line diff), and added `check-omp-port.py` (+22). Grepped FEAT-43's own
untouched source set (`code_grade.py`, `code-grade.py`, `gate_policy.py`, `test-code-grade.py`,
`test-code-grade-cli.py`, `test-gate-policy.py`, `check-plan-routes.py`,
`test-check-plan-routes.py`) for any reference to `inflight_registry`, `dispatch-guard`, or
`check-omp-port`: zero matches. No reachability from main's rewritten surfaces into anything
FEAT-43 depends on.

**Independent confirmation of the orchestrator's byte-untouched claim** (not adopted on faith):
```
$ git diff --exit-code baa96b7e HEAD -- code_grade.py code-grade.py gate_policy.py \
  test-code-grade.py test-code-grade-cli.py test-gate-policy.py check-plan-routes.py \
  test-check-plan-routes.py harness-code-review/SKILL.md harness-code-risk-grading/SKILL.md \
  glossary.md
EXIT-CODE-RESULT: 0
```
Confirmed: zero diff, all eleven paths byte-identical.

## What I did NOT cover

- Main's own content was **not** re-reviewed on its merits — the #551 registry rework in
  `inflight_registry.py`/`dispatch-guard.sh`/`check-omp-port.py`, the OMP identity threading in
  `validate-digest.py`'s `hook_mode()`, and the `blocking: true` frontmatter additions are main's
  own already-reviewed work. I traced their *reachability* into FEAT-43's surfaces only.
- The eight already-closed FEAT-43 defects were not re-opened.
- No canonical/project-wide suite was run; only targeted commands (`--check-kinds`,
  `sync-agent-adapters.py --check`, scoped `git diff --exit-code`) quoted above.
- SEC-01's behavioural discrimination (forged-range rejection) was intentionally left to the
  sibling security reviewer's independent run, per the dispatch — I performed the code-reading
  half only.
- No edits, no commits; working tree confirmed byte-identical to the merge except this artifact,
  HEAD unmoved at `1d292c2`.

```yaml
VERDICT: PASS
DIGEST:
  headline: Both conflict resolutions verified correct in both locations; validate-digest.py's automatic merge does not reach any FEAT-43 symbol; adapter sync and test_kinds classification both intact.
  severity_max: info
  findings: 0
  must_fix: []
  spec_violations: []
  reviewed: "6d6d1ce..1d292c2 (merge 1d292c2, parents cbdadef + 6d6d1ce)"
  human_commits_in_scope: [1d292c2b2e22486fd7ad47fa9021ddec880dabcb]
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-43-code-risk-grading/notes/review-harness-code-reviewer-mergedelta.md
```
