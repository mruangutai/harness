# Plan-panel cycle 2 — scope reader — T-12 and D-12

BLUF: T-12 is clean — correct trace, correct dependency order, verify grep matches the real
`check()` output shape, no other task touches the block it extends. D-12's disposition is
substantively sound but its supporting evidence has one real gap and one shaky citation; neither
is a defect in the *shipped code*, both are defects in the *paper trail* the decision offers as
proof. Two med findings, no highs, no blockers.

## Q1 — T-12's `traces: [REQ-06]`

Apt, not over-claimed. REQ-06 governs the Build-refusal mechanism ("Build refuses to start when
the required Build-entry outcome is absent... may proceed after a recorded temporary
environmental mirror failure"); T-12 fixes a defect inside that exact mechanism
(`_build_entry_preflight`, gh-sync.py:1360) that made the era-exempt continue-branch unreachable
under a trailing slash. T-04, which built the mechanism, traces the same REQ-06 (plan.yaml:632).
Consistent, nothing else served (T-12 does not touch merge-gate/SC-04) and nothing left untraced.

## Q2 — dependencies and topology

`depends_on: [T-04, T-06]` (plan.yaml:1794) — both `status: done` (plan.yaml:389 is T-02, T-03
line 518 done; T-04 line 636 done; T-06 line ~1112 done) — satisfiable now. T-11 gained `T-12` in
its `depends_on` (plan.yaml:1608) alongside T-02/T-03/T-04/T-06; T-12 does not depend on T-11, so
no cycle. Both T-11 and T-12 are `status: ready` (neither `done`), so the new ordering has nothing
retroactively broken to reconcile. Clean.

## Q3 — verify block vs. the file's real shape

Confirmed against source, not prose: `check()` at test-gh-sync.py:733-738 prints exactly
`f"ok    {name}"` (4 spaces) on pass and `f"FAIL  {name}\n      {detail}"` on fail — T-12's
`grep -qF "ok    T-12 era-exempt trailing slash continues"` and the `^FAIL` guard both match the
real format. The `with tempfile.TemporaryDirectory() as tmpT04:` block referenced as "the T-04
block that ends at :3624" is confirmed the **last block in the file** (file is 3626 lines;
`sys.exit(1 if fails else 0)` is the final statement) — no other task can rewrite it out from
under T-12. Grepped every task's `files:` list for `test-gh-sync.py`: only T-02, T-03, T-04 and
T-12 declare it, all three predecessors already `done`, none re-touches the T-04 block. Clean.

## Q4 — D-12 against D-10, D-11, DEC-217, DEC-174

Read D-10's live text directly (plan.yaml:139-149, not the amendment note): it already reads "...
and its DISPOSITION is D-12: the unit kind there is NOT-APPLICABLE, never an owed test recorded
as a gap" — coherent deferral, no residual "gap" language left over from before the amendment.
D-11 governs a different question (which *files* sit inside the DEC-174 execution carve-out) and
does not collide with D-12's *test-kind* disposition.

**Finding A (med) — D-12's DEC-174 supporting clause misreads DEC-174.** D-12 (plan.yaml:158-186)
argues extracting post-merge-sweep.sh's heredoc-hosted retention arm into an importable module
"would be a runtime change to a DEC-174 enforcement surface made to satisfy a directory label...
and it would touch the enforcement layer under DEC-174 as well" — read as: DEC-174 forecloses that
path. But DEC-174 itself (DECISIONS.md:4302-4403, "Where the line falls for a library a gate
calls") states the opposite: *"A module a gate imports is not itself a gate. A squad may write the
library, and the cutover that makes a gate use it is main-session-direct, proven by showing the
gate's violation set is identical before and after."* DEC-174 explicitly sanctions exactly this
extraction shape (team writes the module, main-session does the trivial cutover). D-12's primary
argument — DEC-217's Over clause forbidding a runtime change made solely to satisfy a directory
label — stands on its own and is not undermined by this; the disposition itself does not flip.
But the DEC-174 citation inside D-12's "because" is not a fair reading of what DEC-174 says, and a
future reader following that reference (as this task's own instructions direct: "follow references
out of the decisions you open") is told DEC-174 blocks something it names a sanctioned path for.

## Q5 — is the offered evidence sufficient for T-07's retention branch?

**Finding B (med) — the offered coverage has a real, unexercised branch member.**
post-merge-sweep.sh:222's retention gate is `elif entry not in {"opened", "not-applicable",
"recovered-terminal"}:` — three values share the "let it be removed" side of that set. T-07's
eight named cases (verified present, test-post-merge-sweep.py:886-895) exercise `opened` ("T-07
opened removes the worktree") and `recovered-terminal` ("T-07 recovered-terminal removes the
worktree") individually, plus the absent/recovery-required/era combinations — but **no case ever
sets `build_entry` to `"not-applicable"`** (confirmed by reading the fixture body,
test-post-merge-sweep.py:896-925: `shapes` only ever writes `None` or an explicit non-`None`
`entry`, and the eight names above are the full enumerated set; no ninth "not-applicable" case
exists). T-10's red-proof (plan.yaml:1531-1591) is real and does strengthen the `opened` path, but
it commits `build_entry="opened"`, not `"not-applicable"` — it does not touch this gap either.
`not-applicable` is reachable in production: it is recorded when `github.sync` was false/absent at
Build entry time (SC-01), and post-merge-sweep.sh reads `github.sync` fresh at *sweep* time
(post-merge-sweep.sh:216-217) — a project that flips `github.sync` on between a feature's Build
entry and its merge reaches this exact state. A mutation dropping or misspelling
`"not-applicable"` out of that set literal would silently start retaining (or, the reverse typo,
start removing) worktrees for that state, and nothing in the evidence D-12 offers — "the
integration kind carries the coverage," unqualified — would catch it. This does not fail SC-06
(SC-06 names only the era pair as the graded cases) and does not make the current code wrong; it
means D-12's blanket sufficiency claim for "T-07's retention branch" is one state wider than what
was actually proven.

## Findings summary

- Finding A (med): D-12's DEC-174 citation, inside its `because:` prose, asserts DEC-174 forbids
  an extraction shape that DEC-174's own "library a gate calls" clause explicitly sanctions. Does
  not change the NOT-APPLICABLE disposition (DEC-217's Over clause is sufficient on its own) but
  misdescribes the decision it cites.
- Finding B (med): D-12's "the integration kind carries the coverage" claim for T-07's retention
  branch is not fully proven — the `"not-applicable"` member of the retention allow-set
  (post-merge-sweep.sh:222) is exercised by none of the eight named cases nor by T-10's red-proof,
  leaving a real, currently-silent regression window in the same set the tested members belong to.

No findings on Q1–Q3; T-12 itself (trace, dependency order, verify-vs-source shape) is clean.
