# Grilling — remove executable claims from FEAT-38 — 2026-08-29

Supplements `.harness/notes/grilling-decisions-current-knowledge-2026-08-24.md`, which remains valid
for the fold itself. This round covers only the scope change the operator's REMOVE COMMAND EXECUTION
ruling forces. Prior specification of the redesign is in
`.harness/harness/features/FEAT-38-decisions-current-knowledge/notes/replan-remove-command-execution.md`
— note that its assumed answer to Q1 (mechanism survives declaratively) was **rejected**; the
operator chose removal.

## Destination

FEAT-38 ships the DECISIONS.md fold with **no document-driven command execution anywhere in the
harness**, and with the executable-claims mechanism deleted rather than redesigned. Reaching the end
is: the fold intact, the claims checker and its markers gone, the anchor checker retained, no
remaining script that builds a command line from document or config text.

## Settled

- Does the claim-marker mechanism survive in non-executing declarative form, or go entirely?
  → **Go entirely.** The operator's stated goal for FEAT-38 is removing redundant near-duplicate
  decisions, constant amendments and rulings that reverse themselves. Executable claim-checking was
  machinery layered above that goal, not the goal. Option B chosen after the declarative alternative
  was explained in full.
- Where does the change land? → **Amend FEAT-38.** One id, one branch, one milestone; the landed
  fold work stays with it. BRIEF and plan re-open for re-approval.
- Is the class sweep (former backlog B-9) in scope? → **In scope.** The ruling is about a class of
  risk, so the replan audits the rest of `bin/` for any other code that builds an argv from document
  or config text, rather than filing it separately.
- Does the anchor checker (`check-decision-anchors.py`, T-17) survive? → **Keep it.** Explained from
  first principles and retained: its argv is fixed in its own source, the document contributes
  nothing to it, and it catches citations naming deleted files or out-of-range lines at zero
  authoring cost per claim.
- How are the three previously signed `verify:` corrections (T-10, T-15, T-19) handled?
  → **Hold all three and fold them into the amended plan for one fresh signature.** They are not
  withdrawn; the exact replacement text stays in
  `.harness/harness/features/FEAT-38-decisions-current-knowledge/notes/research-verify-block-defects.md`.

## Not yet specified

- After removal, semantic rot in a citation — a line that still exists but no longer says what the
  entry claims — has no automated detector. The operator accepted that cost implicitly by choosing
  removal; whether anything should replace it later is not yet a sharp question.
- Whether `DEC-205`'s convention needs positive guidance on what an entry does *instead* of carrying
  a checkable claim, beyond simply deleting rule 6b.

## Out of scope

- Redesigning claims in declarative form (`contains` / `max_lines`). Explicitly rejected this round —
  do not carry the two-kind vocabulary from the replan note into the brief.
- Former backlog rows B-8 (harden the executing checker) and B-11 (annotate
  `ALLOWED_GIT_SUBCOMMANDS`): moot, both describe a path being deleted. B-10 superseded — that prose
  is deleted, not patched.
- Merging or opening a PR. The ship decision is not in this pass.

## Facts I verified (so pm does not re-derive them)

- **11 live claim markers, all read-only file reads** — 10 × `grep -F <literal> <path>`, 1 ×
  `grep -c -m 81 -e "" CLAUDE.md`. Measured at `48bbe7e` via
  `git show 48bbe7e:.harness/harness/docs/DECISIONS.md | grep -n '<!-- claim:'`.
- **`DECISIONS.md:6290` is self-referential** — it asserts `ALLOWED_FIRST_TOKENS = {"git", "grep"}`,
  the constant the deletion removes. It must be deleted, not translated.
- **Blast radius outside the feature dir is 5 tracked files** — `check-decision-claims.py`,
  `test-check-decision-claims.py`, `run-unit-tests.sh`, `.harness/harness.json`, `DECISIONS.md`
  (`git grep -ln check-decision-claims 48bbe7e`, feature-dir notes excluded).
- **The anchor checker is not in the same risk class** — `check-decision-anchors.py:111` builds a
  literal `["git", "ls-files"]` argv; no document text reaches any subprocess.
- **The class sweep has a real surface** — 72 files under `.claude/skills/harness/bin/` mention
  `subprocess`, `shlex`, `shell=`, `Popen`, `os.system` or `eval(`. Most are tests invoking fixed
  argv, so the audit is a filtering task, not a one-command answer. `check-decision-claims.py` is the
  only known instance of argv-from-document today.
- **Approval-gated surfaces that move** — `BRIEF.md` REQ-08 ("An entry that states something a
  command can check records that command and its expected…") and SC-09 ("The claim checker runs every
  claim marker…"), plus `plan.yaml` D-10, T-03, T-18, T-19, T-20, T-21. `plan.yaml` currently reads
  `approval.status: approved`, so re-approval is required.
- **`check-state.sh` exits 1 at the worktree** with four violations: FEAT-38 status `Review` with
  `notes/handoff-build.md` missing (DEC-159), and three `runs/**` digests failing the lead digest
  contract (DEC-156). The digests are gitignored and die with the worktree; the handoff gap is a real
  record hole from the blocked ship.
