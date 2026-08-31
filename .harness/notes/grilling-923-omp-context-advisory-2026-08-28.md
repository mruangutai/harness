# Grilling — OMP-native orchestrator context advisory (issue #923) — 2026-08-28

## Destination

The orchestrator's context advisory works under OMP: a real, host-derived number reaches the
orchestrator at its wake, `SKILL.md` step 5 describes a mechanism that exists, and the Claude-only
path is resolved by an explicit decision rather than by neglect.

Reaching the end looks like: a merged PR that closes #923, with a test that fails loudly if the
`contextSnapshot` schema moves — so the advisory cannot silently go inert a second time.

## Settled

- **Retire the Claude context-watch path outright?** → Yes. Delete `context-watch.py`,
  `context-watch-hook.py`, `verify-context-watch-live.py`, `references/context-check.md` and the
  three test files; unregister the PostToolUse hook from `.claude/settings.json`. Claude hosts get
  no context advisory. Rationale accepted: one mechanism means one place it can go inert, which is
  the failure mode #923 exists to fix.
- **How is this tracked?** → Full **FEAT-44** with board mirroring: `BRIEF.md`, `plan.yaml`, parent
  issue, task issues, milestone. Chosen partly so this feature exercises the
  `Building → Review → Done → auto-close` path that PR #922 promised as deferred evidence and could
  not deliver (it merged with zero linked issues and no feature record).
