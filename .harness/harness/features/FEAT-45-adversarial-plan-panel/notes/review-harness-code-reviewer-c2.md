# Code review — FEAT-45-adversarial-plan-panel — c2 (re-pinned SHA)

Scope: `git diff main...70fd441` (three-dot, merge-base `ba338d8`) — 66 files, +7114/-143, the
branch's own contribution. Working tree confirmed byte-identical to `70fd441` for every file cited
below (`diff <(git show 70fd441:<path>) <path>` empty in every case) — all line numbers are the pin's.
`70fd441` is a single commit, `fix: close FEAT-45 validation gaps`, on top of the c1 pin `c745d3a`.

Stage 1 (spec compliance against BRIEF.md/plan.yaml) precedes stage 2 throughout; findings below are
labelled by half, not by stage, per this dispatch's requested split.

## Half one — re-review of the SC-05 restructure (`check-state.sh` INV-32)

**The only functional change in `check-state.sh` between c1 (`c745d3a`) and c2 (`70fd441`) is the
elif-chain at lines 214–219** (`git diff c745d3a 70fd441 -- check-state.sh`: 10 insertions / 6
deletions, the rest is comment/DEC-number drift). Confirmed by diffing the two pins directly.

At `70fd441`, `check-state.sh:211-219`:
```
211        fid = str(item.get("id", "")).strip() or "<missing>"
212        severity = str(item.get("severity", "")).strip().lower()
213        disposition = str(item.get("disposition", "")).strip().lower()
214        if disposition == "resolved":
215            warn.append(f"INV-32: {feat} finding {fid} disposition resolved.")
216        elif fid in overruled:
217            warn.append(f"INV-32: {feat} finding {fid} disposition overruled.")
218        elif severity not in {"info", "low", "med"}:
219            bad.append(f"INV-32: {feat} finding {fid} is {severity or 'unrated'} and remains open without an operator overrule.")
```

