# Review — harness-code-reviewer — validate-delta-c23

**PASS. The enum fix is correct and complete, the ungated-lead-residual claim holds under a live
probe, and the confirmation run reproduces the panel's numbers exactly.** `must_fix` is empty.
`severity_max: none` (the guard's own quality is clean; one `low` finding on the regex's
brittleness to inline comments, non-blocking).

Reviewed `a0ff125..6752597830ee62b91ed34c79be3306dab149c0b6` (the fix commit against its parent —
this is the actual code delta; the full `17106762..6752597` range additionally carries three
bookkeeping commits already covered by the c21 panel and out of scope here). Confirmed the fix
touches exactly the six files the dispatch named: `git diff --stat a0ff125..6752597` →
`.claude/agents/harness-{security,ui}-reviewer.md`, `.omp/agents/harness-{security,ui}-reviewer.md`,
`.claude/skills/harness/bin/test-validate-digest.py`, `.harness/harness/docs/SPEC.md` — 148
insertions, 5 deletions.

**Tool caveat, immediate:** the `read`/`grep` tool served a STALE cached copy of
`validate-digest.py` on my first pass (1068 lines, `SEV` still `["info",...]`, zero `severity_max`
matches) that contradicted `bash sed`/`grep` on the identical path (1505 lines, `SEV` correctly
`["none",...]`, multiple matches). Reported via `xd://report_issue`. Every claim below is a `bash`
result, none from the stale layer.

## Item 1 — the fix, verified live

`grep -n 'severity_max:' <all six agent files>` — all six instructed lines byte-match:
`severity_max: none|low|med|high|critical|n/a` (`.claude/agents/harness-code-reviewer.md:84`,
`.claude/agents/harness-security-reviewer.md:93`, `.claude/agents/harness-ui-reviewer.md:103`, and
the `.omp` twins at the same three line numbers).

`validate-digest.py:36` (re-located, not trusted from the receipt): `SEV = ["none", "low", "med",
"high", "critical"]`. Binding at `validate-digest.py:194`: `"reviewer": {"severity_max":
set(SEV), "findings": int, "must_fix": list}`.

`python3 .claude/skills/harness/bin/sync-agent-adapters.py --check` → `EXIT=0`.

**`n/a` legitimacy — derived from source, then probed live.** `severity_max` is a member of
`NULLABLE` (`validate-digest.py:58`), and `harness_yaml.PLACEHOLDER_UNSET = ("none", "null",
"n/a")` (`harness_yaml.py:440`) — so `n/a` is the DEC-173 placeholder spelling for "declined",
distinct from `"none"`, which is a real `SEV` member meaning "found nothing." Confirmed against
the real validator, three scratch digests under `/tmp/feat43_c23_review/`, persona
`harness-security-reviewer`:
- `severity_max: n/a` → `digest ok`, `EXIT=0`
- `severity_max: none` (the new template value) → `digest ok`, `EXIT=0`
- `severity_max: info` (the stale pre-fix value) → `VERDICT: BLOCKED (contract violation) —
  severity_max='info' is not in ['critical', 'high', 'low', 'med', 'none'].`, `EXIT=1`

The fix is real, complete, and the `n/a`/`none` dual-vocabulary in the template line is not
redundant or confused — it is two distinct, both-legitimate mechanisms (enum member vs. NULLABLE
placeholder) correctly rendered as one `|`-joined line.

## Item 3 — the `harness-validator-lead.md:102` residual, verified ungated

