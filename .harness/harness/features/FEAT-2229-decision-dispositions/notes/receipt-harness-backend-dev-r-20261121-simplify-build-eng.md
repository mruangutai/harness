# Receipt — REUSE angle, FEAT-2229 simplify (harness-backend-dev, r-20261121-simplify-build-eng)

BLUF: 2 nonblocking reuse findings, both in `plan_merge/check.py` (apply lane: harness-dev-ops). No source edited; files_touched [].

## Inspected
`git diff dfa52536..6c4da464` over the full source set; read in full the hunks of harness_yaml.py, plan_merge/check.py, union.py, panel.py; harness.json pair; skimmed test fixtures for restated grammar. Compared against bin/ for existing helpers (grep of index-row grammar, ISO parsing, heading/section helpers, fences).

## Findings

### R-1 (medium) DECISIONS-INDEX row grammar and struck rule restated a third time
- `.claude/skills/harness/bin/plan_merge/check.py:198-200` (`INDEX_ROW_RE`) and `:247-251` (`_struck_by_dec`).
- Existing: `check-plan-routes.py:2394-2407` (`_decisions_index`, same regex, same `{DEC: struck?}` shape) and `gen-decisions-index.py:75-86` (`ROW_RE`, whose comment declares it "THE row grammar, single-sourced").
- Cost: three spellings edited in lockstep when the row format changes; one already diverges on the struck rule — check.py lowercases (`Struck under DEC-188` counts struck, check.py:198-199 says so deliberately) while check-plan-routes.py:2406 is case-sensitive `startswith("STRUCK")`. The same index entry can be struck for plan-merge check and live for the route gate; nobody owns the difference.
- Alternative: one importable parser for the index (e.g. a small module under bin/ that gen-decisions-index.py's ROW_RE and both consumers use; the hyphenated scripts are not importable by name, so the shared thing must be a module, not either script) and one struck predicate. Short of that, at least make check-plan-routes' predicate agree. Apply lane: check.py part only by harness-dev-ops; check-plan-routes.py/gen-decisions-index.py are outside the apply lane (flag-only).

### R-2 (low) Aware-ISO-instant parser restated
- `plan_merge/check.py:203-212` (`_instant`): fromisoformat, reject naive, None on failure.
- Existing: `check_state/ctx.py:189-199` (`_iso_instant`): same contract, also normalizes `Z` for pre-3.11 interpreters; docstring states the "refuse naive" rule.
- Cost: two copies of the INV-43-style rule; if the supported Python floor is below 3.11, check.py's copy rejects `Z` stamps (the very form union._creation_instant writes, union.py `%Y-%m-%dT%H:%M:%SZ`) as malformed — a FAIL on every new draft. [INFERENCE] floor not checked.
- Alternative: import `check_state.ctx._iso_instant` (or promote it to a public shared helper) instead of a second copy.

## Skips (examined, not flagged)
- `_heading_level`/`_section_end` (check.py:269-285) vs check-domain.py:495 `_heading_range` and gen-decisions-index.py `defenced_lines`: different keying (DEC-NNN heading prefix, fence-aware) — no importable equivalent fits; not flagged.
- `_successor_fault` exists in both harness_yaml.py and check.py with different semantics (shape vs resolvability); naming only, distinct modules.
- `DEC_ID_RE`/`SUCCESSOR_RE` in harness_yaml.py: single spelling in the diff; check-skill-refs.py DEC_RE has different anchoring.
- union.py/panel.py `DRAFTED_AT` is single-sourced (panel imports from union).
- Settled set (D-01/DEC-254, era gating, factory_config.FINISHED_STATIONS, root-supplied era resolver) not reviewed.
- Prose/tests: no restated grammar found beyond fixtures (test-plan-decision-dispositions.py index rows are literal fixtures).

## No-source-edit status
No source, suite, build or lint run; only this receipt written.
