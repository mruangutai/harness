# Plan repair c1 — BUG-240 — all seven dispositions applied

**BLUF: done, all seven, in `plan.yaml` only.** Three fields amended through
`plan-merge.py amend` with compare-and-swap: T-01 `intent`, T-01 `verify`, T-02 `intent`.
`approval.status` still `pending`, `status: plan`, 2 tasks, no `panel:` key, decisions/lanes/
traces/files/change_type untouched. `check-plan-routes.py <plan>` → `0 violation(s)`, exit 0.
`git status --porcelain` in the worktree: `?? .harness/harness/features/BUG-240-workspace-hard-reset-guard/`
and nothing else — the feature dir was already untracked, and no tracked path is modified, so
`factory_workspace.py` and `test-factory-workspace.py` are byte-identical.

Acceptance one-liner output, verbatim: `pending plan 2 False`.

## (a) The seven dispositions

| # | Disposition | State |
|---|---|---|
| 1 | G1 fatal — delete the occurrence-count clause from case 7 | **done.** Behavioural half (exit 2 via argparse) and the three-spelling absence tripwire kept; the rationale is carried in the intent ("Assert NO occurrence count of anything, and do not restore one"), naming the three textual occurrences at :22/:39/:48 and calling the count an over-pin. The literal token is spelled as "the environment-lookup token used by run_git" so the acceptance probe `'os.environ' in intent` is `False`. "force-aligned" note kept |
| 2 | G2/Q1 — case 5 red for the right reason | **done.** Unconditional `setattr` + `missing = object()` sentinel try/finally (`setattr` back, else `delattr`); the `getattr(... ) is None` skip branch is deleted and the intent forbids reinstating it. Assertions unchanged (exit 2; no `fetch`/`reset`/`clone`; one non-empty stderr line containing tmproot and "control-plane", not "uncommitted") |
| 3 | Q5 — replace case 6 | **done.** Old identity-restatement case deleted; new case 6 named exactly `BUG-240 other harness checkout: onboarded but not the control plane is not refused`. Count still seven. Fixture: `.git` + `.harness/team-config.yaml` under `checkout_path(wr)`, `_control_plane_root` → a *different* tmpdir under the same sentinel discipline, plain `Recorder()` porcelain `""`, `run_main` as-is; asserts exit 0/None **and** a recorded `fetch` |
| 4 | G3/Q2 — SC-04 ordering | **done.** ONE check added to the existing **(B)** block (`tests/unit/test-factory-workspace.py:156-164`), named `BUG-240 existing checkout: refresh order is fetch, checkout default, reset --hard`. Shape mandated: filter calls to `clone/fetch/checkout/reset`, filtered sequence begins `("fetch","origin")`, `("checkout", DEFAULT_BRANCH)`, `("reset","--hard",f"origin/{DEFAULT_BRANCH}")`, no `clone`, last recorded call is the issue-branch checkout; `rec.calls[0:3]` explicitly forbidden |
| 5 | G4/Q3 — case 5's fleet fixture | **done.** The reason is named in the intent (`run_main` builds from `good_fleet_dict`, `REPO="acme/widget"`, `checkout_path` hardcodes `wr/widget`), then the route: copy `good_fleet_dict(os.path.dirname(tmproot))`, override `repos[0]["name"] = "someowner/" + basename(tmproot)`, `write_fleet`, drive `fw._main` through `run_main`'s own argv/monkeypatch idiom (save/restore `sys.argv` and `fw.run_git`, redirect streams, catch `SystemExit`), `--repo someowner/<basename> --issue 42`. tmproot is a child of an outer temp dir so `dirname(tmproot)` is inside the temp tree |
| 6 | T-01 `verify` back in agreement | **done.** 4 FAIL names + 4 ok names, literal `|` block preserved. `test "$rc" = 1` kept (the runner exits 1 on any failure) and paired with `grep -c '^FAIL  ' = 4`, which pins the count *and* catches any pre-existing check going red. Count-of-presence, so a grep that errors yields 0 ≠ 4 and fails closed |
| 7 | T-02 docstring sentence | **done.** One sentence added: the docstring paragraph must not contain `--force`, `--yes` or `FACTORY_FORCE`, because T-01 case 7 asserts their absence from the source text. `verify` and everything else in T-02 untouched |

## (b) Final case list and PRE-T-02 colour

