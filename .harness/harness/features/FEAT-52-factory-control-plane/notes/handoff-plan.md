# Handoff — FEAT-52-factory-control-plane, plan → signature — written at 8ff525e2, seq-4

## Next

Do NOT dispatch a build segment, do NOT re-run the panel, do NOT re-open the findings — the
Advisor disposed of all 17 and its batch is applied. The signature is TWO acts, both the main
session's: (1) `BRIEF.md` `## Approval` (:209-213) → `status: approved`, `approved-by`, `date`;
it is check-state.sh's one remaining FEAT-52 VIOLATION. (2) `python3
.agents/skills/harness/bin/plan-merge.py sign-approval --file <plan.yaml> --by <operator>
--date YYYY-MM-DD`, plus `approval.rulings` only for a finding the operator overrules. Tell the
operator SC-15 was ADDED to BRIEF — it is a new criterion, not a task tweak. Then the eng segment
starts at T-01/T-02 (`depends_on: []`), though 12 of 15 tasks are `main-session-direct` (DEC-174).

## Trust

- `panel:` reads cycle 5, `last_run: 2026-09-01-02-validator`, 3 readers `ran`, 17 findings, 4 resolved / 13 open, none open above `med` — `yaml.safe_load`, after the amend batch — verified-at 8ff525e2
- All 17 finding ids recompute from `panel_findings.finding_id(reader, summary)`, before AND after the seven amends — so no finding text moved and the 8 cycle-4 carry-overs are byte-identical — recomputed twice, this session — verified-at 8ff525e2
- Plan is 15 tasks / 8 decisions, `status: plan`, `approval: {status: pending}` after the batch — same load — verified-at 8ff525e2
- `BRIEF.md` carries SC-01..SC-15, no existing criterion reworded, `## Approval` still pending — read at source, this session — verified-at 8ff525e2
- T-01's `verify:` now runs `test-inflight-registry.py && test-check-domain.py`, so the new R1 receipt-write case is actually executed by a task's verify — quoted from the task, this session — verified-at 8ff525e2
- check-state.sh reports exactly one FEAT-52 VIOLATION (BRIEF not approved) plus the pending-approval note; the digest-contract violation and every orphan-run note are cleared — full runs before and after — verified-at 8ff525e2
- `sign-approval` inserts an absent `approval:` after `feature:` and refuses any caller carrying `HARNESS_AGENT_TYPE` (exit 10) — read at plan-merge.py:1023-1060, NOT executed — verified-at 8ff525e2
- cycles_used stays 7 of 10: all four runs this session reported 0 send-backs — their digests — verified-at 8ff525e2
- The seven amend items are the right edits, and SC-15's ALLOW/REFUSE pair discriminates — validator lead's assessment over the advisor's drafts, runs/2026-09-01-06-validator/digest.md — UNVERIFIED by me beyond confirming the text landed
- The 7 surviving cycle-4 findings were never re-measured; severities stay pinned to cycle 4 (G-09) — both validator digests say so — UNVERIFIED

## Dead ends

- Writing `panel:` any way but `plan-merge.py set-panel`, or a task field any way but `amend --key tasks --id T-NN --field <f>`: Edit/Write/redirect are denied by the shape gate — both verbs used successfully, this session — verified-at 8ff525e2
- Giving a member a scratch path inside a lead run dir, or a lead a `notes/review-*` artifact path: check-domain.sh refuses both (#216) — each cost one retry, this session — verified-at 8ff525e2
- Prepending a contract block to a recorded digest: check-domain.sh:1204 admits only a payload whose opening bytes are the prior file verbatim; validate-digest anchors on the LAST `^VERDICT:`, so the block goes at the foot — refused then applied, this session — verified-at 8ff525e2
- Proving BRIEF/plan integrity by `git diff` or `git show HEAD:<path>`: the feature dir is untracked, so diff is empty for changed and unchanged files alike and `show` exits 128 — hit by pm, the panel and me — verified-at 8ff525e2
- A /tmp fixture probe of INV-32: bash-write-guard blocks an orchestrator `cp` outside its domain. Verify INV-32's clauses against the live document instead (check-state.sh:418-541) — this session — verified-at 8ff525e2
- Correcting PF-4ea5b566's imprecise summary: it would change the content-hash id and invalidate any ruling on it. Flag it, never edit it — STATE Q8 — verified-at 8ff525e2

## Working set

- `.harness/harness/features/FEAT-52-factory-control-plane/plan.yaml` — 15 tasks; `panel:` at the tail, cycle 5
- `.harness/harness/features/FEAT-52-factory-control-plane/BRIEF.md` — SC-15 is new; `## Approval` at :209, pending
- `.harness/harness/features/FEAT-52-factory-control-plane/runs/2026-09-01-06-validator/digest.md` — the advisor batch and the lead's corrections
- `.harness/harness/features/FEAT-52-factory-control-plane/runs/2026-09-01-06-product/digest.md` — what pm applied, item by item
- `.harness/harness/features/FEAT-52-factory-control-plane/STATE.md` — Q4 is what the operator must be told before signing
