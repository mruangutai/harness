# GOAL-CHECK — FEAT-104, build/validate phase, pin `168f875f`

**BLUF. Nine of nine REQs are met and fourteen of fifteen live criteria are met at the pin. One
criterion is `unmet` and it is a PROOF gap, not a delivery gap: SC-08 requires the declaration route
to be named "by file and symbol … asserted as a substring" at BOTH seams; the digest seam is emitted
and asserted, the step seam is emitted (`check-domain.sh:1655-1658`, `check-state.sh:1527-1529`) and
asserted nowhere.** SC-12 was executed here — exit 0 over 728 manifested artifacts, and the
discrimination case reddened, naming the altered path. SC-13 stays `pending-operator` and gates ship.
SC-14 is `struck`. Everything graded at `git show 168f875f:<path>`; the two commits above the pin are
feature bookkeeping and were not read for content.

## REQ table

| REQ | verdict | pointer at `168f875f` |
|---|---|---|
| REQ-01 | met | `validate-digest.py:1407-1423` closes the key set inside `validate()`, reached at every tier; hook exit 2 asserted `test-validate-digest.py:3155-3159` |
| REQ-02 | met | creation floor `check-domain.sh:1586,1608` (`schema_version floor`), step check `:1653-1658`; T-06 `verify:` (`plan.yaml:443-449`) |
| REQ-03 | met | `run-state-schema.json:45-55` — `evidence` object, `propertyNames ^[a-z][a-z0-9_]*$`, scalar/scalar-array values only |
| REQ-04 | met | checked row-by-row against the documented enumeration in `notes/research-FEAT-104-planfix-c1.md:49-68`, **not** a summary: all 17 rows / 16 distinct names present with matching types at `validate-digest.py:248-280`; `prototype` carried by `NULLABLE` (`:54-61`); the documented `severity_max: info` divergence is corrected at `.omp/agents/harness-validator-lead.md:135` (`none|low|med|high|critical`) |
| REQ-05 | met | digest refusal names every key + route `validate-digest.py:1411-1423`; step refusal names every key + route `check-domain.sh:1653-1658` |
| REQ-06 | met | `stop_hook_active` guard `validate-digest.py:1828-1829` precedes every `validate()` call; written down as DEC-223 (`DECISIONS.md:7128` — "one-shot sufficient") |
| REQ-07 | met | `SCHEMAS["lead"]` requires `adequacy_notes` (`validate-digest.py:207-209`); documented `harness-team/SKILL.md:264`; generic-`lead` archive path keeps it optional `:1249-1250` |
| REQ-08 | met | archive exemption `validate-digest.py:1407` (`raw_persona != "lead"`); version-1 update accepted `test-check-domain.py:148-156`; SC-12 executed below — 728 artifacts, 0 changed, 0 vanished |
| REQ-09 | met | mechanical in BOTH directions over the 16 personas of `CONTRACT_SOURCES` (`test-validate-digest.py:297-314`): reverse `_t01_reverse_contract_gaps` `:2871-2879` driven per persona at `:2936-2941`, forward `run_documented_contract_cases` `:519-538`. Graded against the planfix enumeration, not a claim |

## SC table

