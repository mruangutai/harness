# Code review — FEAT-104-strict-digest-schema — pinned `abff2a84..6126ac07`

BLUF: **PASS with notes.** Stage 1 spec compliance is clean, REQ-01..REQ-09 all MET with mechanically
verified evidence (I re-ran every DEC-174 suite myself and re-ran `code-grade.py` myself). Stage 2
finds one real, previously-unnamed fail-open gap (MED, not gating on its own) and three LOW
documentation/message-quality nits, all of whose remedies live inside DEC-174 carve-out files and so
route to the main session rather than being fixed here. Nothing rises to `must_fix`.

## Stage 1 — spec compliance (REQ-01..REQ-09)

- **REQ-01** (undeclared digest key rejected at every tier) — **MET.** The closed-set check is
  `validate-digest.py:1407-1424` (`if raw_persona != "lead": ... undeclared digest key(s)`), reached
  from `hook_mode()`'s call `validate(agent, text, ...)` where `agent` is always the raw
  `harness-*` type (`validate-digest.py:1996` region), so every one of the 9 `SCHEMAS` tiers is
  covered at the real enforcement point. `tests/integration/test-validate-digest.py` T-04 block:
  34/34 passed (I ran it). **Caveat carried to Stage 2 finding F1**: one secondary re-validation path
  (`check-state.sh:1590`) never exercises this check for lead digests, at any date.
- **REQ-02** (undeclared step key rejected; no new run can opt out) — **MET.** CLAUSE A
  (`check-domain.sh:1614-1667`, unconditional on `_valid_version`, so it runs on both create and
  update) + CLAUSE B / D-11 floor (`check-domain.sh:1589-1612`, gated on `_creating`). `SC-15`'s four
  fixtures (version 2 accept / version 1 refuse / absent refuse / string `"2"` refuse-naming-type) and
  the existing-version-1-update-accept case all pass — I ran `test-check-domain.py`: 11/11.
- **REQ-03** (declared container for step evidence) — **MET.** `run-state-schema.json`'s
  `properties.steps.items.properties.evidence` (identifier-pattern `propertyNames`, scalar/array
  values only) plus `harness-team/SKILL.md:57-64` documents the same rule to authors.
- **REQ-04** (legitimate-use fixed by documented blocks, not observed traffic) — **MET.**
  `PASSTHROUGH`/`DOCUMENTED_OPTIONAL` (`validate-digest.py:235-274`) are built exactly from D-02's
  five rows and D-10's sixteen distinct field names (I recomputed the count: 17 keyed rows minus the
  one duplicate name `in_scope` across `harness-security-reviewer`/`harness-ui-reviewer` = 16,
  matching plan.yaml T-01's own arithmetic).
- **REQ-05** (rejection names every key and its route) — **MET** at the digest tier
  (`validate-digest.py:1415-1424` names `PASSTHROUGH`/`DOCUMENTED_OPTIONAL`/`SCHEMAS` explicitly) and
  at the step tier (`check-domain.sh:1653-1657`, `check-state.sh:1525-1529`), though the two step-tier
  messages have already drifted in the detail they carry — see Stage 2 F2.
- **REQ-06** (re-prompt/one-shot behaviour is a decision, not an accident) — **MET.** D-07/DEC-208 are
  written down (`DECISIONS.md:7124-7127`, new DEC-223 paragraph "The one hole is named
  deliberately"), and SC-09 is pinned by a discriminating test (three-unknown-key payload with
  `stop_hook_active` exits 0) inside the 34/34 T-04 run above.
