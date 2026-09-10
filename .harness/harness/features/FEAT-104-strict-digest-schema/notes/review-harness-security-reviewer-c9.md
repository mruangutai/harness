# Security re-grade — FEAT-104-strict-digest-schema @ 168f875f (origin/main..168f875f)

## BLUF
Both prior high/med findings that touched the write-time guard and the digest-key message are
**CONFIRMED FIXED at source and by execution** (F1 high → fixed, F3 med → fixed). F2 (med, the
raw-persona digest sweep gap) was correctly declined by the operator — I independently reproduce the
stranding evidence and it holds; there is a narrower, non-gating residual worth naming. This cycle's
own audit surfaces **one new med finding**: `check-state.sh`'s new INV-16 at-rest message echoes the
attacker-controlled `run_id`/step `id` fields **without the `repr()`/list-wrapping every sibling
interpolation in this same diff uses**, letting a step author with an already-accepted bypass route
(Bash-authored `state.yaml`) inject raw ANSI/control bytes into the operator-facing sweep report — a
demonstrated terminal-escape spoof of the very audit line meant to flag it. Non-gating: reachable only
through the pre-existing, out-of-scope Bash-write bypass, but reported at full detail since it is new
code and inconsistent with this diff's own hardening pattern. `severity_max: med`, `must_fix: []`.

## Scope — measured, not assumed
Scoped **IN**. Measured: read every hunk of `check-domain.sh` (+102), `check-state.sh` (+54),
`validate-digest.py` (+94/-5) and `run-state-schema.json` (+76, new); ran `test-check-domain.py`
(12/12) and `test-validate-digest.py` (full suite, ALL PASSED including 34/34 T-04 and 10/10 T-08)
against the pin to execute, not merely read, the two prior findings under re-grade. Grepped the fixture
for the two sentinel strings SC-06 depends on. Traced every new f-string/`%s` interpolation of
agent-authored `state.yaml`/digest content in both shell-hosted Python blocks for escaping. Scoped OUT
(assessed, no surface): the 8 agent-template/doc files and the cross-feature `plan.yaml` line — prose
only, byte-identical `.claude`/`.omp` twins, no processing of untrusted input.

## F1 — schema_version downgrade — CONFIRMED FIXED, executed
`check-domain.sh` now reads the **on-disk prior document** for every state.yaml write (the
`if absolute_path is not None:` block that already loaded `prior_doc` for the run-identity checks),
computes `_prior_is_strict` from the prior's own `schema_version` (int ≥ 2), and refuses (`exit 2`,
message substring `schema_version downgrade`) any write whose proposed `schema_version` is missing,
non-int, boolean, or numerically less than the prior value — this fires **regardless of `_post`**, so
it binds the blocking PreToolUse path, not only the post-hoc report. `check-state.sh`'s at-rest sweep
is unchanged and still keys on the *current* on-disk value, but that is now safe: the write-time gate
makes a strict run's `schema_version` monotonically non-decreasing, so the sweep's self-declared key is
no longer reachable by the downgrade route (matches the retired Q2 reasoning in the shared context).
- Verified adversarially at source: a proposed `schema_version: "2"` (string) against a strict prior
  also refuses (`not isinstance(_version, int)` short-circuits `_version_decreased` to `True`) — a
  type-confusion bypass of the numeric comparison does not exist.
- Verified by execution: `python3 tests/integration/test-check-domain.py` → `12/12 T-06 check-domain
  cases passed`, including `"schema_version floor refuses a version-2 checkpoint downgrade"` asserting
  both `returncode == 2` and the message substring.
- **Bypass hunt (per dispatch item 1), beyond the already-escalated Bash-write residue:** checked the
  `_no_parser` early-return in `check-domain.sh` (fires when PyYAML is unavailable in a bootstrap-grant
  session, `return out` *before* any of the new checks). This is **pre-existing** code (predates
  FEAT-104; the surrounding comment block documents a REMOVED line-scan fallback from a prior PR), not
  introduced by this diff, and is already covered by `check-state.sh`'s at-rest sweep catching the
  malformed file at the next `/harness` entry. No other route found: the downgrade check is unconditional
  within `RE_STATE_YAML.match(rel)`, independent of `_post`, and the earlier YAML-parse-failure/dup-key
  branches all `return out` before landing a write, so they cannot smuggle a downgrade through either.

