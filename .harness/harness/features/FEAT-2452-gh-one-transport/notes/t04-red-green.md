# T-04 red/green evidence: wayfind on factory_gh, fail-closed reads, strict JSON, gh_bin deleted

Built main-session-direct (DEC-174) by `BuildD_T04` in this worktree from HEAD `55478dd2`. `HARNESS_AGENT_TYPE` and `CLAUDE_PROJECT_DIR` were unset for every run. Raw outputs are in `t04-red-green/`. No git writes were made.

| Step | File | Result |
|---|---|---|
| C2: confinement landed first, production untouched | `01-prod-untouched.txt` | Only `tests/unit/test-wayfind.py` is modified, and `git diff --stat .claude/skills` is empty. |
| C2: confinement red against the old wayfind | `02-red-confinement.txt` | exit 1, 9 FAIL. The sentinel logs `api repos/acme/widget/issues/5`, `issue close 5 …` and `issue view 7 … --json body`, because the old `gh_bin()` (`GH_SYNC_GH`-or-`gh`) ignores FACTORY_GH. The strict-JSON read, the apply and the gist cases never reach the fake. The dry-run cases pass. |
| Behaviour red against the old wayfind | `03-prod-still-untouched.txt`, `03-red-behaviour.txt` | exit 1. Every blocker and parent failure (401/403/500/network/exit-1-without-404/misleading-404/status-0-malformed-with-404/launch) returns `('value', [], '')` or `('value', None, '')`: the old code silently swallows them, including the sentinel's own exit 97. Invalid, duplicate and NaN JSON exit through `die` instead of raising GhError. In frontier and resolve the diagnostic does not name the failure: resolve reports "no parent map" after a 500. `gh_issues.gh_bin` still exists. |
| Production cutover | (none) | See the summary below. |
| Green | `04-green.txt` | exit 0, 47 PASS, ALL PASS. |
| Owned `gh_bin`/`GH_SYNC_GH`/`D-11`/dual-pin grep | `05-grep-owned.txt` | 0 lines in T-04's three files, excluding case_13's absence asserts. No `ghi.gh_bin` caller remains anywhere in the tree. The `GH_SYNC_GH` mentions left in `tests/manual/probe-issue-types.py` belong to T-05. |
| Literal T-04 verify | `06-verify.txt` | exit 0, with both scripts PASS (2.6 s wall). |
| Code grades | `07-code-grade-full.json`, `07-code-grade-base-wayfind.json`, `07-code-grade-changed.txt` | Every new or changed function PASSes. Production: `gh_json` 5, `gh_json_or_absent` 4, `do` 4 (up from 3), `append_gist` 4, `cli` 5, `issue`/`blockers`/`parent_of` 5. Tests are 4–5. Legacy `main` is grade 1 at base and at head with identical cc/cog; its abc went 66.2→65.5, so it did not drop and is informational. This was a paths-mode run with the base taken from `git show 55478dd2`. The base..head gate is Main's to run after commit. |

## Production change

- `wayfind.gh_json(args)` = `factory_gh.run_gh(args, json_out=True)`. A read is strict JSON: malformed, duplicate-key or non-finite payloads raise GhError, and raw text is never returned. `allow_fail` is gone.
- `wayfind.gh_json_or_absent(args)` is the local absence helper, used only by `blockers` (`… or []`) and `parent_of` (None).
- `do` runs each argv through `run_gh`. Dry-run still prints `would run: gh …` and `DRY RUN …` and launches nothing.
- `append_gist` runs `run_gh(["issue","edit",N,"-R",repo,"--body-file","-"], input=new_body)`. stdin is byte-exact, including `\r\n`, non-ASCII and trailing spaces.
- `issue` no longer has an `allow_fail`/"not readable" branch. A failure propagates as GhError.
- `ticket` creates with text `run_gh(create)`, then `factory_gh.issue_number_from_url(create, url)`, then the internal-id/attach sequence. A malformed URL raises before any id read or attach.
- `cli()` is the new CLI entry (`__main__` calls it). It wraps `main()` and catches GhError once: `die(f"gh {argv[:3]}… failed: {error}")`, which gives the `wayfind:` prefix, exit 1 and no traceback. `main` is otherwise unchanged apart from the ticket create lines.
- `gh_issues.gh_bin` and its `os` import are deleted. The module docstring no longer claims that a shared executor would have to pick one caller's failure policy. It now names factory_gh as the one transport, with failure policy kept per caller. No alias and no re-export were added.

## The 404 classification implemented

```python
_HTTP_404 = "(HTTP 404)"

def gh_json_or_absent(args):
    result = factory_gh.try_gh(args, json_out=True)
    if result.ok:
        return result.value
    if isinstance(result.status, int) and result.status != 0 and _HTTP_404 in result.stderr:
        return None
    raise result.error
```

Absence requires all three of the following, and the helper reads `result.status`, never `error.status`:
1. A completed process, so `status` is an int and never None (None is a launch failure).
2. A nonzero status.
3. gh's explicit `(HTTP 404)` marker in the captured stderr (gh prints `gh: Not Found (HTTP 404)`).

A status-zero malformed body has `ok` False and `status` 0, so it raises the strict-JSON GhError even when stderr says `(HTTP 404)`.

## Regressions (tests/unit/test-wayfind.py)

- **Confinement.** Each case runs in `offline(name, rules)`. That applies `offline_gh_env` via `mock.patch.dict(os.environ, env, clear=True)`, uses ONE FACTORY_GH fake (a rule table; it logs argv and byte-exact stdin), and calls `assert_sentinel_unused`. A sentinel hit is reported as a FAIL.
- **case_3–5:** a valid strict-JSON read on the fake; `do` dry-run launches nothing, while `do` apply runs on the fake; the gist dry-run only reads, while the gist apply sends the exact argv and byte-exact stdin.
- **case_6:** blockers and parent each raise GhError for 401, 403, 500, network, exit 1 without the marker, misleading 404 text (`issue 404 … (HTTP 410)` / `HTTP 4040`), status 0 with malformed JSON plus `(HTTP 404)` in stderr, and a launch failure (missing FACTORY_GH; `status is None`).
- **case_7:** a genuine nonzero `(HTTP 404)` gives `[]` for blockers and None for parent.
- **case_8:** valid blockers and parent reads.
- **case_9:** garbage, duplicate-key and NaN JSON each raise GhError.
- **case_10:** `frontier` with a blocker read returning 401 exits 1, prints no ticket, gives a `wayfind:`-prefixed diagnostic that names HTTP 401 with no traceback, and never reads the candidate issue.
- **case_11:** `resolve --apply` with a parent read returning 500 exits 1, names HTTP 500 (not "no parent map"), and makes no comment, close or gist write. A genuine parent 404 still reports "no parent map".
- **case_12/12b/12c:** a text URL create attaches `sub_issue_id=9001` for #42. A malformed URL exits 1 with the prefixed diagnostic and makes no id read or attach. A ticket dry-run makes only the label-list read.
- **case_13:** `gh_issues` has no `gh_bin`, and wayfind.py has no `subprocess` and no `GH_SYNC_GH`.

## Deviations / notes

- The behaviour red ran against old code that ignores FACTORY_GH, so the old reads hit the exit-97 sentinel instead of the fake's 401/500 replies. The red still shows the defect: the old blockers/parent_of turn the sentinel's nonzero exit into "none".
- `main()` was not split (legacy). The one GhError catch lives in the new `cli()` so that `main`'s grade does not drop.
