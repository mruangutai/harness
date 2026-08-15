# Security review — FEAT-11-graphql-field-resolve — c0

**Range reviewed:** `8dedeae..2ea9af3` (T-01 + MF-1 test fix, both commits). Diff read directly
via `git diff 8dedeae..2ea9af3 -- <file-set>`.

## Claim under test — CONFIRMED

> `owner`, `number`, `field` reach the query as GraphQL variables via `-f`/`-F` argv elements, not
> interpolated into the query document text.

True at `2ea9af3`.

- `_FIELD_QUERY` (`factory_gh.py:201-216`) is a static, module-level triple-quoted string
  constant. No `%`, `.format`, or f-string operates on it anywhere in the diff; `owner`, `number`,
  `field` are never concatenated into it.
- `_project_field_resolve` (`factory_gh.py:220-278`) builds argv as a Python **list**:
  `["api", "graphql", "-f", "query=" + _FIELD_QUERY, "-f", "owner=" + owner, "-F",
  "number=" + str(number), "-f", "field=" + field]`.
- `run_gh` (`factory_gh.py:83-101`, unchanged by this diff) calls
  `subprocess.run([gh] + list(args), capture_output=True, text=True, stdin=subprocess.DEVNULL)`.
  No `shell=True` anywhere in `factory_gh.py`. List-form argv, `shell=False` — no shell string
  interpolation possible.
- `owner`/`field` values are always the argument *slot* of a preceding `-f`/`-F` flag, never a
  bare positional argv element, so a leading `-` cannot be reparsed as a new `gh` flag
  (P-06/G-02 does not apply — there is no positional argv element in this call at all).
- Because the value never enters the query text, GraphQL-syntax characters (quotes, braces,
  newlines) in `owner`/`field` cannot break out of a string literal in the document.

## Second-order surface found and closed: `gh api -f`/`-F` magic-value conversion

`gh api`'s `-f`/`-F` flags do their own value parsing independent of the query text — a value can
be type-converted, and per `gh`'s documented behaviour a value beginning `@` is read from a local
file (`@-` from stdin) rather than sent literally. I could not confirm from this session which of
`-f`/`-F` carries this behaviour without invoking `gh --help`, which is off limits under this
review's hard constraints — so I closed this on **reachability** instead, which settles it either
way without needing that answer:

- Traced every production caller: `factory_claim.py:207-209`, `factory_land.py:87-89`,
  `factory_decompose.py:374-376` all set `owner = fleet["board"]["owner"]`,
  `station_field = fleet["board"]["station_field"]` from `.harness/factory/fleet.yaml`, loaded by
  `factory_config.load_fleet` (`factory_config.py:70`). `board.number` is validated as
  `isinstance(number, int) and not isinstance(number, bool)` (`factory_config.py:85-90`) — always
  a real YAML int, so `str(number)` can never begin `@`, closing that argument regardless of which
  flag carries the magic. `board.owner`/`board.station_field` are only truthy-checked
  (`factory_config.py:80-83`, `92-96`), so a fleet.yaml author *could* set either to a
  `@`-prefixed string.
- Grepped every call site of `_project_field_resolve`/`project_field_set`/`project_field_options`
  (`factory_claim.py`, `factory_land.py`, `factory_decompose.py`, plus every `test-factory-*.py`)
  — the only production writers of `owner`/`field` reaching this function are the three fleet.yaml
  reads above. No agent-generated, issue-derived, or otherwise untrusted text reaches `owner` or
  `field` anywhere in this codebase today.
- Grepped for writers of `.harness/factory/fleet.yaml` — none in production code
  (`factory_*.py`); the only writers are test fixtures (`write_fleet`/`write_yaml` helpers in
  `test-factory-*.py`). `fleet.yaml` is hand-authored operator config (consistent with the git
  history: "the fleet declaration, written by hand under DEC-179").

**Conclusion: not a finding.** The theoretical `-f`/`@filename` mechanism is real in `gh` generally,
but the only actor who can set `owner`/`field` to an `@`-prefixed value is the same operator who
hand-authors `fleet.yaml` and already has direct local filesystem access — per this codebase's
own P-02, an actor who already controls a value already holds the privilege that value would
grant through `gh`. This closes both the `number` case (type-closed) and the `owner`/`field` case
(reachability-closed) without needing to resolve which `gh` flag does the conversion.

**If this ever changes** — any future code path that lets agent-generated, issue-derived, or
otherwise lower-trust text populate `fleet.yaml`'s `board.owner`/`board.station_field`, or that
passes a non-fleet-sourced `field`/`owner` into `project_field_options`/`project_field_set` —
this reopens as a live data-exfiltration vector (STRIDE: Tampering leading to Information
disclosure) and should be re-audited then.

## `project_id`/`field_id` flowing into `item-edit` argv

`project_field_set` (`factory_gh.py:319-337`) now takes `resolved["project_id"]` and
`resolved["field_id"]` from the GraphQL response and passes them to
`gh project item-edit --project-id ... --field-id ...`. These are response-derived GitHub node
ids, the same trust level as the `gh project view`/`field-list` ids the old two-call path used —
no change in provenance, no delta.

## Adjacent questions — answered

- **Static vs. assembled at call time:** static constant, confirmed above.
- **argv list vs. shell:** list, `shell=False` throughout; no `subprocess.run(..., shell=True)`
  and no shell string anywhere in `factory_gh.py`, `test-factory-gh.py`, or
  `test-factory-integration.py` (`grep shell=` returns nothing).
