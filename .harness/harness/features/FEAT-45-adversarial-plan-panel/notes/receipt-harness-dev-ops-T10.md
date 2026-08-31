# Receipt — harness-dev-ops — T-10 (assert the panel's wiring)

**BLUF: deliverable complete and correct; T-10's `verify:` does NOT currently exit 0.**
`test-plan-panel.py` (new, 24 checks, all pass) grades the panel's wiring across
`plan-panel.yaml`, `SKILL.md`, `harness-plan.md`, `team-config.yaml`, the
`.omp/agents/`+`.claude/agents/` roster census, `harness-validator-lead.md`'s frontmatter
`spawns:`, and `sync-agent-adapters.py`'s `SPAWNS` map — no doctrine defect found.
Registered as the last element of `run-unit-tests.sh`'s `UNIT_SCRIPTS`, after T-09's
already-committed `test-panel-findings.py` append (write-lock respected, no race). The
file and its registration are correct; the ONLY thing standing between T-10 and a green
verify is the pre-existing `test-harness-yaml-corpus.py` failure documented in §2, which
T-10 did not cause and is not authorized to fix.

## Verify (T-10's own `verify:`, cross-checked byte-for-byte against plan.yaml before running)
Re-measured directly, not taken on trust. The chain is
`python3 test-plan-panel.py && OUT="$(run-unit-tests.sh --kind unit)" && grep -q
'test-plan-panel.py' <<<"$OUT" && python3 - <<'EOF' [token-presence check]`. A bare
assignment `OUT="$(cmd)"` carries `cmd`'s own exit status, so the `&&` chain
short-circuits at the second link when the runner is non-zero — the grep and the token
heredoc never execute in that run.

Per-link results, each re-run individually and unconditionally:
1. `test-plan-panel.py` alone → **rc=0**, 24/24 checks pass.
2. `run-unit-tests.sh --kind unit` alone → **rc=1** (the pre-existing `test-harness-yaml-corpus.py`
   failure from §2 below; not caused by either of my files).
3. `grep -q 'test-plan-panel.py'` against the runner's captured output, run unconditionally
   (not chained) → **rc=0**, matches (`PASS test-plan-panel.py` is present).
4. The token-presence heredoc, run unconditionally against the test source → **rc=0**,
   prints `OK`.

**The verify block as a whole, run verbatim via `bash -c '<block>'; echo "verify rc=$?"`,
exits `1`** — the short-circuit at link 2, not a defect in links 1, 3, or 4. Each of those
three passes independently, so the test file and its `UNIT_SCRIPTS` registration are
correct and the token probe is satisfied on its own. The verify cannot go green until
`test-harness-yaml-corpus.py`'s SC-05 fixture (documented in §2) is fixed by whichever task
owns it.

## Acceptance §2 — the runner's real result, read correctly (not by tailing)
`OUT="$(run-unit-tests.sh --kind unit)"; RC=$?` → **RC=1**, **2** `^FAIL ` lines:
- `.claude/skills/harness/teams holds exactly 2 team definitions (SC-05)`
- `FAIL test-harness-yaml-corpus.py`

**Both are PRE-EXISTING**, established by `git stash -u` (removing both my files, including
the untracked `test-plan-panel.py`) and re-running: identical 2 `^FAIL ` lines, identical
names, `rc=1`. `test-harness-yaml-corpus.py`'s SC-05 case hardcodes "exactly 2 team
definitions" and plan-panel.yaml (T-02, already committed) is a third team file — that
count is now stale. This is `test-harness-yaml-corpus.py`'s own defect, not caused by
either of my two files, and I have not touched that file (out of scope; not in my `files:`
list). Recommend routing to whichever task owns `test-harness-yaml-corpus.py`'s SC-05
fixture to raise the count to 3.

## Acceptance §3 — falsifiability, 16 mutants, one case-representative check each
Method: `cp` the passing file to a backup, string-replace one needle/comparison per
mutation (never a doctrine file — all mutations are to the test's own source), run, capture
`FAIL` lines, restore from backup. All 16 mutants reddened **only** their target check(s);
every other check stayed green in that run. Final restore verified byte-identical via `cmp`.

| case | perturbed | check reddened |
|---|---|---|
| 1a | should-not-exist prompt needle | `(1a) …what should not be built at all` |
| 1b | scope prompt needle | `(1b) …which tasks serve no live requirement` |
| 1c | SKILL.md goalcheck needle | `(1c) …does this plan deliver…` |
| 2 (resolve) | scope-output persona match forced False | `(2) scope output …resolves to persona code-reviewer` |
| 2 (goalcheck) | `harness-pm` needle | `(2) …goal-check note path resolves to harness-pm` |
| 3 (outputs) | `{{cycle}}` needle | `(3) scope's loop_back outputs are empty or carry…` |
| 3 (playbook) | `c<cycle>` needle | `(3) the playbook names a c<cycle> suffix…` |
| 4a | inverted roster-exclusion predicate | `(4a) should-not-exist persona is not a canonical…` |
| 4c | persona compared against bogus string | `(4c) scope persona is a Validation squad member` |
| 5 | count `== 16` → `== 999` | `(5) .omp/agents/ holds exactly sixteen…` |
| 6 (halt) | inverted `then: halt` predicate | `(6) plan-panel.yaml carries no literal then: halt` |
| 6 (loop_back) | `escalate` needle mutated | both loop_back steps' `(6) …then: escalate and a max_cycles` (both call the same mutated line — correct, not a false positive) |
| 7b | `plan-panel` needle | `(7b) the Target state bullet names plan-panel` |
| 7c | `simplify` needle | `(7c) …still names the simplify pass` |
| 8a | persona compared against bogus string | `(8a) …frontmatter spawns: allowlist` |
| 8b | persona compared against bogus string | `(8b) …SPAWNS["harness-validator-lead"]…` |

Not separately mutant-tested (mechanically identical to an adjacent proven case, same
comparison code path): 1's `_normalize_prose` collapse behavior beyond the 1c needle;
4b/4d (same `_agrees`/list-emptiness mechanism as 4a/4c); 5's `.claude/agents/` count and
name-set equality (same `len(...) ==` and `set(...) ==` mechanism as the `.omp/agents/`
count); 2's empty-outputs skip branch (trivially `True`, no assertion to falsify).

## `git diff --stat` / `git status --porcelain` (post-mutant, final)
Only `run-unit-tests.sh` (modified, one-line append) and `test-plan-panel.py` (new,
untracked) changed by me. `plan.yaml` shows two `status:` field bumps
(T-11 → done, T-10 → building) that were already present before I started this task and
that I did not make — out of scope, left untouched.

## Notes for the next reader
- `check-domain.sh`'s domain guard denied an Edit whose section header used the bare
  filename `run-unit-tests.sh`; re-issuing with the full worktree-relative path in the
  section header resolved cleanly against my granted `.claude/skills/harness/bin/**`
  domain — a resolution artifact of the edit tool, not a real domain gap (P-14 pattern).
- SKILL.md's goal-check needle (case 1c) wraps across a markdown line break with `**`
  bold markers straddling it (G-09): matched by normalizing whitespace and stripping `*`
  before the substring test, rather than by widening the needle.
