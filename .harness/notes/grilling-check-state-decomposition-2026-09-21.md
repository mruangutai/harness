# Grilling — check-state.py decomposition (wave 2 of the control-plane quality work) — 2026-09-21

## Destination
`check-state.py`'s ~2,000 lines of module-level invariant blocks become one function per
invariant, registered in one ordered table of records that a `--list`, `--only`, `--feature`
and `--changed` verb read; three consolidation-audit rules lock the shape (no module-level
invariant code, `reads` covers what a function opens, `authority` resolves and is not struck);
every existing suite's output is byte-identical except the enumerated, ruled divergences.

## Mission
mission: plan
reason: new enforcement surface — three audit rules and four CLI verbs — plus a ~3,000-line diff
in the file every gate depends on; cause known and files named, but rule 3 of the patch test fails.
confirmed-by: operator

Lane, as for FEAT-61: main session writes the diff in a worktree (DEC-174); Harness runs plan,
review and goal-check only.

## Settled
- Shape → one file; `INVARIANTS: tuple[Inv, ...]` of records
  `Inv(name, run, scope, reads, contract, authority)`; module body is the DEC-234 bootstrap
  prologue, the table and `main`. Not a package (blast radius on the bootstrap, `load_repo_module`
  callers and six path consumers); not functions-only (ordering stays implicit, nothing declares
  the set for a lock to read).
- `authority` → present and AUDITED (option 3): every value must resolve in
  `DECISIONS-INDEX.md` and must not be struck; a strike goes red in the consolidation audit until
  the invariant is re-cited or retired — DEC-188's "removed from every gate" made mechanical.
  Decisions amended in place under the same number are an accepted, recorded limit.
- The 47 `except Exception` sites → wave 3, untouched here; byte-identity is this wave's proof.
- Invariant families (INV-3/4/5 one read; INV-38..41 one SC loop) → one row per number; the
  family's parsed input is read once into ctx, each function judges its own rule.
- Blocks looping over features inside repo-level code (INV-3, INV-15, INV-26 and its
  BEGIN/END sub-blocks) → loop moved into the runner; the resulting output-order change is an
  enumerated, red-first-tested, ruled divergence; the INV-26 marker test slice is rewritten
  against the function.
- Verbs → all four ship: `--list`, `--only INV-NN`, `--feature <id>`, `--changed`.
- `--changed` → the reads-lock ships with it (a function body opening an input — file glob,
  `git`, `gh`/board — its row does not declare fails the audit); without it `--changed` is
  fail-open by construction.
- `--changed` posture → loop only. Pre-commit (AGENTS.md rule) and CI `integration` always run
  the full table; the audit asserts no workflow or hook script passes `--changed`.
- Primary loop path → hooks, not agent memory: writers that already run after a feature write
  (`plan-merge.py` and peers) run `check-state.py --changed` and surface its rows.
  `.harness/README.md`'s "run it any time" sentence gains the mid-edit/pre-commit split; no
  SKILL.md text and no preload weight; AGENTS.md's pre-commit line is unchanged.
- Retired numbers (INV-9, INV-10) → a `RETIRED` map so `--list` and old digests resolve
  (DEC-205); never reused.

## Not yet specified
- The exact `reads` vocabulary (file globs vs. named inputs like `git`, `board`, `worktrees`)
  and how the lock recognises an "open" in a function body (string literals, accessor calls,
  subprocess argv). pm sharpens with the extractor that produced the sample table.
- Which writers besides `plan-merge.py` run `--changed` after their write.
- Per-function grades once the blocks are functions: several (INV-26 ~260 lines, INV-38..41
  ~440, INV-3/4/5 ~280) will grade below bar on day one; split or ruled exemption is decided per
  function in the plan, not pre-sliced here.

## Out of scope
- Any change to what an invariant reports (wave 3 owns the catch sites; verdict changes need
  their own ruling).
- Splitting into a package.
- Performance: the script is I/O-bound; only selective execution changes wall time, and that is
  the verbs above, not an optimisation pass.
- The 13 pre-existing check-state violations on this tree (9 legacy DEC-156 digests, 4 stale
  FEAT-53 worktrees) — real findings, not this wave's.

## Facts I verified (so pm does not re-derive them)
- 3,019 lines; 56 module-level `if/for/try/with` blocks totalling 1,998 lines; 22 functions
  totalling 198 lines; accumulators `bad`/`warn` at L94 with 116/24 append sites; exit
  `1 if bad` at the tail — measured by AST at `80b108f2`.
- 40 distinct INV numbers; block sizes/inputs/loop scope per block extracted at `80b108f2` (the
  sample table in this conversation was built from that extraction, not invented).
- Eight integration suites `tests/integration/test-check-state*.py` (6,107 lines) drive the
  script as a subprocess; one uses `exec_module`, some `from check_state` helpers — the
  byte-identity corpus.
- CI `tests.yml` reads exit code AND row count and refuses a pass on an empty corpus (L286–300).
- Path consumers of `check-state.py`: `post-merge-sweep.py`, `feature-worktree.py`,
  `feature-record.py`, `board_lifecycle.py`, `harness_yaml.py`, `gh_cost_log.py`,
  `feature-schema.json`, skills `harness-add-repo` and `harness-distill` — none passes a flag.
- No agent SKILL.md instructs running the checker; invocation guidance lives in AGENTS.md
  (pre-commit, full run) and `.harness/README.md:90`; skill references cite INVs by number only.
- `gen-decisions-index.py` produces the index the authority audit reads; DEC-188 keeps strike
  records so citations resolve.
- Wave 1 precedent for the locks and divergence ledger: `check-plan-routes.py
  --consolidation-audit`, `FEAT-61/notes/build-divergences.md` (15 ruled divergences).