## F2 — raw-persona digest sweep gap — CORRECTLY DECLINED, residual risk named
`check-state.sh:1590` still calls `_vd_mod.validate("lead", _dtext)` with the **literal** string
`"lead"`, not `_host` (the real raw persona already held at `check-state.sh:1577`) — unchanged by this
diff. I independently reproduced the stranding evidence rather than accepting it on relay: I read
`runs/2026-09-09-02-qa-gate-validator/digest.md` (a real FEAT-104 artifact, `host:
harness-validator-lead`, `team: qa-gate`) and its digest legitimately carries `suite`, `failures`,
`kinds` — none of which are in `SCHEMAS["lead"]` or `PASSTHROUGH["lead"]`. Simulating the raw-persona-
aware remedy (`validate("harness-validator-lead", ...)` instead of `validate("lead", ...)`) sets
`raw_persona != "lead"`, which turns on the undeclared-key closure (`validate-digest.py:1408`) and would
flag exactly those three legitimate, pre-closure-contract fields — reproducing the operator's stranding
claim on the actual file, not a hypothetical.
- **Why the remedy cannot simply switch to `_host`:** unlike `state.yaml`, a `digest.md` carries no
  `schema_version`-equivalent discriminator distinguishing "written under the closed contract" from
  "written before it." `state.yaml`'s step sweep is safe to apply universally because `schema_version`
  is a hard version floor introduced at creation (F1's fix makes it monotonic); no analogous marker
  exists on digests, so a raw-persona-aware sweep cannot tell a legitimate pre-change digest from a
  post-change violation. This makes F2's naive remedy a REQ-08/SC-12 violation as claimed, and I find no
  remedy in the DEC-174 carve-out that closes the gap without either stranding historical artifacts or
  inventing a new discriminator field (out of scope for this cycle). **F2 stays declined.**
- **Residual, non-gating risk, stated explicitly:** the decline leaves the at-rest sweep blind to raw
  persona for *all* lead digests, historical and new alike. Combined with the already-accepted
  `stop_hook_active` one-shot passthrough (SC-09/DEC-208, deliberately open), an undeclared key that
  slips onto a **new** lead digest through that one-shot exemption is never later caught by
  `check-state.sh`, unlike the symmetric `state.yaml` step case (which the sweep does catch at rest,
  because `schema_version` gives it a safe universal predicate). This is a known shape of gap
  (defence-in-depth only, single-layer enforcement), not a new one, and does not gate.

## F3 — SC-08 file+symbol naming — CONFIRMED FIXED, executed
`validate-digest.py:1416` now emits `"Declare the field in .claude/skills/harness/bin/validate-digest.py:
..."` ahead of the `PASSTHROUGH`/`DOCUMENTED_OPTIONAL`/`SCHEMAS` tokens. The test
(`test-validate-digest.py::_t04_three_key_failures`) now asserts the literal token
`"validate-digest.py"` alongside the three symbol names and the three offending keys — the exact gap
the prior review flagged as vacuous is closed both in the message and in its test.
- Verified by execution: `python3 tests/integration/test-validate-digest.py` → `ALL PASSED`, `34/34
  T-04 undeclared digest key cases passed`, `10/10 T-08 revision and lead replay cases passed`.

## New — SEC-C9-01 (med, non-gating): unescaped run_id/step-id echo in check-state.sh's INV-16 message
`check-state.sh`'s new sweep (`:1483-1531`) builds, for every schema-invalid step on a
`schema_version ≥ 2` run:
```
bad.append(f"INV-16: {rel}: run {sdoc.get('run_id', '<unknown>')} step {_step_id}: "
           f"undeclared step key or evidence shape {_names} — ...")
```
`sdoc.get('run_id', ...)` and `_step_id` (`str(_step.get("id") or ...)`) are interpolated **as bare
strings**, with no `!r`/`repr()`. Both `run_id` and step `id` are plain, pattern-free `"type": "string"`
fields in `run-state-schema.json` (unlike `evidence` keys, which are pattern-constrained, and unlike
`_names`, the offending-key list, which the code wraps in a Python list — `str()` of a list already
`repr()`s each element, which is why key names are safe). This is **new code in this diff** and breaks
the pattern every other attacker-controlled value in the *same* diff follows: `check-domain.sh`'s
sibling message uses `repr(key) for key in sorted(...)` explicitly; `check-domain.sh`'s downgrade
message uses `{_version!r}` explicitly; `check-state.sh`'s own `_names` is list-wrapped. Only `run_id`
and step `id` in this one new message escape that convention.
- **Concrete failure scenario.** *Actor:* anyone who can place a `state.yaml` on disk without going
  through `check-domain.sh`'s Write/Edit hook — the already-acknowledged, out-of-scope Bash-authored-
  write route (DEC-85 residue). *Input:* a `schema_version: 2` run whose `steps[]` carries one step
  with an undeclared key (or any other JSON-Schema violation) **and** `id:
  "legit-step\x1b[2K\x1b[1A\x1b[2K"` (verified locally: interpolating this value into the exact f-string
  above and printing it collapses/erases the preceding terminal line on render — demonstrated with a
  throwaway Python repro, not asserted). *Wrong observable outcome:* when an operator later runs the
  `/harness` entry sweep, the INV-16 line meant to warn them that this run escaped enforcement is
  itself erased or overwritten on their terminal — the audit channel built to surface the Bash-write
  bypass can be made to hide its own finding.
- **Why med, not high:** exploitation requires the precondition already carved out of this review's
  scope (Bash write access bypassing all Write/Edit-tool enforcement) — no new privilege is gained, no
  new write capability is opened. What is new is that the observability of an *existing* accepted risk
  can now be selectively defeated. **Non-gating**, reported for the next touch of `check-state.sh`; the
  fix is a one-line `!r}`/`{_step_id!r}` and `{sdoc.get('run_id', '<unknown>')!r}` change, or list-
  wrapping to match `_names`'s existing pattern. DEC-174 carve-out — main-session route only.

## Fixture assessment — `tests/integration/fixtures/pre-t04-validate-digest.py.fixture` (+2017)
Confirmed inert, unchanged from the c7 read: grepped the repo tree, the only references are
`test-validate-digest.py`'s own T-08 regression case (writes the bytes to a tempdir and runs them as a
subprocess to prove pre-change/post-change behavior differs) and `plan.yaml`/notes documentation. No
production code path opens or executes this file. Supply-chain framing: it is checked-in, human-
reviewed source like any other file in the diff — its risk profile is ordinary code review, not a
downloaded/unpinned dependency. Drift-hides-a-regression is self-defeating by construction: SC-06's own
discrimination check greps the fixture for the presence of `DOCUMENTED_OPTIONAL` and the **absence** of
`undeclared digest key` (confirmed both hold at this pin: `has DOCUMENTED_OPTIONAL: True`, `has
undeclared digest key: False`) — a fixture that drifted toward matching the current validator would
fail that assertion immediately, so it cannot silently decay into a no-op.

