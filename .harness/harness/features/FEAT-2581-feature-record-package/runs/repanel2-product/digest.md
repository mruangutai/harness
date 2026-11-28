# repanel2-product (cycle 3): FEAT-2581 team digest

**BLUF: FAIL. Do not sign yet.**

The four open cycle-2 substance findings are all reader-confirmed closed:
- PF-14c27514, closed on the second read. Its parent PF-e7dd0045 is resolved with it.
- PF-c36ed89c: the inventory now bounds the delta. Authorization is still the operator's.
- PF-c82fdafb.
- PF-390fdc3e.

All five of this cycle's first-read findings were applied and closed on the second read.

No applied substance text is unread. The run still fails for a different reason. The one permitted second read raised **four new med substance findings**, all in T-03's verify. Per the dispatch, these were left open and **not applied**:
- PF-96cdf9f1: invalid base64 is accepted as a captured stream.
- PF-3882d444: source-only d02# entries are not bound to the real file, symbol and templates.
- PF-cf9cf710: build-divergences.md can omit the `divergence:` records that SC-08 requires.
- PF-a37e5b40: the operator disclosure can consist of escaped byte literals only, with no readable account.

Plan state:
- plan.yaml is still `approval.status: pending`, with panel cycle 3 recorded.
- `plan-merge.py check` exits 0.
- Nothing is signed, and nothing under .agents/ was edited.
- No reader raised a `scope: mission` finding, so I do not recommend a downgrade.

## Verdicts on the open cycle-2 substance findings

| id | reader | verdict | read | worktree pointer | final |
|---|---|---|---|---|---|
| PF-14c27514 (restates PF-e7dd0045) | scope | closed | 2nd (not closed on the 1st) | plan.yaml:339–340, 360, 368, 370; BRIEF.md:41, 43 | resolved, T-03 (PF-e7dd0045 also resolved, T-03) |
| PF-c36ed89c | scope | closed: the inventory bounds the delta (authorization not judged) | 1st | D-02.choice plan.yaml:152; T-03 intent :372–376; BRIEF.md:47, 98–102 | resolved, T-03; PF-7999938a stays open |
| PF-c82fdafb | scope | closed | 1st | T-01 intent plan.yaml:286; SC-03 BRIEF.md:35 | resolved, T-01 |
| PF-390fdc3e | scope | closed | 1st | T-03 verify :335–336, 347–349; intent :364; SC-10 BRIEF.md:51 | resolved, T-03 |

The pointers cite the worktree plan.yaml as the readers read it, before or after the cycle-3 apply.

## Findings raised in this run (reader's own severity and kind; ids from record-panel)

| id | reader | sev | kind | summary | disposition |
|---|---|---|---|---|---|
| PF-0ab2a541 | scope | high | substance | PF-14c27514 not closed: missing required measurement streams accepted | applied (T-03 verify :339, intent :360); 2nd read **closed**; resolved T-03 |
| PF-74107187 | scope | med | substance | audit-count disclosure can disagree with the committed raw audit | applied (verify :346, intent :374); 2nd read **closed**; resolved T-03 |
| PF-f8e3277e | design | high | substance | D-02's operator-facing disclosure is not bound to the measured output | applied (verify :341, :346; intent :374, :376); 2nd read **closed**; resolved T-03 |
| PF-b045e378 | should-not-exist | med | proportionality (task) | T-03 machinery exceeds Settled Q3(a), undisclosed | disclosed at BRIEF.md:104–110; 2nd read **closed**; resolved. Amending Q3(a) is the operator's call (PL-10) |
| PF-2ddbc141 | should-not-exist | low | proportionality (task) | two divergence implementations, so drift voids the receipt | applied (intent :376, normative for both); 2nd read **closed**; resolved T-03 |
| PF-96cdf9f1 | scope | med | substance | invalid base64 accepted as a captured stream | **open, not applied** (2nd read) |
| PF-3882d444 | scope | med | substance | unrelated source templates accepted for unreached D-02 items | **open, not applied** (2nd read) |
| PF-cf9cf710 | scope | med | substance | build-divergences.md can lack the `divergence:` records SC-08 requires | **open, not applied** (2nd read) |
| PF-a37e5b40 | design | med | substance | disclosure may consist of escaped byte literals only | **open, not applied** (2nd read) |

Still open, and the operator's: PF-7999938a (authorization), PF-d35d903d and PF-502d3541 (the bun-leg pair; should-not-exist confirmed the facts are unchanged).

