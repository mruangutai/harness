# Plan fix c1 — the two blocking intent gaps are closed — BUG-1309

**Both rulings are now in the plan text, and the plan still routes clean.** Nine field amendments
across T-04, T-05, T-06, D-07 and D-08, plus three BRIEF clauses. Task count unchanged at 9,
decisions unchanged at 8, `approval.status: pending`, `## Approval` `pending`. **No new task was
needed.**

## Gap 1 — R1, a GitHub outage no longer denies a merge

`plan.yaml` T-05 step 3 now falls back to `git -C <cwd> rev-parse --abbrev-ref HEAD` when the `gh`
route fails, and step 5 has no read-failure deny at all (`plan.yaml:426`, `:440`, `:448`). A deny is
issued only when a resolved branch maps to a feature whose local `github.build_entry` is
`recovery-required` or absent, and its reason must name that local value — the tests assert the deny
reason does NOT carry the gh failure text. When nothing local condemns the merge the gate exits 0
and prints exactly one stderr line, given literally in the intent, opening `merge-gate: could not
verify this merge` and citing DEC-138.

D-07 (`plan.yaml:84-85`) now records the fail-open posture and cites DEC-138 verbatim at
`DECISIONS.md:2948-2952` plus the stated intent's out-of-scope merge-policy line. It keeps
`dec: DEC-174` and the gh-close-gate rationale unchanged.

Tests: the drafted "deny when the head branch cannot be resolved" case is **replaced** by two
offline cases through the existing `GH_BIN` override — (a) gh failing + current branch matching no
feature → exit 0, no `permissionDecision`, one stderr line; (b) gh failing + current branch mapping
to a feature owing a receipt → DENY grounded in the local record. Every other listed case kept.

## Gap 2 — R2, the refusal routes by station, not by merged-ness

T-04's absent-`build_entry` branch no longer mentions merged-ness. It asks one shared classifier —
`feature_schema.recovery_command_for(feat_dir) -> "open" | "recover-terminal"` — and emits one of two
literal refusal lines (`plan.yaml:329-345`). The `recover-terminal` line **contains no `open` token
at all**, deliberately: an operator who reads the word and runs it performs the forbidden act.

**The shared source, one home, three readers.** `BUILD_ENTRY_ERA_EXEMPT` and `recovery_command_for`
are defined by T-06 in `.claude/skills/harness/bin/feature_schema.py` (`plan.yaml:540-566`), beside
the `RUNS_AGENT_EXEMPT` precedent the plan already cited. That file — not `check-state.sh` — because
a bash-local literal is unreadable by `gh-sync.py` and `merge-gate.py`, and `check-state.sh` already
imports the module for INV-23 (`check-state.sh:1345`). T-04 and T-05 both state they define no
station rule and no era set of their own. Consequences accepted: `feature_schema.py` joins T-06's
`files:`, and T-04/T-05 gain `T-06` in `depends_on` (no cycle: T-06←T-01).

`recover-terminal` is named when ANY of: directory in the era set; plan station `review`/`done`; any
task recorded `done`. Absent/unloadable `plan.yaml` returns `recover-terminal` — the conservative
answer, since the irreversible act is the one `open` performs. D-08 records this and why.

New T-04 test: same feature.json (no `build_entry`) whose `plan.yaml` carries a task at `done` →
exit 2, stdout carries `recover-terminal`, and carries **neither** `gh-sync.py open` **nor** the bare
token `open` (both asserted; the first alone passes on a message that merely drops the `.py`). The
pre-change-copy demonstration clause and all existing cases are kept.

## Verifications

`safe_load` over the amended file: 9 tasks, 8 decisions, `approval: {status: pending}`, every
`verify:` still a literal `|` block (9 of them, `plan.yaml` lines 104/157/239/311/398/508/595/645/698)
and every value's tail intact. Neither task's `verify:` command was changed: T-04's greps
`"build entry"`, present in both new refusal lines; T-05 names the two suites the amended tests live
in. Both still name real behaviour.

```
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
0 violation(s) across 1 plan(s)
```

Exit 0. Same three DEVIATION rows as c0 — the expected DEC-174 carve-out output; T-06's row now also
lists `feature_schema.py`, which is granted-but-carve-out for the same reason `check-state.sh` is.

