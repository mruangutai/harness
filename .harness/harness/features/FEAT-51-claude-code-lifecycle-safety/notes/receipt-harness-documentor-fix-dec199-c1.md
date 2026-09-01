# Receipt — harness-documentor — FEAT-51 T-06 fix cycle — amend DEC-199

**Both false present-tense claims in DEC-199 are amended in place, DEC-210 is named as what closes the
first reporting consequence, and the disk-inference consequence is stated as still open. All three
acceptance commands exit 0.** History in DEC-199 — occurrences 5..8, the "FLOOR, never a total" framing,
the per-consecutive-stop-sequence bound paragraph's opening — is untouched.

Files touched (exactly two, both absolute under the worktree):
- `.harness/harness/docs/DECISIONS.md`
- `.harness/harness/docs/DECISIONS-INDEX.md`

## Verified false at source before editing (not taken on report)

- `validate-digest.py:1662-1680` — `_return_verdict == "SUSPENDED"` with live children validates the
  `awaiting` list against the actual child set and `return 0`. A nonterminal turn-end exists.
- `inflight_registry.py:568-583` — `children_refusal_lines` ends by naming `VERDICT SUSPENDED` with an
  awaiting list; it carries no once-only bound. The old sentence "states the same bound" was false.
- `validate-digest.py:1606` — the `stop_hook_active` passthrough is intact, so the per-consecutive-stop-
  sequence mechanism sentence and the residual sentence remain current truth and were kept.

## Passage 1 — DECISIONS.md, was `5708-5717`, now `5708-5720` (verbatim)

> **Issue #551's dispatch cause is closed, and so is the first of its two reporting consequences.** A lead emitting a
> terminal verdict about members it cannot see is closed by DEC-210: a lead or orchestrator whose children are live has a
> legal NONTERMINAL turn-end, `VERDICT: SUSPENDED` carrying an `awaiting` list naming every live child, accepted at exit 0
> inside `validate-digest.py`'s `hook_mode` (`.agents/skills/harness/bin/validate-digest.py:1662`), so no parent is forced
> to grade work it has not seen. The second consequence — an orchestrator inferring run verdicts from disk — is NOT
> closed, and nothing in this file closes it. No wait closes either: the `SubagentStop` hook passes through on
> `stop_hook_active` to avoid an infinite stop loop, so a stop refusal fires at most once per consecutive stop sequence and
> re-fires on each later wake while a child is still live. What ships is aimed at the false REPORT — a lead or
> orchestrator returning a TERMINAL verdict while a child it dispatched is still claimed is REFUSED on that hook once per
> consecutive stop sequence, the one-correction-round strength every other digest contract in that file has, and again on
> each later wake; the loss itself is prevented at the `PreToolUse` hook, whose refusals have no once-only bound. The
> residual, plainly: a second identical return ships when it is immediate, the refusal re-fires only on a later wake while
> a child is still live, and an orphaned child of an interrupted parent has no parent left to refuse it.

## Passage 2 — DECISIONS.md, was `5725`, now `5728-5730` (verbatim)

> `inflight_registry.py`'s refusal message carries no once-only bound; it ends by naming the legal turn-end for a lead or
> orchestrator whose child is live — `VERDICT: SUSPENDED` with an awaiting list naming every live child
> (`.agents/skills/harness/bin/inflight_registry.py:579-582`).

No "Amendment:" construct was added (DEC-205); both passages were rewritten in place.

## Index

The DEC-199 ruling half is hand-written and was updated by hand, then the index regenerated:
`… #551's dispatch cause closes, and DEC-210 closes its false-verdict consequence.` (27 words, inside the
20-non-whitespace-character floor and the 30-word cap). Regeneration recomputed the row's refs
(`DEC-193 DEC-210`), its tags, and every `@line` anchor from DEC-200 onward (+5 lines).

## ONCE_RE occurrence counts — measured, not assumed

`ONCE_RE` = `fires at most once|fires once|refusal fires once|a second identical return will ship|a second identical return ships|one-correction-round`

| | count | line : match |
|---|---|---|
| before | 3 | `5711` "fires at most once" · `5713` "one-correction-round" · `5715` "a second identical return ships" |
| after | 3 | `5714` "fires at most once" · `5717` "one-correction-round" · `5719` "a second identical return ships" |

All three survive inside DEC-199, all three still current truth, and each carries a `QUALIFIER_RE` hit in
its own sentence ("per consecutive stop sequence" twice, "re-fires" once) — graded by
`test-lead-stop-and-wake.py`'s per-occurrence cases, which pass. The `BOUND_SITES` floor (DECISIONS.md is
the sole entry, line 42) is satisfied with margin.

## Acceptance — three commands, run separately, statuses captured individually

| # | command | exit |
|---|---|---|
| 1 | `gen-decisions-index.py --stdout \| diff -q - DECISIONS-INDEX.md` | `0` |
| 2 | `test-gen-decisions-index.py` | `0` |
| 3 | `test-lead-stop-and-wake.py` | `0` |

Baseline before any edit was also `0/0/0`, so all three discriminate on my change rather than reporting a
pre-existing green from a different cause — command 1 was re-greened only by the regeneration.

## Read-not-run re-assertion of the DEC-210 region

`DECISIONS.md:6515-6544` still contains `check-domain.sh` (6516, 6527, 6536), `plan-sign-gate.sh`
(6517, 6524), `quarantine.py adopt` (6519, 6542), and names `plan.yaml` and `plan-merge.py` in one
sentence at 6524-6525. Nothing in DEC-210 was edited.

## Cross-tree write check

After the edits, `git -C /Users/molchairuangutai/GitHub/harness status --porcelain` shows six `??`
untracked entries (other features' notes, `.harness/logs/2026-09-01.md`, two grilling notes) and **zero
`M` entries** — the main checkout's `DECISIONS.md` and `DECISIONS-INDEX.md` are unmodified, so it gained
nothing from this run. In the worktree, `git diff -U0` on my two files bounds my change to exactly three
hunks: `DECISIONS.md @@ -5708,10 +5708,13` and `@@ -5725 +5728,3`, and `DECISIONS-INDEX.md @@ -199,12
+199,12`. The worktree's other modified paths (`test-harness-yaml.py`, `feature.json`, two notes files)
were dirty at spawn and are siblings' work, not mine.

## Open

- DEC-199 now points forward to DEC-210; DEC-210 still does not point back at DEC-199 in its prose,
  though the generated refs graph links both directions. Cheap half done as dispatched; the other half
  is DEC-210's owner's call and out of scope here.
