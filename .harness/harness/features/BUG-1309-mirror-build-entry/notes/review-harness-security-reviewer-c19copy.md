# Security review — c19 copy delta — 4857818bb1408813c7a38311d9e4ffc20373427e

**Verdict: PASS, no findings.** Both axes cleared by direct source read; no security-relevant
change in this commit.

## What I measured

**Axis 1 — gate integrity.** Read `merge-gate.py:176-194` (the full owned-feature branch) and the
commit's raw diff for this file (`git show 4857818b -- .claude/skills/harness/bin/merge-gate.py`):
1 file changed, 1 insertion(+), 1 deletion(-), touching only line 192 — the argument string passed
to the existing `deny(...)` call. The condition reaching that call (`entry` not era-exempt, not in
the allow-set `{opened, not-applicable, recovered-terminal}`, `repo_pinned(...)` true) is byte-
identical before and after; the call site, its `return` afterward, and the outer `try/except`
wrapper (`:157`, `:166-194`) are all unchanged. Nothing merge that was denied at the pin's parent
commit is allowed at 4857818b — this is a pure message-body edit inside an unmoved `deny()` call,
never a control-flow or exit-path change. Confirmed, not inferred.

**Axis 2 — information exposure.** The new message (`:192`) embeds `{command_line}`, built at
`:191` from `os.path.realpath(feat_dir)` — an absolute filesystem path surfaced through
`permissionDecisionReason` (`deny()` at `:144-145`, unedited by this commit). `:191` is untouched by
this diff (outside the changed-line range in the `git show` above) and already built the identical
realpath string before this commit — verified by reading the pre-image half of the diff hunk, which
still interpolates `{command_line}`. So the absolute-path emission is **pre-existing, unchanged by
this delta**, not introduced by 4857818b. Confirmed independently that sibling messages at
`:180` (era-exempt allow, stderr) and `:188` (repo-unpinned deny, using `{ROOT}` = `sys.argv[1]`,
also absolute) emit comparable filesystem paths through other, unchanged branches — the pattern is
systemic to the file, not particular to the line this commit touched. If this exposure is ever
judged worth fixing, it is a finding against the *file*, not against this commit, and is explicitly
out of scope per the dispatch's non-goals.

Net effect on exposure: the **old** message additionally echoed the raw `github.build_entry` value
(`recovery-required`/absent-shaped string) inline (`records github.build_entry=<value>`); the
**new** message drops that field entirely. This delta narrows disclosed internal state, if
anything — it does not widen it.

**JSON/social-engineering shape.** `deny()` (`:144-145`) serializes the whole reason through
`json.dumps(...)`, which escapes quotes, backslashes, control characters and non-ASCII regardless
of `reason`'s content — no value substituted into the f-string (`feat`, `command_line`) can break
the JSON envelope. A directory basename or realpath containing shell metacharacters could in theory
render as a misleading paste-and-run instruction to a human operator, but `feat_dir` is resolved
through this repo's own feature-tree bookkeeping (`feature_for(branch)` against `feature.json`
records), not from unauthenticated external input, and the same interpolation pattern
(`{command_line}` verbatim in the message) already existed pre-commit. Not a new risk surface;
noted and dismissed, not silently dropped.

**Test file.** `tests/integration/test-merge-gate.py:64-65,99-102` — predicate re-anchoring only,
matching the new message text and (for the second case) tightening to require both the feature
name and `"gh-sync.py open"` in `reason`. No security-relevant assertion changed or weakened; this
is copy-tracking, not gate logic.

## Findings

None.

## Threat model

| boundary | STRIDE | mitigated |
|---|---|---|
| Hook stdout (`permissionDecisionReason`) reaching operator/transcript | Information disclosure | true — exposure is pre-existing, unchanged by this commit, and this commit narrows it (drops the raw `build_entry` value) |
| Gate deny/allow branch reached by this commit's changed line | Tampering (fail-open) | true — condition and control flow proven byte-identical to pre-commit |
| Reason string → JSON envelope | Tampering (response-parsing injection) | true — `json.dumps` escapes unconditionally regardless of interpolated content |

```yaml
VERDICT: PASS
DIGEST:
  headline: "Pure message-copy change inside an unmoved deny() call; gate condition and control flow proven unchanged, absolute-path exposure pre-existing and this commit narrows it, JSON envelope unbreakable by any interpolated value — no finding."
  in_scope: true
  scope_reason: "Diff touches operator-facing text emitted by a blocking PreToolUse gate (merge-gate.py:192) plus two test predicates re-anchored to it; that output crosses into hook transcripts/operator view, so both gate-integrity and disclosure axes are in scope even though the change is copy-only."
  severity_max: none
  findings: 0
  must_fix: []
  threat_model:
    - { boundary: "hook stdout (permissionDecisionReason) reaching operator/transcript", stride: "I", mitigated: true }
    - { boundary: "gate deny/allow branch reached by the changed line", stride: "T", mitigated: true }
    - { boundary: "reason string interpolation into JSON envelope", stride: "T", mitigated: true }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1309-mirror-build-entry/.harness/harness/features/BUG-1309-mirror-build-entry/notes/review-harness-security-reviewer-c19copy.md
```
