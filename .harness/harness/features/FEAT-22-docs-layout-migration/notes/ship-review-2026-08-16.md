# FEAT-22 — ship review

**The docs layout migrated, and it is ready to ship.** Twelve of twelve success criteria are met at
`b479afd`. Every gate passed: the blocking qa gate, the four-reviewer panel, and the goal-check.
Six commits, 32 files, nothing pushed. What is left is your call — accept, or send it back.

**What this feature does for you.** The harness's four design documents plus `org.html` now live at
`.harness/harness/docs/` instead of `docs/harness/`. That is unit 4 of the multi-repo control plane:
every piece of harness state now sits under one repository-segmented root, so pointing the harness
at a second repository no longer means the design docs of two projects collide in one directory.
If it were wrong you would see it immediately — the gates that read those docs would fail to find
them, which is exactly what happened mid-build and was caught.

---

## How this briefing was assembled

**No report round was spawned.** I read every run's digest off disk instead, including the plan and
build phases I did not run. That is deliberate and it costs zero spawns; the alternative buys a
re-narration of files I can open. **The digests this is drawn from**, all under
`.harness/harness/features/FEAT-22-docs-layout-migration/runs/<id>/digest.md`:

`2026-08-15-1-product` · `2026-08-15-1-archreview-eng` · `2026-08-15-2-archreview-eng` ·
`2026-08-15-3-product` · `2026-08-15-4-archreview-eng` · `2026-08-15-5-validator` ·
`2026-08-15-6-validator` · `2026-08-15-6-product` · `2026-08-15-7-archreview-eng` ·
`2026-08-15-8-archreview-eng` · `2026-08-15-7-validator` · `2026-08-15-9-product` ·
`2026-08-15-10-archreview-eng` · `2026-08-15-10-validator` · `2026-08-16-11-product` ·
`2026-08-16-11-archreview-eng` · `2026-08-16-12-qa-validator` · `2026-08-16-13-panel-validator` ·
`2026-08-16-13-goalcheck-product` · `2026-08-16-14-regrade-product`

Plus `notes/simplify-pass-2026-08-16.md` and `notes/layout-boundary-2026-08-15.md`.

---

## The gates

| Gate | Verdict | What it actually proved |
|---|---|---|
| **qa** (blocking) | **PASS** | unit exit 0 (15 scripts, 707 checks), integration exit 0 (12 scripts, 652+). It perturbed a control in memory and watched it redden over a non-empty 8-file walk — falsification, not just an exit code |
| **Review panel** (advisory) | **PASS** | `must_fix: []`, severity `med`, all four reviewers PASS, zero send-backs. Three produced falsification evidence |
| **Goal-check** | **FAIL → PASS** | 11 of 12 first pass. SC-10 was a real miss; after the fix, all seven re-graded criteria met |

## The one real miss, and why no test could have caught it

`SPEC.md:1721` still told readers *"reasoning lives in `docs/harness/DECISIONS.md`"* — a
present-tense claim in live instruction, naming a path the migration had already emptied. The
template that same sentence specifies had been corrected; the spec had not, so the two disagreed
from the moment the cluster landed.

**The depth sweep that exists to catch exactly this could not see it.** Its control is an exact
per-file table over `.claude`, `CLAUDE.md` and `.harness/expertise` — the moved docs are in none of
those three, so no clause ever examined `.harness/harness/docs/` for stale claims. It was green over
a class it does not reach. A reviewer reading an artifact is what found it, which is the control the
BRIEF itself flagged as carrying half this feature.

**That makes three checks in one feature that did not track what they claimed**: a check that could
not fail (its walk root had moved, so every absence assertion under it would have gone vacuously
green forever), a check that cannot pass on any tree (`plan.yaml:927` calls a script with no
argument; its usage gate exits 2 on empty argv — it survived ten plan revisions and four review
rounds because no probe ever executed it), and a signed verify that began failing on correct code
when a hygiene commit changed a word it greps for. Individually each is non-behavioural. Together
they say the verify clauses in this plan were not exercised as artifacts in their own right.

## The finding only the panel could make

**The docs grant is correct today and held there by nothing.** Three reviewers each proved a third
and none could state it alone: security reproduced `.harness/*/docs/**` granting write to five
reserved non-segment directories; qa proved no existing test can witness that, because the test
hardcodes its root; and code proved the one live assertion is membership rather than equality, so an
*extra* grantee passes anyway. **Fixing the hardcoded root alone would not close it** — a witness
needs both a repointable root and an exhaustive assertion. That requirement is invisible from inside
any single lens. The recommended remedy is the witness test, not narrowing the grant: the wildcard is
the signed spelling and narrowing breaks the moment a second repository onboards.

## Two errors of mine, corrected rather than absorbed

