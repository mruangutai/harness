# Plan-panel scope review — BUG-442 (drafted, unsigned)

**BLUF: no gating finding.** All 5 REQs trace to T-01 with no orphans and no fictitious citations;
the three acceptance clauses each have a real task step and SC; the mutation controls are
discriminating (verified against the actual test bodies, not just T-01's prose). Two `med` and one
`low` advisory carried forward for the record; none blocks signature.

## Structural sweep (orphan REQ / fictitious trace / dependency order / predecessor-deletes-what-verify-needs)

- **Orphan REQ / fictitious trace: no finding.** `T-01.traces == [REQ-01..REQ-05]`
  (`plan.yaml:64`) and `BRIEF.md` declares exactly REQ-01..REQ-05. Single task, single REQ set,
  bijective.
- **Dependency shape: no finding.** One task, `depends_on: []` (`plan.yaml:67`) — a 1-node graph is
  trivially a topological order.
- **Verify-asserts-something-a-predecessor-deletes: no finding.** No predecessor exists.

## The six pressure points

**1. Acceptance coverage — no finding.** Independently re-derived (not taken from pm's table):
(a) MANIFEST_PATH load → REQ-01/SC-01, T-01 intent §3 calls the helper on module-level
`MANIFEST_PATH` (`test-harness-yaml.py:32`, sole real-manifest consumer besides the pre-existing
equivalence test). (b) exhaustive-16 → REQ-04/SC-02, T-01 §1 `DOCS_GRANT_CENSUS` + §3a per-persona
asserts. (b, addition) → REQ-02/SC-03, M1. (b, removal) → REQ-03/SC-04, M2. REQ-05 (equivalence
fixture unweakened) is enforced by explicit "do not touch" constraints in T-01's intent and gated by
SC-06/SC-07. No REQ lacks a task+SC pair; no task step lacks a REQ.

**2. Mutation controls: discriminating, not merely red — no finding.** I checked what else in the
suite reads the real manifest: only `test_manifest_domains_matches_the_regex_walk_on_the_real_manifest`
(`:190`, against `COLLECT_FIXTURE`) and the two new tests. `test_manifest_domains_excludes_non_canonical_read_true`
(`:199-224`) builds its own tmp fixture, untouched by team-config mutations. `COLLECT_FIXTURE` covers
6 personas — backend-dev, dev-ops, pm, documentor, eng-lead, orchestrator (`:48-133`) — neither
`harness-qa` (M1) nor `harness-ui-reviewer` (M3) is a key in it, so **nothing else in the suite
reddens under M1 or M3**; the witness's own `FAIL` line is the only line that can appear, making the
check trivially sufficient there. M2 is the real case pm flagged (also reddens the equivalence
fixture) — I traced it through `manifest_domains` (`harness_yaml.py:405-416`): after M2 deletes
`.harness/*/docs/**`, `docs_grants['harness-documentor']` returns `['docs/**']` only, which fails
the per-persona assert against `EXPECTED_DOCS_GRANTS['harness-documentor']` inside
`test_docs_domain_grant_is_exhaustive_over_every_persona` itself — so the witness's own `FAIL` line
is a real, non-vacuous signal for M2, not a coincidental echo of the equivalence test's failure.

**3. Anti-false-red control — `low` finding.** The mechanism works, but T-01's own rationale
misdescribes it. `main()` (`:892-904`) wraps each `TESTS` entry in its own `try/except Exception`
and prints `ok`/`FAIL` per test — it does **not** "die on import and print FAIL for everything" (the
stated fear in T-01's intent §4); a per-test exception only fails that one test, and `harness_yaml`
always imports successfully regardless of `HARNESS_PROJECT_DIR` (`BIN_DIR`/`sys.path` are computed
from `__file__`'s real location, `:17-23`, never from the overridden root). The scenario the check
*actually* guards is a whole-file parse failure (e.g. a syntax slip in the new code) that prevents
`main()` from ever starting — in that case neither the `ok` line nor the witness's `FAIL` line
appears in `child.stdout`, and the parent test's own assertions correctly fail. So the control is
functionally sound; only the inline justification text is wrong about the mechanism. If an
implementer copies that prose verbatim as a code comment, it will mislead the next reader. Concrete
consequence: none today (it doesn't change what ships), but it is worth correcting during
implementation rather than carrying a wrong mental model forward.

**4. Self-recursion guard — `med` finding.** Placement is correct: "checked FIRST inside the test
function" (T-01 §4) means nothing in the function body can run before the check, so the intended
recursion cannot be entered. The gap is the untested branch: **if `BUG442_MUTANT_CHILD` is already
set in the environment the top-level (real, non-subprocess) run inherits** — a stale exported value
from a prior manual repro, a shared CI shell step, or any accidental collision with that exact name —
the *parent* invocation of `test_docs_domain_witness_reddens_on_addition_removal_and_census_drift`
hits the guard first and returns immediately, having built zero mutants and asserted nothing.
`main()` sees no exception and prints `ok   test_docs_domain_witness_reddens_on_addition_removal_and_census_drift`
— indistinguishable from a fully-executed, fully-discriminating negative control. This is exactly the
defect class D-03 exists to close ("a witness that cannot fail is the exact defect BUG-442 names"),
reintroduced one layer up: the guard that prevents infinite recursion in the child also silently
disables the entire negative control in the parent under a specific, narrow but real precondition.
Not blocking signature (the var name is unusual enough that accidental collision is unlikely in
practice), but worth a one-line note in the task's intent (e.g., `os.environ.pop` in a `finally`, or
asserting the var is unset on entry) so the failure mode isn't invisible if it ever fires.

**5. Hand-pinned literal census — position: feature, not trap. Severity: `info`.** The stated D-01
rationale ("a walk-only domain of quantification shrinks silently when a persona is deleted") is
exactly what REQ-04 demands ("deleting a persona from the manifest cannot silently shrink the
assertion" — `BRIEF.md` REQ-04). The cost is real — **any** future org-topology change (a persona
added or renamed for reasons unrelated to docs) reddens `test_docs_domain_grant_is_exhaustive_over_every_persona`
until a human updates `DOCS_GRANT_CENSUS`/`EXPECTED_DOCS_GRANTS` — but that is the correct behavior
for an *exhaustive* assertion whose domain includes "does this new persona hold the grant?", not
noise: a new persona is, by definition, a new unanswered question for this test. The failure message
T-01 mandates (name missing vs. unexpected personas separately, §3a) makes the fix-up cheap and
legible rather than a mystery regression. BRIEF's own "Verification notes and gaps" section already
states the adjacent residual candidly, which is evidence this tradeoff was made deliberately rather
than by oversight.

**6. `verify:` hard-codes the absolute worktree path — `med` finding, disagreeing with pm's
"advisory/non-blocking."** `plan.yaml:41-44` repeats
`/Users/.../.claude/worktrees/harness/BUG-442-docs-grant-witness-test/tests/integration/test-harness-yaml.py`
four times. I checked five other recent feature plans in this repo (BUG-1081, BUG-1157, BUG-1286,
BUG-1290, BUG-1302) for the house convention: every sampled `verify:` block uses a **relative** path
(`python3 tests/unit/test-suite-layout.py`, `python3 tests/integration/test-factory-integration.py`,
etc.), which resolves identically from any worktree root and — critically — still resolves after the
worktree that built the feature is torn down, because the same relative path exists in the merged
main checkout. BUG-442's plan is the outlier. Consequence: `plan.yaml` is a durable per-feature
artifact (harness-handoff: pm/qa/reviewers cite it after the worktree is gone); this task's `verify:`
becomes permanently unexecutable — `No such file or directory` — the moment
`BUG-442-docs-grant-witness-test`'s worktree is removed, which conflicts with "verification is the
product": a verify block that stops being runnable stops being evidence. It does not block T-01's own
build-time run (qa executes it from inside the live worktree), which is why it doesn't rise to
`high`, but it is a real, avoidable maintainability defect in a document meant to outlive the
worktree — `med`, not advisory.

## Severity summary

| # | topic | severity |
|---|---|---|
| 1 | acceptance coverage / orphan REQ / dependency order | no finding |
| 2 | mutation-control discrimination (M1/M2/M3) | no finding |
| 3 | anti-false-red rationale mismatch | low |
| 4 | self-recursion guard vs. leaked `BUG442_MUTANT_CHILD` | med |
| 5 | hand-pinned census maintenance cost | info (feature, not trap) |
| 6 | hard-coded absolute worktree path × 4 | med |

None of these reach `high`/`critical` and none is `must_fix`; nothing here should block signature.
