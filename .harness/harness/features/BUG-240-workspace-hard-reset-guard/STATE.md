# STATE

## Current

- feature: BUG-240-workspace-hard-reset-guard
- run: 2026-09-07-03-validator (review panel, cycle 1, over the fixed pin) — COMPLETE, **PASS**,
  `severity_max: med`, `send_backs: 0`, no `must_fix`. **The VALIDATE phase is COMPLETE.**
- status: review (plan.yaml `status: review`; GitHub parent #1473, T-01 #1474, T-02 #1475 at the
  review station; milestone #57)
- `review_sha` = `bae47f3cb75f652c54cec68d7411e1bc26ba41f5`, unchanged and still correct: the two
  commits after it (`af0c2b4f`, `e34cb74b`) touch ONLY `STATE.md`, `feature.json` and
  `observations/` — `git diff --name-only bae47f3c..HEAD`, no code path among them. Anything
  quoting the older pin `ed047fde` is stale.
- **F-PANEL-01 is RESOLVED**, on two independent chains: security-reviewer reproduced the cycle-0
  premise against the fixed predicate in a `/tmp` probe (old `realpath` comparison False,
  `samefile` True on a real case-mismatched pair), and code-reviewer traced the new test case 8,
  which qa confirms RAN green rather than self-skipping on this host. SC-03 holds as worded.
- blocking `test_matrix` gate: `matrix_ok: true`; unit satisfied, integration `not_applicable`
  (a production file is touched, so the tests-and-docs-only predicate does not fire). Re-measured
  by this orchestrator, not taken on the digest's word: `env -u HARNESS_AGENT_TYPE python3
  tests/unit/test-factory-workspace.py` → exit **0** in a variable, `^FAIL ` **0**, `^ok ` **39**,
  `skip` **0**.
- cycles: **5 of 10**, UNCHANGED — `send_backs: 0`, and a clean first-pass run adds zero
  (DEC-157). runs: **12 of 20**, under budget.
- NEXT: **nothing in validate.** SHIP is a separate mission and the main session's to trigger.
  This orchestrator does not ship, does not open or merge a PR, and does not remove the worktree.
  The ship phase needs the CEO briefing built by reading the digests below from disk — including
  the plan and build phases, which no note in context covers — plus the backlog rows and the
  operator's decision.
- commits: `3e3147eb` plan · `6cd80e1b` eng T-01+T-02 · `d5a9f60b` qa · `c5f54761` simplify ·
  `ed047fde` validate seam · `4b87f5d2`+`36ee4a84` mirror · `bae47f3c` F-PANEL-01 fix ·
  `af0c2b4f`+`e34cb74b` bookkeeping.
- digests, read by pointer, never swept: `runs/2026-09-07-03-validator/digest.md` (cycle-1 panel,
  the current verdict) · `runs/2026-09-07-02-validator/digest.md` (cycle-0 panel, all five
  findings in full) · `runs/2026-09-07-02-eng/digest.md` (the fix) ·
  `runs/2026-09-07-1-eng/digest.md` (simplify) · `notes/qa-2026-09-07-1.md` (the qa segment) ·
  `notes/review-harness-{code-reviewer,qa,security-reviewer,ui-reviewer}-c1.md`.

### Backlog rows for the CEO briefing — assessed, NONE gating

Do not re-litigate any of these; do not convert one into a fix cycle. Full text in the two panel
digests.

- **F-C1-01** (low; code-reviewer raised med, lead re-rated) — NEW at cycle 1.
  `factory_workspace.py:142-148`: `PermissionError` is an `OSError` subtype, so a denied
  `os.stat` drops into the fallback's case-blind `realpath` string comparison. The re-rating is an
  ARGUMENT, not a measurement, and is recorded as such: a denial hits both spellings of one
  directory, `isdir(path/.git)` is then also False, `_main` routes into the clone arm, and `git
  clone` into a non-empty directory refuses at exit 2. Defence-in-depth hygiene, not a closed harm
  chain. **No reviewer reproduced it live.**
- **F-PANEL-02** (med, TOCTOU) — no REQ/SC asks for locking; a scope change the operator owns.
- **F-PANEL-03** (low) — the docstring/D-01 containment rationale is false as to mechanism; the
  outcome is safe and the correction is **pm's**, not eng's.
- **F-PANEL-04** (low) — refusal copy folds the verb into `what` where 20 sibling sites use a noun
  phrase. ui-reviewer confirms the copy is byte-unchanged from c0: no new instance at c1.
- **F-PANEL-05** (med) — `code_grade` grade_2 on `_main`, driven solely by ABC (33.0 → 35.7) against
  a bar of 20. The intended cost of T-02's inline guard; guard count stays two, below the
  reviewer's own extraction trigger of three.
- **ALT-5** (med) — the dirty check refuses on non-ignored UNTRACKED files, which no destructive git
  command can destroy. Narrowing it changes behaviour case 4 pins and the operator signed (O-08).
- **qa F-01 / F-02** (low) — F-02 is `PF-d795aab03bf4a49e7ef3ef6614024cdf`, KEPT by the operator at
  signature; `plan.yaml approval.rulings` overrules five more.
- **Adequacy note the briefing must carry** (the lead's own): no fresh red-then-green was measured
  at cycle 1 — qa was author-nothing and established case 8's discriminating power by tracing, not
  by mutating. The mutation proof is this orchestrator's prior `/tmp/b240red` run (post-fix 39/39;
  the identity block alone reverted to the string comparison → exactly one failure). Prior-cycle
  evidence, quoted as such.

### Working memory

- production file `.claude/skills/harness/bin/factory_workspace.py`; `.agents/skills` is a symlink
  to `../.claude/skills`, so there is ONE file with two spellings. Never deduplicate them.
- test file `tests/unit/test-factory-workspace.py`; **39** checks, 10 BUG-240 assertions. Cases
  2/3/4 and case 8 drive REAL git via `real_repo()`; they are NOT monkeypatched.
- case 8 self-skips on a case-sensitive filesystem (it probes a `PROBE`/`probe` pair). Here it
  RUNS. On a case-sensitive CI box it prints `skip` and the suite still reads green, so there the
  ok-line COUNT, not the exit code, is the signal — and nothing in the gate enforces that.
- running the unit suite from an agent tool needs `env -u HARNESS_AGENT_TYPE`, and the runner's
  exit status must be captured in a variable, never read off its last line.
- the test file anchors its import two dirs up, so a copied tree needs a `.harness/team-config.yaml`
  marker AND all of `bin/*.py` (factory_config imports factory_gh), or it raises at import.
- `runs/**` is gitignored here, so run bookkeeping never appears in `git status`.
- the bash write guard resolves only LITERAL ABSOLUTE paths, and refuses a heredoc as a redirect.
  Write helper scripts with the Write tool; pass absolute paths.
- plan.yaml's T-01/T-02 `intent:` blocks end with stray tool-call artifact lines (`</content>`,
  `<parameter name="i">…`). They parse as part of the block scalar; they are NOT instructions.
- lead dispatches died at ~14 min twice under the old pattern; with ONE segment per dispatch, four
  have completed (11m54s, 17m27s, 5m13s, 18m33s). Keep one segment per dispatch.

## Open Questions

- Q1 (non-blocking, harness defect): `runs/2026-09-07-01-product/digest.md` fails the lead digest
  contract and CANNOT be repaired — corrections may only append, and validate-digest.py parses the
  FIRST `DIGEST:` block. check-state.sh reports a VIOLATION until that directory is removed.
- Q2 (non-blocking, harness defect): INV-32 grades the panel record only on an APPROVED plan, so a
  malformed readers index is undetectable until the moment of signature.
- Q3: RESOLVED at signature — the operator KEPT both low-severity plan-panel findings.
- Q4 (non-blocking, harness defect): `notes/handoff-<phase>.md` cannot be written from a worktree
  for a feature not yet on the default branch. check-domain's shape gate calls
  `handoff_done_when.py` with the PROJECT root, and `_feature_dir()` rebuilds the feature dir under
  it, so `Authority:` pointers resolve against a `<main>/.../BRIEF.md` that does not exist
  (measured: `Authority pointer 'brief-sc:SC-06' is unresolved … [Errno 2]`). No agent in a
  worktree can close it. **This `## Current` is the handoff.**
- Q5 (non-blocking, harness defect): a host-killed lead dispatch leaves `runs/<id>/state.yaml`
  reading `status: running` forever and **the slug is then reused** — the fix run wrote into the
  killed build run's `runs/2026-09-07-01-eng/`. Reconciled by hand; nothing prevents a recurrence.
- Q6 (non-blocking, harness defect, from simplify): two of four reader results were unreachable
  through the normal return path (one settled FAILED while its fence carried `VERDICT: PASS`; one
  had to be recovered from `history://`). The cycle-1 panel returned all four cleanly, so it is
  intermittent, not systematic.
- Q7 (non-blocking, process): the cycle-0 fix digest asserted red-then-green but carried neither
  output, though the dispatch required both verbatim. The claim was true — proven independently —
  but such a digest is indistinguishable from one that invented the evidence.
