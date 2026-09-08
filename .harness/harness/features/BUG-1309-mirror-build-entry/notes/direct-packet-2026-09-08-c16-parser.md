# Main-session-direct implementation packet — R-4, the comprehensive parser fix — BUG-1309

**Implementation can begin immediately.** One function's worth of code and seven test cases, all
inside the DEC-174 enforcement carve-out, all now specified by the amended signed plan. The one
outstanding operator signature (SC-11, below) decides how the `--abort` allow is *graded*, not what
the code must do — it does not block this work, and it does block the ship.

**Who runs this: the main session, by hand.** No squad may execute any of it (`plan.yaml` lanes rows
47-49 and 73-75; T-05 carries `execution_mode: main-session-direct`). The orchestrator has moved T-05
and the feature back to station `building` and has touched no code.

**Checkout:** `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1309-mirror-build-entry`,
branch `feat/BUG-1309-mirror-build-entry`. Do not move HEAD.

**Authority is the amended plan, not this note.** Where the two differ the plan wins: T-05 `intent`
step 2's three new clauses and its grade clause, T-05 `verify` (26 gated names + the grade
assertion), and decisions `D-16` / `D-17`. Amended today by pm —
`notes/research-BUG-1309-planamend-c16.md`. Navigate by task id and field name; line numbers move.
The rulings this implements are transcribed in `notes/rulings-2026-09-08-c16-parser.md`.

---

## Edit A — `merge-gate.py` `git_merge`: close the CLASS, keep the fail-closed net, exempt control ops

**File:** `.claude/skills/harness/bin/merge-gate.py`, `git_merge` at lines 46-75. Nothing else in the
file is in scope — `main()`, `feature_for()`, `head_branch()` and `deny()` are unchanged by this edit.

**Today** (verbatim): two closed sets of option NAMES — `global_values` for the pre-subcommand walk,
`merge_values` for the post-`merge` walk. Every option outside them is treated as valueless, so its
VALUE is read as the next positional token. Measured against real git 2.50.1 and the real hook at
`e374c9a2` (`/tmp/bug1309-c15-verify.py`):

| command | real git | gate today | why |
|---|---|---|---|
| `git merge -F <file> feature/test` | **MERGES** | silent allow | `-F` skipped, `<file>` returned as the ref, no feature owns it |
| `git merge --cleanup strip feature/test` | **MERGES** | silent allow | `strip` returned as the ref |
| `git --attr-source HEAD merge --no-ff feature/test` | **MERGES** | silent allow | `HEAD` is the first non-option token, `!= "merge"` → `None` |
| `git merge --abort` / `--continue` / `--quit` | moves nothing | **deny** | `("git", None)` → `head_branch` falls back to the local branch → the receipt rule denies |

**Required, four clauses:**

1. **Value-taking options are a CLASS, in BOTH positions and BOTH spellings.** Pre-subcommand git
   globals and `git merge`'s own options, attached (`--opt=value`, `-C<dir>`) and detached
   (`--opt value`, `-C <dir>`). At minimum the detached forms `-F`/`--file`, `--cleanup`,
   `--into-name`, `-m`/`--message`, `-s`/`--strategy`, `-X`/`--strategy-option` after `merge`, and
   `--attr-source`, `-C`, `-c`, `--work-tree`, `--git-dir`, `--namespace`, `--config-env`,
   `--super-prefix` before it, must consume their value. **The mechanism is yours** — completing
   git's own documented sets, inverting the unknown-option default in the *global* position, or
   another shape entirely. What is pinned is the behaviour.
   **One judgement carried forward from the c7 packet, unchanged:** `--exec-path` has a bare form
   that prints and exits, so it is value-taking **only** in its attached `--exec-path=<p>` spelling.
   Consuming a following token for the bare form swallows `merge` and reintroduces a silent allow.
   Same for the optional-argument forms `-S`/`--gpg-sign` and `--log`: attached only.
   **Do not invert the unknown-option default AFTER `merge`.** There, an unknown option is a
   boolean; treating it as value-taking makes `git merge --no-ff feature/test` swallow its own ref.
2. **FAIL CLOSED on an unresolvable ref — keep it, deliberately.** When the command is a `git merge`
   and no ref token survives the walk, `git_merge` returns `("git", None)`, `head_branch` falls back
   to `local_branch(cwd)` and the local record decides. That is today's behaviour and it is now the
   specified behaviour (D-16): `git merge -F <file>` with `MERGE_HEAD` present concludes a real
   merge, so an unreadable ref must never buy a silent allow. **It must not widen**: attribution is
   untouched, one owner plus any amount of noise is not ambiguity, and an unreadable or
   non-matching record elsewhere in the scan imposes no refusal (`894adc0f`, after panel c5 failed
   `473d82cb`).
