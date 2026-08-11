# Receipt — harness-backend-dev — distillation

## BLUF

Expertise updated: dropped one stale entry (P-04), added two new entries (P-12, P-13). Net
Patterns 11 → 12, Gotchas unchanged 8 → 8, Outcomes 0 → 0, Open 0 → 0. File is 69 lines of 150.

## Ops applied

```yaml
expertise_update:
  - op: drop
    target: P-04
    section: Patterns
    why: >
      Verified stale, not taken on the dispatch's word alone. `grep -rlE 'harness-deploy|deploy\.sh'
      .claude/skills/harness/bin/ ':!test-no-distribution.py'` returns zero hits;
      docs/harness/SPEC.md:428 now states "nothing is installed into it." deploy.sh (T-07) and every
      reference to it (T-10) are gone from this tree. The entry's scenario — diffing a claimed-
      byte-identical change against a deployed copy under `~/.claude/skills/harness/bin/` — no longer
      has a live target anywhere in the codebase; nothing writes that path any more. Dropped, not
      replaced: the general "verify a byte-identical claim by diffing" habit is already implied by
      other entries (e.g. P-11's evidence discipline) and doesn't need a copy-distribution-specific
      restatement.
  - op: add
    target: (none — add)
    section: Patterns
    entry: "P-12: WHEN a task's verify pins a claim to a specific section (e.g. a decision's slice)
      via a presence grep DO scope the grep to the extracted section text, not the whole file — a
      substring present anywhere else in the file lets the check pass while asserting nothing about
      the section it names."
    why: >
      Own receipt (T-13) confirmed `harness/teams` is absent from the DEC-113 slice specifically,
      which is the discipline this entry generalizes. Distinct from P-03 (absence-side, path- vs
      payload-scoping) and P-07 (anchor uniqueness in extraction) — this is presence-side, whole-
      file-vs-extracted-section scoping. Corroborated by relayed candidate 1 describing a sibling
      task whose verify made the same whole-file presence mistake and passed while gating nothing.
  - op: add
    target: (none — add)
    section: Patterns
    entry: "P-13: WHEN a task's intent cites a specific line as an existing assertion of old wording
      to update DO read that line first — it may be a docstring or unexecuted comment, not a check.
      If no executable path exercises it, add new RED-then-GREEN tests rather than treating a
      rewrite as closing the gap."
    why: >
      Grounded directly in own receipt (T-10): the dispatch's intent named a line as an existing
      assertion; on inspection it was a docstring with no executing check anywhere in the file for
      that code path. Distinct from G-02 (a docstring/label claiming a contract the adjacent
      assertion doesn't match) and G-04 (intent vs verify command disagreement) — this is intent
      being factually wrong about whether a line executes at all, and names the correct recovery
      (new RED-then-GREEN, not a rewrite).
```

## Rejections

