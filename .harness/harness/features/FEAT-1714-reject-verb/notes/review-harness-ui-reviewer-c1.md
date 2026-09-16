# UI review — FEAT-1714-reject-verb — cycle 1

## Verdict

PASS, with ADV-02 retained as a medium advisory. Mode B reviewed only immutable pin `8090ce0b0fd8eb9d12c63df83ef9cb45a7b38125`, range `a3bdb2ac3c49f7ba13fc64bc8c9b349588f3d732..8090ce0b0fd8eb9d12c63df83ef9cb45a7b38125`.

## Measured scope basis

- The pinned c1 range contains exactly 9 changed paths: 7 `.py` and 2 `.md`.
- Rendered-interface extension census (`html`, `htm`, `css`, `scss`, `sass`, `less`, `tsx`, `jsx`, `vue`, `svelte`, `svg`) returned 0 paths.
- Direct pinned-object check found no `.harness/harness/features/FEAT-1714-reject-verb/DESIGN.md`.
- Therefore rendered UI, visual fidelity, focus, pointer targets, accessibility controls, and dark/light theme parity are not applicable. The dispatch explicitly places the changed operator-facing terminal confirmation in scope, so that text-only surface was audited without inventing rendered-UI requirements.

## ADV-02 reassessment — retained

**ADV-02 — med · substance · owner T-02.** Dry-run still omits the exact reason/comment that confirmation will publish.

**Concrete scenario:** an operator supplies a stale or mistyped one-line reason and runs without `--yes`. The preview identifies the target and successor disposition but never displays the reason. The operator then re-runs with `--yes` and publishes unseen text. This occurs for a recorded parent and a first-sync/no-parent source ticket, with either a numeric successor or `none`.

**Pinned evidence:** `.claude/skills/harness/bin/gh-sync.py:1813-1824` constructs the posted body as `Superseded by #N: <reason>` or `No successor was named: <reason>`. However, `_reject_steps` reduces that body to only `link to superseding issue #N` or `record that no successor was named` (`:1903-1913`), and the dry-run prints only those step labels (`:1947-1963`). Parent labels at `:1873-1883` and source-ticket labels at `:1886-1900` both consume the reduced disposition, not the exact comment. The c1 tests likewise assert only generic tokens for the parent preview (`tests/integration/test-gh-sync-abandon.py:645-658`) and source-ticket/parent/station identity for first sync (`:716-730`), so they do not close this advisory.

The c1 change improves the preview by accurately distinguishing parent versus source-ticket disposition and by listing mutation order. It does not address the c0 defect's exact shape. The output remains sequential, target-attributed, and readable; no colour-only encoding, spatial interaction, focus management, or theme token is involved. Rendered-size/layout is not verifiable from source, but no rendered surface exists.

```yaml
VERDICT: PASS
DIGEST:
  headline: "No rendered UI exists; the terminal preview is readable, but ADV-02 remains because it still hides the exact comment reason before confirmation."
  mode: B
  in_scope: true
  severity_max: med
  findings:
    - id: ADV-02
      kind: substance
      scope: task
      severity: med
      reader: ui-reviewer
      owner: T-02
      summary: "Dry-run omits the exact reason/comment later posted in both parent and no-parent branches."
      scenario: "A stale or mistyped reason is not shown before the operator re-runs with --yes, so unseen text is published."
      why: "The comment body includes the reason, while the preview renders only the successor disposition."
  must_fix: []
  states_unspecified: []
  contract_violations:
    - path: ".claude/skills/harness/bin/gh-sync.py:1813-1824,1873-1913,1947-1963@8090ce0b0fd8eb9d12c63df83ef9cb45a7b38125"
      actual: "Preview prints only the target and successor disposition."
      specified: "T-02 requires the no---yes report to print the exact comment."
  a11y: []
  open_questions: []
  files_touched:
    - ".harness/harness/features/FEAT-1714-reject-verb/notes/review-harness-ui-reviewer-c1.md"
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1714-reject-verb/.harness/harness/features/FEAT-1714-reject-verb/notes/review-harness-ui-reviewer-c1.md
```
