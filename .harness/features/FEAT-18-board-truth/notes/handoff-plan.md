# Handoff — FEAT-18-board-truth, plan → build — seq-2, SUPERSEDES seq-1 (its build-branch instruction was falsified by the 2026-08-13 revision). Feature dir UNTRACKED at HEAD `2ccd7f0`; `rev` = revised working tree, 2026-08-13.

## Next

Dispatch nothing until `approval.status` reads `approved` in `plan.yaml` AND `## Approval` reads
approved in `BRIEF.md`. Both are `pending`; the operator signs, the main session writes it. **Q1 rides
to that signature unanswered — the operator's alone, unrecoverable by any agent.**

Once signed: `gh-sync.py open .harness/features/FEAT-18-board-truth` (DEC-138), then the build branch
the ORDINARY way — **`git checkout -b feat/FEAT-18-board-truth`**. Then **T-01 and T-05 in parallel**,
both `depends_on: []` and both team lane, to eng-lead as one selection. **T-02 is
`main-session-direct` and also unblocked; not a squad run, not in the eng dispatch.** T-03 waits on
T-01+T-02, T-04 on T-02+T-03, T-06 on T-03.

## Trust

- `check-plan-routes.py`: `0 violation(s) across 8 plan(s)`, exit 0 — re-run by me AFTER the revision,
  not taken from a digest — verified-at rev
- `check-state.sh` exits 1 with EXACTLY ONE violation, `FEAT-18/BRIEF.md is NOT approved`. That is the
  designed terminal state of a plan mission — **do not "fix" it**; signature clears it — verified-at rev
- Holds at **8 REQ, 6 tasks, 8 decisions**; D-08 and SC-08 remain as entries with strike records
  (DEC-188 shape) so citations land — counted by me — verified-at rev
- T-06's `verify:` now greps `checkout -b feat/` in `SKILL.md`, replacing a grep for `gh issue develop`
  the same revision deletes. Count in `SKILL.md` is **0 today**, so it is discriminating and passes
  only after T-06 §3 writes it. The payload does NOT trip `branch-create-gate.sh` — I fired the live
  gate: exit 0, no adjudication, pattern 1 at `:62` needs a `git` token — verified-at rev
- T-04 alone names a DEC-174 carve-out in `files:` and is declared `main-session-direct`; the route
  check's `DEVIATION … but declared` is the more-restrictive direction, not a violation — at 2ccd7f0
- T-02's `gh_board.py` is `main-session-direct` **by content, not name**: `--resolve` grants it, but
  `check-state.sh` imports it and INV-26's verdict comes from its return value — verified-at 2ccd7f0
- `gh-sync.py`'s `gh()` calls `skip()` → `sys.exit(0)`, so "loud on stderr and the run continues" is
  impossible through it; T-03's `intent:` forbids routing station writes there — D-02 — at 2ccd7f0
- The old four board keys were **pinned node ids**, why a wrong id was silent; D-05's three resolve by name — `branch-create-gate.sh:105-108` — verified-at 2ccd7f0
- DEC-186 authorises the station writes and the session-entry read under its second closed purpose; do not let a reviewer re-litigate it — D-01 — verified-at 2ccd7f0

## Dead ends

- **No `gh issue develop`, and no linking the build branch to the parent issue.** Struck on two
  measurements: the route bypasses `branch-create-gate.sh` entirely, and a linked-branch PR closes the
  parent on merge with no keyword (`stateReason=COMPLETED`), landing the parent card in `Done`
  mid-build under board 3's enabled workflows — `notes/answers-2026-08-13-revision.md`, D-08's strike
  record — verified-at rev
- **Do not teach `branch-create-gate.sh` to parse `gh` subcommands.** The strike closes that gap by not
  opening it — BRIEF out-of-scope fence — verified-at rev
- No `Closes #N` composed into a PR body. The operator's standing preference alone; nothing replaces
  it and nothing needs to — `gh-sync.py ship` already closes the parent and posts the ship review on
  it — BRIEF out-of-scope fence — verified-at rev
- No retry, re-attempt or loop anywhere in `gh-sync.py`. Operator ruling —
  `.harness/notes/grilling-board-truth-2026-08-12.md` `## Settled` — verified-at 2ccd7f0
- No product boards, no `factory_claim.py`. Same shape, but inside FEAT-16's signed plan; #278 —
  verified-at 2ccd7f0
- Do not re-derive the grilling's `## Facts I verified` table nor any measurement in
  `answers-2026-08-13-revision.md` — the operator's standing instruction in that file

## Working set

- `.harness/features/FEAT-18-board-truth/plan.yaml`
- `.harness/features/FEAT-18-board-truth/BRIEF.md`
- `.harness/features/FEAT-18-board-truth/notes/answers-2026-08-13-revision.md`
- `.harness/features/FEAT-18-board-truth/runs/2026-08-13-02-product/digest.md`
