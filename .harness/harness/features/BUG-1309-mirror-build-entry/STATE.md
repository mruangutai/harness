# STATE

## Current

- feature: BUG-1309-mirror-build-entry
- run: c19 validate — `runs/c19copy-validator/` (validator lead: qa + three-reader panel) and
  `runs/2026-09-09-01-product/` (product lead, pm goal-check). **Both PASS, zero send-backs, zero
  must_fix.** The authorized c19 copy cycle is now COMPLETE except for the operator's own hand test.
- what was validated: commit **`4857818b`** — the merge-gate refusal copy, 2 files / 3 hunks / +5 −3.
  `merge-gate.py:192` carries the operator's chosen sentence; `test-merge-gate.py:64-65` and
  `:99-102` re-anchored. No case name changed. **No source or test file was touched by any agent in
  this run** — the D-11 carve-out held, verified by `git status --porcelain` showing zero drift on
  `merge-gate.py`, `merge-gate.sh` and `tests/integration/test-merge-gate.py`.
- `review_sha`: **re-pinned to `4857818bb1408813c7a38311d9e4ffc20373427e`** before either validator
  saw the change (INV-6, P-02). The previous pin `9fe5cf31` predated the copy and is superseded.
- station: **review** (`plan.yaml` `status:`, unchanged), T-05 `done` (unchanged). `approval:` and
  `BRIEF.md` are byte-unchanged — pm CONFIRMED R-7 §3: no criterion text moves, **no re-signature
  is owed**.
- budget: **`cycles_used` 17 of `max_total_cycles` 17 — UNCHANGED by this run.** Both leads reported
  zero send-backs, and a clean first-pass run adds zero cycles (DEC-157). The 17th cycle is the one
  the operator authorized for this copy change; this validation is its remainder, not an extra
  cycle. `len(runs)` 55 of `max_total_runs` 20 — INFORMATIONAL (INV-22); the runs still earn their
  place, this one closing a copy change with four independent readers and no rework.
- mirror: unchanged — parent #1407 and nine sub-issues already at review. No station moved, so no
  `gh-sync.py` write was owed.

### Evidence, measured at the pin rather than taken from a digest

- **Integration suite:** `tests/integration/test-merge-gate.py` → rc=0, **36 ok, 0 FAIL,
  `ALL PASSED`**, matching the c18 baseline (`notes/qa-c18.md` §1). Run by the orchestrator and
  independently by qa and the code reviewer.
- **The real message**, rendered by invoking the real `merge-gate.sh` against a
  `build_entry=recovery-required` fixture — not read off the source:
  `merge-gate: FEAT-9001-uat-scratch needs its GitHub mirror recovery completed before this merge
  can continue. Run: python3 .claude/skills/harness/bin/gh-sync.py open <abs-feature-dir>`
- **Discrimination probe** (orchestrator, on a scratch copy at `/tmp`; the tracked file was never
  mutated and the scratch baseline reproduced 36/36 first): dropping `{command_line}` reddens two
  cases; dropping the sentence reddens the re-anchored `T-05 recovery-required denies`. **Dropping
  `{feat}` reddens NOTHING** — see Q9. qa reproduced the sentence half on its own pinned scratch
  worktree (3 cases redden).
- **T-05's own `verify:`** end to end → `VERIFY-PASS`, `code_grade` 4 against a floor of ≥4.
- **All 26 byte-frozen case names** T-05 greps for resolve individually (qa checked each, not by
  file-global grep): 25 exact, 1 a prefix match that `grep -qF` satisfies.
- **Jargon sweep** (orchestrator, independent of the reviewers): the rejected phrases
  `records github.build_entry=` and `no Build entry receipt exists` survive at `merge-gate.py:188`
  (out of scope, Q10), `post-merge-sweep.sh:230-231` (different script, own message), and
  `plan.yaml:1273-1274` — the historical specification D-19 names SUPERSEDED, correctly left intact
  per PRINCIPLES rule 15. **The target deny at `:192` is clean.**
- **UAT:** already exact. pm compared Step 3's quoted block (`:161-163`) and Step 3b's observe line
  (`:211-214`) against the rendered string character by character — **no edit was owed and none was
  made.** Step 7 (`:303`, `recover-terminal … --yes` / not-`open`) stays true and untouched.

### Next, in order

1. **SC-10, the operator's hand test — the ONLY thing standing between this feature and a ship
   decision.** `notes/uat-BUG-1309-mirror-build-entry.md`, Steps 1–2 then Step 3 (`:152-157`).
   PASS condition, quoted from the note (`:175-177`): the message names the feature, says what is
   wrong, and gives a command runnable without opening any source file. Nobody but the operator can
   close a `verify: uat` criterion — it is not met, not waived, not partial.
