# Delta review — F-1 refusal matrix, F-3 grade — review_sha aab31504

Worktree used throughout: `.claude/worktrees/harness/FEAT-51-claude-code-lifecycle-safety`
(confirmed `git rev-parse HEAD` == `aab31504560627044a4d03cdcad611d5947d0b3e` before any check).

## F-1: CLOSED

`diff <(git show fa5ce88e:.../validate-digest.py) <(git show aab31504:.../validate-digest.py)`
— exactly one file changed, 27 insertions / 19 deletions, both hunks inside the same ~35-line
block (the release gate + the `if _kids:` refusal). Nothing else in the 1785-line file moved.

The real fix: the release condition changed from an unconditional "release unless the earlier
accepted-SUSPENDED branch already returned" to `_keep_parent = bool(_kids and _return_verdict
not in VERDICTS)`, and the refusal condition is `if _kids:` again (narrowed
`_return_verdict in VERDICTS` check moved *inside*, gating only the printed message, not
whether the block fires or whether children_refusal_lines/release-command print).

**Six-case matrix, run against the shipped `aab31504` binary** (scratch root via
`inflight_registry.claim()`, parent `harness-eng-lead`/dispatcher `Feat51Build`, child
`harness-frontend-dev`/dispatcher `harness-eng-lead`, feature `FEAT-TEST`; registry re-read
from disk after each run, never inferred from exit code):

| case | payload | rc | parent_live (disk) | child_live (disk) | children_refusal_lines |
|---|---|---|---|---|---|
| 1 absent key | no `last_assistant_message` | 2 | **True** | True | yes |
| 2 null | `last_assistant_message: null` | 2 | **True** | True | yes |
| 3 unparseable | text with no `VERDICT:` line | 2 | **True** | True | yes |
| 4 SUSPENDED accepted | `VERDICT: SUSPENDED` + correct `awaiting` | **0** | **True** | True | n/a (early accept) |
| 5 terminal w/ live child | `VERDICT: PASS` | 2 | False (terminal release fires) | True | yes, incl. `release --agent harness-frontend-dev --feature FEAT-TEST` |
| 6 no live children, SUSPENDED | no child claim; text `VERDICT: SUSPENDED` | 2 | False (nothing to protect) | n/a | no — falls through to schema `validate()`, which rejects `SUSPENDED is 'SUSPENDED'; must be exactly one of ['BLOCKED','ESCALATE','FAIL','PASS']` |

Cases 1, 2, 4 also independently confirmed via the shipped suite:
`python3 test-validate-digest.py` at the pin — **ALL PASSED** (24/24 T-09, 10/10 T-51 incl.
`_t51_accepted`, `_t51_terminal`, `_t51_missing_message`, `_t51_no_child`,
`_t51_omitted_child`, `_t51_member`). Cases 3 and 6 have no existing test — both were
verified independently above, no shipped coverage gap closed by my own run (worth a QA note,
not a `must_fix`: nothing regresses silently there today, but nothing pins it either).

**Discrimination proof against `fa5ce88e`** (same payloads, same fixture, `fa5ce88e`'s
`validate-digest.py` `exec()`'d in-process with `__file__` spoofed into the real bin dir so
`import inflight_registry` resolves — same technique as the premise-check note's P2):

| case | fa5ce88e rc | fa5ce88e parent_live | discriminates? |
|---|---|---|---|
| 1 absent | **0** | **False** (released) | **yes** — rc and claim state both flip |
| 2 null | **0** | **False** | **yes** — same |
| 3 unparseable | 2 | **False** (released) | **partially** — rc does NOT discriminate (both 2); the schema validator's own "no VERDICT: line" error independently produces exit 2 on the old binary even though the `_kids` refusal never fired. The **claim-liveness** is what discriminates: fa5ce88e released the parent's claim before ever reaching the schema check; aab31504 keeps it live. Reporting this literally per instruction: **case 3 is non-discriminating on exit code alone** and the exit-code-only regression test a future author might reach for would not catch a regression back to the old release-before-check order. The claim-state assertion is the one that must be kept.

## F-3: CLOSED

`code-grade.py .claude/skills/harness/bin/quarantine.py` at `aab31504` — **13/13 PASS, zero
FAIL** in the file:

| function | line | cyclomatic | cognitive | ABC | grade | bar | result |
|---|---|---|---|---|---|---|---|
| `_quarantine_containment` | 50 | 4 | 4 | 8.4 | 4 | 4 | PASS |
| `_canonical_for_listing` | 98 | 3 | 3 | 7.1 | 5 | 4 | PASS |
| `cmd_list` | 112 | 4 | 4 | 16.4 | 4 | 4 | PASS |
| `_adopt_target` | 158 | 3 | 4 | 11.4 | 4 | 4 | PASS |
| `_refuse_adopt` | 175 | 1 | 0 | 3.2 | 5 | 4 | PASS |
| `_adopt_payload` | 185 | 2 | 1 | 5.7 | 5 | 4 | PASS |
| `cmd_adopt` | 197 | 4 | 3 | 9.8 | **4** (driver: abc) | 4 | **PASS** — was grade 3 at fa5ce88e |

`cmd_adopt` moved from grade 3 (fail) to grade 4 (pass, driver ABC=9.8) purely by extracting
`_adopt_target`/`_refuse_adopt`/`_adopt_payload`; none of the three extracted helpers, nor the
pre-existing `_quarantine_containment`/`_canonical_for_listing`/`cmd_list`, regressed below
bar — every one of the named functions is grade 4 or 5.

Whole-diff form, `code-grade.py --base 0bc57c88 --head aab31504` — 76 functions graded,
**3 `RESULT: FAIL`, all `SEVERITY: med` (grade 2), zero high/critical**:

- `plan-sign-gate.py:309 _invocation` (grade 2, driver cognitive) — pre-existing, same
  line/grade the premise-check note already reported at `fa5ce88e`.
- `plan-sign-gate.py:353 quarantines` (grade 2) — **explicitly named in this dispatch as
  already signed and not to be relitigated.**
- `test-quarantine.py:109 case_1_2_adopt_plan_unions_tasks_and_preserves_approval` (grade 2,
  test code, bar 3) — pre-existing.

None of the three is new; none is in `quarantine.py`; none blocks (grade-2 never blocks per
protocol). **F-3's fix introduced nothing new at high or critical.**

## Regression surface — all four confirmed at source, `aab31504`

1. **plan.yaml still delegates to `plan-merge.py apply`, exit 7/8 verbatim.**
   `_run_plan_merge` (`quarantine.py:132`) subprocesses `plan-merge.py apply --file <canonical>
   --proposal <quarantined>`, writes the child's stdout/stderr through unmodified, returns its
   raw `returncode`; `cmd_adopt` (`:197`) returns that code immediately on nonzero. Confirmed
   by reading the function body, not by memory of the docstring's claim.
2. **The other three canonical artifacts still go through `harness_merge.locked_update`.**
   `_adopt_payload` (`:185`): `if os.path.basename(canonical) == "plan.yaml": return
   _run_plan_merge(...)`; else `harness_merge.locked_update(canonical, lambda _base,
   payload=payload: payload)`.
3. **A successful adopt still leaves the quarantine directory standing.** `cmd_adopt` has no
   `shutil.rmtree`/deletion call anywhere in its body or its callees; only `cmd_discard` calls
   `shutil.rmtree`. Confirmed by reading the full file, not the docstring's claim of it.
4. **D-11 precedence (FEAT-41 editor-route denial before the quarantine branch on
   `plan.yaml`) holds in both gates, read at the pin, not from memory:**
   - `plan-sign-gate.py` tail: `if denies(cmd): ...; sys.exit(2)` runs and can exit **before**
     `quarantine = quarantines(cmd, ...)` is even computed — textual ordering, not inference.
   - `check-domain.sh`: the FEAT-41 plan.yaml-exclusive-writer block (`if not _post and _tool
     in (...) and _reached_plan: ... sys.exit(2)`) sits immediately **before** the FEAT-51
     quarantine-redirect block that also matches `plan.yaml`'s basename. Since the first block
     unconditionally denies every editor Write/Edit/NotebookEdit reaching `plan.yaml`
     (orphaned or not), the second block's `plan.yaml` case is provably unreachable via editor
     tools — the quarantine redirect for `plan.yaml` can only ever be exercised through
     `check-domain.sh`'s Bash-command path, never the editor route. This is the same shape as
     the failing-panel pin, unchanged by either fix.

Corroborating, not owned by me: `test-quarantine.py` at the pin — 35/35 PASS including
`case10: cross-feature adopt via symlinked quarantine exits 2` and `case13: a
quarantine-shaped file under a foreign root exits 2`, both direct exercises of the F-2
containment rule.

## Trip-over note on F-2 (not my scope, reporting per instruction — nothing new found)

Read `plan-sign-gate.py`'s `_quarantine_artifact` (new in this fix) alongside its
`fa5ce88e` predecessor. The **actual** original defect was narrower than "recognised the
adopt route only on a literal quarantine path segment": the old code derived `rel` via
`_checkout_rel(value)`, a **substring search** for `.harness/` inside the raw `--file`
argument string with no `realpath`/root anchoring at all — an attacker-built
`/tmp/x/.harness/r/features/F/quarantine/w/feature.json` string-matched the regex outright.
The new `_quarantine_artifact` realpaths both the candidate and `ROOT`, and the regex's
`fullmatch` requires the string begin with literal `.harness/` — a `rel` that starts with
`../` (candidate resolves outside root) can never match that anchor, so the explicit
dot-dot guard `quarantine.py` uses is not needed here for the same protection to hold. I
did not find a remaining unanchored path in either file. This differs slightly from how
F-2's own framing describes the original bug; flagging the distinction for whoever owns
that verdict, not asserting a new finding.

## Verdict

Both F-1 and F-3 are **closed** at `aab31504`. No new high/critical introduced by either
fix. One advisory (not `must_fix`): cases 3 and 6 of the F-1 matrix have no shipped
regression test; case 3 in particular would not be caught by an exit-code-only test since
both the old and new binary return 2 for that shape — only the claim-liveness assertion
would catch a regression there.
