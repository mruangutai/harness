# Code review — BUG-1071 era guard — review_sha bf12a96b (base 75daa3bb)

## Stage 1 — spec compliance: PASS

Spec = `issue://1071` + `notes/handoff-plan.md`. Diff is exactly the two named files
(`check-state.sh` +37, `test-check-state.py` +104/-2) — matches the Working Set precisely, no
scope creep.

- **Trust claims re-verified, not trusted.** Ran `bash check-state.sh` on the real tree:
  exit 0, 0 `VIOLATION` lines, 32 `INV-32:` note lines (31 "before the panel shipped" + 1
  "approval.date is missing" for `FEAT-40-harness-writes-done`). Exact match to both
  `handoff-plan.md`'s Trust and `handoff-build.md`'s claimed evidence. Ran
  `test-check-state.py`: 151 `ok` / 0 `FAIL` / exit 0 — exact match.
- FEAT-45's own plan (signed 2026-08-30) is exempted with a note, as required — confirmed in
  the live output.
- **Dead ends avoided, confirmed by diff + grep:** no `plan.yaml` anywhere is touched (diff
  stat is 2 files, both under `bin/`) — no backfilled panel blocks. `grep -n "_is_shipped"
  check-state.sh` → no matches — no grandfathering. Post-era plans missing a `panel:` block
  still `bad.append(...)` (unchanged code path at `check-state.sh:218-220`, confirmed by
  `case_inv32_era_boundary_is_exact` going red-after) — INV-32 was not downgraded wholesale.

No omission, no mismatch against the issue's stated fix (key on `approval.date`; pre-era and
undated both `warn`+`continue`; everything else falls through ungraded... i.e. still graded).

## Stage 2 — code quality: PASS with notes (severity_max: med, must_fix: none)

### Q1 — hardcoded `INV32_ERA_START` — MED

