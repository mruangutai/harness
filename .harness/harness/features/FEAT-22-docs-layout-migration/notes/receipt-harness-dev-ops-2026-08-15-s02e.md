# Receipt — harness-dev-ops — S-02e — read-only measurement

Task: FEAT-22 S-02e. Read-only. No files edited, no commits made. Repo left exactly as found
(pre-existing dirty state from FEAT-20/FEAT-21 review notes was untouched, not created by this run).

## Answers (headline)

1. **rename path printed by `--name-only` = NEW (destination) only.** Old path never appears.
2. **rename detection is effectively ON** (`diff.renames` unset → git's built-in default is `true`
   for `git show`/`git diff`; `--name-status`/`--name-only` on a commit always run rename detection
   by default regardless of the config knob — the R100 lines below prove it fired).
3. **`audit-decisions.py` exit code = 0**, even though it printed multiple "claimed reversal" /
   misattribution findings. No `sys.exit()` on the finding path — confirmed by measurement, not by
   reading the source.

## Measurement 1 — `--name-only` vs `--name-status` on a rename commit

Located rename commit: `e3e6e79c23315eef6e59165a7724072ade247749` (the docs/features layout move,
`git log --diff-filter=R --name-status --format='%H' -20`).

Command: `git show --name-status --format= e3e6e79c` (first 5 rename lines):
```
R100	.harness/features/FEAT-01/feature.json	.harness/harness/features/FEAT-01/feature.json
R100	.harness/features/FEAT-01/notes/receipt-feature-key-drop.md	.harness/harness/features/FEAT-01/notes/receipt-feature-key-drop.md
R100	.harness/features/FEAT-01/notes/review-harness-code-reviewer-FEAT-01-c1.md	.harness/harness/features/FEAT-01/notes/review-harness-code-reviewer-FEAT-01-c1.md
R100	.harness/features/FEAT-01/notes/review-harness-security-reviewer-FEAT-01-c1.md	.harness/harness/features/FEAT-01/notes/review-harness-security-reviewer-FEAT-01-c1.md
R100	.harness/features/FEAT-01/notes/review-harness-ui-reviewer-FEAT-01-c1.md	.harness/harness/features/FEAT-01/notes/review-harness-ui-reviewer-FEAT-01-c1.md
```

Command: `git show --name-only --format= e3e6e79c`, grepped for the same file's destination path:
```
.harness/harness/features/FEAT-01/feature.json
```
Grep for the OLD path (`^\.harness/features/FEAT-01/feature\.json$`) against the full `--name-only`
output: **0 matches**. Grep for the NEW path (`^\.harness/harness/features/FEAT-01/feature\.json$`):
**1 match**.

**Proof pair** (the two lines):
- `--name-status`: `R100	.harness/features/FEAT-01/feature.json	.harness/harness/features/FEAT-01/feature.json`
- `--name-only`: `.harness/harness/features/FEAT-01/feature.json`

Conclusion: for a renamed file, `--name-only` prints **only the NEW (destination) path**, not the
old one and not both. This matters directly for the plan's `k=$(grep -v '^docs/harness/' "$c" | grep -c .)`
count: each of the 5 `git mv` renames in the audited commit will contribute exactly **1** line
(the destination path) to `--name-only` output, not 0 and not 2 — consistent with the plan's
"29 distinct destination-side paths" framing, *provided* the commit is inspected with `--name-only`
(not `--name-status` mixed in, and not `-z`/raw diff which behaves differently).

## Measurement 2 — rename-detection config

```
$ git config --get diff.renames || echo "(unset)"
(unset)
$ git config --get diff.renameLimit || echo "(unset)"
(unset)
$ git --version
git version 2.50.1 (Apple Git-155)
```

Both are unset in this repo/global config (no override), meaning git falls back to its compiled-in
default, which for modern git (this is 2.50.1) is `diff.renames = true` for commands that show
renames by default (`git show`, `git log --name-status`) — and measurement 1's R100 output is the
direct proof that detection is active, not an assumption from the unset config value alone.

## Measurement 3 — `audit-decisions.py` exit code

```
$ python3 .harness/notes/audit-decisions.py > /tmp/audit-out.txt 2>&1; echo "exit=$?"
exit=0
```

`head -5 /tmp/audit-out.txt`:
```
decisions: 192 top-level (fence-guarded) · 17 amendment headings · 192 index rows

## A claimed reversal not reflected in the target's index ruling  (3)
   - DEC-145:3433 says 'Supersedes DEC-24' — DEC-24's row shows no marker
   - DEC-178:4894 says 'superseded DEC-159' — DEC-159's row shows no marker
```

`tail -3 /tmp/audit-out.txt`:
```
   - DEC-138 amendment at line 4220 is inside DEC-168's section — refs and @anchor get misattributed
   - DEC-138 amendment at line 4248 is inside DEC-168's section — refs and @anchor get misattributed
```

The script printed multiple categories of mechanical inconsistency (reversal-marker mismatches,
misattributed amendment sections) and still exited 0. Confirms by measurement — matching the reader's
own reading of the source (no `sys.exit()` call) — that this script cannot be used as a pass/fail
gate as-is; its findings must be parsed from stdout, not from exit code, if a plan task wants to key
off it.
