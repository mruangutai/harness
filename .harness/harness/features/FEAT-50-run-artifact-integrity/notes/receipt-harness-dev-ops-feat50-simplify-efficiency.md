# Efficiency angle — FEAT-50 plan surface

**BLUF.** Actual per-write hot-path cost is negligible for both D-03 and D-05 (sub-millisecond
against the ~38 ms interpreter-startup floor `check-domain.sh:955` already pays per call), but
**neither decision states any cost figure**, despite the figure for D-03's mechanism already
existing verbatim in the code it calls. That absence is itself the finding the dispatch asked me
to make. D-05 also has one small, real, unaccounted-for redundant read the plan's own "costs
nothing" claim doesn't cover. Grading-time redundancy exists in BRIEF.md's SC evidence commands
(2 findings, both low severity). D-01 adds no measurable cost — confirmed by reading the change.

## Findings

| id | severity | element | summary |
|---|---|---|---|
| EFF-01 | med | D-03 (plan.yaml:87-96), T-03 (plan.yaml:267-322) | Hot-path cost of the new per-write worktree lookup is not stated anywhere in the plan, though it is already measured in the code it calls |
| EFF-02 | low | D-05 (plan.yaml:109-119), T-04 intent step 2-3 (plan.yaml:348-378) | The POST-named-target route pays one wholly wasted extra file read the plan's "costs nothing" claim doesn't name |
| EFF-03 | low | SC-04/SC-06 (BRIEF.md:94-100, 106-110) | Two `git show <sha>:…test-check-domain.py` reads of the identical blob, differing only in the grep after |
| EFF-04 | low | SC-01–SC-07 (BRIEF.md:77-116), T-02/T-05 verify (plan.yaml:222-227, 406-411) | The same whole-file suite is re-invoked as evidence once per criterion (6× `test-check-domain.py`, 3× `test-validate-digest.py`) when one execution per file already proves every case |

### EFF-01 — D-03/T-03: hot-path cost measured, but not recorded in the plan

`check-domain.sh:1046`'s own drift-hazard comment and `harness_boundary.py:138-156`'s docstring
already carry the number this decision needs: `linked_worktrees` measures **0.371 ms/call at 5
linked worktrees** (`harness_boundary.py:153`), i.e. **+0.22 ms marginal per governed write**
against a prior 0.147 ms baseline, scaling linearly with worktree count — "no git subprocess,
no segment counting, no regex" (`:122`, `:145`). `real()` (`:258-273`) is two `os.path.realpath`
calls, no subprocess, no directory walk. Against the file's own recorded ~38 ms interpreter-startup
floor per hook launch (`check-domain.sh:955`), the marginal cost is under 1%.

The ordering the intent specifies — regex match on `^\.harness/[^/]+/features/([^/]+)/` **before**
calling `linked_worktrees` — does correctly bound *when* the lookup runs: only writes whose target
matches that path shape, and only inside the already-`_run_domain`/ALLOWED governed-agent branch
(plan.yaml:280-281, 307-311), pay it at all. A write to `.claude/skills/harness/bin/*.py` never
reaches the lookup.

**Failure scenario.** Neither D-03's `because`, T-03's intent, nor T-03's `verify` cites this
number or this bound. A future reader deciding whether to add a second per-write check to
`check-domain.sh` — the same hot path, run on every `PreToolUse:Write|Edit` by every agent in
every project — has no recorded budget to weigh a new addition against; each addition is measured
against nothing, and `check-domain.sh`'s own per-call cost creeps unrecorded, addition by addition,
until the interpreter-start-up-dominated cost this file's earlier authors were careful to protect
(`:952-955`) is no longer the dominant term and nobody can point to when that happened.

**Alternative.** Add one sentence to D-03's `because` clause (or T-03's intent) citing the existing
measurement: *"`linked_worktrees` measures 0.371 ms/call over 5 worktrees and `real()` adds two
negligible realpath calls (`harness_boundary.py:138-156,258-273`); bounded to writes matching the
feature-path regex inside the already-ALLOWED governed branch, this is under 1% of the ~38 ms
interpreter-startup floor `check-domain.sh` already pays per hook launch."* No code change; a
one-sentence addition to the decision record.

