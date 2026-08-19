# Code review — FEAT-24 — PINNED SHA 14994b3

Reviewed diff: `ada8e99..14994b3`. This note clears exactly that diff. All measurements below were
run in a disposable worktree checked out at `14994b3` (`.claude/worktrees/review-14994b3`, removed
after use) or, for the SC-02 mutation probe, directly against the live tree at HEAD (`efaddcf`),
which is code-identical to `14994b3` (see measurement 1) — never against a stale working copy.

## The three measurements

**1. `git diff --name-only 14994b3..7e30983`** — literal output: `.harness/harness/features/FEAT-24-config-responsibility-split/feature.json` only. Zero code files. The dispatch's premise holds:
every anchor below describes the diff that was actually asked for. (I also checked
`14994b3..efaddcf`, HEAD at review time, two commits past the pin: same result plus one
`observations/harness-eng-lead.md` file — still zero code files.)

**2. Full suite at the pin** (`run-unit-tests.sh --kind all`, worktree at `14994b3`):
- `ok`/`PASS` lines: **1578**
- `FAIL` lines: **0**
- exit code: **0**
- SC-13's own instrument, registered script count: `UNIT_SCRIPTS` + `INTEGRATION_SCRIPTS` = 16 + 12
  = **28** at `14994b3`, and **28** at `ada8e99` (16 + 12, counted the same way from
  `git show ada8e99:.../run-unit-tests.sh`). No script deregistered.

**3. `check-state.sh` at the pin, FEAT-24-scoped**: zero `VIOLATION` lines anywhere in the run
(`grep -c VIOLATION` → 0 for the whole repo, not just FEAT-24), exit 0. Every FEAT-24-tagged line
in the output is `note` severity (stale run-dir references for pruned run folders — informational,
not gating). Matches the commit-message claim ("the feature reaches zero violations of its own").
Violations for FEAT-02/05/06/15/20 exist (STATE.md shape, stale run refs) — out of scope per the
dispatch, not investigated further.

**`human_commits_in_scope`, measured not inferred**: `git log ada8e99..14994b3 --grep="harness:human" -i`
→ zero hits. Every commit in range carries `[harness:t-NN]` or no tag; none is a hand edit. `[]`.

## SC-09 (inspection) — closed, not merely asserted

Read live via `gh api "repos/mruangutai/kaya-ai/contents/.harness/harness.json?ref=master"`:
`github.board` carries `owner: mruangutai, number: 2, station_field: Status`, `stations` with
exactly the five required keys and DEC-192 values, and none of `project_number`, `project_id`,
`status_field`, `in_progress_option`. SC-09 is MET, verified against the live merge target, not
inferred from the plan text.

## SC-02 `ready` — mutation-run myself, not trusted from the commit message

The prior validator digest (`runs/2026-08-19-5-validator/digest.md`) had this in `must_fix`:
hardcoding `factory_decompose.py:399` to `"Ready"` reddened nothing, because the fixture's own
`ready` value was literally `"Ready"`. Commit `3396b5e` claims to have fixed this by moving the
fixture to `"Promoted"` and says "I proved it discriminates myself." That is an author's assertion
of intent (P-03/P-06 shape), not ground truth, on a signed `verify: automated` criterion — so I ran
the mutant myself rather than accepting the prose:

```
fc.board_station = lambda fleet, repo, key: ("Ready" if key == "ready" else _real(fleet, repo, key))
```
against `test-factory-decompose.py` at HEAD (code-identical to `14994b3`). Result: **3 cases redden**
— `(2) both stations set to the fleet's ready option`, `(7) resume: the item's station is set to the
ready option`, `(T-03) the station set to A's own ready option (Promoted), never B's (Other-Ready)`
— exactly the three the commit message names. **SC-02's `ready` key is confirmed MET at this pin,**
independently verified, not inherited from the author's own claim.

The other four keys' mutation proofs (`building`/`review` via `test-gh-board.py`'s `Col-B`/`Col-R`,
`backlog`/`done` via `test-check-state.py`'s `Icebox`/`Shipped`) carry forward from the prior
validator run without re-verification here: `git diff --name-only 0fa6315..14994b3` shows neither
`test-gh-board.py` nor `test-check-state.py` changed in that range, so nothing invalidates those
prior proofs. **SC-02 is fully MET at `14994b3`, all five keys, four inherited + one re-verified.**

## The named deliverable — does the fake `gh` recorder mislead on SC-06?

**Yes. SC-06 names three failure modes — missing file, unparseable JSON, `gh` unauthenticated — and
the test suite provides genuine, distinguishing evidence for none of them cleanly: two collapse into
one untested-for-distinction path, and the third has no test at all.**

`factory_config.product_config` (`factory_config.py:252-297`) has three distinct raise sites:
1. `factory_gh.GhError` from `file_at_ref` → `FleetError` ("product config unreadable") — this is
   the path BOTH "missing file" (a 404) and "`gh` unauthenticated" (an auth failure) take. Both are
   just "`run_gh` exits non-zero" to `factory_gh`, so they are structurally the same code path.
