# ALTITUDE — FEAT-34, `9165162..513c4a4` — flag-only, nothing applied

Two findings. Both concrete cost + alternative + severity + call + altitude word, per format.

## F1 — `_repo_arg_for_segment` is duplicated instead of exported from the shared predicate

**File** `.claude/skills/harness/bin/post-merge-sweep.sh:104-115` duplicates
`.claude/skills/harness/bin/worktree_terminal.py:102-115` (`_repo_arg_for_segment`) — identical
branching (literal `"harness"` short-circuit, then `fleet.load_fleet()` + trailing-segment
match), differing only in parameter shape (the sweep drops the `factory_config` argument,
importing it directly instead).

The sweep's own comment names the reason: `worktree_terminal.py`'s docstring declares its
public surface as `CLASSES`, `classify(root)`, `classify_all(root)` only ("Everything else here
is implementation detail that stays private") — so the sweep re-derives the helper rather than
import a name the module's own contract says is not for import.

**Deletion test.** Delete the sweep's copy: the segment→repo-arg mapping does not vanish, it
reappears as an import of a private name (contract violation) or a second hand-written copy
elsewhere. It is duplication earning nothing, not a pass-through — this is exactly the
"several statements that can drift" case the angle asks about. D-02 is stated for the walk/
classification logic ("one predicate the gate and the hook both cross… can never disagree
about what is eligible") and this helper is a piece of that same eligibility computation
(it decides which `--repo` a removal command is composed against) that fell outside the walk
and was never folded into the exported surface.

**Concrete cost.** A future change to fleet-name matching (e.g. matching by full `owner/repo`
instead of trailing segment, or handling a fleet entry with no `name` field differently) has two
call sites to update by hand; the one nobody remembers goes stale silently, exactly as REUSE's
own framing puts it, and here it applies to code, not a spelling.

**Alternative.** Export `repo_arg_for_segment(repo_segment)` from `worktree_terminal.py`
(folding the `factory_config` import inside it, as `classify()` already does for its own
imports) and have `post-merge-sweep.sh` import it. Widens the module's declared public surface
by one function; does not touch `classify`/`classify_all`'s contract that T-02's 19 green cases
pin.

severity: low · fix cycle before ship · **fold-in**

## F2 — the do-not-remove-a-worktree rule: two statements, and it is the right two

Verified the dispatch's own measurement first (P-07): at HEAD, `harness-handoff/SKILL.md` and
`harness/SKILL.md` each state the rule; `harness-principles/SKILL.md` and
`harness-expertise/SKILL.md` contain zero occurrences of "worktree" (`grep -c "worktree remove"`
on all three named non-handoff files: handoff=1, expertise=0, principles=0), matching T-10's own
intent block. `harness-handoff` is one of two `universal_rules:` entries
(`.harness/team-config.yaml:61-62`), so that one statement alone already reaches all sixteen
agents — T-10's stated goal is met by the handoff addition by itself.

`harness/SKILL.md:434-442`'s restatement is not redundant with that goal: it exists inside the
orchestrator's own three-act worktree lifecycle description and adds content handoff does not
carry — the *mechanism* now enforcing the rule (the `post-merge` hook, INV-29's refusal) and the
"used to rest on this paragraph alone" history. Two clauses of phrasing do overlap verbatim in
substance — handoff: "`git worktree remove` exits 0 when run from INSIDE the tree it deletes";
SKILL.md: "`git worktree remove` succeeds at exit 0 from inside the tree it removes" — an
independently-worded restatement of one mechanical fact, not a second rule.

Judged against the angle's own test (one authority vs. several that can drift): the *rule*
("removal is never yours") has exactly one authority reaching every agent (handoff); the
*mechanical justification* for it is stated twice in different words. A future correction to
that justification (e.g. a `--force` exemption landing) has two prose sites to find, but they
are low-traffic doc strings, not code, and the risk is genuinely small.

**Concrete cost if left as-is.** Near zero — a future doc edit to the mechanical clause might
miss one of the two copies for a session or two before the next dev-ops pass catches it.

**Alternative, if ever revisited.** `harness/SKILL.md:434` could point at `harness-handoff`'s
statement as the authority ("see harness-handoff: acts never yours") instead of re-deriving the
`exit 0` fact independently — but this reopens settled scope for a cosmetic gain, and T-10's own
`files:` list already named all four candidate files and the operator chose two.

severity: info · backlog row after ship · **leave**

## Checked, no finding

- **The three-layer hook stack** (`hooks/post-merge` shim → `post-merge-sweep.sh` body →
  `worktree_terminal.py` predicate). Each layer earns its slot: the shim is a path and nothing
  else (`hooks/post-merge:1-36`, deliberately, per its own comment — `test-hooks-install.py`
  case (e)'s RED PROOF repoints the shim and shows the sweep silently not running is exactly
  what a fused shim+body would hide); the body owns process orchestration (ship-then-remove,
  self-exclusion, dry-run) that is genuinely per-hook, not shared; the predicate owns
  classification only. Not a pass-through chain.
- **`core.hooksPath` as an init *procedure* step, not a gated check.** `check-state.sh` (the
  pre-commit gate) has zero references to `hooksPath` or `hooks/post-merge` — confirmed by grep.
  This is a real residual: nothing detects a clone that skipped T-12's manual step or had
  `core.hooksPath` reset later, other than INV-29 catching the *downstream symptom* (a worktree
  still standing) well after the fact, and that symptom-level backstop is explicitly named in
  `harness/SKILL.md:439-442` — "the hook removes the checkout when the merge lands, and
  `check-state.sh`'s INV-29 REFUSES while a worktree is still standing." So the residual is
  accepted **with** a compensating control named, just not a control that diagnoses the actual
  cause. Judged not worth a fold-in: adding a `git config --get core.hooksPath` check to
  `check-state.sh` trades a one-line diagnostic convenience against widening a pre-commit gate's
  scope into git-config auditing, and the existing backstop (INV-29) already makes the failure
  loud rather than silent, which is what the angle's "compensating control named" test asks for.
  Recorded here as a candidate backlog row, not raised as a finding: severity too low to earn
  one of the three parts (no observed drift, no double-authority).
- **Tests cross the interface, not past it.** `test-worktree-terminal.py` calls only
  `w.classify` / `w.classify_all` throughout (grepped) — no test reaches a private helper. This
  sharpens F1: the duplication in `post-merge-sweep.sh` is a real gap in the module's declared
  surface, not something the test suite forced by needing private access.

```yaml
VERDICT: PASS
DIGEST:
  headline: two altitude findings — a duplicated segment-resolution helper (fold-in) and a legitimate two-statement rule split (leave) — nothing applied, flag-only pass
  change_type: infra
  applied: []
  suite: n/a
  task: none
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-34-worktree-act3-enforced/.harness/harness/features/FEAT-34-worktree-act3-enforced/notes/receipt-harness-dev-ops-simplify-altitude.md
```
