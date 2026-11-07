# Operator directive — 2026-11-07

Operator: repository owner (mruangutai), in the main OMP session.

Verbatim:

> review these three ticket:
>  - #2172 (https://github.com/mruangutai/harness/issues/2172) — Fleet mirror routing and wrong-repository receipt recovery.
>  - #2173 (https://github.com/mruangutai/harness/issues/2173) — Historical cycle accounting.
>  - #2174 (https://github.com/mruangutai/harness/issues/2174) — Malformed refused historical digest.
> stack rank them in priority relative to severity of the issue. once done, let's tackle them one at at time. i want you to fix each one, defer to the advisor for questions, and take each to a clean and green merge.

The three tickets, filed by the operator on 2026-11-07, define the effects. They restate this
feature's T-03 (#2157), T-04 (#2158) and T-05 (#2159), whose T-01/T-02 tooling was verified at
`03c4d9c95def9990dc9d4707e722a732f1a8cade`.

## What this authorizes

Recorded as the operator's answer to every gate that STATE.md listed as held:

1. Merging `origin/main` into this branch and resolving conflicts within the T-01/T-02 file lists.
2. Exactly one full active unit matrix and exactly one full active integration matrix at the
   post-merge review pin. This is a new pin-specific ruling; earlier matrix rulings stay consumed.
   No automatic retries.
3. Push, PR, and merge to `main` once CI is green. Fast-forwarding the main checkout to that
   merge is the owner installation that T-03 to T-05 require.
4. T-03 capture, T-04 historical ledger recovery and T-05 full Kaya mirror replacement
   (`--previous-repo mruangutai/harness`, target `mruangutai/kaya`). Each one is recorded with its
   own exact-effect note, which quotes this directive.

## What it does not authorize

These go back to the operator. The advisor's ruling, KayaBlockersAdvisor on 2026-11-07, sets
this boundary:

- `--adopt-receipt` reconciliation after an uncertain create.
- Resolving captured evidence that is missing, changed or contradictory.
- Passing SC-08/UAT, which the operator runs personally.
- Any exemption or waiver added to a check-state, merge or sweep gate.
- Touching Harness milestone 100, parent 2116, tasks 2117 to 2126, or Harness #14.

## Merge reconciliation ruling (advisor, 2026-11-07)

`origin/main` (37cfcfd4, #2068) shipped a `runs[].return_disposition: refused` marker
independently. RefusalModelAdvisor ruled on the merged tree:

- Typed `refusal` provenance is the only mechanism any writer uses.
- The validator's contract-refusal status 65 protocol, `ended_at`/accounting preservation and
  replay-only `run-end` all come from main.
- The three existing marker entries on main (BUG-2161 ×2, FEAT-2037 ×1) stay byte-untouched as
  frozen legacy data. Named readers still read them (INV-15/46, replay), and no writer produces
  the marker any more.
- An entry never carries both the marker and `refusal`.
- Closed BLOCKED runs take provenance only through `record-refusal`.

The ruling stays inside T-01 and T-02. All touched files are already in their signed file lists,
and no signed decision changes meaning.