Open after this run: 7 in total, 4 of them med substance findings that are not the operator's alone.

Resolved in this run: 10, by pm through set-panel. Each resolution follows a reader's closed verdict.

## Steps

| step | persona | verdict | note |
|---|---|---|---|
| scope | harness-code-reviewer | FAIL | 1st read: 3 of 4 closed, plus 1 new med. 2nd read: both routed findings closed, plus 3 new med. Notes: notes/review-harness-code-reviewer-plan-c3.md and notes/review-harness-code-reviewer-plan-c3-reread.md |
| should-not-exist | fable-advisor | PASS | Resolved and ran twice. Nothing should be deleted; T-03's machinery is the ruled price of PF-14c27514. Its 2 proportionality findings were closed on the 2nd read |
| design | harness-ui-reviewer | FAIL | In scope (a text-only operator disclosure); no DESIGN.md is needed. 1st read: high. 2nd read: high closed, plus 1 new med. Notes: notes/review-harness-ui-reviewer-plan-c3.md and notes/review-harness-ui-reviewer-plan-c3-reread.md |
| apply | harness-pm | PASS | Pass 1 changed T-03 verify and intent and added the BRIEF disclosure sentence; routing is in runs/repanel2-product/apply1-changes.md. Pass 2 was record-panel, set-panel and check only, with no text change |

Cycles: one send-back wave, in which each of the three readers got its one second read (cycles 1 per reader in state.yaml). The second pm dispatch was the planned record step, not a send-back.

## pm's command outputs, verbatim as pm relayed them

record-panel `--cycle 3 --digest runs/repanel2-product/panel-c3.md`, exit 0. The check-state preamble is the same as in cycle 2:
- BRIEF not approved;
- INV-29 FEAT-2557 standing worktree;
- INV-37 no Build-entry receipt;
- the note "run repanel2-product has unknown historical cycle attribution";
- FEATURE SET untracked.

Its body:

    ADDED PF-0ab2a54115f601adc844b6ff906f5564
    ADDED PF-74107187b30075ff469855f63e753993
    ADDED PF-f8e3277e88a9a8d53e8fc85c312ba652
    ADDED PF-b045e378e3a26989ec460a400717b923
    ADDED PF-2ddbc1410bd086da4924c7a25bf1ab96
    ADDED PF-96cdf9f10890ac070da480030c481192
    ADDED PF-3882d444d53e5048aab5db3565f24435
    ADDED PF-cf9cf710f71b769e92a542d62f352636
    ADDED PF-a37e5b4054c542a0b7b80de309c1f9ca
    PANEL cycle 3 from FD/runs/repanel2-product/panel-c3.md -> FD/plan.yaml
    APPLIED FD/plan.yaml

set-panel printed `PANEL cycle 3 -> FD/plan.yaml` and `APPLIED FD/plan.yaml`, exit 0. It changed disposition and resolved_by on 10 findings.

check, exit 0:

    OK T-01 11 anchor(s) resolved
    OK T-02 2 anchor(s) resolved
    OK T-03 1 anchor(s) resolved
    CHECK /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/plan.yaml against /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package: 3 task(s), 14 anchor(s) resolved, 0 failure(s)

The full preamble text is in pm's research note §12. I hold no shell and ran neither command.

## Assessment

- **Why FAIL.** By the dispatch's own rule, a substance finding raised on the second read stops the run unapplied. Four did. Nothing is unread. What fails the run is unclosed findings, not unread text.

- **Convergence, and what it says.** The severity is falling: cycle 2 had 3 high and 1 med; cycle 3's first read had 2 high and 1 med; its second read has 4 med and no high. Every new finding sits in one mechanism, T-03's inline verify, and each is narrower than the one it follows: key presence, then encoding validity, then field binding, then a marker, then legibility.

  That is the O-09 shape: each repair surfaces one narrower failure in the same mechanism, and another enumerate-and-patch round will likely find a fifth. The cheaper close is to have pm key the verify on what it must guarantee, so the four findings fall out together:
  - every stream decodes strictly;
  - every disclosed field is derived from the refs, never accepted from the file;
  - every SC-08 marker is present;
  - every ruled id carries a readable account.

  The four are cheap and med, and PF-cf9cf710 is a direct SC-08 mismatch. My recommendation is PL-11 option (a).

