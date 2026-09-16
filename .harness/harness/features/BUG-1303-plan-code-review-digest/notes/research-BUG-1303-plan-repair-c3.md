# Plan repair c3 — all three open panel findings resolved in the plan text

**BLUF: `panel.findings` now carries ZERO `disposition: open`.** The three lows/infos from panel c2
were fixed by the panel's own remedies — two edits inside T-01's intent, one inside T-04's intent —
and nothing else in the plan moved. `approval.status` is still `pending` with no sibling key; no
`--overrule` was used or needed. All writes went through `plan-merge.py amend` (compare-and-swap on
the field sha) and `plan-merge.py set-panel`.

## What changed, with pointers

| finding | remedy | where |
|---|---|---|
| `PF-9c43910b2d2e6e14595b28a0c264a7f9` (A-6, low) | T-04's decision entry must scope "checked mechanically" to SCHEMAS **plus** the reviewer's inline `code_grade`/`reviewed` extension, and must NAME `required_by_persona` in `run_documented_contract_cases` as the hand-written mirror any future inline extension must update | `plan.yaml:555-563` |
| `PF-87f1837ea32b6a51a980a10d527431fc` (S-4, low) | step (4): an entry PRESENT but with an EMPTY source list takes the unmapped-persona branch and is reported by name, never a zero-iteration silent pass; step (7b) gained a sixth assertion demonstrating that direction | `plan.yaml:256-259`, `plan.yaml:343-346` |
| `PF-49abc17456e3e70e647d1f831bf115d3` (A-7, info) | step (3) maps the nine agent-file personas to the canonical `.omp/agents/<persona>.md` only; the `.claude` duplicates are dropped, with D-07 and `sync-agent-adapters.py --check` stated as the reason | `plan.yaml:234-243` |

Dispositions and `resolved_by:` are at `plan.yaml:156-176` (A-6 → T-04, S-4 → T-01, A-7 → T-01).
`panel.last_run`, `panel.cycle`, every `severity`, `reader` and `summary` are untouched; `set-panel`
re-emitted the block from the file's own parsed value with only the three dispositions flipped.

## The (7b) ok-line call — cheaper option taken, deliberately

**The greped literal is unchanged.** Under the new rule an empty mapping *is* an unmapped persona,
so `ok    [documented contract completeness] unmapped persona, absent source, unlocatable block and
out-of-block field each reported by name` still reads truthfully over six assertions. T-01's
`verify:` therefore needed no edit, and literal identity holds: the intent's quoted line
(`plan.yaml:355`) and the string T-01's verify greps (`plan.yaml:192`) are byte-identical —
re-checked programmatically after the amend, not by eye. A short note under the quoted line
(`plan.yaml:356-358`) tells the executor the line must stay byte-identical and why.

## Bounds honoured (each checked, not assumed)

- **T-01 step (6) did not shrink** — the three reviewer sources incl. both agent copies are intact;
  the intent now says so explicitly (`plan.yaml:241`).
- **The seven SKILL.md-documented personas are unchanged** (`plan.yaml:243-246`): there is no
  `.omp/skills/` tree, so D-07's canonicality argument does not reach them. Stated in the intent so
  a later reader does not "finish the job".
- **T-02's `verify:` untouched** — still names `.claude/agents/harness-code-reviewer.md` and
  `.omp/agents/harness-code-reviewer.md` five times each (presence of the corrected fragment in each,
  absence of the stale one in each, plus the body-identity check). Run VERBATIM from plan.yaml at the
  worktree root: **rc 1**, short-circuiting at conjunct 2, `grep -qF "code_grade: pass|fail|grade_2|n_a"
  .claude/agents/harness-code-reviewer.md` — the field T-02 has not yet written. Conjunct 1
  (`sync --check`) is rc 0; both stale-path absence conjuncts are rc 1, i.e. the old path is still
  there pre-fix. It discriminates.
- **REQ-03/SC-04 intact** — no task's `files:` names `.claude/skills/harness/bin/validate-digest.py`
  (checked over all four tasks); T-01's intent still forbids editing it. Nothing found in this repair
  disturbs the zero-validator-change conclusion.
- `check-plan-routes.py <plan>` → `0 violation(s) across 1 plan(s)`. The one `DEVIATION` line is
  T-01's expected DEC-174 carve-out and does not gate.
- Working tree shows no modified tracked file; only the untracked feature directory.

## Open questions

- None blocking. Advisory: dropping the `.claude` copies from `CONTRACT_SOURCES` makes the guard
  depend on `sync-agent-adapters.py --check` continuing to run in `check-omp-port.py` for the
  generated copies. That gate exists today at `check-omp-port.py:156-166` (rc 0); if it were ever
  removed, step (3) would need the `.claude` mappings back. Worth a line in T-04's entry only if the
  panel asks — not added, to keep the remedy at its smallest compliant size.
