# Goal-check FINAL — FEAT-45-adversarial-plan-panel — SC-01..SC-17

**BLUF. Every criterion this repository can settle is now met: 14 met, 0 unmet, 3 carved out to the
operator's first live `/harness-plan`.** Both c0 openings closed and I re-established each
independently rather than restating the fix claim: SC-05 `unmet-behaviour` → `met`
(`check-state.sh:213-217` now emits distinct `disposition resolved.` / `disposition overruled.`
notes, which I confirmed on the criterion's *own* two-high-in-one-record fixture, not on two separate
single-finding fixtures), and SC-03 `unmet-unproven` → `met` (`test-plan-panel.py:294-323` section 9
renders the `scope` output at cycle 0 and cycle 1, asserts the paths **differ**, and resolves both —
28/28, up from 24). **The GOAL is not yet met, for one structural reason only, and it is a reason
SC-16 states in its own text: nothing has ever spawned this panel.**

## Provenance — and one thing the operator should know

`review_sha = d78f393a`. Worktree `HEAD` is `f7c25f5`, two commits later; `git diff --stat d78f393a
HEAD` touches only `feature.json` and four cycle-3 review notes — **no source file moved after the
pin**, so behavioural runs against the worktree are runs against the pin's source. Content criteria
(SC-09, SC-10) were graded with `git show d78f393a:<path>`, never a working-tree read. Tree clean
(`git status --porcelain` → 0 lines) before and after; `HEAD` never moved; nothing written outside
this note and `/tmp/fc45/`.

**The c0 grade was taken at `c745d3a`, which predates the `main` merge `5685a3a`** (416 files,
+55224/−5741 between them). Nothing carried over as "presumably still fine"; every criterion below
was re-run at this pin. `.agents/skills → ../.claude/skills` is a symlink inside the worktree; I
`cmp`-verified `run-unit-tests.sh` and `check-state.sh` are byte-identical through both paths, so the
suites ran the tracked scripts.

## The table — all seventeen