2. `json.loads(raw)` raising `ValueError`/`TypeError` → `FleetError` ("product config invalid …
   does not parse as JSON")
3. `not isinstance(doc, dict)` → `FleetError` ("product config invalid … must parse to a JSON
   mapping")

`test-factory-config.py` exercises exactly **one** case for this whole area —
`"product_config raises naming repo, path and ref when the remote read fails"` (:485-511) — via a
hand-written `_boom` stub that raises a `GhError` with stderr `"404"` in it, but the case's only
assertion checks that repo/path/ref appear in the resulting message; it never inspects the
underlying cause, so the same case would pass identically whether the stub represented a 404 or an
auth failure. That is one shape, doing duty for two of the three named modes, with no assertion that
distinguishes them.

I grepped the entire diff for the third mode and found **nothing**: no case anywhere drives
`product_config` with a stub returning malformed JSON text, and no case returns a JSON document that
parses but isn't a mapping (`grep -rn "does not parse as JSON\|must parse to a JSON mapping"` across
every `test-*.py` in the tree: zero hits outside the production module itself). Raise sites 2 and 3
are dead code from the test suite's perspective — completely unreached, not merely non-discriminating.

Concrete failure scenario: if a future edit changed `except (ValueError, TypeError) as e:` to
swallow the exception and set `doc = {}` (or `return None`), `board_for` would either raise a
different, misleading `FleetError` ("product config missing board" instead of naming the real JSON
failure) or, in the `return None` case, throw an uncaught `AttributeError` on `doc.get("github")` —
a raw traceback reaching a caller instead of the clean, repo/path/ref-naming `FleetError` SC-06
requires. Nothing in the green suite would catch either regression, because nothing ever exercises
the branch.

This also confirms the dispatch's framing at the `factory_gh.file_at_ref` level: the recorder in
`test-factory-gh.py` (`recorder()`, :39-51) plays back a canned `Result(returncode, stdout, stderr)`
queue and records argv; it has no model of gh's real request/response shape or of HTTP method
selection. Coverage there is bought entirely by hand-picked assertions on argv/stdout content (e.g.
`"-f" not in calls[0]["argv"]` at :918), which is exactly what caught the historical `-f` → POST
defect — but the recorder itself still cannot see a similarly-shaped bug it wasn't specifically
asked to probe. The `product_config` JSON-parse gap above is a fresh instance of that same class,
one level up the call stack.

**Verdict on SC-06, decided rather than defaulted: UNMET.** The dispatch's own rule is explicit — "a
criterion whose only evidence is an assertion that cannot fail is UNMET, and say so." Two of SC-06's
three named failure modes have no discriminating evidence (missing-file vs. unauthenticated is one
untested-for-distinction shape) or no evidence at all (unparseable JSON is untested full stop). The
prior validator run set the precedent of putting a partially-unmet signed criterion in `must_fix`
(SC-02's `ready`, same shape: code correct, evidence absent for part of the criterion). I apply the
same standard here. **`must_fix`.**

## The seam question — memo keying, measured

`_product_config_memo` (`factory_config.py:249,271-273,296`) is keyed on **`(repo_name, ref)`**,
where `ref = entry["default_branch"]` resolved fresh from the fleet entry on every call — not on
`repo_name` alone. The memo write (`_product_config_memo[memo_key] = doc`) is the *last* line of
the try path, after both the GhError and the JSON/mapping checks; every raise happens before it, so
a failure is structurally never cached (there is no `except: memo[key] = ...` anywhere).
`test-factory-config.py`'s memoisation cases exercise both halves directly: `:575-586` proves a
second `board_for` call makes no second remote read; `:588-606` proves a raising stub is not cached
and a subsequent working stub recovers on the very next call, with no intervening `check()` (which
would itself clear the memo and mask the defect the case is trying to catch — the test file's own
comment names this trap explicitly).

**No staleness bug exists.** Two fleet dicts naming the same `repo_name` but different
`default_branch` produce different memo keys, so there is no cross-ref leak; a failed read is never
memoised, so there is no cross-attempt staleness either. The one caveat, already accepted and
explicitly stated in D-03/the module docstring as by-design cost rather than defect: the memo is
process-lifetime and has no invalidation, so if a repo's remote config changes mid-process (e.g.
mid-batch factory run), a stale successful read is served for the rest of that process. That is the
documented trade-off, not a silent one, and is out of scope to re-litigate here.

## Stage 1 — spec compliance

Every code-file change traces to a `REQ-NN`/`D-NN`; I did not find scope creep in the reviewed file
set. The eight `board_for`/`load_board` raise shapes are proven identical and paired at both entry
points (SC-04); the `where`-contract pin (`github.board.owner` present, `github.board.board`
absent) appears in both `test-gh-board.py:114-116` and `test-factory-config.py:418-419`, matching
plan item 2a's requirement that the defect be provable from both callers. `validate_board`'s
stations check uses set equality (`set(stations.keys()) != set(_STATION_KEYS)`), which rejects both
missing AND extra keys — no membership-only gap here. `fleet.yaml`, `.harness/harness.json`,
`templates/harness.json` all match their task verifies exactly (I diffed each by hand against
T-06/T-07/T-08's `WHAT MUST BE TRUE AFTERWARDS`). `DECISIONS.md`'s DEC-174 am.3 and DEC-196
am.1/am.2 read accurately against the code as I independently verified it (kaya's board read live,
station derivation, origin-gated close); `gen-decisions-index.py --stdout` is byte-identical to
`DECISIONS-INDEX.md` at the pin (SC-11 closed). `factory_claim.py`, `factory_land.py`,
`factory_decompose.py`, `harness_boundary.py`, `wayfind.py`, `layout_migration.py`,
`branch-create-gate.sh`, `check-plan-routes.py`, `run-unit-tests.sh` are byte-identical between
`ada8e99` and `14994b3` — confirmed by `git diff --stat`, matching the plan's
`resolved_but_not_written` claims. SC-02 confirmed MET (see above, independently mutation-tested).
SC-09 confirmed MET (live remote read). SC-11 confirmed MET (byte-identical index). SC-13 confirmed
MET (1578/1578 ok-lines, 0 FAIL, 28/28 registered scripts).

**One coverage note, low severity, not must_fix.** `test-no-distribution.py`'s `case5()` deletes two
checks — `every_repo_declares_its_own_board` and `kaya_ai_is_paired_with_board_2` (former
lines ~282-315). This is a forced consequence of T-02/T-07's redesign, not an unauthorized edit:
`test-no-distribution.py` is in T-07's own `files:` list, and both checks read `repos[].board`, a
key `load_fleet` now rejects outright — leaving them unedited would permanently redden the suite, so
the deletion is structurally inevitable, not gratuitous. The durable part worth recording: before
this feature, "kaya-ai is paired with board 2" was a local, offline, every-CI-run regression check;
after it, that fact is checkable only via a live, authenticated `gh api` call, and the only place
that call still runs is T-07's own task verify — which never runs again after this feature ships. A
future accidental repoint of kaya's `github.board.number` away from 2 would not be caught by
anything in the checked-in suite. This mirrors the BRIEF's own disclosed SC-09 trade-off (network
reads don't belong in the offline unit suite) closely enough that I read it as consistent with the
feature's accepted cost — noted for the record, not gating.

## Stage 2 — code quality

Nothing rises to a code-quality finding beyond what's captured above. The fail-open hunt (the
`check-state.sh` INV-26 try/except, `board-station.py`/`gh-sync.py`'s new exit-2 paths,
`gh_board.load_board`'s explicit-null branch) all resolved as designed: every unusable-declaration
branch raises or reports a violation rather than silently completing; the one branch that returns
`None` silently (`load_board` on an absent `github` block) is the already-dispositioned residual —
confirmed present in the code exactly as described, not re-reported.

## Already-dispositioned findings — checked against this pin, not re-reported

- `gh_board.load_board` returns `None` for both an absent `github` block and a present block with
  no `board` key — confirmed present in the code at `gh_board.py:71-73` (`if not isinstance(github,
  dict): return None`), contradicting the docstring's "every other unusable shape RAISES" claim for
  that one cell. Per dispatch, `board_for` (the criterion-bearing path) is unaffected and raises
  correctly on all three cells; this is the operator's compatibility call to make, not mine to
  re-raise.
- The three unpinned `test-factory-gh.py` cases (`:960` non-alphabet base64, `:978` line-wrapped
  base64, `:991` absent content field) — confirmed still absent from every `verify:` block in
  `plan.yaml` (`grep` for all three exact ok-line texts across every YAML in the tree: zero hits).
- `.harness/harness.json`'s `integration.detect` vs `INTEGRATION_SCRIPTS` count mismatch (4 vs 12)
  — not re-investigated, out of scope per disposition.
- `test-factory-land.py`'s `review` fixture non-discrimination — not re-investigated.
- `plan.yaml:657-658` stale T-03 prose (`Ready`→`Promoted`) — confirmed the fixture change landed
  in commit `3396b5e`, exactly as the disposition states. (This is a distinct claim from "SC-02 is
  now met" — the disposition covers the stale prose only; SC-02 itself I re-verified independently
  above.)

## must_fix

- **SC-06 is UNMET.** `factory_config.product_config`'s three named failure modes (missing file,
  unparseable JSON, `gh` unauthenticated) collapse to one untested-for-distinction shape for two of
  them and zero coverage for the third (JSON parse failure / non-mapping document,
  `factory_config.py:283-293`). Remedy: at minimum one case per remaining branch in
  `test-factory-config.py`, stubbing `factory_gh.file_at_ref` to return non-JSON text and to return
  a JSON array/scalar respectively, each asserting the resulting `FleetError` names repo/path/ref —
  mirroring the existing `_boom`-style case for the `GhError` path. Route: `harness-backend-dev`
  owns `.claude/skills/harness/bin/**` per `team-config.yaml`, and `test-factory-config.py` is not a
  DEC-174 carve-out file, so the named owner can execute this directly.

`severity_max: high` (a signed `verify: automated` criterion is unmet at the merge-candidate pin).
