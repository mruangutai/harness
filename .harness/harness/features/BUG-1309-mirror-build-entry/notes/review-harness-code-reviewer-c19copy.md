# Code review — c19 copy delta — 4857818bb1408813c7a38311d9e4ffc20373427e

## Stage 1 — spec compliance: YES

Verbatim question: does the rendered message name the feature, expose an executable recovery
command, and carry none of the rejected jargon? **Yes, on all three**, confirmed against the real
rendered string (given evidence) and against `merge-gate.py:190-192` source:
`merge-gate: {feat} needs its GitHub mirror recovery completed before this merge can continue.
Run: {command_line}` → `merge-gate: FEAT-9001-uat-scratch needs its GitHub mirror recovery
completed before this merge can continue. Run: python3 …/gh-sync.py open <dir>`.
- Names the feature: `{feat}` interpolates right after `merge-gate: `. ✓
- Executable command: `{command_line}` is a copy-pasteable `python3 …gh-sync.py {open|recover-terminal} <realpath>`. ✓
- Rejected jargon (`github.build_entry=<value>`, `no Build entry receipt exists for it`): absent —
  confirmed both by reading the new f-string and by a repo-wide grep (below). ✓
- SC-04 ("reason naming the feature and the re-run command", `BRIEF.md:108-111`): satisfied, no
  amendment needed — both pieces present as literal substrings.
- SC-10 ("a message they can act on without reading the source", `BRIEF.md:157-159`): satisfied —
  plain-English clause plus a runnable command; this is a strict improvement over the old copy.
  Ruling §3's claim that neither needs a BRIEF amendment is **confirmed**, not merely assumed.

## §3 table — re-verified at the pin, row by row

`git show --stat 4857818b`: exactly 2 files, `merge-gate.py` 1+/1-, `test-merge-gate.py` 4+/2-;
combined 5 insertions/3 deletions across one hunk per file for the source (the second file has two
hunks) — **matches the claimed 2 files / 3 hunks / 5 ins / 3 del exactly.**

| Site | Claim | Verdict |
|---|---|---|
| `merge-gate.py:174` ambiguity deny | untouched | **PASS** — outside the sole `@@ -189,7 +189,7@@` hunk; text read verbatim, matches pre-change wording |
| `merge-gate.py:180` era-exempt stderr | untouched | **PASS** — same hunk-exclusion; verbatim match |
| `merge-gate.py:188` repo-unpinned deny | untouched, still carries `records github.build_entry={value}` | **PASS** — verbatim match, correctly in scope for no change |
| `merge-gate.py:194` bare-except deny | untouched | **PASS** — verbatim match |
| `post-merge-sweep.sh:230-232` | untouched, own jargon out of scope | **PASS** — file not in the diff; its own `records github.build_entry=…so no Build entry receipt exists` text is a different message in a different script, correctly not this cycle's target |
| Local test run | 36 ok / 0 FAIL / rc=0 | **PASS** — reran independently: `36`/`0`/`rc=0`, tree clean except `feature.json` pin (plus one unrelated untracked sibling-agent note) |

## Old-sentence sweep — every surviving site, allowed/not-allowed

Grepped `records github\.build_entry=|no Build entry receipt exists|needs its GitHub mirror
recovery completed` across the whole tracked tree. Pattern confirmed against the known positive
(`plan.yaml:1273-1274`, hit as expected) before trusting any zero result elsewhere.

- **Allowed, confirmed:** `plan.yaml:1273-1274` (T-05 intent step 6, D-19-superseded, PRINCIPLES
  rule 15 — correctly left standing); `plan.yaml:1284-1289` and `:1710-1713` (spec text for the
  *other*, unchanged branches — repo-unpinned and post-merge-sweep, correctly untouched);
  `notes/qa-matrix-gate-BUG-1309.md`, `notes/research-BUG-1309-goalcheck-amend-c13.md`,
  `notes/review-harness-code-reviewer-c14.md`, `notes/review-harness-security-reviewer-c1.md`,
  `notes/review-harness-ui-reviewer-c6.md`, `-c7.md`, `-c18.md` — all historical review/research
  records, correctly not rewritten; `notes/rulings-2026-09-08-c19-copy.md` — the packet describing
  what was removed, not live guidance.
