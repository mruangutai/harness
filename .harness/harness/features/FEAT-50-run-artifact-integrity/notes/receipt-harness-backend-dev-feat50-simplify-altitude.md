# FEAT-50 simplify pass — ALTITUDE angle

## BLUF

**Instance-vs-class: three patches at genuinely different enforcement points — correctly, not
three unrelated ones sharing a narrative.** #1056 lives in `validate-digest.py`'s `SubagentStop`
Python hook; #1057 lives in `check-domain.sh`'s domain-verdict route (`domain_check()`, ALLOW/DENY
before content exists); #1058 lives in `check-domain.sh`'s content-shape route (`shape_problems()`,
runs only after a write is already allowed). Even the two that share a file answer different
questions — "may this write happen at all" vs "does this write's *content* destroy something" —
and the plan correctly keeps them as separate branches rather than merging into one function. No
unification recommended; this is an explicit clean result on that question.

One real altitude finding: T-03's feature→worktree derivation is planned inline in
`check-domain.sh` when the module that already owns "which checkout does this path stand in"
(`harness_boundary.py`) is not opened by this plan at all. Recommend **fold-in**.

Everything else below (rule-homes counts, the mutant self-reference residual, T-06's prose) checks
out — findings: `[]` for those three checks, with the reasoning that makes them clean rather than
merely unexamined.

## Findings

| id | severity | element | summary | recommendation |
|---|---|---|---|---|
| ALT-01 | med | T-03 (`check-domain.sh` intent, plan.yaml:279-322) | feature-id-from-path derivation + worktree-basename match is planned as inline logic in `check-domain.sh`, not as a named function in `harness_boundary.py`, which the plan's own `files:` and `lanes:` never open | fold-in |

**ALT-01 detail.**
`harness_boundary.py` already owns exactly this class of question — `worktree_owner()` (:515,
"which checkout does `path` stand in"), `checkout_relative()` (:102), `linked_worktrees()` (:138,
enumerates registered checkouts) — and `check-domain.sh` already imports it (`harness_boundary`,
referenced at check-domain.sh:740). T-03's intent (plan.yaml:288-291) instead has the gate itself
regex-match the feature id off the path, call `linked_worktrees(root)`, and select-by-basename —
new domain logic placed in the caller rather than as a fourth named lookup (`worktree_for_feature`
or similar) beside the three that already live in the module. `harness_boundary.py` is not in T-03's
`files:` list (plan.yaml:276-277) and is not a row in `lanes:` (plan.yaml:19-64) — the plan never
opens the file whose job this most resembles.

*Failure scenario:* a later feature needs the same "which worktree owns feature X" lookup from a
different caller — e.g. a Python-side hook wanting to bind writes the way `validate-digest.py`
binds returns. `check-domain.sh` is bash and unimportable, so the author reimplements the
regex-plus-basename-match by hand next to a new call site. The two copies are free to diverge (e.g.
one resolves through `harness_boundary.real()` before comparing per D-03/D-04's own mandate, the
other forgets to and a symlinked worktree path slips past by spelling) — the same "logic duplicated
across call sites, one copy drifts" shape that produced #1057 in the first place.

*Alternative:* add T-03's `files:` entry for `.claude/skills/harness/bin/harness_boundary.py`, and
move the derive-feature-id / select-by-basename logic there as one named function (e.g.
`worktree_for_feature(root, feature_id)` returning the matching checkout or `None`), called from
`check-domain.sh`'s existing `if _run_domain:` block. The regex `^\.harness/[^/]+/features/([^/]+)/`
and the `real()`-before-compare requirement move with it. `check-domain.sh`'s side shrinks to: call
the function, deny with the two named paths if it returns a mismatch.

## The four standard checks

**1. One authoritative statement of a rule, or several that can drift?** — clean, `findings: []`.
Counted the homes for both cited rules. Digest-preservation: D-05/D-06 (plan.yaml:109-128, decision
rationale), T-04's code + mandated comment (plan.yaml:379-382, the one enforcing copy), T-06's two
SKILL.md sentences (plan.yaml:486-495, one "home" per T-06's own instruction — the red-flags-table
row and the run-dir-layout sentence are two mentions inside *one* file, not two homes), T-07's
DEC-208 §3 (plan.yaml:553-561, historical record). Same shape for presence-vs-truthiness (D-01,
T-01's comment, DEC-208 §1) and the checkout binding (D-03/D-04, T-03's comment, DEC-208 §2). In
every case exactly one artifact enforces (the script), and the rest — plan-decision rationale,
skill-doc guidance for a human lead, decisions-record history — are different audiences for the same
fact, which is this repo's standing convention for every feature, not drift risk this plan
introduces. T-06's own "not a third time" instruction is consistent with the plan's actual structure
once "home" is read as artifact, not sentence-count; it is not contradicted.

**2. Capability planned into a caller that belongs in the module it calls?** — ALT-01 above.

**3. Residuals accepted without a compensating control named?** — clean, `findings: []`, for the
mutant-self-reference residual specifically (BRIEF.md:174-178). A control IS named: T-02/T-05
require the mutant text to differ from source AND to exit 0/2 with no traceback on stderr
(plan.yaml:253-256, 437-439), which rules out a `SyntaxError`/`NameError` masquerading as a pass.
The deeper gap BRIEF discloses — nothing proves the mutant harness itself was invoked against the
real artifact, beyond its own assertion — is the same "who tests the tests" limit FEAT-45 accepted
for `inv32-red`, cited as precedent, and disclosed rather than hidden. No deeper fix is reachable
without reopening scope (an independently-invoked, non-self-referential mutation harness is a
tooling project of its own, not a task-sized fix). Leave as disclosed.

**4. `harness-team/SKILL.md` altitude — prose describing code-enforced behaviour.** — clean,
`findings: []`, **leave**. T-06 is scoped to two sentences, explicitly forbidden from restating
enforcement logic (it names `check-domain.sh` and the observable behaviour — refused when content
isn't preserved — never the regex or the shape-route mechanics), and the file carries a 300-line
cap (plan.yaml:481) that bounds how far this could drift into a second authority even if edited
carelessly later. The gate's own exit-2 message (plan.yaml:363-368) is the authoritative,
enforced explanation at the point of failure; SKILL.md's role is prospective orientation for a lead
who has not yet hit it, which is the correct altitude for a playbook document — not a second
enforcement authority.

## Read

`.agents/skills/harness-simplify/SKILL.md` §ALTITUDE; `plan.yaml` (full, both halves); `BRIEF.md`
(full); `.claude/skills/harness/bin/harness_boundary.py` (`checkout_relative`, `linked_worktrees`,
`real`, `worktree_owner`, :102-593); `.claude/skills/harness/bin/check-domain.sh`
(`SHAPE_PATTERNS`/`shape_problems`/`_run_domain` structure, :113-1204).
