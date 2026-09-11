# Panel record — cycle 2 transcribed into plan.yaml

**Done. `panel:` now carries the cycle-2 record with all six findings across three cycles: two
`info` open, two `low` open, two `high` resolved by T-02.** Cycle 0's id reproduced EXACTLY
(`PF-2242299b369215b13ad577fe4279d52e`) from the landed wording, so no operator ruling is orphaned.
`approval:` and all three task `intent:`/`verify:` blocks are byte-unchanged.

Landed block: `plan.yaml:40-103`. Written through `plan-merge.py set-panel --value-file` only; no
editor, no other key.

## `plan-merge.py` stdout, verbatim

```
PANEL cycle 2 -> /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-285-yaml-loader-pin/.harness/harness/features/BUG-285-yaml-loader-pin/plan.yaml
APPLIED /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-285-yaml-loader-pin/.harness/harness/features/BUG-285-yaml-loader-pin/plan.yaml
```

## The six findings

Identity per `panel_findings.py:29-33` — `PF-` + first 32 hex of
sha256(reader + `\n` + lowercase/whitespace-collapsed/stripped summary), computed by the helper's
own CLI, never typed.

| id | origin | reader | severity | disposition |
|---|---|---|---|---|
| `PF-2242299b369215b13ad577fe4279d52e` | cycle 0 | `should-not-exist` | info | open |
| `PF-cceab610738069ec6ea1a56ddc058195` | cycle 1 F3 | `should-not-exist` | info | open |
| `PF-142f3a51c0d0152899db48cf7cbdfe31` | cycle 2 L1 | `should-not-exist` | low | open |
| `PF-a5b9a3c81ee99295515d75f5a776ebae` | cycle 2 L2 | `should-not-exist` | low | open |
| `PF-573413a9f130ec9517e24f31b7a5bf68` | cycle 1 F1 | `scope` | high | resolved, `T-02` |
| `PF-1e2dcbc0764691e922d15d780e6c7e06` | cycle 1 F2 | `should-not-exist` | high | resolved, `T-02` |

Exact hashed summary strings are in the landed block (`plan.yaml:51-103`) and repeated in the DIGEST.

**`resolved_by: T-02` is supported by the record, not chosen by me.** The c2 digest states T-02's
`intent:` now decides `except (json.JSONDecodeError, UnicodeDecodeError, OSError)`
(`runs/2026-09-11-02-planpanelc2-validator/digest.md:3-6`), and `scope` re-verified that tuple at
source (`notes/review-harness-code-reviewer-planpanel-c2.md:12-17`). No other task id closes it.

**F1 and F2 carry byte-identical summaries and DIFFERENT readers, so they hash to two distinct ids**
— one defect, two reporters, both preserved. 6 distinct ids for 6 findings; no collapse.

## Transcription, not adjudication — how wording was kept byte-exact

Summaries were **extracted programmatically** from the sources of record (the digests' markdown
finding rows, and `plan.yaml`'s own landed `summary` for cycle 0) rather than retyped, so a typo
cannot mint a new id. Cross-checks, all `True`:

- cycle-0 landed summary == the c2 digest's carried-forward row for it
- c1's F3 row == the c2 digest's carried-forward F3 row
- c1's F1 row == c1's F2 row

Severities are the readers' own, carried verbatim; backticks around the severity token in the
digests' markdown are formatting, so the field holds the bare enum exactly as the landed cycle-0
record did. Nothing re-severitied, nothing resolved by me beyond the closure the c2 digest states,
nothing added, nothing dropped.

## What was verified after the write

- `panel.cycle: 2` (int), `panel.last_run: 2026-09-11-02-planpanelc2-validator` (the run dir name)
- both cycle-2 readers present, both `status: ran`, neither carrying `reason`
- the loaded `panel` mapping equals the value file's loaded mapping (compared as values, not bytes —
  `set-panel` re-emits through `safe_dump`, so wrapping moves where values do not)
- `approval:` byte-identical to `HEAD`'s copy (sha256 of the block `6f59dc09…` both sides); still
  `status: approved` / `2026-09-09`
- per-field shas unchanged across the write: T-01 `intent` `73412a42…`, T-02 `intent` `d52c04e3…`,
  T-03 `intent` `0f16dcb0…` — all three match the previous cycle's record. `verify` too:
  T-01 `7fee1afa…`, T-02 `e3f7e075…`, T-03 `dca60b2a…`
- tempdir value file composed under `/tmp`, never in the repo tree, and removed

## Open — carried up, not resolved here

- **The approval state is still broken and is the operator's.** `plan.yaml` reads
  `approval.status: approved` dated 2026-09-09 over a task set amended three times since, while
  `BRIEF.md` reads `pending`. Left byte-identical on instruction; it is the c1/c2 blocking question
  (c2 digest Q2), not something this write corrects.
- Two `low` findings are open and each has a one-line remedy the c2 digest names (L1: correct the
  sentence in `notes/research-BUG-285-panelfix-c2.md`; L2: weaken SC-11 to "as named checks"). No
  task owns either yet.
