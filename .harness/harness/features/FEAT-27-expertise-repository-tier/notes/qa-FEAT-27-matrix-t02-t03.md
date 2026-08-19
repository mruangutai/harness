# QA gate — FEAT-27 T-02/T-03, pinned `2117a46`

**VERDICT: PASS.** Both tasks' matrix obligations are discharged, both `verify:` blocks pass
verbatim, and every probed SC binds a named test that can be shown to redden by mutation.

## Step 0 — tree identity

- `HEAD` = `de4b76a0` on `feat/FEAT-27-expertise-repository-tier`, one bookkeeping commit ahead
  of `2117a46` (`git log`: `de4b76a` → bookkeeping → `2117a46` [t-03] → `6edb911` [t-02]).
- `git diff --stat 2117a46 -- inject-expertise.sh test-inject-expertise.py run-unit-tests.sh
  check-expertise.sh test-check-expertise.py` is **empty**. The graded surface's working copy
  equals the pinned commit. Proceeded.

## Matrix compliance

| Task | change_type | Required kinds | Command | Exit | Result |
|---|---|---|---|---|---|
| T-02 | logic | `unit` | `run-unit-tests.sh --kind unit` | 0 | 137 PASS / 0 FAIL, `PASS test-inject-expertise.py` named |
| T-03 | cross_module | `unit`, `integration` | `run-unit-tests.sh --kind integration` | 0 | 90 PASS / 0 FAIL, `PASS test-check-expertise.py` named |

T-03's `verify:` also runs `check-expertise.sh .harness/expertise/` live: exit 0, `ADVISORY` lines
present (29 of them, e.g. `harness-backend-dev.md:63: G-03 names '.claude/'`). Both tasks' `verify:`
blocks match the dispatch's carried-verbatim text exactly — no mismatch.

**`matrix_ok: true`.** `cross_module → always: [unit, integration]` is unconditional
(`harness.json:22-27`); `logic → always: [unit]`. The stale `integration.detect` glob (does not
list `test-check-expertise.py`) is confirmed **non-gating**: `run-unit-tests.sh:18`
`INTEGRATION_SCRIPTS` registers `test-check-expertise.py`, and the live `--kind integration` run
printed `PASS test-check-expertise.py`. The runner is the authority for what executes; the glob is
stale prose only. Reported per the dispatch's ruling — not fixed, `harness.json` out of scope.

## No weakened assertions

- `run-unit-tests.sh` diff (`253287f..2117a46`) is a **pure append** — `test-inject-expertise.py`
  added to `UNIT_SCRIPTS`, nothing dropped or reordered.
- `test-check-expertise.py` diff is a **pure append** — one line removed is the old
  `sys.exit(1 if run() else 0)`, replaced by a wrapper that runs both `run()` (unchanged, all 9
  original cases untouched) and the new `run_extra()`. No pre-existing assertion inside the nine
  original cases was modified.

## SC coverage — binds, not coexists (mutation-proven)

All probes ran against scratchpad copies (`/private/tmp/.../scratchpad/probes/`), zero repo
writes. Baseline sanity (unmutated copy) ran first each time: 18/18 (inject) and 22/22 (check)
confirmed the harness itself works before any mutant was trusted.

| SC | Test | Assertion that carries it | Mutation | Result |
|---|---|---|---|---|
| SC-01 | `test-inject-expertise.py` case1 | `"## Your Expertise — harness repository (repository tier)" in ctx` | repo-header `printf` removed | **case1 FAILED** (also case2, case10 collaterally) — binds |
| SC-04 | `test-check-expertise.py` case1 (`run_extra`) | `"ADVISORY" in out` and `"DEC-042" in out` | `REPO_TOKEN_RE` replaced with a never-matching pattern | **case1's two assertions FAILED**, case2's 9 token-class cases FAILED too — binds |
| SC-05 | `test-check-expertise.py` case6 | `"over the 40-line budget" in out` under bare-path `cwd` invocation | `classify_tier` uses `path` not `os.path.abspath(path)` | **case6 FAILED** — binds |
| SC-06 | `test-inject-expertise.py` case3 + case5b | `"repository" not in ctx"` (no-repo-tier) / empty-stderr assertion (bad agent_type) | precedence-line hoisted unconditional / try-except removed from JSON parse | **case3 FAILED, case5b FAILED — both stated clauses bind** |
| SC-09 | `test-inject-expertise.py` case7a | `"[TRUNCATED at 40 lines" in ctx` | repo `cap_body` call changed 40→45 | **case7a FAILED** — binds |
| SC-10 | `test-inject-expertise.py` case1 | precedence substring present + index-order check | precedence-line `printf` removed | **case1 FAILED** (also case2, case10, case11) — binds |

