# QA Gate — BUG-442 T-01 — re-run at pin 9b3fde7e

## Verdict: PASS — confirms the prior segment (f9f2d392), re-measured at the pin

## Pin and tree state

- `git rev-parse HEAD` = `c3a9d7b9cfde3153a38883a65305af1b9ac10d78`. **HEAD is NOT the pin** — it is
  three commits ahead (`e6f7c18e`, `f9f2d392`'s successor merges, and `9b3fde7e` itself land in
  between; `git log --oneline 9b3fde7e -5` shows `9b3fde7e` as an ANCESTOR of HEAD, most recent
  commit being the SIMPLIFY fold-in commit itself). `git merge-base --is-ancestor 9b3fde7e HEAD` →
  true.
- `git status --porcelain` → **empty**. Working tree is clean, matches HEAD exactly.
- `git diff HEAD 9b3fde7e -- tests/integration/test-harness-yaml.py` → **0 lines**. The graded file
  is byte-identical between HEAD and the pin.
- `git diff 9b3fde7e -- tests/integration/test-harness-yaml.py` (pin vs working tree) → **empty**.
- `git diff --stat HEAD 9b3fde7e` (whole-tree) → only `feature.json` differs (1 line, a status/date
  field), unrelated to the graded surface.
- **Conclusion: the working tree, at HEAD, grades the pin exactly** on the one file that matters.
  Every command below ran in-place, safely.

## verify: clause cross-check

`plan.yaml:82-84` matches the dispatch's quoted three-clause string verbatim, byte for byte,
including both `grep -q '^ok   ...$'` anchors. No mismatch.

## T-01 verify chain, isolated (`env -u HARNESS_AGENT_TYPE -u BUG442_MUTANT_CHILD -u HARNESS_PROJECT_DIR`)

