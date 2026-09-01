# Security review — BUG-1071 era guard — review_sha bf12a96b (base 75daa3bb)

## Scope census

Two files, no network/credential/PII surface. Censused for the real asset at risk: **gate
integrity** — `check-state.sh` INV-32 (`check-state.sh:174-279`) is a fail-closed control
requiring proof an adversarial panel reviewed an approved plan. This diff adds the first
exemption paths into it (`:180-216`, delimited `# INV-32 ERA BEGIN/END (BUG-1071)`), plus
matching test coverage. In scope as Tampering/Repudiation against that control (my Expertise
P-03: a loosened guard is itself the trust boundary). No other surface — `test-check-state.py`'s
changes are fixtures over the same mechanism, not a second surface.

## Verified evidence (claims re-run, not trusted)

- `bash check-state.sh` in the real worktree: **exit 0**, 32 `INV-32` lines, all printed with the
  `note` prefix (never `VIOLATION`) — `check-state.sh:1905-1906` prints `bad` as `VIOLATION` and
  `warn` as `note`; only `bad` drives `sys.exit(1)`. Split confirmed: 1 "approval.date is
  missing" + 31 "before the adversarial panel" = 32. Matches the claimed evidence exactly.
- `python3 test-check-state.py`: 151 `ok`, 0 `FAIL`, exit 0. All four new cases present and
  green, including `case_inv32_era_guard_is_load_bearing` (`real=0 mutant=1 violations` — I
  re-ran it, not just read it).
- Confirmed by grep, not assumed: `INV-32:` / `approval.date` appears **nowhere else** in
  `check-state.sh` outside the INV-32 block. The pre-existing INV-3 check (`:153-172`) validates
  only `approval.status`, never `approval.date`. No second guard forces the field.
- `harness_yaml.load_plan`'s `REQUIRED_TASK_FIELDS` (`harness_yaml.py:288`) covers only task
  shape, not `approval`. No schema-level requirement on `approval.date` either.

## Q1–Q3, answered

**Q1 (hardcoded date).** `INV32_ERA_START` is a literal shipped in harness's own gate script,
run against every onboarded repo. A repo that ships INV-32 later, or a fork of `check-state.sh`
whose panel shipped on a different date, inherits `2026-08-31` as a foreign constant with no
provenance check. Concrete failure mode: none *for this repo* — the constant is a one-time
bootstrap boundary, and the file's own convention elsewhere (INV-30/INV-31 in this same file) is
literal comparison dates hardcoded the same way. Not a new pattern, not a live bug for this repo,
but worth naming: a future repo that vendors `check-state.sh` verbatim inherits the wrong
boundary silently (no assertion anywhere ties `INV32_ERA_START` to that repo's own panel
ship-date). Low severity — hardening, not a finding, since nothing exploits it today.

**Q2 (does the undated branch fail open) — yes, verified, but see judgment below.** Reachable
today: `FEAT-40-harness-writes-done` is approved with no `approval.date` and is permanently
exempted from INV-32 grading with only a `note`. No second guard independently requires
`approval.date` on an approved plan (grepped, confirmed above) — **the bypass is live, not
theoretical**, for both the undated case and an undetected backdated case (`signed <
INV32_ERA_START` is a bare string compare against operator-supplied text; nothing cross-checks
it against git history, commit date, or file mtime).

**Reachability is narrower than "any subsequent agent," though.** `## Approval` blocks —
`plan.yaml`'s `approval:` fragment, which is where `date` lives — are written by the **main
session only** (`SPEC.md:152`, "the one carve-out to single-owner"; enforced for every other
governed agent by `check-domain.sh`'s `approval_guard`, which denies the `approval:` fragment to
everyone but the main session — `check-domain.sh:429-440`, `team-config.yaml:21-25,98-99`). A
governed build/dev agent **cannot** touch `approval.date`; only the main session (operator
channel) can, and the main session is exempt from `check-domain.sh` entirely (no `agent_type` →
ungoverned). So the actor who can exploit this is exactly the actor the dispatch names: a hurried
operator, not "a subsequent agent."

**Judgment — is the fail-open defensible?** Partially, and my Expertise's own pattern applies
directly (P-02: an actor who already controls a value already holds the privilege it grants — no
escalation). The main session is the **only** writer of `approval:` and, per the same manifest
grant (`team-config.yaml:99`, only `approval:` is carved out of `plan.yaml`'s write grant to
`harness-pm`), nothing in `check-domain.sh` restricts the main session from *also* writing
`panel:` — the main session could fabricate a complete, INV-32-passing panel record directly and
skip the era guard's exemption paths entirely. **The undated/backdated bypass grants no new
capability an already-privileged actor did not already have.** It is not privilege escalation.

What it *does* change is cost and visibility: forging a plausible `panel:` block (readers,
findings, dispositions) is conspicuous, effortful work that a reviewer reading the diff would
likely flag. Omitting or misdating one field is a one-line, easily-accidental act that produces
only a `note` — buried in the real tree today among 31 other identical-looking notes — with no
forcing function to ever revisit it, and the exemption is **permanent** (dates don't change on
their own). This is a real quality/audit-integrity gap for the *accidental* case the dispatch's
"hurried operator" framing describes, not a security-boundary breach: it makes it silently easy
for a plan to permanently escape a control designed to force human review, and the only person
who can trigger it is the same person the control exists to keep honest.