3. **Merge control operations are not merges.** When the token after `merge` is `--abort`,
   `--continue` or `--quit`, `git_merge` returns **`None`**, so `main()`'s
   `if not github.get("sync") or not merge_ref(command): return` guard exits 0 before any branch
   resolution — no permissionDecision object, on an owing branch as much as on any other. Decide
   this **before** clause 2's fallback, or the fallback denies them. This closes VF-03, a regression
   `e374c9a2` introduced.
4. **`git_merge` grades 4 or better.** At the current pin it is CYCLOMATIC 8, COGNITIVE 15, ABC 16.1,
   **GRADE 3 / BAR 4 / FAIL / severity high**. Adding three clauses to one `while` inside a `while`
   will make that worse, so decompose: a token-advance helper that consumes a detached value, a
   subcommand-locator over the globals, a ref-locator over the merge options. The bar binds
   `git_merge` and the helpers this change adds. **`main()` grades 2 and is out of scope** —
   pre-existing, carrying its own GRADE-2 reason comment, and excluded from T-05's grade assertion
   by name.

---

## Tests — seven cases in `tests/integration/test-merge-gate.py`

Use the file's existing `fixture()` / `gate()` / `check()` helpers and its conventions. **Append
after the existing cases; edit none of them.** The names are gated verbatim by T-05's `verify`
(26 names) — a renamed case is a red gate.

Every case is staged on the owing fixture `FEAT-9001-fixture-non-era` (no `build_entry`), in a root
whose `harness.json` carries `github.sync: true` and `github.repo: "acme/widgets"`, the same shape
the existing deny cases use.

1. **`T-05 merge -F detached value denies`** — `git merge -F <path> feature/test`. Assert
   `decision == "deny"` and that the reason names the fixture feature.
2. **`T-05 merge --cleanup detached value denies`** — `git merge --cleanup strip feature/test`.
   Same assertion.
3. **`T-05 global --attr-source before merge is still detected`** —
   `git --attr-source HEAD merge --no-ff feature/test`. Same assertion.
4. **`T-05 merge with no identifiable ref denies`** — `git merge --file <path>`, **no ref token at
   all**: the long spelling of `-F`, exercising clause 1 and clause 2 together. Assert
   `decision == "deny"`.
5. **`T-05 merge --abort on an owing branch allows`** — `git merge --abort`. Assert **no**
   permissionDecision object on stdout and exit 0.
6. **`T-05 merge --continue on an owing branch allows`** — same shape.
7. **`T-05 merge --quit on an owing branch allows`** — same shape.

**The staging detail that decides whether cases 4-7 mean anything.** They all reach the verdict
through `local_branch(cwd)`, not through a ref on the command line, so **the fixture's checkout must
be on the owing branch** — the same mechanism the two `gh outage` cases already rely on. If the cwd
resolves to any other branch, case 4 allows for the wrong reason and cases 5-7 pass vacuously
against both the old and the new code. Assert the staging, or reuse the outage cases' fixture path.

---

## Red before green — this is the discrimination evidence, not a nicety

All seven fail against `e374c9a2`. Add the cases **first**, run the file **before** touching
`merge-gate.py`, and keep the output:

```
cd /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1309-mirror-build-entry
python3 tests/integration/test-merge-gate.py      # expect: the 19 existing cases ok,
                                                  # exactly the 7 new names FAIL
```

Expected red, per form: cases 1-4 report `decision` absent where a deny is asserted (the parser
resolves a wrong ref or no merge at all); cases 5-7 report a deny where none is asserted. If any of
the seven is **green before the edit**, it is not discriminating — say so and re-stage it rather
than keeping it (T-05 `intent`, and the same rule SC-03 and SC-07 carry).

## Verification — run exactly these, in this order, after the edit

```
python3 tests/integration/test-merge-gate.py           # 26 ok lines, ALL PASSED, exit 0
python3 tests/integration/test-gh-sync.py              # unchanged: exit 0, 0 FAIL
python3 tests/unit/test-gh-sync-build-entry.py
python3 tests/unit/test-feature-schema-build-entry.py
python3 tests/unit/test-omp-hooks.py
python3 .claude/skills/harness/bin/merge-settings.py . --check \
  --template .claude/skills/harness/templates/settings.snippet.json   # 'all 9 prerequisites present (8 hooks'
python3 .claude/skills/harness/bin/code-grade.py .claude/skills/harness/bin/merge-gate.py --json
```

