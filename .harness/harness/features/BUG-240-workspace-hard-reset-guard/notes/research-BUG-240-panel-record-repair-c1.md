# Panel record repair — BUG-240 — cycle 1

**The panel record now survives INV-32.** `plan.yaml`'s `panel:` was rewritten through
`plan-merge.py set-panel` (the only write route): reader entries are keyed `reader:` instead of the
INV-32-invisible `step:`, the goalcheck reader is recorded, and the goal-check's five findings are
transcribed. Nothing outside `panel:` changed. Not committed, not staged.

## Readers — three, all `status: ran`

| reader | persona | artifact |
|---|---|---|
| `should-not-exist` | `fable-advisor` | validator digest, cycle 0 |
| `scope` | `harness-code-reviewer` | validator digest, cycle 0 |
| `goalcheck` | `harness-pm` | `notes/research-BUG-240-workspace-hard-reset-guard-goalcheck-plan-c0.md` |

INV-32 (`check-state.sh:534-553`) indexes `item.get("reader")` and demands all three with status
`ran`/`skipped`; the previous `step:`-keyed pair read as *two* unrecorded readers plus a missing
third — three REFUSAL-class lines the instant the operator signs. It grades approved plans only, so
nothing fired while `approval.status: pending`.

## Findings — 10 total (5 carried, 5 added)

The five carried entries were re-emitted programmatically (`yaml.safe_load` → dump), so severity,
reader, summary bytes, disposition and `resolved_by` are unchanged and their ids still hash. The two
`open` ones are untouched: `PF-d795aab03bf4a49e7ef3ef6614024cdf` (case 7's source-text scan) and
`PF-ff733189ddbdfca901c0d587800cb8c4` (D-01's containment premise), both `low`, neither with a
`resolved_by`. No severity or disposition was re-adjudicated. D-01's negative half stays covered by
`PF-ff733189…`; no sixth finding was minted for it.

New — all `reader: goalcheck`, all `disposition: resolved`, severity as the goal-check itself stated
it (`unrated` where it stated none; INV-32:527-528 exempts `resolved` from the severity check):

| # | id | severity | resolved_by | subject |
|---|---|---|---|---|
| G1 | `PF-431ac7611df9e9f693cc55960324e0e9` | critical | T-01 | `os.environ`-exactly-once is false at 6d969ed (3×), so BOTH verify chains were unsatisfiable |
| G2 | `PF-96c11e8a1933bb7957d176eba16621bf` | unrated | T-01 | case 5 reddens on `_control_plane_root` absence, so REQ-01's discrimination is unproven |
| G3 | `PF-7bec78635ffb233ec6a99618f15cde1d` | unrated | T-01 | no assertion of SC-04's `fetch → checkout → reset --hard` ordering |
| G4 | `PF-33f44e35ac81b9c0007e93eadec4716e` | unrated | T-01 | case 5's repo-name override cannot come from `good_fleet_dict`/`run_main` |
| G5 | `PF-b7504dbc772ba8f0c0111aadae5c80dd` | unrated | *(none)* | intake's stale `workspace_path` range (399-404, actually 394-399), corrected in `notes/intake-BUG-240.md` |

## Evidence, taken after the write

```
2026-09-07-01-validator 0 ['goalcheck', 'scope', 'should-not-exist'] ['ran'] 10 ['open', 'resolved']
```

Every id re-derived from its own recorded `reader` + `summary` through
`panel_findings.py id` — **10 of 10 MATCH, 0 mismatches** (`/tmp/bug240_panel_verify.py`), which is
what proves the safe_dump line-wrapping of the carried summaries round-trips to the same bytes.
`open findings: [('PF-d795aab03bf4a49e7ef3ef6614024cdf', 'low', 'none'),
('PF-ff733189ddbdfca901c0d587800cb8c4', 'low', 'none')]`.

**The dispatched `git diff` proof is void, and here is its substitute.** `plan.yaml` is UNTRACKED in
this worktree (`git status --porcelain` → `?? …/plan.yaml`; `git ls-files --error-unmatch` fails), so
`git diff` prints nothing whether or not a non-panel key moved — it cannot fail. Substitute, run on
this exact file (`/tmp/bug240_locality_probe.py`): the panel block occupies lines 32-129 of 393; a
copy re-spliced with a deliberately different panel produced `replace old lines 33-129 -> INSIDE
panel`, `hunks outside the panel block: 0`. `set-panel` splices only the located top-level range
(`plan-merge.py:1052-1055`) and refuses if the result does not reload as the value supplied
(`:1063-1065`). Post-write load confirms the neighbours: keys `schema feature approval status
source_issues lanes decisions panel tasks`, `tasks: [T-01, T-02]`, `decisions: [D-01]`,
`approval: {status: pending}`.

## Open questions

- None blocking. Advisory for the operator's signature: with `approval.status: pending` INV-32 is
  inert, so a mis-keyed panel is undetectable until the moment of signing — the check has no
  pre-approval dry run. Raised as a harness observation, not a plan change.