**Severity: MED**, not high — gated on P-02 (no privilege escalation: the exploiting actor already
holds the exact authority being "bypassed") and on reachability being confined to the single,
already-fully-trusted writer. Not `low`/`info`: a fail-closed audit gate that a one-field
omission (not even the deliberate act the design worries about — see `handoff-plan.md`'s Dead
Ends, which reasoned about deliberate downgrading, not accidental omission) can silently and
permanently disable is worth the operator's attention. `must_fix` is empty (see below); this is a
recommendation to consider, not a ship-blocker.

**Q3 (do the four assertions bind).** Yes, independently confirmed:
- `case_inv32_pre_era_is_exempt` / `_boundary_is_exact` / `_undated_approval_warns` assert on
  `_inv32_violations`/`_inv32_notes`, i.e. the specific `FEAT-INV32` + `INV-32` + `VIOLATION`/
  `note` line — never on exit code, correctly, since a bare `plan.yaml`-only fixture is red on
  unrelated invariants (INV-3's `approval.date`-adjacent absence checks don't exist, but
  `STATE.md`/`feature.json`/`BRIEF.md` absence would still gate the exit code). I re-ran the
  suite myself; all four print `ok`.
- `case_inv32_era_guard_is_load_bearing` excises exactly the marked region (`# INV-32 ERA
  BEGIN/END (BUG-1071)`) into a mutant, verified the mutant text differs from source before
  running it, and asserts `real=0, mutant=1` violations on the identical pre-era fixture. I
  re-ran this too: `ok - INV-32 era guard is load-bearing (real=0 mutant=1 violations)`. This is
  mutation evidence, not read-and-conclude (my Expertise O-01).
- Every **pre-existing** INV-32 test (`case_inv32`, `case_inv32_unrated_severity_fails_closed`,
  the mutant-discrimination case) now runs through `_inv32_plan()`'s new default
  `date="2026-08-31"` — i.e. every legacy panel-grading assertion already exercises the post-era
  fall-through path unconditionally. This closes the panel's Q5 coverage question: there is no
  post-era-with-panel path left untested, since the whole pre-existing suite already covers it
  via the shared fixture's new default parameter.

## Q3-adjacent: mutant-file collision (dispatch's own concern 3)

`.check-state-inv32-era-mutant.sh` is a **fixed** filename beside the real script, written,
chmod'd via `shutil.copymode`, and unlinked in a `finally`. Fixed rather than per-process is a
real collision surface if two `test-check-state.py` invocations ever run concurrently against the
same checkout — not unlike a similar pattern to write-then-read races. **Not a new risk this diff
introduces**: I diffed the addition and confirmed `.check-state-inv32-mutant.sh` (no "era"),
`.mutant-check-state-t14.sh`, and `.mutant-check-state-t10.sh` already use the identical
fixed-filename-beside-script convention before this diff (grepped; none of those three helper
functions are additions in this diff — only the filename literal itself is new, following the
existing house pattern verbatim). Rate `info`: pre-existing convention, unlikely to fire in
practice (test suites here are not normally run in parallel against one checkout), no
exploitability distinct from what already exists three times over in this file.

## Q4 — `INV32_ERA_START` inside the loop

Cosmetic only. It is a literal re-assigned every iteration before any use in that same iteration
— no `NameError`, no state leak across iterations, no correctness or security effect. Not a
finding.

## Verdict

No `must_fix`. One `med` (undated/backdated `approval.date` silently and permanently exempts a
plan from INV-32 with no independent guard — reachable only by the main session, and that actor
already holds the authority to bypass the whole control by fabricating `panel:` directly, so this
is not privilege escalation, just a quieter/cheaper route to the same already-reachable outcome).
Two `info` (hardcoded era-start portability across future/forked repos; pre-existing mutant-file
collision convention, not new here). Recommend, as a follow-up and not a blocker: consider making
a missing `approval.date` on a **newly-signed** approval (distinguishable from the 32 legacy
plans by absence of any pre-2026-08-31 evidence) a hard `bad` going forward, or cross-checking
`approval.date` loosely against the commit that introduced the `approved` status. Both are design
questions for the operator, not mine to decide.

```yaml
VERDICT: PASS
DIGEST:
  headline: "INV-32 era guard fail-open on approval.date is real and unguarded elsewhere, but confined to the main session, which already has unrestricted authority to fabricate the whole panel record — not privilege escalation, MED not HIGH, no must_fix."
  in_scope: true
  scope_reason: "check-state.sh's INV-32 block is a fail-closed gate-integrity control; this diff adds its first exemption paths. Tampering/Repudiation surface against gate integrity, not conventional OWASP input/auth/secrets surface."
  severity_max: med
  findings: 3
  must_fix: []
  threat_model:
    - { boundary: "plan.yaml approval: block (main-session-exclusive write channel, DEC-120/SPEC.md:152)", stride: "R (Repudiation)", mitigated: false }
    - { boundary: "INV-32 era-guard undated/backdated approval.date exemption path", stride: "T (Tampering, self-attestation)", mitigated: false }
    - { boundary: "INV32_ERA_START hardcoded constant portability to other/future repos running this shipped script", stride: "I (Info: wrong-boundary risk, not exploited here)", mitigated: true }
  open_questions:
    - { id: Q1, question: "Should a newly-signed (post-2026-08-31, non-legacy) approval with missing/malformed approval.date be a hard `bad` rather than a warn, closing the accidental-omission gap, while the 32 legacy plans keep today's warn treatment?", blocking: false }
    - { id: Q2, question: "Should approval.date be cross-checked (even loosely) against git history for the commit that flips approval.status to approved, to catch a deliberately backdated field?", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/BUG-1071-inv32-era-guard/notes/review-harness-security-reviewer-bug1071.md
```
