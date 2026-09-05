# Goal-check — BUG-1302 at review_sha ac8dd671 — validate cycle 1

**Answer (as of the validate cycle-2 re-grade): 10 of 10 criteria MET.** As first written this line
read "9 of 10 criteria MET; SC-06 is PARTIAL — its behaviour is right, its mandated red is
UNRECORDED"; SC-06 was re-graded to MET on evidence discovered after that pass (see its entry).
Every falsifiable-by-construction criterion was run in BOTH directions (pin and base
`c369fb1`), and every orchestrator measurement below was re-derived, not taken on trust. One new
consequence: writing the INV-32 reader entry (Deliverable 2) made `review_sha` STALE under INV-33 —
the main session must re-pin. One open item remains (Q2, the re-pin); it is main-session-direct
under DEC-174. Q1 was closed by the cycle-2 re-grade.

Substituted `<review_sha>` = `ac8dd671742dc20cea91c03715a9579c7c879e31`; base `B` =
`c369fb1fdfc74a8f78edc9a2df2a8fea738afc94`. `<W>` = this worktree. Every suite run was prefixed
`env -u HARNESS_AGENT_TYPE`. Working tree == pin for both test files (`git -C <W> diff --stat
ac8dd671 -- tests/unit/test-suite-layout.py tests/integration/test-run-unit-tests-layout.py` prints
nothing), so run-output evidence and blob evidence describe the same text.

## Re-derived orchestrator claims (all CONFIRMED, none contradicted)

| Claim | Re-derived |
|---|---|
| unit exit 0, 54 PASS, 0 FAIL | `python3 tests/unit/test-suite-layout.py` → exit 0, `grep -c '^PASS '`=54, `grep -c '^FAIL'`=0 |
| integration exit 0, 14 PASS, 0 FAIL | same shape → exit 0, 14, 0 |
| routes: exit 0, 5 DEVIATION, 0 VIOLATION | see SC-10 |
| AST census B→pin | independently parsed both blobs: `_literal_key_present` `any()` 2→1, `"*?["` 2→1; `_is_inside_tests` `".."` 2→1 |
| `check(` sites 39→48 | `git show B/pin … \| grep -c 'check('` → 39 / 48 |
| diff `54f01854..pin` = 8 paths | confirmed: the 2 test files + 6 BUG-1302 lifecycle artifacts, no production file |

## Per-criterion

- **SC-01 — MET (automated).** `python3 tests/unit/test-suite-layout.py` → exit 0, 0 FAIL lines;
  `git -C <W> show ac8dd671:tests/unit/test-suite-layout.py | grep -q "b4 corpus: _literal_key_present verdicts unchanged"`
  → **exit 0**; same grep at `B` → **exit 1** (falsifiable, and it was absent before). `B4_CORPUS`
  (pinned blob :501-515) carries both classes: clean-extension trailing spans (`test-*.py`,
  `probe-*.py`) and non-clean (`test_*x`, `test-*.p*y`, `test-x.py`, `probe-*.md`).
- **SC-02 — MET (automated).** Run exit 0. Structural fact re-derived by me from the two blobs,
  independent of the suite's own assertion: `any()` 2→1 and `"*?["` 2→1. Red half: the criterion's
  FAIL line is on record — `FAIL b4 structural: the tautological conjunct is absent any calls=2,
  wildcard constants=2` (`notes/red-demonstrations-2026-09-05.md`, T-02). Graded on the record; no
  file was mutated by me (DEC-174).
- **SC-03 — MET (automated).** `… | grep -q "b5 corpus: _is_inside_tests verdicts unchanged"` →
  exit 0 at pin, **exit 1 at B**. `B5_CORPUS` (:455-471) carries `../x/*.py`,
  `tests/../evil/*.py`, `a/../tests/*.py`, `tests/unit/**`, `**/*_test.*`, `/abs/tests/*.py`, `*`.
- **SC-04 — MET (automated).** Run exit 0; `".."` constants in `_is_inside_tests` 2 at B → 1 at pin
  (my own parse). Recorded red: `FAIL b5 structural: no unreachable dotdot comparison dotdot
  constants=2` (T-01 section).
- **SC-05 — MET (automated).** `out=$(python3 tests/unit/test-suite-layout.py)` exit 0;
  `printf '%s\n' "$out" | grep -q '^PASS b6 message: the no-candidate failure names both remedies'`
  → exit 0 (run line 52). `git show ac8dd671:… | grep -q INAPPLICABLE` → **exit 1**; at `B` →
  **exit 0**. Independent confirmation of "constant false condition": I walked the pinned blob's
  `ast.If` on `control_candidate … None` and its `orelse` `check()` call's second positional arg is
  `Constant(value=False)`; at `B` the same branch holds a `print`.
