# Main-session-direct implementation packet — panel c7 remedies R-1/R-2/R-3 — BUG-1309

**Implementation can begin immediately.** Three code edits and six test cases, all inside the DEC-174
enforcement carve-out, all now specified by the amended signed plan. Nothing here waits on the one
open operator question (SC-04 traceability) — that question is about which criterion GRADES the
ambiguity deny, not about what the code must do.

**Who runs this: the main session, by hand.** No squad may execute any of it (`plan.yaml` lanes rows
34-36, 47-49, 73-75; T-04 and T-05 both carry `execution_mode: main-session-direct`).

**Checkout:** `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1309-mirror-build-entry`,
branch `feat/BUG-1309-mirror-build-entry`. Do not move HEAD.

**Authority for every requirement below is the amended plan, not this note.** Where the two differ the
plan wins: T-05 `intent` steps 2, 4 and 6, T-04 `intent`'s non-era notice and its new case. The plan
was amended today in two passes (`notes/research-BUG-1309-planamend-c13.md`, `-c13b.md`); line
numbers move, so navigate by task id and field name.

---

## Edit A — `merge-gate.py` `git_merge`: flag-aware subcommand walk (R-2 / PANEL-2)

**File:** `.claude/skills/harness/bin/merge-gate.py`, `git_merge` at lines 44-48.

**Today** (the defect, verbatim): `args = [word for word in rest if not word.startswith("-")]` then
`args[0] != "merge"`. `git -C <dir> merge X` yields `args[0] == "<dir>"` → `None` → **silent allow**
regardless of the receipt state. No deny, no stderr, no audit trace.

**Required:** walk the tokens after the `git` token **in order**. At each token:

| token | action |
|---|---|
| value-taking git global, value in the NEXT token (`-C <dir>`, `-c <k=v>`, `--work-tree <d>`, `--git-dir <d>`, `--namespace <n>`, `--config-env <k=e>`, `--super-prefix <p>`) | skip it **and** the next token |
| value-taking git global with the value ATTACHED (`-C<dir>`, `-ck=v`, `--work-tree=<d>`, `--git-dir=<d>`, any `--long=value`) | skip that token alone |
| any other `-`/`--` option (`--no-pager`, `-p`, `--bare`, `--literal-pathspecs`, …) | skip that token alone |
| first non-option token | it **is** the subcommand — this and only this is tested against `merge` |

Return `("git", <the token after the subcommand>)` exactly as today; `None` if the subcommand is not
`merge` or the walk runs out. The globals list is a **class with examples** per the amended T-05 step
2 — do not read the enumeration as closed, and do not re-derive it from `git --help`.

**One judgement the plan leaves to you, decide it this way:** `--exec-path` has a bare form that
prints and exits, so treat it as value-taking **only** in its attached `--exec-path=<p>` spelling.
Consuming a following token for the bare form would swallow `merge` and reintroduce the exact silent
allow this edit closes.

**Out of scope, by ruling R-2:** shell-variable indirection (`B=x; git merge $B`) and nesting past
`nested_merge`'s depth cap. Both stay backlog rows. Do not widen the task.

---

## Edit B — `merge-gate.py` record attribution: deterministic ambiguity deny (R-1 / PANEL-1)

**File:** same, `feature_for` at lines 98-109 and its caller in `main()` at line 134.

**Today:** `feature_for` returns the FIRST `glob.glob` match. `glob.glob` guarantees no ordering, so
two well-formed dict records legitimately carrying the merge's branch decide the merge by
directory-iteration luck — bypass in one direction, misattributed deny in the other, reproduced 5/5
both ways (`notes/review-harness-security-reviewer-c7.md`).

**Required** (amended T-05 step 4):

1. **Attribution is unchanged.** A record owns the merge only if it is readable, is a JSON object,
   and its top-level `branch` equals the resolved head branch. Every other record — unreadable,
   non-object, or matching a different branch — is **skipped and can never impose a refusal**.
2. Collect **all** owners rather than returning the first.
3. **Zero owners** → today's behaviour exactly: `return None, None`, caller exits 0 (with the
   existing gh-failure stderr line when the gh route failed).
4. **One owner** → today's behaviour exactly. Nothing downstream changes.
5. **Two or more owners** → **DENY**, deterministically, through step 6's deny shape (the same
   `deny()` JSON object), **before** the era gate and before `github.build_entry`, the era set or
   `recovery_command_for` is consulted at all. No receipt command clears a duplicated branch claim,
   and the era rule presupposes one identified feature.
   The reason must name **every** claiming feature directory id, in a **stable sorted order**, and
   the resolved branch, and must say the duplicated top-level `branch` field has to be corrected
   before this merge can be decided. Wording is yours within those bounds; this satisfies them:
   `merge-gate: <branch> is claimed by more than one feature record (<id>, <id>, …), so this merge
   cannot be attributed to one feature. Correct the duplicated top-level "branch" field in those
   feature.json records before merging; no receipt command clears this.`

