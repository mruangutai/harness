# Handoff — FEAT-23, plan → build — written at b7ae135, seq-6

## Next

**Nothing is dispatchable until the operator signs.** Both approval blocks read `pending`
(`plan.yaml` `approval.status`, `BRIEF.md ## Approval`); only the main session writes them.
On signature: `git checkout -b feat/FEAT-23-ship-flow-fixes`, then `gh-sync.py open`, then the
build phase. T-01 and T-05 have no dependencies and are the two `team` tasks — start there.
T-02, T-03 and T-06 are `main-session-direct` (no persona is granted `.claude/skills/**` or
`.claude/commands/**`); T-04 is `team` to `harness-documentor` and must run LAST.

## Trust

- All six `verify:` clauses execute and exit 1, each with its own discriminating message — re-run by
  me after every revision — `plan.yaml` tasks[].verify — verified-at b7ae135
- T-02's new dispatch-discipline conjunct is two-way proved: GREEN on a complete fixture, RED on a
  paraphrase, RED on a case-flip — my own probe plus pm's independent route — verified-at b7ae135
- The grep literal `four separate, parallel, read-only dispatches` is byte-identical between
  `plan.yaml` T-02 verify and T-02 intent — extracted and compared programmatically — verified-at b7ae135
- **19 of 20 review findings landed. Arch finding G is NOT applied** — D-05's `because:` and
  DEC-196's prescribed body both name "a second board-writing entry point, and one more call site",
  but neither names the duplicated `load_config` github-block precondition policy nor `gh_board.py`
  as its home. The arch review routed G as the operator's call, not a fix — content grep per
  finding — verified-at b7ae135
- T-03's anchors occur exactly once at `SKILL.md` lines 57 and 59, and line 58 carries a second
  sentence (the DEC-118 one) that must not be split — `sed -n '57,59p'` — verified-at b7ae135
- `run-unit-tests.sh --kind unit` exits 0 in 2.5s; `test-gh-sync.py` is ALL PASSED — verified-at b7ae135
- `test-check-plan-routes.py` case_20 is real and sits in `INTEGRATION_SCRIPTS`, so T-05's
  `--kind unit` conjunct cannot execute it — `run-unit-tests.sh:18` — verified-at b7ae135
- `cmd_abandon`'s early exit is a CONJUNCTION (`gh-sync.py:607`), `cmd_ship`'s is not (`:670`) —
  the reason T-01 item 4 takes the structural remedy — verified-at b7ae135
- `github.attached` is array-of-string (`feature-schema.json:76-79`) — verified-at b7ae135
- No DEC-174 file is touched by any task's `files:` — verified-at b7ae135

## Dead ends

- Do NOT re-litigate the three #430 fixed points — operator ruling in issue #430's comments — source: operator
- Do NOT reopen option (b) for #453 — falsified by `_apply_parent_rule` writing stations with no
  `parent_origin` check while the close is origin-gated at `gh-sync.py:631` — verified-at b7ae135
- Do NOT add a `T-04 → T-01` edge — considered twice and leave-listed; the symbol-citation fix
  removed the exposure — `runs/2026-08-17-5-foldin2-product/digest.md` — verified-at b7ae135
- Do NOT add a `stations` map to `harness.json` or a `plan:` key to `fleet.yaml` — `set_station`
  resolves by name at runtime — `notes/research-FEAT-23-453-station.md` — verified-at b7ae135
- Do NOT trust lead digests over disk on this feature — four runs returned BLOCKED while their work
  had in fact landed; `validate-digest.py --hook` extracts a premature verdict from a lead whose
  member is still in flight — compared returns against `find` — verified-at b7ae135

## Working set

- `.harness/harness/features/FEAT-23-ship-flow-fixes/plan.yaml`
- `.harness/harness/features/FEAT-23-ship-flow-fixes/BRIEF.md`
- `.harness/harness/features/FEAT-23-ship-flow-fixes/notes/research-FEAT-23-foldin-red-runs.md`
- `.harness/harness/features/FEAT-23-ship-flow-fixes/runs/2026-08-17-2-archreview-eng/digest.md`
- `.harness/harness/features/FEAT-23-ship-flow-fixes/runs/2026-08-17-5-foldin2-product/digest.md`
