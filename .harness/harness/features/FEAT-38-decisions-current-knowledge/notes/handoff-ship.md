# Handoff — FEAT-38-decisions-current-knowledge, ship → user gate — written at 2557950, seq-1

## Next

**Do not dispatch anything. The ship phase ended at its user gate and the gate is unrun.**
Present `notes/ship-review-2026-08-29-16.md` to the operator. Four asks, in this order: run the UAT
at `notes/uat-FEAT-38.md` (`gates.uat` is `blocking_when_uat_criteria_exist`, so it BLOCKS the ship
decision); decide the three `main-session-direct` tasks T-14, T-22, T-23; strike unwanted rows from
the 18-row proposed backlog; and sign or decline the three `verify:` amendments in
`notes/research-verify-block-defects.md`.

**T-14 is the one with real work in it** — 18 citations in 13 files, listed per file and per line in
`notes/research-FEAT-38-goalcheck-2557950.md`. **SC-04 is `not_met` solely because of it.** All 13
paths return `NOBODY` from `check-domain.sh --resolve`, re-measured this run, so no squad can be
given them.

After T-14/T-22/T-23 land: set their `status: done` in `plan.yaml`, then run
`gh-sync.py status <feature-dir> Review` — it refused this run because it requires every task done.

## Trust

- `review_sha` is `2557950`; suite green there — exit 0, 0 `FAIL`, 1117 `PASS`, 0 anchored `^KIND-DRIFT:` — `run-unit-tests.sh`, output captured into a variable, never piped — verified-at 2557950 by the orchestrator, and independently by qa
- 11 of 13 SCs met; SC-04 `not_met` (T-14), SC-13 `unrun` (operator) — `notes/research-FEAT-38-goalcheck-2557950.md` — verified-at 2557950
- The RCE is closed: `git -c "alias.zz=!<cmd>" zz`, `-c core.fsmonitor=`, `-c diff.external=` all refused with payloads unexecuted, driven through the checker itself — verified-at 2557950 by the orchestrator, then probed for BYPASSES (not re-runs) by the security reviewer
- `DECISIONS.md` byte-frozen at 6299 lines; `gen-decisions-index.py --stdout` diffs clean against the committed index — the feature's one authoritative index-freshness gate — verified-at 2557950
- `DECISIONS.md` is byte-identical between build tip `b32013c` and the pin, so the UAT reads the reviewed tree — `git diff b32013c 2557950 -- <path>` empty — verified-at 2557950
- Both new checkers proved able to REDDEN, by orchestrator mutation with byte-verified restore (md5 match, empty `git status`) — verified-at 3928c70, and re-observed by pm at the pin
- All 15 deleted ids confirmed gone INDIVIDUALLY, not by a file-global count — verified-at 2557950
- Cycles 9 of 10; runs 16 of an informational 20 — `feature.json` — verified-at 2557950
- The main checkout holds no tracked modification from this feature, but one stray reviewer artifact was written there and needs deleting — `git -C /Users/molchairuangutai/GitHub/harness status --porcelain` — verified-at 2557950
- SC-11's meaning-preservation: 10 of 15 entries sampled by the panel, 5 by pm, 15/15 covered — panel and goal-check digests — **the 5 pm graded were not independently re-checked by me**; UNVERIFIED at my own tier

## Dead ends

- Do not re-report SC-04 as a squad gap — carved out to T-14, all 13 paths `NOBODY`; superseded only by the main session doing it — verified-at 2557950
- Do not re-run T-03, T-21, T-06 or T-10's `verify:` blocks expecting green — all four are order-dependent or miswritten; T-03 and T-21 assert an index orphan that T-11 legitimately removed, and T-06/T-10 demand a `FAIL` line T-11 turns green — verified-at 2557950
- Do not root any citation sweep at `.agents/**` — symlink onto `.claude`, so a recursive grep traverses nothing and returns a confident zero — `grep -r` over `.agents/` returns 0 where `.claude/skills/harness/SKILL.md` returns 3 — verified-at 2557950
- Do not edit `DECISIONS.md` or `DECISIONS-INDEX.md` without regenerating the index in the same act — one inserted line re-drifts 24+ `@<line>` rows and breaks the diff-clean gate — verified-at 2557950
- Do not fix the RCE by blacklisting git config keys — `alias.*`, `core.fsmonitor`, `diff.external` are three of many; the shipped fix bounds by position and shape instead — verified-at 2557950
- Do not treat the `gh-sync.py status Review` refusal as a failure — it requires every task `done` and three are legitimately pending; the mirror is never a gate — verified-at 2557950

## Working set

- `.harness/harness/features/FEAT-38-decisions-current-knowledge/notes/ship-review-2026-08-29-16.md`
- `.harness/harness/features/FEAT-38-decisions-current-knowledge/notes/uat-FEAT-38.md`
- `.harness/harness/features/FEAT-38-decisions-current-knowledge/notes/research-FEAT-38-goalcheck-2557950.md`
- `.harness/harness/features/FEAT-38-decisions-current-knowledge/notes/research-verify-block-defects.md`
- `.harness/harness/features/FEAT-38-decisions-current-knowledge/feature.json`
