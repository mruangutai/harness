# Code review — FEAT-13 T-01/T-02 — `6dfbf7c..d4951c2`

## Verdict: PASS

Stage 1 (spec compliance) and Stage 2 (quality) both clean. Every change traces to REQ-01..06 /
D-01..05; no scope creep beyond the named file set (`STATE.md`/`feature.yaml` are process
bookkeeping, not source, and both are in-scope paths per the dispatch and the orchestrator's own
domain). Full unit suite (10/10 scripts) and `test-factory-integration.py` (97/97) pass at the
pin; the task's literal `verify:` (four greps + suites) passes. Read `factory_gh.py`,
`factory_decompose.py`, `factory_land.py`, `factory_claim.py` and all five touched test files at
`d4951c2` via `git show`, plus the two receipts and the qa note.

## Stage 1 — spec compliance

- **The core discrimination (`factory_gh.py:315-421`), the named fail-open hunt target.** The
  collapse the dispatch named — `issue = repository.get("issue"); if issue is None: return
  None` — is **not present**. The code does `if "issue" not in repository: raise` (unrecognised
  shape) **then** `issue = repository["issue"]; if issue is None: return None` (explicit null, a
  real answer). Key-presence is tested before the value is read, exactly as REQ-05/D-03 require.
  QA's mutant M1 (`qa-FEAT-13-T-01-c0.md:76-80`) independently confirms this discrimination is
  load-bearing: reintroducing the collapse reddens exactly one assertion
  (`test-factory-gh.py:709`, "NO 'issue' key... RAISES"), nothing else moves.
- **Escape path for the raise, verified rather than assumed.** Neither `factory_decompose.py`'s
  `if disp == "partial":` block (`:431`) nor `factory_claim.py`'s `--issue` lookup loop
  (`:227-241`) sits inside a `try/except`; a `GhError` from `issue_board_item_id` propagates
  unguarded up to `factory_cli.run()` (`factory_cli.py:71-92`), which traps it and exits 2 — it
  never falls through to "item stayed None" and never reaches `project_item_add`/refuse-as-if-
  absent. Confirmed by reading both call sites and the trap, not inferred from a green suite.
- **No `is:open` reintroduced in decompose** (`factory_decompose.py:271-294`) — grepped, the only
  hit is prose in the docstring contrasting with `factory_claim`'s poll, not a query argument.
- **`land` behaviour-preservation (REQ-04/SC-07).** The explicit open-check
  (`factory_land.py:96-106`) sits after `git push` (`:56`) and after `pr create` (`:69`), before
  `_find_item_id`, station never set on a closed issue — matches today's failure point exactly.
  Verified live: `test-factory-land.py` M7 asserts push-happened and PR-created as *positive*
  facts (not just "station unset"), and QA's mutant M4 confirms the ordering is load-bearing.
- **`claim`'s closed-issue refusal ordering (REQ-03/D-05).** The refusal at `:281-286` (5a-pre)
  precedes the self-ownership branch at `:293` (5a) — confirmed by reading the source, and by
  QA's mutant M3 (moving the refusal after 5a reddens exactly the R6b self-owned case, not R6a).
- **The named question, answered.** In `claim`, `issue` inside the candidate loop (`:271-273`) is
  reassigned from a real `factory_gh.issue_view(repo_name, num, [..., "state", ...])` fetch
  **before** the 5a-pre check at `:281` — the synthetic `--issue` row's `content` dict (which
  carries no `state` key) is read only for `number`/`repository` at `:255-258`, never for
  `state`. In `land`, `issue_view(args.repo, args.issue, ["title", "state"])` (`:63`, widened by
  this diff) is a real `gh issue view --json title,state` call (`factory_gh.py:145-147`) that
  either returns both fields or raises — `run_gh` does not silently return a partial dict.
  Direction if `state` were ever missing: `.get("state") != "OPEN"` is `True` → refuse. Fail
  **closed**, not open — the failure mode is a false refusal, not a false pass. In `land` a false
  refusal would land after push and PR-create with the station unset, which is exactly #238's
  shape (already out of scope, not reopened here).
