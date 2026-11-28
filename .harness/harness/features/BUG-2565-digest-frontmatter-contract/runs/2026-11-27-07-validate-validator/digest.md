# Validate c2: BUG-2565 at ed064577

**ESCALATE.** All four round-1 must_fix items are closed and were measured. The fix round introduced one new T-03 defect, and it breaks the letter of SC-07. The rework budget ends with this round, so the operator has to decide: fix it, or accept it as a residual.

Reviewed: 104252db..ed064577a769b853e291cd71117404cb5dfc3731, focused on bb401aae..ed064577. Cycles used: 0. Members: qa PASS, code FAIL, security FAIL, ui PASS (scoped out), pm PASS.

## What closed (measured, not taken from the receipt)

| Round-1 item | Evidence |
|---|---|
| T-03 code grade | `code-grade.py` passes every production function: `_Loader.project` grade 4, `render` grade 4 (code, QA, pm). The four new witnesses fail on bb401aae's production files and pass at the pin (QA §(d)). Parity is 16/16 (QA, pm). `--check` and the port gate both pass |
| Classification JSON | `test-check-plan-routes.py` is green. The integration kind is green with 95 tests, `runner_exit 0` (QA receipt) |
| DECISIONS-INDEX word cap | 30, 25 and 27 words; `test-gen-decisions-index.py` is green |
| SPEC.md:779 | The Unavailable row now names the yield refusal, so the operator perspective is met (pm) |

The advisory items are also done: three refusals, the OQ-4 narrowing, the probe correction line and the SKILL:146 sentence. QA found no weakened test. All 7 amend dispositions are met.

## Remaining: one gating finding

**F-1. T-03 · substance · code high / security med (both transcribed unchanged). Location: `.claude/skills/harness/bin/gen-agent-output.py:33-63`, in `continues` and `kept`.**

`continues()` treats any line that starts with `-` as part of the stale `output:` value. This causes three failures:

- A valid mapping key such as `-mode: keep me`, placed right after a stale `output:` block, is silently deleted. Round 1's c1 code preserved it, so this is a regression from the fix round. Code and security measured it independently.
- A comment between the items of an indentationless sequence ends the dropped span and leaves an orphaned item.
- A YAML-escaped quoted key, `"struc\u0074ured"`, is not recognised, so the generator adds a duplicate key.

All three outputs re-render identically, so `--check` reports ok. `check-omp-port.py`'s strict parser rejects the last two. The deletion still parses, so nothing catches it.

This breaks SC-07's clause "leaves each agent's … other frontmatter keys byte-for-byte unchanged" (BRIEF.md:29). PM's SC-07 "met" covers only the four enumerated witnesses. On the letter I side with code and security, so SC-07 is **partial**.

My reading of severity: none of the 16 shipped agents triggers it, since all of them render byte-identical. The trigger is a hand-edited frontmatter shape that is unusual but valid. Two of the three cases fail closed at the port gate. So it is real and a regression, but contrived. The gate counts code's `high` as given, because I do not revise a reader's rating.

