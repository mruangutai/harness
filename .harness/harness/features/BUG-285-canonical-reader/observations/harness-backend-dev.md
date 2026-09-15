# Observations — harness-backend-dev — BUG-285-canonical-reader

- 2026-09-14: T-09 removes the obsolete shell differential script before the canonical-reader inventory, so its internal json.load is not a live parse surface.
- 2026-09-14: Present malformed issue receipt fields must be refused before create paths; null remains legitimate unrecorded state.
- 2026-09-14: Shared feature.json validation must preserve absent github/factory blocks while rejecting present recorded parent or issues corruption before either consumer can create issues.
- 2026-09-14: A T-03 row can be marked migrate/team while its remedy is only `documented source route`; this cannot satisfy a public-accessor seam cutover without an amendment naming an accessor.
- 2026-09-14: A path-or-text accessor can retain one strict parser by letting the byte reader perform only I/O and decode, then routing both it and the text source to the same parsing helper.
- 2026-09-14: Before a semantic-reader cutover, verify the assigned public accessor accepts the consumer payload shape; a mapping-only GitHub parser cannot preserve array-output consumers.
- 2026-09-14: parse_gh_json needs a value-level strict parser separate from mapping-only consumers; feature_json path/text modes can share an internal parser and validation boundary.
- 2026-09-14: artifact_accessors.load_plan delegates to schema-validating harness_yaml.load_plan, while handoff_done_when intentionally accepts partial plan task mappings; migrating its classified yaml.safe_load reader changes the caller contract and fails its targeted test.
- 2026-09-14: A classified accessor remedy must preserve the consumer input shape; manifest_domains accepts one agent and cannot replace generic all-role grant discovery.
