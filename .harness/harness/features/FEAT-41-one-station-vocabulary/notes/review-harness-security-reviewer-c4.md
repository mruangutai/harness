# Security review — cycle 4 — FEAT-41-one-station-vocabulary — review_sha 64f42ef8

**BOTH STAGES RAN.** Stage 1: spec compliance, every named REQ/SC re-measured live. Stage 2:
fail-open/silent-failure hunt via mutation, focused on MF-2/MF-5's NUL-crash fix (jobs a/b/c) and
an attacker's-seat pass over the `station_only` marker and the sign-approval gate.

All work done against `git archive 64f42ef8` extractions under `/tmp` (`/tmp/feat41-c4-sec`,
`/tmp/feat41-c4-mainbase` for `origin/main` = merge-base `6ddcac3`, plus disposable `shutil.copytree`
mutants for kill-tests). **The worktree was never written to** — `git status --short` shows only the
two sibling reviewers' own new note files; `git diff --stat` is empty. No tracked file touched.

## Stage 1 — spec compliance, re-measured live

- **REQ-01 / SC-01**: `_STATION_KEYS` — zero hits in any tracked `.py`/`.sh`/`.json`; 26
  narrative-prose files still mention it. Matches D-18(a)'s ruling verbatim: "no source declares a
  second vocabulary" reading holds, prose deliberately not scrubbed. **Recorded faithfully.**
- **REQ-05** (plan.yaml written only by code; agent cannot editor-write it; approval unwritable by
  an agent; only main session signs) — live-tested three ways: (1) governed agent `Edit` on
  `plan.yaml` → `DENIED`, exit 2. (2) **main session** (no `agent_type`) `Edit` on the same file →
  **also** `DENIED`, exit 2 — the shape gate binds every author including the main session, per
  D-06. (3) `plan-sign-gate.py` fed a real `plan-merge.py sign-approval …` command: with
  `agent_type` set → exit 2, refusal names both the literal `sign-approval` and the sanctioned
  route (`plan-merge.py … sign-approval`); with no `agent_type` → exit 0. **PASS, matches SC-07
  exactly** (below).
- **REQ-07 / SC-10** (`ship` refuses a doomed worktree directory, names the main-checkout path;
  terminal record committed) — ran `test-gh-sync.py` in full: **296/296 ok, zero non-ok lines,
  "ALL PASSED."** Specifically confirmed: `T-10 defect two: ship REFUSES a feature dir inside a
  worktree, exit 1` / `…names the equivalent path in the MAIN CHECKOUT` / `…it is a REFUSAL and not
  a SKIP`, and `T-10 defect one: after a successful ship the station file is CLEAN against HEAD`.
  **PASS.**
- **SC-06** (post-Bash sweep names file + offending value) — built a live fixture
  (`.harness/harness/features/FEAT-SC06-TEST/plan.yaml`, `status: not-a-real-station`) and ran
  `check-domain.sh --post` against it for real: `check-domain: OVER BUDGET (already written) —
  .harness/harness/features/FEAT-SC06-TEST/plan.yaml: plan.yaml station vocabulary… top-level
  status 'not-a-real-station' is not a station`. **PASS**, names both file and value exactly as
  required.
