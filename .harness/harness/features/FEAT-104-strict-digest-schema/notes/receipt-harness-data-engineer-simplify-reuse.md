## FEAT-104 · SIMPLIFY · REUSE angle · harness-data-engineer

**Run-state `steps[]` shape question — answered:** SPLIT. The 22 step keys, the `evidence`
property-name pattern and the `evidence` value-type union are each declared ONCE, in
`run-state-schema.json:19-58`, and both `check-domain.sh:1618-1629` (write time) and
`check-state.sh:1490-1499` (read time) load that JSON file and derive `_declared`/`_declared_step_keys`
from `_step_schema["properties"]` at runtime — no parallel key list for the steps sub-schema. Good.
BUT the **top-level document key set** (`schema_version`…`digest`, 24 keys) is a THIRD case: it lives
in the schema's own top-level `properties` (`run-state-schema.json:8-74`) *and* is separately
hand-copied as `ALLOWED` in `check-domain.sh:1537-1540` *and* again as `CHECKPOINT_KEYS` in
`check-state.sh:1397-1411` — neither reads the schema for this part. All three agree today (verified
by diff of the sets). This part of the top-level shape is pre-existing (untouched by this diff), so
it's reported as background risk, not a T-06/T-07 defect. A genuine, in-diff duplication is finding 1
below: the two step-key rejection MESSAGES already disagree in wording.

### Findings

1. **`check-domain.sh:1654-1660` vs `check-state.sh:1524-1530`** — the write-time and at-rest
   "undeclared step key or evidence shape" rejection messages are two independently hand-written
   strings, both new in this diff (T-06/T-07). **Cost:** they have already drifted — the write-time
   message spells out the `evidence` recovery format ("a per-dispatch fact goes under `evidence` with
   a lowercase identifier key and a scalar or scalar-array value"); the at-rest message drops that
   guidance entirely ("put per-dispatch facts under evidence"). An agent who trips this at write time
   gets the fuller guidance; the same violation found later by `check-state.sh` gets a terser one that
   omits the identifier-key/scalar-array detail. The next wording change (e.g. a new evidence
   constraint) has to be applied in both places, and this file pair already shows the "one nobody
   remembers goes stale" failure has already happened once. **Alternative:** both scripts already
   import shared sibling modules from the same `bin/` directory at runtime (`check-state.sh` imports
   `factory_config` specifically to avoid this exact class of drift, per its own comment at
   `check-state.sh:78-80`, citing FEAT-41's "six-key mapping and a validator disagree"). Add one
   function — e.g. `run_state_schema.step_key_violation_message(offending, step_id=None)` in a new or
   existing shared module both heredocs already put on `sys.path` — and call it from both sites
   instead of composing the string twice. **worth-doing: yes** — small, mechanical, and closes a
   drift that has already happened once inside this same feature's own diff.

2. **Top-level run-state key set triplicated** (`run-state-schema.json:8-74` /
   `check-domain.sh:1537-1540` `ALLOWED` / `check-state.sh:1397-1411` `CHECKPOINT_KEYS`) — three
   independent spellings of the same 24-key top-level set, none derived from either of the other two.
   They agree today (diffed all three sets: identical). **Cost:** the exact drift class FEAT-41
   already names in `check-state.sh:78-80` as the reason `factory_config` exists — a future top-level
   key addition (e.g. a new pin field) edited into the schema and one enforcement script but not the
   third silently either rejects a legal checkpoint or accepts an undeclared one, and nothing here
   flags the disagreement because each site treats its own literal as truth. **Alternative:** the
   same technique already used for the *step* sub-schema in these same two files — read
   `_run_schema["properties"]` keys instead of hand-copying them — extends directly to the top level;
   no new tooling required, just the same JSON load already performed a few lines away in both
   scripts. **worth-doing: yes in principle, but not for this feature** — this triplication predates
   FEAT-104 (no lines in the diff touch `ALLOWED` or `CHECKPOINT_KEYS`), so fixing it is out of this
   diff's DEC-174 scope; flagging it here per the dispatch's explicit question, not as a gate on this
   feature.

3. **`SCHEMAS` / `PASSTHROUGH` / `DOCUMENTED_OPTIONAL` in `validate-digest.py:186-280`** — checked
   for restating each other or restating `.omp/agents`/`team-config.yaml`: they don't. Each table
   answers a different question (required-and-typed per canonical persona; lead-only optional
   passthrough; raw-agent-type-only optional), and the bidirectional agreement between
   `DOCUMENTED_OPTIONAL` and each persona's `.omp/agents/*.md` prose block is enforced by
   `tests/integration/test-validate-digest.py`'s T-01 (`_t01_reverse_contract_gaps`,
   `documented_block`), which is the one place in the tree that parses that prose — no second parser
   exists to have reused or duplicated. No finding.

4. **New test helpers in `test-validate-digest.py` diff (+507 lines)** — `_t01_digest`,
   `_t04_base_digest`, `_t04_with_fields`, etc. all call through to existing in-file fixtures
   (`_dev()`, `LEAD_BLOCK`, `PM_OK`, `reviewer_digest`, `write_review_config`,
   `_plan_review_fixture`, `documented_block`, `CONTRACT_SOURCES`) rather than re-deriving them. No
   finding.

5. **`test-check-domain.py`'s `DECLARED` set (lines 20-25)** — a fifth hand-written copy of the 22
   step keys, used once, to assert `schema_keys == DECLARED` in `_declared_shape_case`
   (`test-check-domain.py:120-129`). This looks like the pattern flagged in (2), but isn't: it is a
   deliberate pin (read the schema and assert its key set still equals what the test author expects),
   the same negative-control technique that would otherwise make the assertion vacuous if `DECLARED`
   were itself derived from the schema. No finding — this is the test *doing its job*, not
   duplicating production logic.

6. **New `tempfile.mkdtemp()` fixture plumbing in `test-check-domain.py`/`test-check-state.py`** —
   both call the tree's existing `check_domain_support.fixture()` / `check_state_support`
   helpers (`test-check-domain.py:17`, `test-check-state.py:18`) rather than hand-rolling a new
   fixture harness; the raw `tempfile.mkdtemp()` calls inside those helpers match the established
   convention used by every sibling integration test in `tests/integration/`. No finding.

7. **`.omp/agents/harness-eng-lead.md` and `.omp/agents/harness-product-lead.md`** — both gained an
   identical 4-line paragraph ("When a dispatch asks a specific question, put the answer in
   `adequacy_notes`…"). Not flagged: these are two separately-spawned personas with no shared context
   at dispatch time, so each file must carry the guidance independently for its own reader to see it —
   this is the "separate dispatches share no context" case, not in-tree duplication.

### Verdict
Ran the REUSE angle only (no simplification/efficiency/altitude judgments made). Two findings
worth carrying to review (1, 2); five checks came back clean.