- **should-not-exist's answer to the dispatch's question.** After two rounds of hardening, T-03's verify carries no machinery that should not exist. Each piece traces to PF-14c27514, PF-c36ed89c or Settled Q3(a). The exceedance over Q3(a) is now disclosed for the signer (BRIEF.md:104–110), not silent.

- **Goal-check.** It was not re-run (SC-09). pm appended a dated cycle-3 addendum after pass 1, because T-03's grade-bearing text changed. As in cycle 2, the addendum is pm's own reading. It does not cover the four open findings.

- **Prototype gate.** The design reader judged itself in scope this time, but only for a text disclosure; there is no end-user interaction. No high-fidelity prototype is required. The operator may override in either direction.

- **Form deviations I accepted rather than spend a spawn on (O-02):**
  - fable-advisor returned a structured object instead of the one-key yaml block. Its findings were complete, and I transcribed them.
  - Two readers labelled themselves by persona; I recorded them under their team step ids, as in panel-c2.md.
  - pm's pass-2 files_touched omitted the research note it appended to §12; I added it to the union.

- **Housekeeping for the orchestrator, outside this feature:** INV-29 (the FEAT-2557 worktree) and INV-37 (gh-sync Build-entry receipt), as in cycle 2.

```yaml
VERDICT: FAIL
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/runs/repanel2-product/digest.md
DIGEST:
  headline: FEAT-2581 re-panel c3 FAILs. Readers confirmed all 4 open cycle-2 substance
    findings closed (PF-14c2 with PF-e7dd, PF-c36e (bounded; authorization stays the
    operator's), PF-c82f, PF-390f). All 5 c3 first-read findings were applied and
    closed on the second read, so no applied text is unread. The one second read raised
    4 new med substance findings in T-03's verify (PF-96cd, PF-3882, PF-cf9c, PF-a37e),
    left open and unapplied. The plan stays pending, panel c3 is recorded and check
    exits 0. No mission downgrade.
  open_questions:
  - id: PL-11
    question: 'Four med substance findings in T-03''s verify are open and unapplied.
      They were raised by the one permitted second read:

      - PF-96cdf9f1: invalid base64 is accepted as a captured stream.

      - PF-3882d444: d02# source-only entries are not bound to the real file, symbol
      and templates.

      - PF-cf9cf710: build-divergences.md can omit the `divergence:` records SC-08
      requires.

      - PF-a37e5b40: the operator disclosure can be escaped byte literals only, with
      no readable account.

      Should there be (a) one more bounded re-panel, in which pm keys the verify on
      guarantees (strict decode, fields derived from the refs, SC-08 marker required,
      a readable account per ruled id) followed by one scope and design read, or (b)
      a ruling at signature (overrule, or defer to build review)?

      Recommendation: (a). The four are cheap, and PF-cf9c is a direct SC-08 mismatch.
      Severity is falling (high to med) but the findings keep narrowing within one
      mechanism (O-09), so pm should apply the guarantee in one pass rather than patch
      the four one by one.'
    blocking: true
  - id: PL-01
    question: 'Ruling on PF-7999938a (D-02, high, open): authorize the import-failure
      diagnostics that name deleted files to point at the module actually loaded?
      Signing authorizes only the source text; every measured byte stays red until
      it is ruled in divergence-rulings.json, including the canonical_reader_audit
      scanned-file-count delta. Recommendation: sign D-02 through an approval.rulings
      overrule, then rule the measured records after the build. Updated in c3: the
      scope reader confirmed the inventory now BOUNDS the delta (PF-c36ed89c resolved:
      raw gate bytes, whole-stream comparison, audit at both checkouts with the count
      derived from the raw stdout). Only the authorization half remains.'
    blocking: true
  - id: PL-10
    question: 'New in c3 (pm OQ-Q3A; should-not-exist PF-b045e378, resolved by disclosure).
      T-03''s committed raw-measurement store, its sitecustomize recorder and its
      recomputing verify exceed Settled Q3(a), ''reusing FEAT-70''s receipt-script
      structure with no new proof framework''. FEAT-70 at a98451c5 committed none
      of these. The BRIEF now discloses this at BRIEF.md:104-110. Do you amend Q3(a)
      at signature, or accept the exceedance as disclosed? If amended, BRIEF Constraints
      ''Identity proof (Q3 a)'' (BRIEF.md:91-93) and T-03 intent''s opening sentence
      should be repointed. Recommendation: accept as disclosed. should-not-exist found
      that none of the machinery should be removed.'
    blocking: false
  - id: PL-03
    question: 'D-01 premise correction. Settled said classification rows change only
      file and id. Instead, 24 caller rows'' remedies and the canonical_reader_audit
      keys become feature_record.read.load_feature_json, because the audit matches
      a row only when its callee equals its remedy. Accept? Recommendation: yes. Unchanged
      in c3.'
    blocking: false
  - id: PL-04
    question: 'PF-d35d903d, narrowed by PF-502d3541 (proportionality, task, open).
      The bun junit run stays for SC-10 either way. The operator decides only whether
      to keep the CLI ledger''s bun-spawned class, with its zero-records cli_identity
      gate, and feat2581-bun-preload.js. Dropping them narrows Settled Q3. Recommendation:
      keep. Unchanged in c3; should-not-exist confirmed the facts are unchanged.'
    blocking: false
  - id: PL-05
    question: 'Who rules T-03''s measured divergences, and can that be delegated as
      it was in FEAT-70? Expect at least the relocated traceback frames and the audit
      scanned-file count. Updated in c3: each ruled item now arrives in build-divergences.md
      as a delimited divergence_entry, with exact old and new byte reprs and the audit
      count derived from the raw stdout. If PL-11(a) is taken, each also carries a
      readable account.'
    blocking: false
  - id: PL-06
    question: 'Backlog the (61.b) gap? test-check-state-feat59 (61.b) has never tested
      stale INV-40 registration: Ctx loads the observer before INV-42 runs (ctx.py:391,
      runner.py:325-334). Fixing it needs a new test seam, which Settled forbids.
      Recommendation: backlog it as a separate chore. Unchanged in c3.'
    blocking: false
  - id: PL-07
    question: "Harness defect candidates for the harness owner.\n(a) INV-41's heuristic\
      \ _inv41_invocation flagged an SC that named check-state.py only as a captured\
      \ process.\n(b) DEC-191 names bin/feature-schema.json, but the schema is at\
      \ schemas/feature.json.\n(c) The Harness product checkout has no docs/spec.md,\
      \ docs/decisions.md or docs/architecture.md.\n(d) record-panel's check-state\
      \ output reports 'run <id> has unknown historical cycle attribution' for a registered\
      \ run. It recurred in c3 for repanel2-product.\n(e) The lead digest contract\
      \ forces readers[].reason to none for a ran reader, so reader provenance rides\
      \ in adequacy_notes and panel-c3.md.\n(f) New in c3, from pm: the panel finding\
      \ schema has no rationale key, so resolution rationale (for example 'authorization\
      \ NOT judged' on PF-c36ed89c, or PF-e7dd0045 resolved via its restatement) lives\
      \ only in the pm research note \xA712."
    blocking: false
  - id: PL-09
    question: T-03 commits gzip measurement files at notes/measurements/{baseline,pin}.jsonl.gz.
      Their size is unmeasured, and it is unknown whether any gate objects to binaries
      under feature notes. Since c3, every record must carry every stream of its kind
      as full base64 bytes, which can only grow them. Accept, or set a size ceiling?
    blocking: false
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/plan.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/BRIEF.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/notes/research-feature-record-package.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/notes/research-FEAT-2581-feature-record-package-goalcheck-plan.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/notes/review-harness-code-reviewer-plan-c3.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/notes/review-harness-code-reviewer-plan-c3-reread.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/notes/review-harness-ui-reviewer-plan-c3.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/notes/review-harness-ui-reviewer-plan-c3-reread.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/runs/repanel2-product/state.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/runs/repanel2-product/panel-c3.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/runs/repanel2-product/acceptance-criteria.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2581-feature-record-package/.harness/harness/features/FEAT-2581-feature-record-package/runs/repanel2-product/apply1-changes.md
  expertise_update: []
  team: plan
  steps_run: 4
  cycles_used: 1
  members:
  - step: scope
    persona: harness-code-reviewer
    verdict: FAIL
    headline: 'Closed: PF-c36e (bounded), PF-c82f and PF-390f on the 1st read; PF-14c2
      and the audit-count finding on the 2nd read. The 2nd read raised 3 new med substance
      findings (invalid base64, unbound source-only templates, missing SC-08 divergence:
      records)'
    files_touched:
    - .harness/harness/features/FEAT-2581-feature-record-package/notes/review-harness-code-reviewer-plan-c3.md
    - .harness/harness/features/FEAT-2581-feature-record-package/notes/review-harness-code-reviewer-plan-c3-reread.md
  - step: should-not-exist
    persona: fable-advisor
    verdict: PASS
    headline: T-03's verify carries no machinery that should not exist. The Q3(a)
      exceedance (med) and the dual-implementation drift (low) were both closed on
      the 2nd read; nothing new
    files_touched: []
  - step: design
    persona: harness-ui-reviewer
    verdict: FAIL
    headline: 'In scope as a text-only operator disclosure, so no DESIGN.md is needed.
      The high finding (disclosure not bound to measured bytes) closed on the 2nd
      read; 1 new med finding: disclosure may be byte literals only'
    files_touched:
    - .harness/harness/features/FEAT-2581-feature-record-package/notes/review-harness-ui-reviewer-plan-c3.md
    - .harness/harness/features/FEAT-2581-feature-record-package/notes/review-harness-ui-reviewer-plan-c3-reread.md
  - step: apply
    persona: harness-pm
    verdict: PASS
    headline: Pass 1 applied T-03 verify and intent plus a BRIEF disclosure sentence,
      with no APPROVAL-RESET. Pass 2 ran record-panel c3 (9 added), set-panel (10
      resolved) and check, all exit 0. Approval is still pending; the 4 second-read
      findings were not applied
    files_touched:
    - .harness/harness/features/FEAT-2581-feature-record-package/plan.yaml
    - .harness/harness/features/FEAT-2581-feature-record-package/BRIEF.md
    - .harness/harness/features/FEAT-2581-feature-record-package/notes/research-feature-record-package.md
    - .harness/harness/features/FEAT-2581-feature-record-package/notes/research-FEAT-2581-feature-record-package-goalcheck-plan.md
  must_fix:
  - 'Close the four open med substance findings in T-03''s verify, raised by the second
    read and left unapplied:

    - PF-96cdf9f1: strict base64 validation of every stream.

    - PF-3882d444: bind d02# source-only file, symbol and templates to both refs.

    - PF-cf9cf710: require SC-08''s `divergence:` records in build-divergences.md.

    - PF-a37e5b40: require a readable, id-linked account beside the byte reprs.

    This needs either one more bounded re-panel (apply plus a scope and design read)
    or an operator ruling at signature (PL-11).'
  branch: none
  escalations: []
  adequacy_notes:
  - 'Verdicts per open cycle-2 substance finding:

    - PF-14c27514: closed on the 2nd read (plan.yaml:339-340, 360). PF-e7dd0045 resolved
    via its restatement.

    - PF-c36ed89c: closed on the 1st read (D-02.choice :152, T-03 intent :372-376).
    Bounding only; authorization was not judged.

    - PF-c82fdafb: closed on the 1st read (T-01 intent :286).

    - PF-390fdc3e: closed on the 1st read (T-03 verify :335-336, 347-349).

    The full table is in runs/repanel2-product/digest.md.'
  - 'Reader provenance, which readers[].reason cannot carry for a ran reader:

    - scope: 1st read FAIL with 2 findings; 2nd read FAIL with 3 new.

    - should-not-exist: resolved and ran twice, PASS both times; findings transcribed
    by the lead.

    - design: Mode A in scope (text disclosure); 1st read FAIL; 2nd read FAIL with
    1 new.

    - goalcheck (pm): ran once in run plan-product and was not re-run in c2 or c3
    (SC-09). Its dated c3 addendum is pm''s own reading and does not cover the 4 open
    findings.

    panel-c3.md carries the full reasons.'
  - No applied substance text is unread. Every pass-1 change went back to the reader
    who raised it (apply1-changes.md routes items 1-4), and each of those findings
    was confirmed closed. The FAIL comes from unclosed second-read findings, not from
    unread text.
  - "pm relayed both outputs verbatim, exit 0 each:\n- record-panel --cycle 3: ADDED\
    \ 9 PF ids.\n- check: 3 task(s), 14 anchor(s) resolved, 0 failure(s).\nThe outputs\
    \ are in digest.md and research note \xA712. I hold no shell and ran neither command."
  - 'Cycles: one send-back wave, with three readers each re-reading once (cycles 1
    per reader in state.yaml). pm''s second dispatch was the planned record step,
    not a send-back.'
  - 'Prototype gate: no end-user interaction, so no high-fidelity prototype is required.
    The design reader''s in-scope call covers only a text disclosure. The operator
    may override in either direction.'
  - 'Accepted form deviations (O-02):

    - fable-advisor returned a structured object instead of the one-key yaml block;
    its findings were complete and I transcribed them.

    - Two readers self-labelled by persona; I recorded them under their step ids.

    - pm''s pass-2 files_touched omitted the research note it appended; I added it
    to the union.'
  - 'Highest severity among the findings that remain open: med. The high findings
    raised this run are resolved.'
  - Nothing is signed, and no file under .agents/ was edited. Every task is still
    main-session-direct.
  sc_status:
  - id: perspective:code maintainer
    verdict: met (cycle-1 grade stands per pm's dated c3 addendum; does not cover
      4 open med findings)
    method: inspection (goalcheck addendum, not re-run, SC-09)
    evidence: notes/research-FEAT-2581-feature-record-package-goalcheck-plan.md addendum
      2026-11-27 (cycle 3)
  - id: perspective:operator
    verdict: met (cycle-1 grade stands per pm's dated c3 addendum; does not cover
      4 open med findings)
    method: inspection (goalcheck addendum, not re-run, SC-09)
    evidence: notes/research-FEAT-2581-feature-record-package-goalcheck-plan.md addendum
      2026-11-27 (cycle 3)
  needs_approval: true
  severity_max: high
  matrix_ok: none
  coverage_gaps: []
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: scope
    summary: 'PF-14c27514 not closed: T-03 accepts CLI and replay records missing
      required measurement streams.'
    why: 'plan.yaml:338-343 checked class presence and replay IDs, not stream keys;
      streams {} passed. Disposition: applied (T-03 verify :339, intent :360); 2nd
      read closed; resolved T-03 (PF-0ab2a541).'
  - kind: substance
    scope: none
    severity: med
    reader: scope
    summary: 'New: T-03 accepts an audit-count disclosure that disagrees with the
      committed raw audit.'
    why: 'plan.yaml:346 regex-only; ''0 0'' passed. Disposition: applied (verify :346,
      intent :374); 2nd read closed; resolved T-03 (PF-74107187).'
  - kind: substance
    scope: none
    severity: high
    reader: design
    summary: "D-02\u2019s operator-facing disclosure is not bound to the measured\
      \ output."
    why: 'T-03 verify never read build-divergences.md. Disposition: applied (verify
      :341, :346; intent :374, :376); 2nd read closed; resolved T-03 (PF-f8e3277e).'
  - kind: proportionality
    scope: task
    severity: med
    reader: should-not-exist
    summary: T-03's raw-measurement store, recorder and recomputing verify exceed
      Settled Q3(a) and the plan does not disclose that to the signer.
    why: 'FEAT-70 (a98451c5) has none of these; signer would silently supersede their
      own constraint. Disposition: disclosed at BRIEF.md:104-110; 2nd read closed;
      resolved (PF-b045e378); amending Q3(a) is PL-10.'
  - kind: proportionality
    scope: task
    severity: low
    reader: should-not-exist
    summary: Two independent divergence implementations mean implementation drift,
      not behaviour, voids the receipt.
    why: 'Drift would force a re-pin with nothing wrong. Disposition: T-03 intent
      :376 names the comparison text normative for both, drift = script bug fixed
      with --reuse; 2nd read closed; resolved T-03 (PF-2ddbc141).'
  - kind: substance
    scope: none
    severity: med
    reader: scope
    summary: T-03 accepts invalid base64 as a captured stream.
    why: 'plan.yaml:339-341,360: ''!!!!'' and '''' both decode empty under permissive
      decoding. Disposition: open, not applied (2nd read; PF-96cdf9f1).'
  - kind: substance
    scope: none
    severity: med
    reader: scope
    summary: T-03 accepts unrelated source templates for unreached D-02 items.
    why: 'plan.yaml:341,372,376: any nonblank file/symbol/old_source/new_source passes,
      so the operator can rule on the wrong source. Disposition: open, not applied
      (2nd read; PF-3882d444).'
  - kind: substance
    scope: none
    severity: med
    reader: scope
    summary: T-03 can pass without the `divergence:` records SC-08 requires in build-divergences.md.
    why: 'plan.yaml:335,341,376,378; BRIEF.md:47: divergence_entry blocks alone pass.
      Disposition: open, not applied (2nd read; PF-cf9cf710).'
  - kind: substance
    scope: none
    severity: med
    reader: design
    summary: 'New: T-03 permits an operator-facing disclosure made up only of escaped
      byte literals.'
    why: 'plan.yaml:376 does not require an explanation; multiline/non-ASCII streams
      flatten to one escaped line. Disposition: open, not applied (2nd read; PF-a37e5b40).'
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
