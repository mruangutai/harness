# GOAL-CHECK — FEAT-104, final, pin `984bd26b`

**BLUF. Nine of nine REQs and fourteen of fifteen live criteria are MET at `984bd26b`; the
fifteenth, SC-13, is `pending-operator` and is the ONLY thing left. SC-08 — the sole gap the c9
goal-check found — is CLOSED at this pin: both seams now assert the declaration route as a
substring.** SC-12 was EXECUTED in this run (positive exit 0 over 728 artifacts; discrimination
exit 1 naming the altered path). The c11 reviewer panel returned PASS at this same pin —
`must_fix: []`, four PASS reviewers, `severity_max: med` (advisory under
`gates.review: advisory_unless_high`, `.harness/harness.json:373-375`), `code_grade: pass`
(42 functions), `matrix_ok: true`; not re-adjudicated here. SC-14 is `struck` — deleted during
planning and absent from the signed BRIEF. **The feature is ready for the operator UAT.**

Every row below was re-derived at the pin with `git show 984bd26b:<path>`; no verdict is inherited
from the c9 note. Every c9 pointer still resolves, but many drifted — see Anchor drift.

## REQ table — pointers at `984bd26b`

| REQ | verdict | pointer at the pin |
|---|---|---|
| REQ-01 | met | key set closed inside `validate()`: `validate-digest.py:1407` (`raw_persona != "lead"`) → `:1415` `undeclared digest key(s)`; hook exit 2 asserted `test-validate-digest.py:3155-3159` |
| REQ-02 | met | creation floor `check-domain.sh:1586,1608` (`schema_version floor`); step check `:1663-1682` (both `missing required step key.` and `undeclared step key or evidence shape.`); four creation fixtures `test-check-domain.py:135-153` |
| REQ-03 | met | `run-state-schema.json:45-49` — `evidence` object, `propertyNames ^[a-z][a-z0-9_]*$`, scalar/scalar-array values, `additionalProperties: false` at step level |
| REQ-04 | met | re-counted row-by-row at the pin: `DOCUMENTED_OPTIONAL` `validate-digest.py:248-280` = 17 rows / **16 distinct** names (`in_scope` twice), 1:1 with the test's `_t01_documented_values` `test-validate-digest.py:2962-2976`; `PASSTHROUGH["lead"]` `:235-243` = the 5 rows; `prototype` carried by `NULLABLE` `:54` |
| REQ-05 | met | digest refusal names every key + route `validate-digest.py:1415-1421`; step refusal names every key + route `check-domain.sh:1667,1674,1682` |
| REQ-06 | met | `stop_hook_active` guard `validate-digest.py:1828`, ahead of every `validate()` call; written down as DEC-223 (`DECISIONS.md:7092`, "one-shot sufficient" at `:7127-7128`) |
| REQ-07 | met | `SCHEMAS["lead"]` requires `adequacy_notes` `validate-digest.py:209`; documented `.claude/skills/harness-team/SKILL.md:264`; generic-`lead` archive path keeps it optional `:1248-1250` |
| REQ-08 | met | archive exemption `validate-digest.py:1407`; version-1 update accepted `test-check-domain.py:156-164`; SC-12 executed below — 728 artifacts, 0 changed, 0 vanished |
| REQ-09 | met | mechanical BOTH ways over the **16** personas of `CONTRACT_SOURCES` (`test-validate-digest.py:297-314`): reverse `_t01_reverse_contract_gaps` `:2871` driven per persona `:2936-2941`, forward `run_documented_contract_cases` `:519-538` |

## SC table — 15 live criteria

Automated rows rest on TWO legs, both stated: **(a)** the discriminating assertion existing in the
test source at the pin, and **(b)** execution, **ADOPTED** from qa run 15 at this same pin
(`notes/qa-2026-09-10-15.md`: unit exit 0 / 36 files; integration exit 0 / 70 files). One focused
file was re-run read-only here and is labelled MEASURED.

