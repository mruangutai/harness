# FEAT-1928 append readability review

**PASS: human-authored fence closure and object retry are actionable; validator prose repair is absent. The missing durable browser pointer is now closed; unchanged low/form host attribution remains.** Mode B at exact pin `f9c9f1e21d05ae1d64f3f1fed38465be89059dc1`; bounded review, not whole-feature ship authorization. Paths below are repository-relative, or feature-relative for `notes/` and `runs/`.

- **Measured self-scope:** complete `3c1923cf→f9c9f1e` census has 28 paths: three source/instruction/test paths and 25 feature records/evidence paths. No new visual implementation, DESIGN or prototype path; two added PNGs are saved evidence, not UI. `ee39d887→f9c9f1e` is exactly eight feature metadata/evidence paths, with no source/test/schema/config/probe delta (`artifact://855`). Visual delta is out of scope; explicitly assigned operator guidance remains reviewed. No new 457-path audit.
- **SC-07/D-03/DEC-208 readability:** `.claude/skills/harness-handoff/SKILL.md:43–46` says close every prose fence, correct the human assessment and retry the object. `.claude/skills/harness/bin/validate-digest.py:1858–1874` reads existing bytes, preserves identical-record idempotency, constructs the exact safe-dumped suffix, checks canonical selection before any write, then writes only that suffix. Its refusal names the digest and concrete action: “close any unfinished prose fence before returning.” Following both instructions changes the author's prose and resubmits the object, never asks the validator to close fences or hand-author validated YAML. `digest_record.py:33–64` is unchanged from 3c; no parser repair or live fallback. Three added cases cover first-record refusal, stale-correction refusal and closed-fence success. Main's RED22/24, GREEN24/24, pool120 and actual refusal→author closure→retry are Main executions recorded in `notes/append-visibility-rework.md`, not mine. Source inspection supports closure of the original fence-guidance/readability defect; code/QA/PM own full criterion adjudication.
- **Durable browser binding:** `notes/browser-guidance-proof.md` records Main's actual managed Chromium at executed ee39, 1365×768, light/dark emulation, scroll, computed styles, saved image inspection and closed session. Independently verified pinned `org.html` is byte-unchanged from 3c and SHA256 **e3fa27d470053712baacb7749f341b9b0369e6e77e0a3239301277033cb14114**. Pinned light/dark image hashes exactly match receipt **e818387c…d285 / a90b1934…141c**; inspected local receipt/images/guard/reader/guidance are byte-equivalent to pin. My saved-image inspection sees wrapped, unclipped paragraph text in both 649×121 crops; it is not my browser execution. Prior Q1 (missing pointer) is closed by this durable binding.
- **Original contrast high stays closed, not downgraded:** unchanged HTML tokens and `.digest ~ .sub` retain prior measured **7.204:1 light / 7.788:1 dark**; Main's recorded computed pairs match those tokens at 12.5px. No fresh contrast calculation or full accessibility guarantee claimed. These paragraph crops do not establish responsive/full-page layout, focus, keyboard or overflow access; those remain unverified and require human/rendered checking if claimed. New non-rendering guidance has no theme/focus/layout dimension, not a visual PASS. No new UAT gate.
- **Retained advisory:** pinned `.claude/skills/harness-digest-dev/SKILL.md:80`, independently unchanged from 3c, still attributes missing-field rejection to `SubagentStop`, contrary to SC-08 and `org.html:289–291`. Original F-UI-02 low/form/task remains; no compatibility gate is restored. Prior control-plane URI-routing concern remains outside this feature; no bypass or new routing execution.

No source/test/config/approval/ledger edits; no tests, builds, linters, formatters, probes or browser/UAT runs by this reader. Only metadata/hash/source-equivalence checks and source/saved-image inspection. Open questions: none for this bounded UI assignment; general runtime, authorization and complete SC closure remain the other readers' remit.

```yaml
VERDICT: PASS
DIGEST:
  headline: Fence guidance requires human closure and object retry; durable browser pointer closes, with unchanged low host-attribution advisory.
  mode: B
  in_scope: false
  severity_max: low
  findings:
    - kind: form
      scope: task
      severity: low
      reader: ui-reviewer
      summary: F-UI-02 — unchanged T-02 specialist rules attribute rejection to SubagentStop.
      why: 'Pinned harness-digest-dev/SKILL.md:80 contradicts SC-08 and org.html:289–291; original low/form retained, documentation only, no re-gate.'
  must_fix: []
  states_unspecified: []
  contract_violations: []
  a11y: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.harness/harness/features/FEAT-1928-digest-object-contract/notes/review-harness-ui-reviewer-append.md
```
