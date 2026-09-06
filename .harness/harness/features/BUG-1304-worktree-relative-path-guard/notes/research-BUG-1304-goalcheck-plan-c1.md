# Goal-check — BUG-1304 drafted plan vs stated intent — cycle 1

**DELIVERS WITH NAMED GAPS**

Read at working tree of the BUG-1304 worktree; lanes pinned `c369fb1f` (`plan.yaml:15`). Assessment
only — no file under this feature other than this note was written.

## 1 — Stated intent traced to the plan

Intent's per-issue success definition (`.harness/notes/grilling-six-residual-bugs-2026-09-05.md:9`),
station by station, for the PLAN phase question "can this plan reach it":

| Station | Mechanism in the plan | Reachable |
|---|---|---|
| approved BRIEF | `BRIEF.md:158-162` status pending, main-session write | yes |
| approved plan | `plan.yaml:3-4` `approval.status: pending`, `panel:` block present at `:8-12`, cycle 0 | yes |
| completed build | T-01..T-08, all `depends_on` wired (`plan.yaml:81,145,190,253,294,366,408,474`) | yes |
| completed validation | every task carries a runnable `verify:`; `change_type:` present on all 8 | yes |
| merged PR / ship closeout / closed issue | lifecycle stations, orchestrator-owned; correctly not plan tasks | yes |
| issue-specific verification | SC-01..SC-08 with `verify:` methods (`BRIEF.md:105-148`) | yes, except SC-06 and SC-07 — §6 |
| `check-state.sh` exiting 0 | **no task, no verify, no mechanism** | gap 1 |

Named station with no mechanism: **`check-state.sh` exit 0 and a full-suite regression run**. Eight
tasks change two registered PreToolUse gates and two shared libraries; the widest `verify:` in the
plan is T-08's three guard suites (`plan.yaml:479-483`). Nothing in the plan runs the harness suite
or `check-state.sh`, and the intent names both. It rests entirely on main-session closeout.

## 2 — B-10's defect vs the plan's remedy: legitimate substitution, not a swapped problem

B-10 (`BUG-1286 .../ship-review-2026-09-05-ship-final.md:86`) names the *symptom* (bare relative
paths) and proposes a spelling rule. The plan refuses by resolved destination (`BRIEF.md:33-39`,
D-01 `plan.yaml:35`). **This is the same problem, solved at the harm rather than at the mechanism.**
The argument, tested both directions:

- **Refuses both observed incidents?** Yes, conditionally. Both incidents are a worktree-assigned
  agent writing a main-checkout destination. Under D-01 the main checkout is a member of no agent's
  S, so exit 2 — *provided S is non-empty*, i.e. the writer's claim is live. See gap 2.
- **Refuses anything the spelling rule would have allowed?** Yes — the identical damage written
  absolutely. Measured in the BRIEF: the same claimed path exited 0 relative and 2 absolute on an
  unrelated rule (`BRIEF.md:36-39`), so spelling is not a proxy for harm here.
- **Allows anything the spelling rule would have refused?** Yes — a relative path resolving *inside*
  the assigned worktree. That traffic is legitimate (REQ-03, `BRIEF.md:40-48`), so the allow is a
  false-positive removed, not a miss.

Harm coverage is a strict superset; false-positive surface is a strict subset. The one respect in
which the substitution is *weaker* than a spelling rule is input availability: spelling is always
present in the payload, whereas the destination rule needs a live claim. That is gap 2, and it is
the honest cost of the substitution.

## 3 — Allowed change surface: every `files:` entry enumerated

Intent allows "implementation, focused tests, governing decisions/docs, and Harness lifecycle
artifacts" (`grilling-...:12`). Every path in the plan:

- implementation — `.claude/skills/harness/bin/harness_boundary.py`, `inflight_registry.py`
  (`plan.yaml:148-149`), `check-domain.sh` (`:256`), `bash-write-guard.sh` (`:369`),
  `dispatch-guard.sh` (`:477`);
- focused tests — `tests/unit/test-harness-boundary.py`, `tests/integration/test-inflight-registry.py`
  (`plan.yaml:84-85`), `tests/integration/test-check-domain.py` (`:193`),
  `tests/integration/test-bash-write-guard.py` (`:297`), `tests/integration/test-dispatch-guard.py`
  (`:478`);
- governing docs — `.harness/harness/docs/DECISIONS.md`, `DECISIONS-INDEX.md` (`plan.yaml:411-412`).