- **Not allowed, and NOT found anywhere:** no live production source, no `references/github-mirror.md`,
  no `SKILL.md`. **Confirmed amended:** `notes/uat-BUG-1309-mirror-build-entry.md:161-164` (Step 3)
  and `:209-214` (Step 3b) both now quote the NEW sentence only — pm's amendment landed correctly.
  `tests/integration/test-merge-gate.py:65-66,68-69` carry only the new predicates.
- **Verdict: clean.** No disallowed survival found.

## Stage 2 — quality, on the two moved predicates

**`:65-66`** (`"needs its GitHub mirror recovery completed" in reason`): right seam — the copy is
now the D-19 contract, so anchoring the assertion on the operator's own sentence is correct, not
incidental. The chosen 8-word clause is neither so short it risks false-positives nor so long it
would break on a stray comma; it does not (and does not need to) re-verify feature naming, since
the old predicate it replaces (`"recovery-required" in reason`) never checked naming either — both
old and new copy render an identical message for `entry=None` and `entry="recovery-required"`, so
this case's job was and remains "state X denies," not "state X denies and is named."

**`:99-102`** (`"FEAT-9001-fixture-non-era" in reason and "gh-sync.py open" in reason`): tracing
`merge-gate.py:190-191`, **both conjuncts are satisfied entirely by `{command_line}` alone** —
`os.path.realpath(feat_dir)` ends in `.../features/FEAT-9001-fixture-non-era`, and
`command_name == "open"` is embedded in the same string as `gh-sync.py open`. So yes, this reads as
two checks but binds as one substring. **Does it matter here — no.** This case's stated purpose is
proving the gh-unresolvable fallback still correctly resolves the owning feature and selects the
right recovery command; both facts are exactly what `command_line`'s construction encodes, so the
assertion binds to the right subject for what THIS case exists to prove, even though it is silent
on whether `{feat}` independently appears elsewhere in the sentence.

## Also-graded: the `{feat}`-drop non-reddening

