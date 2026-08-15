# Code review — FEAT-09, cycle 0

base `47ed11f` · review_sha `4918d06` (HEAD). Scope: `git diff 47ed11f..4918d06`. No dirty files among
the 9 source files (git status confirmed clean there), so working tree == pinned SHA for everything
cited below.

## Verdict: PASS, with a lead finding for a follow-up fix

Stage 1 (spec compliance) is clean — every change traces to a REQ/D, no scope creep, no omission, all
SC-01..SC-12 and REQ-01..06 checked against the diff and the BRIEF/PLAN text. SC-11 reconfirmed both
clauses myself: (b) `git diff 47ed11f..4918d06 -- .claude/agents/harness-pm.md` is empty; (a) the rule's
one home is `.claude/skills/harness-spec-driven/SKILL.md:26-48` ("## Routing is resolved at plan time",
confirmed via `grep -n '^## '` on the file — no other `## ` heading duplicates it). Stage 2 found one
real, previously-undisclosed input-handling bug in `check-plan-routes.py` (F0) that in its *modal*
form fails safe (loud, misdiagnosed rejection) and only fails open under a narrower condition this
repo's actual PLAN-authoring convention rarely produces — measured, not assumed, below. That keeps it
at MED rather than a gating HIGH, but it is worth fixing before this checker is trusted as a backstop.

## F0 (NEW, MED) — a blank `files:` field is mishandled; modal case fails safe, one narrower case fails open

`check-plan-routes.py:38`: `FILES_RE = re.compile(r"^\s*files:\s*(.*)$", re.M)`. `\s` matches `\n`, so
when a task's `files:` line has nothing after the colon, the trailing `\s*` slides *across the
newline* into the next line's leading whitespace, and `(.*)$` captures **that next line's content** as
the files value — or, if `files:` is the block's last line, captures nothing, silently.

Reproduced through the real CLI (`check-plan-routes.py <fixture>`, actual subprocess, real files via
process substitution) and discriminated with a control case per the review's own advisor pass:

**Discriminator (proves TASK_RE matches this block shape at all):** the identical one-line-task
fixture with `files:` *filled in* prints `OK T-01`; with `files:` *blank* on the same last-line shape
it prints nothing for T-01 — same overall summary line, T-01 present in one output and absent in the
other. This isolates the silence to the empty-value path, not to TASK_RE failing to match the block.

**Three sub-cases, walked and measured, not asserted:**
1. **Modal case — fails safe.** Blank `files:` followed by an `intent:` line (this repo's universal
   authoring shape — every sampled `files:` line is immediately followed by `intent:`): produces a
   loud `VIOLATION T-01: intent: run a script that touches nothing tracked ungranted (NOBODY); ...`,
   naming a fabricated "path" that is a fragment of the intent prose. Misleading, but it blocks the
   plan — REQ-02's mechanism still fires, just with a wrong explanation.
2. **Fail-open, but rare here.** If the captured fragment happens to contain `*` or `?`, it is
   classified `UNRESOLVED-GLOB` instead, which contributes zero violations by design (D-04) — a blank
   `files:` field silently downgrades to a non-blocking pass. Measured how often this repo's own
   authoring would hit it: `grep`-scanned every `files:` line across all `.harness/features/*/PLAN.md`
   (38 total) and checked whether the immediately following line contains `*` or `?` — **0/38**. So
   this specific fail-open path is real but not supported by how tasks are actually written here today.
3. **Fail-open, but requires a malformed block.** Blank `files:` as the literal last line of a task
   (nothing after it — no `intent:`, no `change_type:`) produces total silence: `0 violation(s) across
   1 plan(s)`, no line naming the task at all. This directly breaks T-02's own stated design principle
   (`PLAN.md:189`, "no finding may be reported by silence") — but it requires a task missing `intent:`
   and `change_type:` too, which `harness-spec-driven/SKILL.md:11-21` already makes mandatory
   ("A task missing any of them is not written") — so reaching it requires the PLAN to already be
   violating a rule this checker is not the first line of defense against.

**Why MED and not HIGH:** the BRIEF's own reasoning for why this feature exists at all is DEC-125's
"prose alone is relied on being pointed at, and decays" — cited directly in `BRIEF.md:110-111`. That
argument cuts both ways here: sub-case 1, the realistic one, still mechanically blocks (prose-adjacent
failure, mechanism intact); sub-cases 2 and 3 are the DEC-125 shape recurring inside the very backstop
built to prevent it, but both require inputs this repo's own convention and its OTHER mandatory-field
rule make uncommon. Real defect, worth fixing (the minimal fix is bounded — reject/flag an empty
captured `files:` value the same way a missing `files:` line is already flagged), but not a
must_fix given the measured rather than assumed reachability.

