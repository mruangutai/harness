# Receipt — harness-backend-dev — FEAT-23 — 2026-08-17-13-distill-eng

## BLUF

Three ops applied to `.harness/expertise/harness-backend-dev.md`: P-13 broadened to cover the
untracked-file case (C1, accept), P-14 replaced with a structural-guarantee-over-conditional-guard
rule (C2, accept), P-06 replaced with a RED-integrity rule sharpened from C3 (C3, accept in
narrowed form). No section grew or shrank — Patterns stayed at 15/15 by construction (displacement
only). `check-expertise.sh` OK, exit 0. `run-unit-tests.sh` exit 0, 197 `PASS` lines (script- and
case-level mixed — some scripts print per-case `PASS <name>` lines, not one line per script), 0
`FAIL` lines (re-run for `suite:` truthfulness on an Expertise-file-only edit — does not validate
the edits themselves, only that nothing else broke).

## Section counts

| Section | Before | After |
|---|---|---|
| Patterns | 15/15 | 15/15 |
| Gotchas | 9/15 | 9/15 |
| Outcomes | 0/10 | 0/10 |
| Open | 0/5 | 0/5 |

## Ops applied (with source bucket)

1. **`replace P-13`** — bucket (b), lead-relayed (C1), verified at source by me against
   `receipt-harness-backend-dev-T-05-c1.md` §"Iron Law discipline". Old P-13 assumed a tracked
   file (`git show HEAD:<path>`); the T-05 case was a brand-new untracked file with no `HEAD:<path>`
   to swap in, and what actually happened (hash, move out of tree, watch RED, restore, re-verify
   hash) is a broader recipe the old wording did not cover. New text: "WHEN production code was
   edited before RED was watched DO reconstruct RED: hash the file, restore its pre-edit state
   (`git show HEAD:<path>` if tracked, moved out of the tree if untracked), confirm the expected
   failures, restore, and re-verify the hash — never treat the lapse as harmless." (47 words)