1. **I asserted the wrong task types.** My qa dispatch claimed all 11 tasks were `change_type: docs`,
   making the test-matrix floor empty, and built its whole framing on that risk. False: 7 docs,
   3 logic, 1 config — and logic mandates `unit`, so the floor held on its own. The validation lead
   caught it before dispatch. The outcome was unaffected; the reasoning was wrong.
2. **I cleared the simplify commit too narrowly.** I verified it changed no executable line and
   reported it hygiene-only. True about behaviour, and incomplete — I never checked whether a signed
   verify greps the *words* it changed. The panel found that one did.

**And a record correction.** One run's digest reads `VERDICT: FAIL` while `feature.json` recorded it
as `PASS`. I reconciled all 17 runs against their digests, found exactly that one mismatch, and
corrected it. **I did not retro-adjust the cycle count**: its basis mixes run-level failures with
in-run send-backs and cannot be reconstructed from disk, so guessing could force a spurious block.
The count may therefore understate. **Nothing in the harness reconciles digest verdicts against
`feature.json`** — that is how a failure sat recorded as a success.

## Recorded deviations — nothing here was quietly smoothed

- `POST-MOVE HEAD` records the literal `git rev-parse HEAD` (`1246b06`), not the cluster commit the
  plan's parenthetical named; a logs commit had landed on top, so naming the cluster commit would
  have described a tree the commands never ran against. A companion line names both.
- A commit cannot contain its own SHA, so the note's closing SHA line landed in its own follow-up
  commit rather than by amending.
- The close-out commit was amended once — before anything was pushed and before any SHA was
  reported — to replace a malformed trailer with the repository's own form.
- `harness_boundary.py`'s "two of the four" clause still contradicts the amendment's corrected figure
  of ONE. It was **not** fixed: it is an operator-ruled accepted residual, and the panel independently
  assessed and dismissed it. It left the blocking list by ruling, not by remedy.
- **SC-05 was carried by omission, and the fix touched its evidence file.** The staleness ruling
  named four criteria to carry and never mentioned SC-05, yet the fix deleted a fragment five lines
  above SC-05's cited evidence. It holds by *measurement* rather than by ruling: that script is in
  the integration array and the integration suite ran green at the pin, so SC-05's case re-executed
  inside SC-08's evidence. Flagged because "carried by omission" is how a criterion silently stops
  being checked.
- SC-09 is met on *assertion-executes* evidence, not a mutation proof — the write guard denied every
  scratch-copy mutation attempted. A named assertion proven to run is weaker than one proven to
  redden, and the next feature should not read it as the stronger thing.

## Close-out: distillation landed, two of its three records did not

**Ship-refresh was SKIPPED, and that is measured rather than assumed**: `.harness/codebase/` does
not exist, so the map mission has never run and there is nothing to refresh.

**Distillation ran for all three squads and the work is durable.** A spend limit killed two of the
three lead sessions mid-run, so `distill-product` has a digest without a verdict and
`distill-validator` has no digest at all. I did not take the survivors' word for what landed — I
checked the files:

- **No wipe.** Every one of the ten Expertise files *gained* entries, +25 net. A wipe is the failure
  mode distillation is most exposed to, because writing the file from new entries alone silently
  deletes every earlier one, and the format checker cannot see it.
- **No double-application.** Zero duplicate entry IDs across all thirteen files.
- **Format gate green.** `check-expertise.sh` exits 0 over the whole directory.

**I chose not to re-dispatch the two killed runs, and the reason is the risk direction.** Their
members had already self-applied their ops; a re-dispatch would re-adjudicate work already on disk
and risks double-applying entries into files that are injected into *every* future spawn. A missing
run record is a gap in the archive. A duplicated Expertise entry is a tax on every agent from now
on. I took the gap and am telling you about it rather than papering over it — the two runs are
recorded as `INCOMPLETE`, not as passes. **`INCOMPLETE` is a token I coined**, not an existing
one: the run-verdict field is a free-form string and nothing in the harness defines or routes on
it. Read it as deliberate rather than as drift — that ambiguity is B-10's gap again.

**One thing this cost.** The digest-skim yield — how many entries came from skimming run digests
versus from observation logs — was to be reported per squad, and DEC-145 cuts the skim if that
number stays near zero across features. Only the eng squad's report survives. This feature is
therefore a weaker data point for that decision than it should have been.

## Budget

**Cycles: 10 of 10 — fully consumed.** The last one bought the SC-10 fix, which closed four findings
in one commit. The re-grade was the back half of that cycle, not a new one.

**Runs: 23 against an informational budget of 20 — the session-entry check now emits its INV-22 note.** Stated because you
should see it, not as an apology. My read: the runs earned their place. Four failures, each resolved
by the run that followed it; a plan that converged over ten revisions before a single line was
built; and all four final gates found something real rather than rubber-stamping.