Re-located (not trusted from the receipt): `.claude/agents/harness-validator-lead.md:102` and
`.omp/agents/harness-validator-lead.md:106` both still read `severity_max: info|low|med|high|critical`
inside "Add to the DIGEST: ...". `validate-digest.py`'s `"lead"` schema (line 207) is `{"team":
str, "steps_run": int, "cycles_used": int, "members": list, "must_fix": list, "branch": str,
"escalations": list, "sc_status": list}` — no `severity_max` key, and the field-validation loop
(`for field, allowed in all_fields.items()`, where `all_fields = {**schema, **UNIVERSAL}`) only
ever inspects keys present in `all_fields`; anything else in the parsed digest is never visited.

**Live probe, not just source-reading:** built a full, otherwise-valid `harness-validator-lead`
digest at `/tmp/feat43_c23_review/digest_lead_info.md` (`steps_run: 0`, `members: []`, all
required fields present) carrying `severity_max: info`. `validate-digest.py harness-validator-lead
<file>` → `digest ok`, `EXIT=0`. The identical digest with the `severity_max` line removed
entirely also → `digest ok`, `EXIT=0`. **The claim is TRUE: a lead digest carrying `severity_max:
info` is accepted, not rejected.** This is not a `must_fix` — it changes nothing observable.

**Is the backlog disposition sound?** Yes. The line is pure narrative guidance the lead template
asks for but the schema never validates (and never has — `adequacy_notes`, named in the same
sentence, is equally unvalidated). Editing it this cycle would also have meant touching
`harness-validator-lead.md`, which the eng-lead explicitly scoped out this cycle (confirmed by the
c22 receipt: "No edit made to harness-validator-lead.md:102 per the eng-lead's scope ruling —
measured, not touched").

**Should the guard have covered lead templates too? A reasoned yes-but-not-here.** `SPEC.md:1139`
states the very principle this fix restores: "enums may not drift per persona." The lead line is
now the one surviving instance of exactly the drift this cycle exists to close, and it is cheap to
add — `run_reviewer_severity_enum_cases`'s discovery/report helpers are already generic over path
and expected-set; a `lead` variant would need only a different expected-path list and a schema
lookup that tolerates "not gated, checked anyway." But extending the guard to a field the
validator does not enforce is a different assertion (prose consistency, not contract drift), and
doing it inside this delta would have meant editing the very file this cycle was ordered not to
touch, to satisfy a guard whose failure gates nothing. I score this `low`, non-blocking, and
recommend it as a follow-up line item — not a defect in this delta.

**Is "unknown keys ignored" a fail-open shape of its own, or bounded design?** Bounded and
deliberate, confirmed from source: the file documents this explicitly for the sibling
`"orchestrator"` schema at `validate-digest.py:217-219` ("a return still carrying [the removed
field] is IGNORED rather than rejected — unknown keys are ignored (measured). Said here so the
next reader does not re-add it 'to be safe'") — the same field-iteration mechanism governs every
schema including `lead`. It is bounded here specifically: `lead`'s one truly consequential
invariant — `VERDICT` must equal the worst member `VERDICT` — is enforced by separate, unconditional
arithmetic (the "LEAD ROLL-UP" block, `validate-digest.py` ~718 onward) that does not depend on
which extra keys a digest carries, and every field the `lead` schema DOES declare (`must_fix`,
`members`, etc.) is still fully validated by the same loop. No smuggling path from an ignored key
to a flipped `VERDICT` exists. Not a finding.

## Confirmation run — `code-grade.py --base 7ccfae8d --head 6752597`

```
$ python3 .claude/skills/harness/bin/code-grade.py --base 7ccfae8d --head 6752597
EXIT=0
```
Independently counted from the captured output: 186 `FUNCTION` records total, `PASSING: 172`
(the tool's own printed total), `RESULT: FAIL` × 14, all 14 carry `SEVERITY: med` (grade-2, never
blocking), zero `SEVERITY: high` or `SEVERITY: critical` anywhere in the output. **This CONFIRMS
the orchestrator's claim exactly: exit 0, 186 gated, zero blocking below-bar, 14 grade-2.** The
delta did not disturb what the c21 panel closed.

## Code quality — `test-validate-digest.py`'s new guard (the only Python in the delta)

`run_reviewer_severity_enum_cases` and its five helpers, read in full against
`a0ff125..6752597`. Live run: `python3 .claude/skills/harness/bin/test-validate-digest.py` →
`18/18 reviewer severity_max enum checks passed.`, `ALL PASSED.`, `EXIT=0`.

- **The expected-template floor is derived from a hardcoded persona tuple, not from the
  validator, and the docstring says so on purpose.** `_EXPECTED_REVIEWER_PERSONAS = ("code",
  "security", "ui")` is a literal, but `_reviewer_template_paths` (the actual discovery) is
  mechanical, walking both `agents/` directories and matching via `validator.norm()`/`ALIAS` — so
  a real fourth reviewer persona is still discovered and checked; the floor only asserts "at least
  these three," never "exactly these three." This is the correct shape for a floor and is stated
  as such in the comment at the tuple's definition — verified by reading, not asserted from the
  receipt.
- **The zero-coverage fail-open from cycle 1 is closed and I can see why.** `checked` is seeded
  from `len(_expected_reviewer_template_paths())` (6) before any discovery runs, so a totally
  broken discovery seam (empty `agents_dir`, or a `norm()`/`ALIAS` regression) now reports `0/6`
  passed with six named `FAIL  ... expected reviewer template missing: <path>` lines rather than
  `0/0` — the exact shape that let cycle 1's regex bug ship silently. Both discovery seams (regex,
  persona-match) are asserted by name per the c22 receipt's own live before/after captures, which
  I did not re-run myself (the sibling QA agent owns mutation testing per this dispatch's
  constraints) but whose logic I traced by reading: `_report_missing_templates` and
  `_report_template_has_lines` each print the offending path unconditionally on failure.
- **Error messages name the offending file in all three failure branches** —
  `_report_missing_templates` (`expected_path`), `_report_template_has_lines` (`path`),
  `_report_severity_drift` (`path`, plus which values are only-template vs only-validator). No
  aggregate-only failure message anywhere in this guard.
- **Finding (`low`, non-blocking):** `_SEVERITY_LINE_RE` requires the instruction line to end
  immediately after the last alternative (`\s*$`) — a legitimate future edit that appends an
  inline comment to the `severity_max:` line itself (rather than the line below it, which is
  where all six current templates place it — confirmed by reading
  `.claude/agents/harness-security-reviewer.md:93-95`) would make the regex match nothing on that
  file, and `_report_template_has_lines` would FAIL it as "no severity_max line found" — a false
  alarm on an equivalent template, not a missed drift. Fails loud, not silently, so it is a
  maintainability nit rather than a defect; not gating.
- No fail-open branch found: every exception path either propagates (unhandled `Exception` types
  during `os.listdir`/`open`, which crash the suite loudly) or is turned into a named, counted
  `FAIL`. No branch returns a passing count on discovering nothing.

## What I did NOT cover

- The four cycle-13 blockers (CR-01/CR-02/SEC-01/UI-01) — out of scope per dispatch, CLOSED by
  the c21 panel.
- `validate-digest.py` itself — not refactored, not reviewed as new work (it is unchanged by this
  delta; I read it only to re-locate line numbers and confirm binding).
- The five focused suites and the guard's own mutation-tested discovery seams — owned by the
  sibling `harness-qa` agent this cycle per the dispatch; I traced the guard's logic by reading
  and ran it once (`18/18`, `EXIT=0`) but did not break its seams myself.
- The canonical suite and `check-state.sh` — the orchestrator's job after this cycle, per
  constraints.
- `Item 2` in the dispatch's own numbering does not exist (items are labeled 1 and 3 in the
  dispatch); nothing was skipped as a result — both named items are answered above.

## Tree state

All scratch files under `/tmp/feat43_c23_review/`. No repo file was written or mutated by this
review.

```
$ git status --porcelain
 M .harness/harness/features/FEAT-43-code-risk-grading/feature.json
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-validate-enumfix-c22-eng.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-documentor-validate-goalcheck-c21-product.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/research-goalcheck-c21.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/uat-sc11-c21.md
?? .harness/harness/features/FEAT-43-code-risk-grading/observations/harness-backend-dev.md
?? .harness/harness/features/FEAT-43-code-risk-grading/observations/harness-documentor.md
```
Identical to the state observed at the start of this run (pre-existing bookkeeping from sibling
agents' prior cycles, none of it mine); the only new file this run adds is this artifact.

```yaml
VERDICT: PASS
DIGEST:
  headline: Enum fix verified correct and complete by live probe (all 6 templates byte-match SEV, n/a and none both legal, old info now rejected exit 1); validator-lead residual independently confirmed ungated (lead digest with severity_max:info accepts exit 0) and its backlog disposition is sound; code-grade.py confirms 186 gated / 0 blocking / 14 grade-2 exactly; new guard has no fail-open branch, one low non-blocking brittleness nit
  findings: 2
  must_fix: []
  severity_max: low
  spec_violations: []
  reviewed: "a0ff125caeb571e49a3bff86c3802cab9b596127..6752597830ee62b91ed34c79be3306dab149c0b6"
  human_commits_in_scope: []
  open_questions:
    - { id: Q1, question: "Should run_reviewer_severity_enum_cases be extended to also check harness-validator-lead.md's (ungated) severity_max vocabulary line, given SPEC.md:1139 states enums may not drift per persona? Reasoned answer: worth doing as a follow-up (cheap, closes the one surviving instance of this drift class), but out of THIS delta's scope since it would require touching a file the eng-lead explicitly ruled untouched this cycle.", blocking: false }
  files_touched: [.harness/harness/features/FEAT-43-code-risk-grading/notes/review-harness-code-reviewer-validate-delta-c23.md]
  expertise_update: []
artifact: .harness/harness/features/FEAT-43-code-risk-grading/notes/review-harness-code-reviewer-validate-delta-c23.md
```
