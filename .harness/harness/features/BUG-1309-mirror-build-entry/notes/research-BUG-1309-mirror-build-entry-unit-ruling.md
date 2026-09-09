# T-07 unit `not-applicable` — recorded as D-12, D-10 reconciled

**Recorded.** `plan.yaml` carries a new `D-12` (`dec: DEC-217`) declaring the `unit` kind
NOT-APPLICABLE for T-07's retention branch, and `D-10`'s `choice` was amended minimally so it no
longer calls the same cell a gap. Decisions 11 → 12; tasks unchanged at 12; `panel` and `approval`
byte-identical. No task text needed amending. **The DEC-217 sibling this note originally
recommended is WITHDRAWN — panel c2 finding 1 falsified the recurrence premise it rested on; see
"Recommendation" below for the corrected call.**

**Corrected 2026-09-07, panel c2 (findings 1 and 4).** Two claims in the sections below were wrong
and are fixed in place: the retention test is at `post-merge-sweep.sh:228`, not `:222`, and the
heredoc-hosted family is TWO scripts, not four. `D-12`'s own text carries both corrections.

## What was verified at source, not taken on trust

- `post-merge-sweep.sh:29` opens `python3 -I - <<'PYEOF'` and `:293` closes it — the whole Python
  body, one heredoc. The retention arm is the `sync_enabled` block at `:221-228`, its retention test
  the `elif entry not in {...}` at **`:228`** — `:222` is only the `entry = …` read that feeds it
  and `:223` the era-exempt gate above it. (This bullet said `:222` until panel c2 finding 4;
  re-derived at source, `post-merge-sweep.sh:214-232`.) Nothing there is importable; no
  `tests/unit/**` file can reach it without extracting the body into a module.
- T-07's eight integration cases exist and pass: `python3 tests/integration/test-post-merge-sweep.py`
  prints 8 `PASS: T-07 …` lines, including the era pair (`era-exempt absent build_entry is swept`,
  `era-exempt recovery-required keeps the worktree`).
- The red-proof and its owner: `T-10` (plan.yaml `T-10`, `status: ready`) owns
  `tests/integration/test-hooks-install.py`; its `intent:` states the case is RED at HEAD **and the
  production code is correct**, tracing the cause to `_commit_feature` writing no `build_entry`
  against `github.sync: true` — i.e. T-07's retention branch engaging.
- The plan carries **no `test_matrix` key** (grep: no matches). The matrix is `harness.json`'s, read
  by the qa gate from `change_type:`; T-07 is `change_type: bugfix` touching runtime code, so
  DEC-217's `touches_runtime_code` leg fires and the `unit` floor is what this ruling dispositions.
- **`BRIEF.md` does not contradict the ruling.** The retention criterion is `SC-06` with
  `verify: automated  evidence: integration`, and the `## Constraints` DEC-217 line already records
  that the runtime surfaces here "are Python and Bash under `.claude/skills/harness/bin/`, whose
  standing beds are all in `tests/integration/`". Nothing to report as a conflict.

## The D-10 reconciliation — what changed, and why it was needed

**(a) Yes, it contradicted.** "recorded as a gap rather than papered over" asserts an owed-but-unfilled
cell; the operator's `not-applicable` asserts nothing is owed. A goal-check reading D-10 alone would
have seen standing debt. The amend is one sentence-tail, pointing the disposition at D-12:

> …and its DISPOSITION is D-12: the unit kind there is NOT-APPLICABLE, never an owed test recorded
> as a gap.

**(b) The citation was corrected inside the same amend**, per instruction — `post-merge-sweep.sh:29-43`
→ `:29-293`. `29-43` named only the import block and understated the heredoc by 250 lines, which is
the load-bearing fact; a reader checking `29-43` would not see that the body never closes there.
Everything else in D-10 is byte-unchanged (`because:` untouched).

## No task text needed amending

- **T-07** (`intent:`, plan.yaml T-07) mentions no unit test and no matrix cell.
- **T-11** scopes itself in its first line to "the unit floor the test matrix requires for T-02,
  T-03, T-04 and T-06" — T-07 absent — and its `files:` are the two `tests/unit/` files only. Its
  one T-07 reference (`post-merge-sweep.sh:223` as a branch BE-10 also covers) claims no obligation.
  Product lead's pre-check confirmed, not assumed.

## Recommendation — WITHDRAWN. Do not write a DEC-217 sibling

**The recurrence premise was false, and it was the whole load-bearing half of the argument.** This
section claimed four bin scripts host their entire Python body in a shell heredoc. The true set is
**TWO**, re-derived at source 2026-09-07:

- `post-merge-sweep.sh:29-293` — `python3 -I - <<'PYEOF'`, the whole body on stdin.
- `bash-write-guard.sh:42` — `python3 -c '… exec(compile(sys.stdin.read(), …))' … <<'PY'`, the same
  shape reached with the payload moved to the `HOOK_PAYLOAD` env var so the heredoc can own stdin.

The other two named here are **counter-examples, and they are the repo's own documented rejection
of the shape**: `gh-close-gate.sh:59` and `plan-sign-gate.sh:43` both carry the comment *"THE
DECISION LIVES IN A FILE, NOT A HEREDOC"*, and both `exec python3 "$(dirname "$0")/<name>.py"` at
`:79` and `:62`. Their stated reason is mechanical, not stylistic: a `python3 - <<'PY'` consumes the
very stdin the hook's JSON arrives on.

