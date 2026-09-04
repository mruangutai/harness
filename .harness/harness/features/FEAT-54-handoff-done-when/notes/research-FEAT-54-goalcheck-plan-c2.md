# Goal-check c2 — revised plan vs the operator's stated intent — FEAT-54

## VERDICT

**YES — the plan delivers the operator's stated intent.** All 10 `## Settled` lines are carried, all
5 `## Out of scope` lines are clean, `## Not yet specified` is empty and nothing contradicts the 4
verified facts. All three batched rulings are delivered in the plan text.

**Gate verdict: FAIL.** Two blocking integrity defects (F-01, F-03) need one repair cycle before
signature. Neither touches intent delivery; both are one-line edits inside pm's own writable surface
or the main session's.

Read at worktree HEAD `36fb2c95`; base `git merge-base main HEAD` = `b7956fc4`.

## 1a. Intent coverage — one row per `## Settled` line

| Grilling line | Settled | Carried by |
|---|---|---|
| :9 | fifth standalone `## Done when` section, benchmarked design | REQ-01; SC-01; T-03(a), T-04, T-08 |
| :10 | describes the immediate action in `## Next`, not phase/feature | REQ-01; SC-10; T-08 (template wording), T-11 (Scope: names the ONE action) |
| :11 | exactly one `Scope:` + 1–4 `Authority:`, no other prose | REQ-02; SC-02; T-01(c), T-02 §2, T-03(c), T-06(c) |
| :12 | authorities combine as logical AND | REQ-03; SC-12; T-01(f), T-02 |
| :13 | four bounded authority types; a source location alone is not one | REQ-04; SC-03, SC-13; T-01(d)(e), T-02 §3, T-03(d)(g) |
| :14 | typed machine-readable pointer syntax | REQ-05; SC-03; D-03, T-02 §3 |
| :15 | every pointer resolves **when written**; syntax-only insufficient | REQ-06; SC-03, SC-15; D-10, T-03(d), T-04 (`resolve=True`) |
| :16 | untouched four-section notes stay valid; every new/edited note uses five | REQ-07; SC-04, SC-06, SC-11; D-01, D-08, T-05, T-06(a)(b), T-07, T-11 |
| :17 | keep 60-line whole-file cap; no per-section caps; bound only `Done when` | REQ-08; SC-05, SC-14; T-03(e)(h), T-06(h), T-07 |
| :18 | permanently gate structure + pointer resolution; rerun benchmark at review, never in the normal run | REQ-10; SC-09; D-04, T-09, T-12 |

**UNCARRIED: 0.** One tension worth naming, not a finding: :18's "permanently gate … pointer
resolution" is satisfied by the write gate (`check-domain.sh`, a registered PreToolUse hook — a
permanent gate), not by the persisted pass. :15 disambiguates it — "when the handoff is written" —
so D-10 is faithful to the grilling, not a narrowing of it.

## 1b. `## Not yet specified`

`None.` (grilling :22). Nothing silently decided, because nothing was left open. D-10 is a
post-grilling operator ruling recorded as a decision with its because-clause citing the ruling — the
correct home, not a silent decision.

## 1c. `## Facts I verified` — contradiction check

| Fact | Plan/BRIEF stance | Verdict |
|---|---|---|
| :34 four headings + hard 60 cap; check-domain.sh refuses; INV-17 scans persisted notes | T-04/T-07 extend exactly these two; cap kept | no contradiction |
| :35 per-section 95th percentiles sum to 67 > 60, so caps would conflict | REQ-08, SC-14, T-03(h), T-06(h) forbid per-section caps | no contradiction |
| :36 plans support `T-NN`+`verify`; some next actions derive from findings/approval gates | D-03 defines all four types incl. `finding:`/`approval:` | no contradiction |
| :37 65.9%→96.5%, 3/15→13/15, +2.8% chars, latency inconclusive, directional only | BRIEF `## Problem` :8-13 restates verbatim with the disclaimer | no contradiction |

