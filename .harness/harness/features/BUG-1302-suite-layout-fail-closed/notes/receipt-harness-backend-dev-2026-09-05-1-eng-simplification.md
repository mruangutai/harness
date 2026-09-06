## SIMPLIFICATION angle — BUG-1302-suite-layout-fail-closed plan draft (read-only)

BLUF: two genuine, low-severity backlog-worthy simplifications found — one corpus over-specification
in B5_CORPUS (2 of 15 pairs are branch-redundant with an existing pair and go beyond what SC-03
names) and one drift-risk in the 9-way restatement of DEC-174's routing rationale. Everything else
asked about (B-4/B-5 pairing, the AST-check shapes, B4_CORPUS, the "demonstrate the red" repetition,
and dead references) is CLEAN — forced by the requirement text, genuinely non-redundant, or already
protected by an explicit in-plan mandate. No finding recommends deleting or weakening an assertion;
the two corpus entries are named as backlog candidates only, per the skill's own carve-out that
naming an over-specified corpus is legitimate while shrinking it is the PM's call.

### Item 1 — B-4/B-5 paired criteria (SC-01/SC-02, SC-03/SC-04): CLEAN
Both halves are forced, not extra: REQ-01/REQ-02 each state two independent clauses in one sentence
— "no longer contains" (structural) and "verdict...unchanged" (behavioural) — so SC-02/SC-04 are not
an invented commitment beyond the requirement, they restate its own second clause.
Traced both removed fragments (`test-suite-layout.py:433` dotdot disjunct, `:448` tautological
conjunct) against their actual behaviour: both are dead/inert code (the dotdot disjunct is
unreachable behind the earlier `if ".." in segments` guard at `:424`; the conjunct is tautologically
True because `trailing` is defined as the span *after* the last wildcard, so it contains none by
construction). Consequence: reintroducing either fragment changes **no** corpus verdict at all — only
the structural (AST-count) half would redden. The behavioural half is what proves "verdict unchanged"
(REQ text); the structural half is the *only* one that can catch regression of "no longer contains."
Non-redundant. Recommend: keep both pairs as specified.

### Item 2 — the three AST walks (T-01, T-02, T-03): FINDING (low)
Read `_is_inside_tests`/`_literal_key_present` (test-suite-layout.py:422-451) and case 11's if/else
(:553-560, confirmed **module-level**, not inside a FunctionDef). T-01 and T-02 are the *same*
operation — locate a named `FunctionDef`, `ast.walk` it, count nodes matching one predicate — used
once by T-01 and twice by T-02. T-03 is genuinely different: it locates a module-level `ast.If` by
its test condition and concatenates string constants from its `orelse` body; this shape cannot share
the FunctionDef-counting helper without contorting it.
Cost: two ~6-line "parse file, `Path(__file__).read_text()`, locate `FunctionDef` by name, walk,
count" scaffolds duplicated verbatim between T-01 and T-02; a fix to one (e.g. switching `ast.walk`
to a body-only iteration) is not guaranteed to land in the other since they are independent plan
tasks landing in sequence.
Recommended change: T-01's intent (which already introduces the `ast` import) should also define
`_count_ast_nodes(func_def: ast.FunctionDef, predicate: Callable[[ast.AST], bool]) -> int` returning
`sum(1 for n in ast.walk(func_def) if predicate(n))`, and use it for its own dotdot-constant count;
T-02's intent should call `_count_ast_nodes` twice (once per predicate) instead of restating the
walk. T-03 stays its own walk — do not fold it in.

### Item 3 — corpus sizes: B4_CORPUS CLEAN, B5_CORPUS FINDING (low)
Traced every pair through the real function bodies (`test-suite-layout.py:422-451`).
- **B4_CORPUS (13 pairs): CLEAN.** No pair takes an identical path differing only in spelling: the
  three True entries differing by prefix (`test-`/`test_`/`probe-`) each independently exercise a
  distinct literal in the hardcoded prefix tuple (a typo in any one prefix string is caught only by
  its own entry); `x_test.*`/`x.test.*` cover the two sides of the early `or` short-circuit; every
  False entry lands on a different branch (extension mismatch, missing leading dot, no-wildcard
  literal, empty trailing, bracket-as-wildcard, no-prefix-match). Every entry earns its place.
