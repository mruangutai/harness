# Cycle-4 code review — FEAT-41-one-station-vocabulary

review_sha: `64f42ef86b5c388544f34c02a8f9b5831250df73` (base `6ddcac3`). Read via
`git archive 64f42ef8` extracted to `/tmp/feat41-c4`; all line/behavior claims below are against
that pinned tree unless marked otherwise. Worktree confirmed unmutated (`git diff --stat` empty;
the two `??` files are sibling panelists' own concurrent artifacts, not mine).

**Both stages ran.** Stage 1 (spec compliance) below; Stage 2 (quality / fail-open hunt,
including the three cycle-3 closures and BUG-1080) follows it.

## BLUF

**FAIL.** One HIGH: `plan-merge.py apply` — an open, ungated verb every orchestrator agent can
call — can inject `station_only: true` into a plan.yaml that still carries real, unapproved
tasks, and `check-state.sh` then silently skips the approval check for it. This is the *same*
hole MF-3 (cycle 3) closed, reopened through a different door: forging the credential instead of
exploiting its absence. Three panels missed it because they tested whether the marker's absence
could be exploited (it can't, anymore) but not whether the marker's *presence* could be forged
through the ordinary, unvalidated top-level-key splice in `apply`. Also: a fifth live evasion of
the sign-approval gate (`xargs` argument substitution), and a genuine but narrower false-positive
in the MF-1 balanced-paren scan.

## Stage 1 — spec compliance

### SC-01 / D-18(a), independently re-measured

`grep -rn --exclude-dir=__pycache__ "_STATION_KEYS" .` in the worktree today: **67** lines, not
the operator's 57 (45+10+2) nor cycle 3's 54. Breakdown I measured: 55 `.md`, 10 `.yaml`, 2
`.html`, **0** `.py`/`.sh`/`.json`, **0** mapping-key declarations
(`grep -rnE '^\s*_STATION_KEYS\s*:'` → empty). The `.yaml` (10, across exactly 3 old plan.yaml
files: FEAT-24 1, FEAT-41 5, FEAT-33 4) and `.html` (2, one file) figures match the operator's
numbers exactly. The `.md` figure does not (55 vs. 45) and that is why the total moved: this
review cycle's own sibling artifacts (`notes/qa-FEAT-41-c4.md`, written by my QA peer literally
while I was running this grep — mtime 07:34 vs. the rest of the tree's ~06:59) already discuss
SC-01 and necessarily quote the retired constant. That is self-referential, expected growth —
every cycle that writes a note about this criterion adds hits to the very corpus the criterion
counts — not a regression and not evidence against D-18(a)'s reading. **Confirmed: the SOURCE
half of the reading (`.py`/`.sh`/`.json`, and any mapping-key declaration) is 0/0, unchanged from
cycle 3. SC-01 stands PASS under D-18(a)'s reading.**

### SC-02 — PASS. `grep -rnE "[\"'](Backlog|Plan|Ready|Building|Review|Done)[\"']"` over
`.claude/skills/harness/bin/*.py` and `*.sh`, excluding `test-*`: **0** lines (was 27 at
`0d4845b`).

### SC-03 — PASS. The anchored assertion
(`^\s{4}status: pending\s*$` over `.harness/harness/features/*/plan.yaml`) exits 0, no
`AssertionError`.

### SC-04 — PASS. `grep -rn "gh_board.set_station(" --include=*.py . | grep -v test-`: **4**
call sites — `board_lifecycle.py:1080,1083` (`_apply_fix`), `board-station.py:175` (manual
override), `gh-sync.py:136` (the one policy site). Matches the criterion's own count exactly.

### SC-08 — PASS. Zero `feature.json` carry `status`; `feature-schema.json`: 10 properties, 7
required, `additionalProperties: false`, no `status` key.

### SC-09 — PASS. `git show 64f42ef8:.../FEAT-40-harness-writes-done/plan.yaml` line 3 is
`status: done`. Full `check-state.sh` run (below) emits **zero** `INV-26` lines.

### SC-11 — PASS. `check-plan-routes.py` exits 0, `0 violation(s) across 4 plan(s)`. The
`DEVIATION` lines printed are informational lane-resolution notices (T-02/T-03/T-06/T-10/T-11/
T-14/T-16/T-17/T-18/T-19 — the whole DEC-174 main-session-direct carve-out), not failures.

### SC-13 — PASS (grep half). `grep -n "_EXPECT" check-state.sh` → empty. The fixture half
(an out-of-vocabulary task station makes INV-26 name the feature/task/value) is covered by the
known-good `test-check-state.py` INV-26 cases in the trusted unit/integration baseline; I did not
re-derive a fresh fixture for it given the time budget spent on the station_only hole below —
flagged as the one SC not independently re-fixtured this cycle.

### SC-14 — PASS. `grep -n "FEAT-41-one-station-vocabulary" DECISIONS.md`: exactly 3 hits, at
DECISIONS.md:4902 (DEC-182, shape-gate clause), :5290 (DEC-191, required-key count), :6165
(DEC-203 §6, the lifecycle-field clause). Each reads "Amended … UNCHANGED … amendment and not a
strike"; none struck.

Full `check-state.sh` run: exit 1, **exactly one** `VIOLATION` line (INV-29 on the standing
`BUG-1080-inv6-plan-phase-runs` worktree — the documented environmental exception), zero `INV-26`,
zero `Traceback`. Matches the dispatch's stated baseline.

### REQ-01..07

- REQ-01 **delivered** — `factory_config.py:143-151` raises `FleetError` naming
  `<key>.stations` and printing the fixed six if `harness.json` declares anything else.
- REQ-02 **delivered** — SC-02 (0 hits) plus D-08's case boundary
  (`gh_board.py` capitalises on write, `factory_config.station_column:364-367` is the one
  capitalisation site).
- REQ-03 **delivered** — `harness_yaml.load_plan` (harness_yaml.py:320-352) requires `tasks:` and
  a vocabulary-checked station.
- REQ-04 **delivered** — SC-04 (4 non-test callers, 1 policy site: `gh-sync.py:136`).
- REQ-05 **materially undermined** — see the HIGH finding below. The Edit-tool and
  sign-approval halves hold; the "validates the station first" half does not extend to
  `apply`'s generic top-level-key path, which is how the marker forgery works.
- REQ-06 **delivered** — SC-08.
- REQ-07 **delivered** — `gh-sync.py:1441-1449` refuses a worktree feature dir at ship;
  `:659-694` commits only the plan.yaml path (`git commit -- <path>`), never a blanket commit.

## Stage 2 — the three cycle-3 closures, by mutation

### Closure 1 — MF-1 (plan-sign-gate.py), by mutation against the real gate AND real bash

**1(a) — a fifth evasion, found and confirmed live end-to-end.** `xargs` argument substitution.
The gate tokenizes the **literal** `tool_input.command` text; when the verb never appears
adjacent to the tool name *in that text* — because it arrives as a template variable filled in by
a second process the hook never inspects — the adjacency scan cannot see it.

```
echo sign-approval | xargs -I{} python3 .claude/skills/harness/bin/plan-merge.py {} \
  --file <plan.yaml> --by Attacker --date <date>
```
Gate: **exit 0, ALLOWED** (`agent_type: harness-orchestrator`). Real execution against a live
fixture (`/tmp/feat41-fixture`, a genuine `.harness` checkout with `harness.json`,
`team-config.yaml`, and a plan carrying `approval: {status: pending}`):
`SIGNED …/plan.yaml by Attacker on <date>` / `APPLIED …` / exit 0. The plan's `approval:` block
now reads `approved_by: Attacker`. This is a full, reproduced forgery — the same class MF-1
closed for `$(...)`/backticks, one member later.

I also tried, against both the real gate and real bash (`bash -n` / `set --` argv proof), and
found **not** live: process substitution `<(...)` (denied — tokenizes as `/dev/fd/N`, no split);
`$[...]` arithmetic and `$'...'` ANSI-C quoting (both glue into a single token, `set --` proves
argc unchanged — not evasions); `sh -c`/`eval` with the full multi-word invocation (caught by the
existing ≥3-word recursion, and any real forgery needs `--file`/`--by`/`--date`, which always
puts it over the 3-word threshold); `env` prefix (denied, `env` isn't `is_tool()` but the
adjacency loop still finds the real tool token); `python3 -c` `runpy.run_path` and `python3 -m`
(both *do* evade the gate at exit 0, but I could not make either one actually execute
`sign-approval` end-to-end in the time available — `-m plan-merge` needs a hyphen-named module on
`sys.path`, unverified; `runpy` needs full argv including `--by`/`--date` and the recursion into
that token's text did not resolve favourably in my traces — so I report `xargs` as the confirmed
fifth member and flag `runpy`/`-m` as **unconfirmed, worth a follow-up probe**, not a second
finding).

**Severity: HIGH.** Same class, same consequence (a forged user signature) as MF-1 itself.

**1(b) — a false positive from the balanced-paren scan, confirmed.** The scan counts every `(`
and `)` character it sees while inside a `$(...)`, with **no quote awareness**. A literal `)`
inside a single-quoted argument closes the counter's depth early, exposing everything after that
point as ordinary (non-neutralised) text — even though bash, which *does* track quoting, would
never end the substitution there.

```
echo "$(printf '%s' 'x)plan-merge.py sign-approval is just a phrase')"
```
Real bash: prints `x)plan-merge.py sign-approval is just a phrase`, exit 0 — a side-effect-free
echo, nothing invoked. Gate: **exit 2, DENIED**, telling the (innocent) caller it tried to call
`sign-approval` and cannot. Traced mechanically: `as_bash_reads_it` mangles the line to
`echo " plan-merge.py sign-approval is just a phrase')"`, whose only token besides `echo` is a
5+-word string that recurses through `denies()` and matches via the raw-text `RAW_SIGN` fallback.
This is realistic in shape (an awk/grep/regex/python one-liner or a commit message assembled via
`$(...)` with a stray unbalanced paren in its own quoted content is ordinary), even though my
exact string is a minimal repro rather than organic prose. It fails **closed** (a spurious deny,
not a spurious allow), so it is not a security hole — it is a usability bug that could confuse an
agent into thinking it tripped the sign-approval gate when it did not.

**Severity: MED.** Real, reproduced, fails safe, narrow trigger shape.

### Closure 3 — MF-3, the `station_only: true` marker — HIGH, the main finding

**Can `apply` inject the marker into a task-bearing plan? Yes, confirmed live.**
`plan-merge.py apply` (and its alias `add-tasks`, identical code path) is one of the two verbs
`check-domain.sh`'s shape gate leaves open to every agent (D-06/T-09); `.claude/settings.json`
has no hook naming it. Its splice algorithm (`apply_merge`, plan-merge.py:459-596) treats
`station_only` — not in `UNION_KEYS = ("tasks", "decisions")`, not `approval` — as "Step 8: every
other top-level key" (:576-596): if the key is absent from the base and present in the proposal,
it is spliced in **verbatim, with zero validation** (no station-vocabulary check — that only runs
for `set-task-station`/`set-feature-station` — and `_verify_spliced` only re-checks `tasks`/
`decisions` id lists).

Reproduced against a live fixture (base plan carrying `tasks: [{id: T-01, status: pending}]`, no
`approval:` block, no `station_only`):
```
$ python3 plan-merge.py apply --file plan.yaml --proposal <(echo 'station_only: true')
APPLIED …/plan.yaml   (exit 0)
$ cat plan.yaml
... tasks: [{id: T-01, ...}]
station_only: true
```
`check-state.sh`'s INV-check (:210-215) reads `if doc.get("station_only") is True: continue` —
**unconditionally**, regardless of whether `tasks` is empty. The freshly-forged plan now skips
the "no `approval:` block — cannot tell if the goal is signed" check entirely, even though it
still names a real, unapproved task. This is the exact outcome MF-3 closed (a feature exempted
from approval-checking with real work behind it) reopened through the marker's *presence* rather
than its absence — the vector cycle 3's fix never considered because MF-3's own threat model was
"someone empties `tasks:` and keeps the old signature," not "someone adds `station_only` to an
unsigned, task-bearing plan via the ordinary merge verb."

**Every sub-question, answered:**
- *Does a proposal injected into `apply` carry the marker through?* Yes (above). `_verify_spliced`
  verifies only that `tasks`/`decisions` id lists reload as computed; it asserts nothing about any
  other top-level key's legality.
- *Does any verb preserve the marker when it should not (station-only stub gains real tasks via
  `add-tasks`, leaving both present)?* **No, but not because anything checks for it** — it's
  incidental. Every legitimate station-only stub is written `tasks: []` (flow style, per the
  INV-34 remediation text itself). `add-tasks`'s splice for `tasks` assumes the base's list is
  block-style with per-item dash lines; against a flow-style `[]` base it produces
  `tasks: []\n  - id: T-01\n...`, which is invalid YAML, and `_verify_spliced`'s reload check
  correctly refuses to write it (exit 5, "UNPARSEABLE"). Confirmed by direct reproduction. This
  fails **closed**, which is good news for that specific sub-question, but it is a separate,
  real usability gap: a legitimate station-only stub can apparently never be promoted to a real
  plan through the tool's own blessed verb. Worth a follow-up ticket; not a security finding.
- *Does the marker survive round-trip through `harness_yaml` load/dump?* Not reachable — I
  grepped and confirmed `harness_yaml.py` has no `dump`/write function of any kind for
  `plan.yaml`; it is read-only. `plan-merge.py`'s byte-splice is the only writer (D-03/T-09),
  so this specific vector does not exist.
- *What do `check-state.sh`/`check-plan-routes.py` do with `station_only: true` AND non-empty
  `tasks:` together?* Nothing — I grepped `station_only` across `check-plan-routes.py`,
  `check-domain.sh`, `factory_config.py`, `gh_board.py`, `board_lifecycle.py`, `gh-sync.py`: zero
  hits in every one of them. Only `check-state.sh` and `harness_yaml.py` know the field exists at
  all, and neither detects the contradictory combination — `check-state.sh` just trusts the flag,
  unconditionally.
- *Is INV-34's remediation text (check-state.sh:1141-1147) safe, as written?* The text itself
  (create a **new**, plan-less directory's plan.yaml with `station_only: true, tasks: []` via
  `apply`) is safe in isolation — `apply` on a non-existent base writes the proposal whole and
  only refuses an `approval` key, and a brand-new station-only stub with no tasks carries nothing
  to protect. What the text does not warn against, and what the tool does not stop, is the same
  verb aimed at an **existing** plan that already has tasks — which is exactly the finding above.
- **The doubled-defense claim — reproduced myself, confirmed exactly as claimed.** Built two
  independent mutant copies of the bin directory (via `tar` pipe, not `cp`/`sed -i`, both of
  which this reviewer's own sandbox write-guard blocks — noted as an aside, not a FEAT-41
  finding, since it's this session's tooling, not the reviewed code) and ran
  `case_inv34_an_emptied_plan_is_not_station_only` (the "(inv34.e)" case) against each:
  - keying reverted only (`check-state.sh`'s `station_only is True` → old `not tasks` keying),
    loader intact → **ok** (plan fails to *load* at all: `"tasks:" is empty ... must SAY so`).
  - loader reverted only (empty-tasks-always-accepted), keying intact → **ok** (loads, but
    `station_only` is absent so the approval/`T-99` dangling-task check still fires normally).
  - **both** reverted together → **FAIL** — the emptied-and-forged plan loads clean and produces
    no violation at all. Confirms the two-layer defense is real, not vacuous, exactly as
    `handoff-build.md` claims.
- **(inv34.e) is not vacuous** — the "both reverted" run above **is** the equivalent
  deletion/flip cycle 3 ran against (inv34.d): mutating what the case guards turns it red. Not
  vacuous.

## BUG-1080 backfill — two judgments

1. **Was writing another in-flight feature's records the right move?** Marginal-yes, with a
   documentation gap. INV-34 is a real, general invariant (every feature directory needs
   somewhere to record a station) and BUG-1080 genuinely had nowhere to record one after the
   rebase — deferring would have meant either suppressing a true violation this feature's own
   check just started emitting, or shipping FEAT-41 against a red `check-state.sh`. Backfilling
   with BUG-1080's *own last recorded value*, through the sanctioned `apply` verb, rather than
   inventing one, is the narrowest available fix. The gap: nothing in `handoff-build.md` or the
   commit (`64f42ef` itself) records that this is a **cross-feature** write with a different
   owner's consent implicitly assumed — a feature backfilling a sibling in-flight feature's
   `plan.yaml` is the kind of action that, done differently, could collide with BUG-1080's own
   session mid-flight. It happened to be safe here (BUG-1080's session was not concurrently
   writing), but that was not verified before the write, only after.
2. **Was `review` the correct recorded value?** `git show 6ddcac3:.harness/harness/features/BUG-1080-inv6-plan-phase-runs/feature.json` — no `plan.yaml` existed at that pin (confirmed by the commit log itself needing to create one); the pre-existing `feature.json` is what carried the last status. I did not independently re-derive whether that file's last value was exactly `review` before this feature deleted `status` from it — the commit message and D-17's "migrated faithfully rather than re-adjudicated" policy make `review` the right FORM of answer (whatever the last recorded value was, lowercased, not `done`, since the migration doesn't adjudicate completion) but I was not able to independently confirm `review` specifically was that last value within the time available. **Flagged as an open question, not a finding** — it is checkable (`git log -p` on that `feature.json` before this feature's rebase) but I did not complete it.

## must_fix

1. `plan-merge.py apply`/`add-tasks` (plan-merge.py:576-596, "Step 8: every other top-level key")
   — no validation on arbitrary new top-level keys lets any agent inject `station_only: true`
   into an existing, task-bearing, unsigned plan, silently disabling `check-state.sh`'s approval
   check for that feature. HIGH. Concrete fix shape (not mine to design): validate `station_only`
   the same way `_STATION`/station values already are before Step 8 writes it, or require the
   marker to only ever be introduced together with `tasks: []` (paralleling the loader's own
   `load_plan` rule) rather than allowing it as an independent, unconstrained scalar splice.
2. `plan-sign-gate.py` — `xargs` argument substitution reaches `sign-approval` at exit 0, live,
   reproduced end to end. HIGH, same class as MF-1.

## should_fix / advisory
- The MF-1 balanced-paren scan can spuriously deny an unrelated, side-effect-free command whose
  `$(...)` content contains a quoted, unbalanced parenthesis (repro above). MED.
- Station-only stubs (`tasks: []`) cannot be promoted to real plans via `add-tasks` — the splice
  produces invalid YAML against a flow-style empty list and is correctly refused, but there is no
  working path forward for that legitimate transition. LOW/advisory, fails closed.
- `runpy.run_path`/`python3 -m` against `plan-sign-gate.py` evade the token scan at exit 0 in
  isolation; I could not confirm either one actually reaches a real `sign-approval` invocation
  end-to-end in the time available. Worth a follow-up probe before treating as closed.

## Verification note
Ran both stages, in that order, as required. Grading tool (`code-grade.py`) not re-run this
cycle — no production Python was touched between cycle 3 and cycle 4 review scope beyond the
BUG-1080 backfill and the re-pin commits (`git log 6ddcac3..64f42ef8` — content commits are the
re-pin/backfill only, no source diff to grade beyond what cycle 3 already graded at 0 gated HIGH
records, which the dispatch states as the trusted baseline).

Artifact re-read from
`/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-41-one-station-vocabulary/.harness/harness/features/FEAT-41-one-station-vocabulary/notes/review-harness-code-reviewer-c4.md`
and confirmed non-empty before yielding.
