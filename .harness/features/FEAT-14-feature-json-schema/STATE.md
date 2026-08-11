# STATE

## Current

- feature: FEAT-14-feature-json-schema
- phase: build (entered from plan at `1bdfe3f`; seam note `notes/handoff-plan.md`)
- status: in_progress — BRIEF.md and plan.yaml both `approved` (operator, 2026-08-11)
- branch: feat/204-feature-json-schema · cycles_used 3 of 10 · runs 5

**The build precondition is DISCHARGED.** Verified by me at `1bdfe3f`, not inherited: all 17
features carry a `feature.yaml`; FEAT-16 (`in_review`) and FEAT-17 (`awaiting_user`) both read
`approval: approved` in `plan.yaml` and are idle. No other writer of `feature.yaml` is active.
`jsonschema` 4.26.0 imports. Working tree clean.

### The lane split governs the whole build

Six of twelve tasks are `main-session-direct` and they interleave with the team tasks on the
critical path, so this feature CANNOT run to completion in one orchestrator session. The
segmentation, minimal given the dependency graph:

| Segment | Owner | Tasks |
|---|---|---|
| 1 | me → eng-lead | T-01, T-03 · then the qa gate |
| A | **layer 0** | T-02, T-04, T-06, T-07, T-12 (dependency-ordered, one turn) |
| 2 | me → eng-lead | T-05, T-11 · then the qa gate |
| B | **layer 0** | T-08 |
| 3 | me | T-09, T-10 · qa · panel · goal-check · close-out · briefing |

### Standing hazards, carried into every segment

- **A dead gate exits clean.** `check-plan-routes.py:386` `SHIPPED_STATUSES` and
  `check-state.sh:451` `if _phase not in PHASE_ORDER: continue` both confirmed verbatim at HEAD.
  Deleting `phase` silently voids both. T-11 and T-12 rebuild them; SC-18 refuses "exits 0" as
  evidence, so each gate is proven to FIRE in both directions, by me, at my own tier.
- **gh-sync is radioactive from T-05 to T-08.** It hardcodes `feature.yaml` and returns the EMPTY
  record on absence, re-filing existing issues — external damage `git reset` does not undo.
- **The mirror never opened.** `gh-sync.py open --parent 204` was DENIED by the environment
  classifier. A SKIP, not a gate (DEC-138). It must run at layer 0 and **before T-04**, or not at
  all; every `close-task` is deferred to segment 3.
- **This feature's own state file is inside the corpus it migrates.** T-04 rewrites it and T-08
  converts it to `feature.json`, after which every write I make is schema-validated in-process by
  `check-domain.sh` (T-06). The comment header above cannot survive into JSON.
- **`handoff-build.md` is owed before status reaches `Review`** and the stem stays a lowercase
  literal (D-12) — never derived from a capitalised status value.
- The carve-out scripts and their `test-*.py` files are outside qa's reach; I run those suites
  myself and record exit codes (G-10).

## Open Questions

- Q2 non-blocking: `validate-digest.py:182`'s orchestrator digest enum stays OUT of scope (D-13).
  It carries `blocked` while the six board columns have no `Blocked`. Confirm the boundary.
- Q3 non-blocking: BRIEF.md SC-08 carries one clause twice — spliced mid-sentence and again at the
  close. Every assertion is present and true; only the scope reads ambiguously. Fix is a deletion.
- Q4 non-blocking: T-12's exemption note pins three tokens — `exempt`, the feature name, `handoff` —
  because T-08's verify greps for them, and it must NOT contain `VIOLATION`. Deliberate coupling
  between a carve-out gate's wording and another task's assertion; it rots silently either side.
- Q5 non-blocking: T-04/T-08 `files:` are a glob plus one literal anchor, not 17 literals —
  enumerating all 17 measures 54 machine-field lines against DEC-182's 50 cap.
- Relayed, not FEAT-14's to fix: `.harness/team-config.yaml:15-16` claims check-domain exits 0 on a
  payload with no `agent_type`. FALSE at HEAD (`check-domain.sh:256` sets a flag).