**Exit 0.** Two `BrokenPipeError` tracebacks observed on stderr from the first two `grep -q`
subshells (expected — `grep -q` closes its read end on first match while the producer is still
writing later `ok` lines; this is shell plumbing, not a test failure, and does not affect the
chain's own exit code, which was captured directly as `0`).

## Bare run: `python3 tests/integration/test-harness-yaml.py`

**Exit 0. `^ok ` count = 24. `^FAIL ` count = 0.** Matches the prior segment's f9f2d392 numbers
exactly, now measured at the pin.

## Full unit runner: `env -u HARNESS_AGENT_TYPE .claude/skills/harness/bin/run-unit-tests.sh`

**Exit 0** (captured via `rc=$?` immediately after the command, not read from tail). **`^FAIL `
count = 0** over the whole log. **`^ok ` count = 2829.** Confirms the prior segment's f9f2d392
measurement of "0 FAIL over 2829 ok" exactly.

## Integration kind: `... run-unit-tests.sh --kind integration`

**Exit 0** (via `rc=$?`). **`^FAIL ` count = 0.** `^ok ` count = 2067 (includes `test-harness-yaml.py`'s
own 24 as a subset alongside every other integration script's cases). Confirms green.

## (a) Out-of-file reproduction — M3 (census drift), reproduced independently

Chose M3 per the dispatch's preference (mechanism most distinct from M1). Built a **standalone**
Python snippet (not importing the test file's `_run_child`/mutation logic): read the real
`.harness/team-config.yaml`, applied `real_text.replace('- name: harness-ui-reviewer',
'- nickname: harness-ui-reviewer', 1)`, wrote the mutant into a fresh `tempfile.TemporaryDirectory`
under `.harness/team-config.yaml`, set `HARNESS_PROJECT_DIR` to that dir, left
`BUG442_MUTANT_CHILD` **unset**, and ran `tests/integration/test-harness-yaml.py` as a subprocess.

Measured:
- `returncode == 1`
- stdout contains `FAIL test_docs_domain_grant_is_exhaustive_over_every_persona: persona set
  drifted from the pinned census` — confirms the census-drift path fires (a missing persona from
  the `name`-key walk), not merely "some assertion failed."
- stdout contains `ok   test_bare_date_scalar_stays_str` — anti-false-red control satisfied
  alongside the FAIL, ruling out an import/parse-time failure.

Expected side effect, same pattern the prior segment noted for M1: because `HARNESS_PROJECT_DIR`
now resolves to my already-mutated scratch root, the child's OWN internal
`test_docs_domain_witness_reddens_on_addition_removal_and_census_drift` also ran and its own M3
no-op guard (`assert m3_text != real_text, "M3 census drift: string replacement was a no-op"`)
correctly tripped, because inside the child `real_text` IS the already-mutated text (no
`- name: harness-ui-reviewer` substring remains to replace). This is downstream of my repro setup,
consistent and expected — not a defect in the witness. **Net: M3 discriminates via a path the
graded code never executed on its own, genuine external verification, matching the rigor the prior
segment applied to M1.**

## (b) Vacuity check — could the ladder pass if `_docs_domain_census` returned an empty mapping?

Checked at source, `tests/integration/test-harness-yaml.py:235-264` (`_docs_domain_census`) and
`:340-355` (`_run_child` plus the unmutated control).

**No, it could not pass vacuously.** `_run_child(real_text)` (`:351`) runs the **unmutated real
manifest** through a repointed scratch root exactly like every mutant does — it is a genuine
subprocess run against a temp `.harness/team-config.yaml`, not a shortcut over the live tree. The
control assertion at `:352-355` requires `control.returncode == 0`. If `_docs_domain_census`
returned `(set(), {})` unconditionally (mapping always empty), the exhaustiveness test's own first
assertion (`:277`, `personas == DOCS_GRANT_CENSUS`) would fail on the **unmutated** manifest too —
`set()` never equals a 16-member frozenset — so `control.returncode` would be `1`, not `0`, and the
outer witness test would itself raise `AssertionError` at the control-check line and print `FAIL
test_docs_domain_witness_reddens...`. An always-empty census breaks the control before it ever
reaches the three per-mutant assertions. The ladder is not vacuous against this specific failure
mode.

**Secondary observation (not gating, worth flagging as info):** the three per-mutant assertions
(`:363-377`) check `returncode == 1` plus the presence of the two named lines in stdout, but do
**not** assert the specific failure-message *content* per mutant (e.g. that M1's failure message
names `harness-qa` specifically, distinct from M2 naming `harness-documentor`). This means the
ladder confirms "this test function failed, for some reason, and nothing else broke" per mutant,
not "this specific persona's specific mismatch was what failed." Given the control check above
rules out the empty-mapping degenerate case, and given each mutant string-replacement is
independently non-vacuous (`:324,333,338`), this is a real but narrow gap — a hypothetical
`_docs_domain_census` bug that always returned the exact WRONG single-persona mismatch regardless
of which of the three manifest regions was mutated would still pass all three per-mutant checks.
This does not gate: BUG-442's own signed decisions (D-01/D-02/D-03) do not require message-content
assertions, and SC-03/04/05's stated bar is "reddens on addition/removal/drift," which is met.
Recorded as **info**, not raised as a blocking finding.

## SC-01 .. SC-07 (against the pin)

- **SC-01** (grant is exhaustive over every persona): **satisfied**. Test runs green at the pin;
  per-persona assertion at `:283-289`.
- **SC-02** (16-persona domain of quantification correct): **satisfied**. Independently confirmed
  via the M3 repro above — the census walk correctly discovers and drops `harness-ui-reviewer` when
  its `name:` key is renamed, proving the walk is live against the real manifest structure, not a
  hardcoded echo.
- **SC-03/SC-04/SC-05** (addition / removal / census-drift each independently redden): **satisfied**.
  M1 was reproduced out-of-file by the prior segment; M3 reproduced out-of-file by me, this run,
  above. M2 rests on in-file assertion plus source review only (unchanged from the prior segment's
  disposition) — not independently reproduced by either segment; recorded as a residual gap, not a
  gate failure, since D-03's design and the in-file assertions (`:331-333`, `:359`, `:367-377`) are
  sound on inspection and M1+M3's independent reproductions corroborate the shared `_run_child`
  mechanism both go through.
- **SC-06** (both new tests registered in `TESTS`, ran, printed `ok`): **satisfied**. Confirmed in
  the bare run (24 `ok`, 0 `FAIL`, both new test names present) and the verify chain's two `grep -q`
  clauses, both of which exited the chain at 0.
- **SC-07** (`verify: inspection`, checked against the PIN not f9f2d392):
  `git diff 6d969ed3 9b3fde7e -- .harness/team-config.yaml .claude/skills/harness/bin/harness_yaml.py`
  → **empty** (0 lines). `git diff 6d969ed3 9b3fde7e -- tests/integration/test-harness-yaml.py` →
  182 insertions, 0 deletions (`git diff --stat`); only the diff header (`--- a/...`) matches a
  leading `-`, **zero real deletion lines**. **Satisfied.**

## Matrix resolution (`bugfix`, unchanged from the prior segment's analysis, re-confirmed at the pin)

Floor: `{integration}` (`fix_confined_to_tests_and_contract_docs` fires; `touches_runtime_code` does
not — the diff is entirely `tests/integration/test-harness-yaml.py` plus feature records).
`unit` is not independently triggered by presence (file is under `tests/integration/**`, not
`unit`'s detect glob) but was run anyway as a floor-is-a-floor sanity check, and is green.

## Findings

- **info** (`tests/integration/test-harness-yaml.py:363-377`): the mutation ladder's per-mutant
  assertions check failure presence and stdout markers, not per-mutant failure-message content —
  see the vacuity-check discussion above. Non-gating; the empty-mapping degenerate case is still
  caught by the unmutated control.
- **info** (residual, unchanged from the signed BRIEF residual): M2 (removal) has never been
  reproduced outside the graded file by either qa segment — only in-file assertion plus source
  review. Not raised as a gate failure; D-03's shared `_run_child` mechanism is corroborated by two
  independent out-of-file reproductions (M1, M3) that go through the identical code path M2 also
  uses.

## Files touched

None. No test file written or modified — this is a re-measurement, per the read-only validate-phase
mandate.
