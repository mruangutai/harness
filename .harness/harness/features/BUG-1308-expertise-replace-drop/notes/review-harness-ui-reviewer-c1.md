# UI/surface review — BUG-1308 — cycle 1 — pinned sha 4c76f0f5

## Verdict
PASS, no gating findings. This diff has no rendered UI; the only human-facing surface is CLI
text (argparse help + three new refusal messages) and agent-facing contract prose in
`harness-distill/SKILL.md`. Both were exercised live at the pin and read consistent, accurate,
and test-locked.

## Measured census (not predicted)
`git diff --stat origin/main..4c76f0f5` — **40 files changed, +5130/-3**. Classified:
- 1 Python source (`expertise-merge.py`, +268 -0, pure addition)
- 2 Python test files (`test-expertise-ops.py` new, `test-expertise-merge.py` +638 lines)
- 1 skill doc (`harness-distill/SKILL.md`, the agent-facing contract)
- 3 harness-doc files (`SPEC.md`, `DECISIONS.md`, `DECISIONS-INDEX.md`)
- 33 feature-bookkeeping files (`BRIEF.md`, `STATE.md`, `feature.json`, `plan.yaml`, `notes/*`,
  `observations/*` — planning/process artifacts, not product surface)

`grep -Ei '\.(html|css|scss|tsx|jsx|vue|svelte|less)$'` against the full changed-path list: **0
matches**. **UI surfaces found = 0.** No `DESIGN.md` exists for this feature (confirmed:
`git cat-file -e 4c76f0f5:.harness/harness/features/BUG-1308-expertise-replace-drop/DESIGN.md`
→ "does not exist in 4c76f0f5"). Mode A/B graphical review is out of scope by direct measurement,
not inference.

## What I opened, and what each yielded
All seven named files opened at content verified byte-identical to the pin (md5/diff-checked
against `git show 4c76f0f5:<path>` before use, or directly `git show`n where noted):

1. **`.claude/skills/harness/bin/expertise-merge.py`** — read `_malformed`/`_validate_verb`
   (:153-201), `_resolve_replace_or_drop`/`_check_proposal_ambiguity` (:203-251), `resolve_ops`
   (:334-350), `cmd_ops` (:484-533), `main`'s `ops` subparser (:547-554). **Live-executed** against
   a scratch fixture (`/tmp`, outside the repo — this role is read-only in-tree) to capture the
   real bytes a caller sees:
   - `ops --help` → `--ops OPS  path to a JSON list of add/replace/drop ops, or - for stdin`
   - `replace` on a nonexistent id → exit 10, `MISSING TARGET section=Patterns id=P-99
     reason=no entry with this id exists in this section`
   - two ops naming one id → exit 11, `AMBIGUOUS TARGET section=Patterns id=P-01
     reason=two ops in one proposal name this target`
   - `op: merge` → exit 12, `MALFORMED OPS op=merge is not a mechanism op; express it as a
     replace on the surviving id plus a drop of the absorbed id.` — **names the rewrite
     verbatim**, matching D-10's requirement.
   - malformed shape (missing `section`) → exit 12, `MALFORMED OPS op index=0: missing required
     key section`
   All four operator-facing messages state fact, location (section + id where applicable), and
   — critically for exit 12/merge — the concrete remedy action.

2. **`tests/unit/test-expertise-ops.py`** — u3, u13, u14 assert `e.lines[0].startswith(...)` on
   `MISSING TARGET`/`MALFORMED OPS` plus that the offending key and op index are named. Confirms
   the message shape I captured live is pinned by a unit test, not incidental.

3. **`tests/integration/test-expertise-merge.py`** — case13/14/20 assert the CLI's combined
   stdout+stderr carries the exact tokens `MISSING TARGET`, `AMBIGUOUS TARGET`, `MALFORMED OPS`,
   the id, the section, and `reason=`. case17's `_harvest_help_verbs` regex
   (`r"list of ([\w/]+) ops"`) parses the live `--ops --help` string I captured above and extracts
   `add/replace/drop` — confirming the drift detector's harvest is not a fossil; it reads the real
   help text I ran.

