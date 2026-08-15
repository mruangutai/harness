# Architecture review — FEAT-07 PLAN — harness-backend-dev

**BLUF.** The plan is sound on mechanism — every mechanical `verify:` claim I re-ran matched the
receipt table exactly, including the two hardest ones (T-01(ii)/(iii) and T-04's awk block). One
real design gap is unresolved and blocks signature: **§A, a three-way conflict that makes this very
dispatch impossible to return honestly after T-01.** Everything else is `med`/`low` — line-anchor and
precondition corrections PLAN should carry, not defects in the mechanism itself.

## must_fix

**F1 (§A) — after T-01, a non-task dev-persona dispatch has no legal `task_verify` value for
`VERDICT: PASS`.** Three things are each true and jointly impossible to satisfy:
1. `task_verify` is REQUIRED on the `dev`/`dev-ops` schema (SC-01) — cannot be omitted.
2. `task_verify: fail` or `n/a` + `VERDICT: PASS` is REJECTED, no carve-out (SC-02/SC-03) — cannot
   be honest, since a non-task dispatch (this one) has no `verify:` command to report on.
3. `.claude/settings.json`'s `SubagentStop` hook matcher is `"harness-.*"` — it fires on every
   `harness-backend-dev` stop, task or not (verified: grep shown in transcript). Cannot be escaped.
   `norm("harness-backend-dev")` → `"dev"`, which is in `GATE_FIELDS["dev"] = {"suite","task_verify"}`
   (`validate-digest.py:73`, and T-01 step 3 keeps it there) — so this is not hypothetical, it is the
   same shape `suite` already enforces on this exact dispatch today.
   Live counterexamples of the same shape: `harness-expertise` distillation dispatch, a
   `harness-systematic-debugging` debug-mode dispatch, any lead-issued investigation — none carries a
   `T-NN` or a `verify:` command. PLAN and BRIEF do not name this case anywhere (grepped for
   "non-task", "distillation", "debug-mode", "investigation", "no verify" — no hits outside T-02/T-05's
   task-dispatch language).
   This is a **design decision**, not mine to make: a fourth `task_verify` enum value for
   "not a PLAN task", or scoping `GATE_FIELDS`/the new fail gate to returns that declare a task id.
   Belongs to pm, raised as `open_questions`.

## med

**F2 (B1, T-01 step 5) — the insertion-point numeral is off by one, in the dangerous direction, but
T-01's own `verify:` self-detects it.** Measured: `validate-digest.py:485` is `continue` (closes the
`field in NULLABLE and val in PLACEHOLDER_UNSET` branch); `:486` is `if isinstance(allowed, set):`.
PLAN says insert "BEFORE the enum branch at `:485`" — read literally that places the new check
*inside* the placeholder branch it must sit outside of, where `suite: fail` (a non-placeholder string)
never enters, making the new gate dead code for the string-valued fields. **It is not silent**: T-01's
own clauses (ii) and (iii) in `verify:` would then stay at exit 0 instead of flipping to exit 1, so
`run-unit-tests.sh` and the task's own verify block catch it before the diff is signed off — this is
why it does not block signature. Fix in PLAN.md: state the insertion point as "immediately after the
`continue` at `:485`, before `if isinstance(allowed, set):` at `:486`" — not "before `:485`".

**F3 (§C, T-09) — PLAN:645 and PLAN:511-512's "no pre-existing drift" claim is false of `3bfedc9`,
and contradicts T-09's own intent clause.** Measured:
- `git show 3bfedc9:docs/harness/DECISIONS-INDEX.md` (committed) vs
  `python3 gen-decisions-index.py --stdout` (run against the unmodified `DECISIONS.md`) — **diff
  exit 1**, not 0. Only the `@NNNN` anchors differ (content-stripped diff is clean); `DECISIONS.md`
  itself is byte-identical to `3bfedc9` (`git diff --stat 3bfedc9 -- docs/harness/DECISIONS.md` empty).
  So the generator's own output never matched the committed index at the reviewed commit.
