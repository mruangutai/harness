# Rulings Q-02..Q-04 applied: BUG-2566 plan and BRIEF

**BLUF:** The fingerprint now covers only the loaded hook module, which after BUG-2565 is `harness-hooks.ts` alone. A stale process still lets a persona yield a `VERDICT: BLOCKED` digest, and only that. Because of that carve-out, DEC-204 and DEC-100 stay true as written: both rows are now `keep`, and T-02 no longer edits DECISIONS.md. `plan-merge.py check` exits 0. `approval.status` is still `pending`, and no verb printed an `APPROVAL-RESET:` receipt, so gh-sync was not run.

Authority: `notes/answers-2026-11-27-01-plan-product.md`. I did not touch `panel:` or `approval:`. Q-01 is left to the scope re-read, and Q-05 is out of scope.

## Plan fields changed, by item

|Item|Field|Change|
|---|---|---|
|D-02|choice, because|Adds the BLOCKED-yield carve-out, which is exactly as narrow as the held-run gate's. Every other yield is refused. A persona's refusal tells it that only a BLOCKED digest may be yielded. The "DEC-204/DEC-100 amended" claim is removed. The basis is Q-04.|
|D-03|choice, because|The fingerprinted set is now the hook module(s) the process loads from `.omp/extensions`. It no longer includes the schema directory, `digest-schema.ts` or `.omp/agents`. The basis (Q-02, Q-03) is that OMP rediscovers agent definitions on every task spawn, and that the post-2565 hook reads no schema file.|
|D-04|choice, because|The 2565-first merge order is kept. The grep matches only the live import line. The fixture rationale for the dropped entries is replaced.|
|T-01|intent|Rewritten as follows. `hookFingerprint(modules)` takes no schema directory. `HOOK_FINGERPRINT_MODULES` holds `HOOK_MODULE` alone. `entryState` returns `not-a-file` without opening the path. `staleHookReason` drops its schemaDir parameter. A new private `isBlockedYieldData` is added, and the handler skips the stale check for a persona's BLOCKED yield. A persona's refusal reason gets the BLOCKED-digest sentence as a suffix. In the tests: SC-02 has refused cases plus three carve-out cases, each reaching `validate-digest.py` exactly once. SC-01 has three cases on harness-hooks.ts (change, delete, FIFO). SC-04 adds negative cases for a schema change, a schema removal and a new `digest-schema.ts`. Each changed file is still named individually in the refusal. verify is unchanged.|
|T-02|title, files, verify, intent|The task is SPEC 4.2 only, with DECISIONS.md and DECISIONS-INDEX.md removed from `files:`. The SPEC paragraph now states the exclusions and the BLOCKED-yield exception. The verify needs `not fingerprinted` and `BLOCKED digest` and drops the DECISIONS and index checks.|
|decisions_affected|DEC-204 row|amend → keep, with successor none. The clause is unchanged and verbatim. The reason is that the carve-out leaves the held-run clause true.|
|decisions_affected|DEC-100 row|amend → keep, on the same reasoning. The clause is unchanged and verbatim, with `\n` at its wraps.|
|decisions_affected|DEC-202, DEC-237 rows|Only the reasons were reworded. DEC-202 no longer mentions the gateRoot/BIN schema path. DEC-237 now notes that the BLOCKED yield reaches validation.|
|lanes|rows|The DECISIONS.md and DECISIONS-INDEX.md rows were dropped because no task touches those files any more. resolved_at is unchanged.|

BRIEF: I updated the operator and orchestrator Done-when lines, SC-01, SC-02, SC-04, SC-05 (the baseline note), SC-06 and SC-09. I also updated the verification gaps (the agent-rediscovery basis) and the constraints: ordering, the fingerprinted set re-decided, and DEC-204/DEC-100 now marked SUPPLY.

## Decisions taken (cheap, reversible)

- **Refusal suffix.** A persona's stale refusal ends with "This run may yield only a BLOCKED digest that names this cause.", mirroring the held-run reason. Without that sentence the child cannot learn that the carve-out exists. Main gets the bare reason.
- **What counts as a BLOCKED yield.** A BLOCKED yield sent as JSON text is decoded, as the BUG-2171 yield path does, so it qualifies. A data-less `type: result` finalize is not a BLOCKED yield, so it is refused.
- **Module list kept as a list.** The module list is kept as a one-entry array, not a single constant. Per-file naming survives, and a future extension module has one place to be added. SC-06's ls-tree clause checks at review that it is complete.

## Principles applied

- Delete First: I removed the schema-directory machinery and the DECISIONS edits rather than amending around them.

## Open

- A sibling dispatch (EquivalentBoa, "re-key T-01") may edit T-01 concurrently. My intent applied with REPLACED, exit 0. The re-read should confirm that the final T-01 still carries `isBlockedYieldData`.
