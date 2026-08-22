# SIMPLIFICATION angle — FEAT-31, d065b3b..HEAD

**BLUF: 0 findings. Nothing material. This is a genuine empty pass, not an unexamined one.**

## What I read

`.claude/skills/harness/bin/context-watch.py` (full 779-line diff, new file), `context-watch-hook.py`,
`verify-context-watch-live.py`, `feature_schema.py`'s new `RUNS_AGENT_EXEMPT` block, `run-unit-tests.sh`'s
kind-drift addition, and the `DECISIONS.md`/`DECISIONS-INDEX.md` diffs for DEC-159's amendment and the new
DEC-198 entry.

## What I looked for and ruled out

- **Pervasive `T-NN`/`D-NN`/`DEC-NN` comment citations throughout `context-watch.py`** (e.g. `# T-06:`,
  `# Seam 4 (T-16):`, inline `(D-24)`, `(D-08)`) looked at first read like narrated-change comments
  rather than present-fact ones. Checked against `plan.yaml` and `DECISIONS-INDEX.md`: every cited id
  resolves to a real, still-live decision or task, and each comment states a present constraint
  ("keep it deep and narrow (D-24)") rather than a changelog entry. This matches the codebase's
  existing citation convention elsewhere (`DECISIONS.md`, `check-state.sh`). Not a finding.
- **The two-line `at_or_above_threshold = False; at_or_above_threshold = ...` seams** in `format_rows`
  and `warn_for_agent` — explicitly named as deliberate mutant anchors in the dispatch. Skipped.
- **Duplicated directory-walk logic** between `discover_orchestrator_rows` and
  `_orchestrator_jsonl_paths` (context-watch.py:~300 and ~600) — real duplication, but it reads as a
  REUSE-angle finding (restated walk where a shared one exists), not a SIMPLIFICATION one, so I left
  it for that reader rather than double-file it.
- **`verify-context-watch-live.py`'s from-scratch reimplementation** of
  `_three_field_sum`/`entry_context_size`/measured-set logic — this is SC-01's required independent
  second opinion (no import from context-watch.py, by design, to avoid comparing a function to
  itself). Anchoring semantics, not redundancy.
- **`feature_schema.py`'s `RUNS_AGENT_EXEMPT` map** — D-23, already settled, not re-litigated.
- **`run-unit-tests.sh`'s inline Python kind-drift heredoc** — verbose but load-bearing (T-12,
  flag-only per dispatch); no simpler equivalent found that preserves the "set comparison with no
  glob classifier" property the comments say was deliberately chosen.
- **DEC-198 / DEC-159 amendment prose** — dense but not duplicative; each paragraph states a distinct
  fact (unit, propagation path, what's tested vs. untested, what remains deferred).

No redundant conjuncts, no dead references to a superseded shape, and no comment I could show narrates
a change instead of stating a present fact.

## Verdict

Zero findings for SIMPLIFICATION. All flag-only/applicable classification is moot since nothing to
route.
