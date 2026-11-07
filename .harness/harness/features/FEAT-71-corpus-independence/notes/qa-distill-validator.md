# qa-distill-validator — harness-qa craft Expertise (proposal only, NOT applied)

**BLUF:** accept C1 and C2 (two replace ops, each displacing a weaker entry); reject C3. Nothing applied; central merge/check follows.

Target: `.harness/expertise/harness-qa.md` (PRODUCT checkout, read live, sha tag 9630).

## Counts
- Before: Patterns 15/15, Gotchas 15/15, Outcomes 10/10, Open 1/5 (46 lines, budget 150).
- Projected after: unchanged — Patterns 15, Gotchas 15, Outcomes 10, Open 1. Both ops are replace-by-displacement; no section grows.

## Candidates
- **C1 ACCEPT** (Outcomes, displaces O-05). Existing entries do not cover it: O-03 grades fail-first reds, P-09/G-13 judge arms that exist; none says an assertion green against baseline merely has no red available, so "cannot discriminate" is an unproven claim needing a mutation proof. Sources: `runs/validate-validator/digest.md` Assessment ("absence of a pre-change defect is not a demonstrated test defect"); `notes/review-harness-qa-c1.md` Finding 2 (overclaim withdrawn). Displaced O-05: weaker because it is a narrow sibling of P-09 (vacuous arm) and O-06 (per-site mutation) in the same mutation-proof cluster.
- **C2 ACCEPT** (Gotchas, displaces G-11). Durable and not covered: G-03 is about test cases for env-selected modes, G-15 about clean detached checkout at SHA; neither says inherited project-root env from the parent session leaks into a standalone clone. Backlog defect itself (B-6 hermetic verifies) not promoted; generic wording, no env-var names. Source: `notes/ship-review-fix-c1-validator.md` Operator notes + B-6. Evidence is one incident, relayed by lead; kept as a rule, incident dropped. Displaced G-11: weaker because change_type vocabulary is a plan-record validity matter guarded upstream and narrow in reach.
- **C3 REJECT.** Distinction (per-block success vs compound-command completion) is largely covered by O-07 (state scope of evidence), O-09 (re-derive from primitive measurement) and G-04 (task-local pass is not the full kind). The lead already handled it correctly (claimed only block-level success, marked pipeline builder-reported); the residual is the harness backlog defect (no exit marker), which is not Expertise. Source: `runs/fix-c1-validator/digest.md` Adequacy; B-6.

## Ops (verbatim, see digest)
1. replace O-05 (Outcomes) — C1 text.
2. replace G-11 (Gotchas) — C2 text.

## Open questions
None blocking. Note: id reuse (replace keeps O-05/G-11) means any external citation of the old entries would repoint.

## Ops JSON (verbatim, proposal only, not applied)

```json
[
  {
    "op": "replace",
    "target": "O-05",
    "section": "Outcomes",
    "entry": "WHEN a baseline-green assertion has no pre-change defect to redden against DO report only that discrimination is unshown, never that it cannot discriminate — absence of a red is not a useless test; assert uselessness only with a mutation proof that stays green.",
    "why": "C1: no existing entry covers this. A claim that baseline-green assertions cannot discriminate was withdrawn at the lead's validation round, since a missing red is not a demonstrated defect. Displaces O-05, a narrow sibling of P-09 and O-06 in the mutation-proof cluster."
  },
  {
    "op": "replace",
    "target": "G-11",
    "section": "Gotchas",
    "entry": "WHEN running a suite in an independent clone or standalone checkout DO unset inherited project-root environment variables exported by the parent session and record the environment — tooling can resolve the parent tree, so a green or red run is not independent of it.",
    "why": "C2: durable environment and root-isolation lesson that G-03 and G-15 do not cover. The backlog defect is not promoted. Displaces G-11, a narrow plan-record validity entry guarded upstream."
  }
]
```

## Application receipt

- Apply (cwd feature root, HARNESS_AGENT_TYPE=harness-qa): `python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/expertise-merge.py ops --file .harness/expertise/harness-qa.md --ops .harness/harness/features/FEAT-71-corpus-independence/runs/distill-validator/ops-harness-qa.json` -> REPLACED O-05, REPLACED G-11, exit=0.
- Check (once): `python3 .claude/skills/harness/bin/check-expertise.py .harness/expertise/` -> exit=0; harness-qa.md OK. One unrelated ADVISORY on harness-security-reviewer.md (G-01 names a DEC id), not mine.
- Counts before: Patterns 15, Gotchas 15, Outcomes 10, Open 1. After: Patterns 15, Gotchas 15, Outcomes 10, Open 1.
