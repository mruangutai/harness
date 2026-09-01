# FEAT-51 plan-panel · scope reader · cycle 5

**BLUF: the plan should ship with three fixes — one MED (D-15 has no self-contained delivery
mechanism, unlike its sibling D-17), one HIGH (the catch-all exception fail-open in the Bash/Write
gates is never exercised by any named test, across all three implementing tasks), one MED (T-07's
own new test group is missing the D-13 negative control that T-09 gives its sibling branch). No
structural defect (orphan REQ/depends_on/verify-discrimination) beyond these three found. Leads 1
and 3 were tested and came back clean.**

## Findings

**SR-1 — sev med — D-15 has no analogue of D-17's self-contained correction, so T-06 can ship the
exact false belief the feature exists to kill, verify green.** D-17 embeds its own fix directly in
T-09's `intent:` ("STEP ZERO ... If T-07 wrote that comment, CORRECT it here", `plan.yaml:917-921`).
D-15 (`plan.yaml:151-154`) has no equivalent: T-06's own `intent:` (`plan.yaml:~495-520`) still
carries, verbatim and uncorrected, the two bullets D-15 says it supersedes — "refused at the
check-domain.sh Write gate on the canonical artifacts" and "the four canonical artifacts are
plan.yaml, BRIEF.md, feature.json and STATE.md" — with no mention anywhere in T-06's intent of
`plan-sign-gate.sh`, the Bash half, or "plan.yaml's only write route is plan-merge.py." Nothing in
T-06's own text points a documentor at D-15. T-06's `verify:` (`plan.yaml:583-586`) only checks
`DEC-209` exists, that `gen-decisions-index.py --stdout` diffs clean, and that the *pre-T-08*,
11-test suite passes — none of which inspects entry content — so **T-06's own gate is green on the
incomplete entry.** The only backstop is T-08, a *test*, not a corrective instruction, dispatched to
a different lane (`harness-dev-ops`, which does not hold `DECISIONS.md` — that's `harness-documentor`
per `lanes.rows`). Consequence: if T-06 is built from its literal, stale intent, the gap surfaces
only at T-08's gate, and repairing it means a cross-lane handoff back to `harness-documentor` that no
task models. Not a build-blocker (T-08 does turn red), but a real, unmodeled rework loop. D-15's own
`because:` clause already predicts this exact failure ("a documentor following T-06's bullet list
verbatim writes an entry that omits the Bash half entirely") without closing it the way D-17 closes
the same class of problem for T-07.

**SR-2 — sev high — the catch-all "any exception → fail open, print a line, fall through" wrapper
around every `inflight_registry` call on the Write and Bash routes has zero test coverage anywhere
in the plan.** T-03 (`plan.yaml:369-372`), T-07 (`plan.yaml:731-734`), and T-09 (`plan.yaml:999-1002`)
all specify the identical shape: import/call `inflight_registry` inside a bare `try` that on *any*
exception prints one stderr line and disables the quarantine check for that call. This is the sole
enforcement mechanism for REQ-03/REQ-04 — the entire feature's core safety promise. I scanned every
named test-case label across T-02's cases 29–33, T-03's six labels, T-07's eight labels and T-09's
seven labels (`plan.yaml:342-347, 397-402, 668-675, 936-942`): none simulates a broken/absent
`inflight_registry`, a raised exception from `orphan_write`/`canonical_artifact`, or otherwise
exercises this branch. Grepped the intent text directly for `corrupt|unparseable|ImportError|not
enforced` — the phrase "not enforced" appears three times, always as the *stderr message text to
write*, never as a test assertion checking that text appears. (T-02's `orphan_write` itself is a
softer case: it reuses `_update_registry`, which the *pre-existing* `case_8_corrupt_registry` in
`test-inflight-registry.py` already proves treats a corrupt file as empty — so that inner layer has
incidental coverage. The outer wrapper in T-03/T-07/T-09 does not.) Consequence: a bug introduced
anywhere inside that `try` block — not just an import failure, since the block's scope is specified
loosely enough to plausibly include the `canonical_artifact`/`orphan_write` calls too — is silently
swallowed and reported only as a stderr line nobody's test reads. A regression that widens the
blast radius (e.g., an unrelated exception three lines later gets caught by the same handler) or
narrows it wrongly (e.g., a crash instead of the promised fall-through, which fails *closed* and
blocks all writes/Bash calls session-wide) both ship green. This is precisely the fail-open class the
review skill and this reviewer's own Expertise (P-02, G-15) flag as highest-value.

**SR-3 — sev med — T-07's new test group has no negative control proving D-13's own stated
fail-open for `--file`, while T-09 gives the same class of case to `--dir`.** T-09 explicitly adds
`NEGATIVE CONTROL: an orphan discard whose --dir value is a shell variable is allowed`
(`plan.yaml:940`) to prove D-13's "a shell variable value falls open" claim holds *under an actual
orphan registry state*. T-07's eight labels (`plan.yaml:668-675`) have no equivalent for `--file`:
the intent text (`plan.yaml:711-714`) instead says the new rule's fail-open on an unresolvable
`--file` "is what keeps the existing controls at :150, :320 and :366 allowed" — but those are
*pre-existing* `denies()`-only tests with no `session_id` and no registry file at all (stated
explicitly by T-07's own intent: "gate() builds a payload with no session_id ... so all twenty-eight
existing cases fall through the new rule untouched"). Those tests prove the *old* sign-approval rule
still fires; they cannot prove the *new* quarantine rule's step 4 (the `.harness/`-segment check)
correctly returns `None`/allow for a shell-variable `--file` **while a live orphan claim exists for
the feature** — the one condition where a wrong answer would actually matter. Consequence: a
regression in the quarantine rule's `--file` normalisation that broke D-13's promise specifically
under an orphan condition — e.g., wrongly matching a shell-variable value against
`CANONICAL_ARTIFACTS` and quarantining a legitimate call, or the reverse, wrongly allowing a real
`--file` value that should have been caught — would pass every test T-07 or T-09 add.

## Leads tested, no finding

- **Lead 1 (proportion):** scanned every task's justification chain for a second instance of "it's
  the only assertion behind an SC" reasoning beyond the settled T-08/SC-09 ruling. Found none — every
  other task traces to a REQ through a mechanism, not a self-referential prose-test. Clean.
- **Lead 3 (the wake):** checked SC-01 through SC-09, SC-11, SC-12 for a quiet dependency on the host
  actually resuming the same parent. All are component-level tests (`validate-digest.py` return
  codes, `check-domain.sh`/`plan-sign-gate.sh` refusals, decision-record content) that neither
  exercise nor assume a live interrupt→resume cycle; only SC-08 (inspection of prose) and SC-10 (uat)
  touch the wake claim at all, and SC-08 grades text-completeness, not truth. This matches the
  goal-check's own §5.2 finding exactly — no new gap beyond the already-accepted bound.
- Orphan-REQ/depends_on-cycle/verify-discrimination hunt: clean. All `depends_on` edges resolve
  backward only (T-03/T-04/T-07 → T-02; T-05 → T-01,T-04; T-06 → T-01..T-05; T-08 → T-06; T-09 → T-07),
  no forward reference, matches the established zero-violation `check-plan-routes.py` result.