## 2. `## Out of scope` — violation check

| Out-of-scope line | Status |
|---|---|
| Rewriting the historical handoff corpus | **clean** — D-01/D-08 freeze 141 paths; SC-11 asserts the empty intersection with a positive control; T-11 touches only this build's own non-baselined notes |
| Raising the 60-line cap | **clean** — T-04 "keep the 60-line whole-file cap … unchanged"; T-07 "leave the 60-line cap … untouched"; SC-05 |
| Section-specific caps for Next/Trust/Dead ends/Working set | **clean** — REQ-08, SC-14, T-03(h), T-06(h) assert the absence positively |
| Claiming token or latency savings | **clean** — BRIEF :12-13 explicitly disclaims; no REQ/SC/task asserts a saving |
| Making the model benchmark a permanent automated release gate | **clean** — D-04 `locally_run`, neither script array, absent from `test_matrix`; T-09 verify + T-12(c) assert it |

**VIOLATIONS: 0.**

## 3. The three rulings — delivered?

| Ruling | Delivered | Plan text |
|---|---|---|
| (a) write-time-only resolution | **delivered** | D-10 (`:136-139`) states resolve=True at write / resolve=False in INV-17, "never opens a target". T-01's contract `:167-175` + case (g) `:201-211` = 4 resolve pairs, the ninth absent-fixture assertion, and the counter-assertions that presence/shape/grammar hold under BOTH settings. T-02 `:265-271` "GATES TARGET RESOLUTION AND NOTHING ELSE … return WITHOUT opening plan.yaml, BRIEF.md, or any finding or approval target". T-03 `:335-337` and T-04 `:364-367` both `resolve=True`. T-06 (e1) `:451-457` unresolvable target is reported by NO line; (e2) `:458-461` shape + unknown-prefix still reported. T-07 `:527-534` `resolve=False`. BRIEF REQ-06 `:35-39`, SC-15 `:156-163` |
| (b) probe kept whole | **delivered** | D-04 `:115-118`, T-09 `:592-658`, T-12 `:775-821`, SC-09 `:111-116` all present and internally consistent. Absence confirmed at source: `UNIT_SCRIPTS`/`INTEGRATION_SCRIPTS` at HEAD do not name it and no task adds it (T-09 intent `:649-651`, verify `:624` `! grep -q`); `test_matrix` absence asserted at `:623`; T-12(c) `:812-816` asserts both arrays |
| (c) mutation experiment struck | **delivered** | tasks are exactly T-01..T-12 (`safe_load`), decisions exactly D-01..D-08 + D-10; `grep -rn 'T-13\|D-09\|mutation'` over plan.yaml + BRIEF.md returns two hits, both legitimate: `plan.yaml:32` is the verbatim c0 panel-finding phrase "no-mutation audit" (must not be edited) and `:796` is the pre-existing `mutate omp_session_accessor` probe cases. No `notes/mutation-*.md` reference survives. SC-07 rewritten as `verify: inspection` over two cited import sites at `review_sha` — gradable without the experiment. No criterion left ungradable by the strike |

### Adjudication of the lead's pre-check — NOT a dangling reference

plan.yaml has **no `risks:` key** (top-level keys: `schema feature approval status source_issues
panel lanes decisions tasks`). The text at `:31-34` is `panel.findings[1]` — `PF-570b9c87`'s verbatim
summary. Read at source: **T-06 case (g) at `:464-467` IS still "the real repository corpus stays
clean … compare mtimes and bytes before and after"** — exactly what the finding describes. The
resolve-pairs case at `:201` is **T-01** case (g), a different task. The pre-check conflated the two
tasks' (g) labels. The finding's text is accurate and current; no dangling reference exists.

## 4. Integrity sweep — four sub-results, reported separately

