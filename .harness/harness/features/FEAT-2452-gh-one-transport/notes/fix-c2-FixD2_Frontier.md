# fix-c2 FixD2_Frontier: M1, M2, B1 and B3

Base HEAD 3465716a (`00-head.txt`). All outputs are in `notes/fix-c2-FixD2_Frontier/`. Everything ran from the worktree with HARNESS_AGENT_TYPE and CLAUDE_PROJECT_DIR unset. There were no git writes and no formatters, and no existing assertion was changed or weakened.

## M1 (T-04, SC-03): wayfind.py
**Change.** `wayfind.py` now validates every field a decision rests on before the decision is made. Small checks (`_state`, `_number`, `_string`, `_list`, `_labels`, `_fields`, `_list_of`) feed `require()`, which raises the existing typed `unusable()` GhError. `cli()` already turns that error into `wayfind:` and exit 1.

Fields audited, with the check now applied to each:

| Reader | Field | Decision it drives | Check now |
|---|---|---|---|
| `sub_issues` (frontier, map) | container | which tickets exist (`or []` removed: null used to read as "no tickets") | list of objects |
| `sub_issues` | `state` | ticket open → considered | string; lowercase `open` or `closed` |
| `sub_issues` | `number` | which ticket's blockers and view are read | `type is int`, ≥ 1 |
| `blockers` | container | (c1) | list of objects; confirmed 404 → `[]` unchanged |
| `blockers` | `state` (each item) | any open → not eligible | string; lowercase `open` or `closed` |
| frontier ticket view | object | (was `.get` on any value) | JSON object |
| frontier ticket view | `assignees` | non-empty → claimed | must be a list (missing, null, string, object all raise) |
| frontier ticket view | `labels` | round's research vs HITL split (`ticket_type`) | list of objects, each with a string `name` |
| frontier ticket view | `number` | the number frontier/round/map advertise | positive int **equal to** the sub-issue number |
| frontier ticket view | `title` | printed with the advertised ticket (KeyError traceback before) | string |
| `parent_of` | `number` | (c1) | unchanged semantics, now via `_fields(number=_number)` |
| resolve ticket view | `title` | written into the gist line; read before the writes | object with a string `title` (was `.get('title','')`: `{}` wrote anyway) |
| `append_gist` map view | `body` | the "has a `## Decisions so far`" decision and the edit | object with a string `body` (was `or ""`: null read as "no section"; an int raised a TypeError) |

Audited and left unchanged, with the reason:
- `resolve` reads no state of its own ticket and decides nothing on one.
- `cmd_map`'s map view (`title`, `number`, `state`) is display only and outside frontier/resolve. Its sub-issue tallies now come from the validated `sub_issues`.
- `ensure_labels`' `or []` (chart/ticket) is outside frontier/resolve. A null list only causes a create of an existing label, which gh refuses loudly.
- `ticket`/`block` `--jq .id` (cid) is outside frontier/resolve. A wrong id is rejected by GitHub with a 422, not silently accepted.
- `ticket_type` drops its dead `str(l)` branch, because frontier now guarantees label objects.

**Red** (`01-red-wayfind.txt`, wayfind.py unmodified at HEAD): 115 FAIL. All of them are new checks, and all 123 pre-existing checks PASS. Each requested input is red:
- `[{}]`, `[{"state":"unknown"}]`: frontier printed `#11 eligible?`, exit 0.
- `[{"state":1}]`: untyped AttributeError, so the `typed_diagnostic` check fails.
- missing, null, string or object `assignees`: missing and null printed the ticket; a string or object read as claimed.
- unusable sub-issue state/number/container, labels, view number/title, resolve title and map body.

The controls are green at HEAD and stay green: `case_8c_*_valid` (OPEN/closed), the empty list, and `case_10d_*` (CLOSED blockers, `[]`, confirmed 404, open blocker, claimed, closed ticket, no sub-issues). The existing case_7 404 absence also stays green.

**Green** (`03-green-wayfind.txt`): ALL PASS, 238 checks.

