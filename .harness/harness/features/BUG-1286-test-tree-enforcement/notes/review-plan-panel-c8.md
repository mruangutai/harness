# Plan panel cycle 8 — BUG-1286-test-tree-enforcement

**BLUF: PASS, advisory. No `must_fix`, `severity_max: med`, nothing high, critical or unrated.**
Both readers ran and both probed by measurement rather than argument. The consultation is answered
three ways: **(a) pm's impossibility claim is FALSE as stated** — both readers independently exhibited
a counterexample — **(b) the substitution is SOUND**, and **(c) one concrete escaping class exists**,
found by `should-not-exist` alone. Four findings survive, all `med` or `low`, and **all four are
remediable in ONE edit to two sites** (T-01 case 11 + SC-19). The panel does not gate the plan.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Plan panel c8 PASS advisory — pm's impossibility claim is false as stated but the substitution is sound; one real escaping class (extension-position wildcards) and a contested bucket clause, all med, all fixable in one edit to T-01 case 11 + SC-19."
  team: plan-panel
  steps_run: 2
  cycles_used: 0
  severity_max: med
  members:
    - { step: should-not-exist, persona: fable-advisor, verdict: PASS, headline: "KEEP on the new machinery except the bucket clause; found one undisclosed escaping class (extension-position wildcard cores) and falsified the impossibility claim by fnmatch.translate closure plus a 280-path fuzz.", files_touched: [] }
    - { step: scope, persona: harness-code-reviewer, verdict: PASS, headline: "Spec review clean — no orphan REQ, valid topological DAG, blast-radius disclosure verified complete against live harness.json and git ls-files; one LOW note on the overstated impossibility sentence.", files_touched: [".harness/harness/features/BUG-1286-test-tree-enforcement/notes/review-harness-code-reviewer-planpanel-c8.md"] }
  must_fix: []
  files_touched: [".harness/harness/features/BUG-1286-test-tree-enforcement/notes/review-harness-code-reviewer-planpanel-c8.md"]
  branch: none
  open_questions:
    - { id: Q1, question: "Harness defect, not a plan defect: the `scope` step's process settled `failed (exit 1)` while emitting a contract-shaped VERDICT: PASS digest and writing its artifact. I verified the artifact exists and is substantive, so I treated the return as valid rather than firing `on_fail`. If the host exit code is ever routed on, a clean reviewer return would be misrouted as a failure.", blocking: false }
    - { id: Q2, question: "The two readers CONTRADICT on whether the `guard-covered bucket must be non-empty` clause earns its place. I resolved it in should-not-exist's favour on evidence grounds (it simulated the config; scope reasoned about it) and carry both ratings unreassigned. The operator may prefer to overrule that resolution — it is the third cycle running that a clause pinning the live config's shape has been flagged.", blocking: false }
  escalations: []
  expertise_update: []
  sc_status: []
  adequacy_notes:
    - "NEITHER reader could exercise the real guard: no code exists. Every 'case 11 is green/red under X' claim in this panel is a simulation of a SPECIFICATION, hand-executed from the plan's prose. The panel cannot tell you the built artifact behaves this way — only that the spec, read literally and simulated faithfully, does."
    - "The hygiene half's sufficient condition is CORPUS-SAMPLED, and neither reader established the completeness of that sample. Two leaks are now known — the directory-component axis (disclosed) and the extension-position axis (SNE-1, undisclosed) — and BOTH were found by picking an axis by hand. Nobody enumerated the axis space, so a third leak is not excluded. This is the panel's largest residual and no individual reader is positioned to state it."
    - "scope's (c) 'NONE FOUND' is credible only along the axis it searched. It probed the directory-component escape across all three wildcard-bearing patterns and stopped; it never varied the extension position. That is a narrower search, NOT a refutation of SNE-1, and I did not treat it as one."
    - "The consultation's (b) answer rests on a claim about enforcement MODE that both readers reached independently and that the plan states correctly but quietly: for the residual class the guarantee is 'the unit suite reddens on the next run', never REQ-01's 'refused before any test executes'. Disclosed, not misrepresented — but it is the sentence most likely to be misread by whoever builds this."
