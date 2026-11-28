# repanel-product (cycle 2): FEAT-2581 team digest

**BLUF: FAIL. Do not sign.** The plan is still `pending`, panel cycle 2 is recorded, and `plan-merge.py check` exits 0.

The re-read closed 4 of the 6 cycle-1 substance findings: PF-ccd4, PF-d91c, PF-aaf4 and PF-b3de. Two are not closed:
- PF-e7dd0045 (proof binding): not closed, and now reopened on the panel.
- PF-7999938a (D-02): its inventory still does not bound the output delta. The authorization half is the operator's.

The scope reader also raised two new substance findings: a contradiction between T-01's gate and SC-03 (high), and RG-A2, which found T-03's baseline_failing exemption unbounded (med).

pm applied all four substance items in this run. No reader has read that applied text. This is the same pattern that failed cycle 1, now on a narrower surface.

No reader raised a `scope: mission` finding, so I do not recommend downgrading the mission.

## Re-read verdicts on the cycle-1 substance findings

| id | re-reader | verdict | source pointer (worktree) |
|---|---|---|---|
| PF-ccd4ca98 | scope | **closed** | plan.yaml T-03 intent :333; BRIEF SC-05 :41; tests/unit/test-feature-record.py:1408–1418 |
| PF-e7dd0045 | scope | **not closed**: CLI/replay PASS is accepted without records; script hashes are not distinct paths; HEAD is not bound to review_sha | plan.yaml T-03 verify :298–321; bin/validate-digest.py:462–483 |
| PF-d91cba6c | scope | **closed** (the migration only; (61.b) was already vacuous, so the probe is not proof of cleanup) | plan.yaml :225–227, :249; bin/check_state/ctx.py:360–372, :391; runner.py:325–334 |
| PF-aaf45b29 | scope | **closed** | plan.yaml :234; research note :69; bin/feature-record.py:124–126, 230, 708 |
| PF-7999938a | scope | **not bounded**: a module-substring filter over decoded gate text, and an audit scanned-file count captured at the pin only. Authorization is not the reader's to judge | plan.yaml :120, :337, :339; bin/canonical_reader_audit.py:212–229, 771–782 |
| PF-b3de0ad1 | should-not-exist | **closed**: one checkout-root token, with fixtures fixed at creation | plan.yaml T-03 comparison paragraph (:341) |

Line numbers cite the plan as the readers read it, before the cycle-2 apply.

## Findings from this run and their dispositions

Each finding keeps the reader's own severity and kind. record-panel computed the ids.