- **SC-07** — see REQ-05 above. **PASS.**
- **PB-07 residual** (SC-05's struck coverage: does the denial STATE THE REASON, not just the
  verb, for a payload with `agent_type` and one without) — re-checked live: the plan.yaml
  write-denial message (`check-domain.sh`) states the reason ("every station value must be
  validated against the vocabulary before it lands on disk… An editor write cannot do that") before
  the route, for every payload regardless of `agent_type`; `plan-sign-gate.py`'s `REASON` states
  the reason ("writes the approval signature, which is the USER'S and is relayed by the main
  session alone") only for the `agent_type`-present path, since the no-`agent_type` path is a
  silent exit 0 by design (main session is exempt, nothing to explain). **PB-07's residual coverage
  is materially intact via T-09's mechanism** — I did not find it weaker than PB-07 claims.

## Stage 2 — MF-2 + MF-5

### (a) Attribution — VERIFIED, operator's correction is TRUE, cycle 3's attribution was WRONG

Built a fixture that reaches `classify()` on `origin/main` (the trap the dispatch names: a fixture
missing `.harness/team-config.yaml` never reaches `_run_domain`, so `classify` is unreached and the
crash cannot occur there — confirmed by reading the gating: `_run_domain = _domain_phase`, and
`_domain_phase` requires `agent_type.startswith("harness-")`, a `target`, and a readable manifest).
Fix: used the **real, full `team-config.yaml`** from each archive extraction as the fixture root
(`/tmp/feat41-c4-mainbase`, `/tmp/feat41-c4-sec`), so the manifest genuinely parses and `classify`
is genuinely reached.

Payload: `agent_type=harness-orchestrator`, `tool_name=Write`,
`file_path="notes/evil\u0000.md"`. Ran the **real** `check-domain.sh` end to end on both trees:

| tree | result |
|---|---|
| `origin/main` (=`6ddcac3`, the merge-base) | **crashes**: `ValueError: lstat: embedded null character in path` at `harness_boundary.py:273 real()`, called from `classify` at `:414` — exit 1, non-blocking, **fail open** |
| `64f42ef8` | `check-domain: DENIED — …/notes/evil.md: plan.yaml has exactly ONE writer…` — exit 2, **fail closed** |

**Cycle 3's attribution was wrong; the operator's correction is right.** The crash is
pre-existing in `harness_boundary.real()` (unguarded `os.path.realpath(os.path.abspath(path))`,
confirmed byte-for-byte via `git show origin/main:…harness_boundary.py` — zero try/except around
that call at the merge-base) and this feature fixed it, not introduced it. `real()`'s own docstring
already states this correction; independently re-derived, not merely re-read.

### (b) Fail-closed branch — unconditional, and does not refuse ordinary work

**Kill-mutations, three independent guards, all three reintroduce a hole when reverted:**

1. `harness_boundary.py real()` reverted to the unguarded form (no try/except) → NUL payload
   crashes again through `classify` (exit 1, fail open) — proves this guard is load-bearing.
2. `check-domain.sh _resolved_rel` reverted to catch only `OSError` (not `ValueError`) → NUL
   payload crashes at `_plan_route → _resolved_rel → realpath` (exit 1, fail open) — proves this
   is an **independent, second** guard, not redundant with (1); it fires even when `real()` itself
   is fixed, because `_resolved_rel` is check-domain.sh's own separate resolution, not a wrapper
   around `harness_boundary.real`.
3. `check-domain.sh _plan_route`'s `if resolved is None: return as_typed` reverted to `return
   None` (the old dead `islink`-conditioned shape) → the SAME NUL payload now exits **0**, silent,
   no stderr — proves this line, not merely "not crashing," is what makes the path a **refusal**.

No fourth mutation reached a fail-open return along this path — I looked at `_hardlink_plan`'s
`except (OSError, ValueError): return None` too: reachable only via a TOCTOU (path deleted/altered
between `_resolved_rel` succeeding and this `os.stat` call), extremely narrow, and the same
inherent-race shape the glob-scan hardlink detector already has; not a new gap this feature adds. **info, not a finding.**

**Ordinary work, not wrongly denied.** Ran the real, unmutated `check-domain.sh` against 8
representative shapes (normal relative, absolute-in-root, spaces, unicode, `.claude/worktrees/…`
shaped, outside-repo entirely, deleted/nonexistent parent, and a **real symlink** to a legitimate
granted file) — twice: once ungoverned (no `agent_type`) and once as `harness-backend-dev` writing
in-domain (`.claude/skills/harness/bin/**`). **All 8 × exit 0, zero false denials.**

### (c) `real()`'s absolute-but-unresolved fallback — weakens ONE other caller class, live-confirmed HIGH

Enumerated every production caller (`grep`, not guessed):

| caller | attacker-reachable input? | effect of the fallback | verdict |
|---|---|---|---|
| `select_base()`: `inside(abs_target, abs_root)`, `inside(abs_target, real(workspace_root))` | **YES** — via `classify()` from both `check-domain.sh` (Write/Edit) and `bash-write-guard.sh` (Bash) | `abs_root`/`real(workspace_root)` are freshly, fully resolved; `abs_target`'s fallback is `abspath` only (no symlink hop) — an H-01-class asymmetry, but triggered by an unresolvable input rather than a crafted symlink | **HIGH — live, confirmed below** |
| `classify()`: `_abs_target = real(abs_target)`, `worktree_owner(real(abs_target))`, `_abs_root = real(root)` | same as above | inherits `select_base`'s weakness for the `select_base` call; `worktree_owner`'s **own final comparison self-heals** — its directory walk strips the NUL-bearing final segment via repeated `os.path.dirname` before its one `real(cur)`-based comparison, so by the time that check runs the string is clean again | classify() as a whole is HIGH via select_base; the worktree_owner sub-path is not independently exploitable |
| `check-domain.sh:233,251` (`--resolve`, plan-time route resolution) | plan-declared paths (task `files:`, lane surfaces), not live agent input | same weakness structurally reachable, but requires plan-authoring access and only affects an offline `check-plan-routes.py` verdict, not a live write | LOW/INFO — not a live PreToolUse bypass |
| `check-domain.sh:1015` (shape-phase path relativization for STATE.md/budget checks) | attacker-influenced target | wrapped in a broad `except Exception: pass` that already falls back to a plain relpath on ANY failure (by design, per its own docstring: "must not gain a fail-closed dependency") — `real()` no longer raising changes which branch is taken but not whether the fallback is safe | LOW/INFO — affects which relative path a budget/vocabulary check applies to, not an authorization decision |
| `checkout_relative()`, `linked_worktrees()`, `resolve_fleet()` | no — git-authored `.git/worktrees/*` pointers, operator `fleet.yaml` | inert for this attack class | INFO |
| `worktree_owner(root)` top-level calls in both hooks (root-side, not target-side) | no — session's own root, not per-write input | inert | INFO |

**Live confirmation, `select_base`/`classify` via `bash-write-guard.sh` (HIGH):**

Root: `/tmp/feat41-c4-sec`, which on this filesystem resolves through a real symlink
(`/tmp` → `/private/tmp`, macOS/APFS) — the same class of topology H-01's original fix was written
against (`/var` → `/private/var`), just triggered here by an unresolvable input instead of a
crafted symlink.

Agent `harness-frontend-dev` (no domain over `.claude/skills/harness/bin/**`) issues, via Bash:
`echo x > .claude/skills/harness/bin/check-domain.sh<NUL>` (embeddable as JSON `\u0000` in
`tool_input.command`, which the hook parses cleanly via `json.load(sys.stdin)`).

| target | via | exit | stderr |
|---|---|---|---|
| same command, **no NUL**, same agent | `bash-write-guard.sh` | 2 | `BLOCKED — …redirect targets .claude/skills/harness/bin/check-domain.sh, outside your domain.` (correct) |
| same command, **with NUL** | `bash-write-guard.sh`, `origin/main` | 1 | Traceback, `ValueError: lstat: embedded null character` (pre-existing crash, same as (a)) |
| same command, **with NUL** | `bash-write-guard.sh`, `64f42ef8` | **0** | **(empty — no denial, no message)** |

Instrumented `select_base` to confirm the mechanism (not just the symptom):
`abs_target='/tmp/feat41-c4-sec/.claude/skills/harness/bin/check-domain.sh\x00'` (unresolved —
`real()`'s fallback, since `os.path.abspath` never resolves `/tmp`→`/private/tmp`) vs.
`abs_root='/private/tmp/feat41-c4-sec'` (fully resolved, fresh `real(root)` call inside
`select_base`). `inside(abs_target, abs_root)` → `os.path.commonpath([...]) == abs_root` → **False**
— namespace mismatch, not a domain decision. `classify()` returns
`{"outcome": "not_a_domain_question", "base": None, …}`, and `bash-write-guard.sh:747` treats that
outcome as `continue` (pass) **by design**, for the legitimate case of a target genuinely outside
both the harness and product bases. Here the target genuinely *is* inside the harness base — the
classification is simply wrong, purely because of the resolution asymmetry.

**Why `check-domain.sh` (Write/Edit) doesn't show the same symptom**: reproduced the identical
mismatch there too (`inside=False`, confirmed by the same instrumentation, using the same
`/tmp`→`/private/tmp` root), but `check-domain.sh` still denies (exit 2) — **only because its own,
separate `_plan_route`/`_resolved_rel` layer (job (b)'s subject) unconditionally refuses ANY
unresolvable target for `Write`/`Edit`/`NotebookEdit`, regardless of what the domain layer decided.**
That layer is scoped to plan.yaml protection and only incidentally covers this case. **Bash has no
such layer** — `bash-write-guard.sh` never routes through `_plan_route`; it is check-domain.sh's own
matcher-registered `Write|Edit` hook, and Bash is a completely separate hook file.

**Consequence, stated precisely.** The hook-level decision is unambiguously and silently wrong —
proven, not inferred: exit 0, zero stderr, on a target that is genuinely inside the harness base and
genuinely out of the calling agent's domain. Per this checkout's own topology (verified: neither the
main checkout nor this feature's worktree currently sit behind a symlink — `abspath == realpath` for
both), **this exact reproduction does not fire on the live repository right now.** It fires on any
deployment where the harness root is reached through *any* symlink component — common (macOS `/tmp`,
many container/CI bind-mount and symlinked-`$HOME` layouts) but not universal, and re-derivable with
zero attacker cost the moment it is. I could not independently verify whether the *actual* Bash tool
execution layer would truncate a NUL-bearing command at the OS boundary (making the underlying write
land on the truncated, sensitive path) or reject it outright before execution (Python's own
`subprocess` module raises `ValueError` on an embedded NUL, tested directly) — that residual
uncertainty is about downstream tool-execution semantics, outside what this review's tools can probe.
It does not reduce confidence in the finding: the decision *layer* — the thing a hook exists to be —
is silently wrong regardless of what a specific downstream runtime does with the result, and per this
role's own G-04 pattern, a silent exit-0/no-stderr bypass is *worse* than the crash it replaced,
because an audit afterward cannot distinguish "the guard allowed this" from "the guard was off."

## Stage 2 continued — `station_only` marker forgery: LIVE, NEW, HIGH (not previously found)

This is the hardest item the handoff flagged ("WHAT TO CHECK HARDEST NEXT"), and it is open.

`check-state.sh`'s INV-34 exemption is `if doc.get("station_only") is True: continue` —
**unconditional on the marker alone**, no longer gated on `tasks` being empty (that was the
pre-MF-3 shape). `harness_yaml.load_plan` only *requires* the marker when `tasks` is empty; it
places **no restriction the other way** — a document with real, non-empty `tasks:` **and**
`station_only: true` loads cleanly, no error. The suite's own comment claims "THE EXEMPTION CANNOT
WIDEN SILENTLY: a plan WITH tasks is still held to both, asserted by case (inv34.d)" — checked
`case_inv34_a_real_plan_is_still_checked`'s fixture (`_I34_TASK`) directly: it carries **no**
`station_only` field at all. (inv34.d) proves the exemption doesn't fire when the marker is
*absent*; it does not test the marker present *and* forged onto a task-bearing plan — the exact
combination that matters.

**Proved live**, importing `test-check-state.py`'s own fixture builders (no reimplementation, same
harness) and running the real `check-state.sh`:

- **Forged**: `tasks:` = one real task (`_I34_TASK`), **no `approval:` block**, `STATE.md`
  references `T-99` (absent from the plan), **`station_only: true` added**. Result: exit 1, **zero**
  approval or STATE.md violations — only unrelated fixture-environment noise (INV-29/31/32,
  missing settings.json). Both invariants **silently skip**.
- **Negative control**: byte-identical fixture, **`station_only: true` line removed**, nothing
  else changed. Result: both violations fire correctly — `…plan.yaml has no 'approval:' block —
  cannot tell if the goal is signed.` and `…STATE.md references T-99, which is absent from its
  plan.yaml.`

One line is the entire difference. **Reachability**: this fires for a plan that is task-bearing —
i.e., an *ordinary*, in-flight feature — not just the twelve backfilled plan-less directories
MF-3/T-19 were about. A raw Bash write via any method `bash-write-guard.sh`'s classifier does not
recognize (a Python one-liner doing `open(path).read()`/`open(path,'w').write(...)`, matching the
same "invisible to the classifier" class cycle 2 already found for `plan-merge.py` CLI invocations
and for `ln`/`ln -s`) reaches `plan.yaml` with **zero domain check performed at all** — not denied,
simply never classified as a write. The SC-06 sweep — the *only* post-hoc net for a Bash write —
checks station **vocabulary** only; it never inspects `station_only`. So this forgery is invisible
to every layer this feature built: not denied pre-hoc (Bash isn't routed through check-domain.sh's
`_plan_route`; the write itself is invisible to bash-write-guard's classifier), not caught post-hoc
(SC-06 doesn't look at this field), and — this is what makes it worse than the already-disclosed
"can't attribute a legal write" residual in the BRIEF — it doesn't just forge a value, it **durably
disables two integrity checks** (approval-signed, STATE.md-consistent) for that feature on every
future `check-state.sh` run, until someone notices and removes the line by hand. This is a new
mechanism, introduced by MF-3's own fix (the tasks-emptiness gate it replaced didn't have this
shape), not a re-discovery of HIGH-1/H-01/H-02.

## must_fix

1. **`check-state.sh:210-212`** — the INV-34 `station_only` exemption is unconditional on the
   marker and must also require `not doc["tasks"]` (or equivalently: reject `station_only: true`
   on a task-bearing plan at `harness_yaml.load_plan` load time, `harness_yaml.py:326-352`) — a
   task-bearing plan with a forged `station_only: true` silently loses both its approval-signed
   check and its STATE.md-dangling-task check. Proven live with a real `check-state.sh` run and a
   byte-identical negative control (**HIGH**).
2. **`harness_boundary.py:288` `select_base()`'s `inside()` check (`:352-374`)** — `real()`'s
   unresolvable-input fallback (`os.path.abspath` only) is compared against a fully-resolved
   `abs_root`/`real(workspace_root)`, so an unresolvable target inside the harness base spuriously
   classifies as `not_a_domain_question` on any checkout reached through a symlink.
   `bash-write-guard.sh` has no independent safety net for this (unlike `check-domain.sh`'s
   `_plan_route`, which incidentally covers it) — proven live: an out-of-domain Bash write to
   `.claude/skills/harness/bin/check-domain.sh` by `harness-frontend-dev` exits 0, silently, on this
   exact machine's `/tmp`→`/private/tmp` topology (**HIGH**; not currently reproducible on the live
   worktree's own root, which sits behind no symlink today — but the mechanism is proven and the
   precondition is common, not contrived).

## Open questions

- None blocking. Whether (2) is fixed by making `real()`'s fallback itself resolve as much as it
  safely can (fixing it once, centrally) versus giving `bash-write-guard.sh` its own
  `_plan_route`-style unconditional-refuse-on-unresolvable layer (duplicating check-domain.sh's
  shape) is a design call for whoever fixes it, not this review's to make.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "Job (a) settles cycle 3's attribution as wrong (crash is pre-existing, this feature fixed it); jobs (b)/(c) find the fix is sound for check-domain.sh but leaves bash-write-guard.sh silently permitting an out-of-domain Bash write on an unresolvable path; and a live, mutation-proven new HIGH — station_only:true forged onto a task-bearing plan silently disables both INV-34 checks."
  in_scope: true
  scope_reason: "Dispatch's entire scope is the enforcement boundary (hooks, path resolution, trust decisions) — every finding sits on that boundary."
  severity_max: high
  findings: 3
  must_fix:
    - "check-state.sh:210-212 (harness_yaml.py:326-352) — station_only:true is accepted, and check-state.sh's INV-34 exemption fires, on a plan with real non-empty tasks: the marker is not restricted to the empty-tasks case it was designed for. Live-proven: forged fixture silences both the approval-block check and the STATE.md-dangling-task check; byte-identical negative control (marker removed) fires both correctly. HIGH."
    - "harness_boundary.py select_base()'s inside() check (:352-374), reached via classify() from bash-write-guard.sh — real()'s unresolvable-input fallback (abspath only, no symlink resolution) is compared against a fully-resolved root/workspace, so an unresolvable Bash-write target inside the harness base spuriously classifies not_a_domain_question and bash-write-guard.sh silently permits it (exit 0, no stderr) on any checkout reached through a symlink. check-domain.sh is saved only by its separate, plan.yaml-scoped _plan_route layer; bash-write-guard.sh has no equivalent. Live-proven on this machine's /tmp topology; not reproducible on the live worktree's own (non-symlinked) root today. HIGH."
  threat_model:
    - { boundary: "check-state.sh INV-34 approval/STATE.md invariants -> Bash write forging station_only:true", stride: "T", mitigated: false }
    - { boundary: "PreToolUse Bash -> bash-write-guard.sh domain check via harness_boundary.classify/select_base, unresolvable-path case", stride: "E", mitigated: false, precondition: "checkout reached through any symlink component; not present on this repo's live root today" }
    - { boundary: "PreToolUse Write/Edit/NotebookEdit -> check-domain.sh real()/_resolved_rel NUL-byte crash (MF-2/MF-5)", stride: "D", mitigated: true }
    - { boundary: "PreToolUse Bash -> plan-sign-gate.py sign-approval refusal (SC-07)", stride: "S", mitigated: true }
    - { boundary: "PreToolUse Write/Edit/NotebookEdit -> check-domain.sh plan.yaml route denial, editor writes incl. main session (REQ-05)", stride: "T", mitigated: true }
    - { boundary: "gh-sync.py ship -> worktree-directory refusal and committed terminal station (REQ-07/SC-10)", stride: "T", mitigated: true }
  open_questions:
    - { id: Q1, question: "Fix (2) by making harness_boundary.real()'s fallback itself resolve as far as safely possible (central fix), or give bash-write-guard.sh its own unconditional-refuse-on-unresolvable layer matching check-domain.sh's _plan_route (duplicated fix)? Design call for whoever fixes it.", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-41-one-station-vocabulary/notes/review-harness-security-reviewer-c4.md
```