- **Amend or strike DEC-198 and DEC-201?** → **Amend both, strike neither.** Determined against
  DEC-188's own test rather than asked: a decision is struck only when the tree *flatly contradicts*
  it. DEC-198's threshold (200000) survives untouched — only its stated *source*
  (`context-watch.py`'s `DEFAULT_CONTEXT_WARN_TOKENS`) is orphaned, so the default must be re-homed.
  DEC-201's ruling (the orchestrator weighs its own context and hands off at a seam) survives; only
  its *mechanism* paragraph — the two-call nonce probe — is superseded. pm may overrule with cause.
- **How does #923 close?** → As `source_issues: [923]` in `plan.yaml`, mirrored into
  `feature.json.github.source_issues` by `gh-sync.py open` and rendered into the PR body by its
  `closes` renderer. No separate manual close step.
- **Does DEC-174 force the whole build main-session-direct?** → **Yes — and only because of the
  consolidation decision below.** This reverses an earlier reading in this same session, recorded
  rather than quietly amended. The module/cutover precedent (FEAT-31 built `context-watch.py` as
  `execution_mode: team`) applies when the logic is a **separate library** a squad can write. Once
  the reader lives *inside* `.omp/extensions/harness-hooks.ts`, there is no library left: every line
  of the implementation is in a hook file. DEC-174's ruling is explicit — "A change to the
  enforcement layer is made **directly** — ordinary edits, tests run explicitly, a human reading the
  diff — not dispatched through a team run whose gates are the thing being changed." So every build
  task in `plan.yaml` is `execution_mode: main-session-direct`. Planning through the harness stays
  fine; executing does not.
- **Does DEC-174's cost warning apply to running full FEAT-44 ceremony here?** → It applies but is
  largely self-mitigating, so the "Full FEAT-44 + board" decision stands. DEC-174 records the smell
  honestly: "$92 went to planning before a single line of code, on a change whose core is roughly
  fifty lines of Python. The ceremony is calibrated for product features, not for editing the
  ceremony." The expensive half of that ceremony — a full team build run — is **already removed** by
  the main-session-direct ruling above. What remains is pm planning, board mirroring (cheap,
  `gh-sync.py`), direct execution, and a review panel. pm should keep the task count lean and MUST
  NOT pad the plan to look like a product feature.
- **One implementation or two?** → **One, in TypeScript, inside `.omp/extensions/harness-hooks.ts`.**
  No sibling module, no Python CLI, no thin shim, no process fork. The CLI that `context-watch.py`
  offered is explicitly **not** a requirement.
- **Does the new reader need an independent verifier, as SC-01 required of the old one?** → **No,
  and the reason is structural rather than a judgement call.** SC-01 mandated
  `verify-context-watch-live.py` as a no-shared-code second opinion because `context-watch.py`
  *performed arithmetic* — summing `input_tokens` + `cache_read_input_tokens` +
  `cache_creation_input_tokens`, then taking a max over `message.usage['iterations']`. Arithmetic can
  be wrong, so it needed a witness. The new reader performs **no arithmetic**: it returns a single
  field the host already computed (`message.contextSnapshot.promptTokens`). There is nothing to
  second-guess, so the requirement that produced the second file does not carry forward. Do not
  rebuild it.
- **Where does the reader's test live?** → In the existing bun suite,
  `.claude/skills/harness/bin/omp-hooks.test.ts` (24 tests today), not a new Python test file. This
  follows from the TypeScript decision and keeps the delete list from being replaced by an
  equivalent add list.

## Not yet specified

Nothing. The frontier emptied — every branch was either settled above, ruled out of scope below, or
resolved as a fact. Two design questions are **sharp enough to state, so they are pm's work rather
than fog** (per the fog test: sharpness of the question, not availability of the answer):

- **Fixture provenance for item 5** — a real captured JSONL versus a hand-built minimal one. Both
  freeze at commit time, so neither alone detects live upstream drift; decide whether the test needs
  a second live-schema assertion beside the frozen fixture. This matters because item 5's whole
  purpose is that a `contextSnapshot` schema change fails CI loudly.
- **Injection filtering** — the `tool_result` handler fires for every `task` result in every
  session. Decide how it is scoped to the orchestrator's wake so the main session and leads are not
  given an advisory addressed to a tier they are not.

## Out of scope

- **DEC-198 threshold calibration.** The disk read yields tokens, not percent, and reported context
  windows vary ~5× across models (`claude-sonnet-5` reported 1,000,000 in probing), so 200000 is 20%
  on one model and 100% on another. Whether an absolute threshold is the right *shape* is a DEC-198
  question, not a portability one. #923 declares it out of scope and that stands.
- **Provider accounting quirks.** Reasoning-token differences across OpenAI and Gemini are inherited
  from omp, not introduced here. We read what the host's own status line shows.
- **An external watchdog.** Rejected in #923 §4 on structural grounds: it cannot spawn the
  replacement orchestrator (DEC-120 makes main the sole user channel, DEC-147 rejects same-layer peer
  spawns, and an external process cannot dispatch through `dispatch-guard.sh` at all).
- Fixing the wording-assertion test class beyond `test-orchestrator-playbook.py` case 4.

## Facts I verified (so pm does not re-derive them)

All at `7ebfc9e` (`origin/main`, PR #922 merged) unless noted.

- **Claude Code is not retired.** DEC-202 keeps it a supported compatibility adapter —
  `DECISIONS.md:7113-7119`. But that parity promise is scoped to agent roles, skills discovery and
  `CLAUDE.md` import; it says nothing about `settings.json` hook contents. Retiring the hook does not
  breach it.
- **The hook cannot fire under OMP.** `.omp/config.yml:1-3` disables the Claude provider, and
  `check-omp-port.py:61-62` enforces that as a port invariant.
- **Nothing blocks deletion.** Zero `context-watch` matches in `check-state.sh`; INV-9's hook
  enumeration (`:316-424`) names inject-expertise and check-domain only. No invariant asserts these
  files exist.
- **#923 undercounts the delete list by one file, and it is the one nothing would have caught.**
  Item 4 enumerates six artifacts (2 source, 1 doc, 3 tests). A seventh —
  `verify-context-watch-live.py`, 518 lines, SC-01's "live half" — depends on `context-watch.py`
  with **no import at all**: it derives the sibling path at runtime
  (`:75-79`, `os.path.join(os.path.dirname(os.path.abspath(__file__)), "context-watch.py")`) and
  forks it via `subprocess.run([sys.executable, context_watch_path, ...])` (`:220-224`). The absent
  import is deliberate — SC-01 required independence, since "sharing that code would compare a
  function to itself" (`:21-24`) — which is exactly why no import graph, linter or file census
  surfaces the coupling. Its `--self-test` mode (`:408`, `:449`) forks the same real sibling, so the
  file's own self-check dies with it too.
- **That file's missing-sibling diagnostic is unreachable, measured.** The `except OSError` at
  `:225` was written to catch a deleted `context-watch.py`, but `subprocess.run` execs
  `sys.executable` — which always exists — so a missing script argument raises nothing. Measured
  directly: no `OSError`, `returncode 2`, empty stdout, error on stderr. `returncode` is never
  checked and stderr never surfaced, so control reaches `:233-238` and reports
  *"context-watch.py reported no measured row for agent id X (not found in its output)"* — which
  reads as "the tool ran and found nothing" when the tool does not exist. Deleting the sibling
  without deleting this file leaves dead code that misdiagnoses its own breakage.
- **It gates nothing, and this was known at FEAT-31's ship.** Verified absent from `UNIT_SCRIPTS`,
  `INTEGRATION_SCRIPTS` and `harness.json`'s `detect` lists. FEAT-31's ship review already recorded
  it as **B-1, "the panel's deepest residual"**
  (`FEAT-31-orchestrator-context-watch/notes/ship-review-ship1.md:116`; also `STATE.md:85`). A
  known-ungated file was left in the tree at ship and the retirement ticket did not see it.
- **Four decision-record citations reference the mechanism**: DEC-158 (`DECISIONS.md:3964-3967`),
  DEC-159 (`:4084-4088`), DEC-198 (`:6782-6785`), DEC-201 (`:7002-7006`).
- **CORRECTED 2026-08-29 — this entry was WRONG as first written, and pm caught it.** The original
  text claimed `test-orchestrator-playbook.py:62-65` asserts the literal `context-watch.py` is
  *present* in `SKILL.md`. It asserts the **opposite**: `case4_absence_claude_sidecar_probe` checks
  `"context-watch.py" not in text`, so deleting the script *satisfies* that assertion rather than
  breaking it. The error came from a scout summary that was passed through without a source check,
  in a section explicitly marked do-not-re-derive — the most expensive possible place to put an
  unverified claim. Verified at source at `7ebfc9e`.
- **Mechanical guards that actually move**, all of which must change in the same commit:
  `case4_presence_host_context_signal` in `test-orchestrator-playbook.py` (a regex requiring the
  phrase `host's current-session context signal` in `SKILL.md` — this is what the step 5 rewrite
  invalidates), `run-unit-tests.sh:17-18` (three registered test scripts), and `harness.json`'s
  integration `detect` list (names the context-watch test files explicitly). Re-verify each anchor
  at source before editing; two of the three line numbers handed to pm were already stale.
- **The module/cutover split is established precedent, from this very mechanism's original build.**
  FEAT-31 put the logic in `context-watch.py` as `execution_mode: team` / `harness-backend-dev`,
  while the thin registered hook plus its `.claude/settings.json` registration was
  `execution_mode: main-session-direct`. Across shipped plans: 128 `main-session-direct` tasks vs
  118 `team`.
- **`source_issues` is a real mechanism**, not a convention: mirrored from `plan.yaml` by
  `gh-sync.py open` and read by its `closes` renderer
  (`test-validate-feature-json.py:328-329`). FEAT-37 carries one.
- **Next free feature id is FEAT-44.** 41, 42 and 43 are live in worktrees and issues; `main`'s
  features directory stops at 40.
- **The OMP extension has no context logic today.** Zero matches for `context` or `warn_tokens` in
  `.omp/extensions/harness-hooks.ts`, confirming #923's premise that no OMP-native counterpart
  exists.
- **`fix/868-analysis-digest-and-lead-notes` is 57 commits behind `main` and empty** — 0 commits
  ahead, no upstream, no PR. Its HEAD commit is already contained in `main`. This work is therefore
  planned from a fresh worktree at `7ebfc9e`, not from that branch.
