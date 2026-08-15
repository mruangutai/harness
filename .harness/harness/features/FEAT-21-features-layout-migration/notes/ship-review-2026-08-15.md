# FEAT-21 — the features layout migration, ready to ship with one decision for you

**The move is done and proven. Every one of the 14 success criteria is met. One criterion, SC-12, is
true of the code and false of the commit count, because fixing a late defect cost a third commit
where it asked for two. That is the single thing I need you to rule on — ratify the deviation, or
have pm amend SC-12's wording. Nothing else is blocking.**

`.harness/features/` now lives at `.harness/harness/features/` — a repository segment, the shape the
multi-repo control plane needs. Twenty-one feature directories moved, and the twelve readers that
resolve that path moved with them **in one commit**, so no landed state exists where the tree and its
readers disagree. The layout detector reads `features: CLEAN — evidence migrated`, `docs: CLEAN —
evidence legacy` — docs deliberately stay behind, and unit 4 moves them.

## What it took

Ten tasks, all `main-session-direct`, because the files this feature edits include four DEC-174
carve-out scripts — the gates themselves. No squad executed any of it; squads planned, reviewed and
verified. Three commits carry the work: `5afa7e3` (the parity test alone), `d033b9d` (the atomic
cluster: the move plus all twelve readers, 617 files, 567 renames), `b1d3925` (the SC-10 fix).

**Seven runs, four rework cycles, against budgets of 20 and 10.** No crossing. Each cycle bought
something: the eng architecture review's cycle-0 FAIL, the pre-commit panel's must-fix, and the
goal-check's SC-10 miss were all real defects found before they shipped.

## What actually caught things — worth reading, because the pattern repeats

**The defects that mattered were invisible to every green gate.** The eng review's three must-fixes
were feature-path resolvers carrying no `.harness/features/` literal at all — a fixed `../../..`
climb, a glob whose zero-match case exits 0, and a module-scope `open()` on a joined tuple. A literal
sweep sees none of them; one would have killed the whole unit suite at import, and two would have
gone silently green.

**A signed decision shipped half-built with its task marked done.** D-08 was a two-sided trade — do
*not* qualify the dictionary keys, *do* qualify the finding labels. The build took the deferral and
dropped the delivery. Every gate was green, because each task's `verify:` bound only its own
mechanical form. A human reading the diff caught it. That is DEC-174's compensating control working
exactly as designed, and it is also the control that has no backup.

**Two gates spent the whole cluster passing while examining nothing.** Mid-build, `check-state.sh`
exited 0 with zero findings and `check-plan-routes.py` reported `examined 0` — correct at the time,
but nothing in the plan's verification chain would have noticed if they had stayed that way. I caught
it by comparing the note-line count against a baseline captured before the move, not by reading an
exit code. When a change moves what a gate *discovers*, its exit code stops being evidence.

**And the last one was the parity test itself.** SC-10 asked for a test proving the CI rendering and
the session-entry rendering agree. The test that shipped composed the session-entry side *itself*, in
a helper its own comment called "mirrored" — so it proved the module against a copy of the gate.
pm found it by mutation. The fix deletes the mirror and runs the real `check-state.sh` as a
subprocess. It is now proven in both directions: I killed the gate-side mutant, qa killed the
`render()`-side one.

## The decision I need

**SC-12** says everything beyond this feature's own planning record lands in **exactly two** commits.
It was met at `d033b9d`. Fixing SC-10 made it three. I did not edit either criterion — that is yours
alone — and I did not skip the fix, because shipping a mutation-proven gap in the exact seam this
feature exists to guard is the worse trade.

**My read: the deviation is cosmetic and the purpose survives.** SC-12 exists so no landed commit
shows a half-moved tree. The cluster still landed atomically; `b1d3925` lands *after* it, touches one
test file, and adds nothing to the migration. The validation panel reached the same conclusion
independently. **Options:** ratify the deviation as recorded, or have pm amend SC-12 to admit a fix
commit against an already-landed task. I recommend the first — amending a criterion after the fact to
match what happened is the weaker record.

## Two corrections to my own record, before you read anything else

