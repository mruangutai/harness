# Receipt — harness-dev-ops — FEAT-22 S-02c (measurement only)

BLUF: `git show --name-only --format= <sha>` prints **ONE line per rename — the destination path
only.** A verify that walks `--name-only` output expecting to see the OLD path (e.g. for a
`grep -v '^docs/harness/'` check meant to catch stragglers left under the old location) will never
see it — the source path is not in that output at all. Only `--name-status` carries both old and
new paths (tab-separated, on the `R<score>` line). Any verify logic that assumes `--name-only`
surfaces renamed-FROM paths is checking the wrong stream.

## M-1 — does `--name-only` print 1 line or 2 for a rename?

Commit used: `aa18302` (small, clean single-rename commit — `2 files changed, 3 insertions(+), 3 deletions(-)`).

```
$ git show --name-status --format= aa18302
R092	.claude/commands/harness-grill.md	.claude/commands/harness-grilling.md
M	.claude/commands/harness.md
```

```
$ git show --name-only --format= aa18302
.claude/commands/harness-grilling.md
.claude/commands/harness.md
```

- `--name-status`: **2 columns for the rename line** (score, old path `harness-grill.md`, new path
  `harness-grilling.md`), tab-separated, `R092` prefix.
- `--name-only`: **1 line for the rename** — `.claude/commands/harness-grilling.md` (destination
  only). The old path `harness-grill.md` does **not** appear anywhere in `--name-only` output.
- Output does **not** begin with a blank line — verified via `head -c 50 | xxd`: first bytes are
  `2e63 6c61 7564 65...` = `.claude` immediately, no leading `\n`.

(Cross-checked against a larger rename commit `e3e6e79` — same shape held: every `R` line in
`--name-status` had a corresponding single destination-only line in `--name-only`, no source paths
present in `--name-only`.)

```
$ git --version
git version 2.50.1 (Apple Git-155)

$ git config --get diff.renames
(empty / exit 1 → unset)
```

## M-2 — pin

```
$ git rev-parse HEAD
0f12f14c166d231ddf648cc00ff4d12029ce0122
```
Matches expected `0f12f14`.

```
$ git status --porcelain | head -20
 M .harness/logs/2026-08-15.md
?? .harness/harness/features/FEAT-20-migration-detector/notes/review-harness-code-reviewer-premerge.md
?? .harness/harness/features/FEAT-20-migration-detector/notes/review-harness-qa-premerge.md
?? .harness/harness/features/FEAT-20-migration-detector/notes/review-harness-security-reviewer-premerge.md
?? .harness/harness/features/FEAT-21-features-layout-migration/notes/review-harness-code-reviewer-2026-08-15-rereview.md
?? .harness/harness/features/FEAT-21-features-layout-migration/notes/review-harness-qa-2026-08-15-rereview.md
?? .harness/harness/features/FEAT-21-features-layout-migration/notes/review-harness-security-reviewer-2026-08-15-rereview.md
?? .harness/harness/features/FEAT-21-features-layout-migration/observations/harness-qa.md
?? .harness/harness/features/FEAT-21-features-layout-migration/observations/harness-validator-lead.md
?? .harness/harness/features/FEAT-22-docs-layout-migration/
```
(Pre-existing untracked/modified state, not created by this measurement run — this run's only write
is this receipt, under the already-untracked `FEAT-22-docs-layout-migration/` directory.)

## M-3 — `docs/harness` references in `test-check-domain.py`

```
$ grep -cE 'docs/harness|"docs", ?"harness"' .claude/skills/harness/bin/test-check-domain.py
19
```

```
$ grep -nE 'docs/harness|"docs", ?"harness"' .claude/skills/harness/bin/test-check-domain.py | tail -5
820:    os.makedirs(os.path.join(esc_root, "docs", "harness"))
823:               os.path.join(esc_root, "docs", "harness", "esc"))
824:    esc = fire_abs(esc_root, os.path.join(esc_root, "docs", "harness", "esc",
826:    legit = fire_abs(esc_root, os.path.join(esc_root, "docs", "harness", "guide.md"),
924:    r = hook("docs/harness/SPEC.md", "harness-documentor")