| id | reader | sev | kind | summary | disposition | applied where (pm) |
|---|---|---|---|---|---|---|
| PF-14c27514 | scope | high | substance | PF-e7dd restated: PASS markers are not bound to the measurements or the review pin | open, **unread** | T-03 verify/intent: committed raw measurements `notes/measurements/{baseline,pin}.jsonl.gz`, a recomputed divergence set, six named script paths, reads at review_sha; BRIEF SC-02, SC-05..08, SC-10 |
| PF-c36ed89c | scope | high | substance | PF-7999 restated: D-02 still does not bound the delta | open, **unread**; authorization stays with the operator | T-03, D-02.choice: raw gate bytes with a calibration record, whole-stream comparison, audit at both checkouts with a disclosed `audit_scanned_files` count |
| PF-c82fdafb | scope | high | substance | T-01's pre-commit gate rejects the mutation output SC-03 preserves | open, **unread** | T-01 intent, last paragraph: the pass condition is the baseline's own result |
| PF-390fdc3e | scope | med | substance | RG-A2: baseline_failing is not bounded to the measured set | open, **unread** | T-03, SC-10: any file beyond typescript-typecheck needs a ruled `baseline#` divergence |
| PF-502d3541 | should-not-exist | low | proportionality (task) | narrows PF-d35d903d to the bun ledger class plus the preload script | open; not trimmed, because trimming would narrow Settled Q3 (the operator's call) | T-03 case-identity text reframed |
| PF-e7dd0045 | scope (c1) | high | substance | (cycle 1) | **reopened** by set-panel | n/a |
| PF-7999938a, PF-d35d903d | (c1) | | | | stay open for the operator | n/a |

## Steps

| step | persona | verdict | note |
|---|---|---|---|
| scope | harness-code-reviewer | FAIL (findings) | A valid return, routed to apply. Note: `notes/review-harness-code-reviewer-plan-c2.md` |
| should-not-exist | fable-advisor | PASS | Resolved and ran. I transcribed its single finding |
| design | harness-ui-reviewer | PASS | Self-scoped out. Note: `notes/review-harness-ui-reviewer-plan-c2.md` |
| apply | harness-pm | PASS after 1 send-back | The send-back asked only for verbatim command outputs, delivered by message |

The goalcheck step was not re-run (SC-09). pm appended a dated addendum to the goal-check note: both perspectives' grades stand, and nothing was re-graded.

## pm's command outputs, verbatim as pm relayed them

pm's research note §10 lacks these outputs; they exist only in this digest, as pm relayed them.

record-panel `--cycle 2`, captured at the time, exit 0:

```text
check-state --changed after .../FEAT-2581-feature-record-package/plan.yaml:
  VIOLATION  .harness/harness/features/FEAT-2581-feature-record-package/BRIEF.md is NOT approved — halt that flow and surface to the user.
  VIOLATION  INV-29: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2557-code-layout-pattern is a standing worktree whose feature FEAT-2557-code-layout-pattern reached a terminal state on the default branch. [...] The tree is dirty: `remove` will DECLINE until those changes are committed, landed or discarded.
  VIOLATION  INV-37 FEAT-2581-feature-record-package: github.sync is enabled but the feature has no usable Build-entry receipt (receipt absent or incomplete) - run python3 .claude/skills/harness/bin/gh-sync.py open <feature-dir>.
  note       .harness/harness/features/FEAT-2581-feature-record-package/plan.yaml approval is pending — awaiting the user.
  note       FEAT-2581-feature-record-package: run repanel-product has unknown historical cycle attribution.
  note       FEATURE SET: 1 feature director(y/ies) on disk that HEAD does not track: harness/FEAT-2581-feature-record-package (not gating).
ADDED PF-14c27514e2b6867bcfb13c6fc5e48234
ADDED PF-c36ed89c5d60906308d92ab5d60eb0a7
ADDED PF-c82fdafb108996c2b8e421d7e3e9f1ef
ADDED PF-390fdc3e437034275ce76d0b728ac620
ADDED PF-502d3541ddcee716cab0352ee9cd74cd
PANEL cycle 2 from .../runs/repanel-product/panel-c2.md -> .../plan.yaml
APPLIED .../plan.yaml
```

check, re-run with no change, exit 0:

```text
OK T-01 11 anchor(s) resolved
OK T-02 2 anchor(s) resolved
OK T-03 1 anchor(s) resolved
CHECK /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/plan.yaml against /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package: 3 task(s), 14 anchor(s) resolved, 0 failure(s)
```

I hold no shell, so neither command was run by me. The `[...]` and `...` marks are my elisions of absolute paths and of the INV-29 remove command.

## Assessment

- **Why FAIL and not PASS.** pm applied four substance changes in this run (PF-14c2, PF-c36e, PF-c82f, PF-390f), and no reader has read them. pm says so itself (OQ-REREAD). The changes are large:
  - a new committed binary measurement artifact;
  - a 31-line verify that recomputes every divergence;
  - raw-byte gate capture.

  This is the run's must_fix.
- **Convergence.** The surface narrowed from 5 findings to 4. Three cycle-1 findings closed cleanly, and the closed findings broke nothing new. A cycle-3 re-read over T-01, T-03 and D-02 is likely to converge. If the orchestrator prefers not to spend it, my own O-10 rule applies: put the four unread changes to the operator as one blocking signature question.
- **The goal-check addendum is pm grading its own unread text.** It claims "RG-A2 and the T-01/SC-03 contradiction are closed in the text". That is pm's claim, not a reader's verdict. The grades standing does not cover the four findings.
- **Prototype gate.** The design reader self-scoped out again, and there is still no end-user surface, so no prototype is needed. The operator may override this.
- **Harness-side observations from the record-panel output** (outside this feature's tasks):
  - INV-29: a standing FEAT-2557 worktree.
  - INV-37: no gh-sync Build-entry receipt.
  - "run repanel-product has unknown historical cycle attribution".

  These belong to the orchestrator.
- Nothing is signed, and no file under `.agents/` was edited.

```yaml
VERDICT: FAIL
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/runs/repanel-product/digest.md
DIGEST:
  headline: 'FEAT-2581 re-panel c2 FAILs: 4 of 6 cycle-1 substance findings are re-read
    closed (PF-ccd4, PF-d91c, PF-aaf4, PF-b3de). PF-e7dd is not closed and is reopened.
    PF-7999''s D-02 inventory still does not bound the output delta. 2 new substance
    findings were raised (T-01 gate vs SC-03, high; RG-A2 unbounded, med). pm applied
    all 4 substance items, and no reader has read that text yet. The plan stays pending;
    check exits 0. No mission downgrade.'
  open_questions:
  - id: PL-08
    question: 'Should the scope reader re-read the text pm applied in cycle 2 (re-panel
      cycle 3) before signature? It covers T-01''s intent gate paragraph, T-03''s
      verify and intent, D-02.choice, and BRIEF SC-02, SC-05..08, SC-10 and the disclosure.
      Four open findings are unread: PF-14c27514, PF-c36ed89c, PF-c82fdafb and PF-390fdc3e.
      The alternative is to put them to the operator as one blocking signature question.
      Recommendation: re-panel. The surface narrowed from 5 findings to 4, and the
      closures broke nothing new.'
    blocking: true
  - id: PL-01
    question: 'Ruling on PF-7999938a and its restatement PF-c36ed89c (D-02, high,
      open). Should the import-failure diagnostics that name deleted files point at
      the module actually loaded? Signing would authorize only the source text. Every
      measured byte stays red until it is ruled in divergence-rulings.json, now including
      the canonical_reader_audit scanned-file-count delta that T-03 discloses. Recommendation:
      sign D-02 through an approval.rulings overrule, then rule the measured records
      after the build. Facts updated in c2: the scope reader judged the inventory
      not yet bounded, and pm''s fix (raw gate bytes, audit at both checkouts) is
      unread.'
    blocking: true
  - id: PL-03
    question: 'D-01 premise correction. Settled said classification rows change only
      file and id. Instead, 24 caller rows'' remedies and the canonical_reader_audit
      keys become feature_record.read.load_feature_json, because the audit matches
      a row only when its callee equals its remedy. Accept? Recommendation: yes. Unchanged
      in c2.'
    blocking: false
  - id: PL-04
    question: 'PF-d35d903d, narrowed by PF-502d3541 (proportionality, task, open).
      The bun junit run stays for SC-10 either way. The operator decides only whether
      to keep the CLI ledger''s bun-spawned class, with its zero-records cli_identity
      gate, and feat2581-bun-preload.js. Dropping them narrows Settled Q3. Recommendation:
      keep.'
    blocking: false
  - id: PL-05
    question: Who rules T-03's measured divergences, and can that be delegated as
      it was in FEAT-70? Expect at least the relocated traceback frames and the audit
      scanned-file count. Unchanged in c2, except that the audit count is added.
    blocking: false
  - id: PL-06
    question: 'Backlog the (61.b) gap? test-check-state-feat59 (61.b) has never tested
      stale INV-40 registration: Ctx loads the observer before INV-42 runs (ctx.py:391,
      runner.py:325-334). Fixing it needs a new test seam, which Settled forbids.
      Recommendation: backlog it as a separate chore. The c2 scope reader confirmed
      the facts.'
    blocking: false
  - id: PL-07
    question: 'Harness defect candidates for the harness owner. (a) INV-41''s heuristic
      _inv41_invocation flagged an SC that named check-state.py only as a captured
      process. (b) DEC-191 names bin/feature-schema.json, but the schema is at schemas/feature.json.
      (c) The Harness product checkout has no docs/spec.md, docs/decisions.md or docs/architecture.md.
      (d) New in c2: record-panel''s check-state output reported ''run repanel-product
      has unknown historical cycle attribution'' for a registered run. (e) New in
      c2: the lead digest contract forces readers[].reason to none for a ran reader,
      so the goalcheck reader''s provenance (ran once in plan-product, not re-run
      in c2) cannot ride in readers: and is carried in adequacy_notes instead.'
    blocking: false
  - id: PL-09
    question: T-03 now commits gzip measurement files at notes/measurements/{baseline,pin}.jsonl.gz.
      Nobody has measured their size, and it is unknown whether any gate objects to
      binaries under feature notes. Accept, or set a size ceiling? Raised by pm (OQ-LEDGER-SIZE).
    blocking: false
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/plan.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/BRIEF.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/notes/research-feature-record-package.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/notes/research-FEAT-2581-feature-record-package-goalcheck-plan.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/notes/review-harness-code-reviewer-plan-c2.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/notes/review-harness-ui-reviewer-plan-c2.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/observations/harness-pm.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/runs/repanel-product/state.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/runs/repanel-product/panel-c2.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/runs/repanel-product/acceptance-criteria.md
  expertise_update: []
  team: plan
  steps_run: 4
  cycles_used: 1
  members:
  - step: scope
    persona: harness-code-reviewer
    verdict: FAIL
    headline: 'Closed: PF-ccd4, PF-d91c (migration only) and PF-aaf4. Not closed:
      PF-e7dd. Not bounded: PF-7999. New: T-01 gate vs SC-03 (high) and RG-A2 (med)'
    files_touched:
    - .harness/harness/features/FEAT-2581-feature-record-package/notes/review-harness-code-reviewer-plan-c2.md
  - step: should-not-exist
    persona: fable-advisor
    verdict: PASS
    headline: 'PF-b3de0ad1 closed: one checkout-root token. One low proportionality
      finding narrows open PF-d35d to the bun ledger class plus the preload script'
    files_touched: []
  - step: design
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'Self-scoped out: T-01 and T-03 have no user-facing surface, and no
      DESIGN.md is needed'
    files_touched:
    - .harness/harness/features/FEAT-2581-feature-record-package/notes/review-harness-ui-reviewer-plan-c2.md
  - step: apply
    persona: harness-pm
    verdict: PASS
    headline: Applied the 4 substance items to T-01, T-03, D-02 and the BRIEF; reopened
      PF-e7dd; panel c2 recorded (5 added, open). record-panel and check exit 0. The
      goal-check addendum says the grades stand. All of this is unread
    files_touched:
    - .harness/harness/features/FEAT-2581-feature-record-package/plan.yaml
    - .harness/harness/features/FEAT-2581-feature-record-package/BRIEF.md
    - .harness/harness/features/FEAT-2581-feature-record-package/notes/research-feature-record-package.md
    - .harness/harness/features/FEAT-2581-feature-record-package/notes/research-FEAT-2581-feature-record-package-goalcheck-plan.md
    - .harness/harness/features/FEAT-2581-feature-record-package/observations/harness-pm.md
  must_fix:
  - 'Re-read, by the scope reader before signature, the substance text pm applied
    in this run without a reader: PF-14c27514 (T-03 verify/intent: measurement binding
    to review_sha), PF-c36ed89c (T-03 and D-02.choice: raw gate bytes, audit count
    delta), PF-c82fdafb (T-01 intent gate paragraph vs SC-03) and PF-390fdc3e (T-03
    and SC-10: bounded baseline_failing). The alternative is to put all four to the
    operator as one blocking signature question.'
  branch: none
  escalations: []
  adequacy_notes:
  - 'Re-read verdicts per cycle-1 substance finding, with worktree pointers, are in
    runs/repanel-product/digest.md and panel-c2.md. Closed: PF-ccd4ca98, PF-d91cba6c
    (closes the migration; (61.b) was already vacuous), PF-aaf45b29, PF-b3de0ad1.
    Not closed: PF-e7dd0045, reopened via set-panel. Not bounded: PF-7999938a, whose
    authorization half was not reviewed and is the operator''s.'
  - 'Reader provenance, which the contract does not let readers[].reason carry for
    a ran reader:

    - scope (code-reviewer): cycle-2 re-read, FAIL, 4 findings.

    - should-not-exist (fable-advisor): resolved and ran, PASS, 1 finding transcribed
    by the lead.

    - design (ui-reviewer): self-scoped out, 0 findings.

    - goalcheck (pm): ran once at plan exit in run plan-product and was re-graded
    there after the cycle-1 apply. It was NOT re-run in cycle 2 (SC-09); pm only appended
    a dated addendum that the grades stand.


    panel-c2.md and plan.yaml panel.readers carry these reasons in full.'
  - 'plan-merge.py check exits 0 per pm''s verbatim relay: ''OK T-01 11 anchor(s)
    resolved / OK T-02 2 / OK T-03 1 / CHECK ...: 3 task(s), 14 anchor(s) resolved,
    0 failure(s)''. record-panel --cycle 2 exited 0, with ADDED PF-14c2, PF-c36e,
    PF-c82f, PF-390f and PF-502d. I hold no shell and ran neither command. pm''s research
    note lacks the verbatim outputs; the digest carries them.'
  - record-panel's embedded check-state output showed INV-29 (a standing FEAT-2557
    worktree) and INV-37 (no gh-sync Build-entry receipt). Neither belongs to this
    feature's plan tasks; they are orchestrator housekeeping.
  - pm's goal-check addendum rests on pm's own reading of its unread c2 text, so it
    does not cover the four open findings.
  - 'Prototype gate: the design reader self-scoped out again and there is no end-user
    interaction, so no prototype is required. The operator may override in either
    direction.'
  - 'Cycles: one send-back to pm, by message, for verbatim command outputs only; no
    reader was sent back.'
  - Nothing is signed, and no file under .agents/ was edited.
  sc_status:
  - id: perspective:code maintainer
    verdict: met (cycle-1 grade stands per pm addendum; unread c2 text)
    method: inspection (goalcheck addendum, not re-run)
    evidence: notes/research-FEAT-2581-feature-record-package-goalcheck-plan.md addendum
      2026-11-27
  - id: perspective:operator
    verdict: met (cycle-1 grade stands per pm addendum; unread c2 text)
    method: inspection (goalcheck addendum, not re-run)
    evidence: notes/research-FEAT-2581-feature-record-package-goalcheck-plan.md addendum
      2026-11-27
  needs_approval: true
  severity_max: high
  matrix_ok: none
  coverage_gaps: []
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: scope
    summary: "PF-e7dd0045 \u2014 T-03 still accepts CLI and replay PASS markers without\
      \ measured evidence bound to the review pin."
    why: "plan.yaml:298\u2013321 checks some metadata and reruns grade, but a receipt\
      \ with no CLI/replay records can pass. Six script hashes need not name six distinct\
      \ paths, and the verifier compares the implementation pin to HEAD without independently\
      \ binding HEAD to the authoritative review SHA (bin/validate-digest.py:462\u2013\
      483). Disposition: open (PF-14c27514), applied by pm, unread."
  - kind: substance
    scope: none
    severity: high
    reader: scope
    summary: "PF-7999938a \u2014 D-02 still does not bound the rendered-output delta;\
      \ authorization remains with the operator."
    why: "plan.yaml:337 filters already text-decoded gate streams by module substring,\
      \ losing other changed frame context or line-ending bytes; the audit prints\
      \ its live bin Python-file count (bin/canonical_reader_audit.py:212\u2013229,771\u2013\
      782), which T-01 changes while T-03 captures the audit only at the pin (plan.yaml:339).\
      \ Disposition: open (PF-c36ed89c), applied by pm, unread; authorization with\
      \ operator."
  - kind: substance
    scope: none
    severity: high
    reader: scope
    summary: "T-01\u2019s pre-commit gate rejects the mutation output SC-03 requires\
      \ it to preserve."
    why: "plan.yaml:254 requires both whole-suite commands to exit zero with no FAIL\
      \ line; SC-03 preserves four deliberate mutation FAIL lines that bin/run_pool.py:107\u2013\
      113 relays on exit zero, and T-03 records the integration compiler failure.\
      \ Disposition: open (PF-c82fdafb), applied by pm, unread."
  - kind: substance
    scope: none
    severity: med
    reader: scope
    summary: "RG-A2 \u2014 T-03 does not bound baseline_failing to the measured set."
    why: "plan.yaml:311\u2013314 subtracts every self-declared baseline_failing path;\
      \ an extra baseline failure can hide loss of a previously passing file; plan.yaml:329\
      \ measures only tests/integration/test-typescript-typecheck.py. Disposition:\
      \ open (PF-390fdc3e), applied by pm, unread."
  - kind: proportionality
    scope: task
    severity: low
    reader: should-not-exist
    summary: 'PF-d35d903d''s facts changed: the bun run now stays for SC-10 regardless,
      so the open operator decision covers only the bun-spawned ledger class and feat2581-bun-preload.js,
      not the run itself.'
    why: 'plan.yaml T-03 case-identity paragraph keeps the junit run even if the bun
      ledger leg is dropped, so dropping saves no execution. Disposition: open (PF-502d3541);
      not trimmed, because trimming would narrow Settled Q3, which is the operator''s
      call.'
  readers:
  - reader: scope
    status: ran
    persona: harness-code-reviewer
    reason: none
  - reader: should-not-exist
    status: ran
    persona: fable-advisor
    reason: none
  - reader: design
    status: ran
    persona: harness-ui-reviewer
    reason: none
  - reader: goalcheck
    status: ran
    persona: harness-pm
    reason: none
```
