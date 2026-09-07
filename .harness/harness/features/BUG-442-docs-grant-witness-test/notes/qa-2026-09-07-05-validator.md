# QA Gate — BUG-442 T-01 — f9f2d392

## Verdict: PASS

All required test kinds are present, active, and green at `f9f2d392`. The mutation ladder
(SC-03/04/05) demonstrably discriminates — verified both through the in-file ladder AND an
independent, outside-the-file reproduction of the M1 mutant. No coverage gaps. No open questions.

## verify: clause cross-check

plan.yaml:82-84 matches the dispatch's quoted string verbatim (byte comparison of all three lines,
including the trailing `grep -q` anchors). No mismatch.

## Matrix resolution — `bugfix`, `test_matrix.bugfix.when` (harness.json:203-219)

- `touches_runtime_code` → **false**. Diff (`git show --stat f9f2d392`) touches only
  `tests/integration/test-harness-yaml.py`, `plan.yaml`, `feature.json`, and a receipt note — no
  production/runtime module. → `unit` NOT obligated by this predicate.
- `fix_confined_to_tests_and_contract_docs` → **true**. Sole code file is a test file under
  `tests/integration/`; nothing outside tests/notes/plan changed. → `integration` **required**.
- `match_bug_class` → **false** (per repo-tier Expertise G-08: this clause is currently an
  unresolvable placeholder in this project; no bug-class taxonomy entry fires for any diff).
- `always: []` contributes nothing.

**Resolved floor: `{integration}`.** No kind added beyond the floor — the diff is entirely a test
file, `unit`'s own detect glob (`tests/unit/**|**/*.test.*|**/*_test.*|**/test_*.py`) does not match
`tests/integration/test-harness-yaml.py`, so unit isn't independently triggered by presence either.
I nonetheless ran the full unit suite too (see below) as a floor-is-a-floor sanity check, in case a
sibling change had reddened it; it is clean.

## Per-kind state

