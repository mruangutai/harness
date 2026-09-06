# STATE

## Current

- feature: BUG-1304-worktree-relative-path-guard
- run: main-session-direct build, orchestrated by BuildBug1304 — COMPLETE
- squad: none for the tasks; validator ran the qa gate, eng ran SIMPLIFY, both once, both PASS
- status: review — build phase closed, review-ready, awaiting the validation panel

BUILD IS COMPLETE AND REVIEW-READY. plan.yaml station `review`; all nine live tasks `done`; T-08
`abandoned` (struck, its defect owned by #1341). `review_sha` pinned at `af5ddd7a`, the station
commit — a pin must both CONTAIN the work and not predate the station write, and INV-6 reported the
earlier `6dd081a1` pin stale the moment plan.yaml moved. `check-state.sh` exits 0 with ZERO
violations. `run-unit-tests.sh --kind all` exits 0 with 0 `^FAIL ` and 73 files discovered — the
SAME 73 as the pre-build baseline, so the green is not a discovery collapse.

EVERY LIVE TASK VERIFIED BY THE ORCHESTRATOR, each task's own `verify:` block re-run VERBATIM at
the named sha, never accepted on report:
- T-01 `da37f082` red (a=1 b=1, and both reds for the RIGHT reason — `claim_worktrees` and
  `live_claims` absent, not an unrelated crash) · T-02 `81a66bb3` green
- T-03 `5a106acd` red, callsites=10 · T-05 `5facdf5e` red, callsites=12. In each the red count
  EQUALS the callsite floor and every red is `[bug1304]`: zero pre-existing cases broke.
- T-04 `62e5bf6d` green (+51/-0, a PURE ADDITION — DEC-153's carve-out was narrowed by ADDING the
  assigned-worktree test, not by deleting its rationale) · T-06 `fb762215` green
- T-09 `a4e8ecf7` green · T-07 `7a9c3cb4`+`6dd081a1` (DEC-218 + index, graded with
  `git show <sha>:<path>` as SC-07 requires) · T-10 `af5ddd7a` green, both halves
- merge `bfd99371` — origin/main brought DEC-216/217 from BUG-1303. DEC-218's body verified
  BYTE-IDENTICAL across the merge; only its index anchor moved `@6792 -> @6844`.

AMENDING COMMITS, each charged one cycle: `83d17657` (11) — `claim_set_refusal` appended the CLI
advice AFTER "write it from a bound worktree", violating REQ-06 and T-05:1155. `ad67d22b` (12) —
FEAT-51 sibling repair under the ruling below. `6dd081a1` (13) — DEC-218's index ruling was 33
words against a 30-word cap; T-07's `verify:` regenerates and diffs the index while the generator
PRESERVES a hand-written ruling (`gen-decisions-index.py:71`), so the cap is asserted ONLY in the
unit suite and no task's verify can reach it. That is why the whole suite is run, not the block.

GATES PASSED on `b64b2d53..6dd081a1`:
- QA GATE (blocking; the project's only one) — PASS. `matrix_ok` true; test-first ordering verified
  from the commit graph on all four red/green pairs; SC-06's `bug1304_assert_pre_change_allows`
  confirmed to assert BOTH halves (quiet stderr AND a positive control still refused at the same
  frozen guard) at all 10+12 call sites; the FEAT-51 `unimportable` case still asserts exit 0, so
  quarantine's own fail-open remains pinned by a LIVE assertion. qa's stated limits, carried
  forward honestly: red-at-the-test-commit was not re-executed, and no mutation testing was run.
  `runs/qa-gate-validator/`.
- SIMPLIFY — PASS and effectively EMPTY, which is a real outcome; nothing was invented to justify
  the step. Apply was FLAG-ONLY under the DEC-174 carve-out. Reuse confirmed both routes reach the
  SAME predicate and the SAME message builder, so the DEC-193 seam holds. `runs/simplify-eng/`.

BACKLOG ROW from SIMPLIFY, filed not applied: `claim_worktrees` (harness_boundary.py:252-277)
computes `linked_worktrees(owner_root)` for `roots`, then `worktree_for_feature` (:229) recomputes
it per matching claim — 1+C enumerations per governed write, ~1.24ms against a ~38ms interpreter
floor, C<=1 fleet-wide, so today's benefit is ZERO. The reader's call-local prefix helper was
REJECTED by the eng lead: it would restate the prefix-match and `AmbiguousWorktree` rule that SC-05
and SC-08 pin. Only safe form passes the computed candidate list into `worktree_for_feature`.

CYCLE BUDGET — 13 of 16 under binding ruling `RuleBug1304FinalBudget` (hard ceiling 20, never a
target; first-pass gate and panel runs cost ZERO, only a send-back charges; record and ledger
repairs are zero-charge; past 16 needs a FRESH ruling with no contingent pre-authorisation).
`len(runs)` 17 of `max_total_runs` 20 — informational, and the runs still earn their place: the
plan phase spent thirteen resolving a design the panel twice sent back, and the build spent four.

NEXT: the validation panel against `af5ddd7a`, then pm's goal-check of all twelve SCs, then UAT if
required, then ship. SC-07 must be graded with `git show af5ddd7a:<path>` and by DECISION ID —
five boundary questions, each against the decision named for it — not by grepping the file.

THE THREE REQUIRED FOLLOW-UPS ARE FILED AND OPEN (verified 2026-09-05). None may be implemented
inside BUG-1304 — doing so expands an approved scope.
- #1341 — `dispatch-guard.sh:122` `_root_for` basename equality should be `worktree_for_feature`
  prefix alignment. Struck T-08's defect; the strike is legitimate only because #1341 owns it.
- #1342 — `linked_worktrees` fail-OPEN on OSError and on an unreadable pointer (F2). NOW NARROWER
  than when filed: the ruling below settled the registry half, so only `linked_worktrees` remains.
- #1343 — `validate-digest.py:1755` `live_children` cannot see a compatibility child past 1200s.

BINDING RULING `RuleBug1304UnreadableConflict`, recorded WITH the reading that LOST. T-04's binding
made FEAT-51's directory-at-the-registry-path case refuse where FEAT-51 pinned fail-open. The
orchestrator argued no conflict existed — REQ-05 enumerates three fail-closed causes and a
directory is an OSError, none of them; every `UnreadableRegistry` assertion in the tree uses a
parse payload, so narrowing `live_claims:298` would have cost zero assertions. THE ADVISOR RULED
OTHERWISE and it binds: keep `except (OSError, UnicodeError)`, narrow the FEAT-51 fixture. DEC-218
carries all three consequences, including that quarantine machinery's own failures stay fail-open.

RECORD REPAIRS COMPLETE, zero-charge: five digests now return `digest ok`; `plan.yaml
panel.readers` re-keyed from PERSONA to STEP name, with `goalcheck` recorded `skipped` WITH a
reason because no goalcheck reader ran in the recorded cycle-3 panel and a false `ran` is worse
than an honest skip. In-place editing was impossible for all three digests —
`check-domain.sh:1252` admits only a byte-prefix EXTENSION of a recorded run digest — so each is an
appended canonical block with the original left superseded and every member FAIL preserved. Eight
run dirs exist that `feature.json` never records and one recorded run has no dir; both are notes,
not violations, and no verdict was backfilled for a run this orchestrator did not conduct.

DEAD ENDS, do not re-open: the binding key (DEC-208 ruling 2 rejected a payload key); building S
from which registry FILE a claim sits in; filtering the binding enumerator with `_expire` or
`CLAIM_TTL_SECONDS`; the `CHECK_DOMAIN_BIN`/`BASH_WRITE_GUARD_BIN` override for SC-06; narrowing
`live_claims`'s OSError catch; and the simplify reader's call-local prefix helper.

## Open Questions

- HARNESS DEFECT — INV-26 and the mirror contract disagree about a done task's card.
  `gh_board.project` places a sub-issue at its own station "VERBATIM AND WITH NO EXCEPTION", so a
  done task wants the done column, but NO subcommand writes that column before `ship`
  (`gh-sync.py cmd_status` writes `ready` and `review` only). D-24's widening papers over it solely
  while the feature's station is `review`, so every feature is red between its last task landing
  and its review transition — and no command can clear it. Cost here: T-10's `verify:` could not
  pass until the seam, which forced the last task to be sequenced after the station write.
- HARNESS DEFECT — INV-32 reports a wrongly-KEYED but otherwise complete reader entry as "reader
  <x> never ran or was not recorded", which reads as a missing panel record.
- HARNESS DEFECT — `plan-merge.py apply` cannot amend an existing top-level `panel`: it is not in
  `UNION_KEYS` (`:104`), so the step-8 guard (`:764-774`) exits 7 CONFLICT and writes nothing. The
  working verb is `set-panel --value-file` (`:1040`), which the orchestrator playbook never names.
- HARNESS DEFECT — a handoff note cannot be written from a worktree. `check-domain.sh:1614` passes
  `rel` worktree-STRIPPED with `root` the MAIN checkout while `FEATURE_RE` is `^`-anchored.
  Measured both ways. BUG-1304's own defect class one layer up; needs its own issue.
- HARNESS DEFECT — `runs/*/state.yaml` is clobbered by a later run reusing a run id; `digest.md` is
  guarded against replacement and `state.yaml` is not. BUG-1305 owns this class.
- HARNESS DEFECT — two subagents returned well-formed VERDICT/DIGEST blocks while the task tool
  reported `failed (exit 1)` with "yield called with null data".