Traced both cycle-0 M1 directions independently, by reading, then by live execution against the
actual script (`_root_env`-equivalent fixture, `.harness/team-config.yaml` marker + `CLAUDE_PROJECT_DIR`/
`HARNESS_PROJECT_DIR`, matching `test-check-state.py`'s own harness):

- **(a) absent `severity` key.** `item.get("severity", "")` → default `""` → `str("").strip().lower()`
  → `""`. `"" not in {"info","low","med"}` is `True`. With `disposition` defaulting to `""` (`!=
  "resolved"`) and `fid` not in `overruled` (empty set on no rulings), execution reaches line 218 →
  219, `bad.append(...)`. **Live**: `VIOLATION  INV-32: FEAT-INV32 finding PF-absent2 is unrated and
  remains open without an operator overrule.`, exit code 1.
- **(b) YAML-null `severity`** (`severity: null` / `severity: None` fixture). `item.get("severity",
  "")` returns the *stored* `None` (default only fires on a missing key), so `str(None)` = `"None"` →
  `.strip().lower()` = `"none"`. `"none" not in {"info","low","med"}` is `True` → same path to `bad`.
  **Live**: `VIOLATION  INV-32: FEAT-INV32 finding PF-null2 is none and remains open without an
  operator overrule.`, exit code 1.

Both reach the `bad` branch. **SC-05: CLOSED.** The restructure adds the `resolved`/`overruled` warn
branches SC-05 asked for (`disposition resolved` vs `disposition overruled`, each named distinctly,
matching `test-check-state.py:3011-3024`'s `_inv32_ruling_checks` and the base fixture at
`test-check-state.py:2982-2991`'s `case_inv32_unrated_severity_fails_closed`, unchanged and still
green). **M1's fail-closed property: PRESERVED, not regressed.** The old `c745d3a` code was
`if severity not in allow and disposition != "resolved" and fid not in overruled: bad` — a single AND.
The new elif chain is exactly that boolean's De Morgan expansion with the two now-excluded branches
promoted to their own explicit `warn` outcomes: the `bad` predicate (`disposition != resolved AND fid
not in overruled AND severity not in allow`) is unchanged in substance, only in how the excluded cases
are now reported instead of silently dropped.

**Ancillary, low-severity, NOT a regression from this diff** (pre-existing code, lines 193-206,
untouched by `c745d3a..70fd441`) — surfaced while tracing branch (b) above: the ruling-validation
loop has two independent `if` statements, not `if/elif`:
```
199    if not str(ruling.get("who", "")).strip() or not re.fullmatch(...):
200        bad.append(f"INV-32: {feat} ruling for {fid or '<missing>'} is unattributed or has an invalid date.")
201    if fid not in finding_ids:
202        bad.append(...)  # STALE OVERRIDE
203    elif str(ruling.get("ruling", "")).strip().lower() == "overrule":
204        overruled.add(fid)
```
An unattributed ruling (`who: ""`) that still names a *valid* finding id with `ruling: overrule` gets
BOTH `bad.append(...unattributed...)` (line 200) AND `overruled.add(fid)` (line 204), because the
`who`/`date` check does not `continue`. Live repro (`code_grade: n_a` not involved, this is check-state):
a HIGH finding `PF-open` with an unattributed overrule ruling produces
`VIOLATION  INV-32: ... ruling for PF-open is unattributed or has an invalid date.` **and**
`note       INV-32: ... finding PF-open disposition overruled.` — the per-finding line reads as a
legitimate override even though the override itself was just rejected two lines above. Exit code is
still 1 (the `VIOLATION` line still fires, so the plan stays blocked) — **this does not reopen M1 or
regress SC-05**, it is a pre-existing, unchanged-by-this-diff audit-trail wart: a human or tool
skimming only `note`-prefixed lines for "which overrides were accepted" would be misled about `PF-open`
specifically. `low`, half one, informational — flagging per dispatch's "MAY falsify" allowance in
reverse (confirms no regression, notes one adjacent pre-existing wart found while proving the negative).

## Half two — first-pass review of new enforcement code

### Risk 1 — SEC-01's conditional binding check: real gap, proven live. **HIGH.**

New in this diff (all `+` lines, `main...70fd441`): `validate-digest.py:864-865` (`_is_plan_review`),
`:868-878` (`_resolve_plan_review_path`), `:880-891` (`_pending_plan_status_error`), `:893-908`
(`_pinned_feature_review_error`), `:910-925` (`_pending_plan_review_error`), wired into
`code_grade_bound_to_review` at `:943-987` via the branch at `:955-956`:
```
955    if _is_plan_review(reviewed):
956        return _pending_plan_review_error(text, reviewed, code_grade, feature_dir)
```
called unconditionally for `harness-code-reviewer` at `:1216-1219`. The code-SHA path's final step,
`_branch_corroboration_error(...)`, sits at `:987` — the plan-review path never reaches it.

**The condition**: `reviewed` starts with the literal `plan:`. When it does, the ENTIRE code-SHA
binding path — `_read_review_sha`, `resolve_reviewed_commit`, the `head_oid != pin_oid` pin check, and
`_branch_corroboration_error` — is skipped and replaced by `_pending_plan_review_error`, which checks
only: `code_grade == "n_a"`; the named plan path resolves to `feature_dir/plan.yaml` (where
`feature_dir` is itself derived from the SAME digest's own `artifact:` line — self-referential, not
independently sourced); that plan's `approval.status == "pending"`; and that `feature.json` has no
real `review_sha` yet.

**What it fails to check**: nothing ties the digest to the checkout the reviewing agent is actually
running in. `_branch_corroboration_error` — built in wave 3 specifically to stop a digest's own
`artifact:` line from picking an unrelated feature's pin — is called on the code-SHA path (line
`987`) and NEVER on the plan-review path. Every fact `_pending_plan_review_error` checks is a fact
about the TARGET feature's own state (self-consistent: does ITS plan say pending, does ITS
feature.json lack a pin) — none of it is a fact about who is submitting the digest or from where.