| SC | State | Method actually run | Evidence |
|---|---|---|---|
| **SC-01a** `should-not-exist` / REQ-02 | met | `test-plan-panel.py:110-112`, asserted on that step's own `prompt` | `plan-panel.yaml:21` — "what here should not be built at all?" |
| **SC-01b** `scope` / REQ-04 | met | `test-plan-panel.py:117-119`, asserted on that step's own `prompt` | `plan-panel.yaml:42-43` — "which tasks serve no live requirement, and what does the feature actually need to ship?" |
| **SC-01c** goal-check / REQ-03 | met | `test-plan-panel.py:125-126` against playbook text | `.agents/skills/harness/SKILL.md:97-98` — "does this plan deliver the operator's stated intent?" |
| **SC-01** falsifier: no reader's question missing | met | three *separate* per-reader assertions above; no file-global match anywhere in section 1 | 28/28 in `test-plan-panel.py` |
| **SC-01** falsifier: no out-of-squad harness persona | met | cases 4a/4c/4d — 4d loops **every** step but `should-not-exist` (`test-plan-panel.py:208-213`) | `code-reviewer` ∈ team-config `Validation` members; `fable-advisor` ∉ the 16 `.omp/agents/harness-*.md` (SC-14's permitted exception) |
| **SC-02a** `scope` rendered output | met | `check-domain.sh --resolve .harness/harness/features/FEAT-45-adversarial-plan-panel/notes/review-harness-code-reviewer-planpanel-c0.md` | rc=0, prints `harness-code-reviewer` (+ `harness-orchestrator`) — the step's own persona |
| **SC-02b** playbook goal-check note | met | `check-domain.sh --resolve .harness/harness/features/FEAT-45-adversarial-plan-panel/notes/research-FEAT-45-adversarial-plan-panel-goalcheck-plan-c0.md` | rc=0, prints `harness-pm` |
| **SC-02** excluded step | n/a | `should-not-exist` declares `outputs: []` (`plan-panel.yaml:18`) — enumerated, then excluded because SC-02's own text assigns it to SC-14 | a read-only reader that writes nothing cannot be denied a path |
| **SC-03a** `should-not-exist` writer | met (vacuous, correctly) | `test-plan-panel.py:162-175` per step | `outputs: []` — nothing to render, nothing to collide |
| **SC-03b** `scope` writer | met | same, per step | `plan-panel.yaml:39` `…planpanel-c{{cycle}}.md` |
| **SC-03c** playbook goal-check writer | met | `test-plan-panel.py:178-179` | `SKILL.md:99` names a `c<cycle>` suffix, "required because this segment re-runs" |
| **SC-03d** superseded record survives a re-run | **met (was `unmet-unproven`)** | read `test-plan-panel.py:294-323` at source, then ran it | asserts `rendered_c0 != rendered_c1` (`:308-311`), then resolves **each** cycle's path to `code-reviewer` (`:312-323`). Run: `ok (9) … c0 path differs from c1 path`, `ok (9) scope c0 … resolves`, `ok (9) scope c1 … resolves`. Behavioural, not a `{{cycle}}`-substring proxy |
| **SC-04** | met | my own fixtures via `check-state.sh` (`/tmp/fc45/probe2.py`), all three directions | high+open, no ruling → `VIOLATION INV-32: … is high and remains open without an operator overrule.`; same finding overruled → note only, no VIOLATION; same finding resolved → note only. Failing-first **standing**: `sc04_refusal` is in `_inv32_mutant_is_discriminating`'s tuple (`test-check-state.py:3080-3084`), and `_inv32_mutant_fixture_passes` requires per fixture real-rc=1 + `INV-32` present, mutant `INV-32` **absent**, no traceback — green as `ok - INV-32 plan panel fixtures, including inv32-red` |
| **SC-05 clause A** "names which is which" | **met (was `unmet-behaviour`)** | the criterion's own fixture: **one** record, two `high` findings, `PF-aaaaaaaa` resolved + `PF-bbbbbbbb` overruled (`/tmp/fc45/sc05_probe.py`) | two distinct lines in one output: `note INV-32: … finding PF-aaaaaaaa disposition resolved.` and `note INV-32: … finding PF-bbbbbbbb disposition overruled.` Source: `check-state.sh:214-217`. No INV-32 VIOLATION |
| **SC-05 clause B** unattributed / undated overrule rejected | met | same fixture with `who: ""`, then with `date` absent | both → `VIOLATION INV-32: … ruling for PF-bbbbbbbb is unattributed or has an invalid date.` (`check-state.sh:199-200`) |
| **SC-05** roll-up | met | both clauses graded separately above, against the same two-high record | neither clause rests on the other's fixture |
| **SC-06** | met | `git ls-tree --name-only d78f393a:.omp/agents` / `:.claude/agents`, + `test-plan-panel.py` case 5 | 16 and 16, same names. Membership: `git diff --name-status ba338d8 d78f393a -- .omp/agents .claude/agents` → only `M harness-validator-lead.md`, no add, no delete |
| **SC-07** | met | my own fixture: `panel` key absent entirely | rc=1, `VIOLATION INV-32: FEAT-INV32 plan is approved with no complete panel result recorded.` (`check-state.sh:181-182`) |
| **SC-08** | met | `run-unit-tests.sh --kind unit` from the worktree — see the volume block below | Files this feature **adds** (`git diff --diff-filter=A ba338d8 d78f393a -- '.claude/skills/harness/bin/test-*.py'`) are exactly `test-panel-findings.py` and `test-plan-panel.py`. Both are in `UNIT_SCRIPTS` (`run-unit-tests.sh:30`) and both are **named** in the run: `PASS test-panel-findings.py`, `PASS test-plan-panel.py` |
| **SC-09** | met | `git show d78f393a:.harness/harness/docs/DECISIONS.md`, `:DECISIONS-INDEX.md` | One entry per REQ-11 carve-out, each naming its precedent: **DEC-206** "A harness lead may wrap a non-harness panel reader…" — *"a precedent needing a signature because the reader's return is structurally unvalidated"*; **DEC-207** "A gate may grade a specification before any code exists…" — *"A gate MAY fire in the plan phase, before any code exists"*. Both cite `FEAT-45-adversarial-plan-panel` as origin. Index **regenerated, not eyeballed**: `gen-decisions-index.py --stdout` output is byte-identical to `git show d78f393a:…DECISIONS-INDEX.md`; DECISIONS.md and the index are both byte-identical between pin and worktree, so the regeneration is against the pin's content |
| **SC-10** | met | `git show d78f393a:.claude/commands/harness-plan.md` | `Target state` bullet: *"under DEC-176 all findings enter the ONE batched review pass rather than opening a separate pre-signature fix dispatch"* — routes in, introduces no separate dispatch |
| **SC-11** | deferred-to-live-run | `verify: uat` — not agent-settleable | criterion's own words: *"**On a live plan, the operator judges** each of the three readers to have earned its spawn"* |
| **SC-12** | deferred-to-live-run | `verify: uat` | *"**On a live plan** whose panel raises nothing at `high`, **the operator** reaches the signature with no extra step"* |
| **SC-13** identity stability | met | `test-panel-findings.py` via the unit gate, 9/9 | case2 normalization-only difference ⇒ **same** id; case3 one-character summary change ⇒ **different** id; case4 different readers ⇒ different ids; `PF-` + 8 lowercase hex, length 11 |
| **SC-13** stale overrule refused | met | my own fixture: ruling on `PF-cafebabe`, absent from the current findings | `VIOLATION INV-32: … STALE OVERRIDE PF-cafebabe: a reworded finding gets a NEW content-hash id, so the old ruling stopped applying and the operator is asked again.` (`check-state.sh:201-204`) |
| **SC-14** | met | `test-plan-panel.py` cases 4a/4b | persona `fable-advisor` ∉ the 16 `.omp/agents/harness-*.md`; `outputs: []` (`plan-panel.yaml:15,18`) |
| **SC-15a** frontmatter allowlist | met | `git show d78f393a:.omp/agents/harness-validator-lead.md` | `spawns:` block lists `- fable-advisor` (5th entry, after the four harness reviewers) |
| **SC-15b** `SPAWNS` constant | met | `git show d78f393a:.claude/skills/harness/bin/sync-agent-adapters.py` | `"fable-advisor"` inside `SPAWNS["harness-validator-lead"]` (`:63-75`), asserted as a **second, separate** check (`test-plan-panel.py` case 8b), persona read from the team file not hardcoded |
| **SC-16** | deferred-to-live-run | `verify: uat` | *"**On the first live `/harness-plan` after this ships**, `harness-validator-lead`'s dispatch of the adversarial reader is not refused at preflight and the reader returns"* |
| **SC-17** | met | my own fixtures, both directions | reader recorded `status: skipped` + persona + reason → `note INV-32: … reader should-not-exist skipped persona fable-advisor: not installed`, **zero** INV-32 VIOLATION lines and no "no complete panel result" line; reader absent with no skip entry → `VIOLATION INV-32: … reader should-not-exist never ran or was not recorded; an unrecorded reader is not a clean reader.` Failing-first **standing**: `_inv32_plan(readers=missing)` is in the same D-13 marker-mutant tuple (`test-check-state.py:3083`) |

## SC-08 — discovery volume, stated explicitly

An exit code cannot distinguish a green suite from a suite that ran nothing, and at the c0 pin the
runner was collecting **zero** tests while exiting in a way that looked survivable. At **this** pin:

| Measure | Value |
|---|---|
| exit status of `run-unit-tests.sh --kind unit` | **0** |
| registered scripts in `UNIT_SCRIPTS` (`run-unit-tests.sh:30`) | **30** |
| script-result lines (`^PASS test-…` / `^FAIL test-…`) | **32** (31 distinct labels — `test-panel-findings.py` prints its own summary line *and* the runner prints one; `test-code-grade` is an internal case label, not a script) |
| `^FAIL ` lines | **0** |
| `not ok` lines | **0** |
| `ok…` assertion lines | **915** |
| `KIND-DRIFT` lines | **0** |

So the suite ran, and it ran the two files this feature added. `test-plan-panel.py` standalone:
**28/28**, exit 0.

## What is deferred, in the criteria's own words

Three items, not four. Each is `verify: uat` and each says in its own text that it needs a live
`/harness-plan` and the operator's judgement:

- **SC-11** — *"On a live plan, the operator judges each of the three readers to have earned its
  spawn."* Nothing on disk can settle whether a finding is substance or padding.
- **SC-12** — *"On a live plan whose panel raises nothing at `high`, the operator reaches the
  signature with no extra step beyond reading the panel's result."*
- **SC-16** — *"On the first live `/harness-plan` after this ships … This is `uat` and not `automated`
  for a measured reason: SC-15 can only grade the list's content, and whether the host RESOLVES the
  pinned persona to a real agent once the allowlist admits it is not determinable from anything on
  disk."*

**There is no fourth deferral, and I am not manufacturing one to match a count.** The reviewer-return
defect (F5/V1) — the executing `SubagentStop` hook resolving the main checkout's 1525-line
`validate-digest.py` instead of the worktree's 1643-line fixed copy, because `gateRoot()` derives
from the extension file's own location — is real and is the operator's recorded
correct-by-inspection, unverifiable-pre-merge ruling. **No criterion in SC-01..SC-17 depends on a
reviewer's structured return landing.** I checked mechanically: the Success Criteria block contains
zero occurrences of `validate-digest`, `reviewer`, `SubagentStop` or `structurally unvalidated`. The
two `digest` mentions are both inside SC-11, and they refer to the *validator lead's own consolidated
digest as read by the operator by eye* — not to the digest validator. SC-09 grades DEC-206/DEC-207 as
**committed content at the pin**, which I read directly; that grade does not wait on any hook.

## Unmet items and their owning lanes

**None.** `unmet-behaviour: 0`, `unmet-unproven: 0`. Nothing to route, and consistent with the
operator's ruling that cycle 10 is preserved.

## Advisories — recorded, not graded, not fix proposals

1. **SC-04, SC-05, SC-07, SC-13 and SC-17 declare `evidence: unit`, but their assertions live in
   `test-check-state.py`, which sits in `INTEGRATION_SCRIPTS`** (`run-unit-tests.sh:31`), unchanged
   since c0. This is **not** a proof failure: the assertions exist, and I ran them
   (`test-check-state.py` → exit 0, 147 lines, 0 `FAIL`, `ok - INV-32 plan panel fixtures, including
   inv32-red`), plus every direction independently through my own fixtures. It is a mislabel in the
   BRIEF's `evidence:` kind, and SC-08 does not catch it because SC-08 quantifies only over files this
   feature **adds** — `test-check-state.py` is modified, not added. Worth a line in the record so it
   is not rediscovered as a defect.
2. **The mutant must live in the bin directory.** My first attempt placed the D-13 marker mutant in
   `/tmp` and it tracebacked — `check-state.sh` resolves its root from `$_SELF_BIN` via
   `harness_boundary`, so a copy outside `.claude/skills/harness/bin/` cannot resolve one. The
   shipped test writes it as `…/bin/.check-state-inv32-mutant.sh` and unlinks it in `finally`
   (`test-check-state.py:3070,3086-3088`); the tree was clean after my run, which is the receipt that
   it cleaned up. Anyone re-deriving the failing-first proof should place the mutant there, not in a
   temp dir, or they will mistake an import failure for the region's absence.

## Three different questions, answered separately

**(a) Are the tasks done?** Yes. All plan tasks `status: done`; the qa gate and the reviewer panel
have run. Not re-litigated here.

**(b) Is every criterion machine-verifiable today?** No, and by design. Three are `uat` and say so.
The BRIEF's own `## Verification gaps` section records why: `eval` has `cmd: null`, so **no runner in
this repository can grade the panel's finding quality**, and **no runner here performs a live spawn**,
so the preflight decision itself is unautomatable. Fourteen criteria grade the panel's *wiring* and
all fourteen are green.

**(c) Is the GOAL met?** **Not yet — and only for the one reason the feature itself named.** The goal
is a *standing* panel that reads every drafted plan, withholds on a `high`, and records an overrule
durably. Everything establishable from disk is now established, and unlike at c0 there is nothing
left in the "correct but unproven" column: the team file resolves, three readers each carry their own
question asserted individually, every non-empty output path is granted to its own persona, each
re-runnable writer resolves `{{cycle}}` and a second cycle provably does not overwrite the first's
record, INV-32 refuses a signed plan with no panel record / an open `high` / a stale overrule / an
unrecorded reader — each demonstrated to redden **only** because of the region this feature added —
and it now names a resolved finding apart from an overruled one in one output. The precedents are
signed and the index regenerates clean.

What remains is not a defect and not a test gap. **Nothing in this repository has ever spawned this
panel.** SC-16 exists precisely because the c1 cycle found that ten green tasks had all graded text on
disk. What has shipped is a correct, fully fixtured, fully wired *specification of a panel plus its
enforcement gate* — and the goal is that the panel **runs**. That closes on the operator's first live
`/harness-plan`, which is also where the F5/V1 reviewer-return fix gets its first real execution. One
live run settles SC-11, SC-12 and SC-16 together.

**Recommendation, as information: this is closeable on the operator's judgement, not on further
engineering.** No cycle-10 work is required to move any criterion.
