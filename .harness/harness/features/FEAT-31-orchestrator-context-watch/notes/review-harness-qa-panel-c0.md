# Coverage ADEQUACY review — FEAT-31, review_sha fcb8984f (5 measurements)

## BLUF

**Adequate.** The two mechanisms that hid the two prior defects (shallow discovery, `_build_row`
arithmetic) are now independently falsified in both directions with cascading, not marginal,
failure. No new **high** finding. Two genuine, low-severity coverage gaps found and named (items 3
and 5) — real on-disk shapes the fixtures never encode, and one dead-code artifact that explains the
count discrepancy without being a defect. SC-09 (the prior HIGH, unmet at ed62d74) is now closed at
`666cd63` inside this range — not re-raised.

## 1. Q-CHECKCOUNT — SETTLED, one execution

Measured at review_sha fcb8984f: **78** static `check(` call sites (79 matches minus the `def
check(` line itself), **76 ran** (`python3 test-context-watch.py` → `76 of 76 cases passed`,
reproduced twice). Line-level instrumentation (frame `f_lineno` capture, scratch copy only, tree
left clean — `git status --porcelain` empty) identifies the exact two unreached sites: **lines 668
and 669**, both `check("J2...")`/`check("J3...")` duplicates **inside** the
`if real_count_j == mutant_count_j:` diagnostic guard (lines 663–673) that only fires when case J's
RED-proof mutation **failed to apply** — the branch itself `raise SystemExit`s immediately after, so
those two calls exist purely as a canary for "the harness itself is broken," never as product
coverage. On every observed run the mutation applies cleanly (`real_count_j=1 != mutant_count_j=0`),
so the branch — and its two `check()`s — is dead code, not two silently-skipped assertions. **Not a
finding against the product**; worth one line to whoever next edits this file: the static grep count
will always read 78 against a genuine 76 RAN, and that gap is structural, not a regression signal.

## 2. Depth fix — FALSIFIED in both directions

Copied `context-watch.py` to scratch (`/private/tmp/.../scratchpad/cw-1level.py`,
`cw-3level.py`), collapsed `discover_orchestrator_rows` to one level and expanded it to three,
diffed each mutant against the original to confirm the mutation applied, then ran the **committed,
unmodified** `test-context-watch.py` via `CONTEXT_WATCH_BIN=<mutant>`.

| mutant | result |
|---|---|
| 1-level (matches the FIRST shipped defect) | **45 of 76 pass** — `L1`, `L2`, plus 27 unrelated cases (A/B/C/D/F/G/N/M-groups) cascade-fail because discovery returns nothing |
| 3-level (over-correction) | **46 of 76 pass** — `L1` plus the same 27 cascade-fail; `L2` still passes because it builds its own internal 1-level mutant independently of `CONTEXT_WATCH_BIN` |

`git status --porcelain -- context-watch.py test-context-watch.py` is empty throughout — no tracked
file was touched. This is stronger than the "L1/L2 both pass" reading from the prior gate note: it
is not just that the depth-specific cases catch it, **nearly a third of the whole suite goes down
with it**, because almost every fixture routes through `discover_orchestrator_rows`. Genuinely
pinned in both directions.

## 3. Fixture realism — mostly faithful, two real shapes never encoded

Compared fixtures against live sidecars under `~/.claude/projects` (read-only).

**Faithful:** the arithmetic fixture's `_usage(iterations=...)` shape matches real data exactly —
2051 of 2058 real `agent-*.jsonl` files on this machine carry a `usage.iterations` list, and a
sampled real iteration entry carries the identical three summed keys
(`input_tokens`/`cache_read_input_tokens`/`cache_creation_input_tokens`) the fixture uses, plus
extra keys (`cache_creation`, `type`) the code correctly ignores. The depth fixture's
`proj-a/sess-a/subagents` correctly encodes the real `<project-dir>/<session-uuid>/subagents` two
levels.

**Not encoded anywhere in the committed suite** — both confirmed present on this machine's real
`~/.claude/projects` tree, read-only:
- A **non-session sibling directory** at the project level (e.g. a `memory/` directory sitting next
  to session-UUID directories under one project dir).
- A **top-level `.jsonl` file** sitting directly under a project dir, at the same level as session
  directories (a main-session transcript, not a subagent sidecar).

