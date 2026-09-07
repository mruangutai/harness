# ALTITUDE angle — BUG-148 gate-record-correction

**BLUF:** One real altitude finding — FEAT-05's `STATE.md` correction is framed as an incident
narration ("**Corrected 2026-09-06 under BUG-148:**") where its sibling correction in
`DECISIONS.md` (DEC-174) states current truth with no such announcement. Recommendation:
`briefing-row` (operator-approved plan phrasing; not mine to edit unilaterally). No other
finding survives — (b), (c), (d) each checked out clean, evidence below. `ALTITUDE: 1 finding`.

## (a) Right depth — current truth vs. narrating the correction

Read both corrected passages (`DECISIONS.md:4308-4317`, `STATE.md:13-19` post-edit) against
DEC-205 ("An entry states current truth directly... it does not append a dated sub-section").

- **DEC-174** (`DECISIONS.md`): "`run-unit-tests.sh`, `check-docs.sh` and `check-state.sh` were
  green, and the fourth gate recorded that day, `gen-decisions-index.py --check`, was no gate at
  all: `--check` was never a supported mode..." — states the fact plainly, zero self-reference to
  the correction event. This is DEC-205's rule applied correctly: the entry reads as if it always
  said this.
- **FEAT-05 `STATE.md`**: "**Three gates green:** ... **Corrected 2026-09-06 under BUG-148:** the
  fourth entry logged on 2026-08-03, `gen-decisions-index.py --check` 0, was no gate at all..." —
  the bold lead-in narrates *that a correction happened, when, and under which bug*, which is
  exactly the amendment-convention pattern DEC-205 kills for the authority file. `STATE.md` is not
  literally bound by DEC-205's test (D-01's `because` confirms no test constrains it), but D-05
  ruling 1 explicitly directs it to match "DEC-174's treatment" — and DEC-174's actual treatment
  carries no "Corrected on X under Y" phrase at all. The two sibling corrections, made the same day
  under the same bug, sit at two different altitudes.
- **Concrete cost:** a future reader of `STATE.md` learns this was "corrected under BUG-148"
  before learning what is true today; the correction event, not the gate state, is what the bold
  text foregrounds. It also sets a style precedent — the next docs-only correction to a STATE.md
  under this flow now has a landed example to imitate that leans toward narration, the opposite
  of DEC-205's direction.
- **Alternative** (fold-in shape, for the record — not applied by me): drop "Corrected 2026-09-06
  under BUG-148:" as a bold lead-in and fold the date into the fact itself, e.g. "the fourth entry
  logged on 2026-08-03, `gen-decisions-index.py --check` 0, is confirmed as of 2026-09-06 to have
  been no gate at all: `--check` was never a supported mode...". **Invariant check:** `2026-09-06`
  stays present (T-02 verify requirement met); `never a supported mode`, `could not prove index
  drift`, `ffbdbfa1`, and the contiguous `gen-decisions-index.py --stdout | diff -
  .harness/harness/docs/DECISIONS-INDEX.md` are all untouched substrings, so they survive; heading
  count (7) is unaffected — this is inline-prose only. Net line effect is on `STATE.md`, not
  `DECISIONS.md` — this finding never touches `DECISIONS.md`, so no index regeneration is
  triggered.
- **Why not `fold-in` from me:** this exact framing ("corrected on 2026-09-06 under BUG-148")
  was specified in T-02's own `intent:` (plan.yaml:197) and D-05 ruling 1 was signed the same day
  by the operator at the signature review that produced this very task. Editing it now would
  quietly reverse a dated, attributed operator ruling rather than apply an unreviewed
  simplification — that is a decision for the lead/PM to re-raise, not mine to apply.
- **Recommendation: `briefing-row`.**

## (b) One authoritative statement vs. drift

Settled item 2 (read-only form named in both, by ruling) and settled item 3 (same mechanism,
same terms, in both) already foreclose "point one record at the other as sole authority" — D-05
rulings 2 and 3 are explicit refusals of exactly that consolidation. I did not re-litigate either.
The remaining live question per the dispatch — is the required duplication paired with a named
compensating control — is answered by T-02's own `intent:` (plan.yaml:221-227): "NO AUTOMATED
CHECK DISCRIMINATES THIS AGREEMENT, and none is added... The agreement therefore rests on this
instruction and on SC-06, the operator's read of both corrected passages." The plan already names
the control (human read at SC-06) and already reasons through and rejects the deeper fix (a
cross-file grep test) as adding a second verify dependency with no new discrimination power over
what T-01's own verify already asserts. This is reasoned-through already, not a gap. No finding.

## (c) Capability at the right home — tool vs. record

Checked whether `gen-decisions-index.py` itself refuses/explains an unrecognized `--check` today,
or whether that knowledge lives only in the decision text. Read `parse_argv()`
(`.agents/skills/harness/bin/gen-decisions-index.py:240-259`): an unrecognized argument (e.g.
`--check`) already prints `unrecognized argument(s): --check. Wrote nothing.` to stderr, prints the
docstring's usage, and exits 2 — landed at `ffbdbfa1` (2026-08-05, confirmed via `git show --stat
ffbdbfa1`: `perf(#140): validate argv so --help stops rewriting the index`, message explicitly
names `gen-decisions-index.py --check` as one of five historical sites of the false claim being
corrected now). So the capability the two records describe — refuse a bad flag loudly instead of
silently regenerating — is **already homed in the tool**, not bolted onto the decision text. The
two record corrections exist to fix a *historical* claim about a day before the fix landed; they
are not standing in for the tool's own guard, which already exists and already explains itself via
`--help`. No finding — the home is right.

## (d) Accepted residuals — right to accept, deeper fix available?

- FEAT-05's 165-line/7-heading shape violation: settled (item 1), D-04, left as found. Confirmed
  unchanged in the diff — no heading added/removed, no line-budget attempt.
- The un-mechanized cross-record agreement (b, above): already reasoned through in T-02's intent
  with a named compensating control (SC-06); accepting it does not reopen settled scope, and no
  cheaper deeper fix was overlooked — the plan already considered and rejected the cross-file-grep
  alternative for the correct reason (redundant discrimination, needless coupling of T-01/T-02
  verifies).
- The (a) framing residual is the one place I found the accepted shape to actually mismatch its own
  stated model (DEC-174's treatment); see above.

## ALTITUDE: 1 finding