**Repair** (main-session-direct; the file is in T-03's set and in the bin tree):
1. Find the generated keys' spans by parsing YAML rather than matching line prefixes. One way is `yaml.compose` node marks over the frontmatter. Another is to accept `-` continuation only for lines matching `^-(\s|$)`, and to treat blank or comment lines as continuation until the next top-level key.
2. Parse the prospective frontmatter strictly before writing, and refuse to write if the parse fails or the set of non-generated keys changes.
3. Add three raw-byte witnesses: a dash-prefixed sibling key, a commented indentationless sequence, and an escaped quoted key. Each must fail RED first.

This also closes PM A-1 and QA gap 2 (orphan lines from a blank or comment line, which is the same mechanism).

## Advisory (non-blocking, ranked)

1. QA, low, T-03: no test pins the new rule that nothing is written if any persona fails (`gen-agent-output.py:118-122`). A revert would stay green. Add one witness alongside F-1.
2. Code, low, form, T-06: `DECISIONS-INDEX.md:109` says "narrow gates refuse matching commands", which overstates the rule. Reword to "narrow gates fail closed only for guarded commands".
3. Security, low, T-02: validator diagnostics forwarded to the child can include an executable path when a spawn fails (`harness-hooks.ts:398-404,432-435,880-885`). This was carried over from round 1, and base forwarded similar detail.
4. PM A-2, low, form, plan record, pre-existing at bb401aae: `plan-merge.py check` exits 1, because T-06's org.html quote anchor names removed text. Do not cite `plan-merge check` as green.
5. Code, med (advisory): grade-2 test functions `walk` and `case_generator` (`test-digest-projection.py:38,189`). The reasons are recorded and they do not gate.

## Operator decision (OQ-1)

- **(a) Fix:** spend a third round, outside the 2-round budget, on F-1 plus advisory 1–2. The diff is small and stays inside T-03 and T-06.
- **(b) Accept:** treat F-1 as a named residual with a follow-up issue and ship. SC-07 is then recorded as partial against its byte-preservation clause, which is the same treatment OQ-2 got.

I recommend (a). The defect is a silent data loss that the fix round introduced. The repair is local and its witnesses are cheap to write, whereas a permanently partial SC-07 would be contested every time anyone reads it.

## Adequacy

- QA's receipts are results from the host interpreter, not CI.
- Fail-first evidence for SC-01, SC-02, SC-03 and SC-06 comes from round 1. Their subject code is unchanged between bb401aae and ed064577.
- F-1 was measured independently by two lenses, code and security. Neither the gates nor the tests detect it.

```yaml
VERDICT: ESCALATE
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2565-digest-frontmatter-contract/.harness/harness/features/BUG-2565-digest-frontmatter-contract/runs/2026-11-27-07-validate-validator/digest.md
DIGEST:
  headline: 'ed064577 closes all four round-1 must_fix items (measured: unit 69 and
    integration 95 green, parity 16/16, production code-grade pass, 3/3 perspectives
    met). The fix round introduced one T-03 regression, a silent frontmatter key deletion
    in gen-agent-output.py:33-63, which breaks SC-07''s byte-preservation letter.
    The budget is spent, so the operator chooses: fix it or accept it as a residual.'
  open_questions:
  - id: OQ-1
    question: 'F-1 (T-03, code high / security med): gen-agent-output.py:33-63 continues()
      treats any line starting with ''-'' as part of a stale output: value. A valid
      sibling key ''-mode: keep me'' is therefore silently deleted; c1 preserved it,
      so this is a fix-round regression. Two other cases: a commented indentationless
      sequence leaves an orphan item, and an escaped quoted key "struc\u0074ured"
      is duplicated. --check stays ok in all three. The port gate catches the last
      two but not the deletion. None of the 16 shipped agents triggers any of them.
      This breaks SC-07 ''other frontmatter keys byte-for-byte unchanged'' (BRIEF.md:29).
      The rework budget is exhausted. Choose (a) a third round: YAML-span-aware key
      removal plus a strict pre-write parse that refuses if the non-generated key
      set changes, with three RED-first raw-byte witnesses, all in T-03 files and
      main-session-direct; or (b) accept F-1 as a named residual with a follow-up
      issue and ship with SC-07 partial. Lead recommends (a): silent data loss, a
      local repair and cheap witnesses.'
    blocking: true
  files_touched:
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/runs/2026-11-27-07-validate-validator/state.yaml
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/runs/2026-11-27-07-validate-validator/digest.md
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/observations/harness-pm.md
  expertise_update: []
  team: validate
  steps_run: 5
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: Unit 69 and integration 95 green at ed064577 (runner_exit 0). Both round-1
      reds now pass. The 4 new witnesses are red on bb401aae's files and green at
      the pin. Parity 16/16, production code-grade pass, no test weakened.
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: FAIL
    headline: 'T-03 still fails SC-07: the generator can silently delete unrelated
      YAML or write invalid frontmatter that its own drift check accepts. The c1 code-grade
      and root-ref findings are closed.'
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: FAIL
    headline: 'T-03''s generator regresses SC-07: regeneration can silently delete
      valid, unrelated frontmatter.'
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'Mode B scoped out: the 25-path fix-round delta touches no rendered
      or interactive UI.'
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: All 3 perspectives pass (operator now met via SPEC.md:779). SC-01..SC-11
      met and 7/7 amend dispositions met. The T-03 amendment is ledgered and INV-40-clean.
      One low advisory (A-1).
    files_touched:
    - .harness/harness/features/BUG-2565-digest-frontmatter-contract/observations/harness-pm.md
  must_fix:
  - 'F-1 T-03 (code-reviewer high, security-reviewer med; substance): gen-agent-output.py:33-63,
    continues()/kept(), removes generated keys by line-prefix heuristics. A valid
    dash-prefixed sibling key after a stale output: is silently deleted (regression
    vs c1). A commented indentationless sequence leaves an orphan item. An escaped
    quoted generated key is duplicated. Repair: find the generated keys'' spans from
    parsed YAML, or accept ''-'' continuation only for ''^-(\s|$)'' and treat blank/comment
    lines as continuation until the next top-level key. Strictly parse the prospective
    frontmatter before writing, and refuse if the parse fails or the non-generated
    key set changes. Add RED-first raw-byte witnesses for all three cases. This also
    closes pm A-1 and QA gap 2. Budget exhausted, so it is routed via OQ-1.'
  branch: feat/BUG-2565-digest-frontmatter-contract
  escalations:
  - id: E-1
    raised_by: harness-code-reviewer, harness-security-reviewer
    question: Fix F-1 in a third rework round beyond the 2-round budget, or accept
      it as a named residual with SC-07 partial?
    domain: rework budget / SC-07 acceptance
    routed_to: orchestrator -> operator
    resolution: pending
    decided_by: operator
    recorded_as: open_questions OQ-1
  adequacy_notes:
  - All four round-1 must_fix items were re-measured at the pin by QA and pm, not
    taken from the build receipt. QA ran code-grade, parity, --check, the port gate,
    and fail-first of the 4 new witnesses against bb401aae's production files.
  - QA receipts are host-interpreter results, not CI.
  - Fail-first for SC-01/02/03/06 carries from round 1. QA confirmed the subject code
    is unchanged between bb401aae and ed064577.
  - 'SC-07 contradiction resolved: pm graded it met on the four enumerated witnesses,
    but code and security each measured the dash-key deletion against BRIEF.md:29''s
    ''other frontmatter keys byte-for-byte unchanged''. Lead rules SC-07 partial on
    the letter.'
  - 'Lead severity reading for F-1: med. It is real and a regression, but no shipped
    agent triggers it and two of the three cases fail closed at check-omp-port.py.
    Code''s high is transcribed unchanged and gates.'
  - Settled items (OQ-1..OQ-4 of round 1, D-01..D-05) were not re-raised by any reader.
  - Every finding is task-scoped; the task is named in each summary. The schema forces
    scope to n/a.
  sc_status:
  - id: SC-01
    verdict: met
    method: automated unit
    evidence: omp-hooks.test.ts:2357; natural red at 104252db (QA c1); hook unchanged
      in fix round
  - id: SC-02
    verdict: met
    method: automated unit
    evidence: omp-hooks.test.ts:2385; mutation-witnessed (QA c1)
  - id: SC-03
    verdict: met
    method: automated unit
    evidence: omp-hooks.test.ts:1737; red at base (QA c1)
  - id: SC-04
    verdict: met
    method: inspection
    evidence: 'pm: 0 retired symbols in harness-hooks.ts at ed064577; digest-schema.ts
      absent'
  - id: SC-05
    verdict: met
    method: inspection
    evidence: binding probe; agent blob unchanged since bb401aae (pm, code)
  - id: SC-06
    verdict: met
    method: automated integration
    evidence: test-check-omp-port.py:205; integration kind green 95 (QA receipt)
  - id: SC-07
    verdict: partial
    method: automated unit + review
    evidence: '4 new witnesses red at bb401aae, green at pin (QA). Byte-preservation
      clause broken by F-1: gen-agent-output.py:33-63 deletes a dash-prefixed sibling
      key (code, security)'
  - id: SC-08
    verdict: met
    method: inspection (QA executed, OQ-3)
    evidence: T-03 parity 16/16 at ed064577 (QA, pm)
  - id: SC-09
    verdict: met
    method: inspection
    evidence: SPEC.md:779, README:182-189, BUILD:58-63, harness-team SKILL:146 (pm)
  - id: SC-10
    verdict: met
    method: inspection
    evidence: 7/7 amend dispositions; index rulings 30/25/27/30 words; test-gen-decisions-index
      green (pm, QA)
  - id: SC-11
    verdict: met
    method: inspection
    evidence: README/BUILD state three refusals (pm)
  - id: PERSPECTIVE-operator
    verdict: met
    method: inspection
    evidence: SPEC.md:779 fixed (pm)
  - id: PERSPECTIVE-orchestrator
    verdict: met
    method: inspection
    evidence: SC-03, SC-05 (pm)
  - id: PERSPECTIVE-code-maintainer
    verdict: partial
    method: inspection
    evidence: pm graded met. Lead downgrades to partial because SC-07 carries this
      perspective and is partial on F-1
  needs_approval: true
  severity_max: high
  matrix_ok: true
  coverage_gaps:
  - 'T-03 gen-agent-output.py:118-122: no test pins the rule that nothing is written
    if any persona fails; a revert stays green (QA, low).'
  - 'T-03 gen-agent-output.py:50-64: a blank or column-0 comment line in a hand-edited
    output block yields unparseable frontmatter that --check calls ok; check-omp-port.py
    exits 1 on it (QA gap 2, pm A-1; same mechanism as F-1).'
  - F-1's dash-key deletion is caught by no gate or test.
  findings:
  - kind: substance
    scope: n/a
    severity: high
    reader: code-reviewer
    summary: 'T-03 F-1: gen-agent-output.py:33-63 line-prefix key removal deletes
      a dash-prefixed sibling key, orphans a commented sequence item, and duplicates
      an escaped quoted key. SC-07 mismatch.'
    why: This is silent frontmatter data loss and a regression from the fix round.
      Security raised the same defect at med; both ratings are kept.
  - kind: substance
    scope: n/a
    severity: med
    reader: security-reviewer
    summary: 'T-03: gen-agent-output.py:50-63 silently deletes a valid dash-prefixed
      sibling key after output (duplicate of F-1).'
    why: Merged into F-1. Kept so the second rating stays traceable.
  - kind: substance
    scope: n/a
    severity: low
    reader: qa
    summary: 'T-03: no witness for the all-or-nothing write at gen-agent-output.py:118-122.'
    why: Advisory. Add one alongside F-1.
  - kind: form
    scope: n/a
    severity: low
    reader: code-reviewer
    summary: 'T-06: DECISIONS-INDEX.md:109 ''narrow gates refuse matching commands''
      overstates DEC-100.'
    why: Advisory. Reword to 'narrow gates fail closed only for guarded commands'.
  - kind: substance
    scope: n/a
    severity: low
    reader: security-reviewer
    summary: 'T-02: harness-hooks.ts:398-404,432-435,880-885 forwards internal validator
      diagnostics, including a spawn executable path, to the child.'
    why: Advisory, carried from c1; base forwarded similar detail.
  - kind: form
    scope: n/a
    severity: low
    reader: pm
    summary: 'Plan record: plan-merge.py check exits 1 on T-06''s stale org.html quote
      anchor (pre-existing at bb401aae).'
    why: Advisory. Do not cite plan-merge check as green.
  - kind: substance
    scope: n/a
    severity: med
    reader: code-reviewer
    summary: 'T-03: grade-2 test functions walk and case_generator at tests/unit/test-digest-projection.py:38,189.'
    why: Advisory test-grade record with reasons. Does not gate.
  readers:
  - reader: qa
    status: ran
    persona: harness-qa
    reason: n/a
  - reader: code
    status: ran
    persona: harness-code-reviewer
    reason: n/a
  - reader: security
    status: ran
    persona: harness-security-reviewer
    reason: n/a
  - reader: ui
    status: ran
    persona: harness-ui-reviewer
    reason: n/a
  - reader: goalcheck
    status: ran
    persona: harness-pm
    reason: n/a
```