4. **`.claude/skills/harness-distill/SKILL.md`** (diff read at pin) — states "the vocabulary is
   exactly `add | replace | merge | drop`" then, two paragraphs later, "`merge` is an authoring
   outcome, not a mechanism op... the tool refuses an `op: merge`." Read in isolation this looks
   like an internal contradiction (I initially flagged it as one). **Checked against
   `plan.yaml` T-03's intent block before filing**: this exact phrasing is plan-mandated —
   "the ops vocabulary line names EXACTLY add, replace, merge and drop — no fifth verb" — and
   machine-verified by T-03's own `verify` grep and by case17's contract-drift detector (D-10,
   SC-09). This is signed, tested design, not a defect (per G-08: a wording finding matching an
   approved plan's intent is a plan-change question, not a remedy). **No finding filed.**
   The doc's remedy instruction for `op: merge` ("Express it as a replace on the surviving id
   plus a drop of the absorbed id") matches the code's exit-12 line word-for-word. The two
   AMBIGUOUS TARGET conditions and the required-`section`-on-every-op rule are also stated
   accurately against the code I read in (1).

5. **`.harness/harness/docs/SPEC.md` §5.3** — prose matches code and SKILL.md. Checked cited
   line ranges against the pin: `compute_union` (:111-137, def at 114 — the doc's start is a few
   lines early to include the preceding docstring/comment, immaterial), `cmd_ops` (:484-533 vs
   actual function body ending at line 534 — off by one line, cosmetic, does not mislead a reader
   to the wrong code), MISSING TARGET (:203-212 — **exact**), MALFORMED OPS (:153-200 — **exact**,
   spans `_malformed` through `_parse_op`), AMBIGUOUS TARGET (:213-251 — correct outer bound but
   the range also spans the unrelated `_resolve_add`/CONFLICT block sitting between the two
   AMBIGUOUS TARGET raise sites; a reader following the pointer still lands on both real sites,
   just with extra unrelated code in the middle). None of these rise above a documentation-nit —
   no reader is misdirected to wrong code.

6. **`.harness/harness/docs/DECISIONS.md`** DEC-219 entry — full Chose/Over/Because/Tradeoff
   accepted read; matches the mechanism I verified live (section+id keying, one base snapshot,
   order-independent rebuild, merge-as-authoring-concept, three new refusals). No drift.

7. **`.harness/harness/docs/DECISIONS-INDEX.md`** — DEC-219 row (`:219`) is a one-line, accurate
   summary of the same decision, correctly cross-referencing DEC-66/DEC-95/DEC-145. No drift.

## Findings
None gate. No `must_fix`. One advisory note, non-blocking:

- **ADV-01** (severity: info) — `MISSING TARGET` and the base-file-duplicate branch of
  `AMBIGUOUS TARGET` (`expertise-merge.py:208-212`, `:213-218`) state only the triggering fact
  ("no entry with this id exists in this section" / "the id appears N times") without an explicit
  remedy phrase, unlike the `op=merge` exit-12 message which names its rewrite outright. In
  practice the remedy is trivially inferable (check the id/section spelling, or use `add` instead
  of `replace`/`drop`), and this house style is consistent across the whole file (`CONFLICT`,
  `CAP EXCEEDED` are equally terse) — so I am not filing it as a defect, only noting it since it's
  exactly the completeness gap this role is tuned to watch for (repo Expertise G-13). No concrete
  failure scenario makes this block a reader; it is a stylistic observation only.

## Accessibility / theme parity
N/A — batch CLI stdout/stderr text, no colour-only state encoding, no rendered surface, no themes.
(Per this role's own gotcha G-02: stated explicitly rather than omitted.)

## Provenance / cleanliness
- `git status --porcelain` — empty, confirmed after review (no HEAD move, no edits to
  plan.yaml/BRIEF.md/STATE.md/feature.json).
- All live command execution against `expertise-merge.py` ran the actual pinned bytes: the
  worktree copy's md5 matches `git show 4c76f0f5:.claude/skills/harness/bin/expertise-merge.py`
  exactly (`5952f07e855bcacc85f9349ac79074ba`), and `git diff 4c76f0f5..HEAD --
  .claude/skills/harness/bin/expertise-merge.py` is empty. Same md5 check performed for both test
  files before reading them.
- Test-fixture files used for live triggering were written under `/tmp`, entirely outside the
  worktree — no source path was touched.

## Open questions
None blocking.
