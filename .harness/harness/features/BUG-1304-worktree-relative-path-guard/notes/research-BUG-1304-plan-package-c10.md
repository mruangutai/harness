# Cycle 10 — signature packaging — BUG-1304

## BLUF

The plan is **signature-ready**. Four targeted edits landed through `plan-merge.py`, panel cycle 3
is recorded with cycles 1 and 2 intact, and the integrity sweep is clean: **no open operator choice
survives in live plan text, no blocking finding remains, no scope was added.** Counts before and
after are identical — 10 tasks, 11 decisions, 7 REQ, 12 SC. `approval.status: pending` in both
files, untouched.

## 1. F-C3-2 — the falsified provenance, corrected in both places

Both replacement sentences, quoted from `plan.yaml` at final state:

- **D-10 `because`, opening:** "THE SHAPE BEGAN AS THE ADVISOR'S REQ-05 PATTERN EXTENDED BY PM AT
  CYCLE 1, AND THE FOURTH BINDING RULING HAS SINCE RULED THE CASE ITSELF."
- **D-10 `because`, closing the same paragraph:** "At cycle 1 no advisor had yet reached the
  registry file itself, so pm extended the existing pattern rather than inventing a rule. The FOURTH
  BINDING RULING (`notes/review-fable-advisor-plan-BUG-1304-f1-binding.md`) SUBSEQUENTLY ruled on
  exactly this case, SELECTED remedy (a), and the operator AUTHORISED that ruling with NO overrules.
  Nothing here is left awaiting a ratify-or-strike at signature."
- **T-07 obligation 1c, closing clause:** "Record the rule and its selected scope as RULED by the
  Advisor's fourth binding ruling (`notes/review-fable-advisor-plan-BUG-1304-f1-binding.md`) and
  AUTHORISED by the operator with no overrules, so a later reader can tell which parts of this entry
  an advisor settled."

