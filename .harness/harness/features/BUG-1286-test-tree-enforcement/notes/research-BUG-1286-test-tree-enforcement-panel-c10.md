# plan-panel c10 — validator squad digest — BUG-1286-test-tree-enforcement

```yaml
VERDICT: PASS
DIGEST:
  headline: "Both readers independently confirm the divergence is correct and could not break the (a)-(d) rule; PASS at severity_max med, must_fix empty, nothing high/critical/unrated — no ground for a cycle 11."
  team: plan-panel
  steps_run: 2
  cycles_used: 0
  severity_max: med
  members:
    - { step: should-not-exist, persona: fable-advisor, verdict: PASS, headline: "KEEP on the whole shape; divergence CONFIRMED per pattern, refinement FAITHFUL, no undisclosed escape over 3423 cores x 33731 basenames, strike SOUND", files_touched: [] }
    - { step: scope, persona: harness-code-reviewer, verdict: PASS, headline: "KEEP; divergence correct per pattern, rule sound over every constructed shape, one med faithfulness gap in condition (b)", files_touched: [".harness/harness/features/BUG-1286-test-tree-enforcement/notes/review-harness-code-reviewer-planpanel-c10.md"] }
  must_fix: []
  files_touched: [".harness/harness/features/BUG-1286-test-tree-enforcement/notes/review-harness-code-reviewer-planpanel-c10.md", ".harness/harness/features/BUG-1286-test-tree-enforcement/runs/2026-09-04-30-validator/state.yaml", ".harness/harness/features/BUG-1286-test-tree-enforcement/runs/2026-09-04-30-validator/digest.md"]
  branch: feat/BUG-1286-test-tree-enforcement
  adequacy_notes:
    - "Every result in this panel is a hand-simulation of a specification against a reader-written reimplementation. Three independent implementations now agree (pm's prototype at a8532ce3, the c9 goal-check's, and each reader's own), which is convergent evidence — but none of them is the artifact that ships. T-01's mandate to re-prove the four red cases against the BUILT artifact is the only thing that closes this, and it is deferred to build."
    - "The panel closed the BASENAME axis analytically, not merely by fuzzing — both readers derived independently that the agnostic key is airtight (any basename matching it carries the literal, which is_test_shaped refuses at any extension) and the restricted key is sound. Neither reader can bound the AXIS SPACE itself; a third axis remains unexcluded exactly as the plan's honest limit states."
    - "Reader independence is partial: both received the same four-part question and the same named probes, so convergence on (a)/(c)/(d) is less independent than it looks. Their METHODS diverged substantially (advisor 3423x33731 fuzz plus analytic derivation; scope a 220-core generative sweep plus an algebraic argument), which recovers most of it."
    - "No qa, security or UI reader ran. plan-panel is a two-reader team by design and nothing here is user-facing or credential-handling, so this is correct scoping rather than a coverage gap."
    - "Neither reader could tell me whether the (b) defect is worth the last cycle. That is a budget judgement, raised as Q3."
  open_questions:
    - { id: Q1, question: "HARNESS DEFECT: validate-digest.py refuses EVERY plan-phase harness-code-reviewer digest. It requires code_grade, then rejects every value because feature.json records review_sha 'none', which in plan phase it structurally cannot carry (INV-6/DEC-207/BUG-1080). scope's job settled 'failed (exit 1)' despite a complete review and a written artifact — a reader that did its job is recorded as failed. Remedy edits .claude/skills/harness/bin/, which no lead may write; operator decision, not a fix cycle.", blocking: false }
    - { id: Q2, question: "plan.yaml's panel: block still records all four cycle-8 findings as disposition: open. All four were addressed by the c9 one-edit remedy. This cycle's transcription owns closing them against T-01 (c9 goal-check GAP-3).", blocking: false }
    - { id: Q3, question: "Spend the last cycle on the (b) one-clause fix, or carry all three findings into the operator's ONE batched signature review under DEC-176? Panel recommendation: the latter. No finding gates, gates.review is advisory_unless_high, and the (b) remedy is one clause of mechanism text that a build-phase task can carry.", blocking: false }
  escalations: []
  sc_status: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1286-test-tree-enforcement/.harness/harness/features/BUG-1286-test-tree-enforcement/runs/2026-09-04-30-validator/digest.md
```

## Readers — both RAN, neither skipped

| reader | persona | status | verdict | findings |
|---|---|---|---|---|
| `should-not-exist` | `fable-advisor` | **ran** | PASS (lead-mapped; the reader carries no VERDICT of its own — max severity low) | 3 (low, low, info) |
| `scope` | `harness-code-reviewer` | **ran** | PASS (its own) | 2 (med, info) |

