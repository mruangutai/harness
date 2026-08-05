# Observations — harness-pm — FEAT-08-remove-cost-tracking

- 2026-08-05: send-back cycle S-01-c1. The dispatch said "carry Q1 and Q2 forward unchanged", but no
  artifact in the repo records their text — not BRIEF.md, not PLAN.md, not
  `runs/plan-product/state.yaml` (whose `steps[].note` carries only a one-line summary). A send-back
  gives the returning agent a fresh context, so an open question that lives only in the previous
  DIGEST cannot be carried verbatim. I returned them by ID with the gap stated rather than
  reconstructing the text.

- 2026-08-05: the unit-test coverage audit found three defects beyond the one the dispatch named.
  The generalisable method: `grep -ln <edited-path>` across every `bin/test-*.py`, then open each hit
  and separate a live-tree read from a `mkdtemp` fixture. The live reads are not obvious from the
  test's name — `test-team-catalog.py` reads `harness/SKILL.md` (`:44`) and `docs/harness/SPEC.md`
  (`:45`), and `test-validate-digest.py` extracts the normative DIGEST templates out of
  `docs/harness/SPEC.md` and `.claude/skills/harness-team/SKILL.md` (`TEMPLATES`, `:23-29`). Two
  documentation tasks and one skill-file task therefore had unit tests on their surface that their
  `verify:` never invoked.

- 2026-08-05: three false positives worth knowing, because each looks like a hit under a bare grep.
  `test-harness-yaml.py:84` contains the literal `.harness/README.md`, but as a grant glob asserted
  against `team-config.yaml` — it never reads the README's content. `test-gh-sync.py` writes a
  `harness.json` fixture carrying only `{"github": …}` — no cost surface. `test-check-state.py:4`
  states outright that it runs against fixture trees, "never against the real repo state".

- 2026-08-05: A-2. SC-01 was unreachable because THREE other approved requirements (SC-04's fixture
  pin, SC-14's marker clause, D-07) each mandate a thing SC-01 forbids. The tell was in SC-14's own
  wording at drafting time: "every remaining X mention carries a marker" PRESUPPOSES mentions remain,
  which is the direct negation of an absence-grep over the same files. A cross-criterion read for
  presupposition would have caught it at plan time; reading each SC on its own did not.

- 2026-08-05: A-2 measurement. The sweep returned 6 files at 95c1c38 and the amended expected set is
  also 6 — but for BUILD.md/SPEC.md the CAUSE differs (raw pre-T-10/T-11 hits now, removal markers
  after S4). Equal counts across a concurrent edit are not confirmation. Every figure was pinned with
  `git grep <SHA>`, never a working-tree grep, because harness-documentor was mid-S4 on both files.

- 2026-08-05: A-1. The Lanes row miscited `team-config.yaml:155`/`:197` for `.harness/harness.json`;
  both are `.claude/skills/harness/bin/**`, and the live config is granted at `:196` — a line the
  plan never named. The same miscitation was repeated in T-04's `execution_mode:` line, which is the
  line an executor reads. Fixing a lanes table without grepping the task bodies for the same citation
  leaves the artifact self-contradictory.

- 2026-08-05: A-3. The survey's grep defines the search space, and the search space silently becomes
  the criterion. T-10's per-site table was built from compound tokens (`cost_usd`, `cost-report`,
  `max_cost`, `per_feature_usd`, `INV-11`); two live SPEC sites use only the plain word "cost", so
  they were invisible to the survey AND to every `verify:` clause in the feature, all of which count
  the same tokens. A site outside the token set is not merely unlisted — it is unfalsifiable. The
  general move: when a task's dispositions are enumerated by grep, one `verify:` clause must use a
  BROADER pattern than the survey did, with the legitimate survivors enumerated as an allow-list.

