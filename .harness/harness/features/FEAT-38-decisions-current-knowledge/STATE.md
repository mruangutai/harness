# STATE

## Current

- feature: FEAT-38-decisions-current-knowledge
- run: `2026-08-29-simplify-ship-eng` — PASS, the four-angle pass applied one dead-code fix
- squad: eng (`harness-backend-dev`, via `harness-eng-lead`)
- status: **Review**. The BUILD IS COMPLETE and `review_sha` is pinned. No PR, no merge, no ship.

**All 28 planned tasks read `done`.** The five that remained at the third signature landed in
`depends_on` order across four commits, each verified by the orchestrator running the task's own
`verify:` extracted from the signed `plan.yaml` with `harness_yaml.load_plan` rather than retyped:

- **T-27** (`0a94d91`) — all eleven claim markers deleted from `DECISIONS.md`, in six entries.
- **T-24** (`8c879f5`) — the claims test deregistered from `INTEGRATION_SCRIPTS` and both claims
  files `git rm`'d, landed together as one atomic step.
- **T-28, T-29** (`70690ea`) — DEC-205's item 2 deleted and its three check-counting sentences
  repaired, index ruling hand-rewritten and proven idempotent; the `bin/` argv-class audit written.
- **T-25** (`8a7c75c`) — the claims test deregistered from `harness.json`'s integration `detect`.
- **qa + SIMPLIFY** (`635cd3b`) — the blocking gate's evidence, and one dead-code apply.

**SC-13 STANDS and does not return to the operator.** Ruling 6 voids the standing UAT only if T-27
touched prose in any of the six marker-carrying entries. It did not, and this was re-derived rather
than accepted on report: at `0a94d91` the prose line sequences before and after are IDENTICAL
(5067 lines each; 20 lines removed = 11 markers + 9 blanks; zero insertions). The check was run
grep-free because this environment's `/usr/bin/grep` is `pi-uu-grep 0.2.0`, in which `^+` matches
EVERY line — it reported 83 insertions against a true `--numstat` of zero.

**Ruling 2 asserted directly, not inferred from a green suite.** `check-decision-anchors.py` and
`test-check-decision-anchors.py` are byte-identical to `git show 99bb52c:` (sha256 `adb9a648…`,
`7a4e0ba1…`) and are named by BOTH registration sides. Re-asserted after the SIMPLIFY apply.

**The blocking qa gate PASSES** — `matrix_ok: true`, `must_fix: []`. Suite at the pinned tip: exit
0, ZERO lines beginning `FAIL `, and all **55** registered scripts actually ran, so the green is not
a gate that discovers nothing. qa recorded its own limits rather than smoothing them: the matrix
owes `[]` over the prose bulk of the diff, and the test-first audit is vacuously clean.

**The retained checker CAN still report red**, which qa honestly flagged it had not established.
Orchestrator probe on a `/tmp` copy, so the tree was never perturbed: unmodified copy exits 0 over
20 anchors; with one fabricated anchor planted it exits 1 naming the line.

**SIMPLIFY ran BEFORE the pin**, so no apply commit can move the tip under the panel. All four
angles reported and three declined on the merits. One apply: `gen-decisions-index.py`'s
`parse_decisions` returned a 3-tuple and an unread `title` key, both orphaned by T-10's deletion of
their only consumers — dead code left by a deletion, and none of SC-06's seven named symbols reach
it. Post-apply the suite is green and the generator's output diffs clean against the committed index.

`review_sha` is **`635cd3ba…`**, pinned at the tip that CONTAINS the build. The stale `48bbe7e`
pin, which named the superseded validate phase, is gone. `gh-sync.py status … Review` moved the
parent #935 and all 29 sub-issues to Review, exit 0.

**Budget: cycles 14 of 30; runs 31 of an informational 20.** `cycles_used` is UNCHANGED: every one
of this phase's six runs returned PASS on its first pass with zero send-backs, and DEC-157 counts
rework only. `len(runs)` has passed `max_total_runs` and INV-22 will say so; the count is
informational and stops nothing. The runs still earn their place — six runs closed the entire
remaining build plus both gates, with no rework.

## Open Questions

None blocking the panel. Carried to the operator in the ship briefing:

- **A run-directory collision destroyed a record.** The T-27 lead wrote its run into
  `runs/2026-08-29-01-product`, already the panel-revision run's directory, overwriting that run's
  `digest.md` and `state.yaml`. `runs/` is gitignored, so it was never in git and is unrecoverable.
  The T-27 artifacts were relocated to `runs/t27-product/` and a tombstone left behind. Nothing in
  the run-directory contract prevents a lead from choosing a slug that already exists.
- **`bash-write-guard.sh` cannot expand shell variables and does not track `cd`** — it resolves a
  write target against the session root, so `cd <dir> && sed -i '' … plan.yaml` and `sed -i '' … "$P"`
  were both denied as "outside your domain" while the identical command with a literal absolute path
  was allowed. `check-domain.sh --resolve` grants `plan.yaml` to `harness-orchestrator`, so the two
  surfaces disagree. A second agent hit the same shape in the edit tool's `[path#TAG]` hashline.
- **A stale prose reference SC-18 forbids fixing.** `check-decision-anchors.py`'s docstring still
  says the snippet problem "is the executable-claims checker's job (a different tool)" — false now
  that the tool is deleted. SC-18 pins that file byte-identical to `99bb52c`, so this feature
  structurally cannot fix it. Pre-existing, not introduced. Backlog.
- **DEC-205 names two refused rot detectors but not what compensates today.** The real answer lives
  only in `BRIEF.md`, a per-feature artifact. The remedy would add positive content to DEC-205,
  which the operator's ruling forbids. Operator's call.
- Non-blocking Q6..Q10 from the plan phase remain open and gate nothing. REQ-08 and SC-09 are
  retired tombstones and are graded by nobody.
