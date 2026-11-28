# Validate c1 — BUG-2566-stale-hook-detection — ESCALATE

**BLUF.** The stale-hook detector at `8e18c053` behaves as signed. Unit 69/69 (omp-hooks 274/0) and typecheck pass, and every automated SC has reproduced fail-first evidence. There is one gating finding: the code reviewer rated it **high**. A non-content load-time baseline (`absent` / `unreadable:*` / `not-a-file`) compares equal to the same state later, so the detector reports fresh. That behaviour is what signed D-03 and T-01 steps 3–5 prescribe, so no fix cycle can legally change it (G-06). It goes to the operator. Two cheap SC-01 test-hardening fixes inside T-01 are `must_fix` for the next round. SC-10 (uat) is pending with the operator.

Reviewed: `87efcd8a..8e18c053f60369b38c182ecbbea75ccc0002947e`. Readers: qa PASS, code-reviewer FAIL, security-reviewer FAIL, ui-reviewer PASS (scoped out, 36-path census), pm PASS (SC-01..09 met, SC-10 pending).

## E-01 — non-content load-time baseline treated as fresh (gating; routed up)

- **Where:** `.omp/extensions/harness-hooks.ts:68-111` (`entryState` → `LOADED_HOOK_FINGERPRINT` → `staleHookReason` equality).
- **Ratings by name:** code-reviewer **high** (D-02 mismatch: the hook is removed between the loader's read and module evaluation, stays absent, and Main `task` passes). security-reviewer **med** (same class, plus a TOCTOU: the file is *replaced* in that window, so the baseline hashes the new bytes and the old code runs undetected while the disk stays at that version). qa: no finding ("module was just imported from that path; not reachable in practice", `notes/review-harness-qa-c1.md` §Probes). **Lead: low.** The fault is reachable only inside the loader→evaluation window. Its outcome is the pre-feature state: no detection for that session, no new bypass of any other gate. It also clears itself on the next disk change, which then differs from the baseline. Per the rules, the reader's `high` is transcribed unchanged.
- **Why not must_fix:** signed plan.yaml D-03 (line 169) defines the fingerprint states as "content hash, absent, not-a-file or unreadable". T-01 step 3 prescribes the `absent` / `unreadable:` returns, and step 5 says "if none [differ] … return undefined". The implementation is literal to that signed text (T-01 hash `ff325664…`). Any remedy amends signed intent.
- **Remedy fit:**
  - (a) The code reviewer's remedy (refuse governed calls when the load-time state is not a sha256 hex) closes only the non-content sub-case. It is about three lines, but it has no witness without a new test seam: a module cannot be imported while absent, and SC-06 allows only `staleHookRefusal` to be exported.
  - (b) The security reviewer's TOCTOU variant needs the bytes OMP's loader actually read. That is an OMP change outside T-01, and the BRIEF already lists "the module-load baseline is the loaded code" under Verification gaps.
  - **Lead recommendation:** accept both as a documented gap. Add one sentence to SPEC §4.2 (T-02's file) stating that a baseline captured in the load window is trusted. Option (a) is the operator's call if a test seam is acceptable.

## must_fix (substance, T-01, `tests/unit/omp-hooks.test.ts`) — order: either; same file

1. **FIFO fixture can pass as the deletion case** (`:4506-4520`; code-reviewer med, verified at source). `spawnSync("mkfifo", …)`'s result is ignored after `rmSync`. If mkfifo fails, the detector returns the deletion reason and every assertion passes. On this host pm's blocking-open mutant L went red, so the vacuity depends on the host. **Repair:** in the probe, assert `status === 0` from mkfifo and `lstatSync(path).isFIFO()` before calling `staleHookRefusal()`, and exit non-zero otherwise.
2. **SC-01 "relative to that root" is unwitnessed** (`:4468-4472`). qa F-1 (low; mutant M3, a `process.cwd()` reason root, stays green 13/13) and code-reviewer item 2 report this as one defect. **Repair:** `expectStale` asserts that `reason` contains `` `no longer matches ${H} on disk` ``.

Both are cheap, sit inside T-01's signed files and close an SC-01 clause literally (G-10). The repo gate is `advisory_unless_high`, so on their own they would not block shipping.

## Advisory (not gating)

- **Exact-`BLOCKED` carve-out unwitnessed by test.** qa F-2 (low; mutant M6 survives 34/34) and pm Q-01 report the same gap. SC-06 pins it by inspection, and validate-digest still judges such a yield. Recommended in the same round: add refused rows for `{VERDICT:"blocked"}` and `{DIGEST:{VERDICT:"BLOCKED"}}`.
- **Unbounded synchronous read** (security low, `harness-hooks.ts:70-75`). **Assessed and dismissed:** the attacker must already be able to write the hook source itself, and the remedy contradicts T-01's signed `readFileSync(fd)` prescription.
- **SC-05:** median 0.119 ms against the 5 ms bound. The threshold's discrimination is not shown (no slow mutant); the signed gap bounds it to the test host.
- **SC-10:** no `notes/uat.md` UAT script at the pin (pm Q-02). Its steps live only in the build receipt. pm Mode 3 should author it before ship.
- **Receipts:** runner receipts are this host's interpreter and environment, not CI (G-03). They are untracked under `runs/**` until main commits them with the closed run (repo G-02).

## Assurance

- qa ran the plan's verify blocks verbatim (T-01 and T-02 exit 0). It reproduced the build's 26-red list at `87efcd8a` and ran nine mutants. qa and pm independently pinned the stale-first ordering (M4/C), carve-out width (M5/D), the Main governance split (M7/M8/G/H/I), the mtime detector (M1/J), the cwd-derived root (M2/B) and the widened set (M9/K). Those are falsification results, not reasoning.
- code-reviewer and security-reviewer were static only: no rerun and no race reproduction.

```yaml
VERDICT: ESCALATE
DIGEST:
  headline: BUG-2566 at 8e18c053 behaves as signed (unit 69/69 with omp-hooks 274/0,
    typecheck 0, fail-first reproduced). One high finding from the code reviewer (a
    non-content load-time baseline is treated as fresh) is implemented literally from
    signed D-03 and T-01, so it goes to the operator. Two cheap SC-01 test-hardening
    items in T-01 are must_fix. SC-10 uat is pending.
  team: validate
  steps_run: 5
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: Unit floor satisfied at 8e18c053 (69/69 files, omp-hooks 274/0) and
      typecheck exit 0. Fail-first reproduced. Two low mutant survivors (F-1 reason
      root, F-2 lax BLOCKED).
    files_touched:
    - .harness/harness/features/BUG-2566-stale-hook-detection/runs/2026-11-27-04-validate-validator/qa/manifest-unit.json
  - step: code
    persona: harness-code-reviewer
    verdict: FAIL
    headline: T-01 treats a missing load-time hook as fresh, and its FIFO test can
      pass without creating a FIFO.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: FAIL
    headline: Startup can silently trust a fingerprint that does not match the executing
      hook.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'Mode B out of scope: none of 36 changed paths renders UI.'
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: SC-01..SC-09 met with discriminating evidence and SC-10 pending UAT.
      Orchestrator and code-maintainer perspectives pass; operator is partial on UAT
      only. D-01..D-04 landed.
    files_touched: []
  must_fix:
  - 'T-01 tests/unit/omp-hooks.test.ts:4506-4520: the FIFO probe ignores the result
    of spawnSync("mkfifo") after rmSync, so a failed mkfifo silently tests the deletion
    case. Repair: assert mkfifo status 0 and lstatSync(path).isFIFO() in the probe
    before calling staleHookRefusal(), exiting non-zero otherwise (code-reviewer,
    med).'
  - 'T-01 tests/unit/omp-hooks.test.ts:4468-4472: expectStale asserts only toContain(H),
    so SC-01''s ''relative to that root'' is unwitnessed (mutant M3, a process.cwd()
    reason root, stays green). Repair: assert the reason contains `no longer matches
    ${H} on disk` (qa F-1 low + code-reviewer item 2, one defect).'
  files_touched:
  - .harness/harness/features/BUG-2566-stale-hook-detection/runs/2026-11-27-04-validate-validator/qa/manifest-unit.json
  branch: feat/BUG-2566-stale-hook-detection
  open_questions:
  - id: OQ-01
    question: "E-01: a load-time fingerprint state that is not a content hash (absent\
      \ / unreadable / not-a-file) compares equal to the same state later, so staleHookRefusal\
      \ reports fresh (.omp/extensions/harness-hooks.ts:68-111). A file replaced between\
      \ the OMP loader's read and module evaluation has its new bytes recorded as\
      \ the baseline. Ratings: code-reviewer high, security-reviewer med, qa 'not\
      \ reachable in practice', lead low (only reachable in the loader-to-evaluation\
      \ window; the outcome is the pre-feature no-detection state, and the next disk\
      \ change clears it). The behaviour is literal to signed D-03 (plan.yaml:169)\
      \ and T-01 steps 3-5, so a fix cycle cannot change it. Options: (a) amend T-01\
      \ to refuse governed calls when the load-time state is not a sha256 hex. That\
      \ is about three lines, but it needs a new test seam, because SC-06 allows only\
      \ staleHookRefusal to be exported and an absent module cannot be imported. The\
      \ TOCTOU variant remains open either way, since it needs OMP's loader bytes.\
      \ (b) Accept both as a documented gap with one sentence in SPEC \xA74.2 (T-02's\
      \ file). Lead recommends (b)."
    blocking: true
  - id: OQ-02
    question: SC-10 has no notes/uat.md UAT script at the pin; its steps exist only
      in notes/receipt-main-session-build.md. Should pm Mode 3 author it before ship?
      (pm Q-02)
    blocking: false
  escalations:
  - id: E-01
    raised_by: harness-code-reviewer (high); harness-security-reviewer (med)
    question: Should the stale detector fail closed when the load-time baseline is
      not a content hash, and is the loader-window TOCTOU an accepted gap? Any remedy
      amends the signed D-03 and T-01 text.
    domain: signed plan intent (D-03, T-01 steps 3-5) / operator
    routed_to: orchestrator -> main session -> operator
    resolution: "pending; lead recommends accepting it as a documented gap in SPEC\
      \ \xA74.2"
    decided_by: pending
    recorded_as: "open_questions OQ-01; runs/2026-11-27-04-validate-validator/digest.md\
      \ \xA7E-01"
  expertise_update: []
  adequacy_notes:
  - 'qa and pm ran falsification mutants (stale-first order, carve-out width, Main
    governance split, mtime detector, cwd root, widened set), and each went red. code-reviewer
    and security-reviewer were static only: no rerun and no race reproduction.'
  - Runner receipts are this host's bun 1.3.14 / omp 19.2.1 environment, not CI. runs/**
    stays untracked until main commits the closed run record.
  - 'The FIFO vacuity depends on the host: pm''s blocking-open mutant L went red here,
    so mkfifo succeeded on this host.'
  - SC-05 median is 0.119 ms against the 5 ms bound. The threshold's discrimination
    is not shown (no slow mutant run).
  - 'The exact-BLOCKED carve-out is pinned by SC-06 inspection only; mutant M6 survives
    (qa F-2 = pm Q-01). Recommended for the same fix round: add refused rows for {VERDICT:''blocked''}
    and {DIGEST:{VERDICT:''BLOCKED''}}.'
  - 'security low (unbounded synchronous read, harness-hooks.ts:70-75) was assessed
    and dismissed: it needs write access to the hook source itself, and the remedy
    contradicts T-01''s signed readFileSync(fd).'
  - Repo gates.review is advisory_unless_high. The two must_fix items alone would
    not block shipping; they close SC-01 clauses literally and cost little.
  - 'Reader roles: qa ran the gate-only matrix with receipts and mutants. code-reviewer
    ran stage 1 only (stage 2 not started after the stage-1 FAIL). security was in
    scope at the tool_call authorization boundary. ui self-scoped out (no UI among
    36 changed paths). pm graded perspectives and dispositions at the pin.'
  sc_status:
  - id: SC-01
    verdict: met
    method: automated
    evidence: omp-hooks.test.ts:4475-4521 green at the pin; red at 87efcd8a and under
      mutants M1/M2. The relative-path clause and FIFO construction are under-pinned
      by the tests (must_fix).
  - id: SC-02
    verdict: met
    method: automated
    evidence: 'omp-hooks.test.ts:2479-2518: 13 refused cases red semantically at 87efcd8a;
      4 carve-out cases preserved and asserting validate-digest exactly once with
      the decoded object; mutants M4/M5/M7a red'
  - id: SC-03
    verdict: met
    method: automated
    evidence: omp-hooks.test.ts:2527 (4 rows); mutants M8/M7b red
  - id: SC-04
    verdict: met
    method: automated
    evidence: omp-hooks.test.ts:4523-4573; the mtime mutant M1 reddens the touch/identical/restore
      cases, M9 the schema cases, M2 tree-B
  - id: SC-05
    verdict: met
    method: automated
    evidence: omp-hooks.test.ts:4575 green; qa probe median 0.119 ms (host-bound)
  - id: SC-06
    verdict: met
    method: inspection
    evidence: 'pm and code-reviewer at the pin: fingerprint set from import.meta.url
      only, sole new export, stale check first, merge prefilter shared, ls-tree shows
      only harness-hooks.ts'
  - id: SC-07
    verdict: met
    method: automated
    evidence: tests/unit/test-omp-hooks.py exit 0, 274/0 at the pin (qa runner receipt
      manifest-unit.json)
  - id: SC-08
    verdict: met
    method: automated
    evidence: bun run typecheck exit 0 at the pin; exit 1 (TS2554) at 87efcd8a with
      the pinned tests
  - id: SC-09
    verdict: met
    method: inspection
    evidence: "SPEC.md \xA74.2 'Stale hook code (BUG-2566)' carries all five statements;\
      \ T-02 verify prints 'SPEC 4.2 ok'"
  - id: SC-10
    verdict: pending
    method: uat
    evidence: operator UAT not yet run
  needs_approval: true
  severity_max: high
  matrix_ok: true
  coverage_gaps:
  - 'SC-01 relative-path clause unwitnessed (mutant M3 survives): must_fix'
  - 'SC-01 FIFO fixture does not assert the FIFO was created: must_fix'
  - 'exact-BLOCKED carve-out unwitnessed by test (mutant M6 survives): advisory'
  - 'SC-05 threshold discrimination not shown: advisory'
  - SC-10 uat pending; no notes/uat.md
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: code-reviewer; security-reviewer (med)
    summary: 'T-01 harness-hooks.ts:68-111: a non-content load-time baseline, or bytes
      replaced in the loader-to-evaluation window, makes the detector report fresh
      indefinitely while the disk state holds.'
    why: This fails open against the operator's 'never enforces stale code' goal.
      It is literal to signed D-03/T-01, so it is escalated as E-01/OQ-01 rather than
      made must_fix. Lead's own rating is low (narrow window, outcome equals pre-feature
      behaviour); the reader severities are transcribed unchanged.
  - kind: substance
    scope: none
    severity: med
    reader: code-reviewer
    summary: 'T-01 omp-hooks.test.ts:4506-4520: the FIFO probe ignores mkfifo''s result,
      so it can silently test deletion instead.'
    why: The SC-01 FIFO witness could go vacuous on a host where mkfifo fails. Verified
      at source by the lead. must_fix.
  - kind: substance
    scope: none
    severity: low
    reader: qa (F-1); code-reviewer
    summary: 'T-01 omp-hooks.test.ts:4468-4472: expectStale does not pin the reason''s
      path as relative to the root (mutant M3 survives).'
    why: SC-01's literal clause 'relative to that root' is unwitnessed. must_fix (cheap).
  - kind: substance
    scope: none
    severity: low
    reader: qa (F-2); pm (Q-01)
    summary: 'T-01 omp-hooks.test.ts:2468-2478: no test pins that the carve-out requires
      VERDICT exactly ''BLOCKED'' (mutant M6 survives).'
    why: Pinned by SC-06 inspection only, and validate-digest still judges the yield.
      Advisory.
  - kind: substance
    scope: none
    severity: low
    reader: security-reviewer
    summary: 'T-01 harness-hooks.ts:70-75: an unbounded synchronous whole-file read
      could stall Main if an oversized file replaces the hook.'
    why: 'Assessed and dismissed: it needs write access to the hook source, and the
      remedy contradicts T-01''s signed readFileSync(fd).'
  readers:
  - reader: qa
    status: ran
    persona: harness-qa
    reason: none
  - reader: code
    status: ran
    persona: harness-code-reviewer
    reason: none
  - reader: security
    status: ran
    persona: harness-security-reviewer
    reason: none
  - reader: ui
    status: ran
    persona: harness-ui-reviewer
    reason: none
  - reader: goalcheck
    status: ran
    persona: harness-pm
    reason: none
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2566-stale-hook-detection/.harness/harness/features/BUG-2566-stale-hook-detection/runs/2026-11-27-04-validate-validator/digest.md
```