**Not caught by the existing suite.** None of the 17 named cases in `test-check-plan-routes.py` uses a
task with an empty `files:` field; the closest, "missing `files:` line" (`:79`), exercises a different
code path (`files_match is None`, confirmed working correctly) — not this one.

## F1 (MED) — SC-08 clause 4's sole behavioural fixture doesn't discriminate an over-permissive reimplementation

Independently reproduced; **already found and disclosed** by harness-qa as F1 in
`notes/review-harness-qa-c0.md` — I concur with the MED rating and the "held at MED, not higher,
because `matches()`/`glob_to_re()` are not modified by this diff" reasoning.

Case 17's grant path — `.harness/features/*/runs/*-eng/**` against
`.harness/features/FEAT-09-plan-time-route-check/runs/1-eng/notes.md` — never requires the mid-pattern
`*` to cross a `/` (it consumes only `1` before `-eng`, within one path segment). So it discriminates
against a naive prefix/`startswith`-before-`/**` reimplementation (confirmed:
`.startswith('.harness/features/*/runs/*-eng')` → `False`, the real matcher → `True`) but **not**
against an `fnmatch`-style reimplementation whose `*` matches `/` — confirmed empirically:
`fnmatch.fnmatch(path, '.harness/features/*/runs/*-eng/**')` → `True`, same answer as the correct
matcher. Cases 8/9/16 are source greps for the literal strings `fnmatch`/`glob_to_re`, respellable by
any reimplementation using different names. This does not affect the delivered code — I read
`resolve_agents()`/`process_task()` end to end and confirmed structurally, not by grep, that there is
no local matching of any kind: every literal path goes to `check-domain.sh --resolve` via subprocess
(`check-plan-routes.py:52-57`) and the caller only parses that subprocess's stdout lines
(`:61-67`). It is a regression-proofing gap in the test suite, not a live bug.

## F2 (MED) — the `SHARED` signal is discarded, producing a misleading VIOLATION message

Independently reproduced; **already found and disclosed** by harness-qa as F2. `resolve_agents()`
(`check-plan-routes.py:64`) filters out both `NOBODY` and `^SHARED ` lines, so a shared-convention-only
path (e.g. `package.json`, granted to nobody's `domain:` but listed under `team-config.yaml:59-67`
`shared:`) resolves to `agents = []`, identical to a genuinely ungranted path. Verified:
`files: package.json`, `execution_mode: team` → `VIOLATION T-01: package.json ungranted (NOBODY);
execution_mode is team — legal tokens: team, main-session-direct`, exit 1. This is **not** a fail-open
(it correctly flags rather than silently passing) but the message is wrong — it tells the planner to
pick `team` or `main-session-direct`, and neither is true; the file is co-owned by convention. Also
checked at the `--resolve` level directly: `check-domain.sh --resolve package.json </dev/null` →
`NOBODY` then `SHARED package.json`, exit 0 — the signal reaches the caller and is thrown away there,
not lost upstream.

## F3 (LOW) — stale line-anchor, inherited from the PLAN, not introduced by the build

`check-plan-routes.py:16` and `test-check-plan-routes.py:142` cite `check-domain.sh:190-197` for the
prefix-comparison bug. At the review SHA, lines 190-197 are the `_shared_hits`/`NOBODY`-emission code
inside the `--resolve` branch — not the bug record. The actual bug documentation lives in
`glob_to_re()`'s docstring at `check-domain.sh:61-69` (confirmed by reading both ranges, and by diffing
against base `47ed11f` where `glob_to_re`/`matches` sat nested inside `domain_check()` at that same
190-197 range before T-01 moved them to module scope in this same diff). `DEC-179`'s own
`DECISIONS.md` entry correctly cites `:61-69` — the right anchor was known, just not propagated back
into the two source comments. Already disclosed by the builder (`feature.yaml` `q1_stale_anchor`),
correctly characterized as inherited from `PLAN.md:210`'s own citation rather than a build defect — I
independently confirm `PLAN.md:210` carries the same wrong anchor. Cosmetic; doesn't affect runtime
behavior. No action needed beyond what's already tracked.

## F4 (checked and cleared — not a new finding) — REQ-05 and the argv-less glob

