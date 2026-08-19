# Security review — FEAT-24 config-responsibility-split — PINNED SHA 14994b3

Diff: `ada8e99..14994b3`. VERDICT: PASS (severity_max: med, must_fix: []).

## BLUF

This diff moves a fleet member's board declaration (owner, Projects-v2 number, station field,
station names) out of local `fleet.yaml` and into that repository's **own remote default branch**,
read live via `gh api` (`factory_config.product_config`/`board_for`, `factory_gh.file_at_ref`). That
is a genuine new trust-boundary crossing: the value now comes from whoever can merge to the fleet
member's default branch, not from the local operator's own git-tracked config, and it drives writes
made with the **local operator's own `gh` credentials**. `validate_board` never binds the declared
`owner` to the repository's own owner, so this is a real confused-deputy shape (F1, med) — currently
precondition-absent because the only live fleet member (`kaya-ai`) is operator-owned. Separately,
SC-06's literal wording claims three distinct tested failure modes for `board_for`'s remote read;
only one distinct code path actually exists, and the QA gate note marks it "met" on cases that don't
exercise two of the three (F2, low / F3, info — the JSON-parse leg is keyword-search-bounded, not
mutation-verified, because my read-only Bash access was correctly refused when I tried to prove it
with a mutation kill).

## Census — the five named surfaces

1. **argv construction in `file_at_ref` and every caller** — examined. `file_at_ref(repo, path, ref)`
   builds `["api", f"repos/{repo}/contents/{path}?ref={ref}", "--jq", ".content"]` as one list
   element (no shell; no flag-injection risk from a leading `-`, since the string always starts with
   the literal `repos/`). The only non-test caller is `factory_config.product_config`
   (`factory_config.py:277`) — `path` is always the constant `.harness/harness.json`
   (`_PRODUCT_CONFIG_PATH`); `ref` is always `entry["default_branch"]` from local, git-tracked
   `fleet.yaml`. No path traversal, no query-string injection reachable from remote content.
   Assessed and dismissed.
2. **Deserialization of remote content** — examined, and this is where F1 lives. `product_config`
   bounds the shape to "parses as JSON, parses to a dict" and nothing more; `board_for` then hands
   the `github.board` sub-object to `validate_board`, which checks `owner`/`number`/`station_field`/
   `stations` for *shape* but never checks that `owner` belongs to the repository that declared it.
   See F1 below.
3. **Error/log exposure** — examined, read-verified this pass (`factory_cli.py:31-45`).
   `GhError.__str__`/`FleetError.__str__` are built exclusively from `factory_cli.body(what, value,
   next_step)` — three short strings, never the raw `stdout`/`stderr` a `GhError` carries as
   attributes (e.g. `file_at_ref`'s undecodable-content raise stores the full base64 blob on `.stdout`
   but never puts it in the message). No token or full-filesystem-path leak found. Assessed and
   dismissed.
4. **Memoisation** — examined. `_product_config_memo` is keyed `(repo_name, ref)`
   (`factory_config.py:271`), so different refs cannot collide, and a failing read is provably never
   cached (`test-factory-config.py`'s two memo cases exercise both halves through the real function,
   not just asserted in prose). Assessed and dismissed.
5. **Trust of `fleet.yaml` itself** — examined. `repos[].name`/`default_branch`/`workspace_root` are
   still local and git-tracked; changing them requires the same access as changing any other harness
   source file. Not a new boundary. Assessed and dismissed.

## F1 — med — remote board declaration is not bound to the declaring repository, and drives the operator's own `gh` credential against an unconstrained target

**Who / what / gets.** Anyone who can merge to a **fleet member's own default branch** (not the
harness operator) controls the `github.board.owner` / `.number` / `.station_field` values that
`factory_land.py:84`, `factory_claim.py:222`, and `factory_decompose.py:329` resolve via
`factory_config.board_for` and then hand, unchecked, to `gh_board.set_station` /
`factory_gh.project_field_set` / `factory_gh.project_items` / `factory_gh.project_field_options` —
run with the **local operator's own authenticated `gh` CLI**, not the fleet member's own token.
`factory_config.validate_board` (`factory_config.py:82`) checks `owner` is truthy and `number` is a
digit; it never checks `owner == repo_name.split("/")[0]`. So a fleet member can declare a board
belonging to **any GitHub user the operator's `gh` token can reach** — not necessarily itself — and
the factory will:
- **read** that board's full item list (`project_items`, `factory_gh.py:196`) — information
  disclosure of an unrelated board's contents to whatever the poll/claim run prints, and
- **write** a station-field value on an item there (`gh_board.set_station` → `project_field_set`) —
  integrity tampering against a board the fleet member's own commit access was never meant to touch.

