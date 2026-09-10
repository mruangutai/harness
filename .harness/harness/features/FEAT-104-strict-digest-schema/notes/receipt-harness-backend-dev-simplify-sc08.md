# Receipt — harness-backend-dev — simplify/simplification — SC-08 assertion delta

BLUF: PASS, no apply — the four-clause conjunction is the weakest sufficient form for Q1 (the
`_report()` failure path prints the raw `stderr[:500]`, which is short enough to show every clause's
actual match state on a break, so nothing beyond a plain conjunction is needed); Q2 finds the two new
clauses co-emitted from one unconditional `out.append` pair, which is a real but backlog-only
redundancy, never an apply.

## Q1 — is the failure report opaque, or does it name the broken clause?

`_report()` (`tests/integration/test-check-domain.py:165-177`) prints, on a failed case, the case
name plus `exit {returncode}: {stderr.strip()[:500]}` — the full raw emitter text, not a per-clause
boolean vector. The emitter side (`check-domain.sh:1653-1659`) produces, for this path, exactly two
`out.append` calls: `_head("undeclared step key or evidence shape.")` (`_head` = `f"check-domain:
{VERB} — {display or rel}: {text}"`, ~60-90 chars for this fixture) and the `offending key(s): …`
body (~230 chars including the `run-state-schema.json` and `` `evidence` `` literal substrings).
Combined they sit well under the 500-char cap, so on any single-clause break the printed `stderr`
is the complete emitted message — a maintainer reads it directly and sees which literal substring
is absent, with no truncation and no guessing. That is the anchoring semantics working: `_report()`
was built (session history, not re-derived here) to dump the actual observed text rather than a
collapsed `False`, precisely so a 4-, 5-, or N-clause AND stays diagnosable without per-clause
instrumentation. **Conclusion: the four-clause conjunction is the simplest sufficient shape; no
finding, no would-be edit.**

## Q2 — is `run-state-schema.json` redundant given `undeclared step key`?

`check-domain.sh:1645-1659`: both the head (`"undeclared step key or evidence shape."`, carries
"undeclared step key") and the body (`"offending key(s): …run-state-schema.json…`evidence`…"`) are
appended unconditionally, back-to-back, inside the single `if _schema_errors:` block guarded from
`:1618`. There is no branch between the two `out.append` calls and no path that emits the head
without the body (or vice versa) — they are one message, split across two Python statements for
line width, not two independently-reachable code paths. So yes: at today's emitter,
`"run-state-schema.json" in strict.stderr` is logically implied by
`"undeclared step key" in strict.stderr` firing at all; the two new clauses buy detection of a
future SPLIT of this one message (e.g. head kept but body's schema-path/backtick-evidence prose
dropped or reworded) rather than of any behavior distinguishable today.

**Finding SIMPLIFY-SC08-01** (`tests/integration/test-check-domain.py:88-89`, severity low): the
two new conjuncts are co-emitted with clause 2 at the single call site
(`check-domain.sh:1653-1658`) and so add zero discriminating power over today's code — only over a
hypothetical future edit that splits the message. Concrete edit it *would* make: drop
`and "run-state-schema.json" in strict.stderr and "`evidence`" in strict.stderr` back to the prior
two-clause form. **Left unmade** — DEC-174 read-only, and per `harness-simplify`'s apply rule this
class of finding ("asserts the same fact twice") is explicitly backlog-only, never an apply, even
off DEC-174. Whether it's "worth its two lines": yes on balance — SC-08 requires the strict denial
to *name the declaration ROUTE at the step seam* (PROOF gap the goal-check found), and asserting the
route explicitly, even redundantly with the head today, is the direct, literal closure of that
requirement; a future maintainer who splits the message text is exactly the regression this line
exists to catch. Recommend keeping it as an accepted, named backlog residual rather than trimming.

## Standing carry-forward
Q7 predicate-spelling residual (3 complete + 2 partial spellings of the strict-schema-version check
across `check-domain.sh`/`check-state.sh`) is already known and accepted — not re-raised here.

## Verification
Read-only run of `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-check-domain.py` was not
needed to answer either question (both resolved by static reading of the two files) and was not run,
per the "reading files... is permitted" note treated as optional, not required, when the code read
already answers the question.
