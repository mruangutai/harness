# Goal-check c2 — FEAT-56 amended plan, confirming the operator's two conditions

**BLUF: YES — both conditions landed exactly as worded, verified at source, and nothing in
`plan.yaml` or `BRIEF.md` broke.** One operator-facing hazard sits OUTSIDE both artifacts:
`STATE.md:28-32` still tells the operator D-12 keeps the floor as a *runtime-conditional* check —
the form they rejected. Fix that before the signature packet ships. Approval stays `pending`.

## 1. Did the two conditions land, as worded?

**D-12 — LANDED.** `plan.yaml:133-146`. `choice` says both the probe line and the `2.1.217` STOP
bullet are DELETED, "not kept, not made runtime-conditional, and not replaced by a warning",
attributed to the operator's 2026-09-09 ruling. `dec: DEC-83` kept; `because` states the reason and
the accepted cost. D-13 (`:147-164`) records the `cli_min_version` cascade as OPEN with no task and
no file edits — correct, since resolving it amends signed DEC-83.
Residue sweep (`2.1.217|claude --version|runtime-conditional|only under Claude Code|warning` over
both artifacts): **no surviving conditional clause anywhere.** The three `runtime-conditional` hits
are all negations/prohibitions — `:137` and `:139` inside D-12's own ruling, `:1461` T-11's intent
telling the doer NOT to substitute one. `BRIEF.md` has zero hits for any of the strings.

**T-11's `verify` — LANDED and RED today.** Loaded via `harness_yaml.load_plan` and run verbatim
from the worktree root: chain `EXIT=1`. The chain short-circuits early, so the two new clauses were
run in isolation against the live file — `! grep -qF 'claude --version'` → **exit 1**;
`! grep -qF '2.1.217'` → **exit 1**; anchors re-confirmed at `harness-init/SKILL.md:34` and `:40`.
Both new clauses are RED, so the verify can grade the deletion. The `Stop; the depth setting will
not take` ban is retained beside them and catches a reworded floor.

**SC-15 — LANDED and discriminating.** `BRIEF.md:256-268`. ~1 minute, operator's own act, two named
FAIL shapes: (a) does not resolve at all, (b) resolves from a root other than `.omp/commands/`.
They are told apart by a marker line added to `.omp/commands/harness-plan.md` before the session;
**reverting the marker is stated** (`:266`). A following operator can distinguish the two: the
marker only exists in the neutral-root copy, so honouring it proves that file was read. Residual
weakness, fails SAFE: a model that ignores the echo instruction yields a false FAIL(b) — loud, not
silent, so not the always-passes shape the cycle-1 panel named twice.

**The deleted gap clause — GONE, and no remaining bullet overstates.** Six bullets at
`BRIEF.md:272-299`; the superseded "REQ-09 has no criterion of any method" clause is absent. The
bullet now citing SC-15 (`:292-296`) claims only that no *automated* gate proves discovery and that
SC-15 (`uat`) blocks the ship decision — it claims nothing SC-15 does not deliver. Bullets 1-4 and
6 re-checked true against the amended plan and against `harness.json test_kinds`.

**Disposition: BOTH CONDITIONS MET — no re-amendment of D-12, T-11 or SC-15 required.**

## 2. Did the amendment break anything?

Every site of both strings, classified — **no DEFECT**:
`plan.yaml:1246` T-10 verify ban, `:1954-1955` T-17 split-test case → correct-and-about-
harness-add-repo. `:1416-1417` T-11 verify → correct-new-ban. `:1454-1463` T-11 intent, `:136-145`
D-12 → correct-new-ban. `:1358-1361` T-10 intent → correct, amended to say harness-init no longer
differs. `:320` → record-of-a-reader (cycle-1 panel summary, `disposition: resolved,
resolved_by: T-11`). No SC asserts either string's presence.

**SC-15 is a third DISTINCT test, not a restatement.** SC-11/SC-12 grade each *procedure's* fitness;
SC-13 grades door *existence, text identity and check-reddening*, all statically. SC-15 alone
observes a **live provider resolving a door at runtime** — the only criterion that can see the
original bug (a `/harness*` door coming back as prompt text).

**Disposition: NOTHING BROKEN — no follow-up task.**

## 3. Internal consistency after two rounds

- **`PF-16dbd621` (`:317-326`) — HARMLESS RECORD.** Its summary still says "no task removes it", but
  it carries `disposition: resolved, resolved_by: T-11`, so the record reads as a reader's words
  plus the plan's answer. No consequence. Untouched, correctly.
- **`PF-c8c892` (open, low) — ACTIVE HAZARD, mild.** Summary: "REQ-09's *actually reachable through
  OMP* still has no criterion of any method requiring the observation". SC-15 now closes that gap.
  Consequence: it is an OPEN finding in the signature packet, so the operator may be asked to rule
  on a gap already closed. Record only — `panel:` is untouchable; the disposition belongs in
  `approval.rulings` (main session).
- **`PF-58fa27` (open, info) — HARMLESS RECORD.** Argues about SC-09, which is STRUCK; its subject
  no longer exists.
- No decision `because` and no other task `intent` cross-reference is overtaken: T-10's was the one
  falsified site and it was fixed (`:1358-1361`).
- **`STATE.md:28-32` — ACTIVE HAZARD, operator-facing.** It states D-12 "keeps the CLI 2.1.217 floor
  as a runtime-conditional check" and attributes it to pm. Consequence: the operator reads the
  packet's own summary asserting the exact form they rejected, and either re-issues the ruling or
  signs believing the conditional survives. `:18` is also stale (13 SCs → 14 live + SC-09 struck;
  12 decisions → 13). Not pm's file.

**Disposition: PLAN AND BRIEF CONSISTENT — main session must rewrite `STATE.md` before the packet.**

## 4. Coverage

- **REQ→task: no orphans.** All of REQ-01..REQ-10 traced; no trace cites an unknown REQ; all 17
  tasks carry `traces:` and `change_type:`. **REQ→SC: no orphans** (REQ-09 → SC-13 + SC-15,
  REQ-10 → SC-13/SC-08, the rest 1:1 as before). Every SC reachable; SC-09 STRUCK.
- **`automated` evidence kinds all ACTIVE:** only `unit` and `integration` used, both non-null
  `cmd`, `status: active`. No SC rests on `component`/`ui`/`typecheck` (null) or
  `functional`/`eval` (excluded, DEC-187). Already disclosed at `BRIEF.md:272-275`.
- **`uat` SCs (SC-11, SC-12, SC-15)** each name an operator act and an operator-only verdict; SC-15
  says so explicitly (`:267`).
- `check-plan-routes.py` over this plan: `0 violation(s)`, exit 0. 17 tasks, 13 decisions,
  `approval: {status: pending}`.

**Disposition: COVERAGE COMPLETE — signature-ready once `STATE.md` is corrected.**

## Open questions

- **Q1 (blocking the packet, not the plan):** `STATE.md` must be rewritten before the operator sees
  it. Not pm's write.
- **Q2 (non-blocking):** the floor deletion has NO permanent regression guard. T-17's split test
  asserts `claude --version` absence for **harness-add-repo** only (`plan.yaml:1954-1955`); SC-14's
  harness-init token list does not include it. Only T-11's one-time `verify` ever asserts it, so a
  later edit re-adding the STOP reddens nothing. The operator's condition is satisfied as worded;
  widening T-17's harness-init case by two tokens would make it durable — an amendment, so theirs.
- **Q3 (non-blocking):** D-13's `cli_min_version` cascade, the operator's at signature.