The panel caught both, and they are mine, not the builders'.

1. I told two squads the review range held **five** commits. It holds **eight** — I forgot my own
   three state-record commits. It misled nobody: two reviewers re-measured and corrected it. The
   figure that matters, three commits touching anything outside this feature's record, I re-verified
   mechanically and it stands.
2. I reported **18** segment-qualified finding labels. It is **17** — my grep counted the function
   definition alongside its call sites.
3. My distillation dispatch to the validator squad asserted three things about its members that were
   false: that its reviewers are write-less (all four hold `Write` and own their Expertise grant, so
   no ops needed me), that they kept observation logs this feature (none did), and it named a file
   pattern that would have dropped two of the ui reviewer's three notes — the two from which it drew
   four of its seven entries. The lead corrected all three rather than routing around them. This is
   my own recorded rule about dispatch premises, and I did not follow it.

## Where each squad's verdict comes from

**No report round was spawned.** I assembled this from the digests on disk, and I name them so you
can tell a complete briefing from one missing a phase:

| Squad | Run | Verdict | Digest |
|---|---|---|---|
| product | plan revision | PASS | `runs/2026-08-14-1-product/digest.md` |
| eng | architecture review | FAIL → PASS | `runs/2026-08-14-1-eng/digest.md`, `digest-recheck.md` |
| validator | pre-commit panel | FAIL (1 must-fix, fixed) | `runs/2026-08-14-1-validator/digest.md` |
| validator | qa gate | PASS | `runs/2026-08-14-2-qa-validator/digest.md` |
| product | goal-check | FAIL (SC-10) | `runs/2026-08-14-2-goalcheck-product/digest.md` |
| validator | review panel | PASS, severity med | `runs/2026-08-14-3-panel-validator/digest.md` |
| product | SC-10 re-check | SC-10 met, escalates SC-12 | `runs/2026-08-14-3-sc10recheck-product/digest.md` |

The blocking `test_matrix` gate passed and **earned it**: the matrix floor for this change is `unit`
alone, which runs none of the three suites that actually bind the gate scripts. qa added `integration`
under the floor-not-ceiling clause. A future gate run reading the floor literally would pass while
binding nothing — that is row B-3 below.

No UAT was required: the BRIEF declares no UAT criteria, and all 14 criteria verify by automation or
inspection.

## Memory: what the org learned

Distillation ran for all three squads and **every member applied its own entries** — nothing was
stranded. I ran `check-expertise.sh` myself afterwards: **13 of 13 files OK**, every one inside
budget.

- **validator** — five files updated; the digest-skim contributed 9 of 24 accepted entries, so it
  earned its cycle. The lead flags the real caveat honestly: 11 of 12 relayed candidates were
  accepted and three of four members rejected nothing, so this round's filtering signal comes almost
  entirely from one member. Worth watching — a member that accepts everything is deferring, not
  judging.
- **product** — twelve entries across pm and the lead, six by displacement against capped sections;
  exactly one entry came from the skim rather than pm's own artifacts.
- **eng** — three ops, all self-derived, no member spawns. The correct result: every task here was
  layer-0, so no engineer produced anything to distil and none was invented.
- **mine** — three patterns displaced by stronger ones, one gotcha sharpened now that I know the
  write-guard's actual mechanism, and both open questions updated with this feature's evidence.

## The honest limits

- **Nothing anywhere stages two repository segments.** Multi-repo is this sequence's entire purpose,
  and every fixture builds one segment. Both of the panel's unresolved coverage findings are
  invisible to every green gate for exactly this reason. B-1.
- **Six of 186 test cases have been mutation-probed.** Suite-green cannot distinguish broad coverage
  from narrow anywhere outside those six.
- **Four criteria are inspection-only** by the BRIEF's own statement — a reviewer reading an artifact
  is the whole control, and that control already failed once here.

## Proposed backlog

Unstruck rows become issues on your acceptance; anything not listed dies silently, so this is all of
it.