| SC | `verify:` | verdict | evidence at the pin |
|---|---|---|---|
| SC-01 | automated/integration | met | lead rogue-key probe `test-validate-digest.py:3084-3089` + hook exit 2 `:3155-3159`; "exits 0 before the change" proven by the vendored pre-T-04 comparison `:3218-3222`. qa same-pin run: integration exit 0 / 70 files |
| SC-02 | automated/integration | met | **9/9** persona keys, each its own case: `canonical_probes` `:3173-3179` → per-canonical failure `:3084-3089`. Accepting fixture built FROM the documented block (`documented_block` parse `:3109-3116`), graded for all **16/16** `CONTRACT_SOURCES` personas `:3120-3127` |
| SC-03 | automated/integration | met | `test-check-domain.py:85-87` — exit 2, `undeclared step key`, and `rogue_step_key` named |
| SC-04 | automated/integration | met | both directions, three separate cases `test-check-domain.py:102-111` (identifier keys accepted; space-bearing key refused; nested mapping refused) |
| SC-05 | automated/integration | met | per item, all four groups: **16/16** documented fields (17 rows, `in_scope` twice) each accept+reject asserted `:2962-2976` × `:2918-2933`; **5/5** PASSTHROUGH rows × 3 assertions each `:2955-2959` × `:2889-2902`; `adequacy_notes` its own 3 assertions `:2905-2915`; **22/22** step keys (21 + `evidence`) individually present in the accepted payload `test-check-domain.py:36-63` and pinned by exact set equality against the schema `:114-124` |
| SC-06 | automated/integration | met | vendored fixture `tests/integration/fixtures/pre-t04-validate-digest.py.fixture` (non-`.py` suffix, no git, no commit id). Content control located `:3193-3204`: contains `DOCUMENTED_OPTIONAL` (verified 2 occurrences at the pin) and does NOT contain `undeclared digest key` (verified 0) — either failing is a red case, not a skip. Discrimination is real: `:3218-3222` requires prior exit 0 AND current exit 2 with the message, over 3 payloads `:3265-3274` |
| SC-07 | automated/integration | met | `:3130-3136` — exactly one undeclared-key message for three rogue keys (`len(errors) != 1` fails), all three names required `:3138-3146` |
| SC-08 | automated/integration | **unmet (PROOF)** | digest seam asserted `:3138-3146` (`validate-digest.py` + `PASSTHROUGH`/`DOCUMENTED_OPTIONAL`/`SCHEMAS`). Step seam: the text DOES name the route (`check-domain.sh:1655-1658`, `check-state.sh:1527-1529` — `run-state-schema.json` + `evidence`) but **no test asserts it**: the only occurrence of `run-state-schema` under `tests/` is the `open()` at `test-check-domain.py:117`; the refusal cases assert only `undeclared step key` and the key name (`:85-87`, `:105-110`), and `test-check-state.py:51-54` asserts run/step/key only. See Gaps |
| SC-09 | automated/integration | met | bypass asserted `:3160-3166` (exit 0 with `stop_hook_active` on SC-07's three-key return). Discrimination located: the guard is `validate-digest.py:1828-1829`, ahead of every `validate()` call, and the key check lives inside `validate()` at `:1407`; placing the check before the guard makes `:3164` red. **Anchor note:** the BRIEF cites `:1744`, which at the pin is docstring text inside `check_qa_matrix_claim` — the guard moved (it is `:1807` in the pre-change fixture). Graded on substance |
| SC-10 | automated/integration | met | `SCHEMAS["lead"]` requires `adequacy_notes` `validate-digest.py:209`; documented `harness-team/SKILL.md:264`; `run_documented_contract_cases` `:519-538` with the omitted-field discrimination group at `:529-532` |
| SC-11 | automated/integration | met | both directions, separate fixtures `test-check-domain.py:76-88` (version-1 undeclared key accepted; version-2 refused and named) |
| SC-12 | inspection | met | executed below — positive exit 0, discrimination exit 1 naming the path |
| SC-13 | uat | **pending-operator** | see below |
| SC-14 | — | **struck** | deleted during planning (`notes/research-FEAT-104-planfix-c1.md:165-173`); absent from the signed BRIEF |
| SC-15 | automated/integration | met | 4 creation fixtures asserted separately `test-check-domain.py:127-145` (v2 accepted; v1, absent, string `"2"` each exit 2 naming `schema_version floor`, the string case also naming the type) + the existing-v1-update acceptance `:148-156`, which is the row that reddens if the floor keys on the write |
| SC-16 | automated/integration | met | **16/16** personas of `CONTRACT_SOURCES` (`:297-314`) each evaluated on its own, failure naming persona + key + source path `:2878`; driven per persona `:2936-2941`. Discrimination located and matches the criterion's own stated mode: `DOCUMENTED_OPTIONAL["harness-documentor"].pop("stale_found")` in-process, then the case must fail naming `stale_found` `:2944-2951` |

Automated criteria are graded by (a) the discriminating assertion existing in the test source at the
pin and (b) qa's same-pin execution (`notes/qa-feat104-tip-168f875f.md`: unit exit 0 / 36, integration
exit 0 / 70, full canonical suite exit 0 / 106). No carve-out suite was run here.

