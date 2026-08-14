# Handoff — FEAT-19-central-product-config, plan → build — written at 63b83c7, seq-1

## Next

Do not dispatch anything. The phase exit is the operator's signature on `BRIEF.md` and
`plan.yaml` (both `approval: pending`), and Q2/Q3/Q4 ride that signature. On approval: create
`feat/FEAT-19-central-product-config`, run `gh-sync.py open`, then start with **T-02**
(`main-session-direct`, kaya's product config) because T-01 `depends_on: [T-02]` — every other
task's ordering follows `depends_on` in `plan.yaml`.

## Trust

- Route resolution is verified, not asserted: `check-plan-routes.py` exits 0, 7/7 routed, 0
  violations — I ran it myself, independently of pm — `.harness/features/FEAT-19-central-product-config/plan.yaml` — verified-at 63b83c7
- No task touches `check-domain.sh`, `bash-write-guard.sh`, `validate-digest.py` or
  `check-state.sh`, so DEC-174's carve-out binds nothing here; D-08 keeps `harness_boundary.py`
  out of every task's `files:` deliberately — plan.yaml `tasks[].files` — verified-at 63b83c7
- T-02, T-03, T-07 are `main-session-direct` because their targets are ungranted, not because of
  DEC-174 — `check-plan-routes.py` output — verified-at 63b83c7
- The plan carries no `file:line` anchors at all; the BRIEF's anchors were re-derived at HEAD and
  its `SC-18` citation is a real invariant, not a dangling ref — `test-factory-config.py:623-629` — verified-at 63b83c7
- eng-lead's F1 (`load_fleet()` binding `FLEET_PATH` at import time, so every fixture test would
  read the live repo's `fleet.yaml` and pass for the wrong reason) is closed in the final T-01
  — `runs/2026-08-13-2-eng/review-architecture-confirm.md` — verified-at 63b83c7
- Branch is `main`, not `feat/FEAT-18-board-truth`; all FEAT-19 artifacts are untracked and
  uncommitted — `git rev-parse --abbrev-ref HEAD` — verified-at 63b83c7
- `check-state.sh` exits 1 solely on FEAT-19's unapproved BRIEF. That is the designed plan-phase
  terminus, not a defect, and it clears on signature — `check-state.sh` output — verified-at 63b83c7

## Dead ends

- Do not re-run grilling and do not re-derive the anchors again from `#206`'s body: its cited
  `check-domain.sh:572-575` and `tests.yml:134-141` are both dead, and the four `[^/]+` regexes
  no longer exist anywhere — `.harness/notes/grilling-central-product-config-2026-08-12.md` `## Fact refresh` — verified-at 63b83c7
- Do not add `mruangutai/harness` to `fleet.yaml` to "finish" the migration — D-01 rules harness
  keeps its own project data local precisely because the entry turns exit 2 into NOBODY — plan.yaml D-01 — verified-at 63b83c7
- Do not rewire `gh-sync.py` to the resolver in this feature — D-06 scopes it to the qa gate only
  and narrows the Goal and REQ-02 in writing to match — plan.yaml D-06 — verified-at 63b83c7

## Working set

- `.harness/features/FEAT-19-central-product-config/BRIEF.md` (18 SC ids, SC-01..SC-17 defined; 8 decisions)
- `.harness/features/FEAT-19-central-product-config/plan.yaml` (7 tasks, `approval: pending`)
- `.harness/features/FEAT-19-central-product-config/DESIGN.md` (the 7-row refusal-message contract; T-01 rows 6-7 are Q2)
- `.harness/features/FEAT-19-central-product-config/runs/2026-08-13-2-eng/review-architecture-confirm.md`
- `.harness/features/FEAT-19-central-product-config/runs/plan-product/digest.md`
