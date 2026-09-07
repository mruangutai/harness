# Panel transcription — BUG-148 — 2026-09-06

**The panel record is now in `plan.yaml` `panel:` (line 187, top level, sibling of `approval:`).**
Five findings, `severity_max: med`, `must_fix: []`, `dismissed: []`, `cycle: 0`. Nothing was
adjudicated, re-worded, re-ranked or fixed. `approval.status` is still `pending` and `status:` is
still `plan`. Two findings need one line each from the operator at signature; the other three need
nothing but his awareness.

Source: `runs/2026-09-06-01-validator/digest.md` §10.4 `panel_findings:` (`:98-103`), which is
authoritative over the markdown table above it (one table row is truncated mid-sentence) and over
the opening BLUF (it says "four surviving findings"; the digest's own appended corrections section
supersedes that at **five**).

## PF- id → reader / severity, and who has to act

| id | reader | sev | one line | operator ruling at signature? |
|---|---|---|---|---|
| `PF-6b4a7af5de3e77e59af34e9a00b68548` | `scope` | med | D-01's `because` presents rewrite-vs-append as forced for STATE.md when it is a preference | **YES — digest Q1 (blocking).** He settled on a dated note; the plan substitutes an in-place rewrite |
| `PF-54450f537e28244ae73d9c0e48ae4efe` | `should-not-exist` | low | REQ-03's `--stdout \| diff` pipeline is plan-added scope the grilling never settled | **YES — digest Q2 (non-blocking scope call).** Decide before any tightening of finding 3 |
| `PF-a2df57f48de3e81d49745cfd1adaa20b` | `scope` | med | both verifies allow a keyword-stuffed correction that still misleads | no ruling needed — accepted-by-design, disclosed in BRIEF "Verification gaps"; SC-06 is the only backstop |
| `PF-ed3ec57922f582bd208169c1120d0946` | `validator-lead` | low | nothing forces the two corrected records to agree; D-01's one-shape intention has no enforcement | **YES — digest Q3 (non-blocking).** Cheapest remedy is one sentence in T-02's intent; that is a plan edit, so it is his call |
| `PF-b7b07ec7b7f6cacb3b894cae4bda2a04` | `scope` | low | SC-01/SC-02 restate T-01/T-02's own verifies; only four criteria measure independently | no ruling needed — informational, concurs with goal-check F-4 |

Finding 4 stays attributed to `validator-lead`, its true author, not laundered into a reader id
(`panel.reader_attribution` records why).

## Two deliberate deviations from the dispatch, both recorded in the file

1. **Ids are content hashes, not `PF-1 … PF-5`.** The dispatch said sequential; `panel_findings.py`
   is the single identity source (`harness-spec-driven`: "never type it"), and its docstring says
   why sequential is wrong — a re-run renumbers, so a risk acceptance recorded against finding 2
   silently starts covering whatever is second next time. `check-state.sh` INV-32 (`:514-517`) and
   `plan-merge.py sign-approval --overrule` both read these ids. Every id above recomputes from its
   stored `summary` field (verified); `panel.transcription_rule` states the rule.
2. **A third reader entry, `goalcheck` (`harness-pm`, `status: ran`).** It ran outside
   `runs/2026-09-06-01-validator` — hence the digest's `steps_run: 2` — and its artifact is
   `notes/research-BUG-148-goalcheck-plan-c0.md`, whose F-2 and F-4 the panel explicitly carries
   forward. INV-32 (`check-state.sh:534-547`) requires all three of `should-not-exist`, `scope`,
   `goalcheck` to be recorded at signature; omitting a reader that demonstrably ran would have made
   the record incomplete and reddened the gate the moment the plan is signed. Its own F-1/F-3/F-5
   are **not** transcribed as panel findings — they live in its note.

Reader field is `reader:`, not `id:` — that is the key `check-state.sh` and every live plan use.

## Open questions

- **Q1 (mine, non-blocking):** the digest's `should-not-exist` row says "no verdict token — external
  persona" and its own corrections section says the return did carry an equivalent advisory
  judgement rolled up as PASS. I recorded `verdict: PASS` with the whole history in the reader's
  `note:`. If the lead meant the row to stand as-is, the note is where to correct it — never the
  finding.
- Q1/Q2/Q3 above are the **digest's**, not mine; they travel to the operator with the signature
  request. None routes a fix cycle: `gates.review` is `advisory_unless_high` and `severity_max` is
  `med`.

## Measured

- `check-plan-routes.py <plan.yaml>` → exit **0**, `0 violation(s) across 1 plan(s)`, both tasks OK.
- Reload: top keys `approval decisions feature lanes panel schema source_issues status tasks`;
  `approval.status: pending`; `status: plan`; 5 findings; readers all `ran`; ids reproduce.
- `panel:` begins at line 187 of a 186-line base — lines 1-186 (lanes, decisions, T-01, T-02) are
  byte-unchanged, and `plan-merge.py apply` carried `approval:` forward verbatim.
- The whole feature directory is untracked, so `git status --porcelain` shows `?? .harness/harness/
  features/BUG-148-gate-record-correction/` rather than a modified-file line. **Nothing is
  committed; HEAD was never moved.**