New test functions: `case_8c_blocker_state_must_be_open_or_closed`, `case_10c_frontier_refuses_unusable_decision_fields`, `case_10d_frontier_valid_decisions_unchanged`, `case_11c_resolve_refuses_unusable_title_and_body`, and the helpers `_without`, `_frontier`, `_check_refused`.

## M2 (T-05, SC-06): github-mirror.md
The abandon cell on row 106 now says that abandon attempts every other write independently, in plan order:
- a ticket whose close succeeds is reseated and reported as closed but not labelled;
- a ticket whose close also fails is reported (`could not close` and the closing `FAILED n of m` line) and is neither reseated nor labelled;
- later tickets, the milestone close and the local `abandoned` station write still run.

This matches `gh-sync.py` `_close_and_reseat` (return before `_to_backlog` and `_label_abandoned` on a failed close), `_apply_abandon_plan`, `_report_abandon_gaps` and the station block. gh-sync.py was not edited.

The wayfind row (118) also names the decision-field validation and the "unusable map body" gist failure, so SC-06 matches the M1 code. `test-station-argument-spelling.py` passes over the edited doc.

## B1 + B3 (T-01): factory_gh._ISSUE_URL
**Change.** The pattern is now:
- host: dot-joined labels `[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?`;
- port: an optional 1–65535 alternation with no leading zero;
- owner: `[A-Za-z0-9-]+`;
- repo: `(?!\.\.?/)[A-Za-z0-9._-]+`.

`issue_number_from_url` itself is unchanged.

**Red** (`02-red-factory-gh.txt`): 17 of 345 FAIL. They are:
- owner `?`, `#`, `.`, `%2F` and `@`;
- repo `?`, `#`, `.` and `..`;
- `a..b`, `a.-b` and `a-.b`;
- ports 65536, 99999, 0, 0443 and 100000.

Leading dot, trailing dot, a leading hyphen and an empty port were already rejected at HEAD, so they are guards, not reds.

The new accept cases are green at HEAD and stay green: `GHE.Example.com:65535/my-org/my.repo_x-1`, `localhost:1/O-1/.github`, `www.github.com/o/r..x`, and the existing ghe.example.co.uk and `:8443` hosts.

**Green** (`04-green-factory-gh.txt`): 345/345.

**ReDoS probe** (`05-regex-timing.txt`): near-misses of 0.4–1M characters take at most 15 ms, which is linear.

**Disclosed limit:** the owner class `[A-Za-z0-9-]` follows the assignment exactly, so an Enterprise Managed User personal namespace such as `jdoe_acme` would be refused. A refused URL means the ordinary create SKIPs as an "unreadable URL" and records nothing.

## Grades
`08-code-grade-base-to-worktree.txt` applies code_grade's own base..head gate (`_gate_file_records`: gated means new, or graded lower than base) with base b788e9da. Because git writes are barred, it reads the head from the worktree. Result: `gated=70 result=pass`, nothing blocking.
- Changed and new production functions all grade at least 4: `frontier` 4, `ticket_type` 4, `append_gist` 4, `issue_number_from_url` 4, and the rest 5.
- Tests grade at least 3: `case_10c` and `case_11c` 3, the others 4–5.
- `wayfind.main` (grade 1 at base, unchanged) is not gated and was not split.

The paths-mode report is `06-code-grade-paths.json` / `07-code-grade-changed.txt`.

## Verifies (literal, from plan.yaml)
- T-01: `09-verify-T-01.txt`, exit 0, all 4 files PASS.
- T-04: `10-verify-T-04.txt`, exit 0, wayfind ALL PASS and factory-gh 345/345.
- T-05: `11-verify-T-05.txt`, exit 0, PASS line (command text in `11-verify-T-05.command.sh`).

## Files changed
- `.claude/skills/harness/bin/wayfind.py`
- `tests/unit/test-wayfind.py`
- `.claude/skills/harness/bin/factory_gh.py`
- `tests/unit/test-factory-gh.py`
- `.claude/skills/harness/references/github-mirror.md`
