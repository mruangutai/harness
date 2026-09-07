# BRIEF — BUG-442-docs-grant-witness-test

## Problem

The `.harness/*/docs/**` grant sits on exactly one persona — `harness-documentor`,
`.harness/team-config.yaml:143-144` — and **nothing pins it**. The only assertion that touches the
docs paths is `COLLECT_FIXTURE` in `tests/integration/test-harness-yaml.py`, which covers 6 of the
manifest's 16 personas and whose subject is a different question (does `manifest_domains()` agree
with an independent reading of the manifest?). So today a docs grant added to a tenth persona, or
removed from documentor, lands green. This is the residual accepted at the FEAT-22 ship briefing
(issue #442): the grant is correct, and pinned by nothing.

**The docs grant itself is CORRECT and is not being changed by this flow.** `.harness/team-config.yaml`
is not edited. This is a missing-witness bug: the suite is green at 6d969ed3
(`python3 tests/integration/test-harness-yaml.py` exits 0, observed at that sha).

## Goal

Add a witness to `tests/integration/test-harness-yaml.py` that states, in one place, which personas
hold the docs-domain grant — reading the manifest live through the repointable `MANIFEST_PATH` the
file already resolves, quantifying over all 16 personas, and reddening on an addition, a removal, or
a shrunken persona census.

## Requirements

- REQ-01: The docs-domain grant status of every persona is asserted against the manifest as loaded
  at run time, not against hand-copied grant literals.
- REQ-02: A docs grant **added** to any persona that must not hold one fails the suite.
- REQ-03: The docs grant **removed** from the persona that must hold it fails the suite.
- REQ-04: The domain of quantification — the persona census — is itself pinned, so deleting a
  persona from the manifest cannot silently shrink the assertion.
- REQ-05: The existing `COLLECT_FIXTURE` equivalence proof keeps working, unweakened, and the
  manifest is unchanged.

## Success Criteria

- SC-01: The witness resolves the manifest from the module's existing `MANIFEST_PATH`
  (`HARNESS_PROJECT_DIR` / `CLAUDE_PROJECT_DIR` overridable, lines 29-32), so pointing the root at a
  scratch checkout grades that checkout: running the test file as a subprocess with
  `HARNESS_PROJECT_DIR` set to a temp root holding a mutated `.harness/team-config.yaml` makes the
  witness print a `FAIL` line while an unrelated control test still prints `ok`.
  verify: automated      evidence: integration
- SC-02: The witness's verdict covers all **16** personas — 1 bare top-level `orchestrator:`, 12
  under `teams[].members[]`, 3 under `leads:` — each with its own asserted grant status, not a
  file-global search and not a chosen subset.
  verify: automated      evidence: integration
- SC-03: A docs grant added to a persona that must not hold one reddens the suite. Demonstrated on a
  scratch manifest copy that adds `{ path: docs/**, upsert: true }` to `harness-qa` — a persona
  absent from `COLLECT_FIXTURE`, so the new witness is the only assertion that can catch it.
  verify: automated      evidence: integration
- SC-04: The docs grant removed from `harness-documentor` reddens the suite. Demonstrated on a
  scratch manifest copy with the `.harness/*/docs/**` line deleted; the witness's own `FAIL` line
  must be present, not merely a non-zero exit.
  verify: automated      evidence: integration
- SC-05: Removing a persona from the manifest reddens the suite rather than shrinking the
  quantification. Demonstrated on a scratch manifest copy where one persona mapping loses its
  `name:` key, leaving 15 discoverable personas against a pinned census of 16.
  verify: automated      evidence: integration
- SC-06: `test_manifest_domains_matches_the_regex_walk_on_the_real_manifest` still prints `ok`, and
  every new test is registered in the file's `TESTS` list (an unregistered test never runs — the
  file's own comment records that this already happened once).
  verify: automated      evidence: integration
- SC-07: `COLLECT_FIXTURE` and `SHARED_MANIFEST_PATHS` are byte-identical to 6d969ed3, and
  `.harness/team-config.yaml` and `.claude/skills/harness/bin/harness_yaml.py` are untouched:
  `git diff 6d969ed3 <review_sha> -- .harness/team-config.yaml .claude/skills/harness/bin/harness_yaml.py`
  is empty, and `git diff 6d969ed3 <review_sha> -- tests/integration/test-harness-yaml.py` shows no
  deletion inside the fixture region.
  verify: inspection

## Verification notes and gaps

- **RED-first cannot come from the current tree.** The grant is correct today, so the witness passes
  the moment it is written. The failing state is demonstrated by the three mutation cases (SC-03,
  SC-04, SC-05), which live in the suite permanently as negative controls. qa's test-first audit
  should grade the mutation cases as the RED evidence; a witness that cannot fail is exactly the
  defect #442 names.
- No criterion rests on a null-runner test kind. `integration` is active
  (`.agents/skills/harness/bin/run-unit-tests.sh --kind integration`) and its detect glob
  `tests/integration/**` matches the changed file.
- **Residual, stated rather than hidden:** the census walk parses the manifest with the same loader
  the grant lookup uses, so a parser bug that hides a *newly added* persona would hide it from both.
  The literal 16-name census closes the deletion half of that hole, not the addition half. Closing
  it fully would need a second, parser-independent reading of the manifest — out of scope here, and
  not required by the acceptance sentence.

## Constraints

- The manifest is **read-only** for this flow (issue #442: the grant is correct).
- `COLLECT_FIXTURE`, `SHARED_MANIFEST_PATHS` and
  `test_manifest_domains_matches_the_regex_walk_on_the_real_manifest` must not be rewritten or
  weakened. Their inlined literals are deliberate: they prove `manifest_domains()` agrees with an
  independent reading, and deriving them from `harness_yaml` would prove nothing.
- `.claude/skills/harness/bin/harness_yaml.py` supplies the mechanism (`manifest_domains(path, agent)`)
  and is not modified. It carries **no persona enumerator**; where the persona list comes from is
  D-01, not a production change.
- Test-directory invariant: the file stays at `tests/integration/`, which is what selects the
  `integration` kind.

## Approval

status: approved
by: operator
date: 2026-09-07
