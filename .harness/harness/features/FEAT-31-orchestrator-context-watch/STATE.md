# STATE

## Current

- feature: FEAT-31-orchestrator-context-watch · phase **ship** · **19 of 19 tasks `done`**
- tree clean at **`0ab4de0`** (one untracked `.harness/logs/gh-cost-*.jsonl`, a gh-sync by-product)
- status: **awaiting_user** — everything a squad can do is done
- budget: **cycles 6/10**. **runs 21/20 — CROSSED**; informational only (INV-22), never a stop.
- `review_sha`: **`0fc10e5a9f48afae512baed6d9297aab88e7f181`**
- **briefing: `notes/ship-review-ship1.md`** (+ `.html`) — the operator's artifact and where the full
  detail now lives. It proposes **B-1..B-22**; anything not listed there dies silently.
- `check-state.sh`: ONE violation, FEAT-26's unapproved BRIEF (another flow). None in FEAT-31.
- **BOTH GATES PASS** (approved / operator / 2026-08-21). **The operator PRE-APPROVED the ship.**

### ALL THREE MACHINE GATES ARE SETTLED — THE UAT IS THE ONLY THING LEFT

**qa (blocking): matrix PASSES** — unit, integration, `--check-kinds` all exit 0, zero FAIL /
MISCONFIGURED / KIND-DRIFT. Its one FAIL was **SC-09 approved with no implementing task**, hidden by
`plan.yaml`'s D-02 *falsely* claiming plan4 closed it. Closed by **T-19**; D-02 corrected with the
superseded sentence KEPT and marked.

**panel: FAILed on one `high`, now FIXED and re-verified.** The warning never said the write LANDED,
against a **hard obligation** in the feature's own `notes/settled-Q-HOOKCTX.md`; exposure 36 of 36. It
now opens *"this write already landed on disk -- do not retry it and do not undo it."*, pinned by ORDER
assertions on three surfaces with a diff-confirmed mutant.

**goal-check: 12 of 14 met** — SC-01..09, 11, 13, 14. SC-10 not met, SC-15 partial; both `verify: uat`.

**`gates.uat: blocking_when_uat_criteria_exist`, so the UAT blocks the ship independently of qa and the
panel. Only the operator can discharge it.** SC-15's behaviour half needs a **CLEAN relay** — a
successor whose ONLY input is the feature directory. **My own relay was refused as CONFOUNDED,
correctly**: my first dispatch did match `handoff-build.md`'s `## Next`, but I also held a prompt naming
T-05 and T-09, so one observation has two sufficient causes. pm refused rather than discounted it, and
I declined to grade my own relay.

### CLOSE-OUT IS DONE

**Ship-refresh SKIPPED — no map exists, nothing to intersect.** Distillation ran as three concurrent
lead dispatches: **329 to 349 entries across 15 files, both tiers exit 0, and I verified every changed
file by enumerating ids against HEAD — nothing lost** (three files carry deliberate displacements).

**All three squads independently found a defect outranking the pass's own output:
`expertise-merge.py` implements only `add`** — union-only, exit 7 on same-id-different-text, exit 8 over
cap, no removal path — while `harness-distill` REQUIRES displacement at a full section. At cap the
required move and the safe move are mutually exclusive. **Two eng members and one qa member therefore
hand-edited Expertise files outside the tool's lock while siblings were live writers.** It also silently
no-ops at exit 0 on a non-matching entries file. I took the disciplined branch, so my own capped
sections are unchanged and `expertise_full` is the honest report. **Five lead `replace` ops are
stranded**, kept verbatim in `runs/distill-eng/digest.md` and `runs/distill-validator/digest.md`.

**The digest-skim measurement came back AGAINST its hypothesis** — eng 9 of 12 from the skim vs 3 from
logs; validation 7 and 0 (no member keeps a log); product 5 and 0 from a skim that landed after
dispatch. **The correlation is the real result: a member without an observations log has its memory
written entirely by its lead.**

### MY SIX ERRORS — the durable rules; the detail is in the commit messages

1. **A run digest is not evidence until its run has RETURNED.** Broken three times; the third
   **dispatched T-19 twice** (two hosts; `mutates_repo` serializes inside ONE host only). Only pm's
   "run verify BEFORE your edit" in T-19's intent stopped a double edit. Later proved by watching a
   `blocked` digest hash stable five times, then change to PASS.