- The discrepancy is **not a uniform +6 shift** as PLAN's own prose frames it: DEC-118 committed
  `@2376` vs generated `@2382` (committed is *lower*); DEC-174 committed `@4680` vs generated `@4674`
  (committed is *higher*). Direction reverses — at least two independent edits, not one shift.
- The gen-vs-`docs/harness/DECISIONS-INDEX.md` diff in the *current working tree* is clean (exit 0) —
  someone ran the generator in write mode after `3bfedc9`, undeclared, which is the working-tree
  modification the review dispatch flagged.
PLAN:503-505 (T-09's own intent) already states the correct rule — "if the regenerated index differs
on any row other than the three new ones, that is pre-existing drift: report it, do not absorb it
silently" — which directly contradicts PLAN:645/511-512's "clean on arrival" claim. Both receipts were
measured against the corrected working tree, not `3bfedc9`. Fix: state the pre-existing drift as a
declared precondition of T-09 (fresh `3bfedc9` checkout would show `diff` exit 1 before T-09 touches
anything), and correct the diagnostic — a red result before any edit means pre-existing drift, not
"T-09 hand-edited."
**SC-12 still discriminates on its first half** (`grep -c '^- DEC-17[5-7] '` 0→3), but its second half
("re-running leaves the file unchanged") does **not** discriminate the thing T-09's own intent clause
demands — it goes green whether T-09 reports the pre-existing drift or silently absorbs it into the
same commit. Not a blocker; note it so T-09's revised verify checks the reporting, not just the
end-state hash.

## low

**F4 (B4, T-01 fixture anchors) — neither handed anchor set is fully accurate; the count of 7 is
correct.** Measured (`test-validate-digest.py`, unmodified at `3bfedc9`, confirmed via
`git diff --stat 3bfedc9`): dev-persona `case()` fixtures needing `task_verify` are at `:187`, `:290`,
`:582`, `:717`, `:951`, `:954` (all six match PLAN exactly) plus one inline dev digest constructed at
`:561-564` inside the DEC-156 file-shape test (PLAN says `:558` — that's the `_dec156_case(` call
line, not the digest text) — **7 total, count correct.** `DEV_NA` is defined at `:939`, not "near
`:943`" (PLAN) or `:943` (grilling note). The grilling note's whole anchor set (`:191/:294/:562/:586/
:721/:943`) is uniformly +4 off PLAN's and reproduces none of the measured `case()` lines — do not use
it as a cross-check. Give the corrected anchor list in PLAN.md so the human reading the diff has
something checkable: `187, 290, 561-564, 582, 717, 939(DEV_NA)/951/954`.

**F5 (T-01 step 1, the missing-field hint feeds §A) — `NULLABLE`'s own error message tells an agent
to write the one value that then gets rejected.** `validate-digest.py:468`: a missing `NULLABLE` field
gets the hint "`none` if genuinely not applicable." `"none"` is in `harness_yaml.PLACEHOLDER_UNSET`
(verified: `('none', 'null', 'n/a')`). After T-01, `task_verify` is in both `NULLABLE` and
`GATE_FIELDS`, so an agent that omits it, follows the hint, and resubmits `task_verify: none` +
`VERDICT: PASS` is rejected again by a *different* message — a two-round-trip loop under a blocking
`SubagentStop` hook. Same root cause as F1; worth a one-line carve in the hint text or in T-02's prose
once pm resolves F1.

**F6 (T-02/T-04 shared-file hazard) — confirmed benign today, but worth stating as a constraint.**
T-04's `awk '/^VERDICT: BLOCKED$/,/^artifact: none$/'` range depends on exactly one `^VERDICT:` line
in `harness-tdd-enforcement/SKILL.md` (currently true: `grep -c '^VERDICT:'` → 1). `validate()`
tail-anchors on the *last* `VERDICT:` match, so if T-02's REQ-08 append ever introduces a second
line matching `^VERDICT: BLOCKED$`, the awk range would extract the wrong span. Not a defect in
either task as specified — the receipt clause T-02 adds is prose, not a worked digest — but PLAN
should say explicitly that T-02's append must not introduce a second `^VERDICT:` line, since that is
exactly the hazard the awk switch (from `sed` line ranges) was built to dodge.

## info

**B5 — the widening's blast radius is exactly the 5 `GATE_FAIL_VALUES` entries and no more.**
`GATE_FAIL_VALUES.get(persona, {})` returns `{}` for `pm`, `reviewer`, `documentor`,
`visual-designer`, `lead` and `orchestrator` — none of them appear as a key in T-01's table, so none
of their fields (`severity_max`, `contract`, `sc_status`, `members`, `status`, etc.) are touched by
the new gate. The reviewer's `severity_max` stays governed only by the existing enum check.
`matrix_ok: 0` + `PASS` does not slip through either: the type-strict fail-gate comparison skips it
(`isinstance(0, bool)` is `False`), but it then falls into `allowed is bool` (`:504`) and is rejected
as "must be a bool, not int" — closed by a different clause, not a hole. BRIEF's 4-row
Behaviour-change table legitimately omits `dev.task_verify` and `dev-ops.task_verify`: those are
brand-new required fields (SC-01/SC-03), not fields that used to accept a fail value and now don't,
so there is no "accepted today" row for them to occupy.

**T-06's `awk` terminators all match** (`grep -nE '^- \*\*eng devs\*\*|^- \*\*qa:|^- \*\*dev-ops:|^- \*\*leads:'
docs/harness/SPEC.md` → 4 hits in order at `:1054/:1056/:1062/:1064`) — both ranges terminate on the
next bullet as PLAN assumes, not at EOF, so T-06's per-bullet counts cannot false-green on spillover.

**Low: T-02 and T-10's `verify:` prose claims placement it doesn't check.** T-02's `grep -c
'task_verify' >= 3` and T-10's `grep -c 'VERDICT: PASS is rejected'` are whole-file counts, but the
prose says "within the fenced ... DIGEST block." The counts still discriminate (0/1 → required
minimum), so this isn't vacuous — it just doesn't enforce the block-scoping the prose claims. One-line
fix if pm wants it tightened; not blocking.

**Deletion test on `GATE_FAIL_VALUES` as a second gate structure: passes.** `GATE_FIELDS` is
structurally incapable of seeing a real `fail` (only consulted inside the `NULLABLE`/placeholder
branch — D-01's own finding, verified at `validate-digest.py:477-481`), so a single merged table
can't answer both "declined to report" and "reported failure" without restructuring the whole
placeholder-branch mechanism. Deleting `GATE_FAIL_VALUES` reopens exactly the three holes fixtures
(g)/(h)/(9)(i)'s siblings pin. The two-table seam is a real drift surface (two persona-keyed tables
answering one question, `dev-ops` asymmetric across them) but PLAN's step (3) already mandates the
comment stating both axes, and a restructure of a DEC-174 file is not warranted for a smaller diff.

## Mechanical checks — verbatim results

All run from repo root against the current tree (`git diff --stat 3bfedc9` confirms only
`docs/harness/DECISIONS-INDEX.md` and `.harness/logs/2026-08-04.md` differ from `3bfedc9`; neither
affects any command below).

- `m` binding: `m = re.search(r"^\s*VERDICT:...", ...)` at `:432`, in scope through the whole function
  including the `:485/:486` insertion point — confirmed by reading, no tool needed beyond `Read`.
- `harness_yaml.PLACEHOLDER_UNSET` → `('none', 'null', 'n/a')`; `'n/a' in ...` → `True`.
- Type-strict truth table (`val == expected and isinstance(val, type(expected))`):
  `False==False→True`, `0==False(type-strict)→False`, `True==False→False`, `'fail'=='fail'→True`,
  `'pass'=='fail'→False` — matches D-05's claim exactly.
- Existing `matrix_ok: n/a` + PASS fixture (`:964/972`) enters the `NULLABLE` branch (val is `str`)
  and `continue`s before the new gate — no double-report.
- `run-unit-tests.sh:6` `SCRIPTS` array: `"test-validate-digest.py"` is first. Confirmed.
- T-01(ii): dev digest `suite: fail`+`task_verify: pass`+`PASS` → `harness-backend-dev` →
  `digest ok`, **exit 0**. T-01(iii): qa digest `matrix_ok: false`+`PASS` → `harness-qa` →
  `digest ok`, **exit 0**. Both match PLAN's receipt exactly.
- T-01 scope: qa `suite: fail`+`PASS` → `digest ok`, exit 0 (SC-14 first half, not previously run —
  matches). dev-ops `suite: fail`+`PASS` → `digest ok`, exit 0 (D-03 residue, matches).
  dev-ops `suite: n/a`+`task_verify: n/a`+`PASS` → `digest ok`, exit 0 (T-01(i), matches).
- T-04 awk receipt: `awk '/^VERDICT: BLOCKED$/,/^artifact: none$/' harness-tdd-enforcement/SKILL.md
  | validate-digest.py harness-backend-dev` → `digest ok`, **exit 0**. Matches PLAN exactly (the
  Expertise-injected copy of this skill in my own context is a truncated excerpt, not the real file —
  the real file has the full block including `artifact: none`).
- T-02 (`harness-digest-dev/SKILL.md`): `task_verify` count 0; `PLAN.md` grep exit 1; paired
  `BLOCKED.*PLAN\.md` regex exit 1; `VERDICT: PASS is rejected` count 1. All match "measured 0/1/1/1
  at `3bfedc9`" exactly.
- T-02 (`harness-tdd-enforcement/SKILL.md`): `receipt` count 0, `verbatim` count 0, paired regex
  exit 1. Matches.
- T-10 (`harness-qa.md`, `harness-verification-rules/SKILL.md`): `VERDICT: PASS is rejected` count 1
  in each; paired fail-value regex exit 1 in each. Matches.
- `run-unit-tests.sh` (full suite): green, includes `test-harness-yaml-corpus.py`,
  `test-upgrade-config.py`, `test-team-catalog.py` (last checks in the run) all passing.
- §C: `git show 3bfedc9:docs/harness/DECISIONS-INDEX.md` vs `gen-decisions-index.py --stdout` (run
  against unmodified `DECISIONS.md`) — content-stripped diff clean, `@NNNN`-inclusive diff exit 1 (57
  changed lines); DEC-118 committed `@2376` vs generated `@2382`; DEC-174 committed `@4680` vs
  generated `@4674` — non-uniform, confirming at least two independent pre-existing edits.

## Not re-derived, judged as instructed

- B2 (D-03 residue, `dev-ops suite: fail`+PASS staying accepted): **discharged, not a gap.** BRIEF
  `## Verification gaps` (`:211-218`) and PLAN D-03 (`:50-62`) both name it explicitly, cite the exact
  re-measured evidence, and PLAN step 9(i)/SC-15 pin it with a named fixture. Non-blocking, matches
  the user's D-03 ruling exactly — not re-litigated here.
- Preload/scope checks (D-06, T-02 site list, propagation table): all confirmed exactly as PLAN
  states — `grep -ln harness-tdd-enforcement .claude/agents/*.md` → the 5 named files;
  `grep -c harness-digest-dev .claude/agents/harness-dev-ops.md` → 0.

## Sequencing

No task's `verify:` silently depends on another landing without a declared `depends_on`, beyond the
already-noted (and correctly harmless) over-serialization on T-03/T-06/T-10's `depends_on: T-01`.
T-02→T-04 ordering (F6 above) is the one real shared-file hazard and is already declared as
`depends_on`.
