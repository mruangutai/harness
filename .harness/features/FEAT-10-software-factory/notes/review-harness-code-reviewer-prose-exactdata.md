# Review — FEAT-10 prose-delta, exact-data sweep on the 13 undiffable criteria + REQ-01..08

**Scope.** The prior pass (`review-harness-code-reviewer-prose-delta.md`) diffed SC-01, SC-12, SC-13,
SC-18, SC-19, SC-21, SC-22 against pre-rewrite text fragments and PASSED. This pass covers the
remaining 13 criteria plus REQ-01..08, none of which have pre-rewrite BRIEF text quoted anywhere in
this tree at criterion-body granularity. Control is `plan.yaml` (task intents, `verify:` blocks,
test-case lists) and `DESIGN.md` (C-1..C-5), neither of which went through the plain-English rewrite
(`notes/answers-esc1-a1.md:67-91`, the FOURTH RULING — read directly, not inferred from the prior
review's characterization of it). The ruling's own scope: "the meaning, the count, the ids, the
`verify:` methods, the `evidence:` kinds, and the REQ traces" must not change — this is a check for
what the 2026-08-08 rewrite altered, not a general BRIEF/plan.yaml consistency audit.

**No `git diff` baseline exists** (feature dir is untracked, established by the prior pass, not
re-confirmed here). `reviewed: none` below is a genuinely inapplicable scalar for that reason, not an
omission.

**BLUF: PASS, no gating finding.** All 13 criteria plus REQ-01..08 check out clean against `plan.yaml`
and `DESIGN.md`, with two non-gating advisories. One of them (SC-10's `evidence:` field) looked at first
like a rewrite-introduced drift and is not one — see the SC-10 detail section for how that was
determined and ruled out as a gate.

## Table — the 13

| SC | Result | BRIEF anchor | Control anchor |
|---|---|---|---|
| SC-10 | **advisory — med, non-gating (pre-existing, not rewrite-introduced)** | `:232-237`, `evidence: unit` | see detail section below |
| SC-16 | clean | `:147-152` | `plan.yaml:696-701` (body order), `:702-721` (board+station), `:651-656` (labels), `:657-679` (parent, "at most one," "only when none is recorded") |
| SC-17 | clean | `:154-157` | `plan.yaml:722-782` (D-14 second pass), `T-04` step 7 "parent never added," T-12's `depends_on` count = 6 confirmed at `plan.yaml:1631` (`[T-02, T-04, T-05, T-06, T-07, T-11]`) matching "the six-blocker task" |
| SC-20 | clean | `:185-187` | `plan.yaml:936-938` — the hash-before/after test case, byte-identical `plan.yaml`/`BRIEF.md`, `feature.yaml` the only changed hash |
| SC-04 | clean | `:193-195` | `plan.yaml:1308-1322` (T-06, branch `factory/issue-<n>`, "must never leave the checkout on the default branch") |
| SC-05 | clean | `:196-198` | `plan.yaml:1397-1398` (T-07, "no call to `gh pr merge`... no git push whose refspec is the default branch") |
| SC-09 | clean | `:224-230` | `plan.yaml:42` (D-01, three purposes in the same order), `plan.yaml:1509-1527` (T-09/DEC-186, DEC-138 named as baseline, blocked_by never read back, cost per-blocker-per-candidate) |
| SC-11 | clean | `:204-206` | `DESIGN.md:152-154` — "the five tools with a command line — `factory_config`, `factory_decompose`, `factory_claim`, `factory_workspace`, `factory_land`," stream-split contract at `:149-150` |
| SC-03 | clean | `:211-212` | `plan.yaml:811-813` (T-04: "only harness file this tool writes is `feature.yaml`... must never write `plan.yaml`, `BRIEF.md` or any approval block") |
| SC-06 | **advisory — med, non-gating** | `:214-215`, "records a **claimed** issue" | `plan.yaml:1446-1464` (T-08/INV-24) checks `factory.repo` for **every** recorded issue in `factory.issues` and `factory.parent` — published, not specifically claimed via the git-ref/`factory:claimed` mechanism. See detail section below |
| SC-08 | clean | `:221-222` | `plan.yaml:300-306` (T-02: "SC-08 requires every tool to refuse to infer its repository or board from the working directory," cited by name) |
| SC-14 | clean | `:251-253` | `DESIGN.md:168-169` — "SC-14 asserts zero mutating calls over the full recorded call list on every refusal path reached before it," cited by name, verbatim match |
| SC-15 | clean | `:255-258` | `plan.yaml:1639,1673-1677,1715-1723` — real process exit status, forked stub run, unwrapped-entry-point case |

## REQ-01..REQ-08 (`BRIEF.md:22-41`)

No exact-data mismatch found against `plan.yaml`/`DESIGN.md`. All eight are prose-level descriptions
of capability with no ids, exit codes, field names, or counts embedded that could drift independent of
meaning. One item checked and **not** a finding, disclosed for the record: REQ-01 says the board spans
"several repositories," while T-01's actual `fleet.yaml` write (`plan.yaml:132-135`) lists only
`mruangutai/harness`. This is not a mismatch — the fleet schema is a list the operator can extend
post-ship, T-01 is this increment's starting snapshot, and REQ-01 describes the system's designed
capability, not T-01's initial data. Noting it so it is not re-raised as new.

## SC-10 detail — looked like drift, traced back, ruled out as a gate

`plan.yaml` gives this exact-data point real teeth: T-12's intent names SC-10 and SC-15 together as
"written about the status **a process** exits with" (`:1642-1644`), states unit tests are "blind to"
the class of defect that "passes every one of those [unit] tests and **violates SC-10 in production**"
(`:1646-1647`), and labels the fork-level case explicitly "**the SC-10 case and the reason the file
exists**" (`:1676-1677`). T-12 is registered in `INTEGRATION_SCRIPTS`, never `UNIT_SCRIPTS`
(`:1725-1727`). Taken alone, that reads as `evidence: unit` (BRIEF.md:237) being wrong — it should
match SC-15's correctly-declared `evidence: integration` (BRIEF.md:258) for the same class of claim.

**That reading does not survive checking `runs/`, which is where pre-rewrite state actually lives.**
`runs/arch-eng/digest.md:45-48` shows SC-10 was already understood as a process-exit criterion at the
architecture-review stage, before T-12 existed at all ("no test observes a process exit status that
SC-10 is written about" was that review's own finding, which is what drove T-12's later addition —
confirmed by `runs/revise-product/digest.md:80`, "new T-12... Closes SC-10's process-exit gap").
Critically, `runs/revise2-product/digest.md:41` — several review cycles before this feature's
plain-English rewrite — already counts BRIEF's `evidence:` values as "**14 unit, 3 integration (SC-06,
SC-15, SC-19)**," the same 14-unit/3-integration split (now 15/3 after SC-20 joined the unit column)
that holds today, with SC-10 among the 14 the whole time. No review between `revise2-product` and the
2026-08-08 rewrite (`contract-validator`, `final-product`, `final2-product`, `prose-delta-validator`)
flags `evidence: unit` on SC-10 as wrong, despite `contract-validator` discussing SC-10 directly
(`:35,100,115`).

**Conclusion: `evidence: unit` on SC-10 predates the plain-English rewrite by several cycles.** It is
not something the FOURTH ruling altered, dropped or invented — the ruling's own scope is "a rewrite of
the PROSE only" (`answers-esc1-a1.md:72-73`), and this field was already what it is now well before that
ruling existed. Whether `unit` vs `integration` is the *correct* editorial call for SC-10 is a real,
disclosable question — plan.yaml's own reasoning (a mis-wired entry point "passes every one of those
[unit] tests and violates SC-10 in production") argues for `integration`, or at minimum for SC-10 and
SC-15 sharing one evidence value — but it is a pre-existing document inconsistency, not a rewrite
defect, and this pass's remit is the latter. Recorded as a non-blocking open question rather than a
`must_fix`.

## SC-06 detail — why this is advisory, not gating

"records a claimed issue" (BRIEF.md:214) is broader in the control than the phrase suggests: T-08's
INV-24 fires on **any** recorded issue in a feature's `factory.issues` map or its `factory.parent` —
published task/parent issues, independent of GitHub claim state (the `factory:claimed` label, the
`refs/heads/factory/issue-<n>` ref). "Claimed" is heavily overloaded in this feature's vocabulary (D-05's
claim mechanism, the `building` station meaning "an agent holds the claim") and reusing it here risks a
reader assuming the invariant is scoped to claimed issues only. It is not gating because T-08's own
`verify:` and test cases are the actual normative spec for the implementer and enforce the broader
scope regardless of SC-06's prose — a narrow ("claimed-only") implementation would fail T-08's own test
cases (e.g. "two features recording the same repository and issue number produce a violation," which
does not require either issue to carry the claimed label). So the imprecision cannot silently let a
too-narrow implementation ship; it is a clarity issue only. No baseline exists anywhere in the tree to
confirm whether "claimed" is itself rewrite-introduced or older phrasing carried through; either way it
is advisory-only for the reason above.

