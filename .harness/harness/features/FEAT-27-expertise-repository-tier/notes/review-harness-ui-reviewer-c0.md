# UI review — FEAT-27-expertise-repository-tier — diff b4659cd..9b929de

**Verdict: PASS (scoped mostly out; one non-gating text-contract finding on the adjacent surface
named in dispatch).**

## Census (measured, not predicted)

`git diff --stat b4659cd..9b929de` → **57 files changed, 3892(+)/93(-)**.

Extension census over all 57 changed paths (`git diff --name-only` piped through extension count):

| ext | count |
|---|---|
| `.md` | 48 |
| `.py` | 3 |
| `.sh` | 3 |
| `.yaml` | 2 |
| `.json` | 1 |

Zero hits for `html/css/scss/tsx/jsx/vue/svelte/less` — no rendered UI surface anywhere in this
diff. `find .harness/harness/features/FEAT-27-expertise-repository-tier -iname 'DESIGN.md'` →
no results; no `DESIGN.md` exists for this feature. Both halves of my expected decline are
directly measured, not inferred: no rendered surface, no design contract.

Of the 48 `.md` files, the great majority are per-feature process artifacts (BRIEF, plan.yaml,
STATE, notes/, observations/, runs/ digests) — feature process record, not a UI contract, per
P-03/P-05 (markdown is a medium this role audits, not a guarantee any given markdown is in scope).
The dozen Expertise files and `.harness/harness/docs/SPEC.md` are prose about agent memory tiers and
budgets — same non-UI classification.

## The one surface worth a real look — inject-expertise.sh's precedence text

Dispatch named the hook's emitted header/precedence line and `check-expertise.sh`'s advisory
output as an adjacent surface worth auditing for legibility/consistency/truthfulness even absent a
rendered UI (P-06). I read both scripts' diffs and both files' test suites end to end.

**`check-expertise.sh`'s new ADVISORY line** (`ADVISORY {path}:{lno}: {label} names '{tok}' —
repository-layer candidate; rule on it (issue 340)`) is legible, consistently formatted against the
existing `FAIL`/`OK` prefixes, truthful about its own non-blocking nature (never appended to
`problems`, never flips exit code — verified in the diff), and matches its own header comment.
No finding here.

**`inject-expertise.sh`'s header/precedence text has a real, if narrow, completeness gap.**
Before this diff, the project-tier header itself stated the precedence rule unconditionally:
`"this codebase (project tier, authoritative on conflict)"` — present on every spawn that had a
project-tier file, regardless of what else was present. This diff (per plan.yaml's T-02/SC-10 and
the eng-lead arch-review it cites) deliberately drops that phrase from the header and moves the
precedence statement into a new line: `"Expertise precedence: repository over project over
global, by specificity. A repository block whose segment is not the one you were dispatched
against is not authoritative for your work — read the segment name."` — **but that line is only
emitted when at least one repository-tier block is present** (`if [ "${#sorted_idx[@]}" -gt 0 ]`,
`inject-expertise.sh` post-diff, in the repository-tier block).

Consequence: an agent whose spawn carries **both** a global-tier file (`~/.harness/expertise/<agent>.md`)
and a project-tier file (`.harness/expertise/<agent>.md`), but no repository-tier file, now receives
two un-arbitrated Expertise blocks with **no precedence statement anywhere in the injected text** —
strictly less information than before this diff, for a governance-critical rule the arch-review itself
called "the hardest-to-reverse thing in the plan."

This is not a hidden bug — `SPEC.md`'s own §5.2 rewrite says so honestly ("the hook says so in the
injected text **whenever a repository block is present**"), and `plan.yaml`/`arch-review.md` show the
resolution was designed and reviewed. But the global+project-only combination appears nowhere in
either artifact's discussion of precedence (`grep -n global` over both returns only budget-line and
generic-precedence-summary hits, never this specific combination), and it is untested: none of
`test-inject-expertise.py`'s 13 cases populate `$HOME/.harness/expertise/<agent>.md` (the global-tier
fixture) at all — every case that touches the `glob` variable's path is absent from the suite, so the
one combination that reproduces the gap is the one combination the test suite cannot see.

Confirmed live in my own spawn: my injected Expertise (visible above, this session) shows only
`## Your Expertise — this checkout's craft (project tier)` — a project-tier file exists
(`.harness/expertise/harness-ui-reviewer.md`), no repository-tier file exists yet for me
(`.harness/harness/expertise/harness-ui-reviewer.md` is absent — confirmed via `ls`), and no global-tier
file exists on this machine (`~/.harness/expertise/` doesn't exist) — so today this is dormant for
every agent, but 10 of 16 agents in this repo (all but backend-dev, dev-ops, documentor, eng-lead,
orchestrator, security-reviewer) already have a project-tier file with no repository-tier
counterpart, and the global tier is exactly the deployment path the feature describes populating
next (`.harness/harness/docs/SPEC.md`'s new §5.2/5.6 text). The day a global-tier file exists for any
of those 10, this combination goes live silently.

**Severity: low.** Non-blocking, no accessibility dimension (agent-context text, not colour-coded,
not a rendered surface), no falsification — SPEC.md accurately describes what the code does. It is a
genuine coverage/completeness gap in a precedence contract whose entire purpose is disambiguation,
worth closing (either restate precedence whenever ≥2 tiers of any kind are present, or add the
missing test case) before the global tier is actually populated for any agent that also lacks a
repository-tier file.

## Accessibility / theme parity

Not applicable — no rendered UI, no colour, no human-facing visual surface in this diff. This
section is explicitly stated rather than omitted, per this role's own gotcha about silent omission
reading as unchecked.

## Rendered-size / layout

Not verifiable from source in general (structural limit of this role), and moot here — nothing in
this diff renders.