### EFF-02 — D-05/T-04: the plan's "costs nothing" is true for the sweep, not for the third route

`check-domain.sh` has exactly one call site of `shape_problems()` (`:1547`), fed by `targets` built
three different ways: PRE-Write (`:1367-1370`, unconditional), POST-named-target for
Write/Edit/NotebookEdit (`:1372-1386`, gated by `has_shape_rules`), and POST-Bash-no-target — what
the file's *own* comment (`:1389`) calls "the sweep" — built from `SWEEP_GLOBS` alone (`:1417`),
never touching `has_shape_rules`/`SHAPE_PATTERNS`. Confirmed: adding `RE_RUN_DIGEST` to
`SHAPE_PATTERNS` cannot widen the sweep's candidate set — it is bounded by `SWEEP_GLOBS`
independently, exactly as D-06/T-04 step 2 intends.

But T-04's intent (plan.yaml:376-378) says the branch is "reached from BOTH call sites of
shape_problems -- the pre route and the sweep," and that on the sweep "the content passed in IS
the file's own content, so the prefix test holds trivially... That is intended and is why step 2
costs nothing." This enumerates two routes and misses the third: **POST-named-target**. On that
route, `has_shape_rules` already triggers a full read of the just-written `digest.md`
(`:1380-1381`) to build `_text`, which is then passed to `shape_problems` as `content` — and the
new `RE_RUN_DIGEST` branch (per step 3's intent) does its *own* independent read of the same path
to fetch the "existing" content for the prefix compare. Since this is POST, disk content and
`content` are identical text (the write already landed), so the compare is exactly as trivial as
the sweep's — but it costs a second `open()+read()` of the same file the route already holds in
memory. Net: one legitimate `digest.md` write costs 3 total reads across the two launches (PRE: 1
old-content read for the real enforcement; POST: 2 reads of the identical new content), where 2
would do.

**Failure scenario.** Magnitude is trivial for a small `digest.md` (well under a millisecond,
nowhere near hot-path scale — digest writes happen a handful of times per run, not per tool call).
But the plan's own accounting is incomplete: "step 2 costs nothing" is read as the full cost
statement for D-05, and it silently omits a real, always-triggered, always-wasted read on the one
route that fires on every legitimate digest write forever. If a later feature adds more
self-comparing `SHAPE_PATTERNS` branches following this one as precedent, each inherits the same
doubled read on its POST-named-target route, uncounted every time because the precedent's own
text said "costs nothing."

**Alternative.** Amend T-04 intent step 3 to note the POST-named-target route explicitly and
either (a) skip the disk re-read there by threading the already-read PRE-old-content or POST-new-
content through as a parameter instead of re-opening the file inside `shape_problems`, or (b) if
leaving the redundant-but-correct read is accepted as simpler, correct the exemption's wording:
*"step 2 costs nothing on the sweep; the POST-named-target route pays one extra read of the file
it just wrote, always compared to itself, which is a cheap no-op rather than a bug."* Either is a
plan-text change; (a) additionally removes the wasted read.

### EFF-03 — SC-04/SC-06: same blob, same commit, two `git show` reads

BRIEF.md:99-100 and BRIEF.md:109-110 both run
`git show <review_sha>:.claude/skills/harness/bin/test-check-domain.py | grep -q '...'` — identical
file, identical commit, differing only in the grep pattern (`feature-checkout-red` vs
`digest-clobber-red`). Each `git show` is an independent object-store lookup and decompression of
the same blob.

**Failure scenario.** Grading SC-04 then SC-06 in sequence re-fetches and re-decompresses the same
git blob twice for zero additional signal; a third SC added later against the same file (there is
already headroom for one, given T-05 adds seven cases to this one file) would triple it, and
nothing in the plan currently catches this as an accumulating one-file-per-check pattern.

**Alternative.** State one combined evidence note for SC-04 and SC-06: capture the blob once and
grep it twice, e.g. `t=$(git show <review_sha>:.claude/skills/harness/bin/test-check-domain.py); printf '%s' "$t" | grep -q 'feature-checkout-red' && printf '%s' "$t" | grep -q 'digest-clobber-red'`.

### EFF-04 — SC-01–SC-07 and their matching task verifies re-run whole files as evidence

Counted directly from BRIEF.md and plan.yaml `verify:` blocks (not from running anything):
`test-check-domain.py` is named as the evidence command **6 times** — SC-03, SC-04, SC-05, SC-06,
SC-07, and again in T-05's own `verify:` (plan.yaml:406-411) — each a bare
`python3 .../test-check-domain.py`, identical command, identical file, for five distinct
sub-claims a single execution's case results already jointly cover (T-05's intent adds all seven
new cases into that one file). `test-validate-digest.py` is named **3 times** the same way (SC-01,
SC-02, T-02's own verify at plan.yaml:222-227).

This is grading-time cost, not hot-path — SKILL.md is explicit that a suspected-slow suite run
"may be a fraction of a second," and I did not run either file (out of scope for this dispatch), so
I state the pattern, not a measured duration. The pattern itself — the same whole-file command
repeated once per criterion when a targeted case or one shared run would bind equally — is exactly
what SKILL.md's plan-surface efficiency guidance names as flaggable, distinct from SC-10's
deliberate full-suite boundary runs (not flagged; that is the evidence the boundary exists).

**Failure scenario.** A grading pass that executes BRIEF.md's `command:` field literally,
criterion by criterion, launches the Python interpreter, imports `harness_yaml`/`harness_boundary`,
and re-registers T-05's worktree fixtures five (or six) separate times for `test-check-domain.py`
alone, for output that is identical each time; any future increase in that file's fixture cost
(e.g. more worktree setup per case) multiplies by the same six, unrecognized as redundant because
each SC's command was written to look self-contained.

**Alternative.** Replace the five repeated `command:` lines under SC-03–SC-07 with one shared
line: *"SC-03 through SC-07 are graded from one execution of `python3
.claude/skills/harness/bin/test-check-domain.py`; each criterion's evidence is that run's own exit
code plus the presence of its named case in the run's output."* Apply the same collapse to
SC-01/SC-02 for `test-validate-digest.py`.

## Not flagged (read, found clean or out of scope)

- **D-01/T-01 (validate-digest.py hook).** Read the intent in full (plan.yaml:170-209): it replaces
  one truthiness branch with a presence discriminator using the same sentinel-read pattern, no new
  I/O, no subprocess, no additional file read. **No measurable cost added to `SubagentStop`.**
- **SC-10's two full-suite runs.** Deliberate boundary evidence per SKILL.md's own carve-out — not
  flagged.
- **Sweep widening.** Confirmed `SHAPE_PATTERNS` and `SWEEP_GLOBS`/`_SWEEP_PATTERNS` are read by
  disjoint code paths (`has_shape_rules` only at `:1377`; the sweep's `targets` built only from
  `SWEEP_GLOBS` at `:1417`) — adding `RE_RUN_DIGEST` to `SHAPE_PATTERNS` alone cannot widen the
  Bash-sweep's candidate set. D-06/T-04 step 2's core claim holds; only the exemption's *wording*
  in EFF-02 is incomplete.
- **T-03's placement/ordering constraints** (regex match before lookup, inside `_run_domain` only)
  — read and confirmed correctly bounding; not itself a cost defect.

## What I read

`.agents/skills/harness-simplify/SKILL.md` (EFFICIENCY section); `plan.yaml` (full, all 7 tasks, 8
decisions); `BRIEF.md` (full, all 14 SCs); `.claude/skills/harness/bin/harness_boundary.py:102-320`
(`checkout_relative`, `linked_worktrees`, `real`, `resolve_fleet`); `.claude/skills/harness/bin/check-domain.sh:919-1058` (`SWEEP_PATTERNS`, `SHAPE_PATTERNS`, `has_shape_rules`, cost-measurement
comment block) and `:1359-1553` (both `targets`-construction routes, the sweep, and the single
`shape_problems` call site).