`fable-advisor` resolved and ran; no skip entry is due. It holds no write grant, so its findings are
transcribed here from its return. `scope`'s artifact is verified present and complete at
`notes/review-harness-code-reviewer-planpanel-c10.md`; its job exited 1 on the Q1 validator defect,
**not** on its work, and its VERDICT block is legible, complete and self-consistent across both copies.

## The advisor consultation — both answers, cross-referenced, uncollapsed

**(a) Per-pattern unbuildability under the operator's LITERAL ruling — CONFIRMED by both, independently. 3/3 do not certify.**

| pattern | `should-not-exist` | `scope` |
|---|---|---|
| `**/*.test.*` | NO — ends in `*`, maximal fixed suffix is empty | NO — no literal suffix |
| `**/*_test.*` | NO — ends in `*`, maximal fixed suffix is empty | NO — no literal suffix |
| `**/test_*.py` | NO — suffix `.py`; `gen.py`/`conftest.py`/`helper.py` refused nowhere | NO — `.py` alone refused nowhere |

**This is the panel's firmest result and it is what makes the divergence legitimate rather than
convenient.** The falsification evidence: `should-not-exist` ran a CONTROL — `**/*_test.py` **does**
certify under the literal ruling (suffix `_test.py` universally refused). The three NOs are therefore
a property of today's patterns, not an artifact of a simulator that says NO to everything. No finding.

**(b) Faithfulness — both say FAITHFUL, and both name the same single exception.** Force is carried by
(a) core-has-no-slash and (c) fixed-literal key; `should-not-exist` derived both keys sound analytically
(agnostic: any basename matching carries the literal, refused at any extension; restricted: prefix at 0
plus a wildcard-free terminal region ending in a source extension forces `splitext` into
`SOURCE_EXTENSIONS`). The exception is (b)'s *contains-a-wildcard* conjunct — finding F-1 below.

**(c) Attack — NO UNDISCLOSED SURVIVOR, from both, by different instruments.** `should-not-exist`:
3,423 fuzzed (a)(b)(c)-passing cores × 33,731 basenames, plus hand-built adversaries (unclosed brackets,
`[x]`-class smuggling, `?`-crossing, `.spy`/`.pyc`/`..py`/`.PY` endswith ambiguity) → **0 basename-level
escapes**. `scope`: a 220-core generative sweep plus an algebraic soundness argument per key. **Both
converged on the same structural conclusion: every constructible escape routes through the disclosed
wildcard-crosses-`/` mechanism.** Two independent analytic derivations reaching the same closure is
much stronger than two fuzz runs agreeing, and it is why an empty result here is credible.

**(d) The strike — SOUND, from both, each re-measuring rather than reading the c9 note's numbers**
(4/4 red cases still fail, 7/7 patterns certify, 4/4 previously over-refused shapes now certify).
`should-not-exist` goes further: over 3,423 (c)-passing cores, **(d) never fails when (c) passes**, so
the struck conjunct's absence cannot open a refusal hole. On evidence adequacy both accept it as
adequate *for a plan-phase gate* precisely because T-01 mandates re-proving the four red cases against
the built artifact — see adequacy note 1.

## Findings — 5 rows, 3 distinct defects, at each reader's own severity

De-duplication is on normalised summary **plus reader id**, so a defect both readers found stays two
rows. No severity is reassigned, averaged or normalised. No PF- ids assigned — `pm` computes identity
once at transcription.

| # | reader | sev | summary | consequence |
|---|---|---|---|---|
| F-1a | `scope` | **med** | Condition (b) NON-DEGENERATE requires a wildcard in core, unmotivated by and contrary to the fixed-slash-free-literal-text insight — a fully-literal core is classified as neither category and trips fail-closed | No live pattern hits it today (all 3 unit cores carry `*`); a future literal-basename detect entry would redden case 11 with **no valid remedy among the three the plan names**, since nothing is wrong with the pattern |
| F-1b | `should-not-exist` | **low** | Same conjunct, refusing fully-literal `**/` cores such as `**/test_foo.py` | Fail-closed keeps it safe; the showcase-vs-rule contradiction costs a confused maintenance cycle. One-clause fix: note in the mechanism text that literal cores are deliberately routed to the fail-closed remedy |
| F-2a | `should-not-exist` | **low** | BRIEF's "One residual is DISCLOSED" bullet exemplifies the directory-component residual with `**/test_*.py` alone, while all three `**/` patterns carry live instances | An operator reading the **signing surface** could sign believing a narrowing of detect retires the residual when it does not — `.harness/tools/a.test.d/gen.py` and `a_test.d/gen.py` survive via `**/*.test.*` and `**/*_test.*` |
| F-2b | `scope` | **info** | Same bullet names only `test_dir/gen.py` ("a path such as") though the mechanism fires identically for the other two | None — SC-19's corpus-spanning language and T-01's intent already name and measure all three; one prose bullet gives one example |
| F-3 | `should-not-exist` | **info** | Post-strike (d) is provably entailed by (c) for refusal power, and its real load-bearing role — coupling (c)'s hardcoded key text to the IMPORTED `is_test_shaped` against vocabulary drift — is stated nowhere | A future simplify pass can delete (d) citing the plan's own disclaimer, severing the only in-case link between the re-spelled keys and the live vocabulary. Bounded (cases 8/10 and the behavioural half still catch drift), hence info |

