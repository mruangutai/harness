# Record-integrity audit — validator digest DEC-156 repair (plan cycle 6)

Target: `.harness/harness/features/FEAT-48-parallel-safe-suite/runs/2026-09-01-08-validator/digest.md`
Worktree: `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-48-parallel-safe-suite`

## BLUF

`validate-digest.py` PASSES (exit 0). `git diff` reports 0 insertions / 0 deletions — **not
because the repair is proven additive-only, but because this file is gitignored and was never
tracked by git at any point.** There is no git baseline to diff against, so "zero deletions" here
carries no evidentiary weight about whether the lead's edit was insertion-only. Insertion-vs-rewrite
cannot be established through git for this class of artifact. Only `git status --porcelain` (empty
tree outside the run dir) and `validate-digest.py`'s structural pass are actual evidence collected.

## Check 1 — `validate-digest.py lead`

Command:
```
python3 .claude/skills/harness/bin/validate-digest.py lead .harness/harness/features/FEAT-48-parallel-safe-suite/runs/2026-09-01-08-validator/digest.md ; echo "exit=$?"
```
Verbatim stdout/stderr:
```
digest ok
exit=0
```
**Verdict: PASS** — the DEC-156 block is present and satisfies the lead-digest contract.

## Check 2 — `git diff` (insertion/deletion count)

Commands and verbatim output:
```
$ git -C <worktree> diff --numstat -- <file>
(no output)

$ git -C <worktree> diff -- <file>
(no output)
```
Insertions: 0. Deletions: 0. **But this diff is against nothing** — see Check 3. There is no
committed version of this file to compare against, so `git diff` cannot show what the lead changed,
in either direction. It does NOT confirm "every inserted line sits after the last pre-existing
prose line" — there is no pre-existing tracked state to anchor that claim to. **Deletion-count-is-0
is true but vacuous here; do not read it as proof of an additive-only repair.**

## Check 3 — `git status --porcelain` and gitignore provenance

```
$ git -C <worktree> status --porcelain
(no output — clean/ignored, nothing shown)

$ git -C <worktree> status --porcelain --ignored -- <file>
!! .harness/harness/features/FEAT-48-parallel-safe-suite/runs/2026-09-01-08-validator/

$ git -C <worktree> ls-files -- <file>
(no output — file has never been tracked)

$ git -C <worktree> log --oneline -1 -- <file>
(no output — no commit has ever touched this path)

.gitignore:7 → .harness/*/features/*/runs/**
```
No path outside `.harness/harness/features/FEAT-48-parallel-safe-suite/runs/2026-09-01-08-validator/`
is modified — confirmed, since `git status --porcelain` on the whole tree is empty. The digest file
is **untracked and gitignored by design** (`.gitignore` comment: run dirs are "ephemeral scratch,
pruned on log_retention_days" — deliberately excluded from git to avoid dirtying the working tree /
triggering the SPEC 8.6 dirty-tree halt). This is expected repository behavior, not an anomaly
introduced by this repair.

**Consequence for this audit's actual question:** because run digests are never git-tracked, git
has no mechanism — now or in any future cycle — to verify that a "repair" to a signed run digest is
insertion-only rather than a silent rewrite of prose. `validate-digest.py`'s structural pass (Check
1) verifies the DEC-156 block is well-formed; it does not verify prose was preserved verbatim. This
audit therefore has direct evidence for: (a) contract compliance, (b) no other files touched. It has
**no** git-based evidence for: prose-preservation / rule-15 compliance of the specific edit, because
no prior tracked version of this file exists to diff against.

## Findings

No tampering, scope creep, or record falsification evidenced by the collected data. The one
material finding is a methodology gap, not a code vulnerability: gitignored run-digest files
structurally prevent git-diff verification of "additive-only" repairs to signed records, for this
cycle and every future one. This is a process/tooling gap worth the harness owner's attention, not
grounds to fail this specific repair (which passes every check actually available).

```yaml
VERDICT: PASS
DIGEST:
  headline: "validate-digest.py exit=0 (digest ok); git diff shows 0 insertions/0 deletions — but the file is gitignored and untracked, so that 0 is an absent baseline, not proof of additive-only repair"
  in_scope: true
  scope_reason: "Dispatch names this a record-integrity audit of the repository's own audit trail (a signed governance record under rule 15); explicitly not self-scoped out."
  severity_max: low
  findings: 1
  must_fix: []
  threat_model:
    - { boundary: "signed run-digest prose vs later edits (rule 15, no post-hoc improvement)", stride: T, mitigated: false }
  open_questions:
    - { id: Q1, question: "runs/** is permanently gitignored (.gitignore:7, by design for dirty-tree-halt avoidance), so git diff can never verify insertion-only edits to a signed run digest, this cycle or any future one. Does the harness need a non-git mechanism (e.g. a content hash of the prose region taken at signing time) to make rule-15 compliance on run digests actually checkable, rather than only structurally checkable via validate-digest.py?", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-48-parallel-safe-suite/notes/review-harness-security-reviewer-digestrepair-c6.md
```