**Concrete digest shape that slips through** (proven, not inferred — production call path,
`validate(agent, text)` with `feature_dir=None`, matching `hook_mode`'s and the CLI's actual
invocation, `.claude/skills/harness/bin/validate-digest.py:1608`/`:1570`):
```yaml
VERDICT: PASS
DIGEST:
  headline: fabricated - never reviewed FEAT-OTHER, submitted while dispatched elsewhere
  severity_max: none
  findings: 0
  must_fix: []
  code_grade: n_a
  reviewed: "plan:<realpath to ANY OTHER unrelated, genuinely-pending feature's plan.yaml>"
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: <that other feature's notes/review-harness-code-reviewer-cN.md>
```
Run against a fixture with a real, unrelated `FEAT-OTHER` (`approval.status: pending`, no
`feature.json`) via `python3 validate-digest.py harness-code-reviewer` (stdin) with
`CLAUDE_PROJECT_DIR`/`HARNESS_PROJECT_DIR` set to the fixture root: **`RC 0`, stdout `digest ok`.**
Any agent that needs a passing `harness-code-reviewer` binding check but never reviewed anything can
pick literally any other still-pending, unsigned feature in the repo (this checkout currently has
dozens — a `check-state.sh` dry run lists 30+ features "approved with no complete panel result
recorded", and pre-signature-pending ones are the intended everyday case for this new path) and cite
its coordinates. Nothing about the reviewer's actual branch, worktree, or dispatch is checked.
**This is precisely the shape SEC-01 wave 3 closed for the code-SHA path — DEC-207's escape hatch
reopens it for the pre-signature path wave 3 never anticipated.** `test-validate-digest.py`'s
`check_pending_plan_review` (`:1991-2010`) calls `validator.validate(..., feature_dir)` with an
EXPLICIT `feature_dir` argument, bypassing the digest-text-derived resolution entirely — the shipped
suite never exercises the production call shape (`feature_dir=None`) for this path, so this gap has
no regression test either.

### Risk 2 — `SKIPPED` reading as success in worst-wins roll-up: real gap, proven live. **HIGH.**

New in this diff: `_skipped_member_error` (`validate-digest.py:927-941`), consumed at the lead
roll-up loop `:1279-1314`:
```
1279        if isinstance(members, list) and members:
1283            for item in members:
1284                fields = parse_member_entry(str(item))
1285                skipped, skip_error = _skipped_member_error(fields)
1286                if skip_error:
1287                    err.append(skip_error)
1288                    continue
1289                if skipped:
1290                    continue          # <-- excluded from ranking entirely
1291                mv = fields.get("verdict")
...
1309            if worst and top in RANK and RANK[top] < RANK[worst]:
1310                err.append(...)       # only fires when `worst` is truthy
```
Per-member, this is correct and matches `harness-team/SKILL.md`'s new prose ("Skips are explicit
records, never verdicts, and do not enter worst-wins") and `SPEC.md:1613-1618`'s updated template
text — a mixed team (some ran, one skipped) is validated correctly (`test-validate-digest.py:547-568`).

**The gap is at the team level, not the member level**: when EVERY member entry is `status: skipped`,
the loop's `worst` variable never gets set (stays `None`, initialised at `:1282`), so the final
cross-check at line `1309` (`if worst and top in RANK ...`) is vacuously false — it does not fire
regardless of what `VERDICT` is claimed. The only other guard, the F1 empty-members check at
`:1273-1277` (`len(members) == 0 and steps_run > 0`), does not apply either: the members list is
non-empty, just entirely skipped. **Nothing in `validate-digest.py` requires at least one member to
have actually run before a lead's `VERDICT` is trusted.**

Proven live (production `--hook`-equivalent CLI path, real `harness.json`/`team-config.yaml` fixture):
a `lead` digest with `steps_run: 3`, three members each `{status: skipped, persona: ..., reason: never
spawned}`, and `VERDICT: PASS` → **`RC 0`, stdout `digest ok`.** `SPEC.md:1616` documents "The team
verdict is computed from the members that ran" as the guarantee; the code does not enforce it when
that set is empty — it simply has nothing to compare against and lets the claim through unchallenged.
This is exactly the mirror image the dispatch named: `SKIPPED` was added to stop a real "did not run"
state from being forced into a fabricated verdict, and in doing so opened a path where an entire
team's worth of "did not run" can be reported as `PASS` with zero pushback. `test-validate-digest.py`
has no case for an all-skipped `members` list against a nonzero `steps_run` — only the mixed case
(`:547-568`) is covered.

### Other half-two files — no findings

`omp-hooks.test.ts`/`harness-hooks.ts` (`.omp/extensions/harness-hooks.ts:733-737`): the new
`if (!contract.trim())` guard blocks an empty structured yield BEFORE calling `validate-digest.py`,
closing the specific "empty message hits the hook's own unreadable-payload pass-through" shape;
`omp-hooks.test.ts:214-233`'s new case exercises exactly that path. Read, no fail-open found.
`.claude/skills/harness-team/SKILL.md` and `SPEC.md` prose changes are internally consistent with the
code EXCEPT for the SPEC.md claim addressed under Risk 2 above (the guarantee is stated, not
enforced, in the all-skipped case).

### Code-risk grading

`code-grade.py --base $(git merge-base main 70fd441) --head 70fd441`: 44 functions reported, all
`RESULT: PASS`, no `SEVERITY:` lines, no grade-2 functions. All six new `validate-digest.py` functions
named above grade 4–5 against the bar-4 production line. Three `test-check-state.py` helper functions
grade 3 against the bar-3 test line — no finding.

## Summary

| Finding | Half | Severity | Gates? |
|---|---|---|---|
| SC-05 restructure / M1 fail-closed property | one | n/a | CLOSED / PRESERVED |
| Unattributed-overrule ruling still marked "note ... overruled" | one | low | no |
| SEC-01 plan-review binding skips branch corroboration | two | **high** | **yes** |
| All-members-`skipped` roll-up bypasses worst-wins entirely | two | **high** | **yes** |

`severity_max: high`. `must_fix`: the two half-two findings — both proven by direct execution against
the production call shape, not inferred. This panel's judgment: **FAIL** on code review, pending a fix
to either bind the plan-review path to the actual dispatch (branch/worktree corroboration, or a
non-digest-controlled feature-identity input) or reject it outright, and to require at least one
non-skipped member (or an explicit "team not dispatched" outcome distinct from `PASS`/`FAIL`) before a
lead `VERDICT` is trusted.
