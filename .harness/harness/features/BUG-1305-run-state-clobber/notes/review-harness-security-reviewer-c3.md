# Security review — c3 (delta at 5ed929bd)

Scope: `1b11bc18..5ed929bd`, `.claude/skills/harness/bin/check-domain.sh` (18 ins / 4 del) +
`tests/integration/test-check-domain.py` (test additions only). `STATE.md`/`feature.json` are
bookkeeping, no security surface. Read at pin via `git show 5ed929bd:<path>`.

## Headline answer

**Failing closed here does not open or widen exposure.** No bounded case found either. The
one narrow caveat (§3b) is a pre-existing gap, unchanged by this diff, not something cycle-13
creates or worsens.

## 1. Availability / DoS against the harness's own agents

No DoS. `sys.exit(0)` → `sys.exit(2)` only fires when `_edit_reconstructed_content` returns
`None` for `RE_STATE_YAML`/`RE_RUN_DIGEST`/`RE_HANDOFF` — i.e. only when the Edit itself could
never have produced a verifiable result. The message names the alternative at source, and it
is real: a whole-file **Write** to the same path.

Traced, not assumed:
- Domain authorization (`domain_check()`, `check-domain.sh:819`) grants by **path glob only**
  (`team-config.yaml` `domain:` lists, walked at `check-domain.sh:250-270` for the
  `HARNESS_RESOLVE_PATH` resolver and identically at `domain_check()`). No grant is tool-scoped
  to Edit-vs-Write. Any agent whose domain covers the target path could already Write it.
- Content shape enforcement (`shape_problems`, `check-domain.sh:1262`, DEC-150) is explicitly
  tool-agnostic by design — the RE_RUN_DIGEST comment at `check-domain.sh:1297` states it
  directly: "This guard fires on Write and Edit: Edit content is reconstructed against the
  on-disk prior before this branch runs." The same `targets` list (content, not tool-name) feeds
  this check whether it came from a successful Edit reconstruction or a Write's `tool_input.content`.
- The one tool-specific branch in the file (`_tool == "Write"`, `check-domain.sh:630`, the
  `main_session.writes` fragment guard) is scoped to `plan.yaml` approval fragments only — it
  never restricts Write on `state.yaml`/`digest.md`/handoff notes.

So Write was already the fully-authorized, fully-validated route for these three artifact
classes before this diff; the diff only stops Edit from silently no-op'ing through a case Edit
could never actually apply. Nothing that needed Edit specifically is now unreachable.

## 2. Message content

Both new messages (`check-domain.sh:2059-2071`) are static strings: no file content, no
absolute path, no run id/uid, no witness internals, no secret. The generic branch and the
`RE_STATE_YAML`-specific branch differ only in which artifact class they name — information
the calling agent already supplied (it chose the target path in its own Edit call). "Issue
1305" is a public tracker reference. No new disclosure.

## 3. Bypass

**(a) Forcing reconstruction to trivially succeed.** Possible (a short/common `old_string`
matched exactly once), but this was already true before 5ed929bd and is not this diff's
concern: a successful reconstruction was, and remains, validated against the *same* DEC-150
shape rules that gate a Write (§1). Trivial-match success routes to enforcement, not around it.
No weakening.

**(b) Unguarded sibling class — real, but pre-existing, not introduced or widened here.**
The new branch covers exactly `RE_RUN_DIGEST`/`RE_STATE_YAML`/`RE_HANDOFF` (plus
`RE_RUN_IDENTITY`, handled separately one branch up by permanent path-only denial). Editing
`feature.json`/`STATE.md`/`CLAUDE.md` (`RE_FEATURE_JSON`/`RE_STATE_MD`/`RE_CLAUDE_MD`, all
members of `SHAPE_PATTERNS` at `check-domain.sh:1244`) via the **Edit** tool at PRE falls
through the *same* `elif _tool != "Write" or not target: sys.exit(0)` (`check-domain.sh:2074`)
that existed before this diff — unconditional exit 0, no reconstruction, no shape check.
`plan.yaml` is separately covered by `approval_guard()` (`check-domain.sh:559`, called from
`domain_check()` at `:968`, a distinct fragment-diff mechanism, not shape rules), so it is not
part of this gap. The gap for the other three is caught only post-hoc (POST re-derives shape
rules from what landed, `check-domain.sh:1104-1114` comment block, "too late to refuse").
This if/elif structure is untouched by `1b11bc18..5ed929bd` — the diff only rewired the
already-in-scope middle branch's failure arm, so this sibling gap is neither created nor
widened by cycle-13. `outside-delta`, recorded and not developed further per dispatch.

## 4. SEC-01 residual (#1376) — composition only, not re-litigated

**Unchanged.** SEC-01 is a run-directory `rm`/`mv` residual, which is Bash-tool surface
governed by `bash-write-guard.sh` — a file this diff does not touch (constraints confirm no
logic change at that seam). The cycle-13 change is scoped entirely to the `_tool == "Edit"`
PRE branch inside `check-domain.sh`'s reconstruction path; `rm`/`mv` never reach that branch
(different `tool_name`, different guard file). No shared code path, no shared state, no
ordering dependency between the two — the fix neither narrows nor widens what SEC-01 already
accepted. Acceptance itself not re-opened.

## Findings

None rise to a gating severity. One recorded, non-gating observation:

- **F-1** (info, `outside-delta`): Edit on `feature.json`/`STATE.md`/`CLAUDE.md` still exits 0
  unconditionally at PRE with no content reconstruction or shape check (`check-domain.sh:2074`),
  relying on POST-hoc detection only. Pre-existing, not touched by `1b11bc18..5ed929bd`. Remedy,
  if ever wanted, is seam logic (extend the reconstruction branch's coverage list) — squarely
  the "no second fix attempt on the seam logic" category, so not proposed for cycle 15.

`must_fix`: none.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Failing closed on unreconstructable governed Edits (5ed929bd) does not open or widen exposure — Write is an already-authorized, already-validated equivalent route for the same three artifact classes; SEC-01 residual is untouched by this diff (different tool, different guard file)."
  severity_max: info
  findings: 1
  must_fix: []
  threat_model:
    - { boundary: "omp Edit payload (file_path only, no old_string/new_string) vs check-domain.sh PRE gate", stride: "T", mitigated: true }
    - { boundary: "Edit-reconstruction-None fail-closed message content (stderr, agent-visible)", stride: "I", mitigated: true }
    - { boundary: "sibling shape classes (feature.json/STATE.md/CLAUDE.md) via Edit at PRE", stride: "T", mitigated: false }
    - { boundary: "SEC-01 run-directory rm/mv (bash-write-guard.sh) composition with this diff", stride: "T", mitigated: true }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1305-run-state-clobber/.harness/harness/features/BUG-1305-run-state-clobber/notes/review-harness-security-reviewer-c3.md
```
