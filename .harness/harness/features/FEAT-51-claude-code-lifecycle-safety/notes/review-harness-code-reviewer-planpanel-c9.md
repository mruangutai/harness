# Plan-panel c9 — scope (traceability + verify audit) — FEAT-51

**BLUF.** The plan is a clean DAG, all nine `verify:` blocks measured RED against the unmodified
tree, and every REQ/SC has a grading task. One new MED finding: T-06's intent bullet list — which it
calls exhaustive ("carries exactly these claims") — was never actually edited to carry D-15's
required content, even though D-15 says in its own `because:` clause that it exists precisely to stop
that omission. One new LOW/INFO finding: T-01's staleness disclosure ("two line hints known stale")
understates the real scope — essentially every numeric anchor inside `hook_mode()` is off by the same
~112-line shift, one landing inside an unrelated function. Both already-mitigated by gates/hedges
already in the plan; neither is a `must_fix` in isolation, but D-15/T-06 is worth the operator's eyes
before signing given D-15's own text names the exact risk.

All four SETTLED items from the dispatch were independently re-derived (D-16/D-17/T-09 gone except
in frozen `panel.findings` + real FEAT-41 `t09` helpers; SR-2 answered by T-10; the four cycle-8/9
closures; PF-e380f685… open by decision) — none re-raised as new.

## Q1 — does anything still assert coverage the feature no longer builds?

**No dangling coverage claim found.** Grepped `D-16`, `D-17`, `T-09`, `SC-12` across `plan.yaml` and
`BRIEF.md`.

- `D-16`/`D-17` occur only inside the frozen `panel.findings` block (`plan.yaml:38,54,65,71`) —
  expected, the frozen record.
- `T-09` occurs in `panel.findings` (same lines) plus two intent references: `plan.yaml:241`
  ("Use the T-09 group's fixture builders…") and `plan.yaml:389` ("Follow the T-09 group instead…").
  **Verified at source, not assumed**: `test-validate-digest.py` has real `t09()`/`_reg_module()`/
  `_t09_root()`/`_t09_fire()` at exactly lines 1227/1231/1241/1249 (FEAT-41's T-09 fixtures, still
  live), and `test-check-domain.py` has a real `t09()` group recorder at line 2495 with cases
  labelled `"T-09 1: …"` through `"T-09 9: …"`. Both are FEAT-41's T-09, not this plan's deleted one
  — the prompt's claim (a)/(b) both check out.
- `SC-12`: zero occurrences in `plan.yaml`; two in `BRIEF.md`, both inside `## Verification gaps`
  explaining the withdrawal — no grading task references it, no orphan.
- Grepped every "discard" mention (10 in `plan.yaml`, 6 in `BRIEF.md`): all describe discard as an
  *explicit act* (no default, no timer) or explicitly state it is *not* covered (T-07 intent, D-18,
  BRIEF `## Verification gaps`). None claims tamper-proofing. Consistent with D-18 throughout.
- Decision list is D-01..D-15, D-18 (16 decisions, confirmed by direct read) — no D-16/D-17 entries
  survive outside the frozen findings text.

## Q2 — is the dependency shape still a topological order, and record after enforcement?

**Yes, a valid DAG; no cycle.** Full edge list from the amended plan:

```
T-01 -> []
T-02 -> []
T-03 -> [T-02]
T-04 -> [T-02]
T-07 -> [T-02]
T-05 -> [T-01, T-04]
T-06 -> [T-01, T-02, T-03, T-04, T-05, T-07]
T-08 -> [T-06]
T-10 -> [T-03, T-07]
```

One valid topological order: `T-01, T-02, T-03, T-04, T-07, T-05, T-06, T-08, T-10`. No back-edges,
no self-loop, no reference to a non-existent task id (checked `depends_on` against the live task-id
set; `T-09` appears in zero `depends_on` list). T-06 (the record) depends on **every** enforcement
task that shipped by this cycle, including T-07 (the Bash route) — the already-ruled fix holds. T-10
correctly lost its edge to the deleted T-09 and gained edges to T-03 and T-07, its actual targets.

**But see the finding below: the record being ordered correctly after the enforcement tasks does not
mean the record's *content instructions* actually incorporate what those tasks require it to state.**
T-06 running after T-07 guarantees the *code* exists to document; it does not by itself guarantee
T-06's intent text asks the documentor to document it.

## Q3 — can any task's `verify:` pass before its task runs?

**No. I RAN all nine verify blocks against the untouched worktree tree; every one is currently RED**
(shell `&&`-chains fail on their first grep, matching the "recorded baseline" every intent claims).
Method noted per task — none were merely read-and-assumed.

