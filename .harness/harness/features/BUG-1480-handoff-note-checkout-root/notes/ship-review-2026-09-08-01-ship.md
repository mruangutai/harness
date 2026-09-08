# Ship review — BUG-1480, handoff note checkout root

**Recommendation: ship.** Every gate is green, no finding gates, and the fix is 12 lines of new
helper plus a one-argument swap, defended by a regression test that was proven red before it.

Harness features have not been able to write the phase-seam handoff note DEC-159 requires, because
every feature lives in a linked worktree until it merges and the shape gate resolved the note's
authority pointers against the MAIN checkout instead. BUG-1480 makes a handoff note validate against
the checkout it actually stands in. This feature reproduced the defect on its own build-phase note
one hour ago and could not write it; that is the last time it should happen.

**No report round was spawned.** This briefing is assembled from the eight run digests already on
disk, listed at the foot, plus the qa and goal-check notes. Nothing here is re-narrated from an
agent asked to summarise itself.

## What changed

Two commits, two files, 57 added lines, standalone off `origin/main` `64fcaa34` (D-01: no
cherry-pick into BUG-201).

| commit | file | change |
|---|---|---|
| `6b5ae254` | `tests/integration/test-check-domain.py` | `_handoff_worktree_cases` — four rows proving a note in a worktree-only feature dir resolves there |
| `d8a99991` | `.claude/skills/harness/bin/check-domain.sh` | `_checkout_root(path)` sibling helper beside `_norm`, and one argument at the `handoff_done_when.problems(...)` call site |

`_norm` already asked `harness_boundary.checkout_relative` for the pair `(checkout root, relative
path)` and threw the root away. The fix stops throwing it away — at one call site, in a sibling
helper, leaving `_norm`'s string return contract untouched for its other 15 call sites (D-03).

## The gates

| gate | verdict | evidence |
|---|---|---|
| qa (**blocking**) | **PASS**, `matrix_ok: true` | `notes/qa-BUG-1480-c0.md` — unit and integration both rc=0, 0 `FAIL`; 402 `ok` rows in the domain suite |
| test-first audit | **PASS** | `6b5ae254` is an ancestor of `d8a99991`; substituting the pre-fix script through `CHECK_DOMAIN_BIN` reddens **exactly** the two rows designed red-then-green and nothing else |
| SIMPLIFY, four angles | **PASS**, 0 edits applied | four receipts under `notes/`; DEC-174 suspends the apply step on both paths, so every finding is deferred |
| review panel (advisory unless high) | **PASS**, `must_fix: []`, `code_grade: pass`, `severity_max: med` | five readers all `ran`, none skipped — code, security, ui, qa and the external `fable-advisor` |
| goal-check | **PASS**, 7 of 7 criteria met | `notes/research-BUG-1480-goalcheck-c0.md` |

Cycles used: **0 of 10** — no rework, no send-back, no failed gate anywhere in the feature. Runs: 7
of 20.

**The green is discriminating, not shallow.** The one measurement that proves it: run the same suite
against the pre-fix script and exactly two rows go red, both in the new group. A test that cannot
report red proves nothing, and this one can.

**Where the evidence is thinnest.** SC-07 — the deliberate narrowing in REQ-06, that a note standing
in a worktree may only point at targets inside that worktree — is graded by reading the code, not by
running anything. Four of the five panel readers verified the same mechanism by reading it. The
behaviour is right today; nothing pins it against a future regression. That is B-2 below.

## Open questions — none blocking

Nothing needs an answer before merge. Every residual is in the table below.

## Proposed backlog — strike any row by ID; **unstruck rows become issues, and anything not listed dies here**

| ID | nature | what | why it is not in this PR |
|---|---|---|---|
| B-1 | bug | `check-domain.sh:1472-1474` — the `RE_FEATURE_JSON` schema lookup joins a checkout-stripped `rel` onto the main `root`, so a worktree-only `feature.json` is schema-checked against the wrong checkout. Same root cause as BUG-1480, outside its diff. Remedy is one token: `_checkout_root(absolute_path)` in place of `root`. Self-documented at `:1464-1468` as an accepted residual since 2026-08-23 | D-01 bounds this PR to one defect. It is a one-line fix that deserves its own red test |
| B-2 | chore | REQ-06's containment narrowing has no executable row: no test observes a worktree note's `finding:`/`approval:` pointer into the MAIN checkout being refused. A later edit could widen or drop the bound with the suite green | `tests/integration/**` is `main-session-direct` under DEC-174; no member may add it, and it is proof, not behaviour |
| B-3 | chore | REQ-02's other direction is unfixtured: no row combines a *present* linked worktree with a note validated in the MAIN checkout. The main-checkout path is covered, but only where no worktree exists | same as B-2 |
| B-4 | chore | `templates/HANDOFF.md:45` documents `finding:`/`approval:` as a bare PATH with no root semantics, while 22 notes across 11 features use the main-root spelling `.claude/worktrees/harness/<FEAT>/…` that the signed narrowing now refuses from a worktree-standing note. Found by reading the 95-note corpus, not the diff — every reviewer scoped to the diff was right to return clean | Documentation change outside the defect. The narrowing itself is signed and correct; what is missing is the sentence telling the next author which root a pointer is read against |
| B-5 | chore | BRIEF.md's `## Constraints` names `_resolved_rel` as a `_norm` call site; at `4de92e75` it is not one — `_hardlink_plan:1920` is. The BRIEF is approval-gated, so the inaccuracy is recorded rather than edited. It graded nothing: SC-05 was verified per call site by name against the file itself | Amending an approved BRIEF needs a re-signature for a prose error that misled nobody |
| B-6 | bug | Harness defect, not product: the `harness-qa` persona's runner reported exit 1 *after* emitting a well-formed `VERDICT: PASS` digest whose artifact was verified on disk. Return validation for that persona may be misreporting | Not this feature's surface at all |

## Digests this briefing was assembled from

`runs/2026-09-07-01-product/digest.md` (plan drafted) · `runs/2026-09-07-02-product/digest.md` (six
goal-check remedies applied) · `runs/2026-09-07-01-validator/digest.md` (plan panel c0, both readers
ran) · `runs/2026-09-07-03-product/digest.md` (panel record transcribed) ·
`runs/2026-09-08-01-eng/digest.md` (SIMPLIFY altitude) · `runs/2026-09-08-01-validator/digest.md`
(qa gate) · `runs/2026-09-08-02-validator/digest.md` (review panel) ·
`runs/2026-09-08-1-product/digest.md` (goal-check). Plus `notes/qa-BUG-1480-c0.md`,
`notes/qa-BUG-1480-c0-sc06.md` and `notes/research-BUG-1480-goalcheck-c0.md`.
