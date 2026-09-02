# Handoff — FEAT-48, build (not executed) → build (main-session-direct) — written at cd8a0c34, seq-9

## Next

**The main session executes T-01 itself. No lead, no squad, no orchestrator.** Every one of the six
executable tasks is `execution_mode: main-session-direct` (DEC-174), and `github-mirror.md:32-34`
assigns exactly that: *"Phases the main session holds itself: plan, ship acceptance, and any
main-session-direct segment."* Dispatching a lead is the team run DEC-174 forbids, on a plan whose
signed `lanes:` declares the carve-out on all three surfaces.

Serial chain, one task at a time: **T-01 → T-02 → T-03 → T-04 → T-06 → T-05**. Per task, in one
act: `plan-merge.py set-task-station --task T-NN --station building`, then `gh-sync.py start-task`
— plan first or the parent write is a silent no-op. Task bodies with `verify:` verbatim at
`plan.yaml` T-01 `:300-448`, T-02 `:449-582`, T-03 `:583-830`, T-04 `:831-1024`, T-06 `:1025-1150`,
T-05 `:1151-1263`.

## Trust

- All 7 tasks are `main-session-direct`; there is no `team` task in this plan — `harness_yaml.load_plan` over every task — verified-at cd8a0c34
- `check-domain.sh` exits **2** for `harness-orchestrator` on `bin/**`, `.harness/harness.json` and `DECISIONS.md`; it permits only the feature-dir note. 8 of 9 task surfaces are closed to me — hook run on real payloads — verified-at cd8a0c34
- Census: **13 sites in 6 files**, not D-10's dated 8 in 4. `test-validate-digest.py` (3 sites) was flagged nowhere before this scan — `notes/census-d10-2026-09-02.md` — verified-at cd8a0c34
- **T-03 cannot ship green until the 5 new sites are fixed**; T-02's derived run set does not reach them, T-03's repo-wide walk does — same note, D-10 "two instruments" — verified-at cd8a0c34
- FEAT-48 carries **zero** `check-state.sh` violations — full run, grepped for FEAT-48 — verified-at cd8a0c34
- Worktree clean at `cd8a0c34` before and after a 257s census that fired every mutation site — `git status --porcelain` empty both times — verified-at cd8a0c34
- `test-check-domain.py` exited 1 once in 5 runs; mechanism **UNVERIFIED**, failing output discarded by my instrument. T-01's verify demands exit 0 — same note — verified-at cd8a0c34

## Dead ends

- **`gh-sync.py`'s review gate is NOT a blocker — `STATE.md`'s open question on it is STALE.** It already tests `finished_stations()`, which returns `('done', 'abandoned')`; its own refusal text reads "done or abandoned". No fix needs to land and no hand-sync is needed — `gh-sync.py:1158-1161`, `factory_config.TERMINAL_MARKER` read live — verified-at cd8a0c34
- Do not re-plan for the widened census. Absorbing a moving `main` with no plan edit is D-10's design and this is its fourth passing test; the lanes glob covers both new files — `plan.yaml` D-10 boundary clause — verified-at cd8a0c34
- Do not add the two new files to any task's `files:`. `amend` cannot write a list field and `apply` refuses a changed value; the receipt names them instead, as the operator already ruled for `test-check-fixture-secrets.py` — `notes/handoff-plan.md` dead ends — verified-at cd8a0c34
- Do not dispatch or edit **T-07**. It is `abandoned` and load-bearing: T-02's verify derives `absorbed` from T-07 being present, abandoned and naming T-02 — `plan.yaml:492`, `:464-467` — verified-at 047f6914
- Do not re-run `gh-sync.py open` — `feature.json`'s `github` receipts make it a no-op — `github-mirror.md` — verified-at 99dab78a
- `review_sha` stays `none`. It pins at the Building → Review seam, after SIMPLIFY, and only once every task is `done` — INV-6, `plan.yaml` — verified-at cd8a0c34

## Working set

- `.harness/harness/features/FEAT-48-parallel-safe-suite/plan.yaml` (the six live tasks; T-07 abandoned)
- `.harness/harness/features/FEAT-48-parallel-safe-suite/notes/census-d10-2026-09-02.md` (derived scope)
- `.harness/harness/features/FEAT-48-parallel-safe-suite/notes/handoff-plan.md` (the plan seam)
- `.agents/skills/harness/references/github-mirror.md` (`:32-34` — who owns a main-session-direct segment)
- `.harness/harness/docs/DECISIONS.md` DEC-174 (`:4271`)
