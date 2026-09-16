# Panel record — BUG-1507 cycle 0 — pm

**BLUF: the panel is transcribed and all four findings are `resolved`. Both mechanical verify
defects were real — I reproduced each fail-open on a staged fixture, repaired it, and both repaired
commands are still RED (exit 1) on the unfixed tree. Rank 1 is accepted: SC-03's negative control is
expressible in-process, so the self-reinvocation machinery is struck from T-05's intent. Rank 4 is
accepted: D-03's `because:` now owns the `change_type` choice instead of attributing it to the
matrix. `approval.status` stays `pending`; nothing under `.claude/` was touched; no commit.**

## The four findings, as recorded in `plan.yaml panel.findings`

| id | rank/sev | reader | disposition | judgement |
|---|---|---|---|---|
| `PF-4d48a7518cc7333294cad13b27fdaed6` | 1 · med | should-not-exist | resolved, T-05 | ACCEPTED — the sibling shape (`tests/integration/test-check-instruction-paths.py:25-26`) proves an explicit-root sweep delivers SC-03's observable; "as a subprocess" was an implementation commitment beyond the requirement (rule 6) |
| `PF-f0a35051dae0d5f3a0b09b52a6a8b862` | 2 · med | scope | resolved, T-02 | tool name now bound to the phrase |
| `PF-0274cfb40625bb45a968c559d773bcfd` | 3 · med | scope | resolved, T-03 | slice narrowed to segment 1 |
| `PF-41dcf8d793040a3bae0c6a120579d480` | 4 · low | should-not-exist | resolved, D-03 | ACCEPTED — the circularity is real (rule 15); `because:` now says the typing is the plan's own choice and strikeable at signature |

Each `summary` is the validator lead's `panel_findings:` string unaltered; each `id` was re-hashed
from the string read back out of `plan.yaml` and matched (4/4). `panel.transcription_rule` records
the normalization.

## Rank 1 — what T-05 now specifies instead

The sweep becomes a pure function of a root, plus one `offenders(root)` predicate both cases assert
on. Struck: `BUG1507_SCOPE_ROOT`, the case-4 skip rows, the 5a recursion guard, both subprocess
self-invocations, and step 7's env-var run. Consequence: rows a–c (including the `MIN_OCCURRENCES`
floor the `scope` reader relied on) are now **unconditional over `REPO_ROOT`**, so the vacuous-sweep
state the panel's live finding describes is unreachable. The negative control is kept and
strengthened — it asserts the offender tuple names the mutated file, tool and token, which
attributes the red better than grepping a child's stdout did. **Both grep labels are unchanged
character-for-character**, so T-05's own `verify:` still holds. SC-03's wording in `BRIEF.md:111-119`
now pins the acceptance and explicitly leaves the invocation route free.

## The two repaired verify commands

**T-02** — last conjunct only; the `re.findall` / `len(m)==3 and all(islower)` conjuncts are
untouched:

`… and 'plan-merge.py set-feature-station --station building' in t else 1)`

**T-03** — slice narrowed to segment 1, delimiters `The eng segment.` / `The qa segment`, both
**counted exactly 1** inside the build-phase block and 1 in the whole file. Segment text is
whitespace-collapsed before the search so a line-wrapped edit is not a false red, and the command
asserts both delimiter counts are 1 and the slice is non-empty before searching. Asterisk-free
delimiters were chosen so the plan value carries no markdown (DEC-182).

### Observed exit statuses — measured, not expected

Run from the worktree root, from the values as stored in `plan.yaml`:

| command | on the unfixed tree | staged fixture |
|---|---|---|
| T-02 verify | **exit 1** (prints `['Review','Ready','Review']`) | correct tool → 0; wrong tool → 1; **no tool at all → 1 (the OLD command exits 0 here — the finding)** |
| T-03 verify | **exit 1** (prints `True 424`) | in segment 1 → 0; **in segment 2 → 1, in segment 4 → 1 (the OLD command exits 0 for both — the finding)**; empty slice → 1; missing block → 1; delimiter absent → 1 |

T-02's new conjunct was proved on a fixture where the three earlier conjuncts are green, so its
green was observed rather than assumed. Probe: `/tmp/bug1507/probe.py` (throwaway, read-only on the
worktree).

## State after this segment

`status: plan`, `approval.status: pending`, 5 tasks (T-01..T-05), 6 decisions (D-01..D-06), no
renumbering. `check-plan-routes.py` → **0 violation(s) across 1 plan(s), exit 0**. `yaml.safe_load`
clean; all five `verify:` values are `|` literal blocks. Only decoration left in any non-`intent`
value is D-05's `.claude/skills/**/*.md` glob, which is pre-existing and a wildcard, not markdown.

## For the operator at signature

- **Q1 (blocking, carried from the panel, not mine to decide):** does scope widen to close DoD
  bullet 2's task-card half (`gh_board.py` station derivation)? Disclosed in `BRIEF.md ## Constraints`.
- **Note, not a question:** `panel.findings` summaries cite `plan.yaml:113` and `plan.yaml:181`.
  Writing the `panel:` key inserts lines above `tasks:`, so those verify values now sit at 155 and
  223. The summaries are byte-identical to the hashed strings on purpose — rewording one would mint
  a new `PF-` id and silently retire any ruling against the old one.
- Rank 1 changed `BRIEF.md`'s SC-03 text. The brief was unsigned, so no signature was reset.