Neither breaks the current code — both fall through harmlessly because `discover_orchestrator_rows`
checks `os.path.isdir` on the **joined** `.../subagents` path rather than on `session_dir` itself, so
a file or an unrelated directory at that level is silently skipped either way. **Low severity: no
defect, but no fixture proves it** — a future refactor that changed the ordering (e.g. checking
`os.path.isdir(session_dir)` before joining) could regress silently, because nothing in the suite
ever hands discovery this exact noise shape.

## 4. T-17 hook coverage

**Bound** by the committed `test-context-watch-hook.py` (run, not just read): exit codes (0
non-crossing / 0 non-orchestrator / 2 crossing), stderr content (current figure, threshold figure,
the word "handoff", never "blocked"/"stopped"/"refused"), stdout staying empty, and a 4-case
never-raises sweep (non-JSON body, empty body, JSON missing `agent_id`, a JSON list instead of an
object) — each asserted to exit 0 with zero stderr, zero traceback.

**Unbound until first fire**, and this is a genuine residual, not the already-closed Q-HOOKCTX: the
hook's key-name assumptions (`session_id`, `agent_id`, `agent_type`, `cwd`) were empirically probed
for a **`PreToolUse`** payload (`notes/probe-hook-payload-identity.md`) and never independently
re-probed for **`PostToolUse`** specifically, which is the event this hook actually registers on. The
extrapolation is reasonable — Claude Code's own hook schema is documented as symmetric across events
— but it is an inference, not a direct observation, and it sits underneath every other assertion in
`test-context-watch-hook.py` (its `payload_for()` fixture assumes exactly these keys). Consequence if
wrong: the hook silently never fires for real orchestrators (fails open, consistent with its own
"never raise" contract) — not a crash, a quiet no-op. **Severity: low-med**, because the fail mode is
the one the design explicitly chose as acceptable, but it is worth a first-fire confirmation once
this branch merges and the hook actually runs (which the prompt already flags as expected and not a
test failure here).

## 5. Untested changed units, and what breaks silently

- **`feature_schema.py::_feature_dir_name` returning `None`** (a display path carrying no
  `features` segment) — the docstring names this as a deliberate branch ("defaults to 0
  exemptions... fails loudly"), but no committed test constructs a display string without a
  `features` segment to exercise it. If a later change flipped the None-default from 0 (strict) to
  "skip the check" (permissive), nothing in `test-validate-feature-json.py`'s `t15_*` cases would
  catch it. **Severity: low** — the current default is the safe direction (denies rather than
  passes), so nothing ships broken *today*, but the safety of that default is asserted only in a
  comment, not a test.
- **`check-state.sh` INV-17 whitespace-only body.** Read the implementation: `hl` is built with
  `.strip()` up front, so a body line of `"   "` collapses to `""` and is correctly treated as empty
  by the `any(_b for _b in _body)` check. But the test fixture (`_empty_section` in
  `test-check-state.py`) only ever inserts a **literal empty string** (`out.append("")`), never a
  whitespace-only line. The behavior is provably correct **by reading the code**, not demonstrated
  by any fixture — a later refactor that stopped stripping before building `_body` would produce a
  false PASS (a whitespace-only section reads as non-empty) and nothing here would go red.
  **Severity: low.**
- **INV-17's glob is single-level** (`notes/handoff-*.md`, not recursive) — correct by the
  repository's own flat-notes convention (confirmed: every feature's `notes/` on disk here is flat),
  so this is not a live risk, just an unexercised edge (a `notes/subdir/handoff-x.md` would never be
  reached). Not raising as a finding — purely hypothetical given the convention.
- **Hook execution order is a platform assumption, not this diff's code**: `context-watch-hook.py`
  is registered in the SAME `PostToolUse` `Write|Edit|Bash` array as `check-domain.sh --post`
  (`.claude/settings.json`, both present at review_sha). Whether Claude Code runs every hook in an
  array regardless of an earlier one's exit code (so the context warning still fires on a Write that
  also trips a domain violation) is asserted nowhere in this diff — it is a property of the hook
  runner, external to this codebase, and out of scope for a unit/integration suite. Flagging as an
  **open question**, not a finding against this diff.

## Verdict inputs

No coverage gap here rises to `high`. Items 3 and 5 are `low` — real, but each fails in the safe
direction (silent no-op or a strict/loud default), not a silent wrong answer shipped as truth. Item 4
is `low-med` — an inference standing under a real test suite, not a gap in the suite itself. Item 1
resolves to a documentation/counting artifact, not a defect.

Prior filed items (#663–#669) and Q-HOOKCTX/Q-WARNVERB not re-raised per instruction.