**Tool note:** the dispatch named `apply --proposal -`, which exits 7 CONFLICT on a changed value.
All nine writes went through `plan-merge.py amend --expect-sha256` (compare-and-swap), the tool's
route for replacing an existing field.

## BRIEF.md

- **SC-03 restated** (`BRIEF.md:90-96`): the command named by the refusal is chosen by the feature's
  own recorded station. Without this, R2's new test case is covered by no criterion.
- **SC-04 restated** (`:97-103`): every deny is earned by the local receipt; an unresolvable head
  branch under an unavailable `gh` is ALLOWED with one stderr line. The old text did not assert
  fail-closed, but it also could not have caught a fail-closed implementation.
- **No renumbering, no new SC** — still 10 REQ / 10 SC.
- **The 17 features** are folded into the **existing third `## Verification gaps` bullet**
  (`:140-147`), named KNOWINGLY UNRECOVERED, forward-only, operator-approved `recover-terminal`
  only. Chosen over `Out of scope` because that bullet already states the era-exempt boundary and a
  second home would be the near-duplicate convention the dispatch warned against; `Out of scope` is
  the operator's own words and adding a line there would read as a new operator ruling.

## Residual risk / open questions

- **T-04 and T-05 now depend on T-06.** T-06 was previously buildable in parallel with the gh-sync
  chain; it is now on the critical path for both refusals. No cycle, and the scheduler reads
  `depends_on`, so this is ordering cost, not correctness risk.
- **`recovery_command_for` reads `plan.yaml` from inside `feature_schema.py`**, giving a schema
  module a plan-reading responsibility. Contained by the lazy `harness_yaml` import; the alternative
  (a fourth module) buys nothing at three call sites.
- **Not re-graded here.** A separate goal-check follows; the c0 note is unmodified.

## Follow-up c1 — INV-37's own message adopted the shared classifier

**The residue is closed.** T-06 hosted `recovery_command_for` but its own INV-37 violation text still
read "run gh-sync.py open for it, or gh-sync.py recover-terminal --yes if it is already merged" — the
exact merged-ness discriminator ruling R2 rejects, in the task that defines the classifier. Only
T-06's `intent:` changed, amended under the same id via `plan-merge.py amend --expect-sha256`.

- **INV-37 now emits ONE line, command chosen by `feature_schema.recovery_command_for(feat_dir)`**,
  never by merged-ness, and never by a station test written inside `check-state.sh`. The `open`
  variant keeps the original wording with `run gh-sync.py open <feature-dir>.`; the
  `recover-terminal` variant reads "...and the feature's own record says the work is already under
  way or finished, so creating the mirror now would mean task sub-issues for completed work - run
  gh-sync.py recover-terminal <feature-dir> --yes." **Verified: the second variant contains no
  `open`-prefixed token at all** (`re.findall(r'\bopen\w*', …)` over that block → `[]`), the same
  rule T-04's second refusal line carries.
- **The station is read ONLY to choose the command.** Stated explicitly beside the fires-regardless
  bullet, so a later reader cannot fold the station back into the firing condition — the mirror of
  the "do not tidy this into INV-26" comment already there.
- **One test case added — THE MESSAGE DISCRIMINATOR**: violating fixture (not in the era set, sync
  true, no `build_entry`) whose `plan.yaml` carries a task at `done` → exactly one INV-37 line whose
  text contains `recover-terminal` and contains neither the substring `gh-sync.py open` nor the bare
  token `open`; both asserted, because the first alone passes a message that merely drops the `.py`.
  Every prior case and the classifier cases are kept; the first case's assertion is narrowed to the
  INV-37 prefix and the feature name, since its own station (`done`) now makes it a
  `recover-terminal` message.
- **`verify:` unchanged.** `grep -q INV-37` still names real behaviour: the `INV-37 <feat>:` prefix is
  identical in both variants, so the block still discriminates on the invariant firing at all, and
  the new command assertions live inside the test file it runs.

Post-amendment state: `yaml.safe_load` clean, 9 tasks / 8 decisions, `approval.status: pending`, all
9 `verify:` values literal `|` blocks, `check-plan-routes.py` exit 0 (3 DEVIATION lines, all the
expected DEC-174 carve-out shape, 0 violations).
