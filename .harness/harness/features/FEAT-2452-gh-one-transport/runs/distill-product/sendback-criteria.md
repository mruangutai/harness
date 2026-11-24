# Send-back criteria — distill-product (written before dispatch)

Accept pm's return only if ALL hold; otherwise send back once, then escalate:

1. Every applied op went through `expertise_apply` (receipt/batch id reported), and `expertise_update` items match the receipt and the resulting file, each with `persona: harness-pm` and no `state`.
2. Each relayed candidate (LC-1, LC-2) has an explicit disposition — applied (which op, which tier) or rejected with a reason. Rejection is a valid outcome.
3. Every new entry is WHEN/DO, <=50 words, names no FEAT/T-/#NN id; tier choice (craft vs repository) is stated.
4. At a capped section an add displaces a named survivor (drop/replace), never merges a story into one; no section ends over its cap; repository file stays within 40 lines.
5. Per-section before/after counts reported for each tier touched.
6. DIGEST carries distill did-nothing spelling (no suite / review claimed).

Not grounds for send-back: which entry pm judged weaker (O-03), or rejecting both candidates with reasons.