**4a. REQ traceability — PASS.** All 10 traced, no task traces a REQ the BRIEF lacks:
REQ-01 T-03/04/11 · REQ-02 T-01/02/03/04 · REQ-03 T-01/02/08 · REQ-04 T-01/02/03 · REQ-05
T-01/02/03/04 · REQ-06 T-01/02/03/04/06 · REQ-07 T-05/06/07/11 · REQ-08 T-03/04/06/07 · REQ-09
T-08/10 · REQ-10 T-09/12. One clause of REQ-09 is not covered by any task — see F-03.

**4b. SC gradability + falsifiability — PASS (15/15).** Each has exactly one `verify:`, each
`automated` one an `evidence:`, and each has a concrete falsifier:

| SC | What would fail it |
|---|---|
| SC-01 | a 4-heading fixture write exits 0, or the refusal text omits `## Done when`/the template |
| SC-02 | any of the five malformed fixtures exits 0, or a message omits the count |
| SC-03 | an unresolvable pointer of any one type exits 0 (asserted per type, so 3-of-4 cannot hide) |
| SC-04 | `check-state.sh` over the repo prints a line mentioning "Done when" |
| SC-05 | the 61-line note is allowed, or the 60-line note is refused |
| SC-06 | an edit that does not add the section is allowed |
| SC-07 | a second `## Done when` body parser or a second pointer-target read is found in either gate at `review_sha` |
| SC-08 | any of the five named surfaces asserts four sections at `review_sha` |
| SC-09 | a KIND-DRIFT line on the real config; or none when the kind is unregistered; or the basename in either array |
| SC-10 | the operator judges a refusal message unactionable, or the template lets a phase-level `Scope:` read as right |
| SC-11 | `comm -12` prints a path, or the positive control prints nothing |
| SC-12 | a 3-of-4-resolving block returns `[]` |
| SC-13 | an unknown prefix or a bare `file.sh:NN` authority exits 0 |
| SC-14 | either gate emits a cap/length message for the 25-line-Trust, 60-line note |
| SC-15 | the state check reports the absent-target note (e1), or fails to report the malformed/unknown-prefix note (e2) |

Evidence kinds resolve: `test-check-domain.py` and `test-check-state.py` are both in
`test_kinds.integration.detect` and `INTEGRATION_SCRIPTS` (verified at HEAD), so the nine
`evidence: integration` criteria rest on a real runner; SC-12's `evidence: unit` rests on
`test-handoff-done-when.py`, which D-06 puts in `UNIT_SCRIPTS` only. No criterion rests on a null
kind — `eval`/`ui`/`component`/`typecheck` are `cmd: null` at HEAD and the BRIEF's
`## Verification gaps` names `eval` explicitly (DEC-163 satisfied).

**4c. `depends_on` — PASS, acyclic.** Every id exists (T-01..T-12 only). `T-07 → [T-06, T-11]` is a
*file-order* forward reference, not a cycle: T-11 → [T-04, T-05], T-04 → T-03 → T-02 → T-01, and
`.claude/skills/harness/teams/build.yaml:84` reads `depends_on: from_task_depends_on`, so file order
is not the scheduler's input. A valid order is T-01, T-02, T-03, T-04, T-05, T-06, T-11, T-07, T-08,
T-09, T-10, T-12.