1. **Candidate 3 (self-referential sweep / token-concatenation workaround) — REJECTED.**
   The durable half ("scope a sweep that forbids the token it must reason about") is functionally
   covered by existing G-06 ("avoid spelling forbidden identifiers anywhere in the file, including
   comments/docstrings that explain the prohibition — the explanation text itself counts as a
   hit"), which already generalizes to test files asserting absence, per its own applied case in
   receipt T-10 (`RETIRED_CMD` built by concatenation to survive T-10's own grep). No new rule
   survives that isn't restating G-06. The candidate's own stated boundary flags the
   concatenation-as-workaround half as belonging in `open_questions`, not Expertise, because it
   works around a gate defect (a sweep whose own removal-evidence requirement is self-defeating) —
   agreed, and that half is excluded on that basis too. Nothing added.

## P-04 staleness check (explicitly requested)

Ran before ruling, not taken on the dispatch's word:
- `grep -rlE 'harness-deploy|deploy\.sh' .claude/skills/harness/bin/ ':!test-no-distribution.py'`
  → zero hits (only `test-no-distribution.py` itself, excluded).
- `ls .claude/skills/harness/bin/ | grep -i deploy` → zero hits — `deploy.sh` itself is gone.
- `docs/harness/SPEC.md:428` → "clones it under `workspace_root`; nothing is installed into it."
  under §3.3 ("The fleet — how a repository reaches the harness").

Conclusion: nothing in the current tree maintains `~/.claude/skills/harness/bin/` as a deployed-copy
reference. Dropped.

## Source split (own receipts vs relay)

- **P-12**: relay candidate 1, corroborated by own T-13 receipt's `harness/teams`-absence check.
- **P-13**: own material — T-10 receipt's docstring-vs-assertion finding, independent of relay
  candidate 2's framing (candidate 2 restates the same incident from the run digest; content
  matches what the receipt already recorded first-hand).
- **Candidate 3**: relay only, rejected — no own-receipt content added.
- **P-04 drop**: own verification (Bash checks above), triggered by the dispatch's flag but not
  taken on its word.

## Suite run (no source touched this run, but re-run to give a real suite result)

`.claude/skills/harness/bin/run-unit-tests.sh > /tmp/feat12-distill-suite.log 2>&1`

**Exit: 0. PASS count: 104. FAIL count: 0.**

## Counts

| Section | Before | After |
|---|---|---|
| Patterns | 11 | 12 |
| Gotchas | 8 | 8 |
| Outcomes | 0 | 0 |
| Open | 0 | 0 |

File: 69 lines (budget 150). No `FEAT-NN`/`T-NN`/`#NN` tokens present (grepped, zero hits).

## Cycle 2 — send-back for word cap (P-12, P-13 over 50)

Lead's count matched exactly: P-12 and P-13 were both 53 words against the script's own logic
(`- P-NN: ` prefix stripped, wrapped continuation lines joined with a single space, split on
whitespace). Re-derived by running the checker's own tokenizer logic directly against the file
(not eyeballed) — same 53/53 result before editing.

**Ops applied this cycle:**

```yaml
expertise_update:
  - op: replace
    target: P-12
    section: Patterns
    entry: "P-12: WHEN a task's verify pins a claim to a specific section via a presence grep DO
      scope the grep to the extracted section text, not the whole file — a substring present
      elsewhere in the file lets the check pass while asserting nothing about the section it
      names."
    why: >
      Cut the parenthetical example "(e.g. a decision's slice)" and shortened "anywhere else" to
      "elsewhere" — no change to WHEN or DO. 53 → 48 words.
  - op: replace
    target: P-13
    section: Patterns
    entry: "P-13: WHEN a task's intent cites a specific line as an existing assertion of old
      wording to update DO read that line first — it may be a docstring or unexecuted comment,
      not a check. If no executable path exercises it, add new RED-then-GREEN tests instead of a
      rewrite."
    why: >
      Cut the trailing restatement "rather than treating a rewrite as closing the gap" down to
      "instead of a rewrite" — no change to WHEN or DO. 53 → 48 words.
```

**Over-cap sweep of the ten untouched entries (P-01–P-11 minus P-12/13, G-01–G-08):** all measured
at or under 50 words using the same tokenizer logic (prefix stripped, wrapped lines joined,
whitespace-split). None was over before this cycle. Full measured counts:

| Entry | Words | Entry | Words |
|---|---|---|---|
| P-01 | 11 | G-01 | 11 |
| P-02 | 43 | G-02 | 41 |
| P-03 | 36 | G-03 | 37 |
| P-05 | 41 | G-04 | 46 |
| P-06 | 43 | G-05 | 39 |
| P-07 | 36 | G-06 | 40 |
| P-08 | 43 | G-07 | 47 |
| P-09 | 47 | G-08 | 35 |
| P-10 | 42 | | |
| P-11 | 47 | | |
| P-12 (new) | 48 | | |
| P-13 (new) | 48 | | |

**Per-section counts, before/after cycle 2:** Patterns 12 → 12 (unchanged — replace, not
add/drop), Gotchas 8 → 8, Outcomes 0 → 0, Open 0 → 0. Content of P-12/P-13 unchanged in meaning,
only length. File: 69 → 67 lines (budget 150).

No source touched this cycle (Expertise-file-only edit). Re-ran the suite anyway for `suite:`
contract truthfulness (`suite: n/a` with `VERDICT: PASS` is rejected per DEC-173) —
`.claude/skills/harness/bin/run-unit-tests.sh > /tmp/feat12-distill-c2-suite.log 2>&1`.
**Exit: 0. PASS count: 104. FAIL count: 0.** Note this does not validate the word-count fix itself:
cycle 1's identical suite was green while the 53-word entries sat in the tree, so
`run-unit-tests.sh` does not gate Expertise-file format — the re-run establishes `suite: pass`
truthfully, nothing more. `check-expertise.sh` was not run (carve-out stands); the word/line counts
above were derived by running the checker's own tokenizer logic against the file directly, not
eyeballed. Re-grepped for `FEAT-\d+|T-\d+|#\d+` across the whole file post-edit: zero hits
(measured this cycle, not inherited from cycle 1).

This is a distillation dispatch, carries no PLAN task: `task: none`, `task_verify` omitted per
`harness-tdd-enforcement`/`harness-digest-dev` (the key, not `n/a`, when `task: none`).
