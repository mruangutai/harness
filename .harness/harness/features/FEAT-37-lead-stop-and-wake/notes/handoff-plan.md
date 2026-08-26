# Handoff — FEAT-37, plan → build — written at 9165162, seq-3

## Next

**TWO BRIEF EDITS ARE STILL UNAPPLIED. `BRIEF.md` is unchanged and NOT signature-ready.** Dispatch
product-lead once, with the prompt already proven in run `2026-08-24-04-product` (it needs no
rework): (a) reword **SC-08 at `BRIEF.md:136`** — it says "Expect exactly one refused return per
dispatch", the falsified bound restated inside the verifying criterion. Operator ruling: refusals are
EXPECTED and NOT SCORED AT ALL — no count, no bound, no "exactly", no "at least", any number correct,
phrased so a later reader cannot reintroduce a count believing they are TIGHTENING it. The criterion
asserts only: no stay-alive tool call between dispatch and wake; no lead killed at ~600s; evidence is
the sidecar path and dispatch-to-resume timestamps. (b) Fix **`BRIEF.md:46`**, still reading
"whatever the operator rules on scope below" — the ruling is made. Then re-run both gates. **Do NOT
start build; the operator signs first.**

## Trust

- **The dispatch was blocked by a FOREIGN `harness-pm` claim, not by anything wrong with the work** —
  `cwd: /Users/molchairuangutai/GitHub/harness` (main checkout) in
  `.harness/.inflight-claims.json`, started `04:46:42Z`, read by me at `04:54:40Z` — verified-at
  9165162. My own children all register under `.../FEAT-34-worktree-act3-enforced`. **DO NOT
  release it**: not ours, and `release_all` drops every persona's claim across all live flows.
  Retry once the claim clears; TTL is 3600s from `04:46:42Z`.
- The loop's cause is the MISSING RULE, not the #551 hook — specimen `agent-a8f1c68d9a0d69f25` has
  the loop signature with ZERO `returned with children in flight` — verified-at 9165162.
- The refusal bound is "at most once per CONSECUTIVE STOP SEQUENCE; re-fires each wake while a child
  is live" — `agent-a89be3fd837d1b779` lines 178 vs 392, same eng-lead claim, different child sets —
  verified-at 9165162.
- The #811 strike is clean: struck ids survive ONLY inside D-07's strike record; `source_issues:
  [831]`; `approval.status: pending` — verified-at 9165162 by my own grep.
- `check-plan-routes.py` 0 violations with the T-08 DEVIATION gone, and `check-state.sh`'s single
  FEAT-37 violation being the unapproved BRIEF — **UNVERIFIED**; lead-reported post-strike, re-run
  both before acting.
- DEC-199 carries the falsified bound in TWO sentences (`:6701`, `:6702`), and the bound guard grades
  the amendment's own text — **UNVERIFIED**, lead-reported. T-06 claims to handle both.

## Dead ends

- Do NOT blind-release the inflight registry — it clears every live flow's claims — verified-at
  9165162 by reading the registry's `cwd` fields.
- Do NOT pass `model:` on any dispatch — `dispatch-guard.sh:41-53` blocks it; this cost a spawn in
  run `2026-08-24-04-product` — source: that run's digest.
- Do NOT reintroduce `SendMessage` for leads — source: #831 comment, #610 closed won't-do.
- Do NOT spend a task on #811 — struck by user ruling; the operator rewrites its premise himself —
  source: `notes/answers-plan-2026-08-24.md` Q1.
- Do NOT let the goal-check grade SC-08 — operator-run uat, outstanding by ruling — source: same, Q5.

## Working set

- `.harness/harness/features/FEAT-37-lead-stop-and-wake/BRIEF.md`
- `.harness/harness/features/FEAT-37-lead-stop-and-wake/plan.yaml`
- `.harness/harness/features/FEAT-37-lead-stop-and-wake/STATE.md`
- `.harness/harness/features/FEAT-37-lead-stop-and-wake/notes/answers-plan-2026-08-24.md`
- `.harness/harness/features/FEAT-37-lead-stop-and-wake/runs/2026-08-24-04-product/digest.md`
