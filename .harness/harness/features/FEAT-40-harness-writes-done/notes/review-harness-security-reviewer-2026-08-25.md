# Security review — FEAT-40 — review_sha 3a548fe

## Verdict: FAIL — critical

`gh-close-gate.sh` (the primary artifact, `.claude/skills/harness/bin/gh-close-gate.sh`) does not
deliver the guarantee its own header comment, T-07's task intent, and SC-07's literal wording all
claim. The regex it uses to spot `gh issue close` and `gh api ... state=closed` is anchored on a
narrow set of boundary characters (`^ ; & | <space>`) immediately before the literal token `gh`.
Any shell form that puts a different character there — a quote, a backslash, nothing at all because
the token was assembled by substitution or indirection — reaches the real `gh` binary and closes the
issue while the gate prints nothing and returns exit 0 (allow). All bypasses below were executed
against the actual pinned-SHA script (`bash <(git show 3a548fe:.../gh-close-gate.sh)`), with a real
`.harness/harness.json` (`github.sync: true`), not reasoned about.

## Finding 1 (critical, must-fix) — `gh issue close` detector: bypassed by ordinary quoting, `eval`, `bash -c`, absolute path, indirection, line continuation

Measured ALLOW (should be DENY), with the shell's actual resulting argv verified via `set --` where
relevant — every one of these really executes `gh issue close 5`:

| command string | result | why the regex misses it |
|---|---|---|
| `gh "issue" close 5` | ALLOW | quote sits between `gh` and `issue`; anchor set has no quote char |
| `gh 'issue' close 5` | ALLOW | same |
| `gh i"ssue" close 5` | ALLOW | same |
| `\gh issue close 5` | ALLOW | `\` before `gh` is not in the anchor set |
| `/opt/homebrew/bin/gh issue close 5` | ALLOW | `gh` is preceded by `/`, not an anchor char |
| `$(echo gh) issue close 5` | ALLOW | the literal text never contains `gh issue` contiguous |
| `G=gh; $G issue close 5` | ALLOW | same — the invoked name is never spelled `gh` in the text |
| `eval "gh issue close 5"` | ALLOW | `gh` is preceded by `"` |
| `bash -c 'gh issue close 5'` | ALLOW | `gh` is preceded by `'` |
| `gh issue \`+newline+`close 5` (backslash-newline continuation) | ALLOW | the run between `issue` and `close` contains a literal `\`, which `[[:space:]]+` does not match |

Two of these — `bash -c 'gh issue close 5'` and `eval "gh issue close 5"` — contain the literal,
contiguous substring `gh issue close` in the raw command text. SC-07 states plainly: "a Bash call
containing `gh issue close` is denied." Both are Bash calls containing that exact substring, and
both are allowed. **SC-07 is false as measured, not just as reasoned about.**

The gate's own header comment claims the opposite of what was measured: *"a false deny is
recoverable and a false allow is not, so where the two cannot be distinguished — including a
`gh issue close` that appears only inside a quoted string — IT DENIES."* Verified directly:
`"gh issue close 5"` and `'gh issue close 5'` (the string quoted exactly as the comment describes)
are both ALLOW. T-07's own task intent in `plan.yaml` is explicit about the required bias — *"if you
cannot distinguish, deny"* — and the delivered regex instead defaults to allow for anything outside
its narrow anchor set, which inverts that instruction.

## Finding 2 (critical, must-fix) — `state=closed` detector: bypassed by quoting the value, by a JSON body, and by GraphQL

The second pattern matches only the bare literal substring `state=closed` (no whitespace, no quote
between `=` and `closed`). Measured:

- `gh api repos/o/n/issues/5 -f state="closed"` — ALLOW. Verified via `set --` that the shell
  actually delivers argv `-f state=closed` to `gh` (quotes are stripped mid-token), so this closes
  the issue for real; the raw text has a `"` between `=` and `closed` and the regex misses it.
- `gh api --input - repos/o/n/issues/5` with a JSON body (`{"state":"closed"}`), whether piped from
  stdin or written out in full inside the same command string — ALLOW. JSON syntax is
  `"state":"closed"`, never `state=closed`, so the CLI-flag-shaped regex can never match a PATCH
  body regardless of where the body's bytes live. This is a real gap in the data the gate CAN see,
  not the `tool_input.command`-only structural blind spot BRIEF/DEC-203 already disclose.
- `gh api graphql -f query="mutation{closeIssue(input:{issueId:...}){...}}"` — ALLOW. A second,
  wholly separate GitHub API surface (`closeIssue` GraphQL mutation) that neither pattern was ever
  written to catch.