## Severity summary

| Item | Severity | Gates |
|---|---|---|
| SC-10 `evidence: unit` — plan.yaml's own reasoning argues for `integration`, matching SC-15, but the value predates this rewrite by several review cycles (`runs/revise2-product/digest.md:41` onward) | med, advisory | no |
| SC-06 "claimed issue" broader than what T-08 actually checks | med, advisory | no |
| All other 11 of the 13, and REQ-01..08 | clean | n/a |

```yaml
VERDICT: PASS
DIGEST:
  headline: "All 13 undiffed criteria plus REQ-01..08 check out clean against plan.yaml/DESIGN.md; two non-gating advisories, neither attributable to the 2026-08-08 rewrite -- SC-10's evidence:unit looks like it should match SC-15's evidence:integration per plan.yaml's own reasoning about T-12, but runs/revise2-product/digest.md:41 shows that value predates the rewrite by several review cycles, so it is a pre-existing document inconsistency outside this pass's remit rather than rewrite drift; SC-06's 'claimed issue' phrase is broader in T-08's actual check than the prose implies, but T-08's own verify/test cases are normative and would catch a too-narrow implementation regardless"
  severity_max: med
  findings: 2
  must_fix: []
  spec_violations: []
  reviewed: none
  human_commits_in_scope: []
  open_questions:
    - { id: Q1, question: "SC-10 (BRIEF.md:237) declares evidence: unit. plan.yaml:1642-1649 and :1673-1677 argue the class of defect SC-10 exists to exclude (a mis-wired CLI entry point) 'passes every one of those [unit] tests and violates SC-10 in production,' which is exactly why T-12 (evidence: integration territory, INTEGRATION_SCRIPTS) exists -- the same reasoning that correctly gives SC-15 evidence: integration. Traced through runs/: this value is not rewrite-introduced (stable since runs/revise2-product/digest.md:41, several cycles before the 2026-08-08 plain-English pass), so it does not gate this review, but it looks like a real pre-existing editorial inconsistency worth a deliberate call at signature: either correct SC-10 to evidence: integration, or record why unit is judged sufficient despite plan.yaml's own stated reasoning.", blocking: false }
    - { id: Q2, question: "SC-06 (BRIEF.md:214-215) says the state check fires on a feature that 'records a claimed issue,' but T-08/INV-24 (plan.yaml:1446-1464) checks every recorded factory issue regardless of GitHub claim state. Not gating -- T-08's own verify/test cases are normative and enforce the broader scope regardless -- but worth a one-word tighten ('a recorded issue' or 'a published issue') before signature so the overloaded word 'claimed' doesn't collide with D-05's claim mechanism for a future reader.", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/features/FEAT-10-software-factory/notes/review-harness-code-reviewer-prose-exactdata.md
```
