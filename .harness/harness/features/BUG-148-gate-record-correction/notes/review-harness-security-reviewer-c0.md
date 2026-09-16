# Security review — BUG-148-gate-record-correction — pin `87e6033`

## What I examined
- `git diff 41c16c7..87e6033` full patch (all 23 changed files) — confirmed the non-feature-tree
  delta is exactly the three named product paths: `.harness/harness/docs/DECISIONS.md` (DEC-174
  evidence paragraph, +12/-4), `.harness/harness/docs/DECISIONS-INDEX.md` (42/42), and
  `.harness/harness/features/FEAT-05-pyyaml-file-parsers/STATE.md` (lines 11-19, +9/-4). Everything
  else is under this feature's own `features/BUG-148-gate-record-correction/` tree (plan.yaml,
  BRIEF, notes, observations, receipts) — no product surface I need to separately clear.
- `DECISIONS-INDEX.md`'s 42/42 diff, spot-checked past DEC-175..DEC-184: every changed line is a
  `@NNNN` line-anchor shift only (e.g. `@4424`→`@4432`); every ruling clause right of ` :: ` is
  byte-identical. Confirms the contract's "regenerated for shifted anchors, not re-authored".
- Full-diff grep for credential/secret shapes (`api[_-]?key`, `secret`, `password`, `token`,
  AWS-key pattern, PEM headers, `bearer `) across every changed file: the only `token` hits are
  `orchestrator_context_warn_tokens` (a context-budget integer, pre-existing, unchanged) and
  argv-parsing prose ("every other token... fell through") — no credential material anywhere in
  the diff.
- The internal-sha/code-line question (dispatched as the one item in my lane): verified
  `ffbdbfa1` resolves to a real, already-merged commit in this same repository's own history
  (`git show ffbdbfa1`, author Mike Ruangutai, 2026-08-05, `perf(#140): validate argv so --help
  stops rewriting the index`), and the quoted line `stdout_mode = "--stdout" in sys.argv[1:]`
  matches that commit's actual pre-fix behavior — the post-fix script's own docstring
  (`gen-decisions-index.py`, read at the current tip) independently states the same fact ("There
  is no `--check`").

## Verdict on the internal-sha/code-line question — stated both ways
**Not an exposure.** The sha and the code fragment are references into this repository's own git
history, already reachable by anyone with the access level needed to read `DECISIONS.md` itself
(`git show ffbdbfa1`, or the file at that revision). No credential, token, internal hostname,
infrastructure detail, or non-public path is embedded — it is implementation-mechanism prose of the
kind this docs corpus already carries throughout (hook internals, script argv shapes, gate
commands). Nothing is disclosed here that a reader with repo access couldn't already get from `git
log`/`git show` in under a second.
**Where I'd flag it anyway:** if this repository were ever exposed to a materially lower-trust
audience than its current git-access holders (e.g. a public mirror with the private history
squashed away, or an external contractor granted docs-only access without git access), citing a
literal source line and commit sha would leak slightly more implementation detail than a prose-only
description would. That's a hypothetical audience change, not a property of this diff, so I don't
rate it as a finding — the record is only as exposed as the git history it draws from, and that
history includes the full pre-fix file already.

## OWASP / STRIDE pass
- Injection, auth, input validation, dependencies, SSRF: not applicable — the diff is markdown
  prose in two decision/state records and a generated index; no code path, config, or executable
  changed.
- Data exposure / information disclosure (the one live boundary): addressed above — no PII, no
  secrets, no elevated-trust detail beyond what the cited commit already makes public in-repo.
- Repudiation / integrity of the record: DEC-205 governs (current-truth, no amendments) and is
  explicitly the mechanism the correction follows (in-place rewrite, not append) — a decision this
  review doesn't re-litigate, only confirms the diff's shape matches it (no stray insertions
  outside the cited hunks).

## Scope-out reasoning
This diff has no auth, injection, secrets, or credential surface. Its only defensible security
question was the information-disclosure one the dispatch named, and I resolved it: not an
exposure, given the material is already in this repo's own reachable git history.

```yaml
VERDICT: PASS
DIGEST:
  headline: "No security surface beyond the internal-sha citation, which discloses nothing not already in this repo's git history."
  in_scope: true
  scope_reason: "Docs-only diff (DECISIONS.md, DECISIONS-INDEX.md, FEAT-05 STATE.md); the one live question was whether quoting commit ffbdbfa1 and its pre-fix argv line is an information-disclosure concern — assessed and dismissed, both directions stated."
  severity_max: none
  findings: 0
  must_fix: []
  threat_model:
    - { boundary: "internal commit sha + source line quoted in a repo-internal record, read by anyone with repo/docs access", stride: "I", mitigated: true }
    - { boundary: "generated DECISIONS-INDEX.md anchors regenerated from hand-written rulings", stride: "T", mitigated: true }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-148-gate-record-correction/.harness/harness/features/BUG-148-gate-record-correction/notes/review-harness-security-reviewer-c0.md
```
