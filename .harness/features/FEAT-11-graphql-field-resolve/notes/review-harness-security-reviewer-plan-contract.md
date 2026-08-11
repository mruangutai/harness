# Security review — FEAT-11 plan-contract (plan.yaml @ 835b2976abd649fb814385d7d9b5b19fb7e1431a)

## BLUF

Thin surface, no must_fix. The five questions dispatched all resolve to info/low. One correction to
the dispatch's own hypothesis on Q3: the plan's transport re-raise *narrows* disclosure versus the
existing `run_gh` default, it does not widen it.

## 1. Query construction / injection — info, not a finding

`_FIELD_QUERY` (plan.yaml:120-142) is a static module-level GraphQL document with `$owner`,
`$number`, `$field` bound as declared variables. Step 2 (plan.yaml:161-167) passes it via
`-f query=` + `-f owner=` + `-F number=` + `-f field=` — operator input goes only into the *variable
values* argv elements, never concatenated, `.format()`-ed, or `%`-ed into the document text. No such
assembly is specified anywhere in the intent.

One gap in the verification story, not the mechanism: the task `verify:` block (plan.yaml:71-76)
reads `factory_gh._FIELD_QUERY` at **import time**, which proves the constant's shape but cannot
detect a query rebuilt or mutated at call time before being passed to `run_gh`. Part B's over-scope
guard (plan.yaml:315-328) closes most of this by regexing the actual `query=` value pulled from the
recorded argv in the success case — but nothing in the plan asserts that emitted value **equals**
`_FIELD_QUERY` by identity/equality, only that it matches the shape regexes. An implementation could
technically build a second, differently-worded string that still passes the shape checks. This has no
attacker: `field` is a value the operator already supplies and the operator already holds `gh`
credentials with equivalent privilege (Expertise P-02). Rate: **info** — suggest `assert q ==
factory_gh._FIELD_QUERY` in the Part B success case, not required to gate.

## 2. Argv construction — non-issue

`run_gh` (factory_gh.py:87-89) calls `subprocess.run([gh] + list(args), ...)` — list-form argv, no
`shell=True`. No shell metacharacter, newline, or embedded `=` in `owner`/`field`/`number` can escape
into a second shell command. Flag-injection (G-02) does not apply either: every operator-controlled
value is emitted as the *value half* of `-f key=value` / `-F key=value` — `gh`'s own flag parser has
already consumed `-f`/`-F` before it reads the next argv element, so an owner value beginning with
`-` becomes the string content of that one argv element, never re-parsed as a new flag. Plan step 2
is unchanged from this existing contract. **info.**

## 3. Error-message disclosure — corrects the dispatch's premise, not a finding

`run_gh`'s existing default path (factory_gh.py:96-99) already puts `gh`'s first stderr (or stdout)
line into the rendered exception message today — pre-existing, not introduced by this plan.

The plan-specific path is intent step 3 (plan.yaml:173-181): on a non-diagnosable `GhError` (a
genuine transport/auth failure), the resolver re-raises with a **fixed** `next_step` string
("re-run after checking gh auth status and network access"). `e.stdout`/`e.stderr` are carried only
as exception **attributes** (`GhError.__init__`, factory_gh.py:40-45); `GhError.__str__` is built
solely from `factory_cli.body(what, value, next_step)` and never renders `stdout`/`stderr`. So this
path actually **narrows** what reaches the operator-facing message relative to `run_gh`'s own
default — raw stderr stops appearing in `str(exc)` on the transport-failure branch. No auth-adjacent
detail from `gh`'s stderr is newly exposed. **info.**

## 4. Token / credential handling — info, established convention

Nothing in the plan captures `GITHUB_TOKEN`/`GH_TOKEN` or environment into an exception or log.
`run_gh` captures only `gh`'s own stdout/stderr; `GhError` never renders raw stdout/stderr into
`str()` (see #3). `run-unit-tests.sh` prints no environment variables (verified: no `env`/`TOKEN`
output in the script).

The `/tmp/feat11-unit.log` / `/tmp/feat11-integration.log` paths (plan.yaml:65-66) are predictable
world-readable `/tmp` paths, but this is the established convention across the tree, not new to
FEAT-11: FEAT-10's plan.yaml uses `/tmp/v-t01.txt`..`/tmp/v-t12.txt` (12 verify blocks) and FEAT-12's
uses `/tmp/feat12-t07.log` etc. — same shared-`/tmp`, predictable-name pattern, none of them carrying
credentials since none of the underlying commands print secrets. **info**, pre-existing pattern, not
a FEAT-11-specific gap.

## 5. Authorization boundary — confirmed refusal-only, plan does not overclaim

BRIEF.md:156 states the intent plainly: "Organization-owned boards stay out of scope: refuse loudly,
do not support." DESIGN.md Contract 2 frames the org branch purely as a client-side error message
(`what`/`value`/`next_step` row), never as an access-prevention mechanism. plan.yaml D-02 branch (b)
and intent step 3b (plan.yaml:189-192) likewise describe it only as raising `GhError` before any
write is attempted — nothing claims this stops GitHub-side access or substitutes for GitHub's own
authorization. A bypass of the client-side refusal (e.g. a future caller invoking the resolver
directly against an org board) would be denied or permitted purely by GitHub's own ACL, exactly as it
is today independent of this feature. **n/a as a security control** — correctly scoped by the plan as
a UX/message-routing decision, not a security boundary. No wording anywhere implies otherwise.

## Escalations

None. Nothing here requires reopening a `## Settled` item from the grilling artifact.

## Open questions

None blocking.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Plan's operator-input surface (GraphQL variables, argv, error messages) is clean by construction; no must_fix"
  in_scope: true
  scope_reason: "Diff touches operator-supplied input (owner/board/field) reaching a GraphQL query document and an operator-rendered error message, plus argv construction into a shelled gh call — a real, if thin, security surface"
  severity_max: info
  findings: 5
  must_fix: []
  threat_model:
    - { boundary: "operator input -> GraphQL query document (_FIELD_QUERY variables)", stride: T, mitigated: true }
    - { boundary: "operator input -> gh argv (list-form subprocess, no shell)", stride: T, mitigated: true }
    - { boundary: "gh stdout/stderr -> operator-rendered exception message", stride: I, mitigated: true }
    - { boundary: "org-board refusal (client-side) vs GitHub server-side ACL", stride: E, mitigated: true }
  open_questions: []
  files_touched: []
  expertise_update: []
cycles_used: 0
artifact: .harness/features/FEAT-11-graphql-field-resolve/notes/review-harness-security-reviewer-plan-contract.md
```