## Bypass-route section for the write-time guard
- **New routes found in this diff:** none. The downgrade fix (F1) applies unconditionally inside
  `RE_STATE_YAML.match(rel)`, independent of `_post`, `_creating`, and prior parse-failure branches.
- **Pre-existing, already-escalated, not re-raised:** Bash-authored `state.yaml` writes bypass
  `check-domain.sh` entirely (DEC-85's acknowledged sharp edge) — this is the precondition for
  SEC-C9-01 above, not a new finding in itself.
- **Pre-existing, newly checked, confirmed non-issue:** the `_no_parser` bootstrap-grant early return
  in `check-domain.sh` predates this diff and is unconditionally caught by `check-state.sh`'s next
  sweep pass, same as before.
- Path arguments to the new schema loads (`check-domain.sh`'s `sys.argv[3]`, `check-state.sh`'s
  `sys.argv[2]`) both resolve to `_selfdir`, derived from `BASH_SOURCE[0]` — the script's own
  directory, confirmed for **both** scripts this cycle (c7 verified only `check-domain.sh`). No
  traversal in either.

## Message-exposure section
- Digest-key rejection (`validate-digest.py:1414-1421`): `repr(field)` for every offending key — safe.
- Step/evidence rejection (`check-domain.sh`): `repr(key)` for every offending key — safe.
- Downgrade rejection (`check-domain.sh`): `{_version!r}` explicit repr; `{_prior_version}` is
  type-constrained to a plain positive int by the `_prior_is_strict` guard before it can appear — safe.
- INV-16 at-rest rejection (`check-state.sh`): offending-key list `_names` is list-wrapped (safe via
  Python's implicit per-element `repr()`); **`run_id`/step `id` are not** — SEC-C9-01 above.
- No attacker-chosen key name can forge a convincing false message: every offending-key surface uses
  `repr()`, which quote-delimits and escapes the value, so a crafted key reads as an obviously quoted
  string rather than free text merging into the surrounding sentence.

## Threat model
| boundary | STRIDE | mitigated |
|---|---|---|
| agent-authored `state.yaml` write vs. check-domain.sh schema_version floor/downgrade gate | Tampering | true — F1 fixed and executed |
| agent-authored `state.yaml` write vs. check-domain.sh closed step schema | Tampering | true — unchanged from c7, still sound |
| at-rest digest sweep vs. raw persona (F2) | Tampering (defence-in-depth only) | false, but precondition requires either historical-artifact reinterpretation (declined, evidence-backed) or the already-accepted stop_hook_active hole (documented DEC-208) |
| Bash-authored `state.yaml` vs. check-state.sh's INV-16 operator report | Spoofing / Information disclosure | false — SEC-C9-01, gated behind the pre-existing Bash-write precondition |
| run-state-schema.json path resolution (both scripts) | Tampering (path traversal) | true — BASH_SOURCE-derived selfdir in both check-domain.sh and check-state.sh |
| crafted step/evidence key vs. operator terminal | Information disclosure / injection | true — repr() escapes control chars, confirmed for all offending-key surfaces |
| vendored fixture vs. supply chain | Tampering | true — inert, human-reviewed, self-detecting drift via SC-06 |

## Open questions
- SEC-C9-01's one-line fix (`!r}` on `run_id`/`_step_id` in `check-state.sh`'s INV-16 message) is
  inside the DEC-174 carve-out; route to main-session for the next touch of that file.
- F2's residual (stop_hook_active + generic-"lead"-persona sweep leaves a NEW digest's smuggled key
  uncaught at rest) is unchanged from c7/DEC-208 and is not new information this cycle — flagged again
  only because the dispatch asked for an explicit residual-risk statement.

