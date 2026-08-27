# Handoff — FEAT-37, plan → build — written at 8fc87f8, seq-4

## Next

**Do NOT start build. The operator signs first — both `approval:` blocks read `pending` and only
the main session writes them (DEC-120).** Once both read `approved`, the first build step is the eng
segment: dispatch `harness-eng-lead` with **T-01 alone** (`plan.yaml:118`), because T-01 is the test
file every other task's `verify:` calls and nothing can be graded until it exists. T-02..T-06 follow
in plan order; **T-03 is strikeable** (`plan.yaml:17`, `:522`) — if the operator struck REQ-08, drop
it and renumber nothing. Inputs: `plan.yaml`, `BRIEF.md`, this note.

## Trust

- All four blockers are closed in the artifacts, each re-opened at disk by me after the lead's PASS — `notes/ship-review-2026-08-26-02-product.md` — verified-at 8fc87f8
- `^## DEC-` matches 201 lines and `^### DEC-` matches 28 in DECISIONS.md, so entries are level TWO — measured twice, by me and by pm — verified-at 8fc87f8
- The single-flight paragraph is gone from the orchestrator playbook; the grep exits 1 — `.claude/skills/harness/SKILL.md`, 288 lines vs 527 at 9165162 — verified-at 8fc87f8
- `children_refusal_lines` keys on HAVING CHILDREN, not on `SINGLE_FLIGHT_AGENTS` — `inflight_registry.py:32`, `:263`; fired live on my return and on the lead's — verified-at 8fc87f8
- REQ-08/SC-09 are MISATTRIBUTED to the operator in `plan.yaml:110`, `BRIEF.md:139`, `BRIEF.md:219`; the call was the orchestrator's — `notes/ship-review-2026-08-26-02-product.md` — verified-at 8fc87f8
- SC-08 cannot be graded from this build: a spawned agent loads skills from the MAIN CHECKOUT — `DECISIONS.md:7023`, D-13 at `plan.yaml:113` — verified-at 8fc87f8
- `check-state.sh` exits 0; its two VIOLATIONs are the expected unapproved-BRIEF halt and a FEAT-40 INV-26 finding that is not this feature's — verified-at 8fc87f8

## Dead ends

- Do NOT add a third `bound` site for `.claude/skills/harness/SKILL.md` — the text it graded was deleted and the case would grade the empty set — `plan.yaml:227-231` — verified-at 8fc87f8
- Do NOT correct `inflight_registry.py:258`'s #551 citation in T-04 — orchestrator scope call, different function and code path, backlog row B-2 — `notes/ship-review-2026-08-26-02-product.md` — verified-at 8fc87f8
- Do NOT re-open Q2 (DEC-199 corrected in place, not struck), Q3 (#811 struck whole, stays open) or the never-wait premise — operator rulings; probe #746 measured the premise — source: operator dispatch 2026-08-27
- Do NOT act on the old 13-anchor amendment list — 12 of the 13 line numbers were wrong and the enumeration is deleted — `plan.yaml` has zero matches — verified-at 8fc87f8

## Working set

- `.harness/harness/features/FEAT-37-lead-stop-and-wake/plan.yaml`
- `.harness/harness/features/FEAT-37-lead-stop-and-wake/BRIEF.md`
- `.harness/harness/features/FEAT-37-lead-stop-and-wake/notes/ship-review-2026-08-26-02-product.md`
- `.harness/harness/features/FEAT-37-lead-stop-and-wake/runs/2026-08-26-02-product/digest.md`
- `.harness/harness/features/FEAT-37-lead-stop-and-wake/STATE.md`