| Task | Method | Result |
|---|---|---|
| T-01 | RAN (2 greps + suite) | grep counts 0/0 → chain fails before the suite runs. RED. |
| T-02 | RAN (2 greps) | grep counts 0/0. RED. |
| T-03 | RAN (2 greps) | grep counts 0/0. RED. |
| T-04 | RAN (`ls` on target files) | `quarantine.py`/`test-quarantine.py` do not exist yet → the task's own `python3 test-quarantine.py` conjunct fails to even start. RED. |
| T-05 | RAN (2 greps) | grep counts 0/0. RED. |
| T-06 | RAN (DEC-210 existence check, awk-region greps, `gen-decisions-index.py --stdout` diff, full test suite) | `## DEC-210` absent from `DECISIONS.md` (count 0), `DEC-210` absent from `DECISIONS-INDEX.md` (count 0), both awk+grep clauses 0. First conjunct fails. RED. (The `diff` clause is separately clean today only because nothing has changed yet — not a pre-pass risk, since the awk clause gates first.) |
| T-07 | RAN (4 exact-label greps) | all 4 counts 0. RED. |
| T-08 | RAN (3 `def` greps) | all 3 counts 0. RED. |
| T-10 | RAN (6 exact-label greps across both test files) | all 6 counts 0. RED. |

No task's gate is pre-satisfied; none can "go green" without the described work actually landing.
This directly reconfirms cycle 8's DEC-209→DEC-210 fix is real and load-bearing (T-06's grep for
literal `DEC-210` truly has nothing to match yet).

## Q4 — SC/REQ traceability matrices

**SC → grading task(s).** All of SC-01..SC-11 and SC-13 have at least one grading task; none orphaned
by SC-12's withdrawal.

| SC | Grading task(s) | Note |
|---|---|---|
| SC-01 | T-01 | exact-label cases in `test-validate-digest.py` |
| SC-02 | T-01 | same group, the three escape-condition labels |
| SC-03 | T-01 | "leaves the parent claim live" label, read off disk |
| SC-04 | T-03 | `BRIEF.md` case + plan.yaml route-denial-preserved case |
| SC-05 | T-03 | notes/quarantine-path allow labels |
| SC-06 | T-04 | adopt/discard/list CLI + sha256 no-op proof |
| SC-07 | T-02, T-03, T-07 | OMP discrimination cases (case 33, check-domain OMP label, plan-sign-gate OMP label); the `check-omp-port.py`/`.omp/agents/*.md`/`--kind` clauses are pre-existing invariants outside all 21 target files — correctly not owned by any task, verified directly at SC-grading time, not a gap |
| SC-08 | T-05 | content + reviewer inspection (verify: inspection) |
| SC-09 | T-06 + T-08 | T-06 writes the entry, T-08 supplies the per-clause assertions in `run-unit-tests.sh` `INTEGRATION_SCRIPTS` — see finding below |
| SC-10 | T-05 (conduct) | verify: uat, operator-run, correctly unowned by any task's automated verify |
| SC-11 | T-07 | exact match to T-07's four/nine labels |
| SC-13 | T-10 | exact match, one-to-one |

**REQ → tracing task(s).** All REQ-01..REQ-07 (the live set) traced; every task's `traces:` cites only
live REQ ids (checked all nine against the REQ-01..REQ-07 set — zero stale references).

| REQ | Tracing task(s) |
|---|---|
| REQ-01 | T-05 |
| REQ-02 | T-01, T-06 |
| REQ-03 | T-03, T-05, T-10 |
| REQ-04 | T-02, T-03, T-07, T-08, T-10 |
| REQ-05 | T-04, T-06, T-07, T-08 |
| REQ-06 | T-01, T-05 |
| REQ-07 | T-02, T-06 |

No orphan REQ, no orphan task (every task traces >=1 live REQ), no orphan SC.

## Q5 — is T-01 still buildable from its own intent, at HEAD?

**Yes, buildable — every quoted literal resolves and the described code shape is accurate — but the
plan's own staleness disclosure undersells how much of the numbering has drifted.** Verified by direct
read/grep against `.claude/skills/harness/bin/validate-digest.py` and `test-validate-digest.py` at
HEAD (both target files, confirmed dirty-free at HEAD, no uncommitted local edits to account for):

- `hook_mode()` — claimed `:1453`, confirmed at `:1565` (the disclosed stale hint). Its docstring and
  three-pass-through structure read identically to what the intent describes.
- `"STEP TWO — THE D-09 RETURN CONTRACT"` (em dash, as the intent warns) — literal resolves, now at
  `:1661` (undisclosed — the intent quoted no number for it, only the literal, so no defect).
- `"STEP ONE — THE RELEASE"` — present, `_reg.release(...)` called unconditionally before the D-09
  children check, exactly as described; the release call is now at `:1646`.
- `d.get("last_assistant_message", _ABSENT)` — confirmed to be read at `:1714`, **after** the
  release/children-check block, matching the intent's explicit "the text is read… AFTER this block".
- `VALIDATE_DIGEST_BIN` — confirmed exactly at `:18` as claimed.
- `VERDICTS = {"PASS", "FAIL", "BLOCKED", "ESCALATE"}` — confirmed exactly at `:35` as claimed.
- Test-file fixtures — `case()` helper at `:239`, `t09()` at `:1227`, `_reg_module()` at `:1231`,
  `_t09_root()` at `:1241`, `_t09_fire()` at `:1249`, `claims()` inside `run_t09` at `:1286` — **all
  five confirmed exactly as claimed, zero drift**, because the `+654/-119` growth in the test file
  landed later in the file, not around these fixtures.
