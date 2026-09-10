# Plan-panel review (scope reader) — FEAT-104 — cycle 1

**BLUF.** The cycle-1 plan is sound. Every claim I could ground-truth against the real source
(`validate-digest.py`, `check-domain.sh`, `feature_schema.py`, `.omp/agents/*.md`,
`harness-team/SKILL.md`, `test-validate-digest.py`) checked out — line anchors, the `raw_persona`
variable D-10 keys `DOCUMENTED_OPTIONAL` on, the `jsonschema`-required fail-closed precedent D-08
cites, the two-space documented-block indentation D-12's reverse parser assumes, all 17 field
citations in `planfix-c1.md`'s re-derivation table. No orphan REQ/SC, no task tracing to nothing,
no dangling `depends_on`, no vacuous grep (all six new literals — `DOCUMENTED_OPTIONAL`,
`undeclared digest key`, `undeclared step key`, `schema_version floor`,
`every documented key is declared`, `pre-change validator` — return 0 hits pre-change, confirmed
myself). T-01 PART 6 / T-08's base-revision pin is genuinely non-vacuous: the pinned blob's
behaviour (ignores unknown keys) really does differ from HEAD's, and the positive/negative grep
pair on the pinned blob prevents a drifted or premature pin from passing silently. Two low-severity
notes below, neither gating.

## Findings

**1 — low — T-01 PART 1's "reuse the existing field loop" instruction is inconsistent with what
that loop actually does; a naive reading reproduces F1's exact defect through a new code path.**
`validate-digest.py:1190` builds `all_fields = {**schema, **UNIVERSAL}` and the loop at `:1197`
(`for field, allowed in all_fields.items(): if field not in seen: err.append("missing ...")`)
treats **every** key of `all_fields` as required-and-missing when absent — there is no
"optional, type-checked-only-when-present" branch anywhere in that loop today. T-01 PART 1 says a
`PASSTHROUGH`/`DOCUMENTED_OPTIONAL` field is "validated exactly as SCHEMAS validates a field of
that type or enum, reusing the existing field loop rather than a second one." Read literally, that
means merging `PASSTHROUGH.get(persona, {})` and `DOCUMENTED_OPTIONAL.get(raw_persona, {})` into
`all_fields` — which would make every one of the 8+16 fields **required**, silently reintroducing
the exact defect goal-check's F1 found (a conforming return omitting an optional field now exits
2). The intent text never states the one adjustment that actually keeps them optional under the
same elif-chain: filter to keys already in `seen` and skip the "field not in seen" branch for
this set. **Why this doesn't ship broken:** T-01 PART 5 explicitly requires "a lead return
OMITTING each PASSTHROUGH key validates" and the equivalent DOCUMENTED_OPTIONAL omission cases —
a naive merge-into-`all_fields` implementation fails those assertions immediately, and T-01's own
`verify:` demands `ALL PASSED`, so the wrong reading cannot land. Recommend tightening the PART 1
prose (e.g. "reuse the same type/enum branches on keys already present; do not add them to the
required-missing sweep") so an implementer doesn't burn a cycle discovering this the hard way.

**2 — low — SC-11's wording, taken on its own in `BRIEF.md`, is falsified by D-11's creation
floor.** SC-11: "A `steps[]` entry carrying an undeclared key is **accepted** when the file
declares `schema_version: 1`… ." D-11/T-06 CLAUSE B now refuses the **creation** of any run
`state.yaml` whose `schema_version` is below 2 — so a brand-new file declaring `schema_version: 1`
is refused regardless of its `steps[]` content, for the floor reason, not the CLAUSE A step-key
reason SC-11 is about. The reconciling qualifier — SC-11's accept case is necessarily an **update
to an already-existing** version-1 file — is stated in D-11's `because:` clause, in T-06's last
CLAUSE B test bullet, and in `planfix-c1.md`'s F3 closure ("SC-11 grades a `steps[]` entry inside
a file that *already declares* version 1"), but not in SC-11 itself. T-06's own intent correctly
disambiguates this for the implementer, so the shipped test suite will almost certainly get it
right; the risk is a future reader (QA, an auditor, an operator) grading SC-11 standalone against
`BRIEF.md` and reading it as satisfiable by a fresh-file fixture, which no longer exists post-D-11.
Recommend adding "on a run already carrying `schema_version: 1`" to SC-11's text.

Both findings are advisory precision notes on the two highest-leverage repairs (D-10's optional
mechanism, D-11's floor/SC-11 interaction) named in this panel's brief; neither is a `must_fix` —
each is self-correcting via the task's own `verify:` gate or is a documentation-only gap in a
criterion whose enforcing test is already specified correctly.

## What I checked and found clean (no finding)

- **D-10 key derivation vs. runtime**: `raw_persona = persona` is set at `validate-digest.py:1135`
  before `norm()`, and every call site (`hook_mode`, the CLI, and every reviewer test helper in
  `test-validate-digest.py`) passes the raw agent-type string (`"harness-code-reviewer"`,
  `"harness-security-reviewer"`, `"harness-ui-reviewer"`, …) — exactly what `DOCUMENTED_OPTIONAL`
  is keyed on. SC-16's reverse-direction parser assumption (documented fields sit at exactly
  two-space indent) holds for every sampled `.omp/agents/*.md` block, including lines carrying
  trailing inline comments.
- **D-11 creation floor vs. concurrency**: the write-payload path already discriminates
  "file does not exist yet" (`prior_state = ""` at `check-domain.sh:~1621`) from "file exists" via
  the same code region CLAUSE B hooks into; the residual risk (a lead dispatched from an
  older preloaded `harness-team/SKILL.md` copy seeding `schema_version: 1` on a brand-new run
  after this lands) is real but already named and accepted in `planfix-c1.md` F3 — the refusal is
  fail-closed with an actionable message naming the seed instruction's path, not a silent break.
- **T-01 PART 6 / SC-06 base-revision pin**: not vacuous. The pinned blob functionally still
  "ignores unknown keys" (T-01 doesn't touch that code), so the same well-formed payload really
  does exit 0 there and 2 at HEAD; the positive+negative grep pair on the pinned blob
  (`DOCUMENTED_OPTIONAL` present, `undeclared digest key` absent) is a genuine two-sided guard
  against a drifted or premature pin, not a single assertion that could pass by coincidence.
- **jsonschema dependency (D-08)**: `feature_schema.py`'s `JSONSCHEMA_AVAILABLE` fallback is
  fail-**closed** (reports "CANNOT be checked" as a violation), confirming D-08's "DEC-190 makes
  it a required dependency" claim and giving T-06 CLAUSE A a correct precedent to copy.
- Traceability (REQ↔SC↔task, `depends_on` DAG) matches `planfix-c1.md`'s tables exactly; I did not
  find a discrepancy independently re-deriving it from `plan.yaml`.
- No scope creep: every task traces to a live REQ; no task exists that no requirement asked for.

```yaml
VERDICT: PASS
DIGEST:
  headline: Plan is sound; two low-severity, non-gating precision notes on D-10's optional-field mechanism and SC-11's wording, both self-correcting via existing verify gates.
  severity_max: low
  findings: 2
  must_fix: []
  spec_violations: []
  code_grade: n_a
  reviewed: "plan:/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-104-strict-digest-schema/.harness/harness/features/FEAT-104-strict-digest-schema/plan.yaml"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-104-strict-digest-schema/.harness/harness/features/FEAT-104-strict-digest-schema/notes/review-harness-code-reviewer-planpanel-c1.md
```