## SC-06 — both stated clauses now proven to redden

SC-06's text has exactly two clauses: (a) no repository tier present → no repository header, and
(b) `agent_type` missing/unparseable → exit 0, no error. Two direct mutants, both against the
verified-faithful baseline copy:

- **Clause (a).** Hoisted the precedence-line `printf` out of the `sorted_idx` guard so it always
  prints, even with zero repository blocks. `case3: craft only, no repository text of any kind`
  **FAILED** (`"repository" not in ctx"` now false) — 16/18. Binds.
- **Clause (b).** Removed the `try/except` and `2>/dev/null` from the inline `agent_type` JSON
  parse, so invalid JSON now raises a Python traceback to stderr instead of printing `""`.
  `case5b: invalid JSON payload -> exit 0, no traceback` **FAILED** — 17/18. Binds.

**SC-06 is fully proven — both stated clauses redden.** It does not cover a third, unstated
robustness case discovered separately below.

## A separate robustness hole, found by mutation but outside SC-06's text

Probe 5 (remove the `[ -r "$f" ]` guard in the repo-tier glob loop) **survived the full 18-case
suite (18/18 unchanged)** — not a broken probe. Confirmed the mutation was live (grepped the
mutated copy: guard line absent) and confirmed the suite actually executed all 18 cases.

Root cause, verified directly: the segment-name filter (`case "$segment" in ''|*[!a-z0-9-]*)
continue;;`) is a second, independent guard. A non-matching glob without `nullglob` yields the
**literal unexpanded pattern** as `$f` (contains a literal `*`), and that literal always fails the
segment regex too — so removing `[ -r ]` alone is masked for the *non-matching-glob* case. But
`[ -r ]` also guards a **different** failure mode the 12 cases never construct: a file that
**matches** the glob but is **unreadable** (permission denied). Built that fixture directly
(chmod 000 on a real repo-tier file): the mutant emits `Permission denied` to stderr twice, an
`integer expected` error, and a **phantom repository header with no body**. This is NOT part of
SC-06's stated text (SC-06 speaks only to "no repository tier" and "bad agent_type", not "an
unreadable repository file"), so it is not a missed SC — it is an additional robustness gap the
suite happens not to cover. Flagged as `coverage_gaps`, not fixed — my domain is tests, not
source, and this is a dev fix (a 13th case).

## Two disclosed weak assertions

**`test-inject-expertise.py` case12 (hostile `agent_type`, `^harness-[a-z0-9-]+$` regex removed).**
Tested the four values directly against a no-regex mutant with case12's real fixture (files at both
tiers named `harness-qa.md`, home neutral). **All four produced empty stdout — none leak, none
discriminate.** None survive as regression pins:
- `harness-` → interpolated path never matches a real file.
- `harness-qa/../../etc` → same.
- `harness-*` → does **not** glob-match the fixture's real `harness-qa.md`. In the script, the
  value is inside double quotes (`"$agent.md"`), so its `*` is a literal character under bash
  pathname expansion, not a wildcard — the glob word requires a file literally named
  `harness-*.md` (asterisk in the filename), which case12's fixture never writes. The dispatch's
  hypothesis (that this value might match a real file) does **not** hold under the case as
  authored.