**The bound that a previous cycle broke — do not break it again.** Cycle 11's `473d82cb` made an
unrelated malformed record deny a merge on a branch that owed nothing; panel c5 failed it and
`894adc0f` scoped it back. **Ambiguity means two or more OWNERS, never one owner plus noise.** The two
existing cases at `tests/integration/test-merge-gate.py:128-150` — *"unrelated non-object feature
record does not block healthy merge"* and *"no-record branch ignores unrelated malformed record"* —
are the fence. They must stay green **unmodified**.

**Watch the seed variable.** `main()` sets `feat = "this feature"` before the try block and the bare
`except` interpolates it. An ambiguity deny raised before `feat` is assigned must not fall into that
handler and print `could not evaluate this feature's Build-entry receipt`.

---

## Edit C — `gh-sync.py` non-era recovery notice derives its command (R-3 / PANEL-3)

**File:** `.claude/skills/harness/bin/gh-sync.py`, `_build_entry_recovery_notice`, non-era branch at
lines 1386-1389.

**Today:** prints `…Build proceeds, the MERGE is refused until gh-sync.py open records opened`
unconditionally, while for the same feature in the same state
`feature_schema.recovery_command_for(feat_dir)` returns `recover-terminal` and `merge-gate.py:152-154`'s
own deny prints `recover-terminal`. Following the notice runs `cmd_open`, whose `_open_sync_task`
skips only `abandoned` or already-recorded tasks — so a `done` task with no recorded issue gets a real
GitHub sub-issue created for finished work.

**Required** (amended T-04 `intent`), two clauses and nothing more:

- **(a)** when `recovery_command_for` returns `recover-terminal`, the emitted line names that command,
  carries ` --yes`, and contains **no `open` token in any form** — not `gh-sync.py open`, not
  `records opened`, not a description of what `open` would do;
- **(b)** when it returns `open`, the sentence that ships today is **retained verbatim**:
  `gh-sync: build entry is recovery-required for <feature-dir>; Build proceeds, the MERGE is refused
  until gh-sync.py open records opened`.

**No second hardcoded string.** Pinning a literal command is the defect. Call the classifier — the
same one three lines above already calls — and name what it returns. The era-exempt half of the
function is untouched.

---

## Tests — six cases, all main-session-direct

### `tests/integration/test-merge-gate.py` — five new cases

Use the file's existing `fixture()` / `gate()` / `check()` helpers and its naming convention. Append
after the existing cases; **edit none of them.**

1. **`T-05 duplicate valid records claiming the branch deny naming both`**
   `fixture()` (owner `FEAT-9001-fixture-non-era`, `build_entry` absent → owes a receipt); add a
   second directory, e.g. `FEAT-9002-fixture-duplicate`, whose `feature.json` is a well-formed dict
   with the **same** `branch: feature/test` and `build_entry: "opened"`. Run `git merge feature/test`.
   Assert `decision == "deny"` **and** both feature ids appear in the reason **and** the reason names
   no `gh-sync.py` recovery command. Run the gate **twice** and assert the reason is byte-identical —
   that is the determinism the finding is about, and a first-match implementation passes a
   single-invocation assertion by luck.
2. **`T-05 single owner plus unrelated malformed record still allows`**
   One owner whose `build_entry` is `"opened"` (owes nothing), plus a second directory whose
   `feature.json` is `[]`. Assert `decision is None`, exit 0. This is the discriminator: an
   implementation counting unreadable records as owners produces an ambiguity deny here.
3. **`T-05 git -C global flag merge is still detected`** — `gate(f"git -C {root} merge feature/test")`
   against an owing fixture. Assert `decision == "deny"`. Fails on today's code.
4. **`T-05 git -c config global flag merge is still detected`** —
   `git -c core.pager=cat merge feature/test`. Assert `decision == "deny"`.
5. **`T-05 git --work-tree global flag merge is still detected`** —
   `git --work-tree {root} merge feature/test`. Assert `decision == "deny"`.

The names are **gated verbatim** by T-05's `verify` (19 names) — it greps `ok    <name>`, so a
renamed case is a red gate.

### `tests/integration/test-gh-sync.py` — one new case

6. **`T-04 recovery-required non-era recover-terminal horn names the derived command`**
   A **non-era** fixture — directory name `FEAT-9001-fixture-non-era` or `BUG-9001-fixture-non-era`,
   never a real feature id, which is in the frozen era set and would invert the case — with
   `github.build_entry: "recovery-required"` and a `plan.yaml` on the **recover-terminal horn**
   (`status: review` or `done`, or any task `status: done`; which is your choice, the case asserts the
   horn, not a fixture shape). Run the same `start-task` path the sibling cases run. Assert: exit 0;
   the card write is attempted; the emitted stderr build-entry line names `recover-terminal`, carries
   ` --yes`, and contains **no** `open` substring in any form (which also excludes `opened`). Then
   assert **agreement**: call `feature_schema.recovery_command_for` on that same fixture directory and
   assert the command named in the line **is the string it returned**. A second hardcoded expected
   command is a rejected implementation — agreement with the classifier is the property under test.