| SC | verify | verdict | evidence at `984bd26b` |
|---|---|---|---|
| SC-01 | automated | met | (a) per-persona rogue-key probe `test-validate-digest.py:3082-3090`; hook exit 2 `:3155-3159`; "exits 0 before the change" via the vendored pre-T-04 comparison `:3207-3223`. (b) ADOPTED integration 70/exit 0 |
| SC-02 | automated | met | (a) **9/9** persona keys counted individually at `:3173-3179` (`pm dev qa reviewer visual-designer documentor dev-ops lead orchestrator`), each its own case in the `for` at `:3084-3089`; accepting fixture built FROM the documented block `:3098-3106`. (b) ADOPTED |
| SC-03 | automated | met | (a) `test-check-domain.py:87-91` — exit 2, `undeclared step key`, `rogue_step_key` named. (b) **MEASURED** here: 13/13, exit 0 |
| SC-04 | automated | met | (a) both directions, three cases `test-check-domain.py:111-118` (three identifier keys accepted; space-bearing key refused; nested mapping refused). (b) MEASURED 13/13 exit 0 |
| SC-05 | automated | met | (a) per item, all four groups: **16 distinct documented fields / 17 rows** `:2962-2976` each driven through accept+wrong+omit `:2918-2933`; **5/5** PASSTHROUGH rows `:2955-2959` × 3 assertions `:2889-2902`; `adequacy_notes` its own 3 `:2905-2915`; **22/22** step keys (21 + `evidence`) each literally present in `_full_step_state()` `test-check-domain.py:35-63` and pinned by exact set equality `schema_keys == DECLARED` `:127-131`. Schema re-counted at the pin: 22 properties, `required: [id,status]`, `additionalProperties: false`. (b) MEASURED + ADOPTED |
| SC-06 | automated | met | (a) vendored `tests/integration/fixtures/pre-t04-validate-digest.py.fixture`, non-`.py` suffix, no git/commit id; content control `:3193-3204` requires `DOCUMENTED_OPTIONAL` present AND `undeclared digest key` absent — either failing is a red case; comparison `:3207-3223` requires prior exit 0 AND current exit 2. (b) ADOPTED |
| SC-07 | automated | met | (a) `:3130-3136` — `len(errors) != 1` fails, so exactly ONE message for three rogue keys; all three names required `:3138-3146`. (b) ADOPTED |
| SC-08 | automated | **met** | **fresh, both seams — see below** |
| SC-09 | automated | met | (a) `:3160-3166` — `stop_hook_active: True` on SC-07's three-key return must exit 0. Discriminates: guard `validate-digest.py:1828` sits ahead of every `validate()` call, key check inside `validate()` at `:1407`; moving the check before the guard reddens `:3164`. Anchor note: the BRIEF's `:1744` is stale at the pin; graded on substance |
| SC-10 | automated | met | (a) `SCHEMAS["lead"]` requires `adequacy_notes` `validate-digest.py:209`; documented `harness-team/SKILL.md:264`; `run_documented_contract_cases` `:519-538` with the omitted-field discrimination group `:529-532`. (b) ADOPTED |
| SC-11 | automated | met | (a) both directions, separate fixtures `test-check-domain.py:76-91` (v1 undeclared key accepted `:85-86`; v2 refused and named `:87-91`). (b) MEASURED 13/13 exit 0 |
| SC-12 | inspection | met | **EXECUTED in this run — both halves below** |
| SC-13 | uat | **pending-operator** | below; no UAT artifact produced |
| SC-14 | — | **struck** | absent from the signed BRIEF; deleted during planning |
| SC-15 | automated | met | (a) four creation fixtures asserted separately `test-check-domain.py:135-153` (v2 accepted; v1, absent, string `"2"` each exit 2 naming `schema_version floor`, the string case also naming `string`) + the existing-v1-update acceptance `:156-164`, the row that reddens if the floor keys on the write. (b) MEASURED 13/13 exit 0 |
| SC-16 | automated | met | (a) **16/16** personas of `CONTRACT_SOURCES` `:297-314`, each its own gap evaluation `:2939-2941`, failure naming persona + key + source path; discrimination in the criterion's own stated mode — `DOCUMENTED_OPTIONAL["harness-documentor"].pop("stale_found")` in-process, case must then name `stale_found` `:2944-2951`. (b) ADOPTED |

## SC-08 — graded fresh, both seams, at the pin

The criterion demands the declaration route be named **by file and symbol** and asserted as a
**substring**. Both seams now do exactly that.

- **DIGEST seam** — `tests/integration/test-validate-digest.py:3138-3146`. The single
  undeclared-key message must contain every member of `tokens`, which at the pin is
  `("rogue_alpha", "rogue_beta", "rogue_gamma", "digest contract is closed", "validate-digest.py",
  "PASSTHROUGH", "DOCUMENTED_OPTIONAL", "SCHEMAS")`, enforced by
  `[f"three-key message omitted {token}" for token in tokens if token not in message]`. **File
  (`validate-digest.py`) and symbols (`PASSTHROUGH`, `DOCUMENTED_OPTIONAL`, `SCHEMAS`) are each
  required as substrings.** Closes the digest half.
- **STEP seam** — `tests/integration/test-check-domain.py:87-91`, case *"schema_version 2 refuses an
  undeclared step key, names it and gives its route"*:
  `strict.returncode == 2 and "undeclared step key" in strict.stderr and "rogue_step_key" in
  strict.stderr and "run-state-schema.json" in strict.stderr and "`evidence`" in strict.stderr`.
  **The route file `run-state-schema.json` and the symbol `` `evidence` `` are each required as
  substrings** — this is the assertion the c9 note found missing, and it is present at
  `984bd26b`. Emission side: `check-domain.sh:1671` head, `:1674` route, `:1682` pointer.
