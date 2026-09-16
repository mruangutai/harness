# UI Review — BUG-1290-factory-claim-repo-root — Mode B — c1

**Verdict: PASS.** No user-facing surface in this diff carries a defect. The one operator-visible
change is the bug fix REQ-03/SC-03 require, and it is correct.

## What I read

- `git -C <worktree> diff 4e52d2e3..76e26386 --name-only` (21 files) and the code-only range
  `4e52d2e3..419614e5` (9 files, the CODE commits per the panel contract).
- Full diff body of all five production files: `factory_claim.py`, `factory_config.py`,
  `feature-worktree.py`, `layout_fixtures.py`, `layout_migration.py`.
- `git diff --name-only … | grep -Ei '\.(html|css|scss|less|tsx|jsx|vue|svelte)$'` → zero matches
  (exit 1). No rendered-UI file type touched anywhere in the diff.
- `git show 76e26386:…/DESIGN.md` → does not exist. Expected: DEC-139 excludes design/product
  segments from BUG flows; this is not a finding.
- `git show 4e52d2e3:.claude/skills/harness/bin/factory_claim.py | grep -n "feature root does not
  exist\|missing or unparseable"` — confirms the `no_plan` refusal's English wording existed
  **byte-identical** at the pre-change commit; the diff changes only the *value* fed into `{path}`,
  never the template.
- `git diff … | grep -n '^\+.*print(\|^\+.*refuse\|^\+.*sys.exit'` across all five production
  files → zero hits. No new stdout/stderr/exit-producing statement anywhere in this diff.

## The one operator-visible surface: `factory_claim.py`'s `no_plan` refusal

This is a batch CLI tool (`factory_cli.py`'s documented stdout/stderr/exit-code grammar); the only
surface that can exist is that grammar, not a rendered UI.

Before this change, `_BlockerCache.plan_path` built `{path}` from a single module-level
`FEATURES_ROOT` constant resolved once at import against `harness_boundary.resolve_root(_BIN_DIR)`
— correct for the tool's own repo, wrong for every *other* repo the poll serves (the bug this
feature fixes). After: `plan_path(repo, feature)` routes through the new
`factory_config.features_root(repo)`, which resolves `<root>/.harness/<repo's own segment>/features`
per repo. The English template in `_blocker_reason_text` — "issue #{num} carries a feature: label
that resolves, but no plan could be read at {path} - the feature root does not exist" / "...the
feature directory or its plan.yaml is missing or unparseable" — is untouched (confirmed above); only
the path value is now correct and repo-scoped. This is exactly REQ-03 ("naming the resolved absolute
path") and SC-03 ("that path carries the repository's segment"). Judged against the surrounding
file's conventions: composed through `factory_cli.refuse`/`fail`'s one canonical grammar
(`factory: {tool}: {what}: {value} — {next_step}`), consistent with every other refusal in this
file — no new line, no new format.

Emission path traced: `_blocker_reason_text` → `factory_cli.refuse(...)` (stderr + exit 2) when
`--issue` is given, else a stderr `skip #{num} — {reason}` print. Both are local-operator-only;
`_emit`'s only GitHub-facing write is the unrelated `factory_cli.payload` JSON for the *winning*
claim, which never carries a blocker reason. So the absolute path this fix now surfaces is visible
only in the operator's own terminal/log, never posted into a shared issue — the "is an absolute
path leaky" question the dispatch anticipates is lower-stakes than a public surface would make it,
but it remains the operator's call per the dispatch's own framing, not mine to fix.

`feature-worktree.py`'s one changed line (`segment = factory_config.segment_of(repo)` replacing the
inline `repo.split("/", 1)[-1]`) computes the identical value — confirmed identical split
expression inside `segment_of`'s body. Zero observable output difference.

## Files with no operator-facing surface at all

- `factory_config.py`: adds `segment_of`/`features_root` (pure helpers, no I/O, no print).
- `layout_fixtures.py`: test-fixture STUB dict content (used only by the test suite, never run
  against the operator).
- `layout_migration.py`: one `READER_TABLE` row's target path updated (`factory_claim.py` →
  `factory_config.py`, matching the D-04 code move) plus an explanatory comment. `render`,
  `blame_text`, `cause_text`, `exit_code` — the functions that actually produce this tool's
  operator-facing migration report — are untouched by this diff. This row is one of the FIVE
  SIGNED CHOICES named in my dispatch (item 2: the paren-free `seg` local is load-bearing for this
  exact regex); I note it as already-adjudicated, not a finding.
- Test files (`test-factory-claim*.py`, `test-factory-integration.py`, `test-layout-migration.py`):
  not a rendered/printed surface; out of this role's remit.

## Accessibility / theme parity

Not applicable. This is stdout/stderr batch text with no rendered surface, no colour-only state
encoding, and no light/dark theme to have parity or not. Stating this explicitly rather than
omitting it (my own G-02).

## Findings

None. No `must_fix`, no severity above `none`.

## Open questions

None raised by me. The five signed choices named in the dispatch are pre-adjudicated and none of
them surfaced as a new defect under this audit.