| Case | Name | Pre-T-02 | Why |
|---|---|---|---|
| 1 | `BUG-240 dirty tracked: exits 2 before any fetch` | **FAIL** | no guard: exit 0 and `fetch` recorded |
| 2 | `BUG-240 dirty tracked: refusal line names the path and the uncommitted-work condition` | **FAIL** | no refusal is printed; stderr empty |
| 3 | `BUG-240 dirty tracked: the modified file survives byte-identical` | **FAIL** | real `reset --hard origin/main` destroys the modification — the defect itself |
| 4 | `BUG-240 ignored-only dirt: not refused` | ok | real git completes the refresh and lands on `factory/issue-42`; nothing refuses today |
| 5 | `BUG-240 self checkout: refused when clean, naming the self-checkout condition` | **FAIL** | the stand-in is installed unconditionally, so the tool reaches the destructive commands instead of refusing |
| 6 | `BUG-240 other harness checkout: onboarded but not the control plane is not refused` | ok | it asserts a NON-refusal, and the tool refuses nothing today; post-T-02 it stays green only because the predicate is path identity |
| 7 | `BUG-240 no bypass: the parser rejects --force` | ok | argparse already exits 2 on the unknown flag, and the three bypass spellings are absent at 6d969ed (grep rc 1) |
| (B) | `BUG-240 existing checkout: refresh order is fetch, checkout default, reset --hard` | ok | `_main`'s refresh branch (`factory_workspace.py:128-130`) already emits that exact triple, and the filter excludes the `status --porcelain` call T-02 adds |

4 FAIL / 4 ok → runner `sys.exit(1)` (test file `:279`), matching `test "$rc" = 1`.

## (c) Name agreement, both directions

Run with a throwaway script, `/tmp/bug240-plan-repair/check-names.py`, over the loaded
`plan.yaml` (`yaml.safe_load`, not the raw text):

- **verify → intent:** regex-extracted the 8 quoted names from `grep -q '^(FAIL  |ok    )<name>'`
  and required each to appear inside double quotes in `intent`. Result `[]` missing.
- **intent → verify:** regex-extracted every `"BUG-240 ..."` quoted string from `intent`
  (8 distinct) and required each to be one of the greped names. Result `[]` missing.

Both directions clean at 8 = 8. The first run caught a real defect this check exists for: three
names were line-wrapped inside the intent block scalar, so the intent's copy contained a newline
the grep pattern never could. Fixed by putting each case name on its own unbroken line
(`Case N - name "..."`).

## (c1b) The FAIL-count clause made well-founded — one field, T-01 `intent`

**Why:** the `grep -c '^FAIL  ' = 4` clause I added in cycle 1 was true only under an
unstated assumption — one `check()` call per case. The file's own house idiom splits one
fixture across several differently-named checks ((A) at `tests/unit/test-factory-workspace.py:149-154`,
(D) at `:183-189`, (F2) at `:221-229`), so a builder following it would emit three FAIL lines
for case 2 alone and the gate would redden a CORRECT implementation. Same over-pin family as
the occurrence-count clause disposition 1 deleted.

**Fix:** the clause stays (fail-closed backstop); the intent now *constrains* the count.
Appended to the paragraph that already mandates the eight verbatim names, three sentences-worth:
each of the eight names comes from EXACTLY ONE `check(name, cond, detail)` call, several
assertions conjoined into that one condition with a diagnosing detail; no splitting the way
(A)/(D)/(F2) do and no further check name in the file, because the verify asserts the total;
the total's purpose stated so a later reader does not delete it (pre-T-02 exactly four of eight
red — cases 1, 2, 3, 5 — and the total also catches a pre-existing check reddening as a side
effect of the new fixtures, since the real-git helper and the `_control_plane_root` stand-in
both mutate module and filesystem state other cases read); and the exception rule restated as
obeying the same arithmetic — one `check(name, False, str(exc))`, one line.

**Untouched:** T-01 `verify` byte-identical to cycle 1 (sha256
`dfd618270765c3fe7b2207dd1fd450e71152dcfbc5c202253006d394a2a767bb`), T-02, decisions, lanes,
approval, status, task count, every file outside `plan.yaml`.

**Re-checked:** acceptance probe `pending plan 2 False`; name agreement 8/8 both directions,
`[]` missing each way, every name still on its own unbroken line; `check-plan-routes.py <plan>`
→ `0 violation(s) across 1 plan(s)`; `git status --porcelain` →
`?? .harness/harness/features/BUG-240-workspace-hard-reset-guard/` only.

## Open questions

None blocking. Advisory: the goal-check's D-01-negative-half gap is now closed by case 6, so its
"Advisory, outside the intake" tail is discharged.
