# STATE

## Current

- feature: FEAT-30-worktree-per-feature · phase **validate, COMPLETE and FAILED** on one high ·
  status Review / awaiting_user. Phase recorded here; the shape gate denies a `phase` key.
- cycles_used: **7 of 13**, six remaining. All five validate segments reported ZERO send-backs, so
  this phase added none. Runs 12 of 20, informational and a floor (the operator's five
  main-session-direct tasks are not runs).
- review_sha: **`a76d69a`**, pinned and committed. Branch tip is one commit past it and changes only
  that value. **I ran the qa segment BEFORE pinning, contrary to INV-6** — `check-state.sh` caught it.
  No harm: the dispatch carried the explicit range and qa's numbers match mine. Ordering was wrong.
- All ten tasks read `status: done`. Both approvals `approved` (`BRIEF.md:275-279`, `plan.yaml:4-5`).
- **Briefing: `notes/ship-review-2026-08-21-04-validator.md`** (+ rendered `.html`).

**VERDICT: FAIL — do not ship.** One high, verified by me independently, INTRODUCED BY THIS DIFF.

**F-1 (high, gates, must_fix).** `bash-write-guard.sh:617-618` `if not findings: sys.exit(0)` runs
BEFORE the reviewer read-only denial (`:628`) and the domain walk (`:640+`). `python3
.../expertise-merge.py apply --file <any path>` matches no write pattern, so `findings` is empty and
the guard exits 0. `cmd_apply` validates neither caller nor `--file`. T-06 built the tool; **T-07, in
this same diff, rewired `harness-distill/SKILL.md:28-34` to instruct every agent — reviewers included
— to use exactly that shape.** Reproduced live: `harness-documentor` → another agent's Expertise file,
→ `src/main.py`, `harness-code-reviewer` (read-only) → `src/main.py`, reviewer → `.claude/settings.json`,
reviewer → outside the repo, documentor → `check-domain.sh`: **all rc=0**, while the same targets via
`echo >` are rc=2. Against a COPY of `check-domain.sh`: exit 0, **67,976 → 71 bytes**. Real files
verified intact. Content is constrained to the Expertise markdown shape, so it is a clean tampering
primitive for Expertise (injected into every spawn — doctrine injection) and a blunt truncation
primitive elsewhere; blunt still disables enforcement.

**Root cause is architectural: the guard is ALLOW-BY-OMISSION.** Options: (a) invert the default for
first-party write tools [enforcement, operator]; (b) each tool self-validates identity and destination
[**squad-appliable**, the immediate close F-1 asks for]; (c) a running post-write audit [operator].
**I did NOT dispatch (b)** — it is one of three options the operator is being asked to choose between,
and applying it unreviewed would move the pin and invalidate the panel verdict on the other 15 files.
One cycle closes it on their word.

**Goal MET.** pm verified all 12 criteria by their own declared methods: 11 `met`, **SC-01
`met-with-caveat`** (its "two for harness" half runs against a stand-in; pm's argument comes from the
criterion's own text and it flagged that it cannot know if that is what was signed).

**Segments:** qa PASS (`matrix_ok` per task, all ten) · simplify PASS, **empty apply set**, nothing
touched the enforcement layer · docs PASS (`SPEC.md` +120/-9; both tools were documented nowhere) ·
panel **FAIL** · goal-check PASS. Suites at the pin, my measurement, three runs each: unit exit 0,
integration exit 0, zero FAIL.

**Weakest point: the feature has never governed a live flow; every proof is a fixture proof.** Two
checkouts exist — the MAIN one (where FEAT-30 was built) and `.claude/worktrees/FEAT-31`, legacy
ONE-segment. The two-level `<repo>/<id>` layout has **zero live instances**. Softening it: governance
inside FEAT-31 is unregressed (same personas as root, both directions), and a path under a
non-existent worktree resolves NOBODY — fail-CLOSED, since resolution reads the git pointer.

**SC-01b, the headline claim, PASSES when run** — exit 0, 14 assertions, four real worktrees, two per
repository via a real `fleet.yaml` (second repo default branch `master`), barrier-synchronised
committers, six pairwise overlaps asserted, no outside branch advancing; seen green five times. **Its
predicate is proven able to redden:** 5 trials against a shared checkout, 4/4 committers succeeding
each time, `IsolationViolation` raised all 5, so the `committer_failed` short-circuit never fired.

**Four relayed claims failed my re-measurement** (detail in the briefing): the simplify pass's only
HIGH (F-ALT-1) is refuted — flipping the three switches reddens their suites 4/13/12; the docs pass's
headline is overstated — `harness-team/SKILL.md:94` correctly names `check-domain.sh` and
`harness-zero-micro-management` makes no such claim; **T-03's recorded red proof is inert at HEAD** —
its mutation leaves 38/38 parity cases green, and the panel showed `WORKTREES_SEGMENT` has no use at
all in the grant re-basing path, so it *cannot* redden one; and my own inference about
`test-expertise-merge.py` was wrong twice — it DOES share the crash structure (`:253-276`) and escapes
only by subprocess isolation. The operator's own build narration held on 4 of 5 claims (T-05's proof
is exact: 10 FAILs, all new refuse cases; T-04's counts hold; D-09's cost is asserted both ways).