- **Data exposure — anything beyond the already-ruled SC-10 owner/number/field echo:** none found.
  The D-03 catch-and-rewrap in `_project_field_resolve` (`factory_gh.py:238-249`) discards the
  original `run_gh`-derived `next_step` (which is `first_line(stderr)` and could in principle
  carry raw `gh` output) and replaces it with a fixed string
  (`"re-run after checking gh auth status and network access"`) — a **reduction** in what reaches
  the message text on this call path, not a regression. `e.stdout`/`e.stderr` are still carried as
  exception attributes (the class's pre-existing "for a debugger" contract, unchanged by this
  diff) but `GhError.__str__`/`factory_cli.body()` never render them — confirmed by reading
  `factory_cli.py:32-34` and the `run()` trap at `factory_cli.py:70-95`, where even the
  `FACTORY_DEBUG` traceback path only prints `str(exc)` (= `body()`), not the raw attributes. No
  token, auth header, or credential is ever placed in `argv` — `gh` handles auth out of band, not
  via any CLI argument this module constructs.
- **New test fixtures — real credentials/tokens/account identifiers:** none. Grepped
  `test-factory-gh.py` and `test-factory-integration.py` for token-shaped strings
  (`ghp_`/`gho_`/`ghu_`/`ghs_`/`ghr_`/`github_pat_`) — no matches. The one hit for "token" is
  prose in an unrelated pre-existing test description (`create_ref: ... (auth failure)`,
  `test-factory-gh.py:540`), not a diff addition. The `mruangutai` string in the file is a
  pre-existing fixture line (`test-factory-gh.py:500/503`), untouched by this diff.

## Verification performed

- Read `factory_gh.py` in full for the touched region plus `run_gh`, `GhError`,
  `_value_from_argv` (lines 1-300).
- Read `factory_cli.body`/`message`/`fail`/`refuse`/`run` to trace what actually reaches stderr.
- Read `factory_config.py` `load_fleet`/`harness_root` and traced all production callers of
  `_project_field_resolve`/`project_field_options`/`project_field_set` to close the `-f`/`-F`
  magic-value reachability question above.
- Ran `python3 .claude/skills/harness/bin/test-factory-gh.py` — 118/118 checks pass, entirely
  in-process against a monkeypatched `subprocess.run`; no real `gh` binary invoked (satisfies the
  "no live GitHub calls" constraint).
- Confirmed via `git diff` that `test-factory-integration.py`'s graphql fixture answers
  unconditionally without inspecting `query=` text, and that it too never spawns a real `gh`
  (`FACTORY_GH` redirected to a Python stub script).
- Grepped the `.harness` bookkeeping portion of the range
  (`git diff 8dedeae..2ea9af3 -- .harness/` — `DESIGN.md`, `STATE.md`, `feature.yaml`,
  `notes/qa-c0.md`, two dev receipts, one observations file) for credential shapes
  (`ghp_`/`gho_`/`ghu_`/`ghs_`/`ghr_`/`github_pat_`/`Authorization:`/`Bearer `/`token[:=]`) —
  zero hits. No `gh` output, token, or auth artifact is pasted into any receipt or STATE entry
  in this range.

## Not re-raised (already ruled per dispatch)

- BRIEF.md verification gaps (GraphQL cost, org-path stub-only, transport/auth stub-only).
- `feature.yaml residuals.d03_partial_success` — reviewed the mechanism (the catch-and-rewrap at
  `factory_gh.py:238-249`); it is a correctness/UX residual (D-03 as signed), not a distinct
  security threat — no new privilege or data crosses a boundary it didn't already cross via the
  old two-call path.
- `mf1_correction` and other `residuals.*`.

## Verdict

No security finding. This diff was genuinely in scope (a GraphQL-argv-construction change is
exactly the injection surface this role exists to check) and was audited to a conclusion, not
scoped out — `severity_max: info` reflects "reviewed, clean," not "nothing to judge"
(`n/a` is reserved for the latter per `bin/validate-digest.py`'s documented reviewer semantics,
read-only, DEC-174).

```yaml
VERDICT: PASS
DIGEST:
  headline: "owner/number/field reach the query as GraphQL variables via -f/-F argv, never interpolated into _FIELD_QUERY; list-form argv, shell=False; the theoretical gh -f @filename magic-value vector is reachability-closed (owner/field are always hand-authored fleet.yaml, never agent- or issue-derived); no credential/token leakage beyond the already-ruled SC-10 echo"
  in_scope: true
  scope_reason: "diff builds a GraphQL query document + CLI argv from fleet-config-supplied owner/number/field and constructs subprocess argv — a genuine injection surface, audited and found clean, not scoped out"
  severity_max: info
  findings: 0
  must_fix: []
  threat_model:
    - { boundary: "fleet.yaml-supplied owner/number/field -> gh api graphql argv (query interpolation)", stride: T, mitigated: true }
    - { boundary: "fleet.yaml-supplied owner/field -> gh -f/-F magic-value @filename read", stride: I, mitigated: true }
    - { boundary: "gh subprocess argv -> shell", stride: T, mitigated: true }
    - { boundary: "GhError message/stdout/stderr -> exception text or logs", stride: I, mitigated: true }
    - { boundary: "test fixtures -> tree", stride: I, mitigated: true }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/features/FEAT-11-graphql-field-resolve/notes/review-harness-security-reviewer-c0.md
```
