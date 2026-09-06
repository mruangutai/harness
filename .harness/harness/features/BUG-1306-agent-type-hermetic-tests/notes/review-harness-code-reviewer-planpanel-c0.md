# Plan-panel — scope reader — BUG-1306 — cycle 0

**BLUF: one HIGH finding.** T-01's `verify:` block (`plan.yaml:59-67`) mechanically discharges
SC-01 and SC-02 only — it never runs the clean-environment control. SC-03 is marked
`verify: automated` in the BRIEF but has **zero** automated coverage anywhere in the plan; it
rests solely on a builder-authored receipt sentence. The goal-check note's own claim
("SC-01/02/03 are discharged verbatim by T-01's `verify:`", item 4) is factually wrong for SC-03.
Everything else checked — mechanism soundness of the D-02 env-pop, SC-05's confinement wording,
decision-block weight — is sound or non-blocking. Recommend the amendment below before signature;
does not require reopening any of D-01..D-07.

## Finding 1 — SC-03 has no automated gate (HIGH)

`plan.yaml:59-67` is T-01's entire `verify:` block. It runs exactly one invocation —
`HARNESS_AGENT_TYPE=harness-orchestrator python3 tests/integration/test-plan-merge.py`
(`plan.yaml:61`) — checks `rc`, checks for `^FAIL`, and greps the two `PASS` strings. That
discharges SC-01 and SC-02. It never invokes `env -u HARNESS_AGENT_TYPE python3
tests/integration/test-plan-merge.py`, the SC-03 command. That command appears exactly once in
the whole plan, in `intent:` prose at `plan.yaml:103-105`, as something the builder is asked to
"also record… in the same receipt" — not as a machine-checked assertion.

**Consequence:** SC-03 is declared `verify: automated` in `BRIEF.md`, which under this codebase's
convention means an automated command enforces it. None does. Every downstream gate that could
have caught the gap declines it by construction: T-01's `verify:` doesn't run it (above); D-07
scopes QA's "independent run" to the *governed* invocation only ("qa records its independent run…"
of "the pre-fix red and post-fix green pair… under the ambient governed invocation, and nothing
else" — SC-03 is the *clean*-env command, a different invocation); SC-03 isn't `verify: inspection`
either, so no reviewer owns citing it. If the builder's receipt sentence for SC-03 is wrong,
copy-pasted without re-running, or simply omitted, nothing mechanical in this plan would notice —
not at build, not at QA, not at review. The actual functional risk of a regression is low (the fix
is a no-op `os.environ.pop` under an already-clean env), but the verification-completeness gap is
total and certain, not probabilistic.

**Remedy (cheap, does not reopen D-01..D-07):** add the SC-03 command to T-01's `verify:` block —
three more lines, same shape as the existing check:
```
out2=$(env -u HARNESS_AGENT_TYPE python3 tests/integration/test-plan-merge.py)
rc2=$?
if [ "$rc2" -ne 0 ]; then exit 1; fi
if printf '%s\n' "$out2" | grep -q "^FAIL"; then exit 1; fi
```
This doesn't conflict with D-07: D-07 scopes what counts as *the regression proof narrative*
(the governed red→green pair), not what `verify:` may mechanically assert. SC-03 is a
no-regression check on an already-passing invocation, not part of that narrative.

## Checked, no finding

- **Mechanism soundness (D-02).** Re-derived `run_pool.py:61-63` — one `subprocess.run` per file,
  confirms the pop cannot reach a sibling file. Grepped `.claude/skills/harness/bin/` and
  `.agents/skills/harness/bin/` (identical, non-symlinked duplicate trees) for
  `HARNESS_AGENT_TYPE`: the only production env-read is `plan-merge.py:1188` in both copies.
  Grepped all of `tests/` for the same variable: no other test file reads it (the one TS hit,
  `tests/unit/omp-hooks.test.ts:311-333`, is a separate Bun process, not sharing this Python
  process). `test-plan-merge.py` does contain two in-process module loads via
  `importlib.util.spec_from_file_location` (`:1662`, `:1915`) — both exercise `_verify_amend`
  and amend-only internals, never `cmd_sign_approval`, and `plan-merge.py`'s module-level code
  never touches `HARNESS_AGENT_TYPE` (it's read only inside `cmd_sign_approval`'s body,
  `plan-merge.py:1188`), so these imports are unaffected by the pop either way. `.github/workflows/
  tests.yml` invokes `.agents/skills/harness/bin/run-unit-tests.sh --kind integration`, sets no
  `HARNESS_AGENT_TYPE`, so CI is already clean and this fix cannot change CI's result — matches
  the BRIEF's own framing and pm's Q1. `run_verb`'s `env=None` default (`:137`) and the negative
  control's env-filter dict (`:1130`) both become redundant no-ops post-pop exactly as the plan's
  own intent text says; confirmed by reading, not assumed. `PLAN_MERGE_BIN` (`:33`) is an unrelated
  variable, unaffected. No orphan caller found.
- **SC-05 confinement.** The amended two-dot-pinned form grades the same twice under normal
  (fast-forward, non-rebased) `main` history. It closes all three escape routes the probe named:
  editing `plan-merge.py` or a runner (`run_pool.py`/`run-unit-tests.sh` — both live under the same
  `.claude/skills/harness/bin/`/`.agents/skills/harness/bin/` prefixes SC-05 already refuses) and
  editing a second test file (caught by the "only" wording, independent of the explicit restatement).
  The "Harness lifecycle artifacts" clause admits anything under
  `.harness/harness/features/BUG-1306-agent-type-hermetic-tests/`, but nothing there is executable
  by production code, so this is not an exploitable admit-gap.
- **Scope weight (D-06/D-07).** D-06 (cycle cap) is, by its own `because:` text, process
  bookkeeping homed in the decision list only because `feature.json`'s schema rejects it elsewhere
  — not a choice about this change. It's honestly labeled as such, not misleading, and no task
  references it via `dec:`. Low/info, not gating: it inflates the "seven decisions" count without
  adding leverage to T-01, but causes no misapplication. D-07, by contrast, is a real choice about
  this change's evidence shape (which artifacts count as the regression proof) — not bookkeeping.
- **Q2 (case_1103 predicate weakening under an unchanged check name).** Real, but narrow: SC-05
  only gates which *files* changed, not which *lines* within the one permitted file changed, so a
  future edit weakening `r.returncode == 10` while keeping the `check()` name string would still
  satisfy SC-01, SC-02, SC-04 and SC-05 as written. D-05/T-01's intent already forbid the *builder
  of this task* from touching those two cases at all, so the immediate risk for this fix is low;
  the gap is a standing one for *future* edits with no detector. Rated med, not high, since nothing
  in this plan's own build task can trigger it — but worth one line in the reviewer's cycle-0
  dispatch: confirm `case_1103_sign_approval_refuses_a_governed_agent` and
  `case_1103_sign_approval_negative_control_absent_is_main_session` (`test-plan-merge.py:1097-1140`)
  are byte-identical to pre-fix HEAD, not merely that their check names are unchanged.

## Not re-litigated

D-01/D-03/D-04's confinement to one file, no shared helper, no `plan-merge.py` change — accepted
per Advisor ruling, not reopened. D-05's "no new case" reasoning is sound at the file level and not
disputed.