**No file falls outside the allowed surface.** The two T-08 paths are inside it by category; whether
T-08 belongs to *this issue* is §4, not a surface violation.

## 4 — T-08 (`dispatch-guard.sh _root_for`): RECOMMENDATION ONLY — strike it

**My recommendation, not a decision: STRIKE T-08 from this feature and file it as its own issue.**

Reasoning. T-08's own intent concedes the enforcement hole is closed without it, because T-02
resolves each claim by its `feature` field rather than by the registry file it sits in
(`plan.yaml:490-492`, D-02 `:40`). What T-08 changes is *where a claim is recorded*
(`dispatch-guard.sh:122` basename equality, `:126` owner-root fallback) — a different defect in a
third gate, with its own regression surface: every consumer that asks `live_claim(root=owner_root)`
stops seeing claims that move into a worktree registry. No REQ requires it (its `traces: [REQ-01]`
is satisfiable without it), and rule 6 says take the weakest sufficient change. It is closest in
kind to what the intent fences off at `grilling-...:27`.

Counterweight, stated honestly: T-08 is the only task that narrows the BRIEF's conceded wiring gap
(§7), and its verify re-runs both guard suites, so the regression risk is managed rather than
ignored. If the operator values closing the registry-placement defect now, keeping it is defensible.

## 5 — The two accepted residues: a reasoned boundary, not a forbidden risk acceptance

D-03 (`plan.yaml:45-46`) records a false-allow and a false-refuse, both same-persona. Judged against
the intent's ban on "risk acceptance" (`grilling-...:28`):

- **Closability.** The write payload is `{agent_type, hook_event_name, cwd}` (`BRIEF.md:87-94`,
  advisor note line 13). `cwd` cannot discriminate, because the premise of B-10 *is* that a
  worktree-assigned agent's cwd is the main checkout — the one field that could name the assignment
  names the wrong tree by construction. Exact match therefore needs a feature identity that does not
  exist on Claude Code at all, and on OMP exists only behind an untested `currentFeature` capture
  whose named wrong-feature-first branch would both refuse legitimate writes and allow the sibling
  harm (advisor note line 17). **This is an unclosable limit, not a deferred fix.**
- **Reachability.** Not rare: the advisor measured 3 personas holding ≥2 live claims at the time of
  the probe (advisor note line 15), and D-03 correctly rests on unbuildability rather than on
  rarity — the honest ground survives the frequency.
- **Direction of change.** Neither residue is a regression. Today `bash-write-guard.sh:794` allows
  *every* governed agent to write *every* worktree; the false-allow narrows that to same-persona
  concurrency. The false-refuse fails **closed**, with a REQ-06 message naming the worktrees held —
  an availability cost the agent can act on, not a silent harm.
- **Neither residue reopens B-10.** Both are worktree↔worktree or over-refusal; the measured
  main-checkout direction stays refused whenever S is non-empty.

**Verdict: legitimate reasoned boundary.** An unclosable limit stated plainly, in the plan and
verbatim in the DECISIONS.md entry T-07 lands (`plan.yaml:436-441`), is the opposite of a waiver —
it is the record the intent's ban exists to protect. **But it is incomplete: a third residue of the
same class is unstated — see gap 2.**

## 6 — SC-01..SC-08, each by name

| SC | Deterministic | Producing task | Verdict |
|---|---|---|---|
| SC-01 Write route, relative, exit 2 + names worktree | yes | T-03 case 1 (`plan.yaml:212-214`), T-04 | covered |
| SC-02 Bash route, redirect + in-place sed | yes | T-05 cases 1–2 (`:315-318`), T-06 | covered |
| SC-03 absolute, both routes | yes | T-03 case 2 (`:215`), T-05 case 3 (`:319`) | covered |
| SC-04 five negative cases, each separate | yes | T-03 cases 4–7 (`:218-230`), T-05 cases 5–8 (`:322-333`) | covered |
| SC-05 unparsed `.git`, ambiguity, both routes | yes | T-03 cases 9–10 (`:234-237`), T-05 cases 10–11 (`:336-339`) | covered |
| SC-06 discrimination against the **pre-change copy**, **run in the same test** | yes | **none** | **gap 3** |
| SC-07 a `D-NN` answering **all five** boundary questions, at `review_sha` | yes | T-07 covers the DECISIONS.md half only | **gap 4** |
| SC-08 short-form worktree basename | yes | T-03 case 11 (`:238-242`), T-05 case 12 (`:340-342`) | covered |