**What that reverses.** A standing DEC entry is warranted when a shape recurs and will keep
recurring. Here the shape is **receding**: of four candidates, two have already been converted to
the decision-in-a-file form, deliberately and with the reason written down, and both survivors are
convertible by the same move — `bash-write-guard.sh` already proves the payload can travel by env,
which is the only thing the heredoc was buying. A DEC that exempts a shape the repo is actively
retiring would outlive its subject and be cited later as a licence to skip the `unit` floor on any
awkward surface, which is precisely the failure `D-12`'s own "WHAT THIS IS NOT" paragraph guards
against. Two instances with a known in-repo remedy do not earn the operator's attention at DEC
level; they earn a chore.

**Corrected recommendation, in two parts.**

1. `D-12` stands **plan-local** and needs no sibling. Its footing is DEC-217's Over clause plus the
   structural fact that `post-merge-sweep.sh`'s body admits no import at all — neither of which
   needs a new entry to be true. If the same cell arises in another feature, that plan records its
   own `D-NN` on the same two feet, which is cheap and is bounded by the surface it names.
2. The generalisable fix is **not an exemption but the conversion**: extract the two surviving
   heredoc bodies into `.py` files beside their shells, exactly as `gh-close-gate.sh` and
   `plan-sign-gate.sh` already do, which removes the unreachable-`unit` shape instead of blessing
   it. That is **backlog, not this feature** — it is a runtime change to two DEC-174 enforcement
   surfaces, priced by DEC-174's *"library a gate calls"* clause (`DECISIONS.md:4377-4380`) as a
   main-session-direct cutover proven by an identical violation set before and after. Recorded here
   as a chore to raise, not as work this plan takes on.

**On the extraction as an escape from D-12:** DEC-174 does **not** forbid it — finding 3 was right
about that, and `D-12`'s `because:` no longer claims otherwise. What refuses it inside this feature
is DEC-217's Over clause alone: an extraction whose only purpose is to satisfy a directory label.

`dec:` was set to `DEC-217` rather than `none`: the field cites the governing authority (D-10 cites
the same), and minting an id for an unwritten entry would dangle. With the sibling withdrawn,
`DEC-217` is the permanent value — there is no entry to repoint it to.

## Verification run

```
$ python3 .claude/skills/harness/bin/check-plan-routes.py \
    .harness/harness/features/BUG-1309-mirror-build-entry/plan.yaml
MANIFEST /Users/molchairuangutai/GitHub/harness/.harness/team-config.yaml
OK T-01 granted to harness-backend-dev, harness-dev-ops, harness-qa
OK T-02 granted to harness-backend-dev, harness-dev-ops, harness-qa
OK T-03 granted to harness-backend-dev, harness-dev-ops, harness-qa
DEVIATION T-04 .claude/skills/harness/bin/gh-sync.py, tests/integration/test-gh-sync.py granted to harness-backend-dev, harness-dev-ops, harness-qa but declared main-session-direct
OK T-05: declared main-session-direct (.claude/settings.json, .claude/skills/harness/templates/settings.snippet.json, .omp/extensions/harness-hooks.ts ungranted)
DEVIATION T-06 .claude/skills/harness/bin/check-state.sh, .claude/skills/harness/bin/feature_schema.py, tests/integration/test-check-state.py granted to harness-backend-dev, harness-dev-ops, harness-qa but declared main-session-direct
DEVIATION T-07 .claude/skills/harness/bin/post-merge-sweep.sh, tests/integration/test-post-merge-sweep.py granted to harness-backend-dev, harness-dev-ops, harness-qa but declared main-session-direct
OK T-08: declared main-session-direct (.claude/skills/harness/references/github-mirror.md, .claude/skills/harness/SKILL.md ungranted)
OK T-09 granted to harness-documentor
DEVIATION T-10 tests/integration/test-hooks-install.py granted to harness-backend-dev, harness-dev-ops, harness-qa but declared main-session-direct
OK T-11 granted to harness-backend-dev, harness-dev-ops, harness-qa
DEVIATION T-12 .claude/skills/harness/bin/gh-sync.py, tests/integration/test-gh-sync.py granted to harness-backend-dev, harness-dev-ops, harness-qa but declared main-session-direct
0 violation(s) across 1 plan(s)
exit=0
```

`DEVIATION` on the six carve-out tasks is the expected DEC-174 output; only `VIOLATION` gates.

**`panel` and `approval` untouched — proven, not asserted.** Raw top-level block slices hashed
before and after both writes (`/tmp/bug1309_block_hash.py`, `yaml.safe_load` in the same run):

| block | before | after |
|---|---|---|
| `approval` | 898 bytes, `sha256=b6515d5c…0299dff6` | 898 bytes, `sha256=b6515d5c…0299dff6` |
| `panel` | 6640 bytes, `sha256=5043db66…018d346a` | 6640 bytes, `sha256=5043db66…018d346a` |
| decisions | 11 (D-01…D-11) | 12 (D-01…D-12) |
| tasks | 12 | 12 |
| 4 ruling ids → live findings | True | True |

Only `panel`'s line range moved (158-288 → 189-319), as D-12 sits above it. All four operator ruling
ids still resolve to findings present in `panel.findings`.

## Open questions

- **Q1 (non-blocking), RE-PUT on the true set of two.** Superseded: the original Q1 asked whether to
  write a repo-wide DEC-217 sibling on the premise that four bin scripts share the heredoc shape.
  Only two do (`post-merge-sweep.sh:29-293`, `bash-write-guard.sh:42`) and the other two document
  rejecting the shape and `exec` a `.py` file, so the recommendation is **withdrawn** — see
  "Recommendation" above. What is left for the operator is narrower: **should the conversion of the
  two surviving heredoc-hosted gates be raised as a backlog chore, or is the shape accepted where it
  stands?** Either answer leaves `D-12` intact and plan-local; neither is needed before signature.
  The full closeout, with the four cycle-2 finding ids, is
  `notes/research-BUG-1309-mirror-build-entry-panel-c2-closeout.md`.
