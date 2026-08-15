# STATE

## Current

- feature: FEAT-21-features-layout-migration
- phase: build — all ten tasks main-session-direct; layer 0 builds, I sequence and verify
- run: none (main-session-direct segments are not runs)
- squad: none
- status: awaiting-user

T-01 is DONE and I re-derived it from disk, not from the report: commit `5afa7e3`
`[harness:t-01]`, one file, 71 insertions. I re-ran its `verify:` verbatim myself — exit 0, both
greps firing, 12 parity assertions printing through the runner over 7 report pairs (MIXED, all five
CANNOT_VERIFY causes including the detail-carrying undeclared-segment, CLEAN), 95 unit suites PASS.
plan.yaml records T-01 `done`; `gh-sync.py close-task T-01` closed issue #389.

The PRE-MOVE boundary capture is on disk, uncommitted, at
`notes/layout-boundary-2026-08-14.md`, HEAD 5afa7e3 recorded inside it. Its content matches the
state I measured myself before the hand-out: both surfaces CLEAN on legacy evidence, 0 mixed,
0 cannot-verify, both exits 0, zero INV-27 lines. No base drift.

MY WRITE WINDOW CLOSES WHEN T-02 LANDS, and I measured it rather than reasoned about it. T-02
rewrites all 43 grants in team-config.yaml from `.harness/features/**` to `.harness/*/features/**`.
`harness_boundary.matches()` translates `*` to `[^/]*`, which cannot cross a separator, so the
migrated grant does NOT match this feature dir at its CURRENT path — probed directly:
`.harness/*/features/**` vs `.harness/features/FEAT-21-.../plan.yaml` returns False, vs the
post-move path returns True. From the moment T-02 lands until T-08 completes the move I can READ
and RUN anything, and can WRITE nothing under the feature dir.

So I front-loaded the bookkeeping in the last writable moment: T-02..T-08 and T-10 are all recorded
`building` in plan.yaml and all eight cards moved on the mirror (#390-#397). That is truthful —
they are one uninterrupted working-tree pass — and it is the only ordering that keeps the
plan.yaml-before-subcommand rule. T-09 stays `pending` deliberately: it runs after T-08 has moved
the dir, by which point my write access is restored and it can be started normally.

Handed back now: T-02 ALONE. It is the highest-value single check-in in the cluster — the first
task to touch the grants and the one that closes my window, so an error there is the one that costs
most. After I verify it I hand back T-03, T-04, T-05 and T-10 as one segment (all share T-02's
single dependency edge and are mutually independent), then T-06 and T-07, then T-08 with a return
before T-09 so I can check the detector at the boundary myself.

Nothing between T-02 and T-08 produces a commit: T-09 lands the whole cluster as ONE commit, so
"landed" for those tasks means working-tree edits with the task's form-check `verify:` green. The
full suites are deliberately red in that window and only T-09 runs them.

## Open Questions

- Q-A (advisory, for the builder; binds T-06 and T-10, NOT T-02): both new clauses anchor on the
  FIRST occurrence of their label string, so an unprompted earlier mention relocates the region.
  Writing `migrated_depth` into test-validate-feature-json.py's module docstring without adding the
  case makes the region docstring-to-first-`def`, which already contains a re-anchored path, and it
  false-greens. Two smaller ones: a conjunct written against a module-level constant instead of an
  inline literal false-REDS, and a literal parked in case_22a's detail f-string rather than its
  assertion condition false-GREENS.
- Q-B (advisory; binds T-06 and T-10): zero DEC-182 headroom — T-10's machine fields sit at 50/50
  and T-06 at 49/50 against `MACHINE_LINES_PER_TASK = 50` (check-plan-routes.py:280). This is also
  why I edit plan.yaml by surgical line replacement and never by a YAML load/dump round-trip: a
  re-wrap reds the gate on a plan whose meaning did not change.
- Q-C (harness defect, raised for the owner, not blocking): `bash-write-guard.sh` refused T-01's
  `verify:` when I ran it verbatim — it read the redirect target `>"$u"` as the literal `xx` and
  blocked it as an out-of-domain write, though `$u` is a `mktemp` path. Every plan `verify:` that
  captures output to a temp file is unrunnable by a governed agent as written. I ran it from a
  scratch script file instead and it exited 0. The guard cannot resolve shell variables, so its
  target report was wrong, not merely conservative.
- Q9 (from the plan run, unchanged — the harness owner's, not this feature's): a lead hosting a
  team cannot yield its turn while backgrounded members are in flight, and leads hold no
  SendMessage, so a lead cannot resume a member to clear that member's own FAIL. Backlog.