## SC-12 — executed, both halves

Cross-checked the command against `plan.yaml:649-673` (T-10 `verify:`, literal block) before running;
byte-for-byte the dispatched string. Run from the OWNER ROOT `/Users/molchairuangutai/GitHub/harness`.

- **Positive** — command as written, no argument. Output `manifested 728 changed 0 vanished 0`,
  **exit 0**. N = 728 ≥ 726; manifest
  `.claude/worktrees/harness/FEAT-104-strict-digest-schema/.harness/harness/features/FEAT-104-strict-digest-schema/notes/run-artifact-manifest-base.txt`.
- **Discrimination** — the manifest copied to `/tmp/feat104-sc12-mutated-manifest.txt` with the
  leading hexdigest character of ONE line (line 401) altered, passed as `argv[1]`. Output
  `manifested 728 changed 1 vanished 0` and the named path
  `.harness/harness/features/FEAT-18-board-truth/runs/2026-08-13-06-validator/state.yaml`,
  **exit 1**. No real run artifact was touched; the mutated copy is the whole proof.

## SC-13 — `pending-operator`, and it gates ship

No harness run can close it: DEC-174 makes the four carve-out files ones a human must read, and the
BRIEF says no automated gate substitutes. Two concrete things for the operator's diff read:

1. **CF-4** — the raw Python `None` reaching the `schema_version` downgrade message in the
   omitted-on-update edge case (`check-domain.sh`, downgrade branch near `:1608`).
2. **CF-1** — unescaped `run_id` / step-id interpolation in `check-state.sh`'s INV-16 at-rest message
   (`check-state.sh:1525-1526`).

## Gaps

**One, and it is proof rather than delivery.**

- **SC-08, step-key seam — PROOF gap.** Owning surface: `tests/integration/test-check-domain.py`
  (and/or `test-check-state.py`) — inside the DEC-174 carve-out, so `main-session-direct`; no squad
  can take it (repo Expertise P-02). Behaviour is correct and verified by reading the pin: both
  refusals name the file `.claude/skills/harness/bin/run-state-schema.json` and the symbol
  `evidence`. What is missing is one substring assertion on that route text in the version-2 refusal
  case. Cost: one assertion beside `test-check-domain.py:85-87`. This is the second ruling in the
  SC-08 family — STATE.md Q4 raised the same shape for the digest half, which F3 closed in both
  emission and assertion; the step half was closed in emission only, so the narrower reading is
  substituting again (project Expertise P-06).

**Findings that bear on nothing graded here.** Q1/CF-1, Q2/CF-3, Q3/CF-2 and Q5/CF-4 are non-gating
operator decisions inside the carve-out and falsify no REQ and no SC: Q1 concerns a non-creation
downgrade comparison that SC-11/SC-15 deliberately leave writable; Q3 is the raw-persona at-rest
question whose F2 declination the panel upheld, and adopting it would strand
`runs/2026-09-09-02-qa-gate-validator/digest.md`, which REQ-08 forbids (reproduced by qa, §6);
Q2 is sequencing; CF-1 and CF-4 are the two items SC-13 asks the operator to look at.
qa's own coverage gap (REQ-08's generic-`lead` exemption has no test able to redden) does not
falsify REQ-08 — the exemption is present at `validate-digest.py:1407` and the behaviour it protects
was demonstrated — but it is the standing regression risk on that requirement.

## May the UAT now be generated?

Yes — SC-13 is the only thing left that a human can settle, and generating the UAT does not depend on
SC-08's missing assertion; but the ship decision must not be taken until SC-08's assertion lands,
because the criterion is `unmet` as written.
