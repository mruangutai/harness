# UI review — BUG-1308-expertise-replace-drop — cycle 4 (final delta)

**Graded commit:** `b70d57b464743034231fed3d18227a17faae2ed4` ("BUG-1308: document the VL-06
target-grammar gate in SPEC 5.3"), confirmed via `git show -s --format='%H %s'`. Worktree HEAD
(`ac6c9c5b…`) sits ahead of the pin, but `git diff HEAD b70d57b4 -- .claude/skills/harness/bin/expertise-merge.py`
is empty, so the live worktree file is byte-identical to the pinned blob and was safe to read
directly.

## 1. Measured scope census (not predicted)

`git diff --name-only origin/main..b70d57b464743034231fed3d18227a17faae2ed4 | wc -l` → **134 files**.
Extension census across that full list for `.html/.css/.scss/.tsx/.jsx/.vue/.svelte/.less`:

- **2 hits**, both `.html`, both under `.harness/harness/features/BUG-1305-run-state-clobber/notes/`
  (`ship-review-2026-09-05-final.html`, `ship-review-2026-09-05-validate-c2.html`).
- `git diff --name-status` shows both as **`D` (deleted)**, not added/modified — they existed on
  `origin/main` and are absent at `b70d57b4`. They are generated ship-review reports for an
  unrelated sibling feature (BUG-1305), not authored content this diff introduces. Per repo
  Expertise P-02, a generated report under `notes/` with no do-not-edit footer check needed here
  since it's a deletion, not new content to audit — there is nothing rendered added by this diff.
- **Zero** other UI-surface-typed files anywhere in the 134.

**`DESIGN.md` check:** `git cat-file -e b70d57b4:.harness/harness/features/BUG-1308-expertise-replace-drop/DESIGN.md`
→ fails (does not exist at the pin). No Mode A design contract exists for this feature.

**Verdict on the rendered-UI question: out of scope.** No file in the 134-file census is a
rendered visual surface, and no `DESIGN.md` exists to hold a Mode A contract.

## 2. In-remit surface named by dispatch: CLI text of the `ops` subcommand

Per dispatch, audited anyway: this tool's operator-facing surface is its `--help`/usage text and
its three refusal message families. Read `.claude/skills/harness/bin/expertise-merge.py` at the
pin directly (raw line ranges 140–330, 540–627) rather than trusting the `_read` structural
cache, which — for this file specifically — returned a stale/mismatched body on a ranged read
until an absolute worktree path was supplied; recorded as a tooling gotcha, not a code defect.

**`ops` subcommand wiring** (`:601-627`) — `p_ops = sub.add_parser("ops", help="apply add/replace/drop
ops to an Expertise file")`, with `--file` ("path to the Expertise markdown file") and `--ops`
("path to a JSON list of add/replace/drop ops, or - for stdin", `required=True`). This is
standard `argparse`; the rendered `--help` text is these strings verbatim under
`usage: expertise-merge.py ops [-h] --file FILE --ops OPS` — deterministic from the library, not
independently re-executed (see §3). Judged: clear and actionable — an agent reading `--help`
learns the exact artifact shape (`--ops`, a JSON list, file-or-stdin) without needing source.

**REQ-04 (missing target, exit 10)** — `_resolve_replace_or_drop` (`:269-278`):
`MISSING TARGET section={section} id={target} reason=no entry with this id exists in this section`.
Names section, id, and reason, verbatim. **Satisfies REQ-04**, and is actionable: the emitting
agent learns exactly which id in which section it must stop targeting.

**REQ-05 (ambiguous target, exit 11)** — two call sites, one shared shape:
- base ambiguity (`_check_base_ambiguity`, `:258-266`): `AMBIGUOUS TARGET section={section} id={target} reason=the id appears {n} times in section {section}`
- proposal-level ambiguity (`_check_proposal_ambiguity`, `:306-316`): `AMBIGUOUS TARGET section={section} id={target} reason=two ops in one proposal name this target`

Both name section, id, reason. **Satisfies REQ-05**, actionable both ways (tells the agent whether
the base file or its own batch is the source of the collision).

**Exit 12 (MALFORMED OPS)** is not itself a REQ-04/05 case (those two REQs are specific to
missing/ambiguous target), but judged under the same operator-facing-contract lens: every
`_malformed`/inline raise (`:154-298`) prefixes `MALFORMED OPS op index={index}: {message}` (or, for
whole-payload shape, `MALFORMED OPS could not decode JSON: {exc}` / `payload is not a list…`), and
the per-field `{message}` always states what was wrong (missing key, wrong type, forbidden key,
unknown verb) and, for the VL-06 grammar refusal, echoes the offending value:
`target {target!r} does not match the entry id grammar`. All actionable — index or op text pins
the location in a multi-op batch.

**One advisory gap, not blocking:** the grammar-refusal message states that `target` failed the
id grammar but never restates the grammar itself (`[A-Za-z]{1,3}-\d+`). An agent seeing this once
knows *that* it failed, not *what shape passes*, without reading source or SPEC §5.3. Low severity
— the convention is otherwise ambient (every existing Expertise entry demonstrates it) and this is
a wording/completeness nit, not a functional defect.

## 3. Execution constraint (read-only domain)

This persona's `bash-write-guard` blocks every file-write pattern (redirect, heredoc-to-file,
`rm`), so I could not stand up a scratch fixture and execute the CLI myself without guardrail
evasion (correctly refused twice, reported per tool policy, not worked around). Instead I
cross-checked the literal message templates above (read directly from the pinned blob, so they
are not guesswork) against **live-executed evidence already on record**:
- `notes/qa-premise-verification-c1.md` (review_sha `4c76f0f5`) captured actual CLI runs producing
  `MISSING TARGET section=Gotchas id=G-08 reason=…` and `AMBIGUOUS TARGET section=Patterns id=P-07
  reason=the id appears 2 times…` — I then diffed `4c76f0f5..b70d57b4` on `expertise-merge.py` and
  confirmed both f-string literals are **byte-unchanged**, only moved into a helper
  (`_check_base_ambiguity`). The earlier live execution still speaks for the graded commit.
- `tests/integration/test-expertise-merge.py:1250-1286` (`case_ops_target_grammar`, VL-06) runs the
  real CLI subprocess and asserts the malformed-target string appears in combined stdout+stderr —
  this is post-VL-06 code, i.e. the exact commit family under review, and per
  `notes/qa-gate-bug1308.md` (title: PASS) this suite is green.

No dimension here needed rendering/pixels — pure text contract, `argparse` output and stderr
lines — so the "not verifiable from source" caveat this role usually carries does not apply.

## `git status --porcelain`

```
(clean — no output)
```
No files changed outside this note.
