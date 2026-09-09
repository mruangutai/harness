# STATE

## Current

- feature: BUG-1507-ready-station-signature
- run: VALIDATE PASSED at `ac5e24e5` — panel `must_fix: []`, `severity_max: med`, all four readers
  ran. Returned to the main session, which owns PR open, CI watch, merge and `gh-sync.py ship`
- squad: none — the orchestrator's build+validate mission is complete
- status: in_review (panel clean; awaiting the main session's PR and merge)
- station: `review` (plan.yaml line 3), written by `gh-sync.py status <feature-dir> review`
- review_sha: `ac5e24e51f2520e273580f66c372b5bd143001f1`
- mirror: milestone #64, parent #1517, sub-issues #1518-#1522, all six at the review station
- cycles_used: 3 of 10 · runs: 10 of 20

Log (condensed 2026-09-09 to the INV-23 budget; the detail lives in `notes/` and `runs/*/digest.md`):

- 2026-09-08: station `plan`. Premises re-verified on disk before any dispatch: `harness-plan.md:24`
  carried `status <feature-dir> Ready`; `github-mirror.md:94,96` carried `Ready`/`Review`;
  `SKILL.md`'s build phase named no feature-level `building` write; `cmd_status`'s docstring omitted
  Building. `.agents/skills` is a symlink to `../.claude/skills`, so `.claude/...` is the one
  canonical, git-tracked path for all four surfaces.
- 2026-09-08: run `plan-product` PASS — BRIEF (6 REQ, 10 SC) and plan.yaml (5 tasks, 6 decisions)
  drafted. pm found a FIFTH live instance at `harness-plan.md:11` (`board-station.py <n> Plan`) and
  folded it in as D-06; the orchestrator confirmed it dead independently (exit 2).
- 2026-09-08: run `2026-09-08-01-product` FAIL — the plan panel's goal-check against the operator's
  stated intent: 3 of 5 DoD bullets discharged, 9 findings, all repairs BRIEF-only.
  `notes/research-BUG-1507-goalcheck-plan-c0.md`. `cycles_used` 0 -> 1.
- 2026-09-08: RECORD CORRECTION, disclosed. The draft run had been appended under the id the
  goal-check lead later gave its own run DIRECTORY, so one id labelled two runs with opposite
  verdicts, and it carried a `code_grade` that belongs only to a validator run. Ids and keys
  corrected; no verdict or outcome altered.
- 2026-09-08: run `2026-09-08-1-product` PASS — fix cycle, R-1..R-7 landed, F-08 accepted, F-09
  declined with reason. Q1 ruled to the disclosure route, Q2 to yes.
- 2026-09-08: run `2026-09-08-01-validator` PASS — plan-panel, `cycle: 0`, `severity_max: med`,
  `must_fix: []`, both readers ran. 4 findings: two `scope` (T-02's and T-03's `verify:` proved
  phrase-presence rather than binding), one `should-not-exist` (T-05's self-reinvocation
  machinery), one low against D-03's circular justification.
- 2026-09-08: run `2026-09-08-02-product` PASS (1 send-back) — the panel record: all four findings
  resolved and transcribed into `plan.yaml`'s `panel:` with computed `PF-` ids.
  `cycles_used` 1 -> 2.
- 2026-09-08: orchestrator verification at its own tier, none delegated: 4/4 `PF-` ids recomputed;
  all five `verify:` commands run and each RED; `check-plan-routes.py` 0 violations; and a probe
  that T-02's and T-03's repaired gates can report GREEN on the correct fix and RED on the exact
  near-miss each finding named. PLAN PHASE CLOSED at the signature gate; `notes/handoff-plan.md`.
- 2026-09-08: OPERATOR SIGNED at acc8bf63. Q1 — accept the disclosed limit, task-card Ready
  exclusivity (`gh_board.py`) stays out of scope. Q2 — keep both T-05 and D-06, retype nothing. The
  main session ran the post-signature `gh-sync.py status <feature-dir> ready` and recorded SC-01's
  transcript at `notes/sc01-ready-write-transcript.md` (partial: (a) and (b) met, (c) not applicable
  — zero sub-issues were recorded at that moment).
- 2026-09-09: BUILD PHASE OPENED, station `ready` -> `building`, by
  `plan-merge.py set-feature-station --station building` run BY HAND from the worktree copy of
  T-03's instruction (the control-plane checkout does not carry it until this branch merges).
  Observed `status: building`; SC-05's record at `notes/sc05-building-write-transcript.md`.
- 2026-09-09: T-01, T-02, T-03 landed main-session-direct by the orchestrator (the DEC-174 carve-out
  `plan.yaml` `lanes:` records). Commits `e5223f10`, `d9caec31`, `3063b1dc`. Each task's own
  `verify:` re-run after its edit: all three exit 0, each RED on the same tree beforehand. T-02's
  Building row names `plan.yaml` explicitly, so SC-06 is answerable from the row alone.
- 2026-09-09: run `2026-09-08-t04-t05-eng` PASS, 0 send-backs — eng-lead hosted the `build` team and
  routed both tasks to `harness-backend-dev`. T-04: 16 docstring insertions, zero deletions, no
  executable line touched (SC-08). T-05: the witness, accepted sets DERIVED from `factory_config`,
  in-process negative control, no self-reinvocation. Orchestrator re-ran both `verify:` blocks
  itself: exit 0 and exit 0, 8 PASS rows / 0 FAIL. Commit `64bc9351`.
- 2026-09-09: run `2026-09-08-03-qa-validator` PASS — the blocking `qa_gate`. `integration` is the
  only kind the matrix demands (T-01, T-02, T-05; the two `docs` tasks require none), all three
  discharged by the new witness, which the lead verified can report RED and not merely green.
  SC-02, SC-03, SC-09 PASS; `must_fix: []`. `notes/qa-BUG-1507-build.md`.
- 2026-09-09: run `2026-09-08-01-simplify-eng` PASS — SIMPLIFY before the pin. All four angles read
  the five-path diff; EMPTY BY RULE. Two non-appliable findings (a redundant conjunct whose removal
  would weaken an assertion after the gate; a residual that D-05's `because:` does not name every
  excluded directory, whose remedy edits a signed plan). Tree clean at `287aafb5`.
- 2026-09-09: BUILD -> VALIDATE seam. `gh-sync.py status <feature-dir> review` run lowercase;
  `review_sha` pinned at the seam commit `ac5e24e5`, which contains every deliverable, the only
  later commits being record writes that touch no code path.
- 2026-09-09: run `2026-09-08-panel-validator` PASS — the validate panel at the pin. All four
  readers RAN, none skipped. `severity_max: med`, `must_fix: []`, `code_grade: grade_2`. Findings:
  VL-01 (med), F-01 (low, a `BrokenPipeError` in the `verify:` chain under `pipefail`, unexploited
  because `run-unit-tests.sh` executes the file directly), F-02 (med, an accepted grade-2 function
  with its reason on file), and two assessed-and-dismissed info rows.
- 2026-09-09: VL-01 MEASURED by the orchestrator rather than relayed —
  `notes/vl-01-plan-merge-shape-measurement.md`. The shape the witness cannot see occurs twice in
  the swept scope, both `building`, both accepted: the gap is latent, nothing ships broken, and the
  `--station <name>` placeholder is already excluded correctly. NOT routed as a fix cycle, because
  T-05's signed `intent:` spells the pattern character for character. Carried up as a backlog row
  with its cost measured (one alternation, one accepted-set entry, `MIN_OCCURRENCES` 6 -> 8).
- 2026-09-09: RECORD CORRECTION, disclosed rather than silently repaired. (1) The qa segment was
  first appended under an id that did not match its run DIRECTORY; the id now matches. (2) While
  probing whether `feature-json-merge.py set-key` accepts a non-scalar, the orchestrator ran it
  against `runs` and it ACCEPTED an array, overwriting the whole runs list with the single probe
  entry. Restored in the next call from this log and the run directories on disk: nine runs,
  verdicts unchanged, `code_grade: n_a` kept only on the plan-phase validator run. No verdict was
  altered. The probe was careless; the tool's silence about it is raised as Q5.
- 2026-09-09: MIRROR REPAIRED (INV-26 was red): this feature had never been mirrored, which is also
  why SC-01's clause (c) had no cards to observe. `gh-sync.py open` created milestone #64, parent
  #1517 and sub-issues #1518-#1522; `status ... review` then moved all six to the review station.
- 2026-09-09: run `2026-09-08-panelrow-product` PASS — INV-32 was red: `panel:` listed two readers
  where the invariant expects three, so the goal-check that DID run (runs `2026-09-08-01-product`,
  `2026-09-08-1-product`) read as never recorded. pm added `{ reader: goalcheck, status: ran }` via
  `plan-merge.py set-panel`: 2 insertions, `PF-` ids and approval byte-identical. Cycles 2 -> 3.

## Open Questions

- Q1 RESOLVED by the operator at signature: accept the disclosed limit — task-card Ready
  exclusivity is `gh_board.py` code work the issue's own scope line excludes.
- Q2 RESOLVED by the operator at signature: keep both T-05 and D-06; retype neither T-01 nor T-02.
- Q3 (harness owner, not a work item): a subagent return delivered as task status
  `failed (exit 1)` with "Subagent called yield with null data" while the transcript carried a
  complete, well-formed VERDICT/DIGEST/artifact block and every claimed artifact was on disk.
  Observed five times across this feature now, at three tiers. A tier routing on the tool status
  alone discards a passing run.
- Q4 (harness owner, not a work item): the orchestrator playbook and the plan.yaml template both
  say `plan-merge.py apply` "unions by id", which reads as though re-emitting a same-id item with a
  corrected body changes it. It does not — `apply` refuses at exit 7 CONFLICT; the verb that changes
  a value is `amend`. A pm reading the current wording takes exit 7 as a gate failure.
- Q5 (harness owner, not a work item): `feature-json-merge.py set-key` is documented as setting a
  top-level key to a JSON SCALAR and accepts a JSON array without complaint, so one mistaken call
  silently replaces the whole `runs` history — the one part of `feature.json` no other verb can
  reconstruct. Either it should refuse a non-scalar, or `runs` should be a protected key.
- Q6 (for the operator, non-blocking): VL-01 as a backlog row — widen the witness to the
  `plan-merge.py set-feature-station --station <token>` shape that this feature itself added to the
  swept corpus. Latent today; cost measured in `notes/vl-01-plan-merge-shape-measurement.md`.
