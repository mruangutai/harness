# FEAT-2537 signature ruling — 2026-11-25

**Authority.** The operator delegated approval to fable-advisor ("start feature F. same parameters, defer to Advisor"). Signer of record: AdvisorF4Sign.

**Gap.** The orchestrator escalated Q1: the plan's fail-closed class is "every non-v2 object", which is wider than the grilling's "extinct v1 shape". It adds `{}` (a strict read raises) and malformed-v2 (the writer warns).

**Ruling.**
- Q1 is ACCEPTED: both deltas are in-class, and so is the v1 writer's expired-count flip from 1 to 0.
- The intake is faithful, with no pre-signature defects.
- Signature: YES. Rework 1 round / 45 min.

**Constraints.**
- The fixture and the `:1038` comment are immutable.
- Ledger amendments land before code, in their own commit.
- Case 18 must assert both directions, for both v1 inputs.
- Any other behavior delta stops for a ruling.

## Full ruling (verbatim)

All load-bearing claims verified at source in the worktree at 3bf9ff77. Ruling follows.

---

# FEAT-2537 signature ruling — fable-advisor, under the operator's delegated approval

## Authority

Operator delegation ("start feature F. same parameters, defer to Advisor"), continuing my grilling ruling of 2026-11-25. I re-verified every decisive claim in the escalation rather than trusting it:

- **Delta (1) is real and exactly as described.** `_known_shape` (`inflight_registry.py:302-308`): a dict without `schema_version` falls to `all(...)` over its items, which is vacuously True for `{}`; `_parse`'s migration arm (`:76-88`) then iterates zero items and returns an empty claim set. So today a strict read of `{}` silently answers "no claims"; the planned `_known_shape` rewrite makes it raise `UnreadableRegistry`.
- **Delta (2) is real and smaller than it sounds.** A dict carrying `schema_version` already takes `_known_shape`'s v2 arm (`:305`), so `{"schema_version": 2, "claims": "x"}` is refused by strict readers **today** — the strict path has zero delta. Only the writer changes: today `_parse`'s migration arm skips every non-list value and folds to empty silently; after, the fold carries a stderr warning. The on-disk result (`{"schema_version": 2, "claims": []}` via `_update_registry:95-99`) is identical before and after.
- **Producibility census confirmed.** Every `_write_raw` seed in `test-inflight-registry.py` is v2 except case 18's deliberate v1 map at `:530`; the module-swap mechanism SC-02 leans on exists (`INFLIGHT_REGISTRY_DIR`, `test-inflight-registry.py:35`); `_update_registry` writes canonical v2 unconditionally. The main session's "nothing produces `{}` or any non-v2 object" holds.
- **One delta the escalation did not name:** the v1-map writer path flips its expired count. Today case 18 asserts migrate-then-expire returns `expired == 1` (`:542-543`); the fold returns `(None, 0)`. The plan's Step 3 already writes the new assertion, so it is carried — I name it here so the builder does not stop-and-rule on it mid-build.

## Gap

My grilling's constraint named "the extinct v1 shape" as the fail-closed class and enumerated "non-object" among the unchanged writer-producible states, but never ruled the two interior cases: the **empty** persona-keyed map, and the **malformed-v2** dict. The orchestrator was right to stop; the stop-clause in my own Constraints required it.

## Ruling

### (a) Q1 — ACCEPT both deltas as in-class, as the orchestrator recommends.

- `{}` is not a widening of the v1 class; it is the **degenerate member** of it — the persona-keyed map with zero personas, i.e. precisely what an untouched v1 registry looks like at birth. It is the single v1 instance most likely to actually survive on disk, and letting it keep reading as "no claims" would re-open the exact "cannot read" = "no claims" hole DEC-218 closed, for the likeliest instance. The spike directive ("an old v1 file must surface as unreadable, never as 'no claims'") decides it. Case 18 asserting it is correct, not optional.
- Delta (2) adds a diagnostic line to a writer path whose refusal, fold, and on-disk bytes are all unchanged, for a shape no writer produces and the census found nowhere. That is inside DEC-218's blessed "treat-as-empty recovery", now merely audible. In-class.
- The restated class — *no change for writer-producible states (missing, empty, corrupt, non-object, v2); every non-v2 object refused by strict readers and folded-with-warning by locked writers* — remains **literally true**: current writers produce only v2, so both deltas live entirely outside the writer-producible set. The BRIEF's Constraints sentence survives unamended.

### (b) Fidelity — the intake carries the grilling faithfully. No pre-signature defects.

Checked item by item: 2b/2c deleted with their CASES entries, 25 rewritten onto `attach_runtime_identity` + exact-parent `live_claims` with the stranded-child assertion and docstring fix, 29 re-driven through `live_claim` keeping the gone-from-disk check (plan Step 3 — matches Q2b verbatim). Case 18 asserts both directions for both v1 inputs, with writer-producible controls per state, written **before** Step 2 with recorded red/green (a test-first strengthening beyond my ruling, welcome). DEC-199/DEC-204/DEC-218 all in `decisions_affected` with the :7262 enumeration clause quoted; ledger lands first in its own commit, DEC-205 no-amendment-paragraph honored, index regenerated, and SC-03's ordering clause plus T-01's verify block enforce it mechanically. Comment-only hooks diff enforced by the verify grep. Fixture, `:1038` comment, inventory, and `validate-digest.py` pinned byte-identical in the verify block. All non-goals present. Rework 1 round / 45 min carried.

Fixable-during-build notes (neither blocks signature, neither needs a BRIEF edit):

1. **Constraints wording nit:** "Every non-v2 object fails closed" conflates the reader refusal with the writer fold; the writer does not fail closed, it recovers-as-empty with a warning. SC-02 and D-01 state the split precisely and are the binding text; the builder reads those.
2. **The expired-count flip** (`1 → 0`) on the v1 writer path is hereby ruled in-class and witnessed by case 18's rewrite; it is not a stop-and-rule event.

### (c) Signature — YES.

Sign FEAT-2537 as drafted: BRIEF.md and plan.yaml at 3bf9ff77, one task T-01 main-session-direct, D-01/D-02 as written, Q1 resolved per (a). Rework budget stands at **1 round / 45 minutes**; any behavior delta beyond the two ruled here, or any diff touching the fixture or `test-validate-digest.py`, remains a stop-and-rule event, not a rework round.

## Constraints (carried forward, unchanged plus the Q1 closure)

- Fixture and `:1038` comment immutable; verify block pins them — any diff there stops for a ruling.
- Ledger before code, inside T-01, own commit.
- Behavior class as restated in (a); case 18 asserts both directions for **both** v1 inputs (`{persona: [claim]}` and `{}`).
- The two in-class deltas ruled here (the `{}` strict refusal, the malformed-v2 writer warning, including the v1 expired-count flip) require no further escalation; anything else does.
