# Binding diagnosis — product recovery

**BLUF: the existing product-lead turn cannot lawfully acquire the missing digest binding. Main must first register one new open product-lead run, then make a fresh dispatch; registration alone cannot repair the already-started turn.**

## Governing mechanism

- The canonical order is registration before dispatch: `feature-record.py run-start` appends a `PENDING`, unended run, and the orchestrator ledger says to invoke it before every dispatch (`.claude/skills/harness/references/ledger.md:7–16`; `.claude/skills/harness/bin/feature-record.py:191–233`).
- At lead startup, the OMP hook opens the exact runtime claim and immediately calls `digest_destination.py`; only that startup path assigns the hook-private `digestBinding` (`.omp/extensions/harness-hooks.ts:993–1010`).
- Binding succeeds only when the exact child/parent claim is live and exactly one matching open registered lead run exists. The binding records that run id and exact `runs/<registered-id>/digest.md` path (`.claude/skills/harness/bin/digest_destination.py:36–63,72–87`).
- Yield does not bind or retry binding. It passes the hook-private value, including `undefined`, to `validate-digest.py`; absent binding is refused (`.omp/extensions/harness-hooks.ts:1296–1317`; `.claude/skills/harness/bin/digest_destination.py:90–104`). Calling the Python binder separately would only print a value; it cannot mutate the extension closure that supplies the yield payload.
- A wake can re-open and rebind only after the hook has returned the run gate to `unready`; the same turn cannot force that lifecycle event (`.omp/extensions/harness-hooks.ts:1100–1108,1484–1489`). Here the claim has already been released and the valid yield was refused, so there is no authorized in-turn route to recreate the required exact live lineage and hook-owned value.

## Current record and lawful recovery

`feature.json` currently contains no open `harness-product-lead` / `product` / `PENDING` run: its product distillation entry is closed `BLOCKED`, and the created recovery directory is not registered (`.harness/harness/features/FEAT-1928-digest-object-contract/feature.json:355–377`). Therefore the created `runs/distill-product-recovery-product/` files and `run_uid` are not a substitute for registration; `digest_destination.py` reads `feature.json`, not `state.yaml` or `.run-identity.json`, to choose authority.

The lawful path is:

1. After this failed runtime is terminal, Main invokes the canonical control-plane command `feature-record.py run-start --file <feature.json> --id distill-product-recovery-product --squad product --agent harness-product-lead`, adding any judgement arguments the ledger derives and requires. The registered id must equal the existing run directory name because authorization resolves the target literally as `runs/<registered-id>/digest.md`.
2. Main then makes a fresh `harness-product-lead` dispatch for the feature. Dispatch/run-start establishes the new exact child/parent claim, and the startup hook derives and retains the binding before any yield.
3. The fresh lead returns the native object to that exact bound digest. No state, source, config, skill, Expertise, GitHub, or claim mutation was performed in this diagnosis.

Registering while the current turn remains active is insufficient: there is no supported rebinding tool or mutable payload field exposed to the agent, and Main's canonical ordering requires the run open before dispatch. Forging `harness_digest_binding`, manually recreating a claim, or treating the unregistered run directory as authority would bypass DEC-237's runtime/checkout/sole-open-run boundary (`.harness/harness/docs/DECISIONS.md:7795–7802`).

## Open questions

None.

## Principles applied

- Redesign From First Principles — treated registration-before-dispatch as a lifecycle invariant rather than adding a late-binding escape hatch to an already-started turn.