- 2026-08-05: A-3, Site A. The defect was CAUSED by a mandated edit. T-10 removed the cost line from
  the §10.3 briefing instruction; the worked example 25 lines below, in the same section, still
  rendered the row — so the spec forbade a thing and then demonstrated it. A disposition that changes
  an instruction must ask whether a worked example of that instruction exists in the same section;
  the example is the copyable artifact and outranks the prose in practice.

- 2026-08-05: A-3. Amending a task that has already EXECUTED and passed silently invalidates its
  receipt. T-10's four clauses were green against a nine-row table; A-3 makes it eleven. The receipt
  proves the rows it was written against, not the table's current contents — and nothing in the plan
  file can re-open the task, so the re-dispatch signal has to travel in the DIGEST.

- 2026-08-05: a lane resolved at plan time by READING team-config.yaml was wrong; the same question
  ASKED of the live hook (exit 0 on one path, exit 2 on the other) was right. Fourth recurrence of
  the routing wall.

- 2026-08-05: A-4. The dispatch handed me a replacement-coverage anchor — "unknown-key tolerance is
  already load-bearing at `test-validate-digest.py:1213` and `:1233`" — as the entire safety argument
  for deleting a fixture. Both lines are COMMENTS, not assertions, and `:1232-1234` names "unknown key
  ignored" as the BAD shape its detector rules out, i.e. the opposite property. Opening the cited
  lines is not enough by itself either: the decisive move was a MUTATION test — build a strict variant
  of the tool under test (here `validate-digest.py` with an unknown-key rejection), run the real suite
  against it via the suite's own `VALIDATE_DIGEST_BIN` override, and see which cases redden. Result: 2
  of ~90, one of them the fixture about to be deleted. Two false starts first — the mutant must be run
  with `PYTHONPATH` set to the tool's own dir (its sibling import fails silently as a whole-suite red),
  and my first mutant flagged `headline`/`artifact`, which are checked outside the schema map, so
  EVERY case failed and the run looked meaningful. A mutant that reddens everything is a broken
  mutant, not strong coverage.

- 2026-08-05: A-4. A criterion whose expected set is a superset-prohibited/subset-allowed list is the
  only shape that can serve as a falsifier for edits nobody's `verify:` covers. Two of the six files in
  the sweep are exactly the two files the outstanding follow-up edits touch, so the criterion fails
  until both land. Stating "reachable, conditional on X landing" is different from "passing" and both
  belong in the DIGEST — an amendment that says only "reachable" reads as done.

- 2026-08-05: A-4, the near-miss. I wrote a replacement requirement to delete the fixture the sweep
  was hitting, and nearly shipped it having grepped only the ONE anchor the dispatch named. The file
  had THREE hits; the third was the comment on the fixture that SURVIVES, so the fix would have left
  the file in the sweep and re-created the very defect it was amending. The rule: when a criterion is
  "file X leaves the sweep", enumerate every hit in X with the criterion's OWN full pattern and
  confirm each sits inside text the edit removes. File-level arithmetic (6 minus 2 is 4) is not
  evidence; hit-level enumeration is. Corollary: greping one token of a five-token pattern verifies
  one fifth of the claim.

- 2026-08-05: A-4. Working-tree greps became unstable for a second, unrelated reason: a sibling
  feature's worktree under `.claude/worktrees/` is a full second copy of the repo inside the search
  path (78 files vs 6). `.gitignore` hides it from `git grep`, so a SHA-pinned figure and a
  working-tree figure disagree by an order of magnitude with neither being wrong. Whether an
  `--exclude-dir` flag is a no-op at an older SHA is answerable as a fact about the disk —
  `stat -f '%SB'` on the worktree dir vs `git log -1 --format=%cI` on the commit — rather than as an
  inference about grep semantics.

- 2026-08-05: A-5. Two inputs disagreed on a denominator (75 vs 81) and I was told to decide which was
  wrong. NEITHER was: `.harness/features/*/runs/**` is gitignored (`.gitignore:7`), so the figure is a
  working-tree count that GROWS as the feature creates its own run dirs. `stat -f '%SB'` on each run
  dir reconstructed both instants exactly (67+8=75 at the goal-check, 67+14=81, 67+15=82 now). Two
  measurements of an untracked tree taken at different times are not in conflict and neither is
  falsifiable against the other; the reconciling variable is time, and it is measurable.