2. Then the rewritten CEO briefing, then the ship decision. The stale briefing at
   `notes/ship-review-2026-09-08-resume.md` and its B-1..B-13 backlog still await disposition, now
   joined by Q9 and Q10 below.

## Open Questions

- Q1 (resolved, 2026-09-08) — SC-04's two evidence gaps: **operator accepted both** on
  inspected-correct source (`notes/research-BUG-1309-c18-sc04-ruling.md`). SC-04 reads MET by
  ruling, NOT by new automated evidence, and c19 does not regress it (pm, §1). The two backlog
  remedies it names remain unscheduled.
- Q2 (resolved by delivery, 2026-09-09) — the `merge-gate: ` prefix was RETAINED in the new copy and
  the ui reviewer confirmed every sibling message still shares that voice. Nothing depends on
  striking it.
- Q3 (non-blocking, UAT coverage) — the UAT has no step exercising the duplicate-claimant ambiguity
  scenario at all. Pre-existing.
- Q4 (non-blocking, harness defect, 5th and 6th sighting) — an agent returned a complete, well-formed
  fenced digest while the host recorded `failed (exit 1) — subagent called yield with null data`.
- Q5 (non-blocking, harness defect) — `bash-write-guard.sh` blocked `cp` and shell redirection for a
  read-only role but did not block `python3 -c "open(path,'w')"` run through bash.
- Q6 (non-blocking, backlog) — T-05's `verify:` grade assertion takes `min(grade)` over
  `git_merge`/`words`/`direct_merge`/`gh_merge` and never names `option_end`, `first_subcommand` or
  `merge_target`. Satisfied in fact (5/5/4); the remedy edits approval-gated `plan.yaml`.
- Q7 (non-blocking, backlog) — `merge_target` matches `--abort`/`--continue`/`--quit` by exact token
  equality while git accepts unambiguous abbreviation, so `git merge --abo` would be DENIED.
  Direction is over-deny, never a bypass.
- Q8 (non-blocking, plan hygiene, pre-existing) — T-05's enumerated case-name contract lists 21 names
  while `verify:` gates 26; the five D-13/D-14 names never reached the enumeration.
- **Q9 (non-blocking, backlog, NEW 2026-09-09)** — no test can see the loss of the explicit feature
  name. `{command_line}` embeds `realpath(feat_dir)`, whose basename IS the feature id, so
  `"FEAT-9001-fixture-non-era" in reason` (`test-merge-gate.py:69`, `:102`) stays true with `{feat}`
  deleted. **Behaviour is correct at the pin** — the name appears twice in the real message — but
  the evidence for "names the feature" is incidental. Found by the orchestrator's probe, concurred
  independently by qa, the code reviewer and pm at the predicate text. `:69` is pre-existing; `:102`
  was added by this commit's re-anchor and is carried by its discriminating `gh-sync.py open`
  conjunct. Remedy shape: assert on the region BEFORE `Run:`. Needs a cycle licensed to edit the
  D-11 carved-out test file.
- **Q10 (non-blocking, backlog, NEW 2026-09-09, med)** — `merge-gate.py:188`, the repo-unpinned
  deny, still opens `{feat} records github.build_entry={value}` — **the exact jargon phrase the
  operator rejected for `:192` in this same cycle** — and splices a bare `(D-09)` into
  operator-facing prose. Before c19 all four deny paths shared one voice; `:192` now reads like a
  more careful author than its sibling. Untouched by this delta and explicitly scoped out by ruling
  R-7 §1/§3. Raised by the ui reviewer (F-01).
- **Q11 (non-blocking, low, NEW 2026-09-09)** — `merge-gate.py:180` leaks the raw Python constant
  name `feature_schema.BUILD_ENTRY_ERA_EXEMPT` into operator-facing stderr. Pre-existing, allow path
  not deny path (ui reviewer F-02).
- **Q12 (record honesty, NEW 2026-09-09)** — **test-first order for `4857818b` CANNOT be established
  from the repository record**, and qa reported it as such rather than assuming either way: source
  and both test hunks landed in one commit, with no intermediate red commit. The pre-edit red
  observation was reported by the main session and is credible; it is simply not corroborated by
  the tree. Recorded per PRINCIPLES rule 15 — not restated as verified.
- **Q13 (documentation, NEW 2026-09-09, trivial)** — `notes/rulings-2026-09-08-c19-copy.md` §5.3
  cites the `recover-terminal … --yes` / not-`open` expectation as "Step 6 (`:300`)"; it is in fact
  Step 7 at `:303` (`## Step 6` at `:258` is the now-allowed merge). Stale anchor in the ruling
  note, not in the UAT. The expectation itself is correct and untouched.
- **SC-10 UAT is still NOT executed and still blocks the ship.** It is the last open item.
