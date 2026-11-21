# Receipt — EFFICIENCY reader — FEAT-2225 — r-20261121-5-simplify-eng

BLUF: two LOW findings, both advisory (cost is seconds per distill, not minutes; neither sits on a per-session or per-write hot path). Source read pinned at `fd8ffcdf` via `git show`; nothing run. All costs below are **estimates from source structure** (CPython start-up taken as roughly 30-80 ms; no measurement taken).

## Findings

### F-1 — validator spawns one `verify-receipt` interpreter per receipt slot, each re-loading every receipt (LOW)
- **File/line:** `.claude/skills/harness/bin/validate-digest.py:2255-2272` (`_verify_receipt`), driven from `_receipt_errors` `:2250-2252`; callee `expertise-merge.py:1452-1480` (`verify_receipt` → `load_active` `:1069-1081`).
- **Summary:** `_active_batches` (`:2148-2157`) already imports `expertise-merge.py` in-process and calls `load_active`; `_verify_receipt` then re-enters it through `subprocess.run([sys.executable, …, "verify-receipt"])` once per `(runtime, destination)` slot.
- **Cost (estimated):** a lead's lineage return (a distill lead listing N member slots) pays N interpreter starts plus N re-reads and re-hashes of every receipt in the feature notes, so O(slots × receipts) file reads. With about 15-30 slots, roughly 0.5-2 s added to that lead's yield, once per distill. Members' own returns carry 1-2 slots (negligible). Not minutes; not a per-session or per-write path.
- **Alternative:** call `merge.verify_receipt(...)` on the module `_active_batches` already loaded, catching `harness_merge.MergeRefusal` (already in `_evidence_failures`) and mapping `refusal.lines` and `code` into the same message. Behavior implications: the refusal text and exit-code detail are rebuilt from the exception, so the "(verify-receipt exit N)" wording would need `refusal.code`; the subprocess's 60 s timeout isolation is lost (an in-process hang is unbounded, though the work is local file reads); and tests that stub the subprocess seam would move to the module seam. If the process boundary is intended as the "same interface the CLI exposes", keep it and accept the cost as advisory.

### F-2 — `expertise_apply` authorizes the same runtime lineage twice per call (LOW)
- **File/line:** `.omp/extensions/harness-hooks.ts:1368,1386-1389` (tool_call gate: `expertise_apply` is in `mutates`, so `authorizationRefusal` runs) and `:1146-1156` (`applyCallerRefusal`, called from `execute` `:1178`, runs `authorizationRefusal` again). Both spawn `inflight_registry.py authorize` (`:1130-1142`) with identical arguments; the comment at `:1128-1129` calls it "the one claim authorization".
- **Cost (estimated):** one redundant Python spawn plus a registry scan per call, roughly 50-100 ms; at about 15 members × 1-3 calls this is about 1-4 s of CPU summed across a distill, mostly parallel. Not minutes.
- **Alternative:** drop the `authorizationRefusal(cwd, currentAgent)` tail of `applyCallerRefusal` and keep its in-process identity/mission/run-gate checks, since the tool_call gate already denied unauthorized lineage before `execute`. Behavior implications: `execute` stops being self-defending if a host path reaches it without the `tool_call` gate (the tests in `tests/unit/omp-hooks.test.ts` that call `execute` directly would then not see an unauthorized-lineage refusal), and the authorization-to-write window widens by one tick. If defense-in-depth at the tool is wanted, keep it and amend the "one authorization" comment.

## Examined, not flagged
- `bash-write-guard.py:268-415` `_program_calls` runs on every governed Bash call: pure string work (`shlex` per segment, depth ≤ 3); microseconds, no I/O. Later re-tokenization is the same order. No finding.
- `dispatch-guard.py:745-838`: `_distill_preflight` runs only when a lead is dispatched or dispatches (`involves_lead` short-circuit); re-reads `feature.json` once more per lead start (ms) and `find_run_claim` scans linked worktrees (7 here). Below threshold.
- `validate-digest.py:2088-2093` `_hook_expertise` resolves context only when `expertise_update` is a nonempty list or the mission is distill; ordinary yields pay nothing. Good shape.
- `expertise-merge.py` `check_candidate` spawns `check-expertise.py` under the per-file lock; the lock is per persona file, so contention is negligible, and the spawn is the validation boundary. `_confirm_agreement` re-read is deliberate integrity evidence. `replay` per-destination `git cat-file` (~tens of spawns, ~0.2 s, one-shot at merge). Not waste.
- `merge-gate.py`: raw-merge hook runs `gh pr diff --name-only` only for merges that pass owner/receipt policy (rare, fail-closed by design). `merge-distill` fetches PR metadata twice (`:324`, `:311`) and main twice (`_fetch_main`, `_live_main`) — deliberate TOCTOU recheck before the merge call; per-file `git cat-file` in `_committed_replay` is a one-shot ~ms-scale loop. Not waste.
- Deliberate boundary suites (test-expertise-merge, test-member-expertise, test-merge-gate, test-dispatch-guard, test-bash-write-guard, omp-hooks): not waste, not judged.

## Ownership note
Neither finding touches a T-01-only builder file; F-1 is validate-digest.py (T-04), F-2 is the OMP hook (T-04): FLAG-ONLY, no edit made.

## Principles applied
None read this run (no craft leaf consulted); no citation claimed.