| ID | Nature | Item |
|---|---|---|
| B-1 | enhancement | **Nothing stages two repository segments.** One fixture change to `test-check-state.py` and `test-check-plan-routes.py` closes this, pins D-08's delivery half, and adds the segment-level readability guard together. qa's recommendation and mine — the strongest row here. |
| B-2 | bug | **D-08's delivery half is correct today and pinned by nothing.** Neutering `fpath()` leaves the suite at exit 0; code-reviewer adds that `test-check-state.py` carries a weakened assertion. The half that was previously missed is the half still untested. |
| B-3 | bug | **`check-state.sh` has no zero-discovery guard.** `check-plan-routes.py` has one in CI; check-state is the higher-consequence gate — six invariants, the budgets and the station mirror all evaluate over its discovery set — and nothing bounds it. |
| B-4 | bug | **`check-plan-routes.py` has no segment-level readability guard.** A `chmod 000` segment directory silently vanishes from the scan; demonstrated live by code-reviewer. |
| B-5 | chore | **`branch-create-gate.sh` hardcodes the segment.** It should derive it; a bare wildcard is wrong, because feature ids are coined per-BRIEF with no cross-repo uniqueness. |
| B-6 | chore | **The gh-sync walk-up probes `team-config.yaml` where T-10's intent named `harness.json`.** The choice is right — it matches every other root probe — but no test discriminates, and it deserves a decision record. |
| B-7 | bug | **`bash-write-guard.sh` blocks quoted redirect targets.** It masks quoted spans, so any `>"$tmp"` blocks, literal or variable. It blocked an **approved** plan `verify:` clause; every one had to be re-run from a script file. |
| B-8 | enhancement | **Nothing reconciles a landed diff against the plan's declared files.** `.harness/expertise/harness-pm.md` — injected into every pm spawn — was path-corrected inside a cluster commit with no task naming it. Benign this time and verified so; the gap is structural. Raised independently by two reviewers. |
| B-9 | chore | **The `no-rows` comment points at the wrong file.** It credits `test-check-state.py`'s `case_x`; the real coverage is case 16 of `test-layout-migration.py`. Cosmetic now, misleading on the next edit. |
| B-10 | chore | **Turn SC-06's manual `--resolve` pair into a standing test case** in `test-check-domain.py`. pm's suggestion. |
| B-11 | enhancement | **Give the INV-27 composition one owner.** Moving it into `layout_migration.py` is the structural fix for the parity seam; deferred because it re-opens carve-out gate code after review. |
| B-12 | chore | **Four criterion-wording drifts, reported and deliberately not rewritten:** SC-02's post-move capture cannot name the commit it lands in; SC-06 declares `unit` where the pinning suite is `integration`; SC-05 declares `integration` where its check is a plan verify; T-01's intent still forbids the fixture tree the sanctioned fix uses. |
| B-13 | chore | **Three FEAT-20 review notes rode into `d033b9d`.** Untracked before this feature, harmless, recorded rather than repaired — rewriting a landed 617-file commit to drop three notes costs more than it saves. |
| B-14 | enhancement | **Raise mutation coverage past six of 186 cases**, or accept explicitly that suite-green is a weak signal outside them. |

| B-15 | bug | **`harness-distill` describes a check `check-expertise.sh` does not implement.** The doc says path-mentioning craft entries are flagged advisorily for a human; the checker has no advisory category and no such rule. The craft/repository split has no checker support. |
| B-16 | bug | **The repository Expertise layer is documented but unwritable.** `harness-distill` specifies `.harness/<repo>/expertise/<agent>.md` with a 40-line budget; no grant in `team-config.yaml` covers it. I ran the domain hook: that path resolves to **NOBODY** for every agent. The split shipped without its grant, and nothing exercised it, so nothing caught it. |
| B-17 | chore | **Four of five validator-squad Expertise files now sit at Patterns 15/15.** Every future distillation for those roles is displacement-only. A cap raise, a periodic curation pass, or accepting it — worth deciding before the next feature closes. |

## What happens on your acceptance

The branch `feat/FEAT-21-features-layout-migration` is ready; merge and PR stay yours. On acceptance
the milestone closes, parent issue #388 closes, and the unstruck rows above become backlog issues.