- **integration** — **satisfied**. Detect (`tests/integration/**`) matches the changed file. Test
  exists FOR this change (both new tests registered, ran, printed `ok`). Ran
  `.agents/skills/harness/bin/run-unit-tests.sh --kind integration`: **exit 0**, `^FAIL ` count
  **0**, pass-marker lines (`ok`/`PASS`/"N/N checks passed") **3466** across every sub-script
  (`test-check-domain.py`, `test-gh-sync.py`, `test-harness-yaml.py` at line 1323, etc. — full log
  `artifact://` from this run's bash output, not re-pasted here).
- **unit** — satisfied (floor not obligated, but green). Ran
  `.agents/skills/harness/bin/run-unit-tests.sh --kind unit`: **exit 0**, `^FAIL ` count **0**, every
  sub-script printed its own `exit 0` header and `N/N checks passed` where applicable.
- All other matrix rows (`functional`, `eval` — excluded DEC-187; `component`, `ui`, `typecheck` —
  unresolved, not in bugfix's `when`) are **not applicable** to this task.
- **locally_run** probes (`omp_session_accessor`, `handoff_comprehension`, `issue_types_live`): T-01's
  diff touches none of their `detect` surfaces (`tests/manual/probe-*.py`). Not triggered.

## T-01 verify chain, isolated

`env -u HARNESS_AGENT_TYPE -u BUG442_MUTANT_CHILD -u HARNESS_PROJECT_DIR` prefixed, from worktree
root: **exit 0**. `BrokenPipeError` tracebacks observed on two of the three `grep -q` subshells
(expected, matches receipt's account — `grep -q` closes stdin on first match while the producer is
still writing later `ok` lines; does not affect the chain's exit code).

Bare `python3 tests/integration/test-harness-yaml.py`: **exit 0**, 24 `ok` lines, 0 `FAIL` lines
(full inventory captured; both new tests print `ok`).

## Test-first audit (BRIEF's stated terms — mutation ladder as RED evidence)

**Reachability of the recursion guard** — confirmed at source
(`tests/integration/test-harness-yaml.py:301-310`). Child branch returns only when
`BUG442_MUTANT_CHILD == HARNESS_PROJECT_DIR` (both set to the SAME fresh tempdir path by the parent
at `:348`); an inherited stale value that doesn't match the run's fresh `HARNESS_PROJECT_DIR` hits
the `assert _child_token is None` and fails loudly rather than silently returning. No forgery path.

**Mutant substance, all three, verified at source (`:315-338`) and against the live manifest**:
- M1 (addition to `harness-qa`): anchor `      - name: harness-qa` at manifest line 244, `        domain:`
  at line 248 (8-space indent), insertion lands at 10-space indent matching every existing domain item
  (line 249 `          - { path: tests/**, ... }`) — syntactically valid YAML list insertion, not a
  malformed sibling of the name key. `harness-qa` confirmed **absent** from `COLLECT_FIXTURE`
  (grepped lines 47-133: only documentor/frontend-dev/etc. keys present) — only the new witness can
  catch it.
- M2 (removal from `harness-documentor`): anchor line 144 (`{ path: .harness/*/docs/**, ... }`)
  confirmed present verbatim in the real manifest; line-based removal, non-vacuous.
- M3 (census drift on `harness-ui-reviewer`): anchor line 289 (`- name: harness-ui-reviewer`)
  confirmed present verbatim; renaming to `nickname:` drops it from the recursive `name`-key walk,
  shrinking discoverable personas to 15 against the pinned 16 — the shrinking-domain trap REQ-04 names.
- All three mutants assert `text != real_text` post-replace in-file (`:324,333,338`) — no-op guard
  present for each.

**Assertions per mutant are substantive** (`:363-377`): child `returncode == 1`, the witness's own
`FAIL test_docs_domain_grant_is_exhaustive_over_every_persona` line present in child stdout
(attributing the redness to the witness, not a bystander), AND `ok   test_bare_date_scalar_stays_str`
present in the SAME child stdout (anti-false-red control — rules out an import/parse failure that
would starve `main()` before it prints anything). Unmutated control child asserted to exit 0
(`:351-355`).

**Independent, outside-the-file reproduction** (not resting solely on the code under grade asserting
about itself): built a scratch temp root with the M1 mutation applied via a standalone Python
snippet (not importing the test file's mutation logic), pointed `HARNESS_PROJECT_DIR` at it, and ran
`tests/integration/test-harness-yaml.py` as a subprocess with no `BUG442_MUTANT_CHILD` set. Observed:
exit 1; stdout line 9: `FAIL test_docs_domain_grant_is_exhaustive_over_every_persona: harness-qa:
docs grant mismatch`; `ok   test_bare_date_scalar_stays_str` present alongside it (line 6). This
confirms the witness reddens on the M1 mutation via a path the graded code never executed itself —
genuine external discrimination, not self-referential proof. (Side effect noted for completeness: my
scratch root became the resolved "real" manifest for that run, so the file's OWN internal
`test_docs_domain_witness_reddens...` control subsequently failed too inside that same run — expected
and consistent, not a defect: its own `real_text` read was my already-mutated copy, so its internal
"unmutated control must exit 0" assertion correctly reddened. This is downstream of my sanity-check
setup, not a flaw in the witness.)

**Verdict: the ladder is reachable and each mutant demonstrably discriminates.** Test-first is
satisfied on the BRIEF's own terms (`## Verification notes and gaps`): RED-first was unobtainable
from the correct tree, and the three permanent mutation cases are the accepted RED evidence.

## SC-01 .. SC-07

- SC-01: **satisfied**. Demonstrated by both the in-file ladder and my independent reproduction above.
- SC-02: **satisfied**. Enumerated all 16 personas directly against the manifest: 1 bare top-level
  `orchestrator:` (`.harness/team-config.yaml:41`), 12 `teams[].members[]` (pm, visual-designer,
  documentor, frontend-dev, backend-dev, ai-dev, data-engineer, dev-ops, qa, code-reviewer,
  security-reviewer, ui-reviewer — lines 103,125,139,168,180,194,207,220,244,267,278,289), 3 `leads:`
  (product-lead, eng-lead, validator-lead — lines 303,312,321; the `lead: { name: ... }` refs at
  93/159/242 collect the identical three names, deduping in the `set()` walk, per plan.yaml's own
  instruction not to special-case them). Total 16, matches `DOCS_GRANT_CENSUS` exactly. The test
  issues a per-persona assertion (`:283-289`, `for name in sorted(DOCS_GRANT_CENSUS): assert
  docs_grants[name] == expected`), not an aggregate dict compare or count.
- SC-03/SC-04/SC-05: **satisfied** — see mutation audit above.
- SC-06: **satisfied**. `test_manifest_domains_matches_the_regex_walk_on_the_real_manifest` prints
  `ok` in every run captured. Both new tests registered in `TESTS`
  (`tests/integration/test-harness-yaml.py:1050-1051`), immediately after the equivalence test per
  the plan's instruction.
- SC-07 (`verify: inspection`, reported as inspection not a test kind): `git diff 6d969ed3 f9f2d392
  -- .harness/team-config.yaml .claude/skills/harness/bin/harness_yaml.py` → **empty** (0 lines).
  `git diff 6d969ed3 f9f2d392 -- tests/integration/test-harness-yaml.py` → only the diff header
  `--- a/...` matches `^-`; **zero actual deletion lines** — confirms no deletion inside
  `COLLECT_FIXTURE`/`SHARED_MANIFEST_PATHS`/the equivalence test region (182 insertions, 0 deletions,
  matching the commit stat).

## Files touched

None. No tests added — the required kind (`integration`) was already present, active, and
sufficient; no gap to fill.