`git_merge` must read `"grade": 4` or better and `"result": "PASS"` in that JSON. Then run **T-05's
`verify:` block verbatim out of `plan.yaml`** — it must print `VERIFY-PASS`. That block, not the bare
invocations, is what the qa gate re-runs.

**Recommended, and worth the two minutes: the real-git end-to-end.** The suites drive the hook
through fixtures; the three silent allows were found by asking *does git actually merge?* against a
throwaway repo. `/tmp/bug1309-c15-verify.py` and `/tmp/bug1309-final-probe.py` were the orchestrator's
probes and may or may not survive in `/tmp`; re-run or re-create one that drives `merge-gate.sh` over
all four ruled forms plus the existing 14 deny forms and 9 preserved bounds.

**If you run the suites from inside an agent tool, prefix with `env -u HARNESS_AGENT_TYPE`** — the
tool's environment leaks into test subprocesses and reddens the plan-merge approval checks as a
phantom failure.

## What must NOT change

- The 19 existing cases in `tests/integration/test-merge-gate.py`, in particular the two
  malformed-record fences (`:128-150`) and every allow case.
- `main()`, `feature_for()`, `head_branch()`, `deny()`, `repo_pinned()` — including `main()`'s
  grade-2 reason comment.
- `gh_merge()` and the `gh pr merge` route, `nested_merge`'s depth cap, and the shell-variable
  indirection case: both remain out of scope by ruling R-2 and stay backlog rows.
- `plan.yaml` `approval:` — the main session's `sign-approval` verb only.
- `BRIEF.md` — approval-gated; see SC-11 below.

---

## After you land it — hand back, do not proceed

1. Commit code and tests (`[harness:t-05] …`, matching the existing commits).
2. `python3 .claude/skills/harness/bin/plan-merge.py set-task-station --file <plan.yaml> --task T-05 --station done`.
3. The mirror writes for this segment are **yours**, not the orchestrator's — the owner of a
   task-start and a phase-transition sync is decided by `execution_mode`
   (`references/github-mirror.md:42,44`), and this segment is main-session-direct. With
   `<feature-dir>` = `.harness/harness/features/BUG-1309-mirror-build-entry`, run from the **main
   checkout**, station argument lowercase:
   `gh-sync.py start-task <feature-dir> T-05` then `gh-sync.py status <feature-dir> building`.
   The mirror is never a gate; a failure here is reported, never a reason to stop.
4. Return to the orchestrator. The remaining sequence is **fixed and is the last cycle available**:
   re-pin `review_sha` at the new tip → `gh-sync.py status <feature-dir> review` → qa `test_matrix`
   re-run → review panel c17 scoped to the delta → pm goal-check of SC-04 (and SC-11 if signed) →
   extend UAT Step 3b with the three previously-allowed forms → operator SC-10 UAT → rewritten
   briefing → ship.

**Budget: `cycles_used` 15 of 16** after this remediation cycle. The re-validation round is the
sixteenth. A second failed implementation attempt exhausts it and the feature returns `BLOCKED`.

## Three operator acts are outstanding

1. **SC-11, or an exclusion sentence in SC-04 — blocking, and it needs a signature.** SC-04 read
   literally *mandates* the deny that R-4 clause 3 reverses: "a merge command issued for a feature …
   whose Build-entry outcome … is absent … is denied", and `git merge --abort` is a merge command.
   pm recommends a new criterion (drafted verbatim in `notes/research-BUG-1309-planamend-c16.md`):
   *SC-11: `git merge --abort`, `--continue` and `--quit`, issued on a branch whose feature owes a
   Build-entry receipt, each exit 0 with NO permissionDecision object; each assertion is
   DISCRIMINATING at `review_sha` against `git show e374c9a2:.claude/skills/harness/bin/merge-gate.py`.*
   The alternative is an exclusion sentence inside SC-04 — cheaper, but it edits a criterion three
   cycles of digests already grade. Declining both leaves a disclosed verification gap. **`BRIEF.md`
   is approval-gated: only the operator edits it, and it needs re-signing either way.**
2. **`plan-merge.py sign-approval`** — `amend` holds the approval bytes by design, so the plan reads
   `approved 2026-09-08` over T-05 text amended after that signature. Required before ship.
3. **SC-10 UAT** — `notes/uat-BUG-1309-mirror-build-entry.md`, Step 3b to be extended with `-F`,
   `--cleanup` and `--attr-source` once they deny. It must run before the worktree is released,
   because the script points at that checkout.
