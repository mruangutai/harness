# Observations - harness-pm

- 2026-09-05: BUG-1308 — check-domain denies harness-pm any notes/ file that is not research-*.md, so a plan proposal handed to plan-merge.py must be named notes/research-<something>.md; plan-merge parses YAML regardless of the .md extension.
- 2026-09-05: BUG-1308 — plan-merge.py apply bootstrapped an absent plan.yaml and spliced approval status pending itself; the proposal carried no approval or panel key and no station, and set-feature-station wrote status afterwards.
- 2026-09-05: BUG-1308 plan goal-check — a task intent said "assert set equality, not containment" while the criterion it serves (SC-09) and a decision (D-10) make the two sets deliberately unequal; the criterion's own disjunctive wording was correct and the dispatch prose was not. Grading the intent prose against the criterion, not just against the issue, is what caught it.
- 2026-09-05: BUG-1308 — a REQ can map cleanly to an issue clause and still have zero criteria: REQ-07 carried "concurrent" from the issue body, and every SC touching it graded only add-only exit codes. Map clause->REQ and clause->SC separately; the first mapping hides the second's hole.
- 2026-09-05: BUG-1308 plan fix c1. A criterion phrased as a set predicate ("set equality") went
  unsatisfiable because the two sets were defined on different sides of a decision; the repair that
  works is to write ONE sentence and paste it verbatim into all four surfaces (SC, decision because,
  contract task intent, test case intent), then verify with a whitespace-normalised substring match
  over safe_load'ed values — line wrapping differs, wording must not.
- 2026-09-05: plan-merge.py amend on a list field needs BOTH --yaml-value and --expect-sha256, and
  --show without --yaml-value errors out telling you so; the sha shown by --yaml-value --show is the
  one it wants.
- 2026-09-05: BUG-1308 c1 re-grade — a cycle-0 "the four places must agree" finding is closed fastest by grepping the literal sentence in each place and diffing the strings, not by reading the repair note; all four carried it byte-identical. Anchor "case 8" in the integration suite is a DOCSTRING label (case_cap_drift_detector), so a grep for `def case8` returns nothing and reads as a rotted anchor when it is not.
- 2026-09-05: BUG-1308 panel c1 transcription — wrote panel findings' summary as double-quoted SINGLE-LINE scalars in the set-panel value file rather than folded '>-'; re-derived every PF- id from the LOADED plan.yaml afterwards (7/7 ID_OK), which catches a fold that reflows differently from the digest text.
- 2026-09-05: BUG-1308 c2. Narrowing a contract (section optional -> required) has a fan-out no single
  finding names: D-02, D-03, D-05, D-06, T-01 Step A/B/C, T-02 case14, T-03 intent AND the SC that
  grades each. I found the D-06 breakage (it claimed a replaced entry keeps its EXACT index, false the
  moment the same proposal drops an entry above it) only by re-reading every decision against the new
  Step D, not from the panel.
- 2026-09-05: BUG-1308 c2. Requiring a key on every op silently broke a test probe design: case17's
  ACCEPTED set probes each candidate verb with one op, and a missing-section refusal is the SAME exit
  code (12) as an unknown-verb refusal. Same-code-different-reason is how a set-difference assertion
  populates wrong and still passes. Folded the fix into T-02's intent.
- 2026-09-05: BUG-1308 c2. Ran both rewritten verify blocks against the unbuilt tree before yielding:
  T-03 exit 1 naming 'expertise-merge.py ops --file', T-04 exit 1 naming 'Chose:'. A verify that only
  greps for text the task is about to write must be shown red first or it is unfalsifiable.
- 2026-09-05: BUG-1308 panel c2 — a whole-suite `verify:` is made falsifiable cheaply by grepping each case's own `check("<id>: ` label token before running the suite, but only if the task intent MANDATES that label shape; without that sentence the grep is a token search over free-form source. `"u1: "` vs `"u11: "` disambiguates only because the colon-space is required.
- 2026-09-05: BUG-1308 panel c2 — `plan-merge.py set-panel` validates only that the value is a mapping carrying `last_run` (str), `cycle` (int), `readers` (list), `findings` (list); per-finding keys (`disposition`, `resolved_by`, extra keys like `cycle:`) are unvalidated, and it reloads the spliced file and refuses if the panel does not round-trip. Generating the value file from a script that loads the digest and the live plan keeps summaries byte-faithful and gives free ID re-derivation.
- 2026-09-05: BUG-1308 panel c2 — `check-state.sh` INV-32 expects three readers (`should-not-exist`, `scope`, `goalcheck`) but a validator-lead digest for a plan panel names only the two validator-segment readers; the goal-check runs in the product segment. Transcribing what the lead recorded leaves INV-32 unsatisfiable by pm.
- 2026-09-05: BUG-1308 panel c2 — an `edit` range for a wrapped markdown criterion must start at the FIRST line whose text changes, not at the line where my replacement prose happens to begin; I clipped SC-09 by one line and duplicated two lines of SC-12 by mis-anchoring, both visible only on re-read.
- 2026-09-05: plan-merge set-panel REPLACES the whole panel mapping from --value-file, so the safe
  route is: safe_load the plan, mutate panel in memory, safe_dump it to the value file, then
  re-load and deep-compare findings after. A hand-typed value file is where fourteen findings get
  silently dropped.
