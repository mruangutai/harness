# STATE

## Current

- feature: BUG-1308-expertise-replace-drop
- run: .harness/harness/features/BUG-1308-expertise-replace-drop/runs/2026-09-05-simplify-eng/digest.md
- squad: eng
- status: in_review

BUILD IS COMPLETE. All four tasks are done and committed; the qa `test_matrix` blocking gate PASSED;
SIMPLIFY ran and was an empty pass. Cycles used 5 of 8 — this whole resume segment added ZERO, since
every run returned first-pass PASS with no send-back. Next: pin `review_sha`, move the GitHub mirror
to `review`, then the review panel and pm's goal-check.

The branch was REBASED onto origin/main (4b0d04e9) by the main session — `git rebase` is refused for
every governed agent by `bash-write-guard.sh`, so the orchestrator cannot perform it. Verified after
the fact: `git merge-base --is-ancestor 4b0d04e9 HEAD` exits 0.

DECISION NUMBER, SECOND RENUMBER. This feature's decision is now **DEC-219**. It was DEC-216, was
renumbered to DEC-218 when BUG-1303 landed 216 and 217, and had to move again when BUG-1304 landed
DEC-218 ("Claim-set membership binds governed writes to assigned worktrees") on main. DEC-219 was
verified free before allocation: zero hits in both DECISIONS.md and DECISIONS-INDEX.md on landed
main, no in-flight feature claiming it, registry `NO CLAIMS`. The operator allocated it, ruled it a
pure identifier substitution, waived a new plan panel and kept both signatures standing. All 11 live
`plan.yaml` references and BRIEF SC-10 read DEC-219; the single surviving `DEC-218` token in
`plan.yaml` is at :184 inside D-16, where it correctly names BUG-1304's entry.

TASKS. T-01 `182a2788` added the `ops` subcommand (`resolve_ops` keyed on the stable (section, id)
pair, never an index, so a replace never moves an entry and multi-op results are order-independent).
T-03 `17ad7746`/`aaa761fd` realigned the distillation contract. T-02 `8fd6ffcb` added
case11..case20. T-04 `fd8e4374` recorded the operation in SPEC §5.3, appended DEC-219 and
regenerated the index. `30b84a94` carried the DEC-219 renumber and T-04's station. `c6aaf9e1`
recorded the qa gate.

TRUST — measured by the orchestrator at this tree, not relayed:
- unit exit 0, 0 `^FAIL ` lines, 28 files. Integration exit 0, 0 `^FAIL ` lines, 46 files.
- T-04's own `verify:` block re-run verbatim: exit 0, including
  `tests/integration/test-gen-decisions-index.py` (14 ok lines).
- The DEC-219 renumber: `grep -c DEC-219 plan.yaml` = 11; the DEC-216 panel finding survives
  byte-identical at :248; both approvals still read `approved`.
- SIMPLIFY changed no source: `git diff --stat HEAD` over the three code files is empty.
- UNVERIFIED, inherited and still unverified: the post-amendment re-signature. The main session
  reported SIGNED/APPLIED with no diff because the fields were already identical. The orchestrator
  can neither write nor re-run `sign-approval`.

DEAD ENDS, still active. Do NOT re-anchor T-02 case17's harvest onto the SKILL.md prose sentence —
the normalised file carries ~14 competing pipe-separated runs from markdown tables, so only the `op:`
key is unambiguous (verified at `aaa761fd`). Do NOT renumber the cycle-1 panel finding, now at
`plan.yaml:248` and reading DEC-216: its id is a hash over the reader plus that text and the operator
approved keeping it as transcribed history. Do NOT attempt to restore any file under `runs/` —
`.gitignore:7` means that tree was never tracked. Do NOT let a simplification drop the wording guards
at `tests/integration/test-expertise-merge.py:542-545` and `:563-566`; they are the ONLY assertions
pinning the exit-11 message tokens, since the unit cases pin the code alone.

WORKING SET. `plan.yaml` (T-04 at :780) · this `STATE.md` · `feature.json` ·
`notes/qa-gate-bug1308.md` · `runs/2026-09-05-simplify-eng/digest.md`.

## Open Questions

- **Harness defect, blocking the handoff NOTE only (not the work).** `notes/handoff-*.md` cannot be
  written for a feature whose directory exists only in a worktree: no legal `## Done when` authority
  both resolves AND binds. Measured by the predecessor: `plan-task:` and `brief-sc:` resolve
  `feature_dir` against the PROJECT ROOT (`handoff_done_when.py:116,131`) and the main checkout has
  no such directory; `finding:` requires `F-\d+`/`PF-\d+` (`FINDING_RE:14`) but this repo mints hex
  ids like `PF-f4d258f365f54f04d9cc976baf0ad981`; `approval:` is the only resolvable type and both
  approvals now read `approved`, so it binds nothing and is correctly refused. Suggested fix: resolve
  `plan-task:`/`brief-sc:` against the feature-tree root per DEC-214's two-anchor rule, and widen
  `FINDING_RE` to the hex ids `panel_findings.py` actually mints. This section is the documented
  disk-only successor path and carries the handoff content.
- **Harness defect, recurring and now cost-bearing.** `runs/<dir>/state.yaml` is UNGUARDED where
  `runs/<dir>/digest.md` is guarded, and nothing stops an agent writing into an occupied run
  directory. `runs/2026-09-05-01-product/state.yaml` has now been overwritten TWICE by two different
  product runs; the second attempted a reconstruction from the surviving digest. It is not
  restorable — `.gitignore:7` means it was never tracked. The canonical record is intact: that run's
  `digest.md` survives and `feature.json` `runs[]` is unchanged.
- Harness defect: the run-digest append-only guard refuses a REPLACING write, so a digest first
  written without the §10.4 contract block cannot be corrected in place. qa worked around it by
  creating a sibling run directory `2026-09-05-qa-gate-record-validator`. One run, one member, zero
  cycles, identical verdict — the sibling is a guard artifact and is NOT recorded as a run.
- Harness defect: `bash-write-guard.sh` blocked a plain shell redirect into a `mktemp -d` scratch
  path and reported the target as `"xx"`, while the same fixture written via a python3 heredoc to an
  explicit `/tmp` path was allowed. Its redirect matcher looks defective on scratch paths.
- Harness defect: `plan-merge.py amend` re-emits a folded `>-` scalar as one long line, so a
  value-only change reflows the whole field. A naive re-wrap split `main-session-direct` across the
  fold and YAML folding turned the break into a space. pm caught and corrected it.
- Harness defect: `check-state.sh` INV-32 (`:533`) requires a `goalcheck` entry in `panel.readers`,
  but `plan-panel.yaml` defines only `should-not-exist` and `scope` — the goal-check runs in the
  PRODUCT segment, so an honest record fails the invariant.
- Record correction, non-blocking: T-04's `intent:` justifies the mandatory index regeneration with
  "appending an entry shifts every later row's source anchor". The documentor measured that it does
  not — DEC-219 appended at EOF moved no earlier `@line` anchor. The instruction's OUTCOME is right
  (the generator is what emits the new row and its `RULING PENDING` sentinel at all) but its stated
  reason is wrong, and it should be corrected before it is copied into a future task.
- Informational, `max_total_runs`: `runs[]` stands at 19 against a budget of 20, and the panel plus
  goal-check will cross it. INV-22 emits a NOTE and never stops a branch. The runs still earn their
  place: every one in this segment returned first-pass PASS with zero send-backs, and the crossing is
  driven by a plan phase that ran two panel cycles, not by rework in the build.