**F-1a/F-1b and F-2a/F-2b are each ONE edit, not two.** F-2's remedy should take
`should-not-exist`'s formulation — it names the consequence at the surface the operator actually reads.

## Lead adjudications — what neither reader was positioned to decide

**1. The F-1 aggravator is FALSE, and I re-measured it at source. The defect survives; its severity
argument is weaker than both readers state.** Both rest part of their case on (b) contradicting the
plan's own showcase. It does not, in live text: the **live** withdrawal paragraph
(`plan.yaml:684-687`) cites **`**/*_test.py`**, whose core `*_test.py` clears (a) no slash, (b) carries
`*`, (c) agnostic key `_test.` — **it certifies.** The non-certifying witness `**/test_foo.py` occurs
at `plan.yaml:297-298`, inside the **frozen `panel:` cycle-8 audit block**, a preserved record rather
than live specification text. `should-not-exist`'s wording ("the one shape the plan's own withdrawal
paragraph showcases") is inaccurate; `scope`'s line citation is accurate but mis-weights a frozen
record as live spec. **The (b) over-refusal itself is real and correctly described by both** — I
confirmed the conjunct at `plan.yaml:664` — but "self-contradiction at the signing surface" is not an
available aggravator. Both severities carried unchanged, as they must be.

**2. The readers appear to contradict on (d)'s independence; they do not, and it is decidable from
their artifacts.** `scope` calls (d) "dormant defense-in-depth, not decoration — it still fires for
`**/test_*.p?`". `should-not-exist` measured 0 of 3,423 (c)-passing cores where (d) fails. Both are
true: (d) *does* fire on `**/test_*.p?` and `**/*.spec.*`, but **both also fail (c)**, so (d) has no
independent refusal power over anything (c) admits. `should-not-exist`'s framing is the precise one,
and the plan's own text already says exactly this. Resolved here; no escalation.

**3. The med/low and low/info splits are immaterial to routing, which is why no cycle need be spent on
them.** `gates.review` in `harness.json` is `advisory_unless_high`. Neither `med` nor `low` gates, so
the gate result is identical under either reading. At 9 of 10 cycles that is the load-bearing fact.

**4. Honest record — my own dispatch carried the error F-2 describes.** I briefed both readers that
`**/test_*.py` was "the ONE known residual". `should-not-exist` caught it and cited it as field
evidence of the misreading its finding predicts. Recording it because it strengthens their finding
rather than my dispatch.

## The gate

`must_fix` is **empty**. `severity_max` is **med**. **NO finding is high, critical or unrated.** The
panel gate (`must_fix` non-empty **or** `severity_max >= high`) is **not tripped** → **PASS**, and
`gates.review: advisory_unless_high` agrees. Under DEC-176 these three findings enter the operator's
one batched signature review, not a pre-signature fix dispatch.

## Should any of this not be built at all

**KEEP, from both readers, explicitly.** `should-not-exist` — the reader whose standing question this
is: *"NOTHING. Five panels of accretion bought a falsification-surviving matcher correction, a
certification rule this reader could not break, three deleted config pins, and a disclosed residual
with a named carrier. Both warts found are prose-grade; neither warrants a cycle 11."* `scope` —
*"Nothing here argues for not building this."* The recurrence watch is **clean**: both readers checked
T-01, D-01, SC-19 and `## Verification gaps` and found **no fourth live-config pin** under any name;
`plan.yaml:733-743` is the deletion, and the surviving `panel:` mentions are the inert cycle-8 record.
The fail-closed clause is a **general rule with no fall-through** — `scope` traced seven edge shapes
(no `**/` prefix, empty core, pure-wildcard core, `|`, leading `/`, the `..` substitution) and every
one lands classified or red-by-name; `should-not-exist` confirmed the partition is asserted over
`_patterns()` output, the exact tokenizer `_is_test_path` uses, so certified set equals matched set by
construction. `scope`'s breakage sweep over SC-06, T-03/T-04, the SC-to-AC table, 9 REQ ids, the
`depends_on` DAG and every `verify:` found **no orphan REQ, no phantom trace, a valid topological
order, and no verify asserting a phrase a sibling deletes.**
