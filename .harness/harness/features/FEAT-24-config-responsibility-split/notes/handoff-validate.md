# Handoff — FEAT-24, validate → ship decision — written at 0c11e23, seq-1

## Next

**Present `notes/ship-review-2026-08-19-ship-02.md` verbatim and take the operator's decision.**
Nothing else runs until then. Two rulings are named in it: SC-05's scope (priced by a six-path
measurement, not escalated as an open question) and whether to pin five cases that guard real
defects but are referenced by no `verify:` block. On acceptance the unstruck backlog rows become
issues via `gh-sync.py backlog`, and `gh-sync.py ship` closes the milestone — **both are the main
session's subcommands, not mine.** No PR is open and nothing is merged.

## Trust

- All ten tasks `done` and committed; 17 commits on the branch; every sub-issue closed; parent
  derived to `Review` — `plan.yaml`, `feature.json` — verified-at 0c11e23
- **FEAT-24's own `check-state.sh` violations: ZERO.** The four remaining all belong to paused
  FEAT-25/26/27 dirs — verified-at 0c11e23
- Full suite: zero FAIL lines, exit 0 — `run-unit-tests.sh --kind all` — verified-at 0c11e23
- pm's goal-check: **7 met, 5 partial, 1 split, nothing broken behaviourally.** Partial always means
  evidence durability, never behaviour — `runs/2026-08-19-11-product/digest.md` — verified-at 0c11e23
- **SC-06 was closed after the panel FAILed it** and I mutation-proved the fix myself by neutering
  the parse raise at runtime: exactly one FAIL, the named case — verified-at 0c11e23
- `load_board` has SIX non-error paths, FIVE meaning "no board"; only `github` present with no
  `board` key raises. This is what prices SC-05 — verified-at 0c11e23
- **My earlier claim that three cells return `None` was WRONG** — the probe passed a file path where
  the function takes a repository root, so it hit file-not-found every time. pm's reading stands
  over mine — verified-at 0c11e23
- Expertise: `check-expertise.sh` exits 0 over all 15 files; each lead verified no wipe by entry
  TEXT, not counts — verified-at 0c11e23
- **Cycles 9 of 10 — one left.** Runs 24 against an informational budget of 20 — `feature.json` —
  verified-at 0c11e23

## Dead ends

- Do not open another repair round casually: one cycle remains and exhaustion is a hard BLOCKED —
  source: DEC-157, `harness.json` budgets
- Do not treat `max_total_runs` as a stop; it is informational and two leads escalated wrongly on it
  — source: `harness.json:167`, "it never stops a branch"
- Do not try to apply another agent's Expertise ops: `check-domain.sh --resolve` grants each file to
  its own agent alone, orchestrator included in the exclusion — verified-at 0c11e23
- Do not reconstruct the three reviewers' verbatim ops from headlines — the text is gone, and
  inventing it into a per-spawn-injected file is the defect this feature exists to remove — source: this session
- Do not read an empty grep as a clean result, and do not trust a green suite as evidence an
  integration works — both failed here — source: this session
- Do not touch `FEAT-25-*`, `FEAT-26-*`, `FEAT-27-*`, and do not stage with `git add -A` or
  `git add .harness` — source: this session's constraints

## Working set

- `.harness/harness/features/FEAT-24-config-responsibility-split/notes/ship-review-2026-08-19-ship-02.md`
- `.harness/harness/features/FEAT-24-config-responsibility-split/runs/2026-08-19-11-product/digest.md`
- `.harness/harness/features/FEAT-24-config-responsibility-split/runs/2026-08-19-9-validator/digest.md`
- `.harness/harness/features/FEAT-24-config-responsibility-split/STATE.md`
- `.harness/harness/features/FEAT-24-config-responsibility-split/notes/research-FEAT-24-goalcheck.md`