Every other paragraph of `because` and every other sentence of 1c is byte-identical: the edits were
produced by a scripted single-occurrence substring replacement over the field read out of the file,
not by retyping (`/tmp/bug1304_c10/mkvalues.py`), and each `amend` carried `--expect-sha256`.
Confirmed at final state: neither field contains `No advisor ruled on the case` or `ratifies or
strikes it at signature`, and 1c's mandated sentence `THE REFUSAL BINDS EXACTLY THE GOVERNED WRITES
THE READABLE ROOTS CANNOT PLACE` survives verbatim (unwrapped).

## 2. F-C3-1 — obligation 1c now has a gate that can fail

One conjunct added, before the final negative, block still a literal `|` scalar, `&&` chain intact:

```
&& grep -qi "readable roots cannot place" .harness/harness/docs/DECISIONS.md \
```

- **Can fail:** `grep -ci "readable roots cannot place" .harness/harness/docs/DECISIONS.md` → **0**
  today (worktree at `c369fb1f`, before T-07 lands).
- **Can pass:** the phrase is the tail of 1c's own mandated sentence, which the task already
  requires verbatim.
- **Case:** `-qi`, the L-03 defect class.
- **Doctrine, not vocabulary:** it asserts the scoped refusal, not the words "unreadable registry".

**Six conjuncts re-checked against today's `DECISIONS.md`, all sound:**

| conjunct | today | reading |
|---|---|---|
| `CLAIM-SET MEMBERSHIP` | 0 | absent — not hollow |
| `the assigned worktree` | 0 | absent — not hollow |
| `OMP_UNVERIFIED_TTL_SECONDS` | 0 | absent — not hollow |
| `inflight_registry.py:30-35` | 0 | absent — not hollow |
| `readable roots cannot place` (new) | 0 | absent — not hollow |
| `! grep -qi "Bash route keeps DEC-153's blanket allow"` | **1** (`DECISIONS.md:5338`) | red pre-change, green only after obligation 3 |

**Advisory, not fixed (would exceed cycle 10):** `grep` is line-bound, so if the doer wraps
`READABLE ROOTS CANNOT / PLACE` across two lines in `DECISIONS.md` the new conjunct goes red on
correct work. That is a *false red*, not a false green — the doer re-wraps and re-runs. The same
exposure already exists for `the assigned worktree` and was accepted at earlier cycles.

## 3. F-C3-3 — resolved in one clause

`T-01` → `test-inflight-registry.py` `live_claims` case 2 now reads: *"a NON-OMP claim (runtime
absent or "claude") past the BINDING horizon is not returned."* No case restructured, renumbered,
merged or deleted; T-01's `verify` untouched. The literal contradiction with case 8 (proven-identity
OMP claim, back-dated past `OMP_UNVERIFIED_TTL_SECONDS`, still returned) is gone; the overlap with
case 7 stands, as the panel judged.

## 4. Panel cycle 3

`set-panel` applied. `cycle: 3`, `last_run: 2026-09-05-09-validator`. Both readers `ran` / `PASS`;
`fable-advisor`'s **return-shape deviation** (JSON object with extra top-level keys instead of one
fenced YAML mapping — parseable, every finding rated, `on_fail` did not fire) is recorded as fact
beside the PASS. Three new findings, ids computed with `panel_findings.py id` over the summaries as
transcribed: `F-C3-1` `PF-976e37a6…` med, `F-C3-2` `PF-38710650…` low, `F-C3-3` `PF-6c5cdabd…` info
— **all three `resolved` by this pass.** `attribution_note` records that F-C3-2 and F-C3-3 appear in
no reviewer artifact and the advisor returned none, and that F-C3-3's sharper contradiction reading
is the validator lead's assessment. `cycle_3_verification` records the headline: all nine
`required_plan_repairs` independently verified APPLIED FAITHFULLY **at source**.

**Additive-only proof, machine-checked before the merge** (`/tmp/bug1304_c10/mkpanel.py` asserts):
all 10 prior findings present and **byte-equal** (`changed: []`), cycle-1 `history` entry unchanged,
cycle-2 `readers` moved into `history` unchanged, `transcription_rule` /
`cycle_2_verification` / `cycle_2_disposition_update` unchanged, **added keys:
`['cycle_3_verification']`, removed keys: `[]`**. F1 `resolved`, F2 `separate_issue_required` —
neither reopened. 13 findings total; history cycles `[1, 2]`.

## 5. Integrity sweep

- `yaml.safe_load(plan.yaml)` — **succeeds**.
- 10/10 tasks carry a plain-string `files:` list, a runnable multi-line literal `verify:`,
  `execution_mode: main-session-direct`, `traces:` and `change_type:`.
- `check-plan-routes.py <plan>` → **0 violations, exit 0**. The 10 `DEVIATION` lines are the
  expected DEC-174 carve-out.
- Placeholders (`TBD`, `TODO`, `XXX`, `<...>`) in `plan.yaml` and `BRIEF.md`: **zero**.
- `approval.status: pending` in both files.
- **Open-choice grep, 7 phrases, 7 hits, all adjudicated as fine:**
  - `plan.yaml:141` `ratified at signature` — inside `panel.findings[L-01].resolution`, frozen
    cycle-1 history describing what D-10 said then. **Knowingly left**, per the dispatch.
  - `plan.yaml:366-367` `No advisor ruled` / `ratifies or strikes` — F-C3-2's own summary, which the
    `transcription_rule` requires be transcribed unaltered (the id is computed over it).
  - `plan.yaml:378`, `:620` `pick between` — both are the *negation* ("Nothing about the
    unreadable-registry rule is left for the operator to pick between").
  - `plan.yaml:547` `left open` — D-10's "IS SELECTED, not left open".
  - `plan.yaml:1546` `open question` — T-09's "no part of it is an open question".
  - **No live plan sentence presents a question as the operator's to pick between.**

## Open questions

None. Nothing found needing more than a sentence beyond the advisory in section 2.
