# UI Review — BUG-1304 — panel-c2 (RE-GRADE) — c5869301

## Verdict: PASS. Both cycle-1 HIGH findings closed; equivalence holds byte-for-byte on both routes.

## F-01 (deny() appends contradictory "Write tool" advice) — CLOSED, confirmed by live execution

`bash-write-guard.sh:655` adds `deny_bare()` (prints `bash-write-guard: BLOCKED — {reason}`, no
second line) and all three `claim_checkout_guard` call sites (`:744` ambiguous, `:749` unreadable
registry, `:766` normal mismatch) now use it instead of `deny()`. Grepped the whole file for
`"Write tool"` — the only two remaining hits are the pre-existing generic `deny()` (READ-ONLY-agent
case and the unrelated `feature_checkout_guard`/domain-mismatch guards), neither touched by
`claim_checkout_guard` and both out of this diff's remit.

Ran the real fixtures (not just read source) for all three shapes on both routes and compared the
actual stderr bytes:

| Shape | check-domain.sh | bash-write-guard.sh |
|---|---|---|
|Normal mismatch (malformed pointer)|`check-domain: BLOCKED — {agent} holds worktree claim(s): {held}. Destination {dest} belongs in its proper checkout at {home}; write it from a bound worktree.`|identical text, `bash-write-guard:` prefix only|
|Ambiguous claim|`check-domain: BLOCKED — {agent} has an ambiguous worktree claim: feature '{id}' matches N linked worktrees: {names}`|identical text, prefix only|
|Expertise route|`check-domain: BLOCKED — {agent} holds worktree claim(s): {held}. Destination {dest} belongs to the control-plane expertise route. Use the sanctioned python3 expertise-merge.py apply command.`|identical text, prefix only|

No route ever appends a second line. The tool-name prefix (`check-domain:` vs `bash-write-guard:`)
is the only difference — that identifies which hook fired, not a route-local addition to the
substance, so D-08's "no route-local additions" clause holds. `test-bash-write-guard.py`'s own case
(`"Write tool" not in stderr`) passed live.

## D-02 ambiguous-claim wording — matches the settled decision verbatim; not a new gap

Plan `D-02` (via `e9dbc91d`) pins the required content precisely: "...naming the candidate
worktrees the resolver declined to choose between" — it does NOT require destination for this
branch (unlike the general claim-mismatch shapes, which do). The code's message ("has an ambiguous
worktree claim: feature 'X' matches 2 linked worktrees: FEAT, FEAT-X") names the candidates exactly
as decided and nothing more. Cycle 1's HIGH finding rested on reading DEC-218's general "name the
destination" language as applying to this branch too; the Advisor-approved `D-02` clause narrows
that scope explicitly for the ambiguous case. Per this role's own G-08 rule (wording matching an
approved plan's intent is a plan question, not a defect), I am not re-opening this. Advisory note
only: the message states a fact (which worktrees are ambiguous) without an explicit next action —
acceptable per the settled scope, but an operator who has never seen this message will still have to
infer "make the claim's feature id resolve to exactly one worktree" on their own. Severity: **info**,
non-gating, consistent with a decision already signed.

## Malformed-pointer `contains` argument — specific enough, confirmed live

Both new test cases (`test-check-domain.py` `_bug1304_domain_multi_and_malformed`,
`test-bash-write-guard.py` `_bug1304_bash_multi_and_malformed`) assert `contains=context["first"]` —
the actual absolute path of the worktree the agent currently holds. Fired both fixtures directly:
the refusal text reads `... holds worktree claim(s): /…/.claude/worktrees/FEAT-1304-A. Destination
/…/.claude/worktrees/broken/.harness/allowed/x.md belongs in its proper checkout at /…; write it
from a bound worktree.` — an operator sees exactly which worktree they hold and where the write
should go. **PASS**, both routes.

## One surprising thing, checked to ground and closed clean, noted as advisory

Firing check-domain.sh's expertise-route branch through `test-check-domain.py`'s own BUG-1304
fixture manifest (`_bug1304_domain_context`) initially returned a DIFFERENT message — the plain
manifest-domain denial ("may not write .harness/expertise/…; it belongs in .harness/team-config.yaml
— do not work around this hook") instead of the claim-set CLI redirect, because that fixture's
manifest never grants `.harness/expertise/**` (unlike `test-bash-write-guard.py`'s fixture, which
adds that grant explicitly). Checked the REAL `team-config.yaml`: every one of the 16 agents' own
domains DOES grant `.harness/expertise/<own-agent>.md` upsert — so in production the write reaches
`claim_checkout_guard`, not the generic domain denial. Rebuilt the fixture with that grant present
and re-fired: `check-domain.sh` produced the byte-identical CLI-redirect text shown in the table
above. **No functional gap** — confirmed by direct execution, not inferred. What IS true:
`test-check-domain.py`'s BUG-1304 suite never exercises this exact scenario (claimed-elsewhere agent
hitting their own expertise file via Write) the way `test-bash-write-guard.py` does — a test-coverage
asymmetry between the two routes' suites, not a shipped defect. Severity: **low**, advisory, more in
QA's lane than mine; naming it so nobody re-derives the same manual check next cycle.

## Cross-check: both suites green under live execution

`run_bug1304_claim_set()` in both `test-check-domain.py` and `test-bash-write-guard.py`: 0 failures,
all PASS, including the ambiguous/malformed/expertise cases enumerated above.

## Not re-litigated (per contract)

Cycle 1's other conclusions (claim-set-equivalence baseline, no new fail-open, `live_claims`
read-only) — nothing in the c5869301 diff touches the refusal-string surface those rested on;
carried forward unchanged.

## Not my lens

SC-06's textual-vs-runtime pre-change-assertion-count question (the ABC-split hoisting some
`bug1304_assert_pre_change_allows` calls into shared helpers) is a test-structure/gate-verify
question, not operator-facing text — left to code-reviewer/qa.

## Actionability, in the round

- Next step present and unambiguous: **yes**, all three shapes, both routes (expertise route now
  gives the CLI command verbatim; normal mismatch names the home checkout; ambiguous names the
  candidates per the settled decision).
- Never advises worktree removal: confirmed clean, all six call sites.
- Theme/contrast/reading-order/rendered-size: not applicable — plain stderr text, no rendered
  surface, nothing new to misrender.
