# Research — FEAT-27 arch send-back, cycle 2 (what was re-measured, and what changed)

**BLUF.** All four must-fixes and three advisories are applied in `plan.yaml` and `BRIEF.md`;
approvals stay `pending`. Two things were re-measured at source and one dispatch claim did not
survive. `yaml.safe_load` loads the plan and `check-plan-routes.py` reports 0 violations.

## Re-measured at source (working tree, 2026-08-18)

- `ls -d .harness/*/` returns **five** directories: `expertise`, `factory`, `harness`, `logs`,
  `notes`. **`.harness/codebase/` does not exist** — the send-back listed it among the existing
  first-level directories. MF-2 is unaffected: the glob is still over `.harness/*/`, so N counts
  every first-level directory that acquires an `expertise/` subdirectory, and `.harness/codebase/`
  is a directory the hook *would* read if it were created (`inject-expertise.sh` already points
  `$index` at `.harness/codebase/INDEX.md`). D-01 now states N = 1 today, growing by one per
  repository, with the measured five-directory tree named.
- `grep -i expertise .claude/skills/harness/bin/check-state.sh` returns exactly two lines, `:343`
  and `:353`, both spelling `Expertise` and both INV-9 prose about the `SubagentStart` registration.
  Case-sensitive `grep expertise` returns zero. BRIEF's constraint bullet now says both; the
  conclusion (no carve-out script is edited) is unchanged.
- `grep -rn 'authoritative on conflict'` over `.claude/skills/`, `.claude/agents/`, `SPEC.md` and
  `README.md`: **one hit**, `inject-expertise.sh:64`. So T-02 removing it is the whole removal —
  no other surface carries the phrase, and T-05's new negative greps against `SPEC.md` cannot
  redden pre-existing text.
- `.harness/expertise/` holds 15 files; `harness-frontend-dev.md` is absent. MF-3(b)'s live state
  is confirmed, and T-02 case 10 is written against it.

## Two judgement calls recorded

- **The precedence line is emitted only when at least one repository block is emitted.** With no
  repository tier there is nothing to arbitrate, and an always-emitted line would collide with
  T-02 case 3's absence assertion. Case 3 is therefore strengthened to assert the word
  `repository` appears nowhere at all, which is a stronger negative than the old one.
- **A-3: `paths.expertise_repo` is dropped, not asserted.** No code reads it, T-01's verify cannot
  assert it without adding a grep for prose, and the repository path is already carried by the
  sixteen domain lines plus `SPEC.md` and `README.md` (T-05). T-01's intent now says do not re-add
  it, so the next doer does not restore it as an oversight.

## One thing not claimed

The `[a-z0-9-]+` segment filter is **name hygiene only** — it stops traversal and metacharacters
reaching an interpolated path or header. It does **not** stop a legitimately named stray directory
(`.harness/backup/expertise/harness-qa.md`) from being injected; only D-01's aggregate bound covers
that. D-01 and T-02's intent both say so explicitly, so the doer cannot ship the stronger claim.