`check-state.sh:199`. The literal `"2026-08-31"` is this repository's own bootstrap date
(day after FEAT-45's signature), embedded in code the dispatch states ships to every onboarded
repository. Concrete scenario (converges independently with QA's mutation report): a
different/forked repo whose own INV-32 mechanism arrives on a different historical date —
which has no relationship to `2026-08-31` — gets graded against a boundary that means nothing
locally. A plan there signed `2026-11-01`, genuinely pre-panel for *that* repo, is wrongly
flagged `VIOLATION` because `2026-11-01 > 2026-08-31` lexicographically. Recommend keying off
something the target repository can verify itself (the commit introducing the `INV-32` marker
in its own `check-state.sh` history, or a value stamped into `.harness/harness.json` at
onboarding/upgrade time) rather than a shared literal.
Caps at MED, not high: nothing exploits this today (no second repo has pulled this diff yet),
this repository's own future plans are all correctly graded going forward, and the file's
existing convention (INV-30/INV-31) already hardcodes comparison literals the same way — this
isn't a new pattern, it's an existing one applied to a fact that happens to be less portable
than the others. No separate finding on hoisting the constant — nothing else in this file
centralizes its per-invariant literals either (`expected_readers` a few lines below is inline
too), so this isn't a deviation from house style.

### Q2 — undated `approval.date` fail-open — MED (verified live, not privilege escalation)

`check-state.sh:200-210`. Grepped the whole script and the loader for any other place
`approval.date` is required on an approved plan: **none exists.** The only other approval
check (`check-state.sh:158-164`, INV-3/4/5) validates `approval.status` only.
`harness_yaml.load_plan`'s `REQUIRED_TASK_FIELDS` (`harness_yaml.py:288`) governs task shape
only, never `approval`. `templates/plan.yaml:38-40` shows `date:` as a field with no loader
enforcement.
**This is live, not theoretical:** `FEAT-40-harness-writes-done`'s real `plan.yaml` has
`approval: {status: approved}` with no `date` key at all, and the live run reproduces exactly
the predicted note — that plan is permanently exempted from INV-32 today, with only a `note`,
never a `VIOLATION`, and nothing will ever force it closed.
Severity caps at MED rather than high: independently spot-checked `check-domain.sh:537`
(`approval_guard`, "DENY a governed agent's write that would change a fragment the main
session owns... exempt BY THE MECHANISM") — the `approval:` fragment is a main-session-only
write channel. The same actor who could omit `approval.date` to dodge grading is already
unrestricted from fabricating a complete, INV-32-passing `panel:` block directly, so the
undated-omission path grants no new capability — only a quieter, cheaper route to an outcome
already reachable. It is a real audit-integrity gap worth closing, not a security-boundary
break.
Recommend: make missing/malformed `approval.date` a hard `bad` for any *newly*-signed
approval (distinguishable from the 32 legacy pre-2026-08-31 plans by date), independent of
the era question, so an approved plan can never permanently escape grading by omitting one
field.

### Warn-message actionability — LOW

`check-state.sh:207-209`. The undated-approval note names the defect ("`approval.date` is
missing or malformed") but not the remedy — no field path, no expected format — unlike
sibling actionable notes in this file (INV-28, INV-21, INV-22 each state a concrete fix). An
operator scanning 32 `INV-32:` lines at once has nothing in the string itself to act on.
Non-blocking; exit code is unaffected either way.

### Q4 — `INV32_ERA_START` reassigned per loop iteration — INFO, no finding

`check-state.sh:199`. A literal string reassigned identically on every iteration of
`for feat, doc in plan_docs.items()`. No cross-iteration state exists for it to corrupt, and
nothing in the loop body depends on it varying — there is no scenario under which this changes
behaviour. Readability nit only (would read cleaner hoisted above the loop), and not a
deviation from this file's own conventions (other per-invariant literals, e.g.
`expected_readers`, are inline too).

### Q5 — post-era plan with `panel:` block, coverage — none found

For `signed >= INV32_ERA_START` both era-guard conditions are False and control falls straight
through, unchanged, to the pre-existing panel-check code at `check-state.sh:217+` — the guard
is a behaviour-preserving no-op past the boundary. This is already exercised: `_inv32_plan()`'s
`date` parameter defaults to `"2026-08-31"`, a literal that was present verbatim
(`"date": "2026-08-31"`) in the dict *before* this diff too (confirmed via
`git diff 75daa3bb..bf12a96b`) — so every pre-existing `case_inv32()` sub-check (open finding,
resolved, rulings, readers, mutant-discrimination) and `case_inv32_unrated_severity_fails_closed`
already runs a full panel-grading pass at exactly the boundary. The comparison is a monotonic
string ordering, so "graded at the boundary" generalizes to "graded at any later date." No
post-era-plan-with-panel-block exists whose behaviour this guard changes untested.

### `case_inv32_era_guard_is_load_bearing` — code_grade: grade_2, MED, reasoned

`test-check-state.py:3172`. `code-grade.py --base 75daa3bb --head bf12a96b`: CYCLOMATIC 6,
COGNITIVE 7, ABC 30.3, bar 3, RESULT FAIL (grade 2, non-blocking). Reasoned: this is a
self-contained mutation-test helper — split the source on named markers, assert the split
materially changed the text, write+chmod the mutant, run real vs mutant against the same
fixture, assert on violation-line divergence plus absence of a traceback, clean up in
`finally`. Each branch is a distinct correctness check a mutation test needs to be trustworthy,
not incidental complexity, and it matches the shape of its unmodified sibling
`_inv32_mutant_is_discriminating` a few dozen lines above. Not a should_fix.
All 5 other changed/added functions (`_inv32_violations`, `_inv32_notes`,
`case_inv32_pre_era_is_exempt`, `case_inv32_era_boundary_is_exact`,
`case_inv32_undated_approval_warns`) grade 4, PASS.

### Mechanics — continue placement, lexicographic safety, regex — all correct

`INV-32`'s `for feat, doc in plan_docs.items()` (`:176-216`) is its own dedicated loop,
separate from the INV-3/4/5 loop above it — the two `continue`s inside the era guard only
short-circuit the *rest of this same loop's* INV-32-only checks (panel/rulings/readers) for
one plan; no other invariant is skipped. The `re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", ...)`
correctly rejects non-zero-padded input like `2026-8-31` (requires exactly two digits for
month/day), routing it to the malformed-warn branch instead of a broken lexicographic compare
— every string that passes the regex sorts identically to chronological order, so
`signed < INV32_ERA_START` is correct for all values reaching it.

### Q3 (assertions bind what they name) — verified by mutation, not by reading

Ran the full suite (151/151) and directly observed
`ok - INV-32 era guard is load-bearing (real=0 mutant=1 violations)` — the shipped test's own
mutation (excising the marked region) executed and discriminated. `handoff-build.md` states the
four new cases were RED first, for the intended reasons, before the guard existed; QA's
independent 7-mutant table (`notes/qa-mutation-verification.md`) confirms every named behaviour
reddens under its corresponding defect with no coverage hole. Not independently re-derived by
me beyond running the suite and reading the confirmed evidence — no reason to.

## Cross-review note

Security review (`notes/review-harness-security-reviewer-bug1071.md`) and QA
(`notes/qa-mutation-verification.md`) reached the same Q1/Q2 evidence independently (grep +
live-tree confirmation); this review's severities for Q1/Q2 converge with security's (MED/MED)
after independently spot-checking the `approval_guard` mechanism they cited. UI review's F1
(warn-message clarity, low) is adopted here rather than re-derived, since it directly answers
this dispatch's "would the warn messages let an operator act" question.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Spec compliance is clean; two MED code-quality findings (a repo-history literal baked into shipped gate code, and a live-but-unescalated approval.date fail-open confined to the already-fully-trusted approval writer) plus one LOW message-clarity gap — none gate."
  stage1: PASS
  stage2: PASS
  severity_max: med
  findings: 6
  must_fix: []
  spec_violations: []
  reviewed: "75daa3bb..bf12a96b"
  human_commits_in_scope: []
  code_grade:
    - { qualname: "case_inv32_era_guard_is_load_bearing", path: ".claude/skills/harness/bin/test-check-state.py", line: 3172, result: grade_2, severity: med, driver: abc, reasoned: true }
  open_questions:
    - { id: Q1, question: "Should INV32_ERA_START be derived per-repo (git history of the INV-32 marker's introduction, or a .harness/harness.json field stamped at upgrade time) instead of a shared literal, given check-state.sh is distributed to onboarded repositories with independent update cadences?", blocking: false }
    - { id: Q2, question: "Should a missing/malformed approval.date on a newly-signed (post-2026-08-31) approval be a hard `bad`, closing the accidental-omission gap while leaving the 32 legacy plans on today's warn treatment?", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/BUG-1071-inv32-era-guard/notes/review-harness-code-reviewer-bug1071.md
```