- `harness-qa;id` → same as the first two.

**Nothing else in the suite binds the regex's actual marginal contribution either.** `case6`
(non-harness agent, value `"some-other-agent"`) *does* redden when the whole gate is removed —
but that value fails the simpler "starts with `harness-`" check the pre-T-02 script already had
(a plain `case` pattern). 1c's real addition — rejecting a bad **suffix** after a valid
`harness-` prefix — has **zero discriminating coverage** in the current suite. Reported, not
fixed (case12 is disclosed-as-is by the dispatch; strengthening it is a test-authoring change
outside this gate's remit — flagged as a `coverage_gap` for a future task, not a `FAIL`).

**`test-check-expertise.py` case2's `FEAT-\d+` sub-case.** Confirmed directly: with the advisory
regex disabled, 9 of 10 token-class sub-cases (`DEC`, `INV`, `.harness/`, `.claude/`, `check-*.sh`,
`factory_*.py`, `gh-sync`, `harness.json`, `team-config`) FAILED as expected. The `FEAT-12`
sub-case did **not** fail — `FEAT-\d+` is also matched by the pre-existing `FEATURE_TOKEN_RE`
hard violation, which independently puts `'FEAT-12'` in the FAIL output regardless of the advisory
scan. Confirmed, not fixed, per the dispatch: strengthening it means asserting the `ADVISORY` line
specifically, a plan change outside this gate.

## Test-first / Phase 1 vs Phase 2

Phase 1 (BRIEF + plan only, no source read) predicted: a discriminator test for the repository
header + precedence wording (SC-01/SC-10), per-agent write-guard proof (SC-02, T-01 — out of
scope here), an advisory-scan test naming file/line/id/token in both directions (SC-04), a
budget-by-tier test including the abspath bare-invocation case (SC-05), a no-repository/bad-input
regression test (SC-06), and a truncation-message-names-the-right-number test (SC-09). All landed,
matching the plan's own prescriptive `intent:` blocks essentially 1:1 — the plan itself enumerates
cases 1–12 / 1–6 by ordinal, so Phase 1 and Phase 2 converge here by construction; no gap to report
beyond the SC-06 permission-file case above, which neither Phase 1 nor the plan's own case list
anticipated.

## Coverage gaps

- SC-06: no fixture constructs an unreadable (permission-denied) repository-tier file; the
  `[ -r ]` guard's protection against that specific failure mode is unverified by the suite
  (demonstrated by mutation, reported above).
- T-02 case12 / 1c: the suffix-hygiene regex's actual marginal behavior (valid `harness-` prefix,
  invalid suffix) has no discriminating test; case12 as written cannot tell the regex is present.

## Scratchpad baseline fidelity

Every conclusion above rests on the scratchpad copies behaving identically to the repo originals.
Diffed all four against the real files: `inject-expertise.sh` is byte-identical; `check-expertise.sh`,
`test-inject-expertise.py` and `test-check-expertise.py` differ **only in comments/docstrings**
(module docstrings and per-case `# ---` banners omitted from the retyped copies) — zero logic
diff. Confirmed by `diff` after the fact, not assumed.

## SCs not assessed, and why

This gate is scoped to T-02 and T-03 only. SC-02 (per-agent `check-domain.sh --resolve`) belongs
to T-01, not built this cycle. SC-03 and SC-08 are `verify: inspection`, not automated — no test to
cite. SC-07 spans all fifteen craft files plus every repository-tier file created, which depends on
T-04 (migration), not built this cycle. None of these are gaps in T-02/T-03; they are out of this
gate's scope by the plan's own sequencing.

## Boundaries observed

No source or test file in the repo was written. All mutation probes ran on scratchpad copies at
`/private/tmp/claude-501/-Users-molchairuangutai-GitHub-harness/070b3f94-b495-4deb-b352-6896cfb60ad3/scratchpad/probes/`.
`.harness/expertise/**` was read-only (the T-03 `verify:`'s own live check). Nothing committed or
staged.