- 2026-08-05: A-5. I was handed "git diff --stat ae2443d..HEAD over these dirs' feature.yaml and runs/
  paths is empty" as the teeth for a criterion. Over `runs/` it is VACUOUSLY empty —
  `git ls-tree -r ae2443d -- .harness/features/ | grep -c 'runs/'` returns 0, nothing is tracked there.
  An empty diff over untracked paths is the already-empty-absence-grep failure wearing a different
  hat. Before writing any emptiness assertion, check that the paths are IN the object store at the
  baseline SHA.

- 2026-08-05: A-5. Two shell facts that break a criterion written by eye. The session shell is `zsh`:
  unquoted `$VAR` does NOT word-split (a seven-path list collapsed into one filename and returned 0),
  and an unmatched glob ABORTS the command rather than passing through. `FEAT-05-pyyaml-file-parsers`
  has no `runs/` dir at all, so `<seven>/runs/*/state.yaml` dies under zsh while working under bash.
  `find <dirs> -path '*/runs/*/state.yaml'` is the portable form. Run any criterion command literally,
  in the real shell, before it goes into a signed artifact.

- 2026-08-05: A-5. `bash-write-guard.sh` blocks `cp`/`rm`/redirects whose target is written as an
  unexpanded shell variable (`$SCR/...`), including into the sanctioned session scratchpad — it cannot
  expand the variable so it fails closed. The same command with the path spelled literally is allowed.
  Correct behaviour, but it means scratch probe scaffolding must use literal absolute paths throughout.

- 2026-08-05: A-5. A JSON config claimed "byte-identical" was not: `ae2443d` carried the `u2014` escape
  where HEAD carries a literal em dash — a re-serialization with equal decoded values. Two clauses,
  not one, is the honest shape: decoded-value equality catches semantic drift, and a byte diff with
  the ONE known exception named catches escape/whitespace changes the decoder cannot see (probed by
  re-encoding a space as its U+0020 escape: byte clause red, decoded clause green). Writing the escape
  sequence into a markdown artifact is itself a hazard — it renders as the decoded character and the
  sentence becomes self-contradictory; name the codepoint in words instead.

- 2026-08-05: A-5. A mutant probe against a `git diff A..B` clause cannot be run by perturbing a
  working copy — the command reads two commits and returns green regardless. `git clone --local
  --no-hardlinks` into the scratchpad, perturb, commit THERE, run the criterion's command against the
  clone. It is cheap and it converts "I argue this discriminates" into a measurement.

- 2026-08-05: A-5 send-back. A criterion clause that is REPLACED rather than repaired can silently drop
  the surfaces it guarded, while the amendment prose still claims nothing was weakened. The failing
  clause here proxied a real constraint through a diff-line prohibition any reformat trips; the repair
  was a named tolerance (this one line and no other), not deletion. Before writing "nothing was
  weakened", list the files each approved clause named and check each still appears in the replacement.

- 2026-08-05: A-5 send-back. A shell command written inside a markdown BLOCK QUOTE inherits the quote's
  indentation when a reader strips the `> `. Shell tolerates leading whitespace; `python3 -c` with a
  multi-line body does NOT — it raises IndentationError. Criterion commands embedded in prose must be
  single physical lines, and the way to prove it is to extract the fenced blocks from the artifact
  programmatically and execute them, rather than re-running what was typed in the terminal.

- 2026-08-05: A-5 send-back. Resolving an ambiguous filename in a criterion by widening to a glob
  (`'*SKILL.md'`, 20 files) rather than to the measured set (3 files) buys no coverage and creates a
  FALSE-FAIL: a file added later that legitimately mentions the token adds a `+` diff line. Measure
  both scopes; if the residual is identical, take the narrow one and name the uncovered remainder.