- **REQ-07** (`adequacy_notes` closes #37) — **MET.** `SCHEMAS["lead"]["adequacy_notes"]: list`
  (`validate-digest.py:209`), required; documented at `harness-team/SKILL.md:264` with the semantics
  sentence directly beneath it.
- **REQ-08** (historical artifacts unrewritten) — **MET, independently re-verified.** I ran T-10's own
  verify script at the owner root against the committed baseline manifest: `manifested 728 changed 0
  vanished 0`, exit 0. The 356 pre-existing runs stay `schema_version: 1` and untouched
  (`check-state.sh:1483-1485` census comment, dated).
- **REQ-09** (documented-vs-declared agreement checked mechanically, both directions) — **MET.**
  `test-validate-digest.py`'s `_t01_reverse_failures` (`:2938-2952`) is a genuine dynamic mutation
  test: it pops `DOCUMENTED_OPTIONAL["harness-documentor"]["stale_found"]` from the **loaded module
  object**, reruns the reverse-contract scan, asserts the gap names `stale_found`, then restores it in
  a `finally`. Not prose. Confirmed by running the suite: `ok [T-01] every documented key is
  declared`.

No requirement is unmet, partially met, or missing a corresponding change. SC-14 struck per
planning ruling — correctly absent from the diff, not reported as a gap.

## Stage 2 — code quality

### 1. `code_grade`, measured by me at the pin
```
python3 .agents/skills/harness/bin/code-grade.py --base abff2a84 --head 6126ac07
```
Exit **0**. 42 changed functions reported (`grep -c '^FUNCTION'` = 42), **zero** `SEVERITY:` lines,
**zero** `RESULT: FAIL`, **zero** grade-1 or grade-2 records. `code_grade: pass`, matching the
orchestrator's pre-measured figure exactly — I did not take that figure on faith, I reran it.

### 2. Fail-open hunt

1. **Does the unknown-key rejection reach exit 2 on every tier, or is one still ignored?**
   Reached at the true enforcement point (SubagentStop hook) for all 9 tiers — confirmed above. **But
   there is a tier that is permanently blind to it**: `check-state.sh:1590` calls
   `_vd_mod.validate("lead", _dtext)` for **every** completed run whose `host` is in `LEADS`
   (`check-state.sh:1396`) — not only historical ones, and not gated by any date or
   `schema_version`-style marker. `validate-digest.py:1407`'s skip (`if raw_persona != "lead":`) is
   written to keep **historical** archived digests readable
   (`validate-digest.py:1404-1406`'s own comment), but the call site cannot tell historical from
   current: `_host` (`check-state.sh:1483`) **is** the real raw persona
   (`harness-eng-lead`/`harness-product-lead`/`harness-validator-lead`) and is sitting right there,
   unused, in favor of the literal string `"lead"`.
   **Concrete failure scenario:** a lead is re-prompted with `stop_hook_active` set (the acknowledged
   D-07/DEC-208 hole) and its return still carries an invented key. The hook returns 0 by design. The
   resulting `digest.md` — now containing that key — is later swept by `check-state.sh`'s INV-15 check
   once the run completes. That sweep reports the digest as satisfying "the lead digest contract"
   (no `bad.append` fires), because `raw_persona == "lead"` there unconditionally skips the very check
   this feature built. DEC-223 explicitly names the `stop_hook_active` hole as the *one* deliberate
   opening; this second hole is not named anywhere. **Severity: med** — it only fires after the
   already-acknowledged one-shot hole is exploited (compounding, not a new entry point), and the
   primary hook-time gate is unaffected; but it means the feature's own "closed contract" claim is
   not actually re-checked by the one mechanism (`check-state.sh`) that exists specifically to catch
   drift that slipped past the hook. Remedy is passing `_host` instead of `"lead"` at
   `check-state.sh:1590`, gated on some era marker so historical files stay exempt — that edit is
   inside `check-state.sh`, a DEC-174 carve-out. **route: main-session.**
2. **Is the `stop_hook_active` bypass exactly where the plan says, and no wider?** Confirmed exactly:
   `validate-digest.py:1827` (`if d.get("stop_hook_active"): return 0`) returns **before** any call to
   `validate()` and before the T-09/#551 registry logic — not widened to skip anything else. This
   matches D-07/SC-09 precisely.
3. **Does the step-key refusal fire on CREATE and WRITE?** Yes on both — CLAUSE A
   (`check-domain.sh:1614-1667`) is gated only on `_valid_version`, independent of `_creating`. One
   coverage gap, not a code defect: `test-check-domain.py` exercises the undeclared-step-key rejection
   only via `_fire_new` (create path); no fixture exercises it against an **existing** `schema_version:
   2` file being updated. The code is structurally indifferent to `_creating`, so this reads as correct
   by construction, but it is untested on that branch. Info-level, not gating.
4. **Does the floor reject omitted `schema_version` and the string `"2"` distinctly?** Yes —
   `check-domain.sh:1594-1607` computes a distinguishing `_version_problem` for each: `"is absent"`,
   `"has type string, not integer"`, `"is N, below 2"`. `test-check-domain.py`'s
   `_floor_creation_cases` (`:127-145`) asserts all four fixtures separately and I reran them: 11/11
   passed, including `"schema_version floor refuses string 2 and names the type"`.

### 3. Discrimination — is red actually exercised, or only described?

- **SC-06** — genuinely dynamic, not prose. `run_t08_revision_proof`
  (`test-validate-digest.py:3262-3298`) writes the vendored fixture bytes to a real temp
  `validate-digest.py` file and runs it as a **real subprocess** (`subprocess.run([sys.executable,
  prior_path, "--hook"], ...)`) against three unknown-key payloads, asserting `returncode == 0`
  there, then runs the **same** payloads against the current file via the same subprocess mechanism
  asserting `returncode == 2` and the literal message. I re-ran the fixture's own provenance
  assertions independently: `grep DOCUMENTED_OPTIONAL` on the fixture matches (T-01 present),
  `grep "undeclared digest key"` on the fixture does not match (T-04 absent). Both directions
  genuinely execute code; this is real, not a claim.
- **SC-12** — genuinely red-capable, verified by me directly (not accepted on report). I ran T-10's
  exact verify script at the owner root against the checked-in baseline: `manifested 728 changed 0
  vanished 0`, exit 0. The comparator is a straight `sha256(open(path).read()) != want` per manifested
  line — it discriminates by construction; I did not additionally fabricate a corrupted-manifest copy
  myself (no write access outside my note path), but the logic leaves no path by which a changed byte
  would fail to redden it.
- **SC-16** — genuinely dynamic. `_t01_reverse_failures` (`test-validate-digest.py:2938-2952`) pops
  `stale_found` out of the **live, loaded** `validator.DOCUMENTED_OPTIONAL["harness-documentor"]`
  dict, reruns the reverse-contract scan against that mutated state, asserts the gap names
  `stale_found`, restores the key in a `finally`. This is an executed mutation-and-detect, not a
  described claim.

### 4. SIMPLIFY S2 and S4 — independent severity, not inherited

- **S2** (`check-domain.sh:1653-1657` vs `check-state.sh:1525-1529` — one shape, two hand-written
  enforcement layers whose messages have drifted): **independently confirmed real** — I read both
  strings myself. Check-domain's message adds the evidence-value shape rule ("a lowercase identifier
  key and a scalar or scalar-array value"); check-state's does not. **My severity: LOW, does not
  gate.** Neither message is wrong or under REQ-05's bar (each names every offending key and a valid
  declaration route), and the actual enforced key set comes from the one shared
  `run-state-schema.json` at runtime in both gates — only the human-facing help text differs, so this
  is a maintainability cost (next drift goes unnoticed, no test pins the two strings equal), not a
  behavioral one. A concrete but narrow scenario: an agent whose evidence value is a nested mapping,
  caught only by `check-state.sh`'s sweep, is told to "put per-dispatch facts under evidence" — which
  it already did — without being told *why* that placement is still wrong (nested objects refused).
  Fixing this touches two DEC-174 carve-out files. **route: main-session.**
- **S4** (three lead-facing files carrying a byte-identical "never a new digest key" sentence, one of
  which explicitly says "not restated here" about its return contract): **independently confirmed
  real** — I read `harness-eng-lead.md:110-113`, `harness-product-lead.md:92-95`, and
  `harness-team/SKILL.md:274-277`; the first two are byte-identical to each other and near-identical
  to the third; `harness/SKILL.md:42-44` paraphrases the same clause a fourth time. This is, however,
  **exactly what T-03's verify demanded** (`grep -q 'never a new digest key'` across all six named
  files) and traces to a decided, signed plan step (D-02/T-03) — it is not an accident the panel
  missed. **My severity: LOW, does not gate.** The "not restated here" sentence refers to the DIGEST
  *field/block structure*, not this separate key-discipline reminder, so it is not a literal
  self-contradiction, but it is real duplication inside one persona's own context (an eng-lead reads
  both `harness-eng-lead.md` and `harness-team/SKILL.md` on the same spawn) with nothing enforcing the
  four copies stay identical if the wording ever needs to change — unlike the field-name contract,
  which the bidirectional T-01/SC-16 test does enforce mechanically. Fixing this touches the lead
  agent files, an explicit DEC-174 carve-out per this dispatch's own constraints. **route:
  main-session.**

