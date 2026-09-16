# ALTITUDE — BUG-1303 simplify pass (harness-ai-dev)

**BLUF:** One real altitude gap, and it is exactly the one DEC-216 already names as a residual: the
`SCHEMAS` reviewer extension in `validate-digest.py` and its hand-written mirror in
`test-validate-digest.py` have no compensating *control*, only a doctrine comment — and the deeper
fix (expose the merged schema as an importable function) reopens SC-04's byte-unchanged boundary, so
it is a `briefing-row`, not an apply. Every other lead checks out as correctly separated. Report-only;
no file in the diff was touched (verified below).

## Findings

**F1 — `_required_contracts`'s hand-mirror of the reviewer schema extension has no compensating control.**
`tests/integration/test-validate-digest.py:385-391` reconstructs `validate-digest.py`'s
`harness-code-reviewer` schema extension by hand (`required["harness-code-reviewer"].update(("code_grade",
"reviewed"))`), duplicating the literal extension applied in code at
`.claude/skills/harness/bin/validate-digest.py:1140-1147` (`if raw_persona == "harness-code-reviewer":
schema = {**schema, "code_grade": ..., "reviewed": str}`). DEC-216 (`.harness/harness/docs/DECISIONS.md:6803-6809`)
correctly *names* this as the residual and states the hazard ("a future inline extension must update
that site or the guard silently under-checks the persona it extends") — but names no automated control
that fires when the two go out of sync, only a warning comment for the next editor. Concrete cost: a
third persona-specific field added to `SCHEMAS` inline in `validate()` ships with zero enforcement that
the persona's documented output was ever updated to mention it, and nothing turns red — the same silent
divergence DEC-216 exists to fix, reopened one field at a time. Deeper fix: `validate-digest.py` expose
the merged per-persona required-field set as a function (e.g. `required_fields(persona)`) the test
imports and calls, retiring the hand-mirror entirely — but that edits `validate-digest.py`, which SC-04
holds byte-unchanged for this feature. That reopens a settled boundary; it is not this pass's to take.
**Severity: med. Recommendation: briefing-row** — flag for the next feature that is allowed to touch
`validate-digest.py`; today's mirror is an acceptable stopgap, not a fixed one.

## Leads, answered

- **`CONTRACT_SOURCES` vs. `documented_block`'s shape logic:** holds. `CONTRACT_SOURCES` (`test-validate-digest.py:297-314`)
  is pure persona→path data; the only `source_path.endswith("SKILL.md")` branch in the file is inside
  `documented_block` (line 284), confirmed by grep as the sole occurrence. The map carries no shape
  knowledge. **Leave.**
- **`_required_contracts` mirror + DEC-216's residual:** see F1 above. **Briefing-row.**
- **`_reviewer_plan_mode_results`'s hard-coded 3 paths / 3 token checks — right home?** Yes. It checks a
  different assertion *shape* (literal substring/regex tokens for the DEC-207 plan-mode convention)
  than `documented_contract_results` (field-starts-a-line gap detection), so it is not a check
  "bolted onto a caller" that duplicates an existing shared mechanism — it is a distinct, narrow
  assertion living beside its sibling in the same test module, and it already reuses the validator's
  own `_PLAN_REVIEW_PREFIX` constant (`validate-digest.py:977`) rather than re-spelling `"plan:"`
  (`test-validate-digest.py:400`). No shared home exists elsewhere for this specific check today.
  **Leave.**
- **Three plan-mode prose surfaces — one authority or three peers?** Only two are *authored*: the
  `.omp/agents/harness-code-reviewer.md` template (terse inline comment, line 93) and
  `.claude/skills/harness-code-review/SKILL.md` (full procedural section, lines 163-189). Verified in
  the worktree: `.claude/agents/harness-code-reviewer.md` is mechanically generated from the `.omp`
  source by `sync-agent-adapters.py` (confirmed `claude_adapter()` in that script), and a line-by-line
  diff of both files' bodies past frontmatter is byte-identical — so it is a derivation, not a third
  peer. The template states the copy-paste syntax once; the SKILL.md section is the "why/when"
  procedure that also reproduces the syntax for teaching, and `_reviewer_plan_mode_results` mechanically
  binds all three texts to the same token, so drift between the authored pair would fail the suite.
  Right altitude. **Leave.**
- **DEC-216 / DECISIONS-INDEX.md row — right level or implementation detail?** Consistent with this
  log's own house style: neighboring entries (DEC-209, DEC-213, DEC-215) also cite concrete function
  and file names as the evidence for their ruling, not as an ongoing prescriptive contract. DEC-216's
  identifiers (`SCHEMAS`, `required_by_persona`, `run_documented_contract_cases`) could go stale as
  *citations* if renamed later, but the ruling itself ("documented output must carry every field the
  schema requires, checked mechanically") does not depend on those names. The index row is a compliant
  one-line summary + refs, matching every other row. **Leave.**

## Non-goal noted, not developed

`validate-digest.py` is the deeper home for F1's fix and for exposing `_PLAN_REVIEW_PREFIX`-style
constants more broadly — it is byte-unchanged by SC-04 in this diff, so both are named above as
briefing-rows only, per the assignment's non-goals.

## Verification

No file in the diff was edited. `git status --porcelain` at the end of this run:

```
 M .harness/harness/features/BUG-1303-plan-code-review-digest/feature.json
 M .harness/harness/features/BUG-1303-plan-code-review-digest/plan.yaml
?? .harness/harness/features/BUG-1303-plan-code-review-digest/notes/receipt-harness-dev-ops-simplify-efficiency.md
```

Neither modified path nor the untracked sibling receipt is a file this angle touched; both are
concurrent siblings' / orchestrator's writes, not mine. No entry in this diff (`63404ef0..b724a0f4`)
appears in this status output.
