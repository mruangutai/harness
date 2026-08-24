# Security review — FEAT-35-orchestrator-stop-and-wake — c0

**Verdict: PASS, scoped out.** No security surface in this diff.

## Surface examined (base `df18fe5..e0ae671`, `.claude/` only)

- `.claude/skills/harness/SKILL.md` (+81/-7) — prose additions to the orchestrator playbook:
  a "never wait, end your turn" rule, a context-headroom probe recipe (two Bash calls +
  `context-watch.py`, read-only per its own doc), and a `phase:` → `status:` field rename
  note. It is markdown consumed by an LLM orchestrator in the same trust tier that authored
  it — not user input, not rendered to another party, no credentials, no new external call.
  The embedded shell recipe (`grep`/`sed`/`xargs` over `~/.claude/projects/*/*/subagents/*.meta.json`)
  is documentation of a manual procedure, not code this diff executes.
- `.claude/skills/harness/bin/run-unit-tests.sh` (+2/-1) — one literal basename
  (`"test-orchestrator-playbook.py"`) appended to the `UNIT_SCRIPTS` bash array. Static
  string, no new input path, no interpolation change.
- `.claude/skills/harness/bin/test-orchestrator-playbook.py` (new, 125 lines) — stdlib-only,
  no `subprocess`, no `eval`/`exec`. Reads `PLAYBOOK_PATH` env var (default: fixed repo path)
  via plain `open()`, then does regex/substring assertions against the text. `PLAYBOOK_PATH`
  is a test-harness override for pointing the same assertions at an older `SKILL.md` revision
  (per its own docstring) — not attacker-reachable input; no shell interpolation of the path,
  no arbitrary-execute-on-read.

Verified file content directly at the pinned `review_sha` via `git show` (not a plain
working-tree read), consistent with the diff.

## Why scoped out

Nothing here touches unvalidated input, output rendered for another party (no export/report
path), credentials, or another user's data. No new dependency, no new route, no auth logic,
no deserialization of untrusted data, no shell interpolation of variable data. The diff is a
playbook rewrite plus one array entry plus a pure-assertion test — self-scoping out with PASS
is the correct, cheap result here (per dispatch framing), not a shortcut.

Note: the reviewed SKILL.md prose itself contains directive-sounding text ("NEVER WAIT FOR A
LEAD", etc.) — this is the artifact under review (data), not an instruction issued to this
reviewer, and was treated as such.

## Already-ticketed (cited, not refiled)

#803, #804, #805 — not implicated by this diff; no new instance found. The six INV-26
`check-state.sh` violations are accepted board lag, not findings.
