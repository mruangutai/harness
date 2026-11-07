# Direct-run evidence amendment

The operator selected **Add explicit count to direct-run receipts** in response to the discovered contract gap: new/changed main-session-direct attribution also requires authentic evidence, but `main-session` currently aliases the closed backend-dev schema without a `cycles_used` property.

Authorized implementation: add an optional integer `DIGEST.cycles_used` property to the existing shared backend-dev schema used by main-session. New/changed run attribution remains mandatory at the feature-record boundary; zero is reported explicitly, never inferred. Other dev receipts remain compatible without the optional field. No new runtime persona, parallel schema convention or historical rewrite is introduced.

Add `.claude/skills/harness/bin/digest-schemas/harness-backend-dev.json` to T-01's files. Existing T-01 regression files cover the direct-run close; existing T-02 ledger guidance documents the explicit count. All other task scope, separately gated Kaya operations, and the 2-round / 90-minute rework ruling remain unchanged.
