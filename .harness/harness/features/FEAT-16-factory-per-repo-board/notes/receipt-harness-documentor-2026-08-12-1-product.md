# Receipt — harness-documentor — FEAT-16 T-10 — 2026-08-12-1-product

**PASS.** All seven `verify:` conditions pass, run separately. Two amendments appended to
`docs/harness/DECISIONS.md` (DEC-174 am.2, DEC-186 am.1), two index rulings re-authored and the
index regenerated, two SPEC rows restated. Nothing committed — the tree is left dirty for the
commit-pen holder (DEC-153).

## What landed

| File | Change | Diff shape |
|---|---|---|
| `docs/harness/DECISIONS.md` | **append only** — DEC-174 amendment 2 after am.1's OWED paragraph; DEC-186 amendment 1 after its "rejected alternative" paragraph | +43 / −0 |
| `docs/harness/DECISIONS-INDEX.md` | DEC-174 and DEC-186 ruling texts (right of ` :: `) re-authored by hand, then regenerated with the script | +20 / −20 (rulings + `@line` anchors + DEC-186's new `am.1` token) |
| `docs/harness/SPEC.md` | §3.3 table rows for `fleet.yaml` and `factory_config.py`, and nothing else | +2 / −2 |

`git diff --stat` on the three paths: 65 insertions, 22 deletions. No code file touched; none of the
four DEC-174 carve-out scripts appears in the diff.

## The DEC-174 index row after regeneration — am-span reads `am.1-am.2`

```
- DEC-174 @4591 am.1-am.2 [plan,state,cost,domain] refs: DEC-142 DEC-173 :: The harness plans its own work but never EXECUTES changes to its own hooks, validators or gate scripts; am.2 declares the per-repository board and closes am.1's board loose end.
```

The span was **not** hand-written; it is computed from `AMEND_HEADING_RE`
(`.claude/skills/harness/bin/gen-decisions-index.py:25`) and appeared only after regeneration. The
authored ruling survived regeneration verbatim (29 words, under the 30-word cap asserted in
`test-gen-decisions-index.py`). The DEC-186 row now carries `am.1` and no longer says "one board":

```
- DEC-186 @5349 am.1 [plan,github,state,approval] refs: DEC-138 DEC-168 DEC-179 DEC-182 :: GitHub Issues and the per-repository board are the factory's control plane; read-back is bounded to exactly three purposes and never writes an approval-gated artifact.
```

## Verify transcript — each condition run separately, from this checkout

```
=== C1  gen-decisions-index.py --stdout | diff -q - DECISIONS-INDEX.md
(no output)                                                          exit=0
=== C2  grep "DEC-174 amendment 2" DECISIONS.md
4704:### DEC-174 amendment 2 (2026-08-12) — the station board is declared per repository, and am.1's board loose end is closed
                                                                     exit=0
=== C3  grep "per repository served" DECISIONS.md
5425:### DEC-186 amendment 1 (2026-08-12) — one board per repository served, with the three-purpose read-back bound unchanged
5437:ready station option per poll; it becomes one such query per repository served per poll. That scales
                                                                     exit=0
=== C4  grep -E "^- DEC-174 " INDEX | grep -o "per-repository board"
per-repository board                                                 exit=0
=== C5  grep -E "^- DEC-186 " INDEX | grep -o "per-repository board"
per-repository board                                                 exit=0
=== C6  grep "repo_entry. / .station" SPEC.md
(no output)                                        grep exit=1 → negation TRUE
=== C7  grep "the .board:. the factory reads work from" SPEC.md
(no output)                                        grep exit=1 → negation TRUE
=== full conjunction as written in plan.yaml T-10 verify:            exit=0
```

C2–C5 print the matching line rather than `-q`, and each match sits in the section/row it is meant
to (C2 in DEC-174's amendment heading at `:4704`, C3's substantive hit at `:5437` inside DEC-186
am.1's cost paragraph, C4/C5 on their own rows). C3 matched **0 times before this run**.

The `verify:` string in the dispatch was cross-checked against `plan.yaml` T-10 `verify:` (dumped
with `yaml.safe_load`) by reading both — no mismatch. The conjunction above was run from the plan's
own string.

## Regression checks beyond `verify:`

- `test-gen-decisions-index.py` — 9/9 ok, including
  `test_committed_index_is_complete_and_within_budget` (30-word ruling cap, 260-line index budget)
  and `test_committed_index_matches_a_fresh_regeneration`.
- `run-unit-tests.sh` — every suite `PASS`, no `FAIL` line anywhere in the output.

## Content claims and where they were checked, not assumed

- Per-repository board, `load_fleet` **rejects** a leftover top-level `board` key: read at
  `.claude/skills/harness/bin/factory_config.py` — the `if "board" in data:` branch raising
  `FleetError`, and the per-entry `if "board" not in entry:` branch. `board_for` and `board_station`
  exist there; `def station(` returns nothing.
- Board 2 figures (211 items / 118 `Done` / 82 `Backlog` / 11 `Building` / 0 each in `Plan`,
  `Ready`, `Review`) are **cited, not remeasured** — the amendment names
  `notes/board2-capture.md` as their source. The rename-not-recreate claim is the capture's own
  surviving-option-id evidence.
- DEC-186 is **amended, not struck**, on DEC-188's own text ("merely dated, narrowed, or partly
  overtaken" → amended; striking needs the operator's word). Both original ruling clauses are left
  standing; the amendment names each by its opening words rather than by line number.

## Generator traps deliberately avoided

- The heading uses the `### DEC-NNN amendment N (date) — title` form, not the bold-inline
  `**Amendment am.N` form, which `AMEND_BOLD_RE` would have counted as a third amendment.
- No line in either amendment begins `**Supersedes/Corrects/Inverts DEC-NN`, which
  `BODY_SUPERSESSION_RE` would have turned into a false `— SUPERSEDED BY` clause on another
  decision's row.
- `per repository served` is written on one physical line; `grep` counts physical lines.

## Open question raised, not acted on

`docs/harness/SPEC.md:425` still says **"Onboarding a repository is one edit: add a
`- name: <owner>/<repo>` entry (with its `default_branch`) under `repos:`"**. That is now false:
`load_fleet` rejects a `repos[]` entry that declares no `board:` of its own, so onboarding requires
the board block too. T-10's intent bounds this task to two table rows and forbids other prose
changes in SPEC.md, so it is flagged here rather than fixed. It is a live stale-doc contradiction of
the kind DEC-188 exists to prevent, and nothing in the tree detects it.