## Finding 3 (info) — fail-open on a malformed hook envelope

If stdin is empty or not valid JSON, the `python3 -c 'json.load(sys.stdin)...'` one-liner that
extracts `cmd` raises uncaught (no try/except, no `set -e`); the failed command substitution yields
an empty string, every subsequent `grep` test fails to match, and the script falls through to the
final `exit 0` with no output — i.e. allow, silently. This matches Claude Code's documented
PreToolUse contract (silence = allow) so it is not a code bug on its own, but it means any framework
hiccup on the envelope defaults to allow rather than deny, the opposite of the gate's stated bias.
Not attacker-reachable through `tool_input.command` content alone (the envelope is harness-built),
so this is recorded as hardening, not gating.

## Confirmed NOT bypassable (tested, denied correctly)

`command gh issue close 5`, `echo 5 | xargs gh issue close`, `gh api -X PATCH ... -f state=closed`
in any flag order, `gh api repos/o/r/issues/9 -f 'state=closed'` (whole-value quoting, not
mid-token). `gh issue edit --state closed` does not exist as a real close path — `gh issue edit
--help` (gh 2.92.0, checked live) has no `--state` flag, so that named candidate is not a live
mechanism.

## Hook registration (`.claude/settings.json`) — correct

`PreToolUse` → matcher `Bash` → `[branch-create-gate.sh, bash-write-guard.sh, gh-close-gate.sh]`.
Fires on every Bash call as intended; no secret/token literal anywhere in the diff.

## Priority 2 — argv construction (`gh_issues.py`, `gh-sync.py`) — clean

Every `gh` invocation is list-argv via `subprocess.run([GH] + args, ...)`, never `shell=True`.
`sub_issues_args(repo, num)`/`internal_id_args`/`detach_sub_issue_args` f-string `repo`/`num` into a
REST path segment, but both values are schema-typed integers (`feature-schema.json`:
`github.parent`, `github.issues.*`, `github.source_issues[]` are all `"type": "integer"`), so a
path-traversal string can only arrive by first hand-corrupting a schema-validated feature.json — a
larger, separate compromise. `first_open_child`'s parsing of the `sub_issues` API response is
properly defensive (`isinstance(k, dict)`, `k.get("number") is not None`, wrapped `int()`).
Reachability-closed; info only.

## Priority 3 — `abandon`, privilege — assessed and accepted, not a new gap

`abandon --yes` now closes the parent unconditionally (DEC-203 item 4 removed the `parent_origin`
gate). Worst case of a mistyped feature-dir: the wrong feature's parent epic gets detached, closed
`not_planned`, labelled `abandoned`, and returned to Backlog. This is Tampering against the wrong
target, but it is an explicitly signed, cost-stated tradeoff (DEC-203 §4, `plan.yaml` D-12, BRIEF
REQ-05/SC-06) — not raised as new. Verified the two things the dispatch asked to check: the dry-run
and the real run share **one renderer**, `_abandon_plan()` (`gh-sync.py:1006`), so there is no
divergent-list risk; and `--yes` is matched by exact `in argv` search, scoped only to `abandon`
(`cmd != "abandon"` dies), so no fuzzy/prefix trigger.

## Priority 4 — schema + 24 feature.json rewrites — clean

`feature-schema.json` drops `parent_origin` from both the `github` and `factory` blocks under
`additionalProperties: false`; every one of the 24 rewritten `feature.json` files diffs to exactly
one deleted line (the `parent_origin` entry), confirmed file-by-file. FEAT-28's 3-line diff is the
same deletion, just adjacent to the closing brace.

## Compensating control (`board_lifecycle.py audit`, STATION class) — does what DEC-203 claims

Reads closed issues (`--limit 1000`) and the board's station map, flags any closed issue whose card
isn't at `done`. This genuinely detects a leaked hand-close or web-UI close, once per feature, inside
`ship`. The `--limit 1000` cap is pre-existing (unchanged by this diff) — a repo with >1000 closed
issues could miss an old leak, but that's not this diff's regression.

## Recommendation

Both critical findings sit in `gh-close-gate.sh`, which is enforcement layer under DEC-174 — I am
reporting, not fixing, and not recommending a dispatched fix through the path being changed, per this
review's own execution-route bound. The constraint any fix must satisfy: stop matching on a
character-class boundary and instead **tokenize** the command the way the shell would (e.g. `shlex`
in a Python check, or a normalize-then-match pass that strips quoting before the boundary test) so
that `gh`, `issue`, `close` are recognized as adjacent *words* regardless of the quoting/indirection
used to spell them — matching T-07's own instruction to deny whenever it cannot tell.