2. **`replace P-14`** — bucket (b), lead-relayed (C2), verified at source by me against
   `gh-sync.py:72,75,682,713,744` per the dispatch's own citation. The old P-14 ("scope argv
   comparisons to argv[1:3]... against this repo's gh-call fakes") names "this repo" explicitly and
   fails the craft test on its own text — it belongs at the repository tier, not craft. This made
   it the weakest current holder by the "true in a repo you've never seen" bar, and C2's rule
   clearly passes that bar, so I displaced it. New text: "WHEN a side-effecting write must not fire
   on an early-exit path DO place it as the unconditional last statement reached after every exit
   primitive (e.g. `sys.exit`), not behind a conditional guard enumerating exit cases — reaching
   that statement is itself the proof no early exit fired." (46 words)

   **Relocation attempted and blocked, not completed — flagged below.** I tried to preserve the
   displaced P-14 content at the repository tier (`.harness/harness/expertise/harness-backend-dev.md`,
   per `harness-distill`'s three-tier description) so it wasn't simply lost. `check-domain.sh`
   denied the write: that path is not in my permitted set (`.harness/expertise/harness-backend-dev.md`
   is; `.harness/harness/expertise/**` is not). Per `harness-digest-dev`, I did not work around the
   guard. Net effect: the argv[1:3]-vs-[0:2] gh-fake convention is no longer recorded anywhere in
   Expertise. See open question Q1.

3. **`replace P-06`** — bucket (b), lead-relayed (C3), narrowed per review. C3 as given bundled two
   claims: (i) a green pre-edit RED run means stop and investigate provenance, (ii) never overwrite
   a predecessor's artifact documenting real work. (ii) restates preloaded rule 15 ("never falsify
   the record") and does not earn its own slot. (i) is durable RED-integrity craft the TDD skill
   doesn't state (that skill says "watch RED fail," not "what a passing RED means") and is more
   broadly load-bearing across dispatches than P-06's narrow awk/sed-anchor trap, so it displaces
   P-06. New text: "WHEN the mandated pre-edit RED run passes on an untouched tree DO stop — a
   green RED means the premise is stale or the test is vacuous, not permission to proceed — and
   establish provenance from on-disk artifacts before writing or overwriting anything." (43 words)

## Rejected

- **C3, framed as "guard against concurrent duplicate dispatchers"** — rejected outright per the
  dispatch's own warning: that framing is a harness bug report (duplicate-dispatch incident),
  already logged in `open_questions` elsewhere, and ages into a stale workaround the moment it's
  fixed. Not craft.
- **C3's "never overwrite a predecessor's artifact" half** — rejected as its own entry. It restates
  preloaded rule 15 verbatim in spirit; an Expertise entry that only repeats a preloaded rule adds
  no new information six spawns from now.
- **Bucket (c) self-derived candidate — comment citing dispatch item numbers instead of in-file
  anchors** (from `receipt-harness-backend-dev-2026-08-17-10-simplify-eng.md`, both edit sites:
  `"item 1's exit contract"` → `"the EXIT CONTRACT paragraph above"`, `"item 6's widened"` →
  `"board-station.py's broad except Exception... documented in its module docstring's EXIT CONTRACT
  paragraph"`). Real and transferable ("WHEN a comment cites a rationale DO anchor to the code's
  own contract text, never dispatch/task numbering"), but examined against every current survivor
  and it does not clearly outrank any of them — it is evidenced by one incident (two sites, same
  fix, same feature) against patterns already curated across multiple features. Section is full;
  no displacement made. Dies here, not merged, not shelved elsewhere.

## Bucket report (explicit, all three)

- **(a) from an observations log:** zero, by construction — I have no observations log on FEAT-23
  (per dispatch: `observations/` on this feature holds only orchestrator, pm, product-lead).
- **(b) surfaced by the lead's skim relay:** 3 accepted (P-13 replace, P-14 replace, P-06 replace —
  C3 narrowed), all independently re-verified at source by me before acceptance (T-05 receipts,
  `gh-sync.py` line citations, the simplify receipt's own two edit sites for the rejected candidate
  above).
- **(c) self-derived, not in the relay:** 1 examined (comment-anchoring rule), rejected — reason
  above. No self-derived candidate survived to an op.

## Pre-existing entries confirmed intact

- **Patterns:** P-01, P-02, P-03, P-04, P-05, P-07, P-08, P-09, P-10, P-11, P-12, P-15 — unchanged,
  byte-identical to the pre-dispatch file. P-13, P-14, P-06 — text changed in place (same ID slots,
  same section, same count), per the three ops above.
- **Gotchas:** G-01 through G-09 — unchanged, byte-identical. Not touched this cycle.
- **Outcomes / Open:** still empty; no candidate this cycle warranted either section.

## `check-expertise.sh` — verbatim

```
$ bash .claude/skills/harness/bin/check-expertise.sh .harness/expertise/harness-backend-dev.md
OK   .harness/expertise/harness-backend-dev.md
EXIT: 0
```

## `suite:` truthfulness — verbatim

```
$ bash .claude/skills/harness/bin/run-unit-tests.sh > <scratchpad>/feat23-distill-suite.log 2>&1
EXIT: 0
$ grep -c "^PASS" <scratchpad>/feat23-distill-suite.log
197
$ grep -c "^FAIL" <scratchpad>/feat23-distill-suite.log
0
```
(197 is a count of lines matching `^PASS`, mixing per-script and per-case output — not "197
scripts". No source touched this cycle — Expertise-file-only edit — this re-run establishes
`suite: pass` truthfully per FEAT-12's precedent (`receipt-harness-backend-dev-distill-c1.md`),
nothing more.)

## Open questions

- **Q1 (non-blocking):** the repository-tier Expertise path (`.harness/harness/expertise/
  harness-backend-dev.md`) described in `harness-distill` is not in my `team-config.yaml` write
  domain — `check-domain.sh` denies it. Two separate issues bundled here: (a) the manifest may need
  a per-agent repository-tier entry if that tier is meant to be used, and (b) even if writable,
  `inject-expertise.sh` only reads `$root/.harness/expertise/$agent.md` (project) and
  `$HOME/.harness/expertise/$agent.md` (global) — it has no third read path for
  `.harness/harness/expertise/`, so a file there would never reach a spawn regardless of who writes
  it. Net effect on this run: P-14's original argv[1:3]-vs-argv[0:2] convention for gh-sync's fake
  harness is not preserved anywhere. Routing/wiring decision, not mine to make.

## Files touched

- `.harness/expertise/harness-backend-dev.md`

## Bounds respected

No `plan.yaml`, `BRIEF.md`, `feature.json`, `STATE.md`, or DEC-174 enforcement file touched. No
`git add`, no commit, no `gh` call. Attempted write to `.harness/harness/expertise/
harness-backend-dev.md` was denied by `check-domain.sh` and not retried or worked around.
