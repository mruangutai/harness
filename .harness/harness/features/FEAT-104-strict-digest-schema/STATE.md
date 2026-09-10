# STATE

## Current

- feature: FEAT-104-strict-digest-schema
- run: `2026-09-10-14-panel-validator` (reviewer panel c10, `harness-validator-lead`, **ESCALATE**)
  at the pinned `review_sha` `790023f0`, range `origin/main..790023f0`
- squads: validator
- status: validate — **the panel's `must_fix` is EMPTY at the pin, but the panel SPLIT on the
  severity of one new finding, and that split is the ship gate.** `gates.review` is
  `advisory_unless_high`: `high` blocks, `med` does not. The remedy edits `check-domain.sh`, which
  DEC-174 makes read-only to every agent, so no squad can close it — it goes UP, not into a fix
  cycle. Owed before ship: this decision, then the SC-13 UAT and the CEO briefing. No merge.

**Four reviewers ran; none skipped, and both self-scoping readers scoped IN after measuring.**
code-reviewer PASS (`severity_max: low`, code grade pass, 42 functions, 0 FAIL); qa PASS GATE-ONLY
(`matrix_ok: true`; unit 36 files / integration 70 files MEASURED fresh at this pin — exactly the
`168f875f` baseline, 0 failing files — with the matrix DERIVATION adopted over a byte-identical tree
and said so); security-reviewer PASS (scoped in after measuring its four surface files
byte-identical to c9; no new finding; CF-1 carried); ui-reviewer **FAIL** (scoped in on
denial-text-as-interface after a 75-file census found no rendered surface and no `DESIGN.md`) — it
raised the only new defect. Notes `notes/review-harness-{code-reviewer,qa,security-reviewer,ui-reviewer}-c10.md`;
consolidated `runs/2026-09-10-14-panel-validator/digest.md`, which validates at exit 0.