**Host file is the integration suite, not `tests/unit/test-gh-sync-build-entry.py`.** T-04's `verify`
greps the integration runner's `ok    <name>` format (`test-gh-sync.py:733-739`); the unit runner
prints `PASS <name>`, and T-04's `files` lists only the integration file. A unit-hosted case makes
T-04's verify permanently unpassable.

---

## Verification — run exactly these, in this order

```
cd /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1309-mirror-build-entry
python3 tests/integration/test-merge-gate.py          # expect 19 ok lines, "ALL PASSED", exit 0
python3 tests/integration/test-gh-sync.py             # expect the six T-04 names among ok lines
python3 tests/unit/test-gh-sync-build-entry.py        # must stay green — Edit C's sibling coverage
python3 tests/unit/test-omp-hooks.py
python3 .claude/skills/harness/bin/merge-settings.py . --check \
  --template .claude/skills/harness/templates/settings.snippet.json   # 'all 9 prerequisites present (8 hooks'
```

Then run **T-05's and T-04's `verify` blocks verbatim** out of `plan.yaml`; each must print
`VERIFY-PASS`. Those blocks, not the bare test invocations, are what the qa gate re-runs.

**Red-before-green is cheap here and worth taking:** cases 1, 3, 4, 5 and 6 all fail on the current
code. Run the two new test files **before** the source edits and keep the output — it is the
discrimination evidence SC-03/SC-07 were amended to require, and it costs one command.

If you run the suites from inside an agent tool, prefix with `env -u HARNESS_AGENT_TYPE`: the tool's
environment leaks into test subprocesses and reddens the plan-merge approval checks as a phantom
failure.

---

## The GitHub mirror writes for this segment are YOURS, not the orchestrator's

`references/github-mirror.md:42,44`: the owner of a task-start and of a phase-transition sync is
decided **by `execution_mode`** — the main session for a `main-session-direct` one. This whole segment
is main-session-direct, so the orchestrator has deliberately run **no** `gh-sync.py` command. The plan
side is already recorded (`plan-merge.py set-task-station` T-04/T-05 → `building`,
`set-feature-station` → `building`), which is what those commands require to have happened first.

`check-state.sh` INV-26 is therefore RED on eleven rows for this feature right now. Two are yours to
clear in the same act as the work:

```
python3 .claude/skills/harness/bin/gh-sync.py start-task <feature-dir> T-04
python3 .claude/skills/harness/bin/gh-sync.py start-task <feature-dir> T-05
python3 .claude/skills/harness/bin/gh-sync.py status <feature-dir> building
```

with `<feature-dir>` = `.harness/harness/features/BUG-1309-mirror-build-entry`, and the station
argument **lowercase** — `gh-sync.py` refuses anything else. The mirror is never a gate: a failure
here is reported, never a reason to stop.

The parent row is cleared by that third command: at `ea0bdd6b` the plan read `status: review` and the
board agreed, so that row is new today and is the mirror catching up with the station move. The other
seven rows (T-01..T-03, T-06..T-09 reading `review` while the plan says `done`) are **pre-existing** —
they predate today's station moves, nothing closes a task sub-issue mid-flight (D-23), and `ship`
writes them. Do not chase those.

---

## What must NOT change

- `tests/integration/test-merge-gate.py`'s existing 14 cases, in particular the two malformed-record
  fences (`:128-150`).
- The era-exempt branch of `_build_entry_recovery_notice`, and the `open`-horn sentence in (b).
- `plan.yaml` `approval:` (lines 3-25) — the main session's `sign-approval` verb only.
- `feature_schema.BUILD_ENTRY_ERA_EXEMPT` — one definition, read by T-04, T-05 and T-06.

## After you land it — hand back, do not proceed

Commit the code and tests (`[harness:t-04]` / `[harness:t-05]` as the existing commits do), record
both tasks `done` through `plan-merge.py set-task-station` in the same act, then return to the
orchestrator. The remaining sequence is: re-pin `review_sha` at the new tip → qa `test_matrix` re-run
→ a scoped review panel c8 over the delta → pm goal-check of the affected SCs → operator SC-10 UAT →
ship briefing.

**Three operator acts are outstanding and none blocks this implementation:**
1. **SC-04 coverage** — SC-04 under-covers the new ambiguity deny (it enumerates deny for a *single*
   feature and pins a reason shape naming one feature and a re-run command). Widen SC-04, add an SC,
   or accept it as a disclosed verification gap.
2. **`plan-merge.py sign-approval`** — the plan still reads `date: '2026-09-04'` over text amended
   today. `amend` holds the approval bytes by design; the signature is a separate act.
3. **SC-10 UAT** — `notes/uat-BUG-1309-mirror-build-entry.md`, 8 steps, must run before the worktree
   is released.
