# CEO briefing — FEAT-42 One root resolver — validate phase

## The one-liner

**The feature does what it set out to do — all eleven success criteria are met and the blocking QA
gate is green — and the review panel still failed it, on one high-severity finding that is this
feature's own defect, one level worse, in the host we call canonical.** The Python half of the fix
is complete and verified. The TypeScript host adapter that *invokes* those gates still picks which
gate script to execute from a caller-supplied working directory. My recommendation is a short
main-session-direct fix before merge, not a re-scope.

## What you are deciding

Two small repairs stand between this branch and merge. Both are in the enforcement layer, so **no
squad may make them** — DEC-174 routes them to you. Neither is a re-plan; neither touches the
approved task set.

1. `.omp/extensions/harness-hooks.ts` — derive the gate directory from the extension file's own
   location instead of from `ctx.cwd`. One constant, eleven call sites downstream of it.
2. `test-check-plan-routes.py:453-454` — a live test case that is green and **cannot fail**.

## How this briefing was assembled

**No report round was spawned.** I read every digest from disk and re-derived the load-bearing
numbers myself. The sources, all under
`.harness/harness/features/FEAT-42-one-root-resolver/`:

| Phase | Digest |
| --- | --- |
| plan (5 runs) | `runs/2026-08-26-2-plan-product/` … `runs/2026-08-26-6-plan-product/digest.md` |
| build, squad | `runs/t01-t02-eng/digest.md`, `runs/2026-08-26-7-eng/digest.md` |
| build, main-session lane | `notes/handoff-build.md`, `notes/receipt-main-session-T-17.md`, `T-18.md`, `notes/verify-technique-2026-08-27.md`, `notes/cwd-import-bypass-2026-08-27.md` |
| qa gate | `runs/2026-08-27-1-validator/digest.md` → `notes/qa-gate-2026-08-27.md` |
| docs sweep | `runs/2026-08-27-2-docs-product/digest.md` → `notes/receipt-harness-documentor-2026-08-27-2-docs-product.md` |
| goal-check | `runs/2026-08-27-3-goalcheck-product/digest.md` → `notes/research-FEAT-42-goalcheck.md` |
| review panel | `runs/2026-08-27-4-panel-validation-validator/digest.md` → `notes/review-harness-code-reviewer-2026-08-27.md`, `notes/review-harness-security-reviewer-2026-08-27.md`, `notes/qa-sc10-mutation-2026-08-27.md` |

Fifteen of the twenty-one tasks ran in the main-session-direct lane and produced no run digest, so
the build's record is the handoff note and the receipts, not `runs/`.

## The blocking finding

`.omp/extensions/harness-hooks.ts:142`:

```
const proc = spawnSync(join(cwd, BIN, script), args, { cwd, ... });
```

`BIN` is the **relative** string `".agents/skills/harness/bin"` (`:5`). So the gate script's own
executable is selected by joining it onto a caller-supplied path. I verified this myself rather than
relaying it: eleven call sites (`:179`, `:186`, `:198`, `:205`, `:212`, `:263`, `:317`, `:318`,
`:325`, `:357`) covering six distinct gates — `check-domain.sh`, `inject-expertise.sh`,
`branch-create-gate.sh`, `bash-write-guard.sh` and `validate-digest.py`. All of them trace back to
`ctx.cwd`.

**Why this is the feature's own defect and not an unrelated one.** Issue #556, which this branch
closes, was that a `harness_boundary.py` in an agent's working directory became the module the gate
imported — the domain gate went from `exit 2 BLOCKED` to `exit 0 enforcement OFF`, switched off by a
file the agent it governs may write. That substituted an imported **module**. This substitutes the
**whole gate**. It is in a file this diff edited (`0a5bd49`, T-20) and it carries no test coverage.

**The comment is what hid it.** T-20 added a note inside that very function saying every script it
invokes "now derives its own root from its own file location, so handing it one is redundant." That
is true, and it sits one line below the call that chooses *which file to execute*. A correct comment
about the adjacent concern is better camouflage than no comment.

**It corrected me.** I had measured — by dispatching a governed agent with no feature-declaration
line and watching it be admitted — that none of this branch's enforcement code had executed against
a live agent, because Claude Code resolves hooks through `${CLAUDE_PROJECT_DIR}`, which is the main
checkout at `3952814`. That measurement is sound but **host-specific, and I stated it without the
qualifier.** Under OMP the gate is selected from the working directory, so an agent working in a
feature worktree runs *that branch's* gates. The consequence is larger than the exploit question:
under the canonical host, **DEC-174's carve-out is enforced by convention alone** — a branch that
weakens a gate is governed by the weakened gate.

**One question I cannot answer and neither can any squad:** whether `ctx.cwd` is steerable by a tool
call inside an OMP session. That decides exploitable-versus-latent. It does not change the finding —
#556's own precedent is that the identical "probably unreachable" assumption was measured wrong.