- **SC-06 — PARTIAL. Positive half MET, red half UNVERIFIABLE (unproven, not wrong).** Met:
  `PASS b6 reachability: no candidate under a corpus-blind config` and `PASS b6 message: …` both in
  the run (lines 51-52), and the literal-`False` second argument re-derived above. Unproven: the
  criterion names two mutations — delete either remedy phrase, or replace the literal `False` with a
  truthy expression — and requires the observed FAIL line on record. `red-demonstrations-2026-09-05.md`
  T-03 records only ONE FAIL, from the pre-fix state: `FAIL b6 message: the no-candidate failure
  names both remedies detail='', condition=None`. That proves the check reddens on the fail-OPEN
  branch; it does not exercise either named mutation, and plan T-03's intent mandated all three.
  The remaining two are prose only. **Behaviour is right; evidence is missing.** Producing it needs
  a temporary edit to `tests/unit/test-suite-layout.py`, which DEC-174 reserves to the main session,
  so I did not produce it.
- **SC-06 — RE-GRADED 2026-09-05 (validate cycle 2): MET (automated).** The PARTIAL above stands as
  written and is not withdrawn: it was correct about the evidence *in hand at the first pass*, where
  `red-demonstrations-2026-09-05.md` T-03 held only the fail-OPEN transcript. It was re-graded on
  evidence DISCOVERED AFTER that pass — the validator segment's qa member had independently produced
  both missing transcripts in a disposable probe worktree at the pin (all mutations reverted, probe
  worktree removed, neither reviewed file touched), recorded in `notes/qa-2026-09-05-6.md` §3 row B-6
  mutants (2) and (3) and §4 parts (ii) and (iii). Nothing about the code changed; the record did.
  - Clause (1) re-run by me at the pin: `env -u HARNESS_AGENT_TYPE python3 tests/unit/test-suite-layout.py`
    → **exit 0**, 54 PASS / 0 FAIL, carrying verbatim `PASS b6 reachability: no candidate under a
    corpus-blind config` and `PASS b6 message: the no-candidate failure names both remedies`.
  - Clause (2), mutation A (delete a remedy phrase): qa mutant (2) — one remedy phrase deleted from
    the detail string with the real `check(..., False, ...)` call intact — reddened `b6 message`,
    citing the truncated detail. Mutation B (literal `False` → truthy expression): qa mutant (3) —
    `False` replaced by `control_candidate is None`, both phrases kept — reddened the SAME check on
    its `condition=Compare(...)` clause. One mutant per named mutation, same named check, at the pin.
  - "**Either** phrase" is discharged by symmetry read off the pinned source, not by a second
    transcript: `:680-686` asserts the two phrases as two peer `in` conjuncts of one `and` chain
    (`"extend CANDIDATE_CORPUS" in b6_detail and "detection regression" in b6_detail`), so deleting
    either falsifies its own conjunct identically. I record this as a structural inference, not an
    observation.
  - "makes it **exit 1**" established from the suite's own accounting, read-only: `check()` appends to
    `failures` on any false condition (`:45-48`) with no detail-string guard, and the file ends
    `raise SystemExit(1 if failures else 0)` (`:712`). A FAIL line therefore entails exit 1 — repo
    Expertise G-08's fail-open counting shape does not apply to this suite.
  - Clause (3) — records location: the two new FAIL lines live in `qa-2026-09-05-6.md`, while the
    criterion names `red-demonstrations-2026-09-05.md`. I judge this **(b) a records-location nit for
    the backlog, not a substantive failure**: the criterion's substance is that the observed FAIL is
    on the durable record in this feature's `notes/` at the pin, and it is, with section and row
    anchors. The nit is real but cosmetic — `red-demonstrations-2026-09-05.md` does not cross-
    reference the qa note, so a reader following the criterion's literal wording finds one transcript
    and concludes two are missing, which is exactly what happened to me. Remedy is a one-line pointer
    in the red-demonstrations note; I did not write it (build-phase artifact, not mine).
  - Residual: none. Q1 below is CLOSED by this re-grade.
- **SC-07 — MET (automated).** Run exit 0, `PASS b14: unreadable tracked sources are reported, not
  raised` present. Fixture at the pin covers both hazards and names both paths
  (blob :694-709: `deleted.py` committed then `unlink()`ed → asserts `unreadable tracked source
  deleted.py: FileNotFoundError`; `binary.py` → `… UnicodeDecodeError`). Recorded red: `FAIL b14:
  unreadable tracked sources are reported, not raised UnicodeDecodeError: 'utf-8' codec can't decode
  byte 0xff …` (T-04 section).
- **SC-08 — MET (automated).** Over `git show ac8dd671:tests/integration/test-run-unit-tests-layout.py`:
  `grep -q '"PASS test-unit.py" not in p.stdout'` → **exit 1** (at `B`: exit 0 — discriminating);
  `grep -c '"PASS test-" not in p.stdout'` → **exactly 2**, at `:93` (`git tracked rogue refused
  before sentinels`, case 2) and `:121` (`git enumeration failure refused before sentinels`, case 4)
  — at `B` the count is 1. `python3 tests/integration/test-run-unit-tests-layout.py` exit 0.
  Red half MET with a NOTE: the record's T-05 demonstration is not the criterion's literal "revert
  case 2" wording — it mutates the fixture's copied runner to emit the integration sentinel before
  refusal, showing `FAIL git tracked rogue refused before sentinels PASS test-integration.py` with
  the widened clause and a green with the narrow clause restored. That is the PF-fc35850348 remedy
  and is strictly stronger than the criterion's wording (it isolates the added property). Graded met.
