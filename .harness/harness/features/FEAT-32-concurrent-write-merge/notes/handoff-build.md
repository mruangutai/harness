# Handoff — FEAT-32, build → build (successor), written at 805653a + uncommitted, seq-3

## Next

**Run `ruling-product` RETURNED PASS and is recorded — it is reconciled, not pending.** Its two edits are
landed and committed: T-13's count is a monotone FLOOR ("at least eight … fired again during the build of
its own fix") citing `validate-digest.py:703`, and `BRIEF.md` SC-13 gained the YAML-split statement.
**THE NEW SC-13 STATEMENT IS ITS SIXTH, NOT ITS SEVENTH** — SC-13 held FIVE clauses, so its own trailing
"four of the six" was already false at `b013dde`; pm removed those integers rather than correct one.
Anything downstream saying "seventh" is wrong.
**Then dispatch T-13** (`plan.yaml:1571-1666`) to product-lead → documentor: append ONE new decision
entry taking **DEC-199** (198 is the highest; read the file, do not assume), then regenerate with
`gen-decisions-index.py`. **T-13 also needs main-session T-08 and T-09 done — check before dispatching.**
Then **T-17** (`:2171-2260`), which amends DEC-174 am.4 in place and takes no new number. Then: qa gate
(validator segment), simplify, pin `review_sha`, review panel, pm goal-check, close-out, briefing.

## Trust

- **The operator's signature is GIVEN on all three items — do not re-ask.** Hedged #551 count in the PLAN only; `.gitignore` lock line (done by main session); YAML split recorded + false sentence fixed — coordinator message, this run
- Six team tasks DONE and I re-ran every `verify:` myself at final bytes, all exit 0 (T-02 18/18, T-03, T-04, T-05, T-06 55/55, T-10) — verified-at 02fe848/8057a99
- All six red proofs audited: each mutant imports cleanly then reddens a proportionate NAMED subset — verified-at 8057a99
- **SC-14 MET**: unit exit 0 / 187 lines / 0 `^FAIL`; integration exit 0 / 470 / 0 / 3 `ERROR`. Baselines 179, 221 — verified-at 805653a
- **SC-11 MET**, all four consumers import the core, zero own `flock`/`O_EXCL`/`os.replace` — verified-at 805653a
- **The lock gap is CLOSED**: `.gitignore:46` `.harness/**/*.lock`; `git check-ignore` ignores all five lock paths AND `plan.yaml` itself is correctly NOT ignored (the control) — verified-at 805653a
- Worktree is **current with main** (`805653a`); `12c66b3` is an ancestor; post-merge `test-validate-feature-json.py`, `test-check-domain.py`, `--check-kinds` all green — verified-at 805653a
- `cycles_used` **3** of 10, all from segment A. Runs **13** of 20. **`review_sha` is still `none` and that is CORRECT** — INV-6 fires only once a `squad: validator` run is recorded, so pin it BEFORE recording the qa run — verified-at 805653a
- Coordinator's three measurements, which I did NOT take: a GOVERNED spawn carries BOTH `agent_type: harness-orchestrator` and `tool_input.subagent_type`; payload `cwd` is the FEATURE WORKTREE and the operator ruled the registry root comes from the payload, per worktree; **`claim()`'s docstring is FALSE** — "Never raises for contention" is wrong, it raises `MergeRefusal` after 10.0s, true only of the single-flight refusal which returns `False`. T-06 shipped that sentence — UNVERIFIED by me
- `ruling-product` PASS, 0 send-backs: `BRIEF.md:16` untouched, one BRIEF hunk inside SC-13, both approval blocks byte-identical to `b013dde`, `check-plan-routes.py` exit 0, 17 tasks, 10 decisions — pm verified at source, spot-checked by me — verified-at 932d433

## Dead ends

- **Do NOT attempt `git merge`** — refused by `HEAD_MOVERS`, `bash-write-guard.sh:144`, and the main session ALREADY merged at `805653a`. Retrying wastes a turn and is refused — verified-at 805653a
- **Do NOT ask pm to write `operator-request-*.md`** — its grant is `notes/research-*.md` only; the guard denied my path (#216). The document is `notes/research-FEAT-32-operator-request.md` — verified-at b013dde
- **Do NOT append `test-validate-digest.py` or `test-check-domain.py` to `test_kinds.integration.detect`.** T-10's approved intent names SEVEN paths on the false premise they are absent; they were already PRESENT. All seven now present with count 1 each. I ratified five-not-seven — verified-at 8057a99
- **Do NOT touch `BRIEF.md:16` or SC-14's 221 figure.** The operator declined both; the brief and plan disagree on the count ON PURPOSE — coordinator message, this run
- **Do NOT re-verify the six done tasks**, and do not trust a `digest.md` or `state.yaml` read before its run notifies — both are working state, and this feature has produced false STATE.md entries that way twice — this run
- **Two facts I caught that would otherwise have travelled up as true:** `validate-digest.py` `RANK` is at **:703** (I said :705, coordinator said :702, both wrong); and T-15 was ALREADY done with #715 closed, so "route the one-character fix to pm" was stale and **T-14 is unblocked**, not blocked — verified-at 805653a

## Working set

- `.harness/harness/features/FEAT-32-concurrent-write-merge/STATE.md` and `feature.json`
- `.harness/harness/features/FEAT-32-concurrent-write-merge/runs/ruling-product/digest.md` (its Q1-Q4; occurrence 9 happened during it)
- `.harness/harness/features/FEAT-32-concurrent-write-merge/plan.yaml` (T-13 at 1571-1666, T-17 at 2171-2260)
- `.harness/harness/features/FEAT-32-concurrent-write-merge/notes/ship-review-2026-08-22-build-gate.md` (supersede at ship)
- `.harness/harness/features/FEAT-32-concurrent-write-merge/runs/t06t10-eng/digest.md` (its Q1-Q7 land on T-08/T-09)
