# T-04 (second rework, c2) — RED-first case (i): linked worktree, resolved-path assertion

## BLUF

Added `case_linked_worktree_main_checkout()` (case (i)) to
`test-post-merge-sweep.py`, run RED against pre-fix code (verbatim below), then GREEN
after the T-03 fix. The assertion turns on the **resolved main-checkout-root path** and
on **which milestone got closed** — never on a SKIP — satisfying the dispatch's explicit
requirement not to re-encode the fail-safe assumption the last run wrongly made.

## Fixture and what it proves

Main checkout `R` carries the LANDED copy of `FEAT-90-linked` (status Done, milestone
810). A separate linked worktree `WT_CALLER`, branched from BEFORE that commit, carries
its OWN divergent, never-landed copy of the SAME feature id (status Review, milestone
811). The fixture-local bin dir is installed **inside `WT_CALLER`**, so BIN_DIR-derived
root resolves there — reproducing the relative-`core.hooksPath` scenario named in the
brief (harness-init `SKILL.md:73/:78`). A third worktree, `dest`, is the actual terminal
worktree eligible for sweeping, added from R's landed commit. The sweep is invoked with
`cwd=WT_CALLER`.

## RED (measured, verbatim, against today's pre-fix code)

```
FAIL: (i) RESOLVED-PATH PROOF: the main-checkout root used for feat_dir is R, the ACTUAL main checkout — never WT_CALLER, the linked worktree the script happens to run from — resolved_main=None repo='/var/folders/.../tmpg3_4ebud/R' wt_caller='/var/folders/.../tmpg3_4ebud/WT-CALLER' stdout='post-merge-sweep: resolved repository root: /var/folders/.../tmpg3_4ebud/WT-CALLER\ngh-sync: no github.board configured — station writes are not attempted\ngh-sync: no parent recorded — closing milestone only\ngh-sync: milestone #811 closed\n...'
FAIL: (i) the milestone close call reached gh for R's LANDED milestone (810) — log='auth status\napi rate_limit --jq .resources.graphql.used\napi -X PATCH repos/acme/repo-x/milestones/811 -f state=closed\napi rate_limit --jq .resources.graphql.used\n'
FAIL: (i) DIVERGENCE PROOF: WT_CALLER's own divergent milestone (811) was NEVER closed — the sweep did not write into the wrong copy — log=(same, milestones/811)
```

This is exactly the operator's ruling, measured, not assumed: pre-fix `feat_dir`
resolves under `WT_CALLER` and **exists there** (`os.path.isdir` is True, no SKIP branch
taken at all) — the sweep silently ships against milestone 811, the divergent WRONG
copy, while R's actual landed milestone 810 is never touched.

## GREEN (after the T-03 fix)

```
PASS: (i) sweep exits 0 when invoked from inside a linked worktree
PASS: (i) BIN_DIR-derived root resolves to the LINKED WORKTREE it actually runs from, not the main checkout
PASS: (i) RESOLVED-PATH PROOF: the main-checkout root used for feat_dir is R, the ACTUAL main checkout — never WT_CALLER, the linked worktree the script happens to run from
PASS: (i) the milestone close call reached gh for R's LANDED milestone (810)
PASS: (i) DIVERGENCE PROOF: WT_CALLER's own divergent milestone (811) was NEVER closed — the sweep did not write into the wrong copy
PASS: (i) the terminal worktree under R was removed, proving feat_dir was found and ship succeeded against the correct main-checkout copy
```

## Verify (verbatim, cross-checked against `plan.yaml:446-447`)

```
python3 .claude/skills/harness/bin/test-post-merge-sweep.py
```
Tail: `EXIT=0` after `PASS: (i) the terminal worktree under R was removed...` — **47
PASS**, 0 FAIL, exit 0 (was 41 pre-rework; +6 new case-(i) assertions).

## Gates (measured this run)

| Gate | Result |
|---|---|
| `python3 .claude/skills/harness/bin/test-post-merge-sweep.py` | 47 PASS / exit 0 |
| `python3 .claude/skills/harness/bin/test-hooks-install.py` | 29 PASS / exit 0 (unchanged) |
| `python3 .claude/skills/harness/bin/test-worktree-terminal.py` | 34 PASS / exit 0 (unchanged) |
| `.claude/skills/harness/bin/check-state.sh` | exit 0, zero violations |
| `.claude/skills/harness/bin/run-unit-tests.sh` | exit 0, zero `^FAIL` — run twice (background, no pipe on `$?`): `.../run-unit-tests.sh > /tmp/rut2.out 2>&1` exit 0; `.../run-unit-tests.sh > /tmp/rut3.out 2>/tmp/rut3.err; echo $? > /tmp/rut3.exit` → `0` |

## Open questions

- None blocking. Same advisory as the T-03 receipt regarding a transient, non-reproducing
  `test-validate-digest.py` interleaving artifact seen in one of three concurrent
  full-suite runs — Q3 stays CLOSED per the dispatch.

## Files touched

- `.claude/skills/harness/bin/test-post-merge-sweep.py`
- `.claude/skills/harness/bin/post-merge-sweep.sh` (shared with T-03; the fix case (i)
  grades)
