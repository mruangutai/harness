# STATE

## Current

- feature: BUG-442-docs-grant-witness-test
- run: 2026-09-07-05-validator (qa segment) — PASS, 0 send-backs
- squad: validator (qa segment closed)
- status: building
- last commit: T-01 committed at `f9f2d392`; the qa segment's record commit follows it
- cycles_used: 1 (unchanged — a clean first-pass run adds ZERO cycles, DEC-157)
- runs: 6 of max_total_runs 20 — informational, nothing to surface

BUILD phase, resumed after the previous dispatch died mid-flight at ~14 min with T-01's work
on disk but unverified and uncommitted. Two things happened this run.

**T-01 verified and committed (`f9f2d392`).** The prior attempt's artifacts were treated as
CLAIMS, not results, and re-measured here before the pen was used (O-02): the task's own
three-clause `verify:` chain re-run verbatim from the worktree root exits 0 with both new
tests printing `ok`; `git diff` is 182 insertions and 0 DELETIONS, so the additive-only
constraint and the byte-identity of `SHARED_MANIFEST_PATHS` / `COLLECT_FIXTURE` hold by
construction rather than by assertion; `.harness/team-config.yaml` and `harness_yaml.py` are
untouched. The negative control was probed for the one defect its own design names — running
the file with a forged `BUG442_MUTANT_CHILD=/definitely/not/this/run` produces a LOUD
`FAIL` at exit 1, not a silent skip, so the recursion guard cannot swallow the ladder (P-15:
a green gate is only evidence once it is shown it can report red). T-01: building -> review at
the commit, then -> done once the gate passed. Both stations written with
`plan-merge.py set-task-station`, never by hand.

**qa segment PASS.** `harness-validator-lead` routed it to `harness-qa`; the blocking
`qa_gate` is satisfied at `f9f2d392`. `integration` is the required kind and is green (exit 0,
0 `FAIL` lines, 24 `ok`); `unit` was run unobligated and is green and says nothing about a
test-only diff. All of SC-01..SC-07 graded PASS. The test-first audit was graded on the
BRIEF's own recorded terms — RED-first is unobtainable because the grant is CORRECT today, so
the three permanent mutants are the RED evidence — and qa did the one thing that makes that
verdict worth anything: it reproduced M1 OUTSIDE the graded file, against a scratch
`HARNESS_PROJECT_DIR`, and saw exit 1 with the witness's own `FAIL` line beside the
anti-false-red control's `ok`. The PASS stands on that, not on the ladder asserting about
itself. Digest: `runs/2026-09-07-05-validator/digest.md`; note:
`notes/qa-2026-09-07-05-validator.md`.

Three residuals from qa, none gating, carried forward for SIMPLIFY and the panel:
- M2 and M3 rest on the in-file assertions plus source review; only M1 was reproduced
  out-of-file. If cheap, an out-of-file M2 would close the strongest remaining doubt.
- The witness filters `mine` only, so a docs grant arriving via the SHARED list is outside its
  lens. Not a gap today: `SHARED_MANIFEST_PATHS` carries no path with a `docs` segment and the
  pre-existing equivalence test would redden if it gained one.
- The BRIEF's signed residual is unclosed BY DESIGN: census walk and grant lookup use the same
  loader, so a parser bug hiding a newly ADDED persona hides it from both. The literal census
  closes the deletion half only.

**Next, in order, and NOT started here** (this dispatch was bounded to verify+commit+one
segment, and stopped at the segment boundary — DEC-148/159 make ending at a clean checkpoint
normal): SIMPLIFY, sequenced to `harness-eng-lead` with an explicit instruction to read
`.agents/skills/harness-simplify/SKILL.md` first, re-running the suites after any apply and
BEFORE anything is pinned; THEN pin `review_sha` and run `gh-sync.py status <feature-dir>
review` (lowercase station); THEN the validator panel. An apply commit after the pin moves the
tip and invalidates the panel's verdict, which is the whole reason SIMPLIFY precedes the pin.
Ship is NOT ours: the main session runs it.

Working memory lives here, in `## Current`, deliberately. `notes/handoff-<phase>.md` cannot be
written from a feature worktree for a feature not yet on the default branch — check-domain's
handoff shape gate resolves `Authority:` pointers against the MAIN checkout root, not this
worktree. Already diagnosed, raised as a defect below, NOT re-diagnosed.

Panel finding `PF-049c59c515c538bc41da6616176f8987` (info, the hand-pinned census) stays
`open` as a deliberate non-action per the plan and per the dispatch. No ruling is needed for an
info-severity finding.

Log — station transitions:
- 2026-09-07: backlog -> plan. Feature dir instantiated; BRIEF.md and plan.yaml drafted;
  panel run at cycle 0; handoff written to notes/handoff-plan.md. Awaiting signature.
- 2026-09-07: plan -> building. Operator signature landed on both artifacts; T-01 moved
  ready -> building; eng segment dispatched to harness-eng-lead with the `build` team.
- 2026-09-07: T-01 building -> review (built, verified, committed at f9f2d392), then
  review -> done (blocking qa gate PASS at that commit). Feature station stays `building`
  until SIMPLIFY and the pin.

## Open Questions

- Harness defect, non-blocking, for the harness owner. Guards resolve a relative path
  against the MAIN checkout instead of the caller's worktree, so worktree-based flows —
  which is how the harness actually runs every feature — hit false denials. Three
  independent sightings: (1) `handoff_done_when.py:359-364` matches FEATURE_RE against a
  worktree-relative `rel_path` then joins it to the main root, so `plan-task:` and
  `brief-sc:` authority pointers CANNOT resolve from a worktree; worked around by using the
  explicit-path `approval:` form. (2) `bash-write-guard.sh` rejected a `rm` issued with a
  relative path from inside the worktree, naming the main-checkout path as the target;
  the identical command with an absolute worktree path was allowed. (3) The same root cause
  makes `notes/handoff-<phase>.md` unwritable from a worktree for a feature not yet on the
  default branch, so build-phase working memory is kept in this `## Current` instead.
- Harness defect, non-blocking, raised by harness-validator-lead. `check-domain.sh:1312-1318`
  permits correcting a recorded run digest only by APPENDING, but `validate-digest.py`'s
  `parse_digest` binds the FIRST `DIGEST:` block and stops at the first dedent. The permitted
  route and the enforced contract therefore do not intersect: no contract defect inside a
  recorded digest can be repaired by any governed agent.
- Harness defect, non-blocking, raised by harness-backend-dev in its T-01 receipt. At dispatch
  time this worktree's `.harness/.inflight-claims.json` held only the eng-lead's claim and no
  claim for the dispatched member, so `check-domain` refused the member's first edit citing
  claims held by concurrent sibling runs; the member had to register its own claim through
  `inflight_registry.claim_with_receipt` before it could write. Claim registration should
  complete before a dispatched member's first write rather than being a gap the member closes
  itself.
