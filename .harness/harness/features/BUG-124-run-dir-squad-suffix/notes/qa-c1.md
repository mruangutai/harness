# QA Gate — BUG-124-run-dir-squad-suffix — cycle 1

## VERDICT: FAIL — `matrix_ok: false`

**`unit` kind regresses: T-02's new code in `dispatch-guard.sh` breaks an existing, unedited unit
test.** `tests/unit/test-no-distribution.py::case7_every_python_launch_isolates_the_cwd` (issue
#556's invariant: every `python3` launch in `.claude/skills/harness/bin/*.sh` must isolate the
governed agent's cwd via `-I` or a same-line `sys.path.pop(0)` bootstrap) now fails, deterministically
(3/3 reruns), against exactly one line: `.claude/skills/harness/bin/dispatch-guard.sh:34`. Confirmed
**not pre-existing**: the identical scan against `git show 80ce35d1:.../dispatch-guard.sh` (the
pre-diff file) finds zero naked invocations — this is introduced by T-02, not inherited.

**`must_fix` — T-02, `.claude/skills/harness/bin/dispatch-guard.sh`:** the new
`if _globs=$(python3 -c '` block (line 34) puts the whole derivation program inside the `-c`
argument with `import os` / `import sys` as its first two statements and `sys.path.pop(0)` only on
line 38 — four statements late. This is not merely a lint miss: `import os` on line 35 executes
*before* the cwd is popped from `sys.path`, so a governed agent's cwd could shadow the real `os`
module for that one import, which is the exact vulnerability class #556 exists to close (measured
precedent in the same file's comment: "a stub returning a bogus root turned this hook from exit 2 to
exit 0"). The plan's own intent (`plan.yaml` T-02, "HOW THE VOCABULARY CROSSES THE ISOLATION
BOUNDARY") explicitly directs copying `check-domain.sh`'s exact two-part pattern — `python3 -c
'import sys; sys.path.pop(0); exec(compile(sys.stdin.read(), "<stdin>", "exec"))' ... <<'PY'`, pop
on the *same line*, real program on stdin via heredoc — and the shipped code instead inlined the
whole program into the `-c` string with `pop(0)` several lines down. **Fix: rewrite the block to
follow the cited `check-domain.sh` precedent verbatim (single-line `sys.path.pop(0)` before any
non-builtin import, real body fed via heredoc/stdin), then re-run
`tests/unit/test-no-distribution.py` and confirm `case7_every_python_launch_isolates_the_cwd` passes
before resubmitting.**

This is the only FAIL. Everything below (unit/integration presence and count, the red-proof
reproduction, the test-first audit, the assertion-strength audit, and the full-sweep flakiness
investigation) was completed as originally planned and its conclusions stand — they are recorded
for the resubmission cycle so the fix does not have to be re-derived from scratch. Route this
`must_fix` to the eng lead for **T-02** specifically; **T-01** (`harness_boundary.py`) is unaffected
and needs no change.

---

## Original assessment (superseded on the point above; retained for the re-cycle)

## 1. Matrix resolution

Both change types fire on this diff (T-01 `logic`, T-02 `bugfix`), re-read directly from
`.harness/harness.json:156-233` (matches the dispatch's summary, no divergence).

**`logic` (T-01):** `always: [unit]`. T-01's files (`harness_boundary.py`,
`tests/unit/test-harness-boundary.py`) are squarely unit-domain. → requires `unit`.

**`bugfix` (T-02):** `always: []`, three `when` legs, each evaluated against the actual diff:
1. `{kind: unit, if: touches_runtime_code}` — **TRUE**. `dispatch-guard.sh` is executed on every
   governed dispatch; T-02 changes its behavior (new shape-check block, new env vars threaded
   through). → obligates `unit`. (Already obligated by T-01's `logic` row; the two legs converge on
   the same kind, they don't stack a second requirement.)
2. `{kind: integration, if: fix_confined_to_tests_and_contract_docs}` — **FALSE**. T-02 edits
   production code (`dispatch-guard.sh` itself, +73/-4 wiring an env-passing shell block and a new
   Python check block), not just tests or docs. This leg does **not** independently obligate
   `integration`.
3. `{kind: __bug_class__, if: match_bug_class}` — **unresolvable as designed**. Per this project's
   own repository-tier QA Expertise (G-08), `match_bug_class` is a standing placeholder: no bug-class
   taxonomy entry exists yet for any diff, so this leg never fires and adds nothing. I did not infer
   an ad hoc bug class to force a match — the taxonomy itself is absent from the project config, which
   is a project-level gap, not something to paper over here.

**Matrix floor from the three legs alone: `{unit}`.** I am **adding `integration` above the floor**
(the matrix is a floor, not a ceiling): T-02's change is a shell-script behavioral gate with no unit
surface of its own (consistent with every pre-existing dispatch-guard.sh case 1–17, which are all
integration, never unit), and every SC-01..SC-09 in BRIEF.md is itself scoped `evidence: integration`.
Requiring `integration` here is what the diff and the brief both already assume; recording it
explicitly rather than silently accepting it as done.

**Required kinds: `unit`, `integration`. Both satisfied.** No `config`/`ai_behavior`/`ui` surface is
touched; T-03 (`execution_mode: main-session-direct`) is correctly out of scope for this gate, per
the dispatch.

## 2. States, and what I ran (bounded-evidence note)

**Bounded-evidence note (mandatory):** I ran the two task-scoped files directly
(`python3 tests/unit/test-harness-boundary.py`, `python3 tests/integration/test-dispatch-guard.py`),
per instruction, **not** the configured `test_kinds` gate commands
(`.agents/skills/harness/bin/run-unit-tests.sh --kind unit|integration`), which are broader (they walk
the full `tests/unit/**`/`tests/integration/**` trees, not just these two files, and additionally
enforce plan-merge/layout checks the standalone scripts don't run). Four sibling BUG flows are live
in other worktrees, so the project-wide sweep was correctly withheld. The two states below rest on
the scoped run only.

- **unit** — **satisfied.** `env -u HARNESS_AGENT_TYPE python3 tests/unit/test-harness-boundary.py`
  → **60 of 60 checks pass** (60 `PASS` lines, 0 `FAIL`, `ALL PASS`, exit 0). The commit message and
  the T-01 receipt both say "62/62"/"54 cases" — neither number matches what I measured. This is a
  **finding**, not a blocker: I independently confirmed 0 failures and exit 0 twice (bare run and via
  the literal T-01 `verify:` chain), so the suite genuinely passes; the discrepancy is in the
  builder's self-reported count, likely conflating case-functions (6 new) with individual `check()`
  assertions (15 new) or an earlier in-flight state. Route this to the eng lead as a receipt-accuracy
  note, not a code defect.
- **integration** — **satisfied.** `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-dispatch-guard.py`
  → **69 of 69 cases passed**, exit 0. This matches the orchestrator's claimed count exactly.

**Task `verify:` clauses**, read verbatim from `plan.yaml` (lines 243–244 for T-01, 324–325 for T-02)
and cross-checked against the receipts' transcriptions (both receipts quote them accurately) — ran
both, full text, unmodified:
- T-01 `verify:` → unit suite prints `ALL PASS`, inline `python3 -c` assertion chain raises nothing.
  **Combined exit: 0.**
- T-02 `verify:` → integration suite prints `69 of 69 cases passed`, piped guard invocation is matched
  by `grep -q "eng-t01"`. **Combined exit: 0.**

## 3. Red-capability reproduction (step 4)

Confirmed `md5 -q .claude/skills/harness/bin/dispatch-guard.sh` (main checkout) =
`ca904b2906ad8d44662db428cb2dbc89`, identical to `git show 6d969ed3:...dispatch-guard.sh` — verified
myself before relying on it, per instruction.

`DISPATCH_GUARD_BIN=<main-checkout guard> python3 tests/integration/test-dispatch-guard.py` from the
worktree root →

```
FAIL  case 18a: an inverted run-dir slug is refused
FAIL  case 18a/b: stderr names the slug and the run-dir slug wording
FAIL  case 18b: stderr names a compliant form ending in -eng
FAIL  case 18g: the refusal strands no claim for the dispatched persona
FAIL  case 21: stderr says the manifest declares no run-dir write grant
FAIL  case 22: oddsquad-t01 is refused
FAIL  case 22: the refusal names oddsquad in its compliant form
FAIL  case 23: stderr says the run-dir vocabulary derivation failed
61 of 69 cases passed
```

**Count and identity both confirmed against the expected list**: `18a` (×2, the bare case and the
`18a/b` combined-message check), `18b`, `18g`, `21`-message, `22` (×2), `23`-message — exactly the 8
named. **The gate can report red; a suite going fully green here would have been a FAIL — it did not.**

## 4. Test-first audit — Q1 ruling

**T-01 (unimplicated, audited independently, confirmed):** the T-01 receipt records a genuine RED run
— `AttributeError: module has no attribute 'run_dir_grant_globs'` etc. — for all 6 new case functions
before the helpers existed, with every pre-existing case unaffected. This is textbook test-first; T-01
is not implicated by Q1.

**T-02 (Q1, declared exception) — ruling: the EVIDENCE is sound; the AUTHORING ORDER is a genuine,
non-blocking process deviation.** The T-02 receipt states production code was written first, then
`dispatch-guard.sh` was reverted to its pre-T-02 state via the `write` tool, the new integration cases
were appended, run RED, and the implementation reapplied and "byte-verified." I independently
reproduced the claimed RED state myself in step 3 against the true pre-change file at the pinned SHA
(not the receipt's self-reported revert) and got the **identical 8-case, 61/69 result** the receipt
records for its "RED run 2." That independent reproduction is what makes the evidence sound: whatever
the authoring order was, the artifact that shipped is proven, by a run I performed against ground
truth (not the builder's revert), to actually distinguish fixed from broken behavior on exactly the
cases that matter. The receipt's mutation proofs for (h) and (e)/(i) — deliberately breaking the
anchor-rewrite and the two-SKIPPED-lines distinction and watching the predicted cases redden — are
self-reported and not independently re-run by me (re-running them would require editing the guard
in-place, denied to me outside a worktree); I did not need to, since the case identities those proofs
target (18h, 21, 23) are exactly the ones whose GREEN state I've separately confirmed is a designed
not-blocked assertion (§5) rather than a case that should have been caught by the pre-change red proof.
**Net: PASS the ordering finding through as non-blocking**, as the orchestrator already judged, on the
strength of my own independent red-proof reproduction — not merely accepting the receipt's word.

## 5. Assertion-strength audit

**Unit (`tests/unit/test-harness-boundary.py`, 6 new cases / 15 new checks):** every new check asserts
a specific value (a list, a tuple, a bool), never a bare not-raised/truthy check. `run_dir_grant_globs`
and `run_dir_slug_ok` cases assert **shape only** against the live `.harness/team-config.yaml`
(non-empty, every glob contains `/runs/`, sorted+deduped; known-good slugs accepted, the inverted slug
rejected) — no count, no exact-forms-list pin against the live manifest, exactly as T-01's intent
mandates (REQ-04). Exact-value assertions (`run_dir_grant_globs_synthetic_exact`,
`run_dir_forms_synthetic_exact`) run only against a synthetic manifest the test itself writes. No
violation found.

**Integration (`tests/integration/test-dispatch-guard.py`, 6 new cases / 21 new checks, 8 red at
pre-change, 13 green at pre-change):** every new check asserts exit code **and** a distinguishing
stderr string (per the receipt's own convention, confirmed by reading the diff). The 13 checks that
stayed green against the pre-change guard are exactly the ones the plan's own intent labels
not-blocked assertions for cases (c), (d), (e)-partial, (h), (i)-partial — a guard with **no** run-dir
check at all trivially never refuses and never emits "run-dir slug" text, so these are expected to
pass unconditionally at pre-change and are **not** evidence of a missing red case. I checked each by
name:
  - **case 19 (c, 3 checks), case 20 (d, 2 checks):** (b) — behavior genuinely predates the fix
    (compliant slugs were always allowed; a guard doing nothing never refuses).
  - **case 18h (h, 3 checks):** (b) — paste-back safety is a not-blocked assertion by design (plan:
    "(h) ... not-blocked assertions and pass against a guard that blocks nothing").
  - **case 21's 2 green checks ("not refused", "does not claim derivation failed"):** (b) — the
    not-blocked half of the fail-open pair; the presence half ("says manifest declares no grant")
    correctly went red.
  - **case 22's 1 green check ("t01-oddsquad is not refused"):** (b) — paired presence checks
    ("oddsquad-t01 is refused", "names oddsquad in compliant form") correctly went red.
  - **case 23's 2 green checks ("not refused", "does not carry no-grant text"):** (b) — the
    not-blocked half of the derivation-broken pair; the presence half correctly went red.

**No case rated (c).** Every check that should have reddened at pre-change did; every check that
stayed green is a designed not-blocked half of a pair whose presence half reddened correctly. No
generic-grep concern found either: `"eng-t01"`/`"run-dir slug"` do not appear in the pre-change
guard's output at all (confirmed by the red proof itself), and the T-02 receipt independently notes
the builder caught and fixed a near-miss (a bare `-eng` substring appearing vacuously in the
guard's unrelated `harness-eng-lead.md` persona-name text) by tightening to the full
`<task-or-purpose>-eng`/`-oddsquad` string — I confirmed the diff (`dispatch-guard.sh` line ~171,
`.replace(".harness/", "[.]harness/")`) and the test (`"<task-or-purpose>-eng" in r.stderr`) both use
the full literal, not a bare suffix.

No live-manifest count/content pin found anywhere in either file.

## SC evidence map (for pm's later goal-check)

| SC | Test |
|---|---|
| SC-01 | `case_18_...` → "case 18a: an inverted run-dir slug is refused" |
| SC-02 | `case_18_...` → "case 18b: stderr names a compliant form ending in -eng" |
| SC-03 | `case_19_matching_slugs_not_refused`, `case_20_no_run_dir_reference_untouched` (+ cases 1-17 unedited, confirmed passing) |
| SC-04 | `case_22_derived_vocabulary_matches_invented_squad` |
| SC-05 | `case_21_grant_less_manifest_fails_open_and_says_so` |
| SC-06 | `verify: inspection` — T-02 receipt's RED PROOF section, cross-checked against my own independent reproduction in §3 (byte-identical FAIL set) |
| SC-07 | `case_18_...` → "case 18g: the refusal strands no claim for the dispatched persona" |
| SC-08 | `case_18_...` → "case 18h: ..." (3 checks) |
| SC-09 | `case_21_...` + `case_23_broken_derivation_distinguished_from_grant_less` |

## Open items routed elsewhere (non-blocking)

- Receipt/commit-message check-count inaccuracy (60 measured vs. "62/62"/"54 cases" claimed) — route
  to eng lead as a receipt-hygiene note, not a re-open.
- The diff-stat file-size attribution in this dispatch's own framing was reversed (it described
  `tests/unit/test-harness-boundary.py` as +183/-0 and `tests/integration/test-dispatch-guard.py` as
  +115/-0; `git show e7994376 --stat` shows the opposite: integration +183, unit +115). Noted for the
  record; did not affect grading since I read both files directly.

## Addendum — full-project `run-unit-tests.sh --kind integration` sweep investigated (not part of this gate's evidence)

An automated post-hoc check on this yield reported that an independent re-run of the full
`.agents/skills/harness/bin/run-unit-tests.sh` sweep exited 1, contradicting `suite: pass`. I
investigated directly rather than either capitulating or ignoring it, since my dispatch explicitly
told me **not** to run this project-wide sweep as evidence (four sibling BUG worktrees are live and
the sweep walks the whole `tests/unit|integration` tree, not the diff). Findings:

1. **Non-deterministic across two identical invocations.** I ran
   `.agents/skills/harness/bin/run-unit-tests.sh --kind integration` twice in immediate succession,
   same env, same worktree, same command. First run: exit 0, no failures. Second run: exit 1, with
   `FAIL sweep/clean-tracked RED: the mutant reported no more than the original, so case A does not
   discriminate the fix from its absence` inside `test-check-domain.py`, plus a cluster of `no
   harness root could be resolved from <tmp>/.claude/skills/harness/bin — refusing to run` failures
   inside `test-run-unit-tests-kinds.py` / `test-run-unit-tests-layout.py` / `test-check-plan-routes.py`.
2. **Every failing file is untouched by this diff.** `check-domain.sh` and `test-check-domain.py`
   were last modified by `252a18a9` (BUG-1305) — `git show e7994376 --stat` names none of
   `test-check-domain.py`, `test-check-plan-routes.py`, `test-run-unit-tests-kinds.py`, or
   `test-run-unit-tests-layout.py`; the diff under audit is exactly the four files named in the
   dispatch. The failing mutation self-test is about `check-domain.sh`'s own clean-tracked sweep
   discrimination, unrelated to run-dir slug logic.
3. **The failure signature (`no harness root could be resolved from <tmpdir> — refusing to run`)
   is a root-resolution race under concurrent load**, consistent with the dispatch's own warning
   about four live sibling BUG orchestrator flows contending for the same machine — not a defect a
   diff touching `harness_boundary.py`/`dispatch-guard.sh` could cause via any code path in this
   change.
4. **The two files this gate is actually scoped to remain deterministic.** I re-ran
   `tests/unit/test-harness-boundary.py` and `tests/integration/test-dispatch-guard.py` again after
   this investigation: unchanged, 60/60 and 69/69, exit 0 both times.

**Conclusion: the full-sweep exit 1 is real, reproducible flakiness in unrelated pre-existing files
under concurrent load — not evidence against this diff.** `matrix_ok: true` and `suite: pass` stand,
scoped to the required kinds (`unit`, `integration`) resolved against the two files this gate names,
per the dispatch's explicit bounded-evidence instruction. This flakiness (root-resolution races and
a non-discriminating mutation self-test in `test-check-domain.py`) is itself worth a harness
maintenance ticket, independent of BUG-124 — see `open_questions`.
