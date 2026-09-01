# Research — FEAT-41 — the vocabulary surface, measured at ee66ae2

BLUF: the grilling's facts hold. Three of its counts are LOW, and one design point it left
implicit has to be settled before the plan works. Everything below is my own measurement at
ee66ae2 in this worktree.

## Three counts the grilling under-reports

1. **`feature.json.status` has ELEVEN non-test read sites, not four.** `check-state.sh:113`
   (abandoned skip), `:603` (STATUS_ORDER / seam notes), `:1048` (INV-28), `:1425` and `:1500`
   (INV-26), `:1577` (INV-30); `board_lifecycle.py:503` and `:988`; `check-plan-routes.py:418`;
   `gh-sync.py:226`; `worktree_terminal.py:271`. Plus ONE writer, `gh-sync.py:580`.
   `worktree_terminal.py:271` is the awkward one: it reads the LANDED file on the default
   branch through `git show`, so repointing it means reading `plan.yaml` at that ref.
2. **`board["stations"][key]` has 20+ non-test sites across SIX modules**, not just gh-sync:
   `factory_claim.py:268,302,419`, `factory_land.py:95`, `factory_decompose.py:328`,
   `board_lifecycle.py:438,522,809,820`, `gh_board.py:116,118`, `check-state.sh:1403`.
   Lowercasing everything therefore touches the factory, not only the mirror.
3. **The `plan-merge.py` rename touches 13 live files, not 11.** The grilling missed
   `.omp/agents/harness-orchestrator.md` (2 refs) — and `.omp/agents` is CANONICAL under
   DEC-202 (`sync-agent-adapters.py` docstring: "edit the OMP source, then run `--apply`");
   `.claude/agents/*` are generated adapters. `test-plan-merge.py` carries 12 refs, not 13.
   Feature notes and observations under `.harness/harness/features/**` are records, left alone.

## The design point the grilling left implicit

`check-domain.sh` exits 0 for a payload with no `agent_type` — that is how the MAIN SESSION is
exempt, by mechanism (`check-domain.sh:508-514`). So a plan.yaml denial written into the DOMAIN
region would not bind the main session, and item 5 says every LLM Edit is denied. The denial
therefore belongs in the SHAPE region, which DEC-180 makes independent of domain and binding on
every author including the main session. That is also where `plan.yaml` is today explicitly
EXCLUDED, with a comment (`check-domain.sh:1017-1022`) arguing the exclusion — so DEC-182 takes
an amendment and that comment is replaced, not merely edited around.

## Other load-bearing facts

- `harness.json` `github.board.stations` is a MAPPING today; the six keys are also the six
  values. Under the mandate it becomes an ordered list, and ORDER matters: `check-state.sh:513`
  `STATUS_ORDER` drives the seam-note table, so the declared order is read, not just the set.
- `gh_board.derive_station` (`gh_board.py:87-120`) already derives the parent's station from
  plan.yaml task statuses. The projection function is an EXTENSION of it, not a new idea.
- `gh-close-gate.py` is the working model for the identity-gated Bash refusal: shlex tokenizing,
  basename compare, `eval`/`bash -c` re-scan (DEC-203 section 8 records why a regex is not enough).
- Every bin test runs standalone and fast: `test-factory-config.py` 0.11 s, `test-gh-board.py`
  0.77 s. Per-task `verify:` can name one file and stay far under 60 s.
- `BUDGETED_FIELDS` (`check-plan-routes.py:286`) excludes `intent:`, so a complete dispatch
  prompt costs nothing against the 50-line machine budget.
- `.harness/glossary.md` does NOT exist. DEC-149 says a feature that pins a vocabulary updates it
  in the same pass; creating it is outside #845's seven items, so it is an open question, not a task.

## Open

- Whether the terminal marker `abandoned` should live in `harness.json` (it names no column) or
  as a code constant. The plan takes the code constant; see D-05.
