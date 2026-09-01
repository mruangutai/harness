# Code review — cycle 3 — FEAT-41-one-station-vocabulary — review_sha 5dc77108

**Both stages ran.** Stage 1 (spec compliance, SC re-measurement) and Stage 2 (code quality, fail-open
hunt via mutation) both completed. **Verdict: FAIL** — two HIGH, independently exploitable evasions of
the two write-integrity guarantees this feature exists to deliver (REQ-03/REQ-05).

All work done against a `git archive 5dc77108` extraction in `/tmp` (outside the worktree). **The
worktree itself was never written to** — verified clean (`git status --short` and `git diff --stat`
both empty) after every mutation; all scratch copies removed.

## HIGH — 1: a raw Bash write can empty a real plan's `tasks:` and escape both guards (item 1b)

`check-state.sh:201`'s T-19 exemption (`if not doc["tasks"]: continue`) is **correctly scoped against
every route `plan-merge.py` exposes** — I read all five verbs (`apply`/`add-tasks` are add-only splices,
`set-task-station`/`set-feature-station` rewrite one line, `sign-approval` touches only the approval
block) and none can shrink `tasks:`. `load_plan` also can't be tricked via a duplicate `tasks:` key —
`harness_yaml.py`'s loader raises `DuplicateKeyError` on that. **1(a) answer: no, not via any mediated
route.**

But Bash is explicitly *not* mediated — `check-domain.sh:926-929`'s own comment says so: "the PostToolUse
Bash route is the ONE route this rule cannot deny before the fact... the sweep is where a dead station
word gets caught after it lands." I read that sweep (`check-domain.sh:1158-1188`, `SC-06`'s mechanism):
it validates `_top`/`_t.get("status")` against `MANDATED_STATIONS` — **it never inspects whether `tasks:`
shrank or emptied.** A shell write that keeps the approval block, keeps a legal `status:`, and replaces
`tasks:\n  - id: T-01...` with `tasks: []` produces zero `_bad` entries — the sweep is silent both before
and after.

**Proved end-to-end** with the real `check-state.sh` and the real sweep logic (not a paraphrase): a fixture
with a signed, task-bearing plan and a `STATE.md` referencing a dangling `T-99` correctly reports
`VIOLATION ... STATE.md references T-99, which is absent from its plan.yaml.` After overwriting `plan.yaml`
in place (simulating the shell write) to `tasks: []` with the same approval block and same `STATE.md`, that
same violation **disappears completely** — full output confirmed only unrelated fixture-scaffolding
violations remained, nothing about the now-orphaned approval or the dangling task ref. `station_of()`-based
checks (line 977) still fire on an illegal top-level `status`, but nothing checks task-list shrinkage.

**1(c):** `case_inv34_a_real_plan_is_still_checked` (`test-check-state.py:3771`) IS vacuous **with respect
to the exemption line itself** — mutation-confirmed: removing the exemption line (`check-state.sh:201-202`)
entirely leaves `(inv34.d)` green, unchanged (only `(inv34.c)` goes red, as expected). It is *not* fully
vacuous — mutating the condition to `if True: continue` (total collapse) does turn `(inv34.d)` red. So the
suite catches gross regression but has **no case exercising "a plan whose `tasks:` was emptied out from
under a still-live approval/STATE.md record"** — exactly the state a raw shell write can now produce, and
exactly what the exemption cannot tell apart from a legitimate station-only record. **1(d):** confirmed
INV-34 fires correctly when `plan.yaml` is deleted, silent when present — that half works.

**Failure scenario:** an agent (backend-dev, dev-ops, anyone with Bash) runs a one-line Python/`sed`
edit against a signed, task-bearing `plan.yaml`, sets `tasks: []`, leaves `approval:` and `status:`
untouched. `check-state.sh` goes silent on both the approval-signed check and the STATE.md task-id check
for that feature from then on; `check-domain.sh`'s SC-06 sweep never flags it. `check-state.sh:201`,
`check-domain.sh:1176-1183`.

## HIGH — 2: unquoted command substitution bypasses `plan-sign-gate.py`'s IFS fix (item 4)

