# ALTITUDE — FEAT-104-strict-digest-schema

BLUF: two genuine fold-ins (an adequacy_notes routing sentence hand-restated in exactly
the way a nearby comment says it isn't, and a duplicated step-schema loader across the
two run-state enforcement points), one briefing-row (the vendored fixture's provenance is
weaker than the sibling convention it sits beside), three `leave` (DOCUMENTED_OPTIONAL's
per-agent keying, the vendoring choice itself, and DEC-223's residual naming) are all
sound as built.

## F1 — the adequacy_notes routing rule is restated verbatim in 3 places and paraphrased in a 4th, contradicting its own "not restated here"

- file/line: `.omp/agents/harness-eng-lead.md:110-112`, `.omp/agents/harness-product-lead.md:92-94`,
  `.claude/skills/harness-team/SKILL.md:274-276` (byte-identical three-line paragraph), plus a
  paraphrase at `.claude/skills/harness/SKILL.md:42-44`.
- Both lead files say, two lines above the restatement: *"Your return contract is the team digest
  in the `harness-team` skill … one canonical copy for all three leads, not restated here"*
  (`harness-eng-lead.md:107-108`, `harness-product-lead.md:87-88`) — then the very next paragraph
  restates the routing rule anyway, word for word against `harness-team/SKILL.md`.
- Cost: the routing answer ("where does a per-dispatch answer go: adequacy_notes / evidence /
  digest artifact") now has 4 hand-typed copies. Nothing tests they agree — unlike the field-name
  contract, which `test-validate-digest.py`'s `documented_contract_gaps`/`_t01_reverse_contract_gaps`
  checks mechanically in both directions, this prose has no such check. An editor who trusts the
  file's own "not restated here" claim and edits only `harness-team/SKILL.md` (say, to add a fourth
  destination) silently strands 3 stale copies.
- Alternative: delete the paragraph from `harness-eng-lead.md` and `harness-product-lead.md` (and,
  if `harness/SKILL.md`'s orchestrator-facing copy earns its keep, point it at `harness-team/SKILL.md`
  §"Reporting up" instead of retyping it) so the file's own claim becomes true.
- worth-doing: yes — cheap, no behavior change, and the sentence to delete is already redundant with
  a skill both files already preload.
- recommendation: **fold-in**

## F2 — `DOCUMENTED_OPTIONAL` keyed by raw agent type

- file/line: `.claude/skills/harness/bin/validate-digest.py:245-280` (table),
  `tests/integration/test-validate-digest.py:297-314` (`CONTRACT_SOURCES`, the sibling table a new
  entry must also touch), `:2871-2952` (`_t01_reverse_contract_gaps`/`_t01_reverse_failures`, the
  mechanical bidirectional check).
- DEC-223's own reasoning for keying by raw type instead of putting these fields in `SCHEMAS` is
  sound (a `SCHEMAS` member is required under DEC-121, which would force `mode` onto a code-review
  digest that can never carry it). The residual this creates — two persona-keyed dicts
  (`DOCUMENTED_OPTIONAL`, `CONTRACT_SOURCES`) that must be added in lockstep for a new agent — is not
  silent: `_t01_reverse_contract_gaps` asserts every documented field is declared, and
  `documented_contract_gaps` (via `_required_contracts`) asserts every required field is documented,
  both directions, both mechanically enforced.
- What breaks at 30 agents instead of 16: nothing structurally. Growth is linear (one dict entry +
  one `CONTRACT_SOURCES` row per new agent), and the reverse-contract test scales with it rather than
  degrading. The right home is the validator's table, not each agent's own frontmatter, precisely
  because the validator is the one place required to typecheck a field regardless of which of the 3
  reviewer output-modes produced it.
- worth-doing: no — the residual is real but already compensating-controlled.
- recommendation: **leave**

## F3a — the vendored 2017-line fixture as the T-08 proof instrument

- file/line: `tests/integration/fixtures/pre-t04-validate-digest.py.fixture` (whole file),
  consumed by `tests/integration/test-validate-digest.py:3226-3298` (`_t08_revision_failures` /
  `run_t08_revision_proof`).
- The proof it actually serves: that the PRE-CHANGE validator, run as the real `--hook` CLI
  subprocess it always was, exits 0 on an undeclared key (`rogue_revision_probe`) for three personas,
  while the current validator exits 2 naming it. That is a real red/green proof of a *behavior*, not
  a text diff, and it requires an actually-executable prior script — a hand-trimmed reproduction
  would only prove the test author's belief about the old code's behavior, which is exactly the
  fidelity risk full vendoring exists to avoid.
- This is not a fresh pattern invented by this diff: `tests/integration/fixtures/prior-validate-digest.py.fixture`
  (1048 lines, a different, earlier revision) already vendors a full validator copy for the identical
  proof shape, established under "Q11 cycle-27" specifically to stay hermetic in a shallow CI
  checkout with no `git show` (comment at `test-validate-digest.py:30-34`). `pre-t04` reuses an
  already-settled trade-off rather than making a new one.
- worth-doing: no
- recommendation: **leave**

## F3b — the new fixture's provenance is weaker than the sibling convention it sits beside

- file/line: `tests/integration/fixtures/pre-t04-validate-digest.py.fixture:1` (no origin recorded),
  contrast `test-validate-digest.py:34` (`PRE_FEATURE_REVISION = "df63193f…"`, a pinned git SHA for
  the sibling fixture) against `_t08_fixture` at `test-validate-digest.py:3193-3204`, which instead
  checks two textual sentinels (`"DOCUMENTED_OPTIONAL" not in source`, `"undeclared digest key" in
  source`) as a proxy for "this really is the pre-T-04 state."
- Cost: the sentinel check proves the fixture lacks T-04's rejection string and contains T-01's
  table — it does not prove the fixture is byte-identical to any real historical commit. A
  hand-edited or partially-patched vendor copy that happens to satisfy both substring checks would
  pass silently, whereas the sibling fixture's SHA-pinned header at least states a falsifiable claim
  a reader could check against `git show`.
- Alternative: record the source SHA this fixture was extracted from in a header comment, mirroring
  `PRE_FEATURE_REVISION`'s convention already present two fixtures away in the same file — no test
  changes needed to add a comment.
- worth-doing: yes, but low stakes — the two sentinel checks already catch the failure mode that
  matters (fixture accidentally carrying T-04's own change), so this is a provenance-hygiene gap,
  not a proof-soundness one.
- recommendation: **briefing-row**

## F4 — `check-domain.sh` and `check-state.sh` each hand-roll the same step-schema loader

- file/line: `.claude/skills/harness/bin/check-domain.sh:1619-1629` (`import jsonschema` through
  `_name_pattern = re.compile(...)`) and `.claude/skills/harness/bin/check-state.sh:1490-1499`
  (`import jsonschema` through `_evidence_name = re.compile(...)`); shape source-of-truth is
  `.claude/skills/harness/bin/run-state-schema.json`, referenced independently by both.
- The two-enforcement-point *architecture* itself is not the problem: write-time refusal
  (`check-domain.sh`) plus at-rest reporting (`check-state.sh`) is the established harness pattern
  for exactly this kind of invariant (DEC-150/DEC-180 already do this for `feature.yaml`/STATE.md
  caps), and at-rest auditing legitimately catches drift a write gate never saw (hand edits, older
  tooling, merges). That split is settled and out of scope to re-litigate.
- What is duplicated is the 8-10 lines of loader boilerplate itself: `import jsonschema`, open and
  `json.load` the schema file, index into `properties.steps.items`, build a
  `Draft202012Validator`, take `set(properties)` for the declared keys, and compile the `evidence`
  `propertyNames` pattern — reimplemented nearly line-for-line in both scripts with only cosmetic
  variable-name differences (`_validator` vs `_step_validator`, `_declared` vs `_declared_step_keys`).
  A change to the schema's structure (e.g. nesting `evidence` differently) requires editing both
  call sites in lockstep, and nothing cross-checks that they still agree beyond both reading the same
  JSON file at runtime.
- Alternative: factor the loader into one shared function (e.g. a `run_state_shape.py` helper beside
  `run-state-schema.json` in `bin/`, or a function in an existing shared module such as
  `harness_boundary`) returning `(validator, declared_keys, evidence_name_pattern)`, called from both
  embedded scripts; the refuse-vs-report *behavior* around the loader stays exactly as different as
  it needs to be.
- worth-doing: yes — mechanical, no behavior change, removes a lockstep-edit hazard between the two
  gates DEC-223 relies on to both enforce the same shape.
- recommendation: **fold-in**

## F5 — DEC-223's accepted residuals

- file/line: `.harness/harness/docs/DECISIONS.md:7126-7129` (the `stop_hook_active` short-circuit)
  and `:7118-7124` (the 356 historical version-1 runs staying permanently unenforced).
- Both are named, not silent, and both carry a stated compensating control: the `stop_hook_active`
  hole is closed by requiring the refusal message be "one-shot sufficient" (the producer gets one
  reading and no second gate); the legacy-run residual is bounded because creation below
  `schema_version` 2 is refused, so the unenforced population is fixed at 356 and cannot grow —
  the bound is itself the control, not merely a hope.
- worth-doing: no
- recommendation: **leave**

```yaml
VERDICT: PASS
DIGEST:
  headline: 2 fold-in, 1 briefing-row, 3 leave — the digest-contract duplication and the two enforcement points' loader code are worth folding in; DOCUMENTED_OPTIONAL, the vendored fixture, and DEC-223's residual naming are sound as built
  findings_count: 6
  open_questions: []
  files_touched:
    - .harness/harness/features/FEAT-104-strict-digest-schema/notes/receipt-harness-ai-dev-simplify-altitude.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-104-strict-digest-schema/.harness/harness/features/FEAT-104-strict-digest-schema/notes/receipt-harness-ai-dev-simplify-altitude.md
```
