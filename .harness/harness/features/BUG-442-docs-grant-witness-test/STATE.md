# STATE

## Current

- feature: BUG-442-docs-grant-witness-test
- run: 2026-09-07-02-eng (SIMPLIFY segment) — PASS, 1 send-back
- squad: eng (SIMPLIFY closed)
- status: review (feature station written with `plan-merge.py set-feature-station`)
- last commit: SIMPLIFY apply + records; `review_sha` pinned at that commit
- cycles_used: 2 (was 1; +1 for the send-back the lead reported from inside the run, DEC-157)
- runs: 7 of max_total_runs 20 — informational, nothing to surface

BUILD phase closed and the Building -> Review seam crossed. One segment ran this dispatch.

**SIMPLIFY PASS, one fix applied.** Four angles as four separate read-only spawns, no angle
collapsed and none read by the lead. Two seats, recorded because an unattributed pick is
unreviewable: `harness-backend-dev` owns `tests/integration/**` by the plan's own lane
(resolved_at 6d969ed3) and took REUSE + SIMPLIFICATION and the apply; `harness-dev-ops` is the
adjacent gates/test-infra seat and took EFFICIENCY + ALTITUDE. Findings, costs, alternatives and
every skip-with-reason: `runs/2026-09-07-02-eng/digest.md`.

The one apply is ALTITUDE F1 at `tests/integration/test-harness-yaml.py:373` — the anti-false-red
control's failure message pinned `test-harness-yaml.py:892-904` for `main()`'s per-test
try/except, but `main()` is at 1074 and 892-904 holds an unrelated test. T-01 inserted 182 lines
above that point, so the pin was never true post-commit and a reader diagnosing a real failure
would land on the wrong code. Replaced with a content anchor, not a new number. **The asserted
expression is byte-identical** — only text inside an f-string message moved, so no assertion was
deleted or weakened and the one-fix ceiling is spent. Verified here on disk, not taken from the
digest: `git diff` is exactly that one line.

EFFICIENCY returned EMPTY and measured rather than guessed (0.74s whole file, 0.653s the witness,
four subprocess re-entries inside D-03's protected mechanism; nothing invokes this file at
session entry, on write or from a hook). An empty angle is a real outcome, recorded as one.
Nothing settled was re-litigated: no persona enumerator (D-01), no `COLLECT_FIXTURE` rewrite
(D-02), no trimming of the `BUG442_MUTANT_CHILD` mechanism (D-03).

**Suites re-verified at my own tier after the apply**, not accepted from the digest (DEC-204):
T-01's three-clause `verify:` chain exits 0 with 24 `ok` and 0 `FAIL`; the unit runner
`.claude/skills/harness/bin/run-unit-tests.sh` exits 0 with 0 `^FAIL ` lines over 2829 `ok`,
counted rather than tail-read (P-01). Both with `env -u HARNESS_AGENT_TYPE`.

**Seam mechanics, in this order and for this reason.** The station write and the code sit in ONE
commit and only `feature.json` changes after it, because INV-33 compares the pinned commit's
`plan.yaml` BYTES against the plan on disk — a station written after the pin makes the pin stale
by that comparison. So: commit A carries the apply, the receipt, STATE.md, the run record and
`plan.yaml status: review`; `review_sha` pins at A; commit B writes only that pin. A contains
every reviewed byte, and the plan bytes at A equal the plan on disk (P-02).

**Q1 from the lead is answered at rung 1 and is NOT pm's.** It flagged that the unit runner named
in its dispatch, `tests/run-unit-tests.sh`, does not exist here. Correct — but that literal was
MY dispatch's invention, not the plan's. `plan.yaml`'s T-01 `verify:` (lines 81-84) names only
the three `python3 tests/integration/test-harness-yaml.py` clauses and no runner at all. T-01's
gate is runnable exactly as written; nothing for pm to correct.

qa's three residuals are unchanged, non-gating, and SIMPLIFY correctly declined to touch them
(only M1 reproduced out-of-file; the `mine`-only lens, not a gap today since
`SHARED_MANIFEST_PATHS` carries no `docs` path and the equivalence test would redden if it
gained one; the signed shared-loader residual, closed on the deletion half only). Those, plus
SIMPLIFY's three skipped findings (ALT-F2, REU-F1, SIM-F1), are the briefing-row candidates for
the ship review — each with its reason in the eng digest, none gating.

Panel finding `PF-049c59c515c538bc41da6616176f8987` (info, the hand-pinned census) stays `open`
as a deliberate non-action per the plan. No ruling is needed for an info-severity finding.

**Next, and NOT started here** (bounded to SIMPLIFY + the seam): the validator panel at the
pinned `review_sha`, entering validate. `gh-sync.py status <feature-dir> review` runs at the
seam, before the panel is dispatched. Ship is NOT ours: the main session runs it.

Working memory lives here, in `## Current`, deliberately. `notes/handoff-<phase>.md` cannot be
written from a feature worktree for a feature not yet on the default branch — check-domain's
handoff shape gate resolves `Authority:` pointers against the MAIN checkout root, not this
worktree. Already diagnosed, raised as a defect below, NOT re-diagnosed.

Log — station transitions:
- 2026-09-07: backlog -> plan. Feature dir instantiated; BRIEF.md and plan.yaml drafted;
  panel run at cycle 0; handoff written to notes/handoff-plan.md. Awaiting signature.
- 2026-09-07: plan -> building. Operator signature landed on both artifacts; T-01 moved
  ready -> building; eng segment dispatched to harness-eng-lead with the `build` team.
- 2026-09-07: T-01 building -> review (built, verified, committed at f9f2d392), then
  review -> done (blocking qa gate PASS at that commit).
- 2026-09-07: building -> review. SIMPLIFY closed with one apply and both suites green; the
  station crossed the seam in the same commit as the apply, and `review_sha` pinned.

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
  complete before a dispatched member's first write rather than being a gap the member closes.
- Harness defect, non-blocking, disclosed by harness-eng-lead against ITSELF in the SIMPLIFY
  run. The lead seeded this segment's checkpoint into `runs/2026-09-07-01-eng/state.yaml`,
  which already belonged to the earlier BUILD segment, overwriting it. `check-domain` REFUSED
  the follow-on `digest.md` write at that path but PERMITTED the `state.yaml` one, so the
  protection is asymmetric across two files of the same run. Should `state.yaml` be protected
  from cross-run replacement the way `digest.md` already is?
- Harness defect, non-blocking, paired with the above, raised by harness-dev-ops. The whole
  `.harness/*/features/*/runs/**` tree is gitignored (`.gitignore:7`), so a clobbered run
  checkpoint has NO recovery path: `git ls-files --error-unmatch` exits 1 and `git show
  HEAD:<path>` reports the path exists on disk but not in HEAD. A restore errand returned
  BLOCKED having restored nothing. The class has no recovery, though damage here is bounded.