**Verdict: (ii) a pre-existing test-strength gap, not a defect in this delta.** The case it applies
to — `"T-05 non-era absent build_entry denies naming feature and re-run command"` (`:67-69`) — has
an unchanged predicate (outside this commit's two hunks) and is unrelated to today's edit. The
behavior at the pin is correct (the feature name is genuinely in the message, via `{feat}` and
independently via `command_line`'s path); what's incidental is only the EVIDENCE, because
`os.path.realpath(feat_dir)` always embeds the feature's own directory basename, so any assertion
of the form `"<feat-id>" in reason` is structurally satisfied by `command_line` regardless of
whether `{feat}` itself is ever emitted. A discriminating assertion would need `{feat}` to appear
in a location `command_line` cannot reach (e.g., checking the reason *before* the word `Run:`).
This is real backlog material — a future regression dropping `{feat}` alone would go undetected —
but it predates this commit and its case's predicate was not touched here, so it does not gate this
review.

## code_grade

`4857818b` changes only an f-string literal and two test predicates; it adds no branch and touches
no function's shape. Ran the grader over the canonical range anyway, since `validate-digest.py`
recomputes it independently: `python3 code-grade.py --base $(git merge-base origin/main 4857818b)
--head 4857818b` → 53 functions graded, 49 PASS, 4 gated at `GRADE: 2` (none grade 1, none
production grade-3-below-bar) — **identical in shape and numbers to every prior cycle's report for
this feature** (c0/c2/c3/c4/c6/c7/c14/c17/c18 all report the same four). None of the four is
touched by this commit's two hunks, and all four already carry a written reason (in-source
`GRADE-2 REASON` comments or the review record, per c2/c7/c17/c18):

- `merge-gate.py:154 main` (cyclomatic 19/cognitive 22/ABC 45.0, bar 4) — pre-existing in-source
  `GRADE-2 REASON` comment: orchestration boundary, helpers own parsing/resolution/rendering, this
  function preserves the policy's ordered exits; unchanged by this commit's one-line string edit.
- `test-check-state.py:4621 case_t06_build_entry_invariant` (ABC 45.0, bar 3) — table-driven case
  intentionally drives each independent invariant state through the external checker in one body;
  splitting it would hide the fixture-to-checker contract. Unchanged by this commit.
- `test-hooks-install.py:396 _run_merge_and_check` (ABC 27.0, bar 3) — this SC-14 fixture
  deliberately keeps setup/commit/worktree/real-merge/hook-observation/retention assertions in one
  routine; splitting would hide the shared clone/worktree state the end-to-end contract must prove.
  Unchanged by this commit.
- `test-post-merge-sweep.py:885 case_t07_build_entry_receipt` (ABC 35.6, bar 3) — table-driven test
  keeps all retention states in one visible matrix so the era pair and no-mirror contrast cannot
  drift apart. Unchanged by this commit.

`code_grade: grade_2`.

## Findings

| id | severity | summary | file:line |
|---|---|---|---|
| F-01 | low | `T-05 non-era absent build_entry denies naming feature and re-run command`'s naming assertion is satisfied incidentally by `command_line`'s embedded directory path rather than by an independent check on `{feat}`'s appearance — pre-existing, unchanged by this commit, worth a backlog line to make the feature-naming claim discriminating on its own. | `tests/integration/test-merge-gate.py:67-69` |
| F-02 | low | The re-anchored `:99-102` predicate has the identical "two checks, one substring" shape as F-01, but for this case's stated purpose (proving the gh-fallback path resolves feature and command correctly) that binding is the right one — noted for the record, not a defect. | `tests/integration/test-merge-gate.py:99-102` |

No `must_fix`. `severity_max: low` (the four grade-2 records are pre-existing, unchanged, and
already reasoned above, so they are not filed as additional findings; F-01/F-02 are advisory only).

```yaml
VERDICT: PASS
DIGEST:
  headline: "Copy delta at 4857818b satisfies SC-04/SC-10 verbatim, no BRIEF amendment needed; §3 table and old-sentence sweep both clean; two low-severity test-shape notes, neither gating."
  spec_compliance: "yes — message names the feature, exposes an executable command, and carries none of the rejected jargon; verified against the rendered string and merge-gate.py:190-192"
  sc04_satisfied: true
  sc10_satisfied: true
  table_section_3: "6/6 rows PASS — all four untouched merge-gate.py branches verbatim-match, post-merge-sweep.sh out of scope, local suite 36 ok/0 FAIL/rc=0 reproduced independently"
  old_sentence_sweep: "clean — every surviving occurrence is either plan.yaml:1273-1274 (deliberately superseded, PRINCIPLES rule 15) or a historical notes/review-*.md or notes/research-*.md record; UAT Step 3/3b confirmed amended to new copy; no live source, SKILL.md, or references/ carries it"
  severity_max: low
  findings: 2
  must_fix: []
  spec_violations: []
  code_grade: grade_2
  grade_2_reasons:
    - { qualname: "merge-gate.py:main", reason: "orchestration boundary; helpers own parsing/resolution/rendering, this function preserves the policy's ordered exits; unchanged by this commit" }
    - { qualname: "test-check-state.py:case_t06_build_entry_invariant", reason: "table-driven case intentionally drives every independent invariant state through the external checker in one body; splitting would hide the fixture-to-checker contract; unchanged by this commit" }
    - { qualname: "test-hooks-install.py:_run_merge_and_check", reason: "SC-14 fixture deliberately keeps setup/commit/worktree/real-merge/hook-observation/retention assertions in one routine to preserve shared clone/worktree state; unchanged by this commit" }
    - { qualname: "test-post-merge-sweep.py:case_t07_build_entry_receipt", reason: "table-driven test keeps all retention states in one visible matrix so the era pair and no-mirror contrast cannot drift apart; unchanged by this commit" }
  reviewed: "4857818bb1408813c7a38311d9e4ffc20373427e^..4857818bb1408813c7a38311d9e4ffc20373427e"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1309-mirror-build-entry/.harness/harness/features/BUG-1309-mirror-build-entry/notes/review-harness-code-reviewer-c19copy.md
```
