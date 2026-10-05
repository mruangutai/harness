# FEAT-1928 simplify briefing — retained assessment and main-session disposition

The retained squad snapshot below preceded main's re-signature and record repair. Current dispositions are in the final section; verification and independent validation remain required before ship.

## Definition of done

No validation goal-check has run; every perspective is ungraded until the `validate` run.

| Perspective | Signed outcome | Verdict | SCs | Evidence |
|---|---|---|---|---|
| operator | Closed persona contracts reject malformed text, null data, dispatcher-owned schema controls; live retry evidence precedes repair deletion. | ungraded | SC-01, SC-04, SC-05 | Fresh receipt pending at `notes/live-digest-object-probe-current.md` (main). |
| orchestrator | Every persona returns the same typed object; no prose parsing. | ungraded | SC-02 | No validate digest. |
| code maintainer | One canonical schema feeds validation and provider bundles; obsolete parsers removed. | ungraded | SC-03, SC-08 | No validate digest. |
| reader | Validated YAML append-only; historical digests byte-stable. | ungraded | SC-06, SC-07 | No validate digest. |

## Current result

- Plan reconciliation (`runs/plan-reconcile-T02-product`, `runs/plan-reconcile-T02b-product`): T-02 verify drops the hard-coded checkout SHA test, keeps all canonical suites and the receipt verifier, points `--verify-receipt` at `live-digest-object-probe-current.md`; T-02 intent and BRIEF SC-05 require installed-release identity (version, launcher sha256, release-tag source SHA, provenance labelled). Both runs returned FAIL only because signature is main-session-only.
- Simplify (`runs/simplify-eng`): four angles graded 14f04a75. Ten advisory findings F-01..F-10, none blocking; MC-1 (probe reads deleted runtime-pin.json — main's in-flight rewrite removes it); MC-2 (FEAT-495 lineage-field refusal unreachable on the OMP path — DEC-250 owner's backlog). One reader breached read-only conduct (timing + deleted /tmp file), disclosed and excluded from evidence. The lead's return object was accepted by the host but the hook released its claim before the validator-owned fence was appended, so the run is open until main renders the block from `runs/simplify-eng/return-object.json`.
- Main reports (not yet on disk): Python pool 118/120 with the two doc/index failures fixed directly, hook 105/0, provider suites 111/0, provenance helper smoke PASS on OMP 18.6.0 / source 89d26109.

## Open blockers

1. Operator: approve the reconciled T-02 and strengthened SC-05; main runs `revoke-approval` then `sign-approval` (commands in `notes/research-plan-reconcile-T02.md`) and restores BRIEF `## Approval`.
2. Main: render the `simplify-eng` fenced block; land the fresh live receipt; commit records; then the successor pins `review_sha`, moves cards to Review and dispatches `validate`.

## Spend and record

- Runs: 14 of informational 20 (simplify-eng open). Cycles: 2 of 10, 3 after simplify-eng closes. Rework window: 0 minutes / 0 rounds of the 90 / 2 ruling.
- Judgements: 6 (mission, finding_kind, succession, regate ×2). Builder amendments: none; overrule rate 0/0.
- UAT: not run.

## Proposed backlog

| ID | Nature | Residual |
|---|---|---|
| MC-2 | bug | FEAT-495 dispatch-guard lineage-field refusal cannot fire on the OMP path (normalization strips keys first; revisedInput keeps them) — `harness-hooks.ts:248-273,308-318`, `dispatch-guard.py:181-190`. |
| F-05 | chore | `digest_record.structured_keys` has no production caller; retire with its test under separate review. |
| F-06 | chore | TS persona alias/prefix branches in `digest-schema.ts:31-67` appear unused on the dispatch path; confirm callers before removal. |
| HOOK | bug | Pre-cutover hook releases a lead claim before the validator-owned append, leaving prose-only digests (third occurrence this feature). |
| TOOLS | bug | check-domain refuses `agent://` peer messages and `xd://report_issue` for governed agents. |

Assembled from `runs/plan-reconcile-T02-product/digest.md`, `runs/plan-reconcile-T02b-product/digest.md`, `runs/simplify-eng/digest.md` and main-session IRC claims marked as such.

## Main-session disposition — 2026-10-04

- Re-signed T-02 and T-04, approved BRIEF under the operator's existing authorization, and restored all cards to Building. The plan checker resolves all 76 anchors with zero failures; the classification-file overlap is intentional.
- MC-1 is fixed in the parent-owned probe migration: no runtime-pin read; actual installed launcher identity and separately labeled release-source metadata are recorded. Fresh end-to-end runtime proof is still required.
- The record handoff blocker is resolved without restoring or fabricating a claim: the original BLOCKED assessment is retained, a transparently labeled offline canonical re-expression is rendered by the worktree validator, and the durable-record-aware close-run consumer records BLOCKED / one cycle. The legacy main consumer refused the new sentinel/member encoding; that refusal was not overridden or reported as PASS.
- Applied F-01's schema-lookup reuse and removal of its one-caller forwarding wrapper, and F-04's shared severity reference. An actual hook-mode smoke accepted the resulting schema/lookup paths; a repeated append left the durable file byte-identical.
- F-02/F-03 are not blockers and remain advisory: further persona-alias/fixture consolidation is outside the closed return-object cutover, and independent negative fixtures should not lose their expected behavior during wrap-up. F-05/F-06 retain their explicit separate-review proposals; no assertion or exported alias is retired here.
- F-07/F-08/F-09/F-10 require no change: preserve fail-closed schema loading, claim-scope traversal, independent runtime seams, and the small standalone probe helper. MC-2, HOOK and TOOLS remain the inherited-surface proposals above, not invented FEAT-1928 acceptance waivers.
- No timing measurement from the read-only breach is accepted as evidence. Final validation must independently grade the committed candidate and the fresh runtime receipt.
