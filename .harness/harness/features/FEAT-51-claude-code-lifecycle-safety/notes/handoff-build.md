# Handoff — FEAT-51-claude-code-lifecycle-safety, build → validate

## Next

**One main-session-direct fix, then pin and panel.** The build phase is closed: nine of nine tasks
`done`, qa worked to its residual, SIMPLIFY run and applied. The next act is a one-line guard in
`check-domain.sh:1686` — it imports `inflight_registry` **before** the canonical-basename check, so
every governed `Write`/`Edit`/`NotebookEdit` in every session pays it. Measured by the efficiency
reader over 80 runs: **66.6ms at HEAD against 43.0ms at base**, on a hook whose own comment records
~104.7ms. `plan-sign-gate.py:337` defers the identical import correctly *in the same diff*, so the
pattern exists and was simply not applied here. DEC-174 holds `check-domain.sh` main-session-direct,
so no squad can apply it.

Then, in order: `review_sha` pin at the tip **after** that fix commits (INV-6),
`gh-sync.py status <feature-dir> review` in the same act, the validation panel, pm's goal-check
against BRIEF's twelve SCs, and the CEO briefing. Merge, PR and ship acceptance are the operator's.

## Trust

- Nine of nine tasks at station `done`, each with its declared `verify:` passing; T-04, T-06 and T-08 I re-ran at my own tier — `plan.yaml` read with `yaml.safe_load` — verified-at 6db25ba2 and later
- `run-unit-tests.sh --kind unit` exit 0, 519 PASS, 0 FAIL — captured the runner's own status in a variable, counted `^FAIL ` lines — verified-at the pre-SIMPLIFY tip
- `--kind integration` exit 1, 742 PASS, **7 FAIL, all the `test-check-plan-routes.py` manifest-DEVIATION family** — same method — verified-at the pre-SIMPLIFY tip
- Those 7 are caused **solely** by T-03's approved route line: `diff` of the main and worktree `team-config.yaml` returns exactly that route plus its comment and nothing else, and `_manifest_deviation`'s own docstring records that a route change deviating is intended. Removing the other cause moved 9 → 7 exactly — I ran the diff and both suites myself — verified-at 344f3c84..HEAD
- The deviation is **not** an environment artifact: `HARNESS_PROJECT_DIR` pointed at the worktree changes nothing, because the checker resolves routes against the *owner* manifest, which is what the hook consults — probed myself — verified-at the pre-SIMPLIFY tip
- `quarantine.py` works end to end against its real dependency: `list` read-only by sha, illegal basename exit 2, `adopt` of `BRIEF.md` replacing and leaving the directory, `discard` refusing outside a quarantine segment; and on the delegation path 14 tasks + 1 = 15 ids with the approval byte-identical, `plan-merge.py` exit 7 and exit 8 surfaced verbatim — two throwaway roots, run by me — verified-at e47afa3f
- T-08's three DEC-210 guards each discriminate: six mutation probes, one per clause plus heading-removal and row-removal, each reddening only its own test — my own probe, in a throwaway repo root, including the row-removal case the squad did not run — verified-at 6db25ba2
- T-05's four playbook clauses each discriminate independently against the pre-change playbooks through `TEAM_PLAYBOOK_PATH` and `PLAYBOOK_PATH` — I ran both — verified-at f260b5fb
- DEC-199's two falsified claims are amended and the `ONCE_RE` floor re-measured at three qualified occurrences; `DECISIONS.md` is now that check's **only** bound site, T-05 having removed `inflight_registry.py` — the fix cycle measured it and I measured the before-state myself — partially UNVERIFIED after the amendment
- SIMPLIFY applied exactly one change, the `COLLECT_FIXTURE` hoist to `SHARED_MANIFEST_PATHS`, and claims the gate baseline is unchanged — **UNVERIFIED at the time of writing; a re-run of both kinds was in flight**

## Dead ends

- Do not try to make the integration kind green in this worktree. The seven DEVIATION failures are true, intended, and unsatisfiable until merge; the manifest diff and the function's own docstring both say so — verified-at the pre-SIMPLIFY tip
- Do not route the seven to a fix cycle or to pm. There is no in-worktree remedy and no plan change closes them; they are gate-placement debt for the operator's ruling — the validator lead reached the same conclusion independently — verified-at 2026-09-01-03-validator
- Do not dispatch a squad for `check-domain.sh`, `validate-digest.py`, `inflight_registry.py`, `plan-sign-gate.py`/`.sh`, their test files, or the two playbooks. DEC-174 holds them main-session-direct and `check-plan-routes.py` records four of them as declared deviations — verified-at 0bc57c88
- Do not commit before re-running both kinds yourself. The SIMPLIFY apply touched a test file and its baseline claim has not been independently confirmed — this note's own Trust section — verified-at now
- Do not treat a green `run-unit-tests.sh` tail as a green suite. Its last line is the last script's own `N/N checks passed`; count `^FAIL ` lines and capture the runner's exit status in a variable — cost this feature one false report already — verified-at 2026-09-01-01-eng
- Do not assume an editor write landed in this worktree. A repo-relative write resolved against the **main checkout** twice in this feature, silently, because both copies were byte-identical; use absolute paths and check `git -C /Users/molchairuangutai/GitHub/harness status --porcelain` after — measured twice, both instances cleaned — verified-at now

## Working set

- `.harness/harness/features/FEAT-51-claude-code-lifecycle-safety/plan.yaml`
- `.harness/harness/features/FEAT-51-claude-code-lifecycle-safety/notes/qa-2026-09-01-03-validator.md`
- `.harness/harness/features/FEAT-51-claude-code-lifecycle-safety/runs/2026-09-01-2-simplify-eng/digest.md`
- `.harness/harness/features/FEAT-51-claude-code-lifecycle-safety/BRIEF.md`
- `.claude/skills/harness/bin/check-domain.sh`