Checked independently per the dispatch's specific ask. Confirmed: `python3 check-plan-routes.py` run
bare from a non-repo-root cwd prints `0 violation(s) across 0 plan(s)`, exit 0. This is a real,
reproducible property, matching the antipattern REQ-05's prose describes. My independent read: REQ-05
is *operationalized* by the BRIEF as SC-01..SC-04, all of which are scoped to `--resolve`
(`check-plan-routes.py` is not traced to REQ-05 by any task — `PLAN.md`'s T-02 traces line omits it).
`--resolve` itself is solid: I probed empty arg, path with spaces, absolute path, path outside the
repo, `..` traversal, `.`, and no-arg-after-`--resolve` — every case printed at minimum `NOBODY`,
never silence, matching SC-02. So `check-plan-routes.py`'s bare-invocation behavior is a real but
narrower issue than REQ-05 as scoped by the SCs, already disclosed by the builder as `feature.yaml
q6_argvless_glob` and correctly marked non-blocking today (not reachable via the one documented
invocation, `harness-spec-driven/SKILL.md:39`, which always passes an explicit path) — becomes blocking
only if a future feature promotes this to an argv-less `check-state.sh` invariant. I agree with that
call; not raising as a new finding, only confirming the measurement independently since it was asked
for by name.

## SC-08 clause 1 (invokes check-domain.sh for every path decision) — structural confirmation

Read control flow, not grep, per the dispatch's ask. Every literal `files:` entry passes through
`resolve_agents()` → `subprocess.run([CHECK_DOMAIN, "--resolve", path], stdin=subprocess.DEVNULL, ...)`
(`:52-57`). There is no entry-versus-grant comparison anywhere else in the file — `process_task` only
branches on whether `resolve_agents()` returned a non-empty list and on the `execution_mode:` token
string. Confirmed exactly one matcher (`matches()`/`glob_to_re()`) exists in the diff, at
`check-domain.sh:61-97`, and diffed the post-agent-identity section of `check-domain.sh` against base:
identical except `glob_to_re`/`matches` moved from nested-in-`domain_check` to module scope (comment at
`:325-326` says so; confirmed byte-for-byte via `diff`).

## Hook-path regression check (SC-04) — confirmed unchanged, tested via pipes not inline strings

Piped real JSON payloads into `check-domain.sh` (no `--resolve` in argv): an out-of-domain write
(`harness-backend-dev` → `docs/harness/DECISIONS.md`) → exit 2 with the expected `BLOCKED` message and
permitted-domain listing; an in-domain write (`harness-backend-dev` → `.claude/skills/harness/bin/x.py`)
→ exit 0, no stderr. Matches `test-check-domain.py` cases (g)/(h) (`:459-469`), which use the same
subprocess-with-real-JSON shape rather than an inline escaped-quote string.

## `--resolve` structural stdin-safety (SC-03) — confirmed by reading control flow

`payload=$(cat)` (`check-domain.sh:40`) sits in the `else` branch of `if [ "${1:-}" = "--resolve" ];
then ... else payload=$(cat); fi` (`:36-41`) — provably unreachable when `--resolve` is in argv, not
just empirically fast. `HARNESS_RESOLVE_PATH` is the only channel used on that branch.

## Divergence check (hazard 4) — hook fails open, `--resolve` fails closed on missing manifest

Read and agree with the design: `check-domain.sh:128-132`'s comment states the reasoning directly — the
hook's open-fail exists because blocking every write in an un-onboarded project is worse than not
enforcing (DEC-101), and that logic does not transfer to a plan-time query, where reporting `NOBODY`
on the strength of a broken/absent config would put a task in the main-session lane incorrectly. This
is the right asymmetry, not a bug.

## What I did not re-litigate

`run-unit-tests.sh`'s `SCRIPTS` array: confirmed the FEAT-08/FEAT-09 concurrency hazard PLAN.md
describes did not fire — base `47ed11f` already has `test-cost-report.py` removed (FEAT-08 merged
first per `git log`), and the diff here is a clean one-element append (12→13 entries, `git diff
--numstat` = one line changed). `run-unit-tests.sh`, `test-check-domain.py`, `test-check-plan-routes.py`
all pass locally (32 named checks total across the two new/changed test files, plus 12 unrelated
scripts), and `check-docs.sh` exits 0. DECISIONS.md's new DEC-179 entry and the DECISIONS-INDEX.md row
are accurate against the diff (cites `check-plan-routes.py:52-57` and `check-domain.sh:61-69`
correctly — the fresher, correct anchor, unlike the two stale in-source citations in F3).

## Findings ranked

1. F0 — MED — a blank `files:` field is mishandled by `check-plan-routes.py`'s `FILES_RE`; modal case
   fails safe with a misdiagnosed message, a narrower case (rare in this repo's actual authoring, 0/38
   measured) fails open. Worth fixing, not gating.
2. F1 — MED — SC-08 clause 4's behavioural proof is narrower than claimed (test-suite gap, not a live
   bug); already disclosed by harness-qa, independently reproduced.
3. F2 — MED — `SHARED`-only paths produce a misleading VIOLATION message (not a fail-open); already
   disclosed by harness-qa, independently reproduced.
4. F3 — LOW — stale `check-domain.sh:190-197` anchor in two source comments, inherited from
   `PLAN.md:210`; already disclosed, cosmetic.
5. F4 — checked, cleared as a *new* finding — the argv-less glob is real but out of REQ-05's
   SC-scoped coverage and already disclosed/accepted as non-blocking; independent measurement matches.