## Open Questions

- **Q1, BLOCKING, OPERATOR DECISION.** The allow-by-omission choice: (a), (b) or (c) above. (b) is
  squad-appliable; (a) and (c) are enforcement-layer and theirs.
- **Q2, effectively blocking.** SC-01's stand-in reading — if the operator disagrees with pm, SC-01 is
  unmet and that is a re-plan, not a build defect. Never mine to mark.
- **Q3.** T-05's signed intent (`plan.yaml:944-947`) requires refusing "a shell composition that hides
  the subcommand". **Unimplemented**, and none of its eleven cases covers it; the same clause calls the
  guard a casual-shape filter at `:946`, contradicting itself. I verified the gap: `checkout`,
  `reset --hard`, `rebase` and `git -C … checkout` are blocked for every persona including the
  orchestrator, but `python3 -c "…git checkout…"`, a heredoc equivalent, and `g=git; $g checkout main`
  are allowed. **Implement or STRIKE per DEC-188**; nothing detects a falsified signed requirement.
- **Q4, OPERATOR, outward-facing.** Mirror unsynced: 11 INV-26 rows — sub-issues #616-#625 OPEN against
  a plan reading `done`, parent #572 at `Building` where the plan derives `Review`. Ordering is already
  satisfied; remedy is ten `gh-sync.py close-task` runs. **My attempt was denied by the permission
  classifier** — a correct denial, not to be worked around.
- **Q5, OPERATOR, DEC-174.** Two high findings inside the blocking gate: `unit.detect`'s glob claims all
  32 `bin/` scripts while `--kind unit` runs 18, so the unit leg **cannot fail** (eight of ten
  `matrix_ok` verdicts rest on it); `integration.detect` names 6 where the runner runs 14, so this diff
  MOVED B-1 rather than fixing it. Why nobody caught it: none of the five test files this diff touches
  is in `UNIT_SCRIPTS`, so the feature exercised the unit leg zero times. Fix the consistency check first.
- **Q6.** `SPEC.md:2239` says per-team serialization suffices "because the teams are operating on
  different checkouts", while the carve-out at `bash-write-guard.sh:687` blanket-allows any governed
  agent to write into any worktree on the Bash route. DEC-143 and DEC-153 answer differently and each
  route implements one answer. Intended? Inside #626's scope?
- **Q7.** Is there any *running* post-run audit of HEAD position, versus the one-shot manual DEC-153
  audit? If not the HEAD-move residual is uncompensated, unlike the write-side one.
- **Two escape hypotheses remain structural, not demonstrated**, because the panel is read-only: a
  symlink escape from the carve-out, and a nested-`.git` candidate. Each needs a probe, not a reviewer.
- **The gate's headline numbers are not a coherent unit.** "213 integration" counts `^PASS ` lines, of
  which only 16 are per-script summaries; the suite emits **738** further case results as `ok ` plus 19
  section summaries. Sound as a comparative regression signal — which is how SC-09 uses it, and pm's
  `comm -23` on line identities is sounder — but not a test count. I had repeated it before checking.
- **Backlog B-1..B-18 is enumerated in the briefing** with an ID column. Unstruck rows become issues on
  ship acceptance; anything unlisted dies silently. B-1/B-2 are the gate defects above; B-8 is that
  `remove` has no cwd guard and no test for one, which is the exact self-deletion hazard that makes
  removal the main session's act.
- Attribution corrected by the panel: the internally contradictory signed intent is **T-04's**
  (`plan.yaml:736-739` vs `:861-863`), not T-05's. Q21's recorded subject is **T-10, not T-04**. My qa
  dispatch's T-04 premise was inverted — the leg lacking execution evidence is unit, not integration.
- Issue **#626** is filed, unblocked and OUT OF SCOPE here; it may be one entry short (`DECISIONS-INDEX.md:114`,
  DEC-95). `check-state.sh`'s other rows are FEAT-26/28/29; the count is a shared mutable global, so
  scope by name never count. Ship-refresh is a legitimate SKIP: no `INDEX.md` map exists in this repo.
