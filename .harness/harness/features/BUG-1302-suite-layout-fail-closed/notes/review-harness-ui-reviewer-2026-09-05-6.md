# UI Review — BUG-1302 — pin ac8dd671 — Mode B (CI text legibility)

## BLUF
No graphical surface exists (0 UI-extension hits across the diff — n/a for that lens by measurement,
not prediction). The task hands me an adjacent surface instead: the human-read PASS/FAIL text a CI
reader sees. I read every new `check(...)` call site and its docstring in
`tests/unit/test-suite-layout.py` at the pin, plus the widened assertion in
`tests/integration/test-run-unit-tests-layout.py`. **PASS**, with two LOW advisory findings (naming
ambiguity on b4/b5, and a naming-convention split); nothing rises to a gate.

## B-6 message — the centrepiece (`test-suite-layout.py:641-644` region, case 11 no-candidate branch)
Literal FAIL line when it fires:
`FAIL case 11 behavioural: positive control offender is detected no CANDIDATE_CORPUS entry is
counted-but-unrefused under the live test_kinds config -- either extend CANDIDATE_CORPUS with a shape
the new config counts, or treat the config change as a detection regression`
- **(a) what went wrong** — stated: no corpus entry currently exercises the counted-but-unrefused
  path. Legible to anyone who has the file open (`CANDIDATE_CORPUS` is a module-level tuple defined a
  few lines above the branch that prints this).
- **(b) two causes flagged** — yes, explicit `either / or`.
- **(c) actionable per branch** — remedy 1 names the exact identifier to edit
  (`CANDIDATE_CORPUS`) and the exact criterion ("a shape the new config counts") — concrete, no
  BRIEF.md round-trip needed. Remedy 2 ("treat the config change as a detection regression") is
  correctly a judgement pointer rather than a mechanical step, because which of the two applies is
  itself a judgement call — that asymmetry is appropriate, not a gap.
- The file self-verifies this exact wording never regresses: `b6 message: the no-candidate failure
  names both remedies` ASTs the branch and greps the printed detail for `"extend CANDIDATE_CORPUS"`
  and `"detection regression"` (`:680-684`). A future edit that waters the message down to one remedy
  or vague prose fails this check by itself — a good design for keeping a fail-closed message
  fail-closed.
- Verdict: **legible, no defect.**

## The other new FAIL names
|name (literal)|fires on|accuracy of the name vs. actual trigger|
|---|---|---|
|`b4 structural: the tautological conjunct is absent` (`:534`)|`b4_any_count != 1 or b4_wildcard_count != 1` (AST census of `_literal_key_present`)|**Misdescribes one real trigger.** The name reads as "the bug came back." It equally fires when a legitimate future refactor changes the `any()`/`"*?["` shape for an unrelated reason — exactly the residual risk BRIEF.md § Residual risk already records verbatim (naming this literal check text). Confirmed no such misdescription risk exists for the pre-existing 26 `case N: ...` checks in the base file (`git show 54f01854` has zero `bN`-style names) — this is a genuinely new naming shape.|
|`b5 structural: no unreachable dotdot comparison` (`:483`)|`b5_dotdot_count != 1` (AST census of `_is_inside_tests`)|Same class of ambiguity as b4, same BRIEF.md acknowledgement.|
|`b14: unreadable tracked sources are reported, not raised` (`:701`/`:704`)|either `_violations_callers` raised (except branch, detail = `f"{type(error).__name__}: {error}"` — shows the real exception, immediately falsifying the "not raised" half) or the returned list is missing one/both of the two expected named entries (else branch, detail = `repr(unreadable_callers)` — shows exactly what *was* reported so the gap is visible by omission)|**Accurate.** Both failure shapes it can produce are legible straight from the printed detail; no ambiguity comparable to b4/b5, because this checks a behavioral invariant (raise-or-not, entry-named-or-not) rather than an incidental AST shape count.|

**Severity of the b4/b5 gap:** LOW, not blocking. It is a real send-back-worthy wording gap, but (1)
BRIEF.md already names it, accepts it, and assigns its remedy path (re-derive the pin, main-session
fixture maintenance) — this is a documented, owned residual risk, not an unnoticed one; (2) the printed
detail carries the actual counts, so a careful reader is not stuck — only a rushed one is misrouted.

**Precise send-back (do not apply — DEC-174):** in `tests/unit/test-suite-layout.py`,
`_literal_key_present`'s `check(...)` at `:534-536`, change the detail f-string from
`f"any calls={b4_any_count}, wildcard constants={b4_wildcard_count}"` to something that states the
expected shape and both possible causes, e.g. `f"expected any-calls=1 wildcard-constants=1; got any
calls={b4_any_count}, wildcard constants={b4_wildcard_count} -- either the tautological conjunct was
reintroduced, or _literal_key_present was legitimately refactored and this census pin needs updating"`.
Mirror the same shape in `_is_inside_tests`'s `check(...)` at `:483-484` for the dotdot count. This is
the "cheap wording change" the dispatch asked me to judge — it exists and costs one line each; I am
not the one who may apply it.

## B-8 (`tests/integration/test-run-unit-tests-layout.py:90`)
This is **not a new FAIL name** — the check name stays `"git tracked rogue refused before sentinels"`
(unchanged), and the printed detail on failure is the full `p.stdout + p.stderr` blob (the real runner
output including any `MISCONFIGURED:` lines), also unchanged. The diff only widens the discriminating
substring from `"PASS test-unit.py"` to `"PASS test-"` inside the boolean condition — it makes the
check fire on any sentinel prefix, not just `test-unit.py`. No legibility question applies: nothing
human-readable changed, only what the assertion is willing to tolerate. No defect.

## Consistency with surrounding conventions
- **Naming scheme split.** The base file's 26 pre-existing checks and this diff's non-`bN` new checks
  use `"case N: <prose>"` or plain descriptive prose. This diff introduces four checks
  (`b4 …`, `b4 …`, `b5 …`, `b5 …`, `b6 …`, `b6 …`, `b14: …`) that instead key off the BRIEF.md task ID.
  Traceability to BRIEF.md is a genuine benefit; the mixed convention within one file is a minor,
  non-blocking style note — each name is still individually legible, so nothing misroutes.
- **Detail-string convention.** Every other `check()` in the file passes `repr(...)` of computed data
  or an f-string of counts as detail; B-6 alone passes hand-authored prose. That is a deliberate,
  singular exception matching B-6's stated special status (the fail-closed centrepiece) — appropriate,
  not an inconsistency to flag.
- **Path rendering.** The new `unreadable tracked source <path>: <ErrorType>` format
  (`_violations_callers` docstring, `:161-166`, and call site `:180`) matches the file's existing
  `"tracked test-shaped file outside tests/: <path>"` convention already in use elsewhere in the file —
  consistent.
- **Truncation/interleaving.** All these checks execute serially in a single-process top-to-bottom
  script (`check()` is a plain synchronous `print()`); no concurrent producers, so P-10-style
  attribution risk does not apply. Any truncation a reader might see is a property of whatever log
  viewer captures this script's stdout, outside this diff's control — not a defect in the message
  design itself.

## Accessibility / theme parity
Explicitly not applicable (G-02): this is plain CI stdout text, colour-only state encoding and dark/
light theme parity have no surface to attach to. Stated, not omitted.

## Verdict
`severity_max: low`. Two advisory findings (b4/b5 FAIL-name ambiguity, naming-convention split), zero
`must_fix`. Neither meets the gate bar in this role's rule (`must_fix` non-empty or
`severity_max >= high`).