- **B5_CORPUS (15 pairs): FINDING.** `("tests/integration/**", True)` takes the identical control
  path as `("tests/unit/**", True)` — break on the wildcard 3rd segment, `normalized` ends up
  `"tests/<dir>"`, true via the `startswith("tests/")` disjunct — differing only in subdirectory
  spelling; SC-03 (BRIEF.md:69-72) names only `tests/unit/**` as required. Likewise
  `("**/test_*.py", False)` takes the identical path as `("**/*_test.*", False)` — wildcard on the
  very first segment, immediate break, empty prefix, `not normalized` branch — differing only in the
  glob suffix; SC-03 names only `**/*_test.*`. Branch coverage is preserved by the paired entry in
  both cases, so removal is nameable per the skill's own bar. (Separately, `../x/*.py`,
  `tests/../evil/*.py` and `a/../tests/*.py` are *also* structurally identical to each other — all
  three hit the `if ".." in segments` guard before any prefix computation — but T-01's intent
  (plan.yaml:66) explicitly says these three "must not be dropped"; that is an in-plan mandate, not
  an oversight, so it is not re-flagged here.)
Recommended change (backlog, PM's call, not an apply): drop `("tests/integration/**", True)` and
`("**/test_*.py", False)` from B5_CORPUS, from 15 to 13 pairs; both dropped branches remain covered
by their paired entries named above.

### Item 4a — "demonstrate the red" repetition (5 task intents + BRIEF SC preamble): CLEAN
One authority (BRIEF.md:45-46: "each new assertion must be demonstrated failing before the fix
lands") states the policy once; each task's closing paragraph supplies the *mechanically distinct*
steps for its own mutation (T-01 restores a tuple element, T-02 restores a conjunct, T-03 demonstrates
twice — a call-site swap and a string deletion, T-04 reverts a guard, T-05 untracks a fixture file).
There is no shared wording to drift apart — the specialisation is required precisely because the five
defects are different, not an accidental restatement of the same sentence.

### Item 4b — DEC-174 routing rationale (9 restatements): FINDING (low)
Same fact — "DEC-174 makes these two test files main-session-direct" — is independently spelled out
in: `lanes.rows[0].reason` and `lanes.rows[1].reason` (plan.yaml:13,16), `D-01.choice`/`.because`
(plan.yaml:20-21), `execution_reason` on T-01..T-04 (plan.yaml:38,87,141,191, byte-identical) and T-05
(plan.yaml:241, analogous), and the BRIEF Constraints paragraph (BRIEF.md:128-134). BRIEF.md:178
itself flags that amending DEC-174's enumeration is an open operator question — if that ever happens,
up to 9 independent prose copies need editing in lockstep; missing one leaves a routing rationale
that contradicts the table it explains.
Recommended change: keep `D-01` (plan.yaml:19-22) as the single authority — it already carries
`dec: DEC-174`, the canonical pointer — and replace `lanes.rows[].reason` and each task's
`execution_reason` with a short reference (e.g. `reason: see D-01` / `execution_reason: see D-01`)
rather than restated prose. Retain the BRIEF Constraints paragraph as-is: it is operator-facing prose
for a different consumer than the plan's own machine-checked fields, which is a legitimate reason to
keep a second copy (cf. this repo's own O-08 pattern: no single mechanism spans an LLM-facing summary
and a structured plan field).

### Item 5 — dead references: CLEAN
Confirmed T-04 (the only task after T-03 touching `tests/unit/test-suite-layout.py`) never touches
case 11 or the string `INAPPLICABLE` — T-03's `! grep -q INAPPLICABLE` verify clause (plan.yaml:147)
stays valid through the rest of the sequence. Cross-checked every SC `verify:` string against the
task intent that is supposed to produce it: SC-05's `INAPPLICABLE` absence check matches T-03; SC-08's
two sentinel-grep clauses match T-05's exact replacement text; SC-10's `check-plan-routes.py` check
references the routing table directly, which nothing in this plan revises. No task or SC references a
shape a revision elsewhere removes.

### Confirmation
Wrote nothing under `tests/`. Did not touch `plan.yaml` or `BRIEF.md`. Ran no test suite, formatter,
linter, or build — all branch tracing above was done by reading source, not executing it.