### Minor / info (non-gating)

- `test-validate-digest.py:3297` (`run_t08_revision_proof`) prints `f"{10 - len(failures)}/10 ..."`
  but the function performs 12 distinct checks (3 revision payloads + 6 PASSTHROUGH/adequacy_notes
  replays + 3 non-passthrough-field checks), not 10. Purely a stale diagnostic denominator — the
  actual pass/fail gating uses `return len(failures)`, unaffected — but it is a label asserting a
  coverage count that does not match the code beside it.
- `run-state-schema.json`'s top-level `additionalProperties: false` is declared but never consulted
  by either gate (`check-domain.sh`/`check-state.sh` only load `properties.steps.items`) — inert
  documentation, not a live enforcement surface. This matches the plan's explicit instruction that
  `CHECKPOINT_KEYS` stays the top-level authority, so it is not a defect; flagging only so a future
  reader does not assume the top-level shape is machine-enforced here. Same territory as SIMPLIFY's
  S3 (pre-existing triplication, correctly out of this diff's scope).

## Verdict

PASS. No `must_fix`. `severity_max: med` (F1 above), which does not on its own cross the FAIL bar
under this protocol (`must_fix` non-empty or `severity_max >= high`). All actionable remedies land
inside DEC-174 carve-out files and are routed to the main session rather than attempted here.
