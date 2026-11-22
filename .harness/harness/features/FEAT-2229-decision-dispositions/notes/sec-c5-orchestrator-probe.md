# SEC-C4-01 actual-CLI controls at pin c163d5ea — executed by the orchestrator (validate c5)

**Result: 325 observations through the real `plan-merge.py check`; every true identifier continuation is rejected, every documented delimiter is accepted, CRLF/tab/trailing-whitespace/closing-hash shapes resolve, neighbouring and fenced spoofs never leak. No bypass of the DEC_ID_END lookahead found.** Six of the 325 lines print `FAIL`: all six are the probe's own mislabelling of two headings that the signed design treats as DEC-10's heading, not as continuations (below).

Why this note exists: security c5 (`notes/review-harness-security-reviewer-c5.md`) planned 107 CLI observations of exactly these classes and was guard-refused before executing any (its Bash grant covers `git diff` only). The orchestrator holds a shell; DEC-177 says a question a measurement can close is probed before it travels up. This is orchestrator-tier evidence — it does not change the security reader's own BLOCKED receipt; whether it closes the security-owned runtime acceptance is the operator's call (open question in the ship return).

## How it was run

- Tree: feature worktree at e220cde8; `git diff --stat c163d5ea e220cde8 -- . ':!.harness'` is empty, so the code under test is the pin's.
- Script: `notes/sec-c5-orchestrator-probe.py` (loads `tests/integration/test-plan-decision-dispositions.py` by path and uses its `run_check`, `plan_text`, `row`, `_docs` fixture builders — the same path the registered cases take; each observation writes a temp fixture root and invokes the real CLI). Run with `env -u HARNESS_AGENT_TYPE python3 <script> <test path>`; rc 1 only because of the six mislabels.
- Output: `notes/sec-c5-orchestrator-probe.out.txt` (trimmed to the six non-ok lines and the total; 77 s to reproduce).

## Classes and outcomes

| class | observations | outcome |
|---|---|---|
| identifier continuations (`DEC-100`, `DEC-10x`, `DEC-10X`, `DEC-10é`, `DEC-10_a`, `DEC-10-1`, `DEC-10.5`, `DEC-10/x`, `DEC-10a — title`, `DEC-10-extra`, `DEC-10_`, `DEC-10x:`, `DEC-10x (x)`) — spoof fails, genuine passes, spoof-only has no section | 39 | all ok |
| malformed heading formats (`##DEC-10`, seven `#`, 4-space indent, `-DEC-10`, `xDEC-10`, `dec-10`, `DEC 10`, `DEC-010`) are not a DEC-10 section | 8 | all ok |
| delimiters after the full id (`DEC-10`, trailing space/tab/two spaces, `:`/`:Ten`, ` (Ten)`/`(Ten)`, ` — `/`—`, ` – `/`–`, ` - `, tab, ` -- `) × levels 1/2/3/6 × indent 0–3 spaces, plus tab after hashes | 255 | all ok |
| CRLF (spoof pair + bare + dashed genuine), trailing spaces, trailing tab, closing `##` | 8 | all ok |
| bounded neighbours: `## DEC-10x` after `## DEC-10` does not extend DEC-10; `### DEC-10.5` stays inside DEC-10's section | 3 | all ok |
| fence controls: spoof heading inside ```` ``` ````, `~~~`, `` ~~~ a`b `` is content; genuine heading after the fence resolves | 6 | all ok |
| probe mislabels (see below) | 6 | design-conformant |

## The six `FAIL` lines

1. `## DEC-10-` (hyphen at line end). `DEC_ID_END` admits `-\s`; the scanner keeps line endings, so the newline is the `\s` and the heading IS DEC-10's. It carries no further identifier, so it is not a continuation under the signed comment ("a hyphen joined to more identifier"). Shadowing effect: identical to a second `## DEC-10` heading, which the document author can always write — no new gain.
2. `## DEC-10—x` (em dash joined). `\u2014` is a listed delimiter, so this IS DEC-10's heading; `## DEC-10—Ten` was also run as a positive and passed. The probe listed it under continuations by mistake.

Both are recorded as residual observations in the briefing's backlog table for the operator to keep or strike; neither is a bypass.
