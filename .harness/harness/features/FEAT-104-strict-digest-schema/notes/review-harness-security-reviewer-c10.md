# Security review — FEAT-104-strict-digest-schema — panel c10 @ 790023f0

**VERDICT: PASS.** `must_fix` is empty at this pin. No new finding. Every security-relevant source
file (`check-domain.sh`, `check-state.sh`, `validate-digest.py`, `run-state-schema.json`) is
**byte-identical** to the c9 pin (168f875f) — the entire delta between c9 and c10 in non-feature-
directory files is `tests/integration/test-check-domain.py` at exactly `+4/-2` (verified with
`git diff --stat 168f875f..790023f0`), matching the dispatch's claim precisely. c9's finding set
therefore carries forward unchanged; this review re-derived it independently rather than trusting
the carry-forward, and confirms it.

## Census (measured, not forecast)

`git diff --stat origin/main..790023f0`: 75 files, +10697/-31. Read/diffed directly:
- **In scope, has security surface** — read every hunk: `check-domain.sh` (+102, write-time gate),
  `check-state.sh` (+54, at-rest sweep), `validate-digest.py` (+94/-... , agent-return validator),
  `run-state-schema.json` (new file, +76, declarative JSON Schema consumed by both gates), the 3
  `.claude/agents/harness-*-lead.md` files, `harness-team/SKILL.md`, `harness/SKILL.md`,
  `DECISIONS.md`/`DECISIONS-INDEX.md`/`SPEC.md` (DEC-223 write-up).
- **In scope, test-only, behavior-relevant** — read and ran: `tests/integration/test-check-domain.py`
  (+4/-2, the SC-08 route-naming assertion this panel exists to re-check),
  `tests/integration/test-check-domain-artifact.py` and `test-check-domain-grant.py` (fixture
  `schema_version: 1` → `2` bumps so pre-existing cases still isolate what they tested, no new
  assertions), `tests/integration/test-check-state.py` (+82, new INV-16 cases),
  `tests/integration/test-validate-digest.py` (+507, new PASSTHROUGH/DOCUMENTED_OPTIONAL/undeclared-
  key cases).