**PF-C10-01 — I reproduced it MYSELF rather than relaying it.** A `schema_version: 2` step missing a
REQUIRED field is refused (exit 2, fail-closed) with `offending key(s): .` — empty — under the head
`undeclared step key or evidence shape.`, which is the wrong reason: nothing is undeclared, a
required key is absent. Bounded read-only probe importing the standing test module's own `_fire_new`
into disposable fixture roots (no tracked file written): `missing-status` and `missing-id` → empty
list; controls `id: 5` (type error on a PRESENT field) → `'id'` and `rogue_step_key` → names the key.
Mechanism at `check-domain.sh:1645-1659`: offenders are harvested only via `_path =
list(_error.path); if _path:`, and a jsonschema `required` violation reports at the container's own
path (`[]`), so the branch never fires and jsonschema's own `e.message` is discarded. `grep -n
required tests/integration/test-check-domain.py` → no hits; no case builds this shape.

**The severity split is real and I did not average it away.** ui rates `high`: the message states a
FALSE reason on the exact seam this cycle exists to harden, and REQ-05 demands a rejection be
*immediately actionable*. The lead rates `med`, decided not averaged: the write is denied (no
incorrect-accept, no integrity consequence), the route sentence still emits `run-state-schema.json`
where `required` is declared, and no signed SC governs this path — SC-03/SC-08 govern the
undeclared-key case, which works. **My read, for the operator, not a ruling:** `med` is the better
grade, but the cheap resolution is the one-line fix (`e.validator == "required"` → fall back to
`e.message`) rather than arguing the grade, since the file is already open for the SC-13 UAT read.

**SC-08 is MET on BOTH seams, both with EXECUTABLE evidence** — the lead's `sc_status`, and I
checked both myself. Step seam: `tests/integration/test-check-domain.py:79-89`, a real subprocess
asserting `returncode 2` + `undeclared step key` + the offending key + `run-state-schema.json` +
backticked `` `evidence` ``; 12/12 green at this pin. The conjunction cannot be met by the other
producer naming the schema file — the `except Exception` branch emits a DIFFERENT head (`run-state
schema CANNOT be checked`) carrying neither `undeclared step key` nor backticked `` `evidence` `` —
and all four probe payloads routed through the intended branch. Digest seam:
`tests/integration/test-validate-digest.py:3130-3145`, re-run by me — exit 0, 164 `ok`, `ALL
PASSED`. Red capability on the step seam stays REASONED, not mutation-executed (DEC-174 forbids
editing the carve-out); unchanged from c9, not new debt. Q8 is therefore RESOLVED: an approved
criterion was satisfied, not amended, so no re-signature is owed.

**Carried dispositions held, each re-verified at this pin rather than assumed.** F1
(`schema_version` downgrade refusal) CLOSED — its case green in the 12/12. F3 (undeclared-digest-key
message naming file + `SCHEMAS`/`PASSTHROUGH`/`DOCUMENTED_OPTIONAL`) CLOSED — `validate-digest.py:1411-1423`
unchanged since c9. F2 (generic-`lead` exemption, `check-state.sh:1590`) **DECLINED, and the decline
STANDS**: the generic lead is the archive-reader compatibility contract REQ-08/SC-12 requires, and
every NEW return is validated under its true raw persona at the SubagentStop hook. Residual carried
as Q9/Q3. CF-4 still present, still `low`.

**`cycles_used` stays 9 of 10** — the lead reported ZERO send-backs, and a clean first-pass run adds
no cycle (DEC-157). `len(runs)` is 24 of 20, informational only (#79); this run earned its place —
it found a defect four prior gates had not, and re-verified every carried disposition independently.
**The pin did NOT move and no source or test file was touched**: `git status --porcelain` showed
only the four new c10 notes before I recorded this, and this run's bookkeeping commit sits ABOVE
`790023f0` touching only the feature's own directory, as the c9 one does.

**A dispatch imprecision of mine, disclosed not buried.** I told the panel the only
non-feature-directory file in `168f875f..790023f0` was `tests/integration/test-check-domain.py`; ui
corrected me — `.harness/notes/analysis-feat104-run07-review-sha-recordfix.md` (+81/-0, new,
repo-level) is also in range. No review consequence; the ship note must not repeat the claim.

## Open Questions

- Q10 (**BLOCKING**, main session, DEC-174): **PF-C10-01 severity is CONTESTED** — ui `high`, lead
  `med`. Under `gates.review: advisory_unless_high` this decides whether the ship blocks. The remedy
  is one line in `check-domain.sh`, a DEC-174 carve-out no squad may edit: apply it (plus a case for
  the required-absent shape, a new pin, a narrow re-gate), or accept `med` and backlog. Detail:
  `runs/2026-09-10-14-panel-validator/digest.md`, `notes/review-harness-ui-reviewer-c10.md`.
- Q11 (not blocking, harness defect — new): panel falsification capability is ASYMMETRIC.
  `bash-write-guard.sh` refused the code reviewer's disposable /tmp copy while the ui reviewer ran a
  live repro — and the reviewer that could EXECUTE found the only new defect. Should a read-only
  review dispatch guarantee a scratch-write route?
- Q12 (not blocking, harness defect — new): `harness-qa`'s terminal return exited 1 with "yield
  called with null data" although its fenced block and note were complete on disk. Accepted without
  a send-back; a defect in the yield path, not a member error.
- Q13 (not blocking, main session): SC-08's STEP seam closes under `plan.yaml:460-462`'s decided
  route text (file path + the `evidence` property name), a narrower reading of "symbol" than the
  digest seam's three Python identifiers. Hold a future feature reusing the pattern to it?
- Q6 (**NARROWED**, harness defect): the append-only channel CAN repair a digest whose defect is a
  REMOVABLE key (used on `runs/-12`); it cannot repair a MISSING required field (`runs/-06`) or a
  verdict CONTRADICTION (`runs/-08`). Those two stay stranded.
- Q-B3 / Q4 (not blocking, harness defect): the digest contract has no home for per-kind suite exits
  and file counts, and the `lead` schema declares no `code_grade`. **Avoided this cycle** — the c10
  dispatch named the declared lead field set and the digest validated at exit 0 first time. Should
  `PASSTHROUGH['lead']` gain these as unverified roll-ups?
- Q9 (not blocking, main session): REQ-08's generic-lead archive exemption
  (`validate-digest.py:1407`) has no test able to redden. Does not falsify REQ-08. Backlog or accept.
- Q1 (not blocking, main session, DEC-174): **CF-1** (security, `med`) — `check-state.sh:1525-1526`
  interpolates `run_id` and the step id as bare strings, so the DEC-85 Bash-write route can spoof or
  erase the INV-16 audit line. One-line remedy (`!r`). Carried unchanged by the c10 security reader.
- Q2 (not blocking, main session): **CF-3** (code, `low`) — `abff2a84`, a FEAT-56 `plan.yaml` station
  flip, is this branch's root commit and merges with this PR, untracked by any REQ or D. ACCEPT and
  record in the ship note; excising it rewrites history beneath a signed pin.
- Q3 (not blocking, main session): **CF-2** severity CONTESTED — qa `med`, code `info`, lead `low`.
  `check-state.sh:1590`'s at-rest exemption has no test able to report RED; the remedy sits inside
  the carve-out, so no squad may close it.
- Q5 (not blocking, main session, DEC-174): **CF-4** (ui, `low`) — the `schema_version` downgrade
  branch renders a raw Python `None` in the omitted-on-update edge; `T-06` has no such case.
- Q7 (not blocking): the 3 complete + 2 partial strict-version predicate spellings want one home.
- F-QA-1 (not blocking, main session): `T-05` declares `change_type: logic` while DEC-212's
  `touches_config_shape` arguably covers `run-state-schema.json`, making `integration` a floor line.
- Residual non-gating risks, in the c9 and c10 panel digests: the DEC-85 Bash-write bypass; F2's
  runtime residual; `check-domain.sh`'s `_no_parser` bootstrap early return; the
  `run-state-schema.json` guards argued fail-closed rather than mutation-proven. Standing: the
  INV-26 card/plan mismatch and the per-persona worktree-claim guard.
