# User answers — FEAT-06 ship gate — 2026-08-04

Taken by the main session from the user directly.

## Q1 (SC-05's count conjunct) — ALREADY CLOSED by the main session. No segment 4 needed.

The user ruled "assert the count exactly" while the briefing was being written. Done, and the trap
named in the briefing was avoided:

- The assertion went into `bin/test-harness-yaml-corpus.py` (now **13** checks), **not**
  `test-team-catalog.py`, whose signed `verify:` requires exactly **ten**. Re-verified: ten.
- `TEAMS_EXPECTED = 2` plus one `check()` on the `counts` dict.
- **Proven both ways**: green on the real tree (13/13); **RED** on a throwaway root whose `teams/`
  holds three files, with the failure naming the directory contents.
- Cost recorded in the code comment: this freezes `teams/` at two, so a legitimate third team
  reddens it — the intended prompt to revisit SC-05, not to silently widen the number.

**SC-05 is now met as written.** pm's goal-check may cite `test-harness-yaml-corpus.py` for BOTH
conjuncts.

## NEW WORK, user-directed at the gate — `personas:` is DELETED from build.yaml

The user asked why `build.yaml` re-listed the Engineering roster when `team-config.yaml` already
holds it. Investigated at source; three findings, all verified:

1. **Nothing reads it at runtime.** `personas` appears nowhere in `harness-team/SKILL.md` or
   `harness/SKILL.md`. The expansion routes by `persona: by_consult_when`, so the lead resolves
   each task against `consult-when` and never consults the list. `review.yaml` has no equivalent
   key. **The only consumer was `test-team-catalog.py` checks (3) and (4)** — i.e. the field existed
   to be asserted, and the assertion existed because the field did.
2. **The guard pointed the wrong way.** Check (3) asserted `listed ⊆ Engineering`. Nothing asserted
   `Engineering ⊆ listed`. Simulated: adding a sixth engineer to `team-config.yaml` left
   `build.yaml` stale and **check (3) still passed**. The copy was unguarded in exactly the
   direction a copy rots.
3. **The header comment contradicted its own list.** Comment (c) said the set "was derived from
   FEAT-03's recorded eng build runs … n = 2 … a FLOOR, not a closed set" — while the list was all
   five Engineering members copied from `team-config.yaml`. Two runs justify a floor of
   `{dev-ops, backend-dev}`, which is what SC-08 asserts.

Origin: `PLAN.md:408-410` instructed the field explicitly. The main session wrote what the approved
plan specified rather than questioning it.

**The user was offered the cheap path (shrink the list to the observed floor, no BRIEF change) and
chose the expensive one deliberately: delete the field and amend the BRIEF.**

### What the main session already did (code only)

- **`teams/build.yaml`** — `personas:` key deleted. Comment (c) rewritten to state that the file
  deliberately does NOT list personas, why (the roster lives in `team-config.yaml`; a second copy is
  data no runtime consults and goes stale the day a member is added), and that the recorded floor is
  evidence from two eng runs on one feature.
- **`bin/test-team-catalog.py`** — checks (3) and (4) rewritten to read `team-config.yaml` directly.
  **Still exactly TEN checks**, as T-07's signed verify requires.
  - **(3) now asserts the single-squad property via the LEAD**: `build.yaml` declares
    `lead: eng-lead`, and `team-config.yaml` records that lead's squad as `eng`. A lead cannot
    dispatch outside its own squad (DEC-118), so a team hosted by an eng-squad lead is eng-squad by
    construction — no roster copy required.
  - **(4) now asserts the recorded floor against the squad that supplies it**: the Engineering
    members include `harness-dev-ops` and `harness-backend-dev`. What makes those reachable at
    dispatch is squad membership, not a list in `build.yaml`.
- **Both proven to discriminate, independently** (two probe bugs found and fixed before trusting the
  result — a truncating `open(p,"w")` that emptied the fixture, and a member deletion that orphaned
  sub-keys and broke the YAML; both made the checks look coupled when they are not):

  | break introduced | (3) | (4) |
  |---|---|---|
  | `lead:` → a non-eng lead | **FAIL** | pass |
  | `backend-dev` renamed out of Engineering | pass | **FAIL** |

  The new checks catch the failure the old pair structurally could not: a squad-membership change
  now reddens a test.
- Gates after the change: `run-unit-tests` 0, `check-docs` 0, `check-state` 0,
  `test-team-catalog.py` 10/10.

### What pm must do — the BRIEF amendment

SC-07 and SC-08 both **presuppose the deleted field** and are now wrong as written:

- **SC-07** — "…and **its declared personas** are a subset of the eng squad's members in
  `team-config.yaml` (DEC-118: a team is single-squad)." With the field gone this passes
  **vacuously** (an absent set is trivially a subset) — this feature's own charter defect.
- **SC-08** — "**`build.yaml`'s declared persona set** covers the personas that FEAT-03's eng-squad
  build runs actually used — `dev-ops` and `backend-dev`…" With the field gone this is
  **unsatisfiable**: an absent set covers nothing.

Reword both to assert the SUBSTANCE the new checks now prove, keeping `verify: automated
evidence: unit`:

- **SC-07's second clause** → `build.yaml` is hosted by a lead whose squad is Engineering in
  `team-config.yaml`, so the team is single-squad by construction (DEC-118). It must NOT be worded
  as a property of a list inside `build.yaml`.
- **SC-08** → the Engineering squad in `team-config.yaml` covers the personas FEAT-03's eng build
  runs actually used (`dev-ops`, `backend-dev`, from `runs/2026-07-31-09-eng/state.yaml` and
  `runs/2026-07-31-10-eng/state.yaml`), so the expansion can route to them by `consult-when`.

Do not weaken either to a presence assertion, and do not renumber. `PLAN.md:408-410` (the T-04
instruction that created the field) and D-03's surrounding text should be corrected in the same run
so the plan does not describe a field the shipped file lacks.

The main session re-signs BRIEF and PLAN after the amendment. Only it writes `## Approval`.

## Q2 (SC-13, the UAT) — NOT YET ANSWERED

The user has `build.yaml` and `SKILL.md:40-53` open and is reading. Do not mark SC-13, do not
assume it, and do not proceed to ship acceptance until they rule.

## Backlog — FOLD INTO SHIP ACCEPTANCE, do not file yet

The user's instruction: create the unfiled backlog items in ONE pass at ship acceptance, together
with whatever they strike. Already filed and needing no action: **#36** (item 1) and **#19**
(item 8). Still unfiled: items 2, 4, 5, 6, 7, plus routing-wall recurrence 7 (item 3), which the
main session argued should be its own issue rather than a comment on **#20** — #20 is about
plan-time domain resolution, while recurrence 7 is a permanent hole: `harness-qa` has no writable
test surface anywhere, since all 13 test scripts live in `bin/`.

Also note **#37** was filed after the briefing was written and is therefore absent from its backlog
table: `adequacy_notes` is load-bearing across tiers and absent from the digest schema.