---

## Proposed backlog

Strike any row by ID. Anything not listed here dies silently, so this list is deliberately complete.

| ID | Finding | Nature |
|---|---|---|
| B-1 | Three checks that did not track what they claimed (could-not-fail, cannot-pass, verify falsified by a hygiene commit). A green panel on a small delta cannot distinguish a clean delta from a shallow probe set | chore |
| B-2 | The cluster was nearly split across two commits — a foreign pen swept staged renames. Caught by dry-run, repaired while nothing was pushed. Live hazard for any pen committing mid-build | chore |
| B-3 | `bash-write-guard` misparses redirects and heredoc bodies — a variable or a `->` in a quoted span reads as a redirect target. Hit twice by me this session | bug |
| B-4 | `plan.yaml` is untracked, so no revision of this plan could ever be diffed; three reviewers corroborated deltas by anchor-matching instead | chore |
| B-5 | `org.html` names `PLAN.md`, `STATE.md`, `DESIGN.md` as bare filenames — measured 5 occurrences. Stale, pre-existing, deliberately outside the cluster | chore |
| B-6 | The orchestrator playbook says to record `phase:` in `feature.json`; the schema sets `additionalProperties: false` and defines no `phase`. Instruction and enforcement disagree | bug |
| B-7 | `STATE.md`'s template says the activity stream is appended as each digest arrives, but `.harness/logs/` is outside the orchestrator's domain — measured, exit 2 | bug |
| B-8 | `audit-decisions.py` is live, untested, cwd-dependent, in no suite, and **reports 10 inconsistencies while exiting 0** — nothing can gate on it as written. Promote to `bin/` with a smoke test, or freeze it as archival | bug |
| B-9 | Sharper than B-8's count: 2 of those 10 are not dangling references but prose narrating a deletion. The real defect is that the index generator scrapes decision ids out of prose, so two index rows list a decision that does not exist in their `refs:` | bug |
| B-10 | Nothing reconciles digest verdicts against `feature.json`. A failed run sat recorded as passed until I checked all 17 by hand | bug |
| B-11 | The playbook's distillation clause is stale in both directions: it says reviewers are write-less and the orchestrator applies their ops. Measured — all five write their own file (exit 0), the orchestrator is denied (exit 2). Following it literally strands the ops | bug |
| B-12 | The docs grant is correct but pinned by nothing; a witness needs both a repointable root and an exhaustive assertion. Remedy is the witness test, not narrowing the grant | enhancement |
| B-13 | `plan.yaml:927` invokes `check-expertise.sh` with no argument, so that clause cannot pass on any tree. Signed text — **your call** whether to correct it | chore |
| B-14 | DEC-189 amendment 1 says the control-plane list is "advertised in deny messages". Measured false — it is a filter, never printed. The amendment copied the wording from a code comment that has since been corrected, leaving the signed text as the sole carrier. Signed text — **your call** | chore |
| B-15 | `harness-pm` holds no `notes/goalcheck-*.md` grant, so the goal-check flow's named artifact path is unwritable by its own author. Hit on two consecutive runs | bug |
| B-16 | A suspected concurrency-sensitive test: two reviewers independently saw transient failures neither could reproduce, in back-to-back subprocess-heavy suite runs | bug |
| B-17 | Nothing reserves a run id and `Write` does not warn on clobber — two leads collided and one overwrote an in-flight `state.yaml` | bug |
| B-18 | An agent with subagents in flight cannot idle-wait; ending a turn trips the digest validator | bug |
| B-19 | `validate-digest.py:745` validates any artifact path ending `digest.md` against the full lead schema | bug |
| B-20 | The simplify pass weakened a failure *message*: it no longer reports the walked-file count that distinguishes an empty walk from a wrong one, on the very test whose vacuous-green history is this feature's headline finding. Assertion unaffected | chore |
| B-21 | `layout_migration.py:34` carries two stale tenses — a fix described as pending and a rewrite described as future. Ruled a knowing survivor, outside SC-10's text. Worth correcting whenever that file is next opened | chore |
| B-22 | A second amendment-span gate in any future plan is the crystallization trigger for a shared decision-span checker | enhancement |
| B-23 | The partition rule is restated in several task intents; the BRIEF section is the authority and the copies should re-derive | chore |
| B-24 | The control-plane-redundancy mechanism is spelled in full twice; one of the two is the authority | chore |

**Not proof that the segment machinery generalises.** Nothing in the tree stages two repository
segments. This feature is evidence the machinery works for the one declared segment, and no more —
the panel and qa both said so independently, and the BRIEF said it first.
