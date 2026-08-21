# UI review — FEAT-30-worktree-per-feature — scope check at a76d69a

**Scoped out. No UI surface in this diff.**

## Evidence

`git -C <repo> diff --stat 49c528a a76d69a` — 45 files changed, 5595 insertions(+), 170
deletions(-). Extension census against `*.html *.css *.scss *.tsx *.jsx *.vue *.svelte *.less
DESIGN.md` matched exactly one file:

```
.../notes/ship-review-2026-08-20-01-build-eng.html | 99 ++++++++++++++++++++++
```

Inspected it directly (`git show a76d69a:...ship-review-2026-08-20-01-build-eng.html`): it carries
CSS custom-property tokens and a `prefers-color-scheme`/`data-theme` dark-mode block. That looks like
design work at a glance, but a repo-wide check shows it is not new: an identical template already
exists for ~15 other features going back to FEAT-03 (`ship-review-*.html` under
`FEAT-{03,04,06,10,11,12,13,14,20,21,22,23,24,25,27,29}`). This is the orchestrator's standing
ship-review-to-HTML rendering convention, not a surface FEAT-30 introduces or owns. FEAT-30's own
content in it (`ship-review-2026-08-20-01-build-eng.md`, the markdown twin) is a Q1 escalation about
a guard-allowlist contradiction — no design content.

No `DESIGN.md` exists under this feature's `notes/`. The sixteen named source/config files
(`harness-orchestrator.md`, `harness.md`, the two SKILL.md files, and the `bin/*.py`/`*.sh` files)
plus `.harness/harness.json` and `SPEC.md` are backend tooling and docs — no template, no CSS, no
markup, nothing a human renders and judges by appearance.

## Adjacent question (per dispatch): operator-facing CLI output intelligibility

Checked `feature-worktree.py`'s stdout/stderr lines and `bash-write-guard.sh`'s refusal text.

- `feature-worktree.py`: every error line is `feature-worktree: <subcommand>: <what> <value>` (e.g.
  `create: destination already exists: <dest>`, `remove: not a linked worktree of <root>: <dest>`);
  status lines during removal are single verbs + path (`WOULD DISCARD <path>`, `MISSING <rel>`,
  `DIFFERS <rel>`, `VERIFIED <rel>`, `REMOVED <dest>`). Consistent grammar, names the noun and the
  path in every case. Intelligible.
- `bash-write-guard.sh`: refusals follow `bash-write-guard: BLOCKED — <reason>`, and the reason
  names the specific subcommand and why it is undecidable/refused (e.g. "`git worktree <sub>`
  carrying a force flag..."). Intelligible.

No finding to raise here — reporting `info`-only per dispatch instruction would apply only if
something were unintelligible; nothing was.

## Not verifiable from source

Rendered appearance of the ship-review HTML template (spacing, contrast, layout at real window
sizes) is not verifiable from source — but that template is pre-existing and unowned by this
feature, so it is out of remit regardless.
