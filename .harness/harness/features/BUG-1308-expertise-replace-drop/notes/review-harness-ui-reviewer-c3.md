# UI Review — BUG-1308, cycle 3 (final)

Mode: B (post-build). Pin `5942e34e82cf84fd127ff496fdb64202ad647ba6`, read via `git show <sha>:<path>`.

## Scope decision: NOT IN SCOPE — measured, not assumed

`git diff --name-only origin/main..5942e34e82cf84fd127ff496fdb64202ad647ba6` returns **55 files**
(full census pasted below). Extension breakdown: 51 `.md`, 2 `.py`, 1 `.json`, 1 `.yaml`. Zero
`.html/.css/.scss/.tsx/.jsx/.vue/.svelte/.less` hits — no rendered surface exists in this diff, and no
`DESIGN.md` exists at this pin (confirmed absent by the same census, not inferred: the only markdown
under the feature tree is BRIEF/STATE/notes/observations/plan.yaml, none named DESIGN.md).

Full 55-path list (for the record):
```
.claude/skills/harness-distill/SKILL.md
.claude/skills/harness/bin/expertise-merge.py
.harness/harness/docs/DECISIONS-INDEX.md
.harness/harness/docs/DECISIONS.md
.harness/harness/docs/SPEC.md
.harness/harness/features/BUG-1308-expertise-replace-drop/{BRIEF.md,STATE.md,feature.json,plan.yaml}
.harness/harness/features/BUG-1308-expertise-replace-drop/notes/*.md  (39 files: handoff, qa,
  receipts, research, review — all prior-cycle process artifacts)
.harness/harness/features/BUG-1308-expertise-replace-drop/observations/*.md  (4 files)
tests/integration/test-expertise-merge.py
tests/unit/test-expertise-ops.py
```
No markdown here specifies spacing, colour, states, or interaction for a rendered surface (P-03) —
every `.md` is process documentation (spec/decisions/plan/notes), not a design contract. Per this
checkout's repository-tier Expertise (P-01: harness is files-only, no build step) and my own P-01,
this is the expected shape for this repo, now confirmed by direct census rather than assumed.

**Result: `PASS`, headline `not in scope` — nothing for Mode A or Mode B to grade against a design
contract.**

## In-remit anyway: the one human-facing CLI surface (dispatch-directed, P-06)

Per dispatch, audited the `ops` subcommand's `--help` text and its three refusal lines, executed live
against the pinned commit's code (O-08) — probes ran from `--file`/`--ops` pointed at temp copies
under `$TMPDIR` only; nothing in the worktree was touched (see `git status --porcelain` below).

**`--help` text** (both subcommands, actual output):
```
$ python3 expertise-merge.py ops --help
usage: expertise-merge.py ops [-h] --file FILE --ops OPS
options:
  --file FILE  path to the Expertise markdown file
  --ops OPS    path to a JSON list of add/replace/drop ops, or - for stdin

$ python3 expertise-merge.py apply --help
usage: expertise-merge.py apply [-h] --file FILE --entries ENTRIES
options:
  --file FILE        path to the Expertise markdown file
  --entries ENTRIES  path to the proposed entries, or - for stdin
```
Consistent style across both subcommands; `--ops` accepting `-` for stdin mirrors `--entries`'s
existing convention (`apply`'s help already says "or - for stdin") — not a defect, matches house
style (P-14 satisfied by direct comparison, not assumption).

**Refusal-line probes** (three temp ops files, `--file` pointed at a temp Expertise file matching
`EXPERTISE_TAIL`'s required suffix so the destination guard is not what fires):

- `12 MALFORMED OPS` (extra key at array index 3):
  `MALFORMED OPS op index=3: forbidden key extra_key for op=replace` — names **both** the op index
  and the offending key; remedy (remove the key) is directly inferable.
- `10 MISSING TARGET` (a `replace` on an id absent from base):
  `MISSING TARGET section=Patterns id=P-02 reason=no entry with this id exists in this section` —
  names section+id (sufficient to locate the op in almost every real proposal, since duplicate
  targets across ops in one file are rare) but **omits the op's array index**, unlike 12.
- `11 AMBIGUOUS TARGET` (two ops in one proposal naming the same target):
  `AMBIGUOUS TARGET section=Patterns id=P-01 reason=two ops in one proposal name this target` — same
  shape: section+id, no index.

**Verdict on this asymmetry: advisory only, not a defect.** `SPEC.md` §5.3's own refusal table
(`git show <sha>:.harness/harness/docs/SPEC.md`, the `Refusal … adds beside apply's 6,7,8,9` table)
documents this exact shape verbatim — 10 and 11 report `section=<s> id=<id>`, only 12 reports
`op index=<i>`. This is a reviewed, deliberate design captured in DEC-219 and the spec, not an
oversight the code introduced independently. An operator reading only a 10/11 line can locate the
offending target by grepping their ops file for that section+id (usually one hit); they cannot
pinpoint the array index without that grep if the same id happens to recur non-adjacently. Tagged
`enhancement` (would be a genuine quality-of-life improvement to add `op index=<i>` to 10/11 the way
12 already has it) — **not `must_fix`**: text polish, matches the signed contract, does not gate.

No accessibility/theme-parity dimension applies: this is monochrome stderr/stdout batch text with no
colour-only state encoding (G-02) — stated explicitly as not-applicable rather than omitted.

## Verification performed
- `git diff --name-only origin/main..5942e34e82cf84fd127ff496fdb64202ad647ba6` — 55-file census (above).
- `git diff --summary -M` not needed — no renames in the 55-file set worth distinguishing from real
  content (all are genuine adds/edits per the census; none score as UI-typed extensions regardless).
- Live-executed `ops --help`, `apply --help`, and three `ops` invocations against temp files under
  `$TMPDIR/uirev_root/.harness/expertise/harness-test.md` (destination-guard-compliant path) with
  three ops files also under `$TMPDIR`, to observe exact byte-for-byte refusal text.
- `git status --porcelain` in the worktree, post-probes:
```
(empty)
```
Confirms nothing in the worktree changed; all reproduction happened against `$TMPDIR` copies only.

## Findings
- `must_fix`: none.
- Advisory (`enhancement`): 10 MISSING TARGET / 11 AMBIGUOUS TARGET omit `op index=<i>` that 12
  MALFORMED OPS carries — matches the signed SPEC §5.3 table and DEC-219 exactly, so this is a
  possible future polish item, not a gate. Raised as `open_questions` below, non-blocking.

## Open questions
- Q1 (non-blocking): should a future cycle add `op index=<i>` to the 10/11 refusal lines for
  parity with 12? Purely cosmetic, spec-conformant as-is; not this cycle's call since it would
  touch a signed, tested contract shape (SPEC §5.3 table, DEC-219) that no verification gap forces
  open.
