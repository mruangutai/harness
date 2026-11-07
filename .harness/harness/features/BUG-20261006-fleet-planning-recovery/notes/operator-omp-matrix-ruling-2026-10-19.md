# OMP-compatible pin matrix ruling

On 2026-10-19 the operator selected **Authorize one new-pin matrix** in response to:

> Authorize one full unit/integration matrix at b3f55520?

The selected option states: “Run both kinds once at the OMP-compatible pin, preserving both failed receipts. No Kaya, installation, push or merge.”

This expressly authorizes one full active unit/integration matrix at `b3f5552088c271c2083025ea9e7ff815741c310f`, notwithstanding the signed plan's original exactly-once limit and the consumed additional f9a13cac ruling. It grants no automatic retries. The original signed plan, both failed matrix receipts, historical returns, verdicts, timestamps and counts remain unchanged. It authorizes no Kaya operations, installation, push or merge.

## Final corrective-pin ruling — 2026-10-24

The operator selected **Authorize one new-pin matrix** after code/security
reviews cleared `03c4d9c95def9990dc9d4707e722a732f1a8cade` and focused tests
and CLI smoke passed. The selected option explicitly authorizes each full kind
exactly once at this pin, preserving prior receipts, with no automatic retries
or Kaya/install/push/merge/deployment. This is a new, pin-specific exception to
the consumed previous exactly-once rulings, not a change to the signed plan,
historical evidence or accounting. T-03–T-05 remain held.
