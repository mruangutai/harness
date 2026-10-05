# Blocker — plan-product run cannot close canonically (2026-10-05)

## BLUF
Intake work is complete and pending signature; the run `plan-product` cannot be closed through
`feature-record.py close-run` because its durable digest never received the host-appended
fenced mapping. The defect is host-side (lead digest binding), not in the intake artifacts.
Nothing was signed, built or committed to production files.

## What exists on disk (verified by the orchestrator)
- BRIEF.md — 50 lines, `## Approval` pending, four perspective-tagged SCs (SC-01..SC-03 `verify: uat`, SC-04 inspection).
- plan.yaml — one task T-01, `status: plan`, `approval.status: pending`, `change_type: docs`,
  `execution_mode: main-session-direct` over the four grilling files (check-domain `--resolve`:
  NOBODY for the three skill files, harness-documentor for .harness/harness/docs/SPEC.md; the
  one-task patch lane keeps SPEC.md with the layer-0 edits and widens no grant).
- `plan-merge.py check --file plan.yaml --root <worktree>` (orchestrator re-run, after the pm
  correction): `OK T-01 4 anchor(s) resolved` · `1 task(s), 4 anchor(s) resolved, 0 failure(s)` · exit 0.
- notes/uat-product-document-guidance-c0.md — draft, NOT RUN YET; corrected per the main
  session's form finding: no decoy staging in the main checkout, CONTROL = edited worktree (or
  managed disposable pin) observed as the injected root, `omp --cwd=<worktree> --session-dir=...`
  launcher with the observe-don't-assume caveat, one assertion per U-step.
- notes/research-patch-intake-c0.md — pm evidence incl. verbatim plan-check receipt.
- runs/plan-product/state.yaml — step `draft` complete PASS, cycles 0; digest.md holds the lead's
  prose assessment only (no fenced mapping).

## The blocker, exactly
- Two harness-product-lead spawns (SupremePorpoise, AdditionalBison) each returned a
  schema-valid object; the host refused both:
  `check-digest: REFUSED harness-product-lead's return: authorization has no trusted hook-owned digest binding`.
- The binding is computed by `.omp/extensions/harness-hooks.ts` `openRun` at the lead's
  SubagentStart via `digest_destination.py bind()`, which requires (a) a live runtime claim for
  the lead's agent id whose `cwd` realpath equals the feature root
  (`inflight_registry.feature_root` → the worktree) and (b) exactly one open PENDING
  harness-product-lead run in feature.json — (b) held throughout (`plan-product`). The lead's
  own append was refused `inflight_registry: BLOCKED - runtime child lineage has no matching claim`.
- Consequence: `feature-record.py close-run ... --verdict BLOCKED --cycles-used 0 --code-grade n_a`
  → `REFUSED at stage digest: later stages were not run` (digest.md has no fenced mapping, not JSON).
  Per BUG-1723 the later stages (`run-end`) are not re-issued by hand; the run stays PENDING.

## Supported recovery (for the host owner / main session), not attempted here
- Determine which `bind()` check failed for the lead spawn (the hook discards the refusal
  message; `digest_destination.py` prints `{"ok": false, "message": ...}` on stdout). The
  likely candidate is the claim `cwd` not resolving to the worktree root for a lead spawned
  from the main checkout; this is an inference, not an observation.
- Once a lead spawn binds, a single harness-product-lead resume of run `plan-product`
  (assess-not-redo) can persist the digest, after which `close-run --verdict PASS
  --cycles-used 0 --code-grade n_a` closes the run.
- No hooks, gates, registry internals or fleet state were modified (main-session instruction).
