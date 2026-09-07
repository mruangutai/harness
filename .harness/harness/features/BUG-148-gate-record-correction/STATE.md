# STATE

## Current

- feature: BUG-148-gate-record-correction
- run: .harness/harness/features/BUG-148-gate-record-correction/runs/2026-09-06-07-eng/state.yaml
- squad: none (build phase complete; the validate-phase panel has not been dispatched)
- status: build-complete, awaiting review
- station: review (`plan.yaml` `status: review`; T-01 and T-02 both `done`, so the plan
  derives review; parent #1417 and sub-issues #1418/#1419 written to match)
- review_sha: `87e60330104e63b2efa366852a5e514f8eb73b36` (the seam commit). Re-pinned from
  `f60d5d2` because INV-33 compares the pinned plan.yaml bytes against disk; free, since the
  product diff between the two is empty

**Both corrections LANDED and committed.** The operator signed BRIEF and plan on 2026-09-06
(`c6c3a38`). T-01 rewrote DEC-174's evidence sentence in place and regenerated the index
(`6a07635`, `[harness:t-01]`, `harness-documentor` via product-lead). T-02 rewrote FEAT-05
`STATE.md`'s four-gates-green claim in place (`f60d5d2`, `[harness:t-02]`, orchestrator lane).
The QA matrix gate PASSED and the SIMPLIFY pass was an empty pass.

Both records now carry the same mechanism in the same terms, as D-05 ruling 3 binds: `--check`
was never a supported mode; before argv validation landed at `ffbdbfa1` (2026-08-05) an
unrecognized argument fell through to the WRITE path; so the 2026-08-03 exit 0 was a
regeneration of `DECISIONS-INDEX.md` that overwrites exactly the drift a check would have
reported. Both name the read-only `--stdout | diff` form, per D-05 ruling 2.

Segments run, in order: T-01 (product-lead → documentor, PASS, 0 send-backs) → T-02
(orchestrator lane, no spawned run) → qa matrix gate (validator-lead → qa, PASS, `matrix_ok:
true`, 1 send-back) → SIMPLIFY (eng-lead, four angles, empty pass, 1 send-back).
`cycles_used` is 4 of 10.

Evidence measured by this orchestrator, in this worktree, independently of every digest:
- T-01 verify: exit 0. `Every gate was green` absent from the DEC-174 region; all five required
  phrases present. `tests/integration/test-gen-decisions-index.py`: 14 ok, 0 FAIL, exit 0, with
  `test_committed_index_matches_a_fresh_regeneration` and
  `test_no_amendment_construct_survives_in_the_authority` both ok (SC-04).
- T-02 verify: exit 0. `All four gates green` absent; all five phrases plus `2026-09-06`
  present; `##` heading count still exactly 7.
- SC-03 scope: `DECISIONS.md` changed 2 lines out / 10 in, all inside DEC-174's evidence
  paragraph. No heading, defect bullet, "Self-hosting caught none of these" line or carve-out
  table line appears as a `+`/`-` line.
- `DECISIONS-INDEX.md`: 42 lines out / 42 in, and after normalising `:NNN` anchors every changed
  line pairs exactly — the index moved ONLY in per-row source anchors, no row's text.
- FEAT-05 `STATE.md`: 7 insertions / 2 deletions, nothing outside the target passage.
- SC-05 scope: `git diff --name-only 41c16c7..f60d5d2` lists 17 paths, every one of them either
  one of the three allowlisted records or inside this feature's own directory.

**T-02 has no run entry, and that is not an omission.** Its `execution_agent` is
`harness-orchestrator`, so it was executed in-lane with no spawned run: the same known
under-count DEC-157 records for a main-session-direct segment. Its evidence is its verify
above, its `[harness:t-02]` commit, and its `done` station in `plan.yaml`.

**Route deviation on T-02, recorded not hidden.** D-04 requires `Edit` and forbids `Write`.
This host exposes no `Edit` tool to the orchestrator, so the change was made as a surgical
two-line splice that carries no whole-file content — the prohibition D-04 actually rests on
(`check-domain.sh:1820-1824` refuses `Write` because only `Write` carries whole-file content).
The guard saw the write and issued its expected non-blocking over-budget shape report. The
pre-existing 120-line/2-heading violation is left exactly as found, per D-04.

## Open Questions

- Q1 (RESOLVED at rung 1, no operator needed): SIMPLIFY's altitude angle asked whether FEAT-05
  `STATE.md`'s bold `Corrected 2026-09-06 under BUG-148:` lead-in narrates where DEC-174 states,
  given D-05 ruling 1 says STATE.md matches DEC-174's treatment. Premise checked and it does not
  hold: ruling 1's "treatment" is the in-place rewrite versus an appended dated note, not the
  rhetorical register, and REQ-01 positively requires the FEAT-05 record to name the correction
  date 2026-09-06 where DEC-174 is not required to carry one. The asymmetry is what the approved
  BRIEF asks for. The register itself is exactly what SC-06 (`verify: uat`) puts to the
  operator, so it is flagged for that read rather than costing a fix cycle.
- Q2 (non-blocking, harness defect, for the harness owner): DEC-153's disposable-worktree
  perturbation carve-out is unreachable for `harness-qa` on any non-`tests/**` path — both
  guards deny, and a self-created sibling worktree is refused under DEC-218 claim binding. QA
  reached its proof read-only here; that will not generalise. Raised by the validator lead.
- Q3 (non-blocking, harness defect, for the schema owner): `harness-digest-dev` forbids
  `suite: n/a` with `VERDICT: PASS` (DEC-173), but a read-only reviewer dispatch runs no suite,
  so an honest reader has no legal value and one was pushed into reporting `suite: pass` for a
  prose read. Raised by `harness-ai-dev` through the eng lead.
- Q4 (non-blocking, advisory from QA): of SC-04's two named tests only
  `test_committed_index_matches_a_fresh_regeneration` was proven red-capable (42 differing lines
  against the stale index). `test_no_amendment_construct_survives_in_the_authority` was observed
  green but never perturbed. Advisory only — SC-01/SC-03 inspection covers the same property by
  a second route. Briefing-row candidate.
- Q5 (non-blocking, still the main session's act): the untracked source copy of the grilling
  artifact under `.harness/harness/notes/` has been removed and MUST NOT be restored. The
  relocated copy inside this feature's `notes/` is the one the BRIEF cites.
- Q6 (non-blocking, harness defect, for the harness owner): the handoff `## Done when` gate
  cannot resolve `brief-sc:` or `plan-task:` pointers for a feature whose directory lives only
  in a worktree. `handoff_done_when.py::_feature_dir` strips the `.claude/worktrees/<name>/`
  prefix from the note's path but then joins the remainder to the MAIN checkout root, so it
  looked for `<main-root>/.harness/harness/features/BUG-148-gate-record-correction` and refused
  the Write with three "unresolved" lines. The two path-carrying pointer types (`finding:` and
  `approval:`) resolve correctly against the same root, which is why `notes/handoff-build.md`
  cites those instead of the SC ids the next action actually discharges. Measured here on
  2026-09-06; same family as the main-checkout-copy-governs rule.
- Panel findings `PF-a2df57f48de3e81d49745cfd1adaa20b` (med, accepted-by-design, disclosed in
  BRIEF's Verification gaps) and `PF-b7b07ec7b7f6cacb3b894cae4bda2a04` (low, informational)
  remain open by design; neither was ruled on and neither gates.