SC-06's failure is specific and mechanical: T-03/T-05 produce a *transient* red suite
(`plan.yaml:197,301`), which is gone the moment T-04/T-06 land, so nothing at `review_sha`
demonstrates discrimination. The idiom SC-06 requires already exists — `CHECK_DOMAIN_BIN`
(`tests/integration/test-check-domain.py:28`) and `BASH_WRITE_GUARD_BIN`
(`test-bash-write-guard.py:27`) — and only T-08 is instructed to use it (`plan.yaml:509`). T-03/T-05
are not.

SC-07's plan.yaml half asks for **a** `D-NN` stating all five answers; the five are spread across
D-01 (who is bound, destination not spelling), D-05 (preserved traffic), D-08 (both routes) and
D-01/REQ-05 (unresolvable). An inspection at `review_sha` grades that partial as written.

## 7 — The conceded verification gap (`BRIEF.md:150-156`)

**Narrows by one of two links, only if T-08 stands; otherwise leaves it exactly as conceded. Nothing
widens it.** The chain is dispatch → claim → payload identity → guard. T-08's new dispatch-guard
case asserts that a real dispatch records its claim where the guards will resolve it
(`plan.yaml:506-509`), which is the first link exercised for the first time. The second link — that
`agent_type` on a live Write payload is the identity the fixtures synthesise — remains proven by
construction under every task, T-08 included. Strike T-08 and the gap returns to its conceded state.

## Gaps found

1. **gating** — No task or `verify:` covers `check-state.sh` exiting 0 or a full-suite regression,
   though the intent names both as success (`grilling-...:9`). Eight tasks change two registered
   gates. Add a closeout verify or state explicitly that main-session closeout carries it.
2. **gating** — A third same-persona-class residue is unstated *and* one task's intent can create
   it. `_expire` keeps an OMP claim live at any age via supervisor identity but expires a
   compatibility-host claim at `CLAIM_TTL_SECONDS = 1200`
   (`.claude/skills/harness/bin/inflight_registry.py:29,215-224`). So on Claude Code a governed
   agent past 20 minutes has S empty, reads unbound, and B-10's exact incident is allowed again —
   unrecorded in D-03 or in T-07's entry text. Worse, T-02 instructs `live_claims` to "drop claims
   older than the TTL the module already applies" (`plan.yaml:159-161`): read as bare
   `CLAIM_TTL_SECONDS`, that also empties S for every OMP leaf past 1200s (the module records a
   7,200s longest measured leaf run, `inflight_registry.py:35`) while every fresh-fixture test stays
   green — D-02's own silent-unbinding failure shape in a second guise. Remedy is small and belongs
   at plan time: T-02 should name `_expire` as the reuse, T-01 should assert an OMP claim older than
   `CLAIM_TTL_SECONDS` with a live supervisor IS returned, and D-03/T-07 should state the
   compatibility-host TTL residue.
3. **gating** — SC-06 has no producing task. T-03/T-05 rely on a transient red suite, not an
   in-test pre-change copy at `review_sha`. Point them at `CHECK_DOMAIN_BIN` /
   `BASH_WRITE_GUARD_BIN` the way T-08 already points at `DISPATCH_GUARD_BIN`.
4. **gating** — SC-07 asks for one `D-NN` answering all five boundary questions; the answers are
   spread over D-01, D-05 and D-08. Either widen D-01's `choice` or re-scope SC-07 to the plan's
   `decisions:` block. Fixable pre-signature; unfixable after, since a change resets approval.
5. **advisory** — T-06 places the Bash-route claim-set check "beside the existing
   `feature_checkout_guard` calls" at `bash-write-guard.sh:841` and `:845` (`plan.yaml:385-390`).
   The `:840` branch fires on `allow` **and** `not_a_domain_question`, which is the `/tmp`
   pass-through SC-04 case 4 and T-05 case 14 require to stay exit 0. The Write route has no such
   overlap — `not_a_domain_question` returns earlier at `check-domain.sh:908`. One clause ("in-repo
   destinations only") removes the ambiguity; without it the build discovers it as a red case.
6. **advisory** — T-03 case 7 / T-05 case 8 instruct asserting that the owner-root registry "WAS
   read" (`plan.yaml:226-230`, `:331-333`) without naming an observable that distinguishes it from
   a skipped registry through a subprocess exit code. T-01 case 2 (`:121-123`) supplies that
   discrimination at the unit level; say so, or name the mechanism.
7. **advisory** — T-08's scope question is live and unanswered; see §4 for my recommendation to
   strike. Operator's call at signature, as the plan says.