- **MEASURED here:** `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-check-domain.py` →
  **13/13 T-06 cases passed, exit 0, `ALL PASSED`**. The file is byte-identical between `984bd26b`
  and the worktree HEAD (`git diff --name-only 984bd26b HEAD` lists only `.harness/` artifacts), so
  the measurement is at the pin's source. Nothing on disk was changed.
- **AT-REST seam — does not need the assertion.** `tests/integration/test-check-state.py:51-54`
  asserts only `run`, `step` and `key` (`r1`, `strict-step`, `rogue_step_key`) and no route.
  **Ruling: SC-08 is satisfied without it.** SC-08 grades *rejection* text — a refused digest return
  (REQ-01) and a refused `steps[]` write (REQ-02). `check-state.sh`'s INV-16 is an at-rest **report**
  over already-written artifacts, not a rejection, and REQ-08 forbids acting on historical ones. The
  emission there does carry the route anyway (`check-state.sh:1526-1528`), so the behaviour is
  present-but-unasserted; recorded as a recommendation, not an unmet criterion.

## SC-12 — executed in THIS run, both halves

Cross-checked byte-for-byte against `plan.yaml:649-673` (T-10 `verify:`, literal block) before
running; identical. Run from the OWNER ROOT `/Users/molchairuangutai/GitHub/harness`.

- **POSITIVE** — command as written, no argument. Literal output line:
  `manifested 728 changed 0 vanished 0`. **Exit 0.** N = 728 ≥ 726; `changed 0`; `vanished 0`.
- **DISCRIMINATION** — the manifest copied to `/tmp/feat104-sc12-c11-mutated-manifest.txt` with the
  leading hexdigest character of ONE line (line 201) altered, passed as `argv[1]`. Output
  `manifested 728 changed 1 vanished 0`, naming
  `.harness/harness/features/FEAT-10-software-factory/runs/goalcheck2-product/digest.md`.
  **Exit 1.** No real run artifact was touched; the mutated copy is the whole proof.

## SC-13 — `pending-operator`, the sole remaining item

**In one line: the operator must read the diff of the four DEC-174 carve-out files —
`validate-digest.py`, `check-domain.sh`, `check-state.sh` and their tests — and confirm it changes
nothing beyond the declared contract.** Concrete items to look at: **CF-1** (unescaped `run_id` /
step-id interpolation in `check-state.sh`'s INV-16 at-rest message, `check-state.sh:1525-1526`,
security `med`, re-measured byte-identical this cycle) and **CF-4** (raw Python `None` reaching the
`schema_version` downgrade message, `check-domain.sh` downgrade branch near `:1608`, `low`). The c11
panel adds **Q14** (`med`): a declared step key with a type violation prints under the
*undeclared* head with a remedy that, followed literally, yields `evidence: {cycles: "3"}` accepted
at exit 0 while the step-level field is silently lost — one branch inside the carve-out.

## Anchor drift from the c9 note — every pointer re-located, none vanished

The `790023f0` fix inserted the `missing required step key` branch and its case, shifting anchors
below it. `check-domain.sh:1653-1658` → `:1663-1682`; `test-check-domain.py:85-87` → `:87-91`,
`:102-111` → `:111-118`, `:114-124` → `:122-132`, `:127-145` → `:135-153`, `:148-156` → `:156-164`;
`check-state.sh:1527-1529` → `:1526-1528`. All re-derived by content string. **No c9 pointer failed
to resolve** — but the c9 SC-08 verdict itself is falsified at this pin, which is why it was graded
fresh rather than carried.

## Not criteria — recommendations only

None is an unmet SC; the BRIEF states none of them. Each is routed in `open_questions` as a
RECOMMENDATION, and each judged new-vs-covered.

- **R1 — at-rest route assertion (NEW, uncovered).** `test-check-state.py:51-54` asserts no route
  string, though `check-state.sh:1526-1528` emits one. Outside SC-08's subject (see the ruling
  above); a one-line addition inside the DEC-174 carve-out whenever that file is next touched.
- **R2 — Q17, seam pinned by invocation path (COVERED by the panel, non-gating).**
  `undeclared step key` has two producers (`check-domain.sh:1671`, `check-state.sh:1526`); the step
  case discriminates because it fires a Write hook, not because the phrase is unique.
- **R3 — Q14 remedy prose (COVERED by the panel at `med`, advisory).** Carve-out fix; an operator
  decision, never a fix cycle.
- **R4 — Q9, the generic-`lead` archive exemption at `validate-digest.py:1407` has no test able to
  redden.** It does not falsify REQ-08 — the exemption is present and the behaviour demonstrated —
  but it is the standing regression risk on that requirement.

`git -C <worktree> status --porcelain` at the end of this run, literal: `?? …/notes/
research-FEAT-104-goalcheck-build-c11.md` and ` M …/observations/harness-pm.md` — this note and my
observations log, both feature-tree artifacts this run legitimately writes. **No tracked source or
test file is modified.**