2. **Regenerate a generated index UNCONDITIONALLY** after any body edit — T-19 shifted 39 `@line`
   anchors. "Only if the row changed" was wrong in the silently-corrupting direction.
3. **DEC-141 governs `render-map.py`**, not index generation — I cited it wrongly.
4. **`^### DEC-` matches only the 25 amendment sub-headings**, not the 195 entries: it is 197, not 194.
5. **I named artifact paths personas hold no grant for** — pm's goal-check path (#216) — and asserted
   the two reviewers hold no Write when both do. **That refusal surfaced the merge-tool defect.**
6. **BOTH SIDES OF AN EQUALITY OVER A MOVING CORPUS MUST BE MEASURED IN THE SAME BREATH.** "103 + 5 vs
   a glob of 107 — exact agreement" does not add up. Re-measured atomically: **109 = 104 + 5.**

**Errors 2, 3 and 5 were caught by subordinates reading source instead of complying with my prose; 6 by
the review panel.** Four of the six were assertions I made without checking.

### THE ENFORCEMENT LAYER GOVERNING THIS SESSION IS THE MAIN CHECKOUT'S

Hooks resolve via `CLAUDE_PROJECT_DIR` to the main checkout, so a branch changing the enforcement layer
is governed by the OLD layer while being built. **T-15's `agent` rule is INVERTED in-session** (the
branch validator passes with the key and fails naming `runs[9]` without it; the session hook rejects it
as `undeclared`). **T-17's hook cannot be observed firing from here** — first fires after merge. Neither
is a defect. The VERB is the good one: `OVER BUDGET (already written)` is why every one of my
`feature.json` writes survived.

### Premises a successor must not re-derive

- **NO GATE EVER WALKS THE REAL PROJECTS ROOT** — `verify-context-watch-live.py` is in neither script
  list, so even its own `--self-test` never gates and the discovery-depth mechanism this feature fixed
  stays undetectable by CI. Deepest residual (B-1).
- **The tool cannot say "I could not scan"** — `main()`'s catch prints "no orchestrators found" at
  exit 0, a clean sentence meaning the opposite of the truth.
- **"187 PASS lines" IS NOT A COVERAGE MEASURE** — one PASS line per script, and the file carrying all
  78 defect proofs prints `ok`/`FAIL`, contributing exactly one.
- **Q-DEC159CAP** — `DECISIONS.md:3986` denies handoff notes above 40 lines, its own `:3968` says ~60,
  `check-domain.sh:951` enforces 60. It survived T-19, a cycle about a false clause in that same entry.
  No SC covers it, so fixing it is scope expansion; left deliberately (B-2).
- **Q-HOOKCTX is CLOSED.** #663-#669 are filed.
- Do NOT trust a `verify:` floor expressed as an absolute case count; verify by case NAME.
- Do NOT run `feature-worktree.py behind` from inside this worktree — use the PRIMARY checkout.

## Open Questions

<The channel from subagents to the user. A non-empty entry is an ACTIVE ROUTING SIGNAL: the
orchestrator asks the user, writes answers to notes/answers-<runid>.md, and re-delegates with that
path. Clear each entry when it is answered.>

- **Q-UAT, BLOCKING, THE OPERATOR'S ALONE.** SC-10 and SC-15's behaviour half; the latter needs a relay
  whose only input is the feature directory.
- **Q-SIGNATURE, BLOCKING-ADJACENT.** The plan gained a 19th task after the 18-task signature.
  `approval:` is byte-identical and SC-09 was already approved scope, so I read T-19 as fulfilling the
  signature rather than extending it — the operator confirms, not me.
- **Q-MERGETOOL, BLOCKS THE NEXT DISTILLATION, not this ship.** `expertise-merge.py` implements only
  `add`; five lead `replace` ops are stranded and two accepted-in-judgement candidates are unwritable.
- **Q-STRAY, non-blocking, OUTSIDE MY WORKTREE.** Two stray files in the MAIN checkout:
  `runs/t09-product/digest.md` (stale, claims BLOCKED, contradicts the real PASS) and
  `runs/fix3-eng/state.yaml`.