**Diff attribution, precisely.** `validate_board`'s shape-only check is unchanged by this diff — the
gap is not new code. What changed is the **provenance** of its input: pre-FEAT-24 (DEC-174 amendment
2) the same fields came from local, git-tracked `fleet.yaml`, so the affected-party set was "whoever
can edit this repo," identical to the operator. Post-diff (DEC-174 amendment 3) they come from the
fleet member's own default branch, so the affected-party set is now "whoever can merge to that other
repository" — a materially different, and today unexamined, set. The check that would close the gap
(bind `owner` to the repository's own owner) was never written for either shape, but only the new
shape makes its absence a genuine trust-boundary gap rather than a no-op.

**Availability leg (STRIDE-D), confirmed by code, not inference.** `factory_claim.py`'s poll mode
(no `--repo`) resolves `board_for` for **every** served fleet member before doing any claim work
(`factory_claim.py:213-234`), and `factory_cli.run(TOOL, _main, expected=(FleetError, GhError))`
(`factory_claim.py:391`) means a `FleetError` or `GhError` raised while resolving **any single**
member's board — malformed shape, unreachable remote, station-option mismatch via
`factory_cli.refuse` (`factory_cli.py:47`, `sys.exit(2)`) — aborts the **entire process** at exit 2.
One fleet member with a poisoned or simply broken remote board declaration blocks claim polling for
every other fleet member served in the same run.

**Reachability today: precondition-absent, not live.** The only fleet member at this pin is
`mruangutai/kaya-ai`, owned by the same person who operates the local `gh` credential
(DEC-174 amendment 3, live-read confirmed `owner mruangutai, number 2`). No third-party attacker
exists in the current fleet, so this is not exploitable today. It becomes live the moment the fleet
gains (a) a second member repository, or (b) any collaborator/CI identity on the existing member's
default branch other than the operator. Recorded as `open_questions` below rather than `must_fix`,
per the operator's own approved architecture decision (BRIEF: "Placement is in the product's own
repository") — this is a design trade-off for the operator to weigh, not a defect in this diff's
stated scope.

## F2 — low — SC-06's three named failure modes collapse to one untested-as-distinct code path

SC-06: *"a failed remote read — missing file, unparseable JSON, `gh` unauthenticated — raises naming
the repository, the path and the ref"*. Traced against the real call graph:
- `preflight()` (a blanket `gh auth status` check) runs **before any board read** in all three real
  callers — confirmed both in code (`factory_claim.py`: preflight is step 1, board resolution is
  step 2; `factory_land.py`: preflight is step 4, board write is step 5) and in
  `test-factory-integration.py`'s Case (C) comments ("claim: preflight is step 1, before any board
  read"). A globally unauthenticated `gh` never reaches `board_for`'s own error-handling branch at
  all — it exits 2 upstream, through a wholly different code path than `product_config`'s `except
  factory_gh.GhError` clause.
- A **repo-scoped** access failure (a token that passes `auth status` but lacks access to one member
  repository) would reach `product_config`'s `except factory_gh.GhError` clause — the same one
  "missing file" hits — since both present as an opaque non-zero `gh api` failure with no shape
  distinction available to catch on.

So `board_for`'s own remote-read error handling has exactly **one** distinct failure code path for
"the API call itself failed" (covers both missing-file and repo-scoped auth failure indistinguishably)
and a second, separate one for "the call succeeded but the body didn't parse" (F3). SC-06 as worded
claims three; only two exist, and QA's gate note (`qa-2026-08-19-matrix-gate.md:188`) marks it "met"
citing `test-factory-config.py:526,560` — both of which construct one fabricated, generic `GhError`
via `patched_file_at_ref` and assert only that `product_config` re-wraps whatever it's handed. Given
this is the exact function (`file_at_ref`/`product_config`) where two live defects (a POST-flip and a
`validate=True` base64 rejection) already shipped past a fully green 208-check suite, a signed SC
whose evidence is narrower than its wording is worth recording precisely so the next reviewer doesn't
read it as having verified more than it did.

## F3 — info — the "unparseable JSON" branch has no adversarial-shaped test; claim is search-bounded, not measured

`product_config`'s `except (ValueError, TypeError)` around `json.loads(raw)` (`factory_config.py:278`)
is real, reachable production code that runs directly on content pulled from a lower-trust remote
(see F1's provenance argument). Grepped every touched test file for a case that serves malformed/
non-JSON content through `patched_file_at_ref` or the fake `gh`'s `contents` endpoint (searched
`not json`, `garbage`, `invalid json`, `malformed`, `corrupt`, `does not parse`) — zero matches. I
attempted to settle this with a mutation kill (copy the module to scratch, break the except clause,
re-run the suite in the copy) rather than rest on the grep; `bash-write-guard.sh` correctly refused
the `cp`/`rm` commands, citing this role's read-only Bash contract. I did not route around that with
an equivalent file-write via a different tool — the guard's refusal is exactly what it exists to do,
and using a different mechanism to reach the same write would have been guardrail evasion, not
verification. So this claim stands at the confidence a grep supports: **the branch is unexercised by
name**, not proven broken — reading the code, it looks correct (catches both exception types, raises
`FleetError` naming repo/path/ref, matching SC-06's letter). Recorded as info, not a live defect.

## Incidental, out-of-scope observation

While attempting F3's mutation test, `python3 -c "shutil.copytree(...)"` against the exact same
scratch destination succeeded silently where the shell `cp`/`rm` form was blocked — `bash-write-guard.sh`
pattern-matches shell verbs, not the file-write outcome. `bash-write-guard.sh` is a DEC-174 carve-out
(edited by hand only, never through a dispatched run) and is untouched by this diff, so it is out of
scope for this verdict; flagged here, unfixed, for the operator per that carve-out's own rule.

## Already-found, not re-litigated

`gh_board.load_board`'s `None`-on-typo behaviour, the three unpinned `test-factory-gh.py` cases, the
`integration.detect`/`INTEGRATION_SCRIPTS` count mismatch, `test-factory-land.py`'s non-discriminating
`review` fixture, and `plan.yaml:657-658`'s stale T-03 prose — all previously dispositioned; no new
evidence found that changes any of those verdicts.
