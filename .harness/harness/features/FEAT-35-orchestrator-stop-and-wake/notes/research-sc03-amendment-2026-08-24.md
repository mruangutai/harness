# SC-03 amendment — FEAT-35 — 2026-08-24

**SC-03 now grades the reviewer's OWN `agentType`, and says out loud what it therefore does not
cover.** One hunk in `BRIEF.md`; nothing else in the file changed.

Filename note: the dispatch suggested `notes/sc03-amendment-2026-08-24.md`; `check-domain.sh` denies
that path for `harness-pm`, whose per-feature notes path is `notes/research-*.md`. The guard is
right (#216) — this is that artifact.

## Why the old criterion was unclosable — re-derived at source, not taken on report

`.claude/skills/harness/SKILL.md:114` filters candidate sidecars on
`'"agentType":"harness-orchestrator"'` **before** the nonce grep is applied
(`SKILL.md:114-118`: `grep -l ... | sed ... | xargs grep -l ORCH-SELF-7Q4X2M9K`). A reviewer's own
sidecar never carries that type, so the intersection is empty by construction and the single-match
citation SC-03 demanded could never be produced by the persona SC-03 named. The validate panel
measured 0 of 31 in-session against 116 orchestrator-typed machine-wide
(`notes/review-harness-code-reviewer-c0.md`, `runs/2026-08-24-01-validator/digest.md` MF-1). Zero is
the permanent outcome, not a flush delay — the playbook's own "zero matches" branch reads it as
"not flushed yet", which is why the failure looked transient.

**The defect was in the criterion, not the mechanism.** The mechanism is sound; it was pointed at a
persona that cannot satisfy its own filter.

## What the amendment changes

- The `agentType` filter is set to the reviewer's own persona as stand-in.
- Everything else is untouched: verbatim execution, two separate Bash calls, the three recorded
  facts (matching sidecar path, derived agent id, `context-watch.py` row), each cited `file:line`,
  and `verify: inspection` with no `evidence:` field.
- The criterion now names its own blind spot explicitly: the orchestrator-typed glob stays
  unexercised until a real orchestrator runs it post-merge. Proven is the mechanism's *shape*
  (two-call sequence, match-count logic, `context-watch.py` accepting the derived id); unproven is
  that an orchestrator's sidecar satisfies that filter.

Stating the gap is the fix, not a caveat on it. A criterion that hides what it cannot reach reads as
coverage and grades as coverage — the same failure shape as #804's exact-literal greps.

## Scope held

SC-01/02/04/05/06/07, `## Verification gaps`, `## Problem`, `## Goal`, `## Requirements`,
`## Constraints` and `## Approval` are byte-unchanged (`## Approval` still `date: 2026-08-23`, for
the main session to re-sign). SC-05's `partial` grading and its post-merge obligation (answers note
Q2) are the main session's record, deliberately NOT carried here — riding them on a signature scoped
to exclude them is what the operator forbade. No commit; HEAD did not move (`e0ae671`).

## Open

- None blocking. The post-merge exercise of the orchestrator-typed glob is now a stated,
  unowned-in-this-BRIEF gap; if it wants an owner it belongs with SC-05's post-merge obligation,
  which the main session holds.
