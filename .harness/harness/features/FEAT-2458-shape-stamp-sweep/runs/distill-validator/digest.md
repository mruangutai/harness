# FEAT-2458 distill — validator squad — PASS

**BLUF.** Four personas distilled: 11 ops applied in 5 batches and 0 refusals remain. No diff was reviewed and no suite was run. Each member's receipt was read and checked against the resulting file; every applied entry is present in its file verbatim.

## Per member
| Persona | Ops applied | Rejected candidates | Counts before→after | Receipt (under `notes/`) |
|---|---|---|---|---|
| harness-qa (craft) | replace P-02, P-09, P-14 | skim-only `bool(reason)` weakening: already held by G-06/P-09 | P15→15 G15→15 O10→10 Q1→1 | `expertise-receipt-dbb2bef7….json`, batch `a62b7063…` |
| harness-qa (repo `harness`) | replace G-13; add G-15 | — | P0→0 G14→15 O0→0 Q0→0 | same receipt, batch `64c836f8…` |
| harness-code-reviewer (craft) | replace P-07, G-12 | cand. 3 (isolated predicate probes): held by O-01. Fleet-ruling note: held by O-06 | P15→15 G15→15 O10→10 Q0→0 | `expertise-receipt-972a214e….json`, batch `efbf6da3…` |
| harness-security-reviewer (craft) | replace P-04, G-07 | cand. 3 (blob identity in a test-only round): held by O-01 + O-07 | P15→15 G15→15 O10→10 Q0→0 | `expertise-receipt-0231fabc….json`, batch `667aaa0e…` |
| harness-validator-lead (craft) | replace G-06, O-02 | — | P15→15 G15→15 O10→10 Q0→0 | `expertise-receipt-8399ca5b….json`, batch `3786913f…` |

## Accepted entries by source
- **From the observations log:** 5. All five qa ops come from the three log bullets. No other member logged.
- **From the lead's skim** of the digests and notes: 6. Code-reviewer 2, security 2, and lead 2.
- **Relayed and rejected:** 3. One each from qa, code-reviewer and security, all because the lesson is already held.

## Lead ops
- **G-06, broadened at equal length.** The old entry covered a remedy outside every task's file set. It now also covers a remedy that amends signed intent or criterion wording. Both go up as ESCALATE or an open question, never as must_fix. Evidence: c1 code #1 and #2 became OQ-3 and OQ-2.
- **O-02, displaced.** The old entry had a malformed double prefix and was an implementation rule. Its replacement: a must-fix that restructures tests carries "every predicate still rejects what it rejected before" as acceptance. Evidence: in c2, code-grade exited 0 and the PASS-name sets were unchanged, yet `_feature_row` had weakened to `bool(reason)`.
- **Two self-refusals, both resolved.** My own first two attempts were refused at exit 14 because G-06 was 51 words against a 50-word cap. I shortened the entry and re-applied, and nothing was written by the refused attempts.

## Notes
- harness-ui-reviewer and harness-pm also read in validate, but the dispatch scoped this distill to qa, code-reviewer and security, so neither was distilled.
- qa's repository-tier G-15 names this repo's `test-check-plan-routes.py` self-test registry. qa re-verified it at main `86ce6ba`, and it remains true because OQ-1 and OQ-4 were never fixed.