```yaml
VERDICT: PASS
DIGEST:
  headline: "F1 (high) confirmed fixed at source and by execution (12/12 T-06); F3 (med) confirmed fixed at source and by execution (34/34 T-04); F2 (med) correctly declined — independently reproduced the REQ-08/SC-12 stranding evidence on a real digest and confirmed no schema_version-equivalent discriminator exists for digest.md to make the remedy safe. One new med, non-gating finding: check-state.sh's new INV-16 message echoes run_id/step id unescaped, unlike every sibling interpolation in this diff, letting the pre-existing Bash-write bypass also spoof/erase its own audit line on the operator's terminal."
  in_scope: true
  scope_reason: "Diff changes a write-time guard, an at-rest sweep and a validator over agent-authored YAML/markdown; read every hunk, executed test-check-domain.py (12/12) and test-validate-digest.py (ALL PASSED) against the pin, traced every new interpolation of attacker-controlled content for escaping."
  severity_max: med
  findings: 1
  must_fix: []
  threat_model:
    - { boundary: "state.yaml write vs. check-domain.sh schema_version floor/downgrade", stride: T, mitigated: true }
    - { boundary: "state.yaml write vs. check-domain.sh closed step schema", stride: T, mitigated: true }
    - { boundary: "at-rest digest sweep vs. raw persona (F2)", stride: T, mitigated: false }
    - { boundary: "Bash-authored state.yaml vs. check-state.sh INV-16 report echo", stride: S, mitigated: false }
    - { boundary: "run-state-schema.json path resolution, both scripts", stride: T, mitigated: true }
    - { boundary: "crafted step/evidence key vs. operator terminal", stride: I, mitigated: true }
    - { boundary: "vendored fixture vs. supply chain", stride: T, mitigated: true }
  open_questions:
    - { id: Q1, question: "SEC-C9-01: check-state.sh's INV-16 message should wrap run_id/step id in repr() (or a list) to match every other attacker-controlled interpolation in this diff, closing a terminal-escape spoof of the audit line reachable via the already-accepted Bash-write bypass. DEC-174 carve-out, main-session route.", blocking: false }
    - { id: Q2, question: "F2's residual: stop_hook_active's one-shot passthrough plus the digest sweep's persona-blind validate('lead', ...) call means a NEW lead digest that slips an undeclared key through the one-shot exemption is never caught at rest, asymmetric to the state.yaml step case. Already covered by DEC-208's acceptance of stop_hook_active; flagged only as an explicit residual per this cycle's dispatch.", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-104-strict-digest-schema/notes/review-harness-security-reviewer-c9.md
```
