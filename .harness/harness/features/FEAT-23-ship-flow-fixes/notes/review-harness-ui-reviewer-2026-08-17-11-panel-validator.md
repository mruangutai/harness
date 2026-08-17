# Mode B post-build audit — FEAT-23 ship-flow fixes

**Pin:** `git rev-parse HEAD` = `490c37c` at time of review. Content read via `git show 490c37c:<path>`
object reads, not a checkout — the working tree carried unrelated local modifications to this
feature's own `STATE.md`/`feature.json` (`git status --short` showed `M` on both) plus untracked
notes from sibling features, so the dispatch's "tree is clean at that tip" was not literally true.
Harmless to this review: every artifact cited below was read as the pinned commit's object, never
from the dirty working copy.

**Verdict: PASS.** Both concrete follow-ups from the Mode A note
(`notes/review-harness-ui-reviewer-2026-08-17-2-uireview-validator.md`) resolved cleanly in the
shipped code, and a third adjacent surface the Mode A census had flagged (`gh-sync.py`'s new print
line) checks out consistent too. No rendered UI surface exists in this diff — the Mode A census
already established that (no html/css/tsx/jsx/vue/svelte anywhere in the touched set, no
`DESIGN.md`), and nothing in the T-01/T-02/T-04 commits since then changes that (simplify-pass
SKILL.md, DECISIONS.md/DECISIONS-INDEX.md — agent-consumed prose, out of scope per the Mode A
ruling, not re-litigated here).

## Check 1 — Mode A Question 1's prefix gap: closed

Mode A flagged that T-05's intent specified the `board-station: ` prefix for the success/error
lines (items 5-6) but was silent on it for the two environmental-precondition lines (items 3-4),
leaving room for an implementer to ship two of four output lines unprefixed.

**Resolved, and resolved the coherent way.** `board-station.py` (`.claude/skills/harness/bin/board-station.py`)
routes every stdout/stderr line through two helpers:

```
def out(line):
    print(f"board-station: {line}")

def err(line):
    print(f"board-station: {line}", file=sys.stderr)
```

Every one of the tool's eight possible output lines — no harness root, no `harness.json`, unreadable
`harness.json`, non-mapping `harness.json`, no github block, sync disabled, repo not pinned, no board
configured, the `BoardError` line, and the success line — calls `out(...)` or `err(...)`, so all
eight carry the prefix uniformly. The module docstring states this as a deliberate design choice
("EVERY line this tool prints, on stdout or stderr, carries the 'board-station: ' prefix — the
environmental lines below included, matching `gh-sync.py`'s own universal prefix discipline"),
closing exactly the inconsistency Mode A predicted was possible.

This is gate-backed, not just docstring narration: `test-board-station.py` asserts
`r.stdout.startswith("board-station: ")` on the environmental-precondition branches at lines 159,
196, 208, and `r.stderr.startswith("board-station: ")` / `"board-station: ERROR - "` at 172, 186,
221. The prefix is enforced by the test suite, not merely asserted in prose.

## Check 2 — Mode A Question 2's `/harness-plan` branch: shipped as specified

T-06's `plan.yaml` intent required: the literal marker `KICKOFF: the source ticket moves to Plan`;
the tool named by path (`board-station.py`); the literal phrase `no ticket is named` for the
no-source-ticket branch; the kickoff bullet positioned before the `squad plans,` sequence line
(`k < t`); and T-03's simplify clause between `squad plans,` and `eng-lead reviews architecture`
left byte-identical.

I reproduced T-06's `verify` clause against the pinned commit's file content directly (not by
running the harness's own gate, since I hold no execute path — this is the same grep logic the
clause specifies, run over `git show 490c37c:.claude/commands/harness-plan.md` output):

- marker count = 1
- `squad plans,` anchor count = 1
- `board-station.py` present
- `no ticket is named` present
- collision regex (`squad plans,.*simplif.*eng-lead reviews architecture`) matches
- `k=10`, `t=20`, `k < t` holds

All six clauses pass. The shipped bullet
(`.claude/commands/harness-plan.md:10-16`) states recognition in one clause ("The ticket is the
issue the user names in the opening ask or in answer to step zero; no separate question is asked
for it") and the no-ticket branch in the same sentence ("When no ticket is named, write nothing and
ask nothing"). Mode A's one open, non-blocking question — how "the operator names the ticket" is
recognized during a live session, since grilling's own bullet doesn't mention tickets — is
unaddressed by the shipped text in the same way it was unaddressed by the plan; I still rate it a
dialog-interpretation question for whoever owns grilling, not a state-completeness defect in the
surface I audit. Not re-raised as a new finding — same status, same non-blocking classification, no
new information changes it.

## Check 3 — adjacent surface: gh-sync.py's new print line, wording consistency

Mode A's census (T-01 row) flagged that this feature's changes to `gh-sync.py` add "one
unspecified-wording print line on an unreadable-file path" and ruled it out of the two named
Question surfaces but did not check its wording for consistency. The LEAVE list in this dispatch
settles `_record_status`'s *test coverage* gap, not its message wording, so this is a distinct,
in-scope check.

```
git diff 6f7a5fd..490c37c -- .claude/skills/harness/bin/gh-sync.py | grep -E '^\+' | grep -i print
```

returns three new print statements, all `gh-sync: `-prefixed:

```
print(f"gh-sync: {path} could not be read — status not recorded")
print(f"gh-sync: {path} is not a JSON mapping — status not recorded")
print(f"gh-sync: feature.json status -> {status}")
```

Consistent with the tool's existing prefix discipline (`gh-sync.py:197,199` cited in the Mode A
note). No finding.

## Accessibility and theme parity

Explicitly n/a, not omitted. Every surface in this diff and its Mode A predecessor is CLI
stdout/stderr text or markdown read by an agent or an operator's terminal — there is no colour, no
CSS, no theme, and no state conveyed by colour alone anywhere in the touched set. There is nothing
for these dimensions to check.

## Known-limit clause

Not triggered. Every claim above is source-legible — grep counts, line numbers, literal string
presence — with no rendered-layout or pixel-level claim made or needed. This note makes no PASS
claim on a dimension this role cannot observe from source.

## Digest fields — reasoning

- `severity_max: info` — both Mode A opens closed cleanly with gate-backed evidence; the one
  adjacent check (gh-sync.py wording) turned up nothing. No advisory-level finding remains open.
- `must_fix: []` — nothing blocks.
- `contract_violations: []` — nothing diverges from the Mode A contract or T-06's verify.

artifact: .harness/harness/features/FEAT-23-ship-flow-fixes/notes/review-harness-ui-reviewer-2026-08-17-11-panel-validator.md