- `main()` registration — claimed `:3036`, confirmed at `:3571`/`:3572` (the second disclosed stale
  hint), and `fails += run_t09()` is present at `:3578` for the new group to sit beside.

**The undisclosed part:** the shift inside `validate-digest.py` (net `+270/-158` = **+112 net lines**)
is not confined to the two disclosed anchors — it applies uniformly to essentially every numeric hint
*inside* `hook_mode()`'s body (`:1527` STEP ONE, `:1549` STEP TWO comment, `:1563` `live_children()`,
`:1575` `children_refusal_lines`, `:1594` return 2, `:1602` the `last_assistant_message` read,
`:1498` "the order the comment… requires", `:1494` `stop_hook_active`, `:1510` unavailable registry,
`:1523` no root, `:1544` failure-swallowing), all off by the same ~110–119 lines. Concretely checked:
**`:1527` today lands inside `check_artifact_file()`, a wholly unrelated function** (artifact-path
resolution for DEC-156), not `hook_mode()` at all. A builder navigating by line number rather than by
the mandated literal-grep would land in the wrong function with no obvious warning, since the
surrounding code is plausible-looking Python.

**Severity: low/info, not blocking.** The intent's own preamble already instructs "treat the quoted
literals as the anchors and the numbers as hints" and "re-read before you edit" — the exact hedge that
covers this. Every literal I checked resolves uniquely and correctly, and the semantic content
(release-before-classification ordering, "read AFTER this block") is accurate at HEAD. The finding is
that the plan's own framing ("two line hints are known stale") is a sample, not the full picture —
worth a note so nobody downstream treats "two" as a bound on how many `:NNNN` values to distrust.

## Findings

1. **[MED] T-06's intent bullet list was never actually amended to carry D-15's required content,
   despite D-15 saying it supersedes exactly those bullets.** `plan.yaml:600-652` (T-06's `intent:`)
   states "it carries exactly these claims" over a closed 8-bullet list. Grepped that intent text in
   isolation (not the surrounding `verify:`/decisions): **zero** occurrences of `plan-sign-gate`,
   `Bash`, `PreToolUse`, or `D-15`. Bullet 3 still reads "…refused at the check-domain.sh Write gate
   on the canonical artifacts…" and bullet 4 still begins "The four canonical artifacts are
   plan.yaml, BRIEF.md, feature.json and STATE.md" — these are, near-verbatim, the exact two bullets
   D-15 (`plan.yaml:205-208`) names as the ones it "SUPERSEDES," because (D-15's own `because:`
   clause) "a documentor following T-06's bullet list verbatim writes an entry that omits the Bash
   half entirely and leaves a reader believing plan.yaml is covered because the FEAT-41 denial
   handles it, which is the exact false belief T-07 exists to overturn." That is exactly what a
   documentor following T-06's intent as literally written would still produce today — D-15 was
   added as a decision, but the text it claims to have already superseded in T-06 was never edited.
   **Consequence:** a documentor who does not separately cross-reference D-15 (which T-06's intent
   never names) ships a DEC-210 entry that fails T-06's own `verify:` (the `plan-sign-gate\.sh` grep,
   confirmed absent today), fails SC-09, and fails all three of T-08's new guard tests — forcing at
   least one redo cycle, and risking a documentor "gaming" the grep by inserting the bare string
   `plan-sign-gate.sh` without the semantic content D-15/T-08 actually require (T-08's sentence-
   adjacency check on `plan.yaml`+`plan-merge.py` mitigates this specific risk, but the general
   confusion of a self-contradicting task spec remains). **This is adjacent to but distinct from the
   dispatch's already-ruled item 3** ("T-06's `verify:` greps… BOTH `plan-sign-gate.sh` and
   `plan-merge.py`") — that item closed the *gate*; it did not touch the *intent text* the gate is
   meant to validate against, so the underlying inconsistency D-15 names is still live in the
   artifact. Not `must_fix` on its own (the gate genuinely blocks a bad ship), but worth a line-edit
   before sign: fold D-15's (a)/(b)/(c) into T-06's bullet list directly, or have T-06's intent
   explicitly say "D-15 supersedes bullets 3 and 4 below; read D-15's text as authoritative."

2. **[LOW/INFO] T-01's disclosed staleness ("two line hints") undersells the real scope of drift
   inside `hook_mode()`.** See Q5 above for the full measurement. Not blocking — every literal
   resolves, the intent's own hedge already covers it — but the plan should not be read as "only two
   numbers moved."

## Already-ruled, not re-raised

Independently landed on all four items named in the dispatch's SETTLED section (D-16/D-17/T-09/SC-12
clean removal per D-18; SR-2 answered by T-10; the T-06→T-07 dependency + two-name verify grep +
T-07 `--file` control + DEC-209→DEC-210 renumber, all reconfirmed present and RED-until-built; and
PF-e380f685… correctly still `open` by operator decision, not reopened here). None of my findings
above duplicate these.