- **SC-09 — MET (automated), enumerated one grep per name.** Unit run: `^PASS real layout is valid`,
  `^PASS sole implementation sweep`, `^PASS case 11 hygiene: every running-kind detect pattern is
  certified` — each grep exit 0. `^PASS case N: ` for N = 1,2,3,4,5,6,7,8,9,10 — **ten separate
  greps, all exit 0**. Integration run: `^PASS ` for `clean layout`, `runs unit`, `runs
  integration`, `git clean tree runs both sentinels`, `git tracked rogue refused before sentinels`,
  `git three tracked rogues reported in sorted path order`, `git enumeration failure refused before
  sentinels`, `git untracked rogue is not reported and both sentinels run` — **eight separate
  greps, all exit 0**. `grep -c '^FAIL'` = 0 in both runs. 21/21 named items present.
- **SC-10 — MET (inspection).** `python3 .claude/skills/harness/bin/check-plan-routes.py
  .harness/harness/features/BUG-1302-suite-layout-fail-closed/plan.yaml` → **exit 0**, exactly 5
  DEVIATION lines (T-01..T-04 naming `tests/unit/test-suite-layout.py`, T-05 naming
  `tests/integration/test-run-unit-tests-layout.py`, nothing else), **0 VIOLATION**. Transcript is
  the evidence, as the criterion says. Run before Deliverable 2's write; the write touches no task
  or lane.

**Count over the ten: 10 met, 0 unmet, 0 partial.** (First pass: 9 met, 1 partial — SC-06, re-graded
to met in validate cycle 2 on evidence discovered after that pass; see the SC-06 re-grade entry.) No
criterion is unmet on BEHAVIOUR. No emergent criterion adopted; nothing outside BRIEF was graded.

## Deliverable 2 — INV-32 reader record

Confirmed from CONTENT, not filename: `notes/research-BUG-1302-goalcheck-plan-c1.md` opens
"Goal-check — BUG-1302 plan vs the operator's stated intent — cycle 1" and carries six lens verdicts.
Persona established from `runs/2026-09-05-2-product/digest.md:9` —
`{ step: goalcheck-plan, persona: harness-pm, verdict: FAIL, files_touched: [… research-BUG-1302-goalcheck-plan-c1.md] }`.
So: `reader: goalcheck, status: ran, persona: harness-pm`.

**The mandated `apply` route CANNOT do this and was proven to refuse.**
`plan-merge.py apply --file <plan> --proposal -` with the panel proposal on stdin exits **7**:
`CONFLICT: top-level key 'panel' carries two different values` — `UNION_KEYS = ("tasks",
"decisions")` (`plan-merge.py:104`), so `panel` falls to the step-8 whole-value equality branch
(`:764-774`) and any change to it conflicts. The controlled verb for this key is `set-panel`
(`:1040`), which validates the mapping and reloads before writing. I used it:
`plan-merge.py set-panel --file <plan> --value-file /tmp/b1302_panel.json` → `PANEL cycle 1 -> …`,
`APPLIED …`, exit 0. Still one plan-merge write route; no Edit, no Write, no redirect.

**Proof of the write's blast radius:** `git -C <W> diff -U0 -- …/plan.yaml` shows **3 added lines and
0 removed** — exactly `- reader: goalcheck` / `status: ran` / `persona: harness-pm`. Parsed against
`git show ac8dd671:…/plan.yaml`: `approval` identical (`approved`, mruangutai, 2026-09-05), top-level
`status: review` identical, all five task `status: done` identical, `tasks`, `decisions`, `lanes`,
`panel.findings`, `panel.last_run/cycle/transcription_rule` all identical. `panel.readers` now
carries exactly 3 entries.

**check-state.sh after the write:** the `INV-32 … reader goalcheck never ran or was not recorded`
VIOLATION is **GONE**. It surfaced a NEW one my write caused: `INV-33 … review_sha ac8dd671 is STALE
— plan.yaml has changed since it was pinned`. Expected and unavoidable — closing INV-32 requires
editing the pinned file. The main session must re-pin `review_sha` after this lands. Two unrelated
pre-existing VIOLATIONs also stand: `notes/handoff-build.md` fails the HANDOFF.md shape (missing
`## trust`, `## dead ends`, `## working set`, `## done when`) and `runs/2026-09-05-1-eng/digest.md`
fails the lead digest contract. Neither is mine to fix.

## Open questions

- Q1 — **CLOSED** in validate cycle 2. It read: the two SC-06 mutations must be run and their FAIL
  lines appended to `notes/red-demonstrations-2026-09-05.md`. Both mutations were in fact already run
  by qa at the pin in a disposable probe worktree and are recorded in `notes/qa-2026-09-05-6.md` §3
  row B-6 / §4 (ii)(iii). Residual is a records-location nit only: `red-demonstrations-2026-09-05.md`
  carries no pointer to them. Backlog, not blocking.
- Q2 (blocking the ship record): `review_sha` needs re-pinning past this plan.yaml write, or the
  entry must be folded into the reviewed commit. INV-33 is red until then.