artifact: .harness/harness/features/BUG-1286-test-tree-enforcement/runs/2026-09-04-25-validator/digest.md
```

## Readers

|Reader|Persona|Status|Artifact|
|---|---|---|---|
|`should-not-exist`|`fable-advisor`|**ran**|no write grant — findings transcribed here from its return|
|`scope`|`harness-code-reviewer`|**ran**|`notes/review-harness-code-reviewer-planpanel-c8.md` (verified present)|

Neither reader was skipped. `fable-advisor` resolved and ran on this host. `should-not-exist` returns
findings only and carries no VERDICT of its own; I mapped its row to `PASS` because its maximum
severity is `med` and the gate is `must_fix` non-empty or `severity_max >= high`. That mapping is mine,
not a claim the reader made.

## The advisor consultation — both answers, cross-referenced, not collapsed

### (a) Is pm's impossibility claim true as stated?

**Both readers say NO, independently, each with a live probe. This is the panel's firmest result.**

|Reader|Answer|Evidence it ran|
|---|---|---|
|`scope`|FALSE as stated; true for every pattern actually in play|`**/test_foo.py` — `**/`-prefixed, matches only paths whose basename is the fixed literal `test_foo.py`, which `is_test_shaped` always accepts. Zero escaping paths|
|`should-not-exist`|FALSE as stated; the buildability conclusion survives|`fnmatch.translate("**/*_test.py")` = `(?s:(?>.*?/).*_test\.py)\z` — every match must END with `_test.py`, a suffix containing no `/`, so it survives into the basename and is refused. Confirmed with `**/test_foo.py`, `**/*_test.py`, `**/*.test.py`, each **0** escapes over a 280-path adversarial corpus|

**Where they differ, and it matters for the remedy.** `scope` states the rule as *"pm's argument only
holds for a pattern that carries a wildcard after the leading `**/`"*. That rule is itself wrong, and
`should-not-exist` has the correct one: `**/*_test.py` **does** carry a wildcard after the `**/` and
still satisfies the universal form, because what closes the escape is a **fixed literal suffix
containing no `/`**, not the absence of a wildcard. Whoever rewords SC-19 and D-01 must take
`should-not-exist`'s formulation; taking `scope`'s would replace one false sentence with another.

**The conclusion the operator asked for:** the *substitution decision* is correct and was forced —
all three of today's repo-wide `unit` patterns violate the universal (`**/*.test.*` and `**/*_test.*`
at 32 escapes each in the corpus, `**/test_*.py` at 4), so a hygiene half asserting the universal
directly would be red on the unmutated config and could never be green. **Only the stated REASON is
wrong.** It is a claim about *this pattern set*, not about all `**/`-prefixed shapes.

### (b) Is the substitution sound?

**Both readers: YES.** `scope` adds that the behavioural half re-derives `tracked_paths(ROOT)` at
*test-run time*, so it is not blind to a future commit — the objection in the dispatch ("sees nothing
about a path that does not yet exist") is answered: it sees the path the moment it is committed.
`should-not-exist` bounds the window from the other side — the residual cannot manifest in scope
without a commit to harness's own index (product checkouts excluded by REQ-08/SC-16/DEC-189, untracked
files outside the tracked invariant), and `tests.yml:20-22,86` runs the unit kind on every
`pull_request` and `main` push.

Both independently flag the same precision point: what carries the residual is **case 11's own
assertion**, not `suite_layout.violations()`. `is_test_shaped` is basename-only by construction and
structurally can never flag `.harness/tools/test_dir/gen.py`. So REQ-09's "refused by the guard" holds
as *"the unit suite reddens on the next run"* and not as REQ-01's *"refused before any test executes"*.
The plan says "reddens the unit suite" at both sites and is therefore honest — this is a clarity
exposure, not a defect, and neither reader raised it as a finding.

`should-not-exist` additionally probed the control's INAPPLICABLE seam and could not defeat it: every
config it built that could reach a real offender either still counted a candidate (`**/test_*.p?`
selects `.harness/tools/test_dir/gen.py`, since `.p?` matches `.py`) or failed hygiene's corpus-hit
requirement and went RED. The single exception is a dead `_is_test_path` returning False everywhere —
green with the control INAPPLICABLE, but then nothing is counted anywhere and REQ-09 holds vacuously
and *honestly*. That defect belongs to `code_grade`, not to this feature. `scope` reached the same
place by a different route: an over-matching `is_test_shaped` would be caught on a different
assertion, T-01 case 1's exact-equality list under SC-06.

**The re-based positive control survives both probes.** Both readers reproduced the legitimate
narrowing mechanically: dropping `**/test_*.py` re-selects the next family and stays GREEN.

### (c) Does a class escape both halves?

**The readers DIVERGE, and this is the panel's finding.**

- `scope`: **NONE FOUND** — it verified the directory-component escape afflicts all three
  wildcard-bearing patterns, then confirmed T-01 case 11's control corpus already spans all three
  shapes, so it is not a new gap.
- `should-not-exist`: **YES, named concretely** — see SNE-1 below.

**My resolution: SNE-1 stands.** These are not contradictory measurements; they are searches of
different width. `scope` varied the *directory* position and found the disclosed residual. It never
varied the *extension* position, which is where `should-not-exist` found the leak. A "none found" from
a search that did not cover the region is not evidence of absence there, and I did not let it cancel a
positive result. `scope`'s work stands as correct within its own scope.

## Findings — every reader's own severity, never reassigned

Ranked by what the project does next. No PF- ids assigned; pm computes identity at transcription.

|#|Reader|Sev|Summary (reader's own words, condensed to one line)|Concrete consequence|
|---|---|---|---|---|
|**SNE-1**|`should-not-exist`|**med**|The hygiene half's corpus-sampled condition certifies extension-wildcard cores (`**/test_*.p?`, `**/test_*.p*`, `**/test_*.[ps]y`, `**/probe-*.p?`) as guard-covered while under `fnmatch` they count basename-level paths the extension policy never refuses|Simulated case 11 exactly as specified passes ALL halves under `unit.detect += "\|**/test_*.p?"` while the matcher newly counts `.harness/test_evil.pw` — stem restricted, extension `.pw` outside SOURCE_EXTENSIONS, refused nowhere, **no directory component involved**. REQ-09 promises a widening edit "fails loudly rather than reopening the gap in silence"; for this edit class that promise is false until a tracked instance lands|
|**SNE-2**|`should-not-exist`|**med**|The `guard-covered bucket must be non-empty` clause is a live-config occupancy pin, not an invariant|`unit.detect := tests/unit/**` alone — with other running kinds' patterns inside-tests literals — leaves hygiene ok, bucket EMPTY, control INAPPLICABLE, case RED, **with no uncertified pattern to fix and no vocabulary to widen**. That end state is the *ideal* fulfilment of DEC-213's directory-is-the-kind rule, so the maintainer doing the right thing is trained to edit an assertion marked NEVER-weaken. The trained-to-delete channel F-03/F-04 closed, rebuilt one notch weaker (`>=1` instead of `==1`)|
|**SNE-3**|`should-not-exist`|**low**|The impossibility claim justifying the substitution is overstated at BOTH sites (SC-19 and T-01 case 11): "no `**/`-prefixed fnmatch pattern satisfies that property" is false|Falsifiable at review time by any inspector who tries one pattern — a manufactured spec-vs-fact dispute of exactly the kind cycle 6 flagged in SC-12 — and a future amender who trusts it will wrongly rule out fixed-suffix patterns as necessarily leaky|
|**SCO-1**|`scope`|**low**|Same defect as SNE-3, from the code side: the impossibility sentence in D-01's `because` (`plan.yaml` ~88) and SC-19's HYGIENE paragraph (`BRIEF.md` ~190) is technically overbroad|Zero operational consequence today — none of the four running kinds' `detect` values are of the exempted shape, and the plan's own hygiene rule classifies such a pattern UNCERTIFIED (fail-closed, not fail-open). A justification overstatement, not a coverage gap|

**De-duplication.** SNE-3 and SCO-1 are ONE defect reported by both readers at `low` and `low` — I keep
them as separate rows because de-duplication is on normalised summary **plus reader id**, and both
ratings and both wordings are the record. They are one edit, not two. SNE-1 and SNE-2 are distinct
defects with distinct remedies and are not merged with anything.

**Contested — both ratings carried, NOT averaged.** SNE-2 is the one place the readers directly
contradict. `scope` assessed the same clause and concluded it **earns its place**: *"Not a hardcoded
value pin — it asserts non-emptiness only... without pinning which or how many patterns land there.
Replaces a cardinality pin with a coverage-sanity check, correctly per F-03/F-04."* I resolved this in
`should-not-exist`'s favour and record why: **it simulated the narrowing config and `scope` did not.**
`scope`'s true half — non-emptiness is strictly weaker than cardinality — is preserved and is correct;
its *conclusion* is not established, because the config that reds the clause was never tested against
it. A demonstrated red beats an untested "earns its place". The severity stays `med`, exactly as
`should-not-exist` stated it, and `scope`'s dissent travels up unedited.

## Assessed and dismissed, with reasons

|Item|Why it is not carried as a finding|
|---|---|
|REQ-09's "refused by the guard" reads as REQ-01's pre-execution refusal|Both readers checked and both found the plan says "reddens the unit suite" at both sites. Accurately disclosed. A clarity exposure for the builder, not a defect — neither reader raised it as a finding and I do not manufacture one|
|Dead `_is_test_path` makes case 11 green with the control INAPPLICABLE|Real, but the failure is `code_grade`'s and nothing is counted anywhere, so REQ-09 holds vacuously **and honestly**. Out of this feature's scope; not routed as a finding|
|Blast-radius disclosure incomplete|**Falsified by independent re-derivation from both sides.** `component` → exactly 3 uncertified (`**/*.spec.tsx`, `**/*.stories.tsx`, `**/*.stories.ts`), `ui` → 2 (`tests/e2e/**` certifies inside-tests, leaving `e2e/**` and `**/*.e2e.spec.ts`), `typecheck` → 2 (`**/*.ts`, `**/*.tsx`). `git ls-files` on `\.tsx?$` returns exactly three tracked files: one inside `tests/`, plus the two BRIEF already names. **No third file exists that BRIEF failed to count.** Disclosure accurate and complete|
|Blast-radius disclosure is the wrong response / leaves DEC-163 blocked with no route|Both readers rejected this. T-05 states the remedy explicitly (widen the vocabulary or record the scope in DEC-213); for `typecheck` the DEC-213 route is the only buildable one, since widening the vocabulary to refuse `*.ts` everywhere is absurd. **Blocked-with-a-route, not blocked-with-no-route** — the future dev-ops engineer meets a documented cost, not a mystery red|
|Unit-only phrasing surviving where the union is meant|**Falsified.** `scope` grepped every `unit.detect` / "unit kind" occurrence: three of four hits are the historical Problem statement (`BRIEF.md:12`, correctly describing the original bug), the superseded `panel:` block (out of scope), and a worked illustrative mutation naming `unit.detect` as *one instance* (`plan.yaml:645`) — with the governing rule at `plan.yaml:529-530` explicitly saying "Do NOT scope this case to the unit kind". D-01, REQ-09, SC-19, T-05 consistent|
|Amendment breakage against earlier text|**Falsified item by item.** SC-06's one-element exact-equality list (`BRIEF.md:88-103`) matches T-01 case 1's fixture verbatim; T-03's `TOTAL 85 / OUTSIDE 9 / VIOLATIONS 0` matches BRIEF's closing bullet; SC-12/T-03/T-04 quote the two refusal messages identically at all three sites|
|Orphan REQ / dangling trace / non-topological DAG|**Falsified.** All 9 REQs traced from at least one task; no task cites a nonexistent REQ. `T-01:[]`, `T-02:[T-01]`, `T-03:[T-01]`, `T-04:[T-03]`, `T-05:[T-01,T-02]` is a valid topological order with no cycle, and nothing `verify:`s something a predecessor deletes — every change is additive|
|F-01's fix present but inert|**Falsified.** The `..`-rejection-then-normalize text is present in case 11's HYGIENE section and `scope` traced it by hand against `tests/../evil/**`: the `..` segment is rejected outright regardless of normalization, and separately the core still contains `/` so it also fails GUARD-COVERED. Uncertified either way — present **and** correct|
|Case 11 / the new machinery should not be built|**KEEP, and it is a real verdict, not a default.** `should-not-exist` reports the two-half split, derived control, candidate corpus and INAPPLICABLE branch **interlock** — hygiene's corpus-hit requirement backstops the control's corpus misses — and it could not defeat the interlock except through the two residuals it reported. The maintenance surface earns its weight. The one piece failing the earn test is SNE-2|

An empty-or-small findings list is credible here **because both readers produced falsification
evidence, not assurances**: `scope` reproduced `tracked=2706`, `counted-outside-tests/=0` and the
running-kind set `{handoff_comprehension, integration, omp_session_accessor, unit}` from its own probe
at `cab6adb2`, the exact cited commit; `should-not-exist` ran a 280-path adversarial fuzz and a full
hand-simulation of case 11. Each named what would have shown a defect and reported what it returned.

## Ordering the fixes — the one thing no reader could see

**All four findings land in the same two sites: T-01 case 11 and SC-19.** They must be applied as ONE
edit, in this order, because two of the remedies interact:

1. **SNE-3/SCO-1 first** — reword the impossibility claim, using `should-not-exist`'s formulation (a
   fixed literal suffix containing no `/` is what closes the escape), **not** `scope`'s. Doing this
   second would mean rewording text that step 2 has already rewritten.
2. **SNE-1** — add extension-poison basenames (`test_x.pw`, `probe-x.pw`, `test-x.pw`) to the hygiene
   corpus, and disclose the extension-position class beside the directory-component residual bullet so
   the sufficient condition's known leaks are **enumerated** rather than implied to be one. This is the
   same paragraph step 1 touches.
3. **SNE-2** — if accepted, replace the bucket clause with `should-not-exist`'s fixed-literal self-test
   of the certifier (`tests/unit/**` → inside-tests, `**/*_test.*` → guard-covered, `**/test_*/**` →
   neither). It catches BOTH degeneracy directions, including the everything-guard-covered direction the
   bucket clause misses, while pinning nothing about the live config.

None of these remedies touches an operator-ruled item: they add corpus entries and reword
justifications. They do not narrow REQ-09, do not touch D-01's vocabulary, do not touch D-05, and do not
delete or weaken case 11.

## The gate

`must_fix` is empty and `severity_max` is `med`. Nothing is `high`, `critical` or `unrated`.
By the panel gate — `must_fix` non-empty **or** `severity_max >= high` → FAIL — this is **PASS with
notes**, logged and surfaced, not blocking. `gates.review` in `.harness/harness.json` is
`advisory_unless_high`, which agrees. Both approvals remain `pending`; this panel does not sign
anything, and `plan.yaml`'s `panel:` block still holds the superseded cycle-6 record for pm to replace.
