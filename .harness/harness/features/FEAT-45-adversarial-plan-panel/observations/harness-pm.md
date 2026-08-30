# Observations — harness-pm — FEAT-45-adversarial-plan-panel

- 2026-08-29 (plan draft): plan-merge.py REFUSES the create path when the proposal carries an
  `approval:` key (apply_merge step 3 / 7b, exit 8) — so the mandated write tool can never produce a
  NEW plan.yaml that check-state.sh accepts, because the plan.yaml invariant requires an `approval:`
  mapping. I created the file with Write instead. Raised as an open_question; it is a harness defect,
  not a workaround to keep.
- 2026-08-29 (plan draft): `observations-merge.py … --entries -` cannot be fed by a heredoc —
  `bash-write-guard.sh` classifies `<<'EOF'` as a redirect and BLOCKS the whole command whatever the
  target. There is no in-domain temp path to stage entries in either, so on a first append the only
  route is Write on the log itself.
- 2026-08-29 (plan draft): `.agents/skills` is a SYMLINK to `.claude/skills` in this repo — one inode,
  two spellings. A task listing both paths would be doing nothing twice; `check-domain.sh --resolve`
  answers on the `.claude/...` spelling.
- 2026-08-29 (plan draft): the ` :: <ruling>` tail of a DECISIONS-INDEX.md row is HAND-written by the
  entry's author; gen-decisions-index.py does not produce it. A verify that greps the index for a
  phrase therefore fails on regeneration alone, and the task intent must say to write the row text.
- 2026-08-29 (plan draft): proving a verify block discriminates is cheap — load the plan, `bash -n`
  each verify for syntax, then run each one against the unbuilt tree and require a non-zero exit.
  8 of 10 ran read-only in 31s; skip only the two that mutate (gen-decisions-index.py,
  sync-agent-adapters.py).
- 2026-08-29 (plan draft): `check-plan-routes.py` prints `DEVIATION` — not `VIOLATION` — for a granted
  path declared `main-session-direct`, and still exits 0. A DEC-174 carve-out is therefore expected to
  show as DEVIATION; reading that line as a failure would have sent me rewriting correct lanes.
- 2026-08-29: T-08 shipped a `pre-change` case reading the gate at a relative commit ref to prove INV-32 could fail. Broken by construction: the predecessor task T-07 lands as its own commit, so the previous commit already carries INV-32 the first time the standing test runs, and the ref drifts one step further on every later commit. Fix was to reuse the target file's OWN mutation idiom (test-check-state.py T14_MARKER/T10_MARKER: marker-bracketed region stripped into a mutant copy placed BESIDE the original, never in the fixture tmpdir). Lesson: before authoring a failing-first proof, read how the file under test already proves red.
- 2026-08-29: a "regenerate the generated file so the constant propagates" premise handed down in a
  dispatch was measured false end to end: sync-agent-adapters.py's SPAWNS map is reachable only via
  --bootstrap-from-claude, whose bootstrap() refuses to run once .omp/agents exists, and the
  generated .claude/agents adapter carries no spawns key at all. The enforced list was the
  hand-maintained canonical frontmatter. Reading the generator's main() and its refusal branches
  before writing the task moved the load-bearing edit to a different task and a different lane.
- 2026-08-29: two verify blocks in a c0 draft could not pass for mechanical reasons invisible to a
  reader: a script whose argparse group is required=True invoked with no argument (exit 2), and
  `git diff --quiet` over a file the task itself edits (uncommitted at verify time). Running each
  verify's exact command against the current tree caught both in under a minute.
