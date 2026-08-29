# Grilling — DECISIONS.md states current knowledge only — 2026-08-24

Source tickets: **#615** (fold amendment sub-sections) and **#78** (delete superseded decisions
outright and remove the marking machinery). #615 already carries an operator ruling dated
2026-08-20 that was never built.

## Destination

`DECISIONS.md` holds only live decisions, each stating current truth in its own voice. No amendment
sub-sections, no `am.N`, no superseded entries, no `SUPERSEDED BY` markers, and no code that can
produce any of them. Strike records stay.

## Settled

- **Does a falsified claim survive the fold?** → Yes, as ONE CLAUSE OF CURRENT TRUTH. The entry
  states what is true and that the opposite was measured and failed — in the document's own voice,
  with no dates, no "amendment", and no attribution. Without it a reader can re-propose something
  already measured false, and nothing in this repo would stop them.
- **How deep does the fold cut?** → REWRITE each amended entry, cutting the history. Not a verbatim
  merge. The entry says what is true and why; reasoning about how it CHANGED goes. The operator's
  words: "no need to keep historical reasons or prior decisions."
- **What happens to the 13 live citations that would dangle?** → REPOINT them to the superseding
  decision. `DEC-19` becomes `DEC-84`; `DEC-102` becomes `DEC-120`. A reader still lands somewhere,
  and lands on current truth.
- **What happens to the generator's `am.N` and supersession machinery?** → DELETE it, with its
  tests. Not kept-but-unused: a future amendment written out of habit would silently get a marker
  again.
- **Who deletes the replaced entry going forward?** → The AUTHOR of the superseding decision, in the
  SAME edit. Writing the replacement and deleting the replaced is one act, so there is never a
  moment where both exist. This is what stops the file refilling — nine superseded entries
  accumulated precisely because the deletion was somebody's later problem.
- **Does anything detect a regression?** → ONE TEST ASSERTION in `test-gen-decisions-index.py`:
  `DECISIONS.md` holds no amendment heading and no supersession clause. It runs in the suite and
  refuses nothing at write time. Deliberately NOT a `check-state.sh` refusal — that would put a
  documentation convention on the enforcement layer, a far heavier surface.
- **Do strike records go too?** → NO. DEC-188 keeps a struck entry so citations still land
  somewhere, and this repo has no propagation checker.

- **Does this feature also install stale-statement detection?** → YES, TWO MECHANISMS, and only
  because the entries are already open. **M1, an anchor rot check:** for every `file.py:NNN` cited
  in `DECISIONS.md`, assert the file exists and the line is in range — better, that a short stored
  snippet still appears near it. A script, no model, runs in the suite. **M2, executable claims:**
  where a rewritten entry states something a command can check, it records the command and the
  expected result inline, and a checker re-runs them. M2 rides on the 22 rewrites for almost
  nothing; retrofitting it later means touching all 199 entries.

## Not yet specified

- How many of the 199 entries carry DESIGN claims that are stale — statements no command can check.
  M1 and M2 reach the mechanical half only. A periodic LLM audit (M4) and a referenced-file watch
  (M3) were both considered and left OUT of this feature; whether either is worth building is not
  yet a sharp enough question to scope, because nobody knows the size of what they would find.

## Out of scope

- **Strike records and DEC-188's machinery** — ruled to stay.
- **A size target for `DECISIONS.md`** — shrinkage is a consequence of stating current truth, never
  the goal. Nothing is cut to hit a number.
- **M3, a referenced-file watch**, and **M4, a periodic LLM audit of design claims.** Both were
  considered and ruled out here: M3 hands over a review list without proving anything, and M4
  decays the moment code moves, so it is a one-time sweep rather than a gate. Neither is cheap
  because the entries happen to be open, which is the whole reason M1 and M2 are in.
- **The other decision-adjacent tickets** — #626, #148, #803, #323, #499, #167. Related surface,
  different problems.

## Facts I verified (so pm does not re-derive them)

All measured at `513c4a4` unless noted.

- `DECISIONS.md` is **6,984 lines / 199 entries**; `DECISIONS-INDEX.md` is **219 lines**.
- **22 entries carry amendment text**, and those entries hold **2,046 lines — 29% of the file**.
  (#615 measured 30 blocks across 14 decisions at an earlier sha; it has grown since.)
- **Four distinct amendment formats**, not two — `### DEC-N amendment [k]`,
  `**Amendment N (date) —**`, `**Amendment (same day):**` unnumbered, and
  `**Amendment am.N (issue #NN):**`. The generator's `AMEND_BOLD_RE` at
  `gen-decisions-index.py:26` matches the last two only by luck.
- The machinery lives at `gen-decisions-index.py:25-26` (`AMEND_HEADING_RE`, `AMEND_BOLD_RE`),
  `:28` and `:38` (supersession verbs), `:213-218` (`am.N` span rendering), `:256-263` (clause
  stripping before the 30-word cap) and `:330` (appending `— SUPERSEDED BY DEC-NN`).
- **`DECISIONS.md` contains zero literal "SUPERSEDED" text.** The marker is DERIVED from titles and
  body prose, not authored. This is the single most important fact before touching it.
- **8 superseded rows**: DEC-19, 20, 37, 67, 82, 88, 92, 102. **7 struck rows**: DEC-90, 103, 104,
  137, 140, 181, 188.
- **Live citations to the 8 superseded entries: 13 in total, across only two of them** —
  `DEC-19` (7) and `DEC-102` (6). The other six are cited by nothing in `.claude/skills`,
  `.claude/agents` or `docs/`. Counted with a numeric boundary so `DEC-19` does not match `DEC-193`.
- Those 13 sit in nine files, including `harness-team/SKILL.md`, `check-state.sh`,
  `validate-digest.py`, `gh-sync.py` and `harness-orchestrator.md`.
- **The amendment convention is written down NOWHERE** — not in `SPEC.md`, not in
  `harness-documentor`'s agent file or skill. It exists only in the generator's regexes, so the new
  rule needs a home and that home is a new `DEC-NN`.
- **LANES — this feature is entirely squad work.** `check-domain.sh --resolve`:
  `DECISIONS.md` and `DECISIONS-INDEX.md` → `harness-documentor`;
  `gen-decisions-index.py` and `test-gen-decisions-index.py` → `harness-backend-dev harness-dev-ops`.
  Nothing is `main-session-direct`, and `gen-decisions-index.py` is NOT in DEC-174 amendment 4's
  enforcement enumeration.
- `test-gen-decisions-index.py` is registered in `run-unit-tests.sh`'s `INTEGRATION_SCRIPTS`.
- **Anchor rot is REAL and mechanically detectable — measured, not assumed.**
  `DECISIONS.md` carries **35** `file:line` anchors across **23** distinct files, plus 13
  backticked commands. Two stale referents found in one shell loop:
  `.claude/settings.json:112` when that file has **77 lines**, and three anchors naming
  `feature.yaml`, which exists nowhere — DEC-191 renamed it to `feature.json`.
  This is the existence proof that M1 finds real rot today, before any model is involved.