- **REQ-06 / poll untouched.** `factory_claim.py:238`'s poll still calls
  `factory_gh.project_items(owner, board_number, query=...)` unchanged; `test-factory-claim.py`
  R8 pins the query string and asserts `issue_board_item_id` is never called on that path.
- **T-02 (SC-10).** Live receipt reports `points_used: 1` (≤5 bar), `item_id_match: yes`, derives
  the reference id from a step-4 `gh project item-list` read taken *after* the measured window
  (not contaminating the delta), and includes a null-control pair (`delta 0`) establishing the
  window is attributable to the one lookup. Meets the intent's ordering and honesty requirements.
- **Already-adjudicated items** (per dispatch) all confirmed present and not relitigated: the
  `argv[:2]`/`argv[1:3]` plan-text correction, claim's exit-2-not-1 ratified delta (D-02, and
  exercised in `test-factory-claim.py` R7), `land`'s #238 latent bug left untouched.
- **SC-05's unit-evidence limitation** — flagged by the implementer's own receipt (Q1) and
  separately addressed by QA against the BRIEF's explicit constraint ("Proof is unit call-shape
  assertions plus one live read... explicitly chosen against a FEAT-11-style live measurement").
  Not reopened here; T-02's live receipt closes the live half.

## Stage 2 — code quality

- **`factory_gh.py` `_generic()` collapses five distinct unrecognised-shape branches** (no
  `data` key, no `repository` key, `repository` not a dict, no `projectItems` key/not a dict, no
  `nodes` key/not a list) into one `what="gh graphql call failed"` with a network/auth
  `next_step` — byte-identical to the genuine transport-failure raise. If GitHub restructures
  `repository.issue`'s shape, the operator is told to check `gh auth status` and network access
  and re-run, with no signal that the response shape itself changed. The plan prescribed distinct
  `what` values for four specific cases (`repository not found`, missing `totalCount`,
  non-integer `totalCount`, truncated) and was silent on these five, so this is inside the
  plan's latitude, not a violation — raising as **low**, diagnostics-quality only. The
  discrimination itself (raise vs. return-None) is proven load-bearing by QA's mutant M1
  regardless of which `what` string the raise carries.
- No dead code left behind: `_item_repo` fully deleted (`factory_decompose.py`), no stray
  references anywhere in `bin/*.py` (grepped). Docstrings rewritten to match the new mechanism
  per the plan's per-sentence verdicts (spot-checked against the diff, not just QA's claim).
- Test additions consistently pin call *arguments*, not just counts, at each of the three call
  sites (`REPO != OWNER` fixture in `test-factory-land.py` specifically defeats the bare-login
  mis-wire) — matches P-13/G-02 from this reviewer's own Expertise (a count-only assertion would
  pass a same-name reimplementation).
- Not raised (evaluated and dropped as non-findings): `isinstance(total, int)` accepting `bool` —
  no realistic GraphQL response produces a JSON boolean for `totalCount`, no scenario. Multi-repo
  `--issue` iteration (first-non-None-wins across `fleet["repos"]`) has no dedicated multi-repo
  test — `info` at most: the miss path (`"issue": null` → `None` → loop continues) is exercised
  by `ISSUE_ITEM_ISSUE_NULL_JSON` at the helper layer, single-repo `fleet.yaml` means the
  iteration itself is unexercised in production today, and pinning the adjacent multi-repo case
  was not required by any SC.

## Verification performed

- `bash run-unit-tests.sh --kind unit` at `d4951c2`: 10/10 suites PASS, no failures.
- `python3 test-factory-integration.py`: 97/97 PASS.
- Task `verify:`'s four greps re-run directly: all four conditions hold (`issue_board_item_id`
  defined; zero `factory_gh.project_items` in decompose/land; exactly one in claim).
- Read `factory_gh.py`, `factory_decompose.py`, `factory_land.py`, `factory_claim.py` and the
  five test files in full at `d4951c2` via `git show`; not relied on diff hunks alone for the
  fail-open hunt.
- Manually traced the exception-escape path (`try`/`except` grep across the three production
  files plus `factory_cli.py`) rather than assuming a green suite implies no swallow.

## Open questions

None blocking. QA's already-answered open question (SC-05 unit-evidence framing) is not
reopened.