## The second repair: a test that cannot fail

`test-check-plan-routes.py:453-454` asserts `"IGNORING it" not in r_root.stderr`. I grepped the whole
`.claude/skills` tree: that string occurs **exactly once**, in the assertion itself. Nothing can
produce it, so the assertion is a tautology. The case is green, is counted in every zero-failure
claim on this feature, and its own comment at `:447-452` names the `if asked:` → `if True:` mutant it
exists to kill — which walks straight past it today. Its siblings `19b3`/`19b4` moved to the
resolver's `"discarding"` wording and this one was left behind. Four passes missed it; the goal-check
found it.

## What is verified, and how

| Claim | Evidence |
| --- | --- |
| **All 11 success criteria MET** | goal-check, `sc_status` full and PASS |
| SC-01: zero occurrences of the retired name | **I re-derived it**: 0 across 0 files over 1669 tracked files. Discriminating — 21 across 17 at `3952814` |
| SC-04: seven deleted resolvers gone | **I checked each symbol separately**, not one global grep. All 0 in executable code; both survivors intact (`harness_boundary.py:515`, `post-merge-sweep.sh:64`) |
| SC-05: byte-identical verdicts across the cutover | The real two-sha proof, taken this run: 43 paths, 43 lines each side, 0-line diff — with a **positive control** that moved 17 of 43 lines when mutated. QA had reported the #556 cwd proof against it by mistake; I routed the re-derivation to pm and it now holds |
| SC-10: red-before-green for four resolver functions | Met on its wording, and settled beyond it: a mutation probe killed **6 of 6** mutants with named failures. The receipts are misleading; the coverage is real |
| QA gate (the project's only blocking gate) | PASS. Suite exit 0, 3139 case verdicts, zero failures |
| #556 closed | Same command from repo root and from `bin/` gives a byte-identical verdict set; 203 lines each side, one differing line — the `#556` case going FAIL → `ok` |
| No DEC-174 lane breach in squad-tagged work | The one TEAM-tagged commit (`98bd4b3`) touches no enforcement file |
| Tree state | Zero **source** files dirty at the pinned sha; HEAD is the pin. `check-state.sh` was exit 0 / zero violations until the goal-check digest landed and is now exit 1 on that one bookkeeping violation — see "One red gate" below |

## Where the record is weaker than it looks

- **`e51b814` breached DEC-174 as a record, if not as an act.** It is tagged with three team-lane
  tasks and touches two enforcement-layer test files. The content is correct; the commit simply
  cannot tell us whether a squad or the main session wrote those hunks. Mixed-lane commits destroy
  the only evidence the carve-out has.
- **SC-01's presence half is method-sensitive.** It requires "at least 16 files" importing the
  resolver. Counting `.py` and `.sh` gives 23; counting strict `.py` import statements alone gives
  **14**, below its own floor. It passes on the reading the criterion's wording supports, and I would
  not want that noticed for the first time by someone arguing the other way.
- **SC-09 resolves by accident.** Its three line anchors were comments at `ea71a1c`; fourteen lines
  added above them drifted executable case bodies onto them. It is satisfied, by drift rather than
  design.
- **Two suites are non-hermetic** while any dispatch is in flight, and `validate-digest.py` releases
  a returning agent's claim *before* refusing its return. That defect fired on two separate leads
  during this validation and cost several no-op spawns.

## Budget, and my read on it

**Cycles 6 of 10. Runs 11 of 20.** Both inside budget, and the run count is informational by design.

One cycle was spent in this whole phase — the goal-check lead sent its first pass back for grading
the wrong scope on SC-09, and the second pass came back with a better answer than the lead's own.
The QA gate, the docs sweep and the review panel were all clean first passes. That is what the cycle
counter is for and it is behaving.

Cost worth naming: three leads each burned a no-op spawn reaching for a message tool they do not
hold, while blocked from returning by the claim-release defect. Roughly 60k tokens each, and it is
the same defect three times.

## Proposed backlog

Strike any row by ID. **Unstruck rows become backlog issues on acceptance; anything not listed dies
silently.**

| ID | Finding | Nature |
| --- | --- | --- |
| B-1 | `harness-hooks.ts` selects gate scripts from caller cwd — 6 gates, 11 call sites, no coverage | bug |
| B-2 | `test-check-plan-routes.py:453-454` asserts a string that exists only in the assertion; the case cannot fail | bug |
| B-3 | `harness-brief/SKILL.md:131` prescribes the deleted `harness_root` to every future brief author | bug |
| B-4 | `test-check-plan-routes.py:1133-1136` keeps a live gate exemption alive on a defect that is fixed | bug |
| B-5 | `validate-digest.py` releases a returning agent's claim before refusing the return; fired twice this run | bug |
| B-6 | `test-validate-digest.py` is non-hermetic while any dispatch is in flight | bug |
| B-7 | `bash-write-guard.sh` parses an angle bracket or ASCII arrow in prose as a redirect and refuses | bug |
| B-8 | `bash-write-guard.sh` denies an agent Bash writes to its own dispatched scratchpad | bug |
| B-9 | `change_type: test` exists in plans and in no taxonomy that grades it | bug |
| B-10 | `gh_cost_log.py` reads `FACTORY_GH` not `GH_SYNC_GH`, breaking `test-gh-sync.py`'s offline guarantee | bug |
| B-11 | `gh-sync.py` has `start-task` and no per-task finish command | bug |
| B-12 | Path-shape authorisation cannot see WHICH checkout, so a write lands in the wrong tree unrefused | bug |
| B-13 | Dispatched run-dir slugs a persona cannot write — third recurrence; fix the slug derivation | bug |
| B-14 | `dispatch-guard.sh:105` and `harness-zero-micro-management/SKILL.md:30` hardcode this feature id as the copy-paste exemplar; a lead copying it is admitted and silently routed to the wrong checkout | bug |
| B-25 | The lead digest contract cannot represent an honest send-back: a lead that records cycle 1 FAIL and cycle 2 PASS is forced to a team FAIL, so `check-state.sh` is RED on the goal-check digest at this sha | bug |
| B-15 | `e51b814` mixes team-lane tags with enforcement-file edits; add a commit-tag-vs-files-touched check | chore |
| B-16 | `STATE.md`'s "1040 verdict lines" does not reconcile with the measured 3139 | chore |
| B-17 | Eng digest Q6 (standalone failures) does not reproduce at `9d12e3a`; confirm closed rather than masked | chore |
| B-18 | T-21 has no GitHub sub-issue where every other task has one | chore |
| B-19 | DEC-174 am.4 enumerates the enforcement layer by filename and nothing checks the list | chore |
| B-20 | SC-04's standing invariant covers six of seven deleted definitions; `wayfind.root` is caught by nothing | enhancement |
| B-21 | SC-01 greps the surviving name, so it is blind to the retired one; 8 of 12 docs findings are invisible to it | enhancement |
| B-22 | `check-domain.sh` resolves a relative `file_path` against the cwd; needs a decision, not a guess | enhancement |
| B-23 | Ten further stale-narration doc sites from the sweep | enhancement |
| B-24 | `.harness/expertise/harness-dev-ops.md:30` teaches the retired chain as craft, injected every spawn | enhancement |

## Questions only you can settle

1. **Is `ctx.cwd` steerable by a tool call within an OMP session?** Decides whether B-1 is
   exploitable or latent. It does not change the recommendation.
2. **Does DEC-174's library rule still hold?** It says "a module a gate imports is not itself a
   gate." This feature makes `harness_boundary.py` the import of all six enumerated gates, so a
   squad-authored change to it now reaches every gate without touching one. The enumeration needs no
   amendment; the rule may.
3. **Who lands `harness-brief/SKILL.md`?** It carries the docs sweep's highest-harm defect and
   resolves to `NOBODY` under the domain gate.
4. **Should `check-domain.sh` refuse a relative `file_path` rather than pick a base?** The panel and
   the security reviewer reached this independently: refusing is not the guess the note declined to
   make. Leaving it as-is is defensible; refusing is better.

## One red gate, and why I did not clear it

`check-state.sh` exits 1 at this sha on exactly one violation, and it is bookkeeping, not a
deliverable: `runs/2026-08-27-3-goalcheck-product/digest.md` "does not satisfy the lead digest
contract". The reason is `validate-digest.py`'s rule that a team verdict must equal its worst member
verdict. The goal-check lead honestly recorded **both** cycles — `goal-check-c1` FAIL, `goal-check-c2`
PASS — and reported the team as PASS because the work ends passing. The rule then reads the
superseded FAIL as current.

A legal representation does exist: one member entry per step carrying its final verdict, with the
send-back recorded in `cycles_used`, which is exactly what that counter is for and where I have
recorded it. So the lead can fix this. **I did not spend a lead run on a formatting repair**, and I
did not edit the file myself — it is the lead's artifact and correcting another agent's record by
hand is how a digest stops meaning anything.

I am flagging it rather than clearing it because the contract, not the lead, is the thing worth
changing: as written it makes an honest send-back unrepresentable, and the tempting fix — deleting
the truthful cycle-1 entry — is the record falsification our own rules forbid. That is B-25.

**Nothing has been committed.** The gate is red, project convention is to run it before committing
rather than after, and the record files are safe in the worktree until you decide.

## Recommendation

**Fix B-1 and B-2 in the main-session-direct lane, re-pin, re-run the suite, then merge.** Both are
small and both are precisely the defect class this feature exists to eliminate. Shipping as-is means
shipping the feature's own bug in the host DEC-202 makes canonical, with the branch's stated
achievement — one resolver, no cwd fail-open — untrue at the boundary where the gates are launched.

Everything else on the list is genuine and none of it gates.