C2-03 closed **braced** parameter expansion (`${IFS}`) as an IFS-whitespace-injection vector into
`plan-merge.py sign-approval`. I tried the full battery requested — `$'\x20'`, `${IFS:0:1}`, `${IFS-x}`,
`$\{IFS\}`, backslash-newline, `"${IFS}"`, `${!x}`, `$((...))`, `{a,b}`, `~` — against the real gate script
end to end, **and against real bash** to check each candidate actually splits words:

| form | gate exit | real bash splits tool/verb? |
|---|---|---|
| `${IFS}` / `${IFS:0:1}` / `${IFS-x}` / `"${IFS}"` / `${!x}` | 2 (denied) | yes — correctly caught |
| `$'\x20'`, `$\{IFS\}`, `$((1+1))`, `{,}`, `~`, `\`+newline | 0 (allowed) | **no** — each glues into one non-matching token; verified with `set --` under real bash (argc=1 or a doubled-glued word), so none of these are live evasions |

None of the requested forms bypass the gate for a working reason. **But testing the parallel mechanism
the fix's own docstring doesn't mention — unquoted command substitution — found a real one:**
`plan-merge.py$(printf ' ')sign-approval` splits into exactly two argv words in real bash
(`set --` proof: `argc=2`, `[plan-merge.py]` `[sign-approval]`), because unquoted `$(...)` output undergoes
IFS word-splitting exactly like `${IFS}` did before the fix. `as_bash_reads_it`'s `BRACED_EXPANSION` regex
(`plan-sign-gate.py:127`) only matches `\$\{[^{}]*\}` — it does not touch `$(...)`. Ran the **exact string**
through the real `plan-sign-gate.py` with a full `agent_type`/`tool_input.command` payload: **exit 0, empty
stderr — not denied.** `cmd_sign_approval` (`plan-merge.py:833`) has no agent-identity check of its own;
this gate is the sole enforcement DEC-120/REQ-05 rely on. `test-plan-sign-gate.py` has zero cases mentioning
`$(` or command substitution — this class was never exercised.

**Failure scenario:** any agent with Bash access runs
`python3 plan-merge.py$(printf ' ')sign-approval --file <plan.yaml> --by <name> --date <date>` and writes
a real, reload-verified approval signature nobody authorized — the exact thing REQ-05 says only the main
session may do. `plan-sign-gate.py:127,133`.

**False positive, also checked (item 4's second half):** the adjacency scanner already flags ordinary prose
that puts the literal words `plan-merge.py sign-approval` next to each other (e.g. an echoed sentence) —
that is a pre-existing, documented limitation of the token/`RAW_SIGN` design, not something the `${IFS}`
substitution itself introduces. No new false positive traced to the C2-03 change specifically.

## MED — C2-02's "unresolvable link fails CLOSED" claim is false; dead code, not a proven bypass (item 3)

Prediction A confirmed empirically: `os.path.realpath` (Python 3.14, non-strict/default mode) does **not**
raise `OSError` on a broken symlink or a self-referential loop — it resolves as far as possible and
returns a path. So `_resolved_rel`'s `except OSError` (`check-domain.sh:1505-1507`) is unreachable in
ordinary operation, and the fail-closed branch at `:1549-1550` (`if os.path.islink(path): return as_typed`)
is dead code. The docstring's claim "`realpath` follows a chain of ANY length, and raises on a loop"
(`:1500`) is factually wrong.

I could not turn this into an actual write bypass: every broken-symlink and self-loop case I constructed
(including a loop with real trailing path components past it) still resolves, via `os.path.realpath`, to
the *correct* target — so `RE_PLAN_YAML.match(resolved)` or `_hardlink_plan` still catch it the same way a
working symlink would be caught. Rating MED, not HIGH: real defect (wrong doc, unreachable "protection"),
no demonstrated consequence. `Prediction B` (worktree/cwd root confusion) does not apply as framed — `root`
in `check-domain.sh` is `harness_boundary.root_from_script`, pure arithmetic off the script's own on-disk
location, never cwd; verified by reading `harness_boundary.py:41-48`.

## Verified — no finding (items 1a/1d, 2, 5, 6)

- **Item 2:** `load_plan` (`harness_yaml.py:321-342`) does not validate a station-only plan's `status`
  against the vocabulary — `status: garbage-not-a-station` loads clean. But it's caught **downstream, by
  two independent mechanisms**: `check-state.sh:977` (`if _status not in STATUS_ORDER`) and
  `gh_board.py:271` (`_parent_station` raises `FleetError`) — both confirmed by fixture run
  (`status: banana` → `VIOLATION ... records station 'banana', which is not in the station vocabulary`).
  All the "carries no fact" values (`0`, `false`, `'   '`, `null`, `[]`) are correctly rejected at
  `load_plan` itself by the existing `not str(...).strip()` guard.
- **Item 5:** spot-checked 6 of 12 backfilled directories (BUG-1030, BUG-1055, BUG-1071, FEAT-01,
  FEAT-08, FEAT-09) against `origin/main`'s `feature.json.status` — every one is a faithful case-lowered
  copy, none re-adjudicated. BUG-1030 specifically confirmed `Review`→`review`, not `abandoned`.
- **Item 6, SC-01:** literal command as stated has a caveat — `_STATION_KEYS` still has 54 hits in the
  tracked tree (`--exclude-dir=__pycache__`), but **all 54 are narrative prose in `notes/`/observations
  files** discussing the retired constant historically; zero hits in any `.py`/`.sh`/`.json` source file.
  Reporting rather than silently accepting the handoff's "no longer exists anywhere" — read maximally
  literally it's false; read as "no source declares a second vocabulary" it's true and verified.
- **SC-02:** re-ran verbatim, 0 lines. **SC-03:** re-ran the exact Python assertion, exit 0. **SC-04:**
  re-counted `set_station(` calls outside tests/def: exactly 4 (`board_lifecycle.py`×2, `board-station.py`,
  `gh-sync.py`), matches. **SC-08:** 0/47 `feature.json` carry `status`; schema confirmed 10
  properties/7 required/`additionalProperties: false`. **SC-09** (inspection): `FEAT-40`'s `plan.yaml` at
  `review_sha` carries `status: done` at top level (confirmed); a full `check-state.sh` run over the whole
  tree produced 709 lines, zero `INV-26` lines. **SC-14:** exactly 3 `FEAT-41` mentions in
  `DECISIONS.md`, one each inside `DEC-182`/`DEC-191`/`DEC-203`, none struck.

## Code grade (Stage 2)

`code-grade.py --base $(git merge-base origin/main 5dc77108) --head 5dc77108`: **0 gated HIGH**, matches
the handoff's claim. 9 grade-2 records, all `SEVERITY: med`, none blocking:
`plan-merge.py:_verify_spliced`, `plan-merge.py:_task_status_line`, `plan-merge.py:cmd_sign_approval.transform`,
`plan-sign-gate.py:denies` (notable — this is the function with the command-substitution gap above; its
complexity is a symptom of accreting ad-hoc evasion branches, not the cause), plus 5 in
`test-check-domain.py`/`test-plan-merge.py`. Reason for not-must-fix on all 9: pre-existing pattern in this
codebase (verb tables, splice/verify pairs, adversarial-fixture test functions) already carries this shape
elsewhere in the tree; none regressed past its own bar newly in this diff by more than the grader's
tolerance, and grade 2 is non-blocking by design.

## must_fix

1. `check-state.sh:201` / `check-domain.sh:1158-1188` — extend the SC-06 sweep (or a new invariant) to
   flag a `plan.yaml` whose `tasks:` list shrank versus its own git history, or gate `tasks:` emptying the
   same way `set-feature-station` gates station values — a shell write must not be able to manufacture a
   station-only-shaped document out of a real, signed plan.
2. `plan-sign-gate.py:127` — extend `as_bash_reads_it` (or add a sibling check) to neutralise unquoted
   `$(...)`/backtick command substitution the same way `${...}` is neutralised; `$(printf ' ')` and
   equivalents currently forge a real signature.

## Open questions

- None blocking review completion. Whether items 1 and 4 warrant reopening T-09/T-08's task or a fast-follow
  bug is the operator's/eng-lead's call, not mine to decide here.