- **Out of scope, no security surface** — 55 note/receipt/observation/plan.yaml files under
  `.harness/harness/features/FEAT-104-strict-digest-schema/`: prose records, not consumed by any
  gate or by an agent's untrusted-input path. `tests/integration/fixtures/pre-t04-validate-digest.py.
  fixture` (+2017): inert vendored bytes for SC-06's hermetic red-control, never executed as a
  module (confirmed by c9, re-checked: it is loaded as text into a temp file and run as a
  subprocess target, not imported).
- **`tests/unit/`**: zero files touched (`git diff --stat origin/main..790023f0 -- tests/unit/`
  returned empty) — nothing to review there at this pin.
- Bookkeeping commit `790023f0..3321bcdd`: `git diff --stat` shows 8 files, every one under
  `.harness/harness/features/FEAT-104-strict-digest-schema/` (STATE.md, feature.json, one new note,
  4 new receipts, one observations file) — confirms the claim that it touches only the feature's own
  directory.

## What the diff actually does (spec compliance)

`check-domain.sh` adds two write-time checks to the `state.yaml` branch: (1) a `schema_version`
floor — a **new** checkpoint must declare `schema_version >= 2`, denied otherwise (REQ-02); a
downgrade from an already-strict prior checkpoint is also denied; (2) for a `schema_version: 2`
document, the `steps[]` array is validated against `run-state-schema.json`'s closed step shape via
`jsonschema.Draft202012Validator`, with `evidence:` as the one governed free-form container
(lowercase-identifier keys, scalar/scalar-array values, `propertyNames` pattern-enforced).
`check-state.sh` mirrors the same schema at rest (INV-16) for `schema_version >= 2` runs already on
disk. `validate-digest.py` adds `PASSTHROUGH`/`DOCUMENTED_OPTIONAL` typed tables and a closed-set
check (`undeclared = sorted(set(seen) - legal_fields)`) that rejects any digest key outside a
persona's declared+documented set, in one message naming every offending key (REQ-05/SC-07).
Executed at this pin: `test-check-domain.py` 12/12, `test-validate-digest.py` 55+34+10 = ALL PASSED,
`test-check-state.py` 3/3 — all green (`env -u HARNESS_AGENT_TYPE`).

**SC-08 STEP-KEY seam, the reason this panel re-ran:** the new assertion clauses
(`"run-state-schema.json" in strict.stderr` and `` "`evidence`" in strict.stderr ``) exercise a real
substring in the actual denial message (`check-domain.sh`'s step-schema block: "A recovery field is
declared in .claude/skills/harness/bin/run-state-schema.json; a per-dispatch fact goes under
`evidence`..."). Confirmed live, not by inspection alone: the case is green in the 12/12 run above.
**Test-only change — it asserts against existing, unaltered denial text; it does not touch any
trust boundary.**

## Message-injection / audit-record spoofing — traced every new interpolation

- `check-domain.sh` step/evidence offending-key names: `", ".join(repr(key) for key in sorted(...))`
  — `repr()` quote-escapes; safe.
- `check-domain.sh` downgrade message: `{_version!r}` explicit repr; `_prior_version` is
  type-constrained to a plain positive int by `_prior_is_strict` before interpolation — safe.
- `check-state.sh` INV-16 offending-key list `_names`: Python list — `str()` of a list already
  `repr()`s each element — safe.
- `validate-digest.py` undeclared-key names: `", ".join(repr(field) for field in undeclared)` — safe.
- **`check-state.sh` INV-16's `run_id`/step `id`** (`f"... run {sdoc.get('run_id', '<unknown>')}
  step {_step_id}: ..."`, `:1525`): interpolated as **bare strings**, no `!r`. This is **CF-1**
  (c9's SEC-C9-01), re-verified present at this exact byte offset — **carried, unchanged**, not a
  new finding. *Concrete failure scenario, restated from c9, still valid:* an actor who can place a
  `state.yaml` on disk without going through the `Write`/`Edit` hook (the pre-existing, separately-
  accepted **DEC-85** Bash-write bypass, confirmed still standing in `DECISIONS.md` today —
  serialization + `isolation: worktree` is the real write-safety mechanism, the hook is a
  guardrail, `bash-write-guard.sh` narrows only the casual case) sets `run_id` or a step `id` to a
  string carrying ANSI/terminal control bytes. At the next `/harness` entry, `check-state.sh`'s
  INV-16 sweep prints that value unescaped into the operator's terminal — the audit line meant to
  flag the schema violation can itself be overwritten or hidden on-screen. Severity **med**: it
  requires the already-out-of-scope Bash-write precondition, and the outcome is a visual/terminal
  spoof of one report line, not privilege change or data loss. Remedy is a one-line `{sdoc.get(
  'run_id', '<unknown>')!r}` / `{_step_id!r}` change (or list-wrapping to match `_names`'s existing
  pattern) — inside the DEC-174 carve-out, routed to the next main-session touch of this file, not
  gating this panel.

## Fail-open / fail-closed sweep of the new gate logic

- `check-domain.sh`'s new step-schema block wraps the whole `jsonschema` load-and-validate in
  `except Exception as _schema_exc:` and **denies** ("run-state schema CANNOT be checked; the write
  is denied") — fail-**closed**. Correct: a checker that cannot run must never be why a write
  passes, matching the sibling `feature.json`/`feature_schema` branch's own documented rule earlier
  in the same file.
- The file's **pre-existing** (not touched by this diff) `_no_parser: return out` early exit inside
  the `state.yaml` branch — reached only when PyYAML itself is unavailable, i.e. a bootstrap-grant
  session before dependencies are installed — sits **above** both new FEAT-104 blocks in source
  order. It therefore fail-**opens** the entire `state.yaml` shape check, including the new
  `schema_version` floor and the closed step schema, exactly as it already fail-opened DEC-154's
  key-whitelist check before this feature. This is not a new gap: it is documented in-file (line
  ~1554-1560) as a deliberate, user-ruled trade-off — "no line-scan alternative, no degraded mode"
  — with a stated compensating control: a malformed checkpoint written during a bootstrap grant is
  still caught, named, and reported by `check-state.sh`'s at-rest sweep at the next entry, which now
  (this diff) also carries the same closed-schema check via INV-16. The new FEAT-104 write-time
  checks inherit the pre-existing bootstrap-grant exemption without widening its scope or weakening
  its compensating control — assessed and dismissed, not a finding.
- **F1** (`_version_decreased` downgrade refusal): present, unchanged, test-confirmed green
  ("schema_version floor refuses a version-2 checkpoint downgrade") — **CLOSED**, confirmed.
- **F3** (undeclared-key rejection naming `validate-digest.py` and its symbols; three-rogue-key
  case): present, unchanged, test-confirmed green (34/34 T-04 undeclared-key cases, including the
  one-message-for-three-keys case) — **CLOSED**, confirmed.
- **F2** (generic `lead` archive-reader exemption in `validate-digest.py`): topology re-traced, not
  relitigated. `check-state.sh:1536` calls `_vd_mod.validate("lead", _dtext)` with the **literal**
  string `"lead"` — this is the only call site using that literal. `validate-digest.py`'s
  `hook_mode()` (SubagentStop, unchanged by this diff) reads `agent = d["agent_type"]` — the real
  dispatched persona (e.g. `"harness-eng-lead"`) — and passes that raw value into `validate()`, so
  `raw_persona != "lead"` for every live return and the undeclared-key check applies to it in full.
  The exemption is reachable only through the archive-reader path check-state.sh uses for historical
  digests, exactly as REQ-08/SC-12 requires. **DECLINED disposition stands**; not reopened.

## No secrets, no new injection surface

Full-diff grep for credential-shaped strings (`api[_-]?key|secret|password|token|BEGIN (RSA|OPENSSH|
PRIVATE)|AKIA...|ghp_...|xox[baprs]-`) across all 75 files: only incidental hits ("design token",
"coverage tokens", test-assertion identifiers). No shell/SQL/template construction touches this
diff — `run-state-schema.json` is static declarative JSON consumed via a `sys.argv`-derived selfdir
path in both scripts (pre-existing, BASH_SOURCE-anchored, no traversal). The 3 lead-agent `.md` and
2 `SKILL.md` changes are dispatcher/prompt prose with no execution surface.

## Carried, unchanged (not re-raised as new)

- **CF-1** (`check-state.sh` INV-16 bare `run_id`/step-id interpolation, med): confirmed present,
  see above.
- **DEC-85** (Bash-write bypass, standing accepted risk): confirmed still documented in
  `DECISIONS.md` as the accepted trade-off (serialization + `isolation: worktree` is the real
  write-safety mechanism; `bash-write-guard.sh` narrows the casual case, does not void it).

## Threat model

| boundary | STRIDE | mitigated |
|---|---|---|
| state.yaml write vs. check-domain.sh schema_version floor/downgrade | Tampering | true |
| state.yaml write vs. check-domain.sh closed step schema | Tampering | true |
| bootstrap-grant (`_no_parser`) vs. new FEAT-104 write-time checks | Tampering | false, precondition-absent outside first-session bootstrap; compensating control is check-state.sh's at-rest INV-16 sweep, itself part of this diff |
| Bash-authored state.yaml vs. check-state.sh INV-16 report echo (CF-1) | Spoofing | false, gated behind the pre-existing DEC-85 precondition |
| at-rest digest sweep vs. raw persona (F2) | Tampering (defence-in-depth) | true — literal-"lead" call site confirmed singular; live returns use their raw persona |
| digest undeclared-key rejection vs. crafted key names | Information disclosure / injection | true — repr() on every offending-key surface |
| run-state-schema.json path resolution, both scripts | Tampering (path traversal) | true — selfdir-anchored |

## Open questions

- Q1 (from c9, still open, non-blocking): CF-1's one-line fix (`!r}` on `run_id`/`_step_id` in
  `check-state.sh`'s INV-16 message) is inside the DEC-174 carve-out — route to the next
  main-session touch of that file.
