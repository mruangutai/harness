# Handoff — FEAT-32, build → build (successor), written at 805653a + uncommitted, seq-3

## Next

**Step zero: reconcile run `ruling-product`. It was IN FLIGHT when I was stopped.** Its `digest.md` and
`criteria.md` exist and its edits are on disk, but it never notified me, so nothing of it is verified or
recorded in `feature.json`. Read that digest, then re-verify its two edits yourself before trusting them.
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
- `cycles_used` **3** of 10, all from segment A. Runs **12** of 20. **`review_sha` is still `none` and that is CORRECT** — INV-6 fires only once a `squad: validator` run is recorded, so pin it BEFORE recording the qa run — verified-at 805653a
- Coordinator's three measurements, which I did NOT take: a GOVERNED spawn carries BOTH `agent_type: harness-orchestrator` and `tool_input.subagent_type`; payload `cwd` is the FEATURE WORKTREE and the operator ruled the registry root comes from the payload, per worktree; **`claim()`'s docstring is FALSE** — "Never raises for contention" is wrong, it raises `MergeRefusal` after 10.0s, true only of the single-flight refusal which returns `False`. T-06 shipped that sentence — UNVERIFIED by me
- pm's `ruling-product` edits, on disk but UNACKNOWLEDGED: T-13 now reads "at least eight … fired again during the build of its own fix"; SC-13's fragile "four of the six" was REMOVED not incremented; `BRIEF.md:16` still reads seven; `plan.yaml` approval byte-identical — UNVERIFIED, reconcile first

## Dead ends

- **Do NOT attempt `git merge`** — refused by `HEAD_MOVERS`, `bash-write-guard.sh:144`, and the main session ALREADY merged at `805653a`. Retrying wastes a turn and is refused — verified-at 805653a
- **Do NOT ask pm to write `operator-request-*.md`** — its grant is `notes/research-*.md` only; the guard denied my path (#216). The document is `notes/research-FEAT-32-operator-request.md` — verified-at b013dde
- **Do NOT append `test-validate-digest.py` or `test-check-domain.py` to `test_kinds.integration.detect`.** T-10's approved intent names SEVEN paths on the false premise they are absent; they were already PRESENT. All seven now present with count 1 each. I ratified five-not-seven — verified-at 8057a99
- **Do NOT touch `BRIEF.md:16` or SC-14's 221 figure.** The operator declined both; the brief and plan disagree on the count ON PURPOSE — coordinator message, this run
- **Do NOT re-verify the six done tasks**, and do not trust a `digest.md` or `state.yaml` read before its run notifies — both are working state, and this feature has produced false STATE.md entries that way twice — this run
- **Two facts I caught that would otherwise have travelled up as true:** `validate-digest.py` `RANK` is at **:703** (I said :705, coordinator said :702, both wrong); and T-15 was ALREADY done with #715 closed, so "route the one-character fix to pm" was stale and **T-14 is unblocked**, not blocked — verified-at 805653a

## Working set

- `.harness/harness/features/FEAT-32-concurrent-write-merge/STATE.md` and `feature.json`
- `.harness/harness/features/FEAT-32-concurrent-write-merge/runs/ruling-product/digest.md` (reconcile FIRST)
- `.harness/harness/features/FEAT-32-concurrent-write-merge/plan.yaml` (T-13 at 1571-1666, T-17 at 2171-2260)
- `.harness/harness/features/FEAT-32-concurrent-write-merge/notes/ship-review-2026-08-22-build-gate.md` (supersede at ship)
- `.harness/harness/features/FEAT-32-concurrent-write-merge/runs/t06t10-eng/digest.md` (its Q1-Q7 land on T-08/T-09)