```yaml
VERDICT: PASS
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2458-shape-stamp-sweep/.harness/harness/features/FEAT-2458-shape-stamp-sweep/runs/distill-validator/digest.md
DIGEST:
  headline: 'FEAT-2458 validator-squad distill PASS: 11 ops applied in 5 batches across
    qa (craft + repo harness), code-reviewer, security-reviewer and the lead; every
    receipt was checked against the resulting file, and 0 refusals remain. 5 accepted
    entries came from the log and 6 from the skim; 3 relayed candidates were rejected
    as already held. No diff was reviewed and no suite was run.'
  team: distill
  steps_run: 3
  cycles_used: 0
  branch: none
  members:
  - step: distill-qa
    persona: harness-qa
    verdict: PASS
    headline: "5 ops. Craft: P-02, P-09, P-14 replaced (P15\u219215 G15\u219215 O10\u2192\
      10 Q1\u21921, batch a62b7063). Repo harness: G-13 replaced, G-15 added (G14\u2192\
      15, batch 64c836f8). Receipt notes/expertise-receipt-dbb2bef7\u2026json. The\
      \ skim candidate (bool(reason) weakening) was rejected as held by G-06/P-09."
    files_touched:
    - .harness/expertise/harness-qa.md
    - .harness/harness/expertise/harness-qa.md
  - step: distill-code
    persona: harness-code-reviewer
    verdict: PASS
    headline: "Craft: P-07 and G-12 replaced; counts unchanged at P15 G15 O10 Q0 (batch\
      \ efbf6da3, receipt notes/expertise-receipt-972a214e\u2026json). Rejected candidate\
      \ 3 (isolated predicate probes) as held by O-01, and the fleet-ruling note as\
      \ held by O-06."
    files_touched:
    - .harness/expertise/harness-code-reviewer.md
  - step: distill-security
    persona: harness-security-reviewer
    verdict: PASS
    headline: "Craft: P-04 (ancestor resolution for confined unlink) and G-07 (escape\
      \ controls in operator diagnostics) replaced; counts unchanged at P15 G15 O10\
      \ Q0 (batch 667aaa0e, receipt notes/expertise-receipt-0231fabc\u2026json). Rejected\
      \ candidate 3 (blob identity in a test-only round) as held by O-01+O-07."
    files_touched:
    - .harness/expertise/harness-security-reviewer.md
  must_fix: []
  files_touched:
  - .harness/harness/features/FEAT-2458-shape-stamp-sweep/runs/distill-validator/state.yaml
  - .harness/harness/features/FEAT-2458-shape-stamp-sweep/runs/distill-validator/digest.md
  - .harness/expertise/harness-validator-lead.md
  - .harness/expertise/harness-qa.md
  - .harness/harness/expertise/harness-qa.md
  - .harness/expertise/harness-code-reviewer.md
  - .harness/expertise/harness-security-reviewer.md
  - .harness/harness/features/FEAT-2458-shape-stamp-sweep/notes/qa-distill.md
  - .harness/harness/features/FEAT-2458-shape-stamp-sweep/notes/review-harness-security-reviewer-distill.md
  - .harness/harness/features/FEAT-2458-shape-stamp-sweep/notes/expertise-receipt-dbb2bef79a883750d7b938f60a623d6bb146ae67c4ff2384501c6862bf8d6f55.json
  - .harness/harness/features/FEAT-2458-shape-stamp-sweep/notes/expertise-receipt-972a214e33e68e198a92eeaf424fb5a392db59a1c56a1097027a18dd9ac049d5.json
  - .harness/harness/features/FEAT-2458-shape-stamp-sweep/notes/expertise-receipt-0231fabc532604cd2df8ba60fcc07748bb213fd71e3bb2b010df784558a3b2bd.json
  - .harness/harness/features/FEAT-2458-shape-stamp-sweep/notes/expertise-receipt-8399ca5bd19d49b20bd723532cca11503e7db526ef39f56945d02a91c3d72721.json
  open_questions: []
  escalations: []
  expertise_update:
  - persona: harness-qa
    op: replace
    target: P-02
    section: Patterns
    entry: "WHEN asserting a token in output, present or absent, DO bind it to the\
      \ specific field or structured record and confirm no fixture-supplied value\
      \ (ids, names, paths) echoed there already contains it \u2014 a bare substring\
      \ check passes vacuously on unrelated or self-supplied text."
    why: A fixture id containing the asserted marker made a token clause vacuous;
      a reason-dropping mutant stayed green a full cycle. Sharpens P-02's substring-vacuity
      rule to cover self-supplied text, same length.
  - persona: harness-qa
    op: replace
    target: P-09
    section: Patterns
    entry: "WHEN judging whether a mutation proof discriminates DO compare against\
      \ a control differing in one factor \u2014 the mutant's effect neutered while\
      \ its reached-marker fires, or, after a test-only fix, the pre-fix tests run\
      \ on the same mutant; only a red the control lacks proves discrimination."
    why: Running pre-fix tests against the same mutant (green) beside the fixed tests
      (red) is what proved a test repair closed a vacuity finding; generalizes P-09's
      neutered-effect arm into one control-arm rule instead of adding to a full section.
  - persona: harness-qa
    op: replace
    target: P-14
    section: Patterns
    entry: "WHEN crediting a test as a required kind's evidence DO confirm that kind's\
      \ cmd actually executes it \u2014 the file on the runner's explicit list and\
      \ the case reachable without a flag or env the runner never passes; a glob match\
      \ or flag-gated registry reports satisfied while never running."
    why: A named SC case was registered only under a self-test flag no runner invokes,
      so it could never redden; same failure class as P-14's glob-without-list-membership,
      so P-14 is broadened rather than a new entry added to a full section.
  - persona: harness-qa
    op: replace
    target: G-13
    section: Gotchas
    entry: "WHEN removing or redirecting under bash-write-guard DO use a literal absolute\
      \ target path \u2014 an rm or redirect whose target contains a shell variable\
      \ is blocked even under /tmp; pipe to grep inside mutant loops, and drive scratch-tree\
      \ setup and cleanup from a python script (shutil)."
    why: 'Observed this feature: rm with a variable target is blocked too, not only
      redirects; the python driver was the working route. Extends G-13 at equal scope.'
  - persona: harness-qa
    op: add
    target: G-15
    section: Gotchas
    entry: "WHEN citing a test-check-plan-routes.py CANONICAL_READER_CASES case as\
      \ evidence DO cite the CI step `check-plan-routes.py --canonical-reader-audit`\
      \ instead \u2014 those cases run only under `--canonical-reader-self-test`,\
      \ which neither run-unit-tests.py nor CI invokes, so they cannot redden."
    why: 'A named SC test in that registry could never redden through a cycle; re-verified
      at main 86ce6ba: only the test file itself references the self-test flag, while
      .github/workflows/tests.yml:243 runs the audit.'
  - persona: harness-code-reviewer
    op: replace
    target: P-07
    section: Patterns
    entry: WHEN tests are refactored to reduce complexity DO compare old and new predicates
      on contract-invalid values the old test rejected, not just on passing fixtures
      or case names; a simpler predicate can admit the wrong type, shape, or value.
    why: The test split kept the same passing cases but let a truthy non-string reason
      pass where a string was required. This check applies to ordinary test refactors
      more often than the displaced meta-gate registry check.
  - persona: harness-code-reviewer
    op: replace
    target: G-12
    section: Gotchas
    entry: WHEN a diagnostic substring is reserved for one outcome DO put the marker
      in interpolated inputs on a different outcome and check the emitted text for
      collisions; searching for literal producers cannot show that dynamic text keeps
      the marker exclusive.
    why: A non-miss reason could acquire the absence marker from an interpolated status
      or id. This production-side probe complements the existing search for alternate
      producers and applies more broadly than the displaced injected-carrier severity
      reminder.
  - persona: harness-security-reviewer
    op: replace
    target: P-04
    section: Patterns
    entry: WHEN auditing deletion confined to a trusted directory DO check how every
      ancestor is resolved and whether enumeration and unlink use the same securely
      opened directory handle. Skipping symlinks at the leaf does not stop pathname
      re-resolution through a redirected parent.
    why: The sweep's leaf check did not confine deletion. This reusable filesystem
      boundary check displaces the narrower invariant-detector exemption guidance;
      the stamp-specific consequence stays in the review record.
  - persona: harness-security-reviewer
    op: replace
    target: G-07
    section: Gotchas
    entry: WHEN operator diagnostics include untrusted filenames or reasons DO verify
      that rendering escapes line breaks and terminal controls, so input cannot appear
      as a separate trusted status line even if no automated gate consumes the output.
    why: The sweep exposed a human-facing integrity boundary not covered by the exit-status
      lesson. This displaces a severity-token reminder already governed by the reviewer
      contract.
  - persona: harness-validator-lead
    op: replace
    target: G-06
    section: Gotchas
    entry: "WHEN a real finding's only remedy edits a file in no task's declared set,\
      \ or amends signed intent or criterion wording, DO route it up \u2014 ESCALATE\
      \ if it gates, an open question if not \u2014 never must_fix: no fix cycle may\
      \ legally apply it."
    why: Two cycle-1 reader findings were real but their remedies rewrote a signed
      task intent and a signed criterion's marker; routing them as open questions
      instead of must_fix kept the fix round on the test-only defects. Generalizes
      G-06's file-set case to signed-wording remedies.
  - persona: harness-validator-lead
    op: replace
    target: O-02
    section: Outcomes
    entry: "WHEN a must-fix restructures tests to clear a structural gate DO put 'every\
      \ predicate still rejects what it rejected before' in its acceptance \u2014\
      \ gate exit 0 and an unchanged PASS-name set both held while a string check\
      \ collapsed to truthiness, caught only a cycle later."
    why: The complexity-driven split cleared code-grade with identical PASS-name sets
      yet weakened a reason check to bool(); only the next panel's code-reviewer probe
      found it. Displaces O-02, a malformed (double-prefixed) entry whose content
      is an implementation rule other personas already hold, not a lead outcome.
  adequacy_notes:
  - 'Distill only: no diff was reviewed and no suite was run.'
  - "Per-section counts before\u2192after:"
  - "- qa craft: P15\u219215, G15\u219215, O10\u219210, Q1\u21921."
  - "- qa repo harness: G14\u219215."
  - "- code-reviewer craft: P15\u219215, G15\u219215, O10\u219210, Q0\u21920."
  - "- security craft: P15\u219215, G15\u219215, O10\u219210, Q0\u21920."
  - "- validator-lead craft: P15\u219215, G15\u219215, O10\u219210, Q0\u21920."
  - 'Accepted entries by source: 5 from the log (all qa) and 6 from the lead''s skim
    (code 2, security 2, lead 2). 3 relayed candidates were rejected as already held,
    one each from qa, code and security.'
  - 'Receipts, all under the feature notes/ directory:'
  - "- qa: expertise-receipt-dbb2bef7\u2026json (2 batches)."
  - "- code: expertise-receipt-972a214e\u2026json."
  - "- security: expertise-receipt-0231fabc\u2026json."
  - "- lead: expertise-receipt-8399ca5b\u2026json (batch 3786913f)."
  - Every member's receipt ops were checked against the resulting files by grep, and
    all 9 member entries are present verbatim.
  - My own first two lead apply attempts were refused at exit 14 because G-06 was
    51 words against a 50-word cap. I shortened it and re-applied successfully; the
    refused attempts wrote nothing.
  - harness-ui-reviewer and harness-pm also read in validate, but the dispatch scoped
    this distill to qa, code-reviewer and security, so neither was distilled.
  sc_status: []
  needs_approval: none
  severity_max: none
  matrix_ok: n/a
  coverage_gaps: []
  findings: []
  readers: []
```