**4d. `verify:` conflicts — PASS with one by-design caveat.** No task's verify asserts state another
task deletes, except the three red/green TDD pairs, which are point-in-time by construction: T-01
(`test "$rc" -ne 0`) goes stale when T-02 lands, T-03 when T-04 lands, T-06 when T-07 lands. That is
the intended TDD shape and is stated in each intent ("expected state at the end of this task is
RED"); it means those three verifies must not be re-run at `review_sha`. T-05's baseline verify
(141 paths, none carrying the section) survives T-09 because T-09's intent requires the two keys
byte-identical. T-09's `! grep -q probe-handoff-comprehension run-unit-tests.sh` survives T-12,
which writes a different file. T-08's `! grep -rqi 'four sections'` is scoped to the two docs it
edits. **No cross-task contradiction.**

**4e. Dangling references — PASS.** No `T-13`, no `D-09`, no `notes/mutation-*.md`, no removed
artifact and no `FEAT-52` path in plan.yaml or BRIEF.md. `FEAT-52` survives only in STATE.md
`:10-13` and `research-FEAT-54-planrevision-c2.md` `:4,:12,:66` — commentary about the rename, which
the constraint permits — plus git's staged rename metadata (`R` entries), which is not a live path.
`.harness/harness/features/FEAT-52-handoff-done-when/` does not exist on disk. `handoff-plan.md`
carries **0** `FEAT-52` occurrences; see F-05.

## 5. Live anchor re-check — every cited anchor, read at HEAD `36fb2c95`

| Anchor as the plan cites it | Read at | Result |
|---|---|---|
| `check-state.sh:1059` `HANDOFF_HEADINGS = ["## next","## trust","## dead ends","## working set"]` | `check-state.sh:1059` | **unmoved**, text exact |
| `check-state.sh:1199` computes `miss` | `check-state.sh:1199` (`miss = [h for h in HANDOFF_HEADINGS if h not in hl]`) | **unmoved** |
| `check-state.sh:1219` selects non-empty-body headings | `check-state.sh:1219` (`if _l not in HANDOFF_HEADINGS:`) | **unmoved** |
| INV-17 handoff glob | `check-state.sh:1197` (`glob(... "notes","handoff-*.md")`) | present |
| 60-line cap / `_handoff_exempt` / parsed config `cj` | `check-state.sh:1228`,`:1231`; `:1075`; `:980-986` | all present |
| `check-domain.sh` `RE_HANDOFF` branch of `shape_problems`, at the `"handoff shape (DEC-159)"` head | `check-domain.sh:1511` (branch), `:1527` (`_head("handoff shape (DEC-159).")`) | present, exact string |
| `run-unit-tests.sh` KINDCHECK heredoc, "spanned :111-163 when this task was written" | `run-unit-tests.sh:111` (`python3 -I - <<'KINDCHECK'`) and `:163` (`KINDCHECK`) | **unmoved** — the plan's own advice to locate by delimiter still holds |
| `code_grade.py:468-471` defaults `exclude` to none (panel finding PF-9183) | `code_grade.py:469` (`for pattern in _patterns(kind.get("exclude", ""))`) | inside the cited span; claim true — all 8 kinds at HEAD carry `exclude` |
| `harness.json test_kinds` — 8 kinds; `omp_session_accessor` `locally_run`; `eval`/`ui`/`component`/`typecheck` `cmd: null` | `.harness/harness.json` parsed | confirmed; `handoff_done_when_baseline` absent as expected (T-05 adds it), `_panel_era_start_note` present (T-05's stated register model) |
| 141 notes at `b7956fc4`, 0 carrying `## Done when` (REQ-07, T-05, D-01, D-08) | `git ls-tree -r b7956fc4` filtered → **141**; `git show` each → **0** with the section | both exact |
| next free decision id "212 at b7956fc4" (D-07, T-10) | `DECISIONS.md` max is DEC-211 at HEAD | still 212 |
| `SKILL.md` seam paragraph "Four sections, ~60 lines, shape-gated at write" | `.claude/skills/harness/SKILL.md:304` | present, exact |
| DEC-159 handoff paragraph "The handoff: working memory, not summary" | `DECISIONS.md:3698` | present |
| `probe-omp-session-accessor.py`, `gen-decisions-index.py`, `test-run-unit-tests-kinds.py` exist | `.claude/skills/harness/bin/` | all three present |
| `test-run-unit-tests-kinds.py` `_mutant_config_kind`, `case_1`, probe cases 6-8 | `:69`, `:82`, `:208`/`:232`/`:253` | all present; cases 6-8 are the probe cases as stated |
| `handoff-plan.md` is the predicted T-11 subject (non-baselined, no section) | 53 lines, 0 `## Done when` | T-11's predicted case is real and fits the 60-line cap |

No moved anchor.

## Findings

1. **F-01 — BLOCKING — `plan.yaml` `panel.findings` PF-4205e7e2f84e2eb24d421c924f4d7ac3
   (`:19-27`) still reads `disposition: open`.** The operator accepted this finding and the plan
   implemented it as D-10, so the record understates what the plan has done, and an operator at the
   signature gate reads an unaddressed `med` finding. Disposition is pm's write: it must become
   `resolved` with `resolved_by:` naming the task that discharges it (T-02 implements the flag,
   T-07 applies it in the persisted pass). Severity and summary must stay byte-identical.
2. **F-02 — advisory — the batched ruling itself is nowhere in `plan.yaml`.** `approval:` is
   `status: pending` and nothing else — no `rulings:` key. The rejection of PF-1e45eb3a (probe kept
   whole) and the strike of the mutation experiment are visible only as absences and in STATE.md
   `:17-18`. `approval.rulings` is the main session's write, not pm's, so this is an escalation, not
   a repair task. Without it the next reader cannot tell a struck item from an item nobody planned.
3. **F-03 — BLOCKING — BRIEF REQ-09's leading clause ("No live document **or gate** still tells an
   author the contract is four sections") is uncarried for `check-domain.sh`.** T-04 `:360-361`
   updates only *the message* ("the four sections" → "the five sections"), and the normative comment
   at `check-domain.sh:1512-1513` — "the handoff note is working memory for a successor — four fixed
   / sections" — is instructed by no task. SC-08 will not catch it: its scope is
   "`check-domain.sh`'s required-section list", not its comments. Repair is one clause in T-04's
   intent. (Same class, lower stakes, at `check-state.sh:1188` and `:1201-1204`; those are dated
   FEAT-31 measurement/rationale comments, not statements of the live contract, and rule 15 argues
   for leaving the record alone — I do **not** raise them.)
4. **F-04 — advisory — T-04 double-reports a missing section at the write gate.** T-04 adds
   `"## Done when"` to `check-domain.sh`'s `required` heading list *and* appends
   `handoff_done_when.problems(..., resolve=True)`, whose own first message also names the absent
   section (T-02 §1). An author omitting the section sees the same problem twice. No SC fails —
   T-03(a) is satisfied by either message — and SC-07 is not violated, because heading presence is
   not body parsing. Note the asymmetry: T-07 `:513-518` explicitly de-duplicates the same overlap
   at the state check via `HANDOFF_NARRATIVE_HEADINGS`. One sentence in T-04 (source the
   missing-section message from the module only) closes it.
5. **F-05 — advisory — `research-FEAT-54-planrevision-c2.md:66` is stale.** It asserts
   `handoff-plan.md` still spells `FEAT-52` "×8" and that five other notes do too. Measured: **0**
   occurrences in every one of them; STATE.md `:12-13` records that this run renamed them. The note
   is read-only for me. It matters because T-11's doer is told its `Authority:` pointers must be
   rewritten off `FEAT-52` paths that no longer exist — a successor may go looking for work that is
   already done.
6. **F-06 — advisory — three c0 panel findings carry no plan response.** PF-570b9c87 (T-06(g) in the
   permanent integration suite — confirmed still true at `:464-467`), PF-918326 (T-09's `test_kinds`
   entry omits `exclude`, which all 8 kinds at HEAD carry) and PF-d0ea19ff (SC-14/T-03(h)/T-06(h)
   plant permanent machinery for an out-of-scope exclusion) remain `disposition: open` with no
   `resolved_by` and no recorded ruling. The batched ruling covered only PF-4205e7e2 and
   PF-1e45eb3a. PF-918326 is the cheapest and the most likely to bite: adding `exclude` to the new
   kind is one key in T-09's intent.

## Open questions

- **Q1 (non-blocking):** does the operator want F-02 recorded as `approval.rulings` before signing?
  Only the main session can write it.
- **Q2 (non-blocking):** F-06's three open findings — rule them, or sign with them open? They are
  `low`/`low`/`low` and none blocks intent delivery.