- 2026-09-05: INV-32 (check-state.sh:533) names THREE readers - should-not-exist, scope, goalcheck -
  and hard-fails any whose status is neither ran nor skipped. goalcheck runs in the product segment,
  which is why it keeps getting omitted from panel.readers; where it runs does not change that the
  invariant counts it.
- 2026-09-05: BUG-1308 c3 polish — an intent gloss cross-referencing unit cases ('u13 and u14 are their unit halves') mis-paired them; the operative case texts were right. Re-derive every id pairing from BOTH definitions, never from the gloss.
- 2026-09-05: BUG-1308 c3 — an SC/case mismatch is not automatically a criterion to narrow: T-01 pinned the refusal line shape (op index + key) and cmd_ops prints resolver lines verbatim, so widening the CLI case was the evidence-backed fix. Check whether the mechanism already supplies the clause before weakening the criterion.
- 2026-09-05: plan-merge.py amend --show prints the dedented value then a trailing 'sha256: <hex>' line that is NOT part of the value; rebuild the --value-file without it or the field grows a stray line.
- 2026-09-05: BUG-1308 renumber DEC-216->218. plan-merge.py `amend` re-emits a `>-` folded scalar as ONE long line when the value-file is one line; hand it the ORIGINAL line wrapping (the fold makes the loaded value identical) or the diff carries reflow noise on top of the digit change.
- 2026-09-05: bash-write-guard denies a redirect written against a relative path even inside /tmp; the same command with the literal absolute `/tmp/...` target is allowed. `rm -f` on absolute /tmp paths is allowed too.
- 2026-09-05: a dispatch's prescribed decision WORDING can contradict its own acceptance grep (D-16 text would have re-introduced the very `DEC-216` token criterion 1 forbids). The falsifiable gate wins; restate the facts without the forbidden token and flag it.
- 2026-09-05: BUG-1308 second renumber (218->219). plan-merge.py `amend` re-emits a folded `>-` scalar as ONE long line; re-wrapping it with textwrap.fill broke `main-session-direct` on its hyphen and YAML folding turned the break into a space ('main-session- direct'). The diff looked innocent. Only loading the value and comparing against `git show HEAD:<plan>` caught it. Use break_on_hyphens=False, and prove folded-scalar edits by loaded value, never by reading the diff.
- 2026-09-05: the strongest acceptance proof for an identifier-substitution amendment is a walk over safe_load(HEAD) vs safe_load(worktree) asserting every differing field satisfies old.replace(X,Y)==new, with the deliberate rewrites enumerated. It proves approval/panel untouched and no collateral edit in one run, where per-token greps only sample.
- 2026-09-05: BUG-1308 goal-check. SC-11 asserted "no production test bypass". The passing test cannot show this; I graded it by diffing the two production files against the baseline (harness_merge.py empty diff, expertise-merge.py no getenv/environ/flag) and reading the lock path and hold window at the caller. A negative claim about production code is graded from the production diff, never from the green fixture that asserts it.
- 2026-09-05: BUG-1308 goal-check c3. Twelve criteria graded green at 48d2285b while REQ-03 was false. Cause: REQ-03 has two clauses ("a replace at capacity keeps the size" and "no operation can leave a section over its cap") and only the first has an SC; SC-01 is existential over one benign fixture. I split multi-clause CRITERIA when grading (P-04) but had not split multi-clause REQUIREMENTS when tracing coverage, so a REQ clause with no SC was invisible. Sharper: the only criterion naming exit 12 (SC-04) is scoped to the key `section`; the words `entry` and `target` appear in no exit-12 clause, so `_reject_multiline` sat outside the graded surface of all twelve criteria by construction.
- 2026-09-05: BUG-1308 c3. The cycle-1 panel found the same defect class (VL-01) and the fix landed, but no criterion was added — BRIEF is approval-gated and nobody proposed one. The next goal-check therefore re-graded twelve criteria none of which mention that surface, and the cycle-2 panel found the class again at a wider alphabet. A landed panel finding does not create a criterion; consecutive goal-checks stay blind to the same surface.
