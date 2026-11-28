schema: plan/1
feature: FEAT-2641-local-working-files
status: plan
source_issues: [2641]

lanes:
  resolved_at: 0b5aa6e40d4bcf541addf40a4fdb7863303e3362
  rows:
    - surface: .claude/skills/harness/bin/**
      lane: main-session-direct
      reason: DEC-174 keeps the gate scripts, validators and refusing tools this feature changes with the main session.
    - surface: tests/**
      lane: main-session-direct
      reason: DEC-174 keeps each gate's owning tests and the reader registries with the change they grade.
    - surface: .gitignore
      lane: main-session-direct
      reason: check-domain.py --resolve answers NOBODY; an ungranted surface is a declared main-session step (DEC-179).
    - surface: .claude/skills/harness/templates/**
      lane: main-session-direct
      reason: check-domain.py --resolve answers NOBODY (DEC-179).
    - surface: .claude/skills/harness/schemas/**
      lane: main-session-direct
      reason: check-domain.py --resolve answers NOBODY (DEC-179).
    - surface: .claude/skills/harness/references/**
      lane: main-session-direct
      reason: check-domain.py --resolve answers NOBODY (DEC-179).
    - surface: .claude/skills/harness/SKILL.md
      lane: main-session-direct
      reason: check-domain.py --resolve answers NOBODY (DEC-179).
    - surface: .claude/skills/harness/teams/**
      lane: main-session-direct
      reason: check-domain.py --resolve answers NOBODY (DEC-179).
    - surface: .claude/skills/harness-uat/SKILL.md
      lane: main-session-direct
      reason: check-domain.py --resolve answers NOBODY (DEC-179).
    - surface: .omp/**
      lane: main-session-direct
      reason: check-domain.py --resolve answers NOBODY for agent definitions and commands (DEC-179).
    - surface: .harness/README.md
      lane: main-session-direct
      reason: granted to harness-documentor, but its committed-versus-local sentence describes the DEC-174 enforcement change and lands with it, as in FEAT-2581.
    - surface: .harness/harness/docs/**
      lane: main-session-direct
      reason: granted to harness-documentor, but the decision-record amendments describe the DEC-174 enforcement change itself and land with it, as in FEAT-2557 and FEAT-2581.

decisions:
  - id: D-01
    choice: A feature's notes/ (prototypes, mockups and screenshots included), runs/ (all of it, not only ui/) and observations/, and every project note under .harness/notes/, are local working files - ignored by four directory rules in .gitignore and templates/gitignore.snippet, untracked here with git rm --cached, history never rewritten, and a committed guard test refuses any tracked one; the committed feature record is feature.json, plan.yaml, BRIEF.md and STATE.md. Recorded as a new decision that strikes DEC-257.
    because: Since FEAT-71 about half of main's object growth is notes and runs and deleting them later never shrinks history; the operator ruled notes exist only for distill and expertise. An ignore rule alone leaves already-tracked files and in-flight branches tracked, so the index is guarded too.
    dec: DEC-260
  - id: D-02
    choice: check-state retires INV-8, INV-12, INV-15, INV-16, INV-17, INV-18, INV-36, INV-43, INV-46, INV-47 and INV-51 and INV-40 clause (c), numbers never reused; INV-7 keeps only the cycle arithmetic; the read-side evidence helpers in feature_record/evidence.py go with them. Rejected - keeping them as local-only check-state rows, because check-state is one program CI also runs and a row red in CI by construction is the defect being removed.
    because: Each reads a notes, runs or handoff file that is no longer in any checkout CI sees; write-time and yield-time checks keep grading the same artifacts while they exist on disk.
    dec: DEC-260
  - id: D-03
    choice: No working file gets a committed home. Answers, UAT results, ship briefings, prototypes, research, debug and review notes, handoffs, receipts and run records stay local; feature-record --decision, --evidence and --digest keep their write-time checks and record path and sha256 as provenance of a file not retained after cleanup. Rejected - copying ruling and answer text into feature.json, which DEC-150 caps at 300 lines, or into the PR body.
    because: The operator ruled notes need not be committed or included in any artifact; the decisions they informed are already in feature.json judgements, rework and runs and in plan.yaml approval and panel.
    dec: DEC-260
  - id: D-04
    choice: Expertise receipts stay at notes/expertise-receipt-<sha>.json as local working files; expertise-merge reads every receipt in the feature's local notes with no base-tree exclusion, merge-distill replays them unchanged, and already-applied state is main's merged Expertise plus the receipts' deletion by the post-merge cleanup. Distill runs stay registered in feature.json runs, committed, while their run directories stay local and are read at runtime by validate-digest and dispatch-guard as today. Rejected - committing receipts to a tracked path outside notes, which keeps a remote audit of applied ops but regrows the committed record the operator excluded.
    because: merge-distill already runs in the live distill worktree where the receipts exist, so committing them only served the git ls-tree exclusion that an untracked receipt makes dead.
    dec: DEC-260
  - id: D-05
    choice: One module, bin/working_files.py, owns cleanup - it deletes the feature directory's notes/, runs/ and observations/ and each project note feature.json project_notes lists, unlinking a symlink rather than following it. Callers - merge-gate.py merge-distill after a successful merge, gh-sync.py abandon --yes and reject --yes after their last mutation, and a new feature-worktree.py clean verb, refused below a terminal station, for a declined distill and for retrying a failed cleanup.
    because: The operator wants cleanup to be a routine, not a hand step; one implementation keeps the four terminal paths deleting the same set (generalizes DEC-238's abandon prune).
    dec: DEC-260
  - id: D-06
    choice: feature.json gains project_notes, a list of .harness/notes/<name> paths, written only by feature-record.py project-note; the orchestrator records the grilling artifact and every other .harness/notes/ path its dispatch hands it at its first cycle; cleanup deletes only listed project notes and never one no feature claimed.
    because: A grilling note is written before the feature id exists, so it cannot live under the feature; a recorded claim is the only way cleanup can tell a feature's project notes from spike and ad-hoc notes it must never delete.
    dec: DEC-260
  - id: D-07
    choice: gh-sync.py ship's validation precondition reads feature.json instead of notes/handoff-validate.md - it refuses, before any GitHub write, a feature with no validator-squad validate or fix run recorded PASS unless every task is main-session-direct. Rejected - deleting the precondition outright, which reopens BUG-1129 (the post-merge sweep shipping a feature whose validate is still in flight).
    because: Ship runs in the main checkout or a plain clone, where an untracked note never exists, so the old check would refuse every feature; the PASS run it stood for is already in the committed ledger.
    dec: DEC-260
  - id: D-08
    choice: feature-worktree.py remove refuses, exit 4, while the feature directory holds any file under notes/, runs/ or observations/ that git does not track, naming each and the clean command; the post-merge sweep therefore keeps a shipped feature's worktree until distill or clean has run. Rejected - deleting working files with the tree, because the sweep removes the worktree when the station-done record lands, which would destroy the observation logs before distill reads them.
    because: Ignored files are invisible to the existing dirty-tree gate and git worktree remove deletes them silently, so without this gate nothing protects them.
    dec: DEC-260
  - id: D-09
    choice: harness.json seam_era_start stays declared in the schema and template and in this repository's harness.json, unread once INV-43 retires.
    because: Removing a declared key makes every onboarded checkout's harness.json fail DEC-256's closed schema; a schema migration is outside this feature, and an unread declared key breaks nothing.
    dec: DEC-256

decisions_affected:
  - dec: DEC-257
    disposition: strike
    clause: is ordinary tracked
    successor: D-01
    reason: Run records become local working files, so the entry's ruling that every run file except ui is tracked is flatly contradicted (DEC-188).
  - dec: DEC-238
    disposition: amend
    clause: '**Abandon prunes.** `gh-sync.py abandon` removes `runs/` in the same act as recording the'
    successor: D-05
    reason: Abandon, reject, merge-distill and clean all delete notes, runs and observations through one routine, and INV-51 retires.
  - dec: DEC-238
    disposition: amend
    clause: '**Ship keeps the record and drops the rest.**'
    successor: D-01
    reason: prune-run-evidence.py is deleted; ship keeps no run evidence because none is committed.
  - dec: DEC-44
    disposition: amend
    clause: write answers to `.harness/notes/answers-<runid>.md`, never only into a run dir.
    successor: D-03
    reason: Answers are written to the feature's notes/answers-<runid>.md, a named local working file, not retained after cleanup.
  - dec: DEC-130
    disposition: amend
    clause: "`.harness/notes/` remains for\ngenuinely project-scoped artifacts (cross-feature research, docs sweeps)"
    successor: D-06
    reason: .harness/notes/ also holds pre-feature intake notes a feature claims through project_notes, and all of it is local.
  - dec: DEC-131
    disposition: amend
    clause: '**INV-12** now warns on any run dir absent from `feature.json`'
    successor: D-02
    reason: INV-12 retires; an orphaned run directory is local disk no CI gate reads.
  - dec: DEC-154
    disposition: amend
    clause: "check-state.py INV-16 now whitelists top-level state.yaml keys and rejects\nduplicates."
    successor: D-02
    reason: INV-16 retires; check-domain's write-time state.yaml whitelist (DEC-160) is the remaining mechanism.
  - dec: DEC-156
    disposition: amend
    clause: '**check-state.py INV-15:** every complete lead run needs a readable accepted digest'
    successor: D-02
    reason: INV-15 and INV-46 retire; validate-digest's yield-time append to the local digest.md stays.
  - dec: DEC-156
    disposition: amend
    clause: '**check-state.py INV-16 (mechanizes DEC-154):**'
    successor: D-02
    reason: INV-16 retires with the committed run checkpoints it read.
  - dec: DEC-157
    disposition: amend
    clause: "INV-7 rejects impossible attribution above the total and invalid\npresent evidence"
    successor: D-02
    reason: INV-7 keeps the attribution arithmetic and no longer verifies cycle evidence files.
  - dec: DEC-159
    disposition: amend
    clause: '`check-state.py` INV-17 demands all five sections of every handoff note'
    successor: D-02
    reason: INV-17 retires; the write-time shape gate grades every handoff while it is written.
  - dec: DEC-159
    disposition: amend
    clause: '(2) **The seam is graded.** `check-state.py` INV-43:'
    successor: D-02
    reason: INV-43 retires; feature-record run-start's succession refusal grades the seam at runtime.
  - dec: DEC-160
    disposition: amend
    clause: '3. **INV-18: run dirs without feature.yaml.**'
    successor: D-02
    reason: INV-18 retires with the run directories it keyed on.
  - dec: DEC-160
    disposition: amend
    clause: The whitelist is deliberately duplicated in check-state.py (INV-16) and
    successor: D-02
    reason: With INV-16 retired the whitelist lives only in check-domain.py.
  - dec: DEC-203
    disposition: amend
    clause: record `abandoned` before pruning `runs/` under INV-51 and DEC-238.
    successor: D-05
    reason: Abandon records the station, then the shared routine deletes notes, runs, observations and claimed project notes; INV-51 retires.
  - dec: DEC-208
    disposition: amend
    clause: keeps the INV-15 pointer
    successor: D-02
    reason: INV-15 retires, so the pointer the fail-open branch kept names nothing.
  - dec: DEC-215
    disposition: amend
    clause: "INV-17 demands all\nfive sections, `## Done when` included, of every existing handoff note"
    successor: D-02
    reason: INV-17 retires; the shared parser runs at write time only.
  - dec: DEC-230
    disposition: amend
    clause: a handoff with runs after it and no `succession` entry
    successor: D-02
    reason: INV-40 drops clause (c); run-start refuses a successor run without its succession at runtime.
  - dec: DEC-230
    disposition: amend
    clause: INV-40's four triggers are the ones that leave a trace in `feature.json`
    successor: D-02
    reason: INV-40 keeps three triggers once the handoff clause retires.
  - dec: DEC-237
    disposition: amend
    clause: INV-15/INV-46 distinguish
    successor: D-02
    reason: INV-15 and INV-46 retire; the refusal provenance stays in feature.json.
  - dec: DEC-252
    disposition: amend
    clause: INV-17 demanded `notes/handoff-validate.md` only at `done`, so
    successor: D-07
    reason: No note is demanded anywhere; ship's precondition reads the validate PASS from feature.json.
  - dec: DEC-252
    disposition: amend
    clause: keep their checks (INV-44, INV-51)
    successor: D-02
    reason: INV-51 retires; rejected keeps INV-44.
  - dec: DEC-253
    disposition: amend
    clause: '`notes/expertise-receipt-<sha256-runtime-id>.json`, committed in this PR.'
    successor: D-04
    reason: Receipts are local working files, never committed, deleted by the post-merge cleanup.
  - dec: DEC-253
    disposition: amend
    clause: reconstruction with original receipts before merge. Only this PR's receipts participate.
    successor: D-04
    reason: Only the reconstructed Expertise is committed; the replay reads this feature's local receipts.
  - dec: DEC-255
    disposition: amend
    clause: '**Receipts are committed with the run record.**'
    successor: D-01
    reason: QA runner receipts stay in the local run record and are read at yield; nothing commits them.
  - dec: DEC-174
    disposition: keep
    clause: Planning such a change through the harness remains fine and useful;
    successor: none
    reason: Every task is main-session-direct; the harness plans but never executes changes to its own gates.
  - dec: DEC-75
    disposition: keep
    clause: bundled with PLAN approval as one signature
    successor: none
    reason: The prototype becomes a local working file; its approval stays recorded by the plan signature.
  - dec: DEC-226
    disposition: keep
    clause: '--rework rounds=N,minutes=M --decision <path>` writes'
    successor: none
    reason: The ruling path stays write-time provenance; feature.json rework remains the committed record (D-03).
  - dec: DEC-231
    disposition: keep
    clause: A handoff's `## Done when` cites at least one
    successor: none
    reason: check-domain still enforces the brief-perspective authority at write time.
  - dec: DEC-112
    disposition: keep
    clause: '`.gitignore` is still merged by `merge-gitignore.py`, never hand-edited'
    successor: none
    reason: merge-gitignore.py ships the four new rules and removes the superseded run rules.
  - dec: DEC-145
    disposition: keep
    clause: never injected, so detail is free
    successor: none
    reason: Observation logs keep their role and writer; only their committed copy goes.
  - dec: DEC-74
    disposition: keep
    clause: produces a step in
    successor: none
    reason: The UAT file still gates the briefing; it is a local working file.
  - dec: DEC-191
    disposition: keep
    clause: admits only schema-declared keys
    successor: none
    reason: project_notes is added through the feature.json schema.
  - dec: DEC-256
    disposition: keep
    clause: (Draft 2020-12) is the sole
    successor: none
    reason: seam_era_start stays declared so no onboarded harness.json fails the closed schema (D-09).
  - dec: DEC-188
    disposition: keep
    clause: struck from the record
    successor: none
    reason: DEC-257 is flatly contradicted and struck; softer changes are amended.
  - dec: DEC-205
    disposition: keep
    clause: An entry states current truth directly.
    successor: none
    reason: Every amendment rewrites its clause in place; no amendment notes.

tasks:
  - id: T-01
    title: Ignore the four working-file classes, untrack the tracked ones, and guard the index
    traces: [SC-01, SC-02, SC-03]
    change_type: cross_module
    execution_mode: main-session-direct
    execution_reason: DEC-174 - merge-gitignore.py and the ignore contract are Harness enforcement surfaces, and .gitignore resolves to NOBODY (DEC-179).
    depends_on: []
    status: ready
    files:
      - .gitignore
      - .claude/skills/harness/templates/gitignore.snippet
      - .claude/skills/harness/bin/merge-gitignore.py
      - tests/integration/test-merge-gitignore.py
      - tests/unit/test-working-files-untracked.py
    verify: |
      set -e
      cd "$(git rev-parse --show-toplevel)"
      env -u HARNESS_AGENT_TYPE python3 tests/unit/test-working-files-untracked.py
      env -u HARNESS_AGENT_TYPE python3 tests/integration/test-merge-gitignore.py
      env -u HARNESS_AGENT_TYPE python3 .claude/skills/harness/bin/merge-gitignore.py . --check
      test -z "$(git ls-files -- '.harness/*/features/*/notes/*' '.harness/*/features/*/runs/*' '.harness/*/features/*/observations/*' '.harness/notes/*')"
      for p in .harness/kaya/features/FEAT-0-probe/notes/prototypes/FEAT-0-probe/shot.png .harness/harness/features/FEAT-0-probe/notes/mockups/shot.png .harness/harness/features/FEAT-0-probe/runs/r/digest.md .harness/harness/features/FEAT-0-probe/observations/a.md .harness/notes/probe.md; do git check-ignore -q --no-index "$p"; done
      if git check-ignore -q --no-index .harness/harness/features/FEAT-0-probe/plan.yaml; then exit 1; fi
      git merge-base --is-ancestor e2bffca0 HEAD
      git cat-file -e e2bffca0:.harness/harness/features/FEAT-2581-feature-record-package/notes/answers-2026-11-27-signature.md
    intent: |
      Product checkout: the Harness repository itself, worktree /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2641-local-working-files, branch feat/FEAT-2641-local-working-files, base e2bffca0. Every relative path is relative to it and every edit stays inside it. docs/spec.md, docs/decisions.md and docs/architecture.md do not exist in this checkout (docs/ holds PRINCIPLES.md only as prose); the governing record is .harness/harness/docs/DECISIONS.md - read DEC-112, DEC-238 and DEC-257 and this plan's D-01 and D-09 first. Run Python as env -u HARNESS_AGENT_TYPE python3.

      1. templates/gitignore.snippet. Inside the existing --- harness --- block, delete the rule .harness/*/features/*/runs/*/ui/** and the comment lines above it that call run records retained, committed evidence, and the sentence listing notes among the committed record. In their place write one comment stating that each feature's notes/ (prototypes, mockups and screenshots included), runs/ and observations/, and project notes under .harness/notes/, are local working files kept only for distill and expertise and never committed (DEC-260), then exactly these four rules, one per line, in this order:
      .harness/*/features/*/notes/
      .harness/*/features/*/runs/
      .harness/*/features/*/observations/
      .harness/notes/
      Keep every other line of the block (.harness/**/*.lock, .harness/.pyyaml-bootstrap, __pycache__/, *.pyc, .claude/worktrees/, .DS_Store and their comments) byte-identical.

      2. bin/merge-gitignore.py. OBSOLETE_RULES becomes the three run rules Harness once shipped: b".harness/features/*/runs/**", b".harness/*/features/*/runs/**", b".harness/*/features/*/runs/*/ui/**". HEADER keeps its first line and replaces the three rationale lines with: "# A feature's notes/, runs/ and observations/ and .harness/notes/ are local working\n# files, never committed (DEC-260). Everything else under .harness/ is committed on\n# purpose - it is the record of what shipped.\n". OBSOLETE_RATIONALE gains the three rationale lines of the previous HEADER, byte for byte as they read at e2bffca0, so a block an older version wrote loses them (removed only inside a Harness block, as today). _report_obsolete's parenthetical becomes "(superseded by the working-file rules, DEC-260)" and _report_removed says "removed superseded run rules". Rewrite the module docstring's OBSOLETE RULES paragraph to say the three run rules are replaced by the snippet's four working-file directory rules. Behaviour otherwise unchanged: obsolete removal first, then missing rules appended in one marker block, --check exits 1 naming every obsolete and missing rule and writes nothing, exit 0 when complete.

      3. Repository .gitignore. Run env -u HARNESS_AGENT_TYPE python3 .claude/skills/harness/bin/merge-gitignore.py . at the worktree root; it removes the run-UI rule and appends the four rules in a marker block. Then delete by hand the four comment lines that stood above the removed rule (they begin "# Harness run UI: screenshots and traces" and claim every other run record is retained, committed evidence), because they sit outside a marker block and are now false. Leave every other line as it is.

      4. tests/integration/test-merge-gitignore.py. Replace the cases that treat the run-UI rule as canonical: (a) a target holding each of the three obsolete rules, inside and outside a Harness block, is rewritten without them and gains the four rules; (b) --check on that target exits 1, names the three as obsolete and the four as missing, and leaves the bytes unchanged; (c) a block written with the previous HEADER loses its three rationale lines and keeps project lines; (d) the existing byte-preservation cases (order, CRLF, unrelated rules and prose) keep passing. Never weaken an existing assertion that still holds.

      5. Create tests/unit/test-working-files-untracked.py, a plain script in the style of the other tests/unit scripts: one "ok <name>" or "FAIL <name>: <detail>" line per assertion, exit 1 when any FAIL printed. Repository root is Path(__file__).resolve().parents[2]. Assertions: (i) git -C <root> ls-files -z exits 0 and lists at least one entry matching ^\.harness/[^/]+/features/[^/]+/feature\.json$ (non-vacuity); (ii) no entry matches ^\.harness/[^/]+/features/[^/]+/(notes|runs|observations)/ or ^\.harness/notes/ - on failure print the count, the first ten paths and the repair command: git rm -r --cached --sparse --ignore-unmatch -- followed by the four pathspecs ':(glob).harness/*/features/*/notes/**' ':(glob).harness/*/features/*/runs/**' ':(glob).harness/*/features/*/observations/**' ':(glob).harness/notes/**'; (iii) git check-ignore -q --no-index exits 0 for .harness/kaya/features/FEAT-0-probe/notes/prototypes/FEAT-0-probe/shot.png, .harness/harness/features/FEAT-0-probe/notes/mockups/shot.png, .harness/harness/features/FEAT-0-probe/runs/r/digest.md, .harness/harness/features/FEAT-0-probe/observations/a.md and .harness/notes/probe.md; (iv) it exits 1 for .harness/harness/features/FEAT-0-probe/plan.yaml, feature.json, BRIEF.md and STATE.md (positive control, DEC-169). The fixture ids carry no asserted token.

      6. Untrack. From the worktree root run git rm -r --cached --sparse --ignore-unmatch --quiet with the four pathspecs from step 5. Files on disk stay; history is not rewritten. Commit this index change as its own commit, separate from steps 1-5, so the deletion of the 2,750 tracked working files (1,954 notes, 750 runs, 46 observations at e2bffca0) is reviewable alone. Never use git add -f anywhere in this feature.

      Expected red before the work: at e2bffca0 test-working-files-untracked.py fails assertion (ii) with 2,750 paths and assertion (iii); keep that output for qa.
  - id: T-02
    title: Retire the check-state rows that read notes, runs or handoffs, and keep INV-7's arithmetic
    traces: [SC-04]
    change_type: cross_module
    execution_mode: main-session-direct
    execution_reason: DEC-174 - check-state.py is a CI gate and its tests grade it; the change is executed directly, never through the gate it changes.
    depends_on: []
    status: ready
    files:
      - .claude/skills/harness/bin/check-state.py
      - .claude/skills/harness/bin/check_state/*.py
      - tests/integration/test-check-state-*.py
      - tests/integration/test-checker-structure-locks.py
      - tests/integration/test-corpus-non-regression.py
      - tests/unit/test-handoff-policy.py
      - tests/unit/test-artifact-accessors.py
      - {path: tests/unit/test-check-state-retired.py, create: true}
    verify: |
      set -e
      cd "$(git rev-parse --show-toplevel)"
      for f in tests/unit/test-check-state-retired.py tests/integration/test-check-state-local-files.py tests/integration/test-check-state-feat59.py tests/integration/test-check-state-table.py tests/integration/test-check-state-records.py tests/integration/test-check-state-entry.py tests/integration/test-checker-structure-locks.py; do env -u HARNESS_AGENT_TYPE python3 "$f"; done
      for f in .claude/skills/harness/bin/check_state/seams.py .claude/skills/harness/bin/check_state/run_state.py tests/integration/test-check-state-handoff.py tests/integration/test-check-state-inv51.py; do test ! -e "$f"; done
      if grep -nE 'notes/|"notes"|runs/|"runs", *"\*"' .claude/skills/harness/bin/check_state/table.py; then exit 1; fi
    intent: |
      Product checkout: the Harness repository itself, worktree /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2641-local-working-files, branch feat/FEAT-2641-local-working-files, base e2bffca0; every edit stays inside it. docs/spec.md, docs/decisions.md and docs/architecture.md do not exist here; the governing record is .harness/harness/docs/DECISIONS.md - read DEC-156, DEC-157, DEC-159, DEC-205, DEC-230, DEC-252 and this plan's D-02 and D-09. Run Python as env -u HARNESS_AGENT_TYPE python3.

      Retire eleven rows. In check_state/table.py remove the Inv rows INV-8, INV-12, INV-15, INV-16, INV-17, INV-18, INV-36, INV-43, INV-46, INV-47 and INV-51, remove groups left empty (seams, runs-without-record, run-state, abandoned-evidence), remove their imports and the _RUN_STATE and _HANDOFF constants once unused, and add each number to RETIRED with the value "DEC-260 - <what it read> is a local working file no CI gate reads" naming its artifact (handoff notes for INV-17 and INV-43, member review notes for INV-47, run directories for INV-8, INV-12, INV-18 and INV-51, run checkpoints for INV-16 and INV-36, run digests for INV-15 and INV-46). Numbers are never reused (DEC-205).

      Delete check_state/seams.py and check_state/run_state.py whole. In check_state/feature_record.py delete inv_8, inv_12, inv_18, inv_43 with its helpers (_feat59_note_seq, _feat59_succession_entries, _feat59_successions, _inv43_run, _inv43_placement) and inv_47 with its helpers (_note_cycle, _note_verdict, _inv47_member_notes, _passed_validate_cycle, _passed_validate_cycles, _inv47_hit) and their comment blocks. In inv_40 delete clause (c): _inv40_handoff_need, _inv40_successions and their call; clauses (a) mission, (b) regate and (d) amendment stay byte-for-byte in behaviour; INV-40's reads tuple drops _HANDOFF and its contract keeps naming mission, regate and amendment only. collate_feat59 keeps its legacy-note behaviour for INV-39 and INV-40 hits and drops INV-43 and INV-47 handling. In check_state/plan.py delete inv_51 and its comment.

      INV-7: in inv_7 delete the feature_record.evidence load and the run_evidence_problems loop and the "historical cycle attribution without evidence" note; keep the nonnegative-integer total check, the per-run attribution type check, the unknown-attribution note and the attributed-exceeds-total violation. Its reads tuple becomes (_FEATURE_JSON,) and its contract "nonnegative per-run cycle attribution never exceeds the feature total; unknown history is noted".

      check_state/ctx.py: delete the station-to-handoff-note mapping and its comments, the runs/*/state.yaml iterator, and the seam_era_start attribute (D-09 keeps the harness.json key, unread); delete any other ctx member left without a caller. check-state.py: delete the handoff_policy import and anything else left unused. bin/handoff_policy.py stays (dispatch-guard and gh-sync use it).

      Tests. Delete tests/integration/test-check-state-handoff.py and tests/integration/test-check-state-inv51.py. In test-check-state-feat59.py delete the INV-40 succession groups, the INV-43 groups and the INV-47 groups; every INV-39 and INV-40 mission, regate and amendment group stays unchanged. In the other listed test files delete or update only assertions that name a retired row, its function, its reads or its message; never weaken an assertion about a surviving row. Create tests/unit/test-check-state-retired.py (plain script, ok/FAIL lines, exit 1 on FAIL): imports check_state.table from the bin directory and asserts per number that each of the eleven is a RETIRED key and names no INVARIANTS row, that INV-7 and INV-40 are still rows, and that no row's reads names notes/, runs/ or handoff paths. Create tests/integration/test-check-state-local-files.py, reusing the fixture helper the existing check-state integration tests use: one feature at station review with a signed BRIEF, an approved plan.yaml and a feature.json recording an eng run and a validator-squad validate run at PASS, cycles_used 0 and a pinned review_sha, and no notes/, runs/ or observations/ directory; check-state.py --feature <it> exits 0 with no line starting VIOLATION; check-state.py --list shows each of the eleven numbers as retired; positive control - the same fixture with cycles_used -1 prints an INV-7 VIOLATION for that feature.

      Expected red before the work: at e2bffca0 the fixture prints INV-17 and INV-15 VIOLATION lines (no handoff notes, no digests), and test-check-state-retired.py fails; keep that output for qa. tests/integration/canonical-reader-classification.json and integration-durations.json are T-09's, not this task's.
  - id: T-03
    title: Add the working-file routine, the clean verb, and the worktree-removal gate
    traces: [SC-08, SC-09]
    change_type: cross_module
    execution_mode: main-session-direct
    execution_reason: DEC-174 - feature-worktree.py remove is a refusing gate the post-merge hook calls; the routine is shared by gh-sync and merge-gate.
    depends_on: []
    status: ready
    files:
      - {path: .claude/skills/harness/bin/working_files.py, create: true}
      - .claude/skills/harness/bin/feature-worktree.py
      - tests/integration/test-feature-worktree.py
      - {path: tests/unit/test-working-files.py, create: true}
    verify: |
      set -e
      cd "$(git rev-parse --show-toplevel)"
      env -u HARNESS_AGENT_TYPE python3 tests/unit/test-working-files.py
      env -u HARNESS_AGENT_TYPE python3 tests/integration/test-feature-worktree.py
      env -u HARNESS_AGENT_TYPE python3 .claude/skills/harness/bin/feature-worktree.py clean --help
    intent: |
      Product checkout: the Harness repository itself, worktree /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2641-local-working-files, branch feat/FEAT-2641-local-working-files, base e2bffca0; every edit stays inside it. docs/spec.md, docs/decisions.md and docs/architecture.md do not exist here; the governing record is .harness/harness/docs/DECISIONS.md - read DEC-193, DEC-238, DEC-252, DEC-257 and this plan's D-05, D-06 and D-08. Run Python as env -u HARNESS_AGENT_TYPE python3.

      1. Create bin/working_files.py, the one owner of a feature's local working files (D-05). Contents:
      WORKING_DIRS = ("notes", "runs", "observations").
      class WorkingFilesError(Exception).
      PROJECT_NOTE_RE = re.compile(r"^\.harness/notes/(?!\.\.?$)[^/]+$").
      feature_directory(root, feature): the one directory .harness/<segment>/features/<feature> under realpath(root), segment being any directory under .harness/; exactly one existing, non-symlinked match or WorkingFilesError naming the count (the same rule expertise-merge.py feature_directory applies today; T-06 makes that one call this).
      project_notes(feature_dir): the feature.json project_notes list read with feature_record.read.load_feature_json; absent key or absent feature.json gives []; any entry that is not a string matching PROJECT_NOTE_RE raises WorkingFilesError naming it.
      targets(feature_dir, owner_root): absolute paths in this order, only those for which os.path.lexists is true - feature_dir/notes, feature_dir/runs, feature_dir/observations, then owner_root joined with each project note in list order.
      clean(feature_dir, owner_root, dry_run=False, emit=print): for each target emit "would remove <path>" or "removed <path>"; a symlink is os.unlink-ed and never followed, a directory is shutil.rmtree-d, a file os.unlink-ed; returns the list of removed paths; an OSError propagates after earlier removals, with every earlier removal already emitted.
      untracked(checkout, feature_rel): the paths git -C checkout ls-files -z --others -- <feature_rel>/notes <feature_rel>/runs <feature_rel>/observations prints (no --exclude-standard, so ignored files are included; tracked files are not); a failed git raises WorkingFilesError.

      2. bin/feature-worktree.py.
      (a) remove: after GATE 2 and before GATE 3, for the worktree that holds artifacts (segment is not None) add GATE 2b: resolve the feature directory as GATE 3 does (_artifact_id), call working_files.untracked(dest, artifact_rel); when non-empty print "WOULD DISCARD WORKING FILE <rel>" per path, then "working files remain for <id>: distill (merge-gate.py merge-distill removes them after merging) or run feature-worktree.py clean --repo <repo> --id <id> --yes at a terminal station", and exit 4. No worktree is removed when any gate of any worktree refuses (cmd_remove's existing order). Tracked files never trigger GATE 2b; GATE 3 still grades them.
      (b) new subcommand clean --repo <repo> --id <id> [--yes]. Feature directory: the artifact-holding worktree's when that worktree exists, else the owner root's (the same targets() resolution remove uses). Owner root for project notes: harness_boundary.resolve_root(). Station: check_state.ctx.lenient_station(feature_dir) (DEC-252's one-line reader; import it, never re-implement). A station other than done, abandoned or rejected prints "REFUSED clean: <id> is at station <s>; working files are cleaned only at a terminal station" and exits 7, removing nothing. Without --yes it prints each target as "WOULD REMOVE <path>" and "re-run with --yes to remove them" and exits 0. With --yes it runs working_files.clean and prints "REMOVED <path>" per path; an OSError prints the error and what was already removed and exits 1. No targets prints "nothing to clean for <id>" and exits 0. Add clean to the module docstring's subcommand list.

      3. tests/integration/test-feature-worktree.py: new cases on the existing fixture, whose worktree .gitignore carries the four rules .harness/*/features/*/notes/, runs/, observations/ and .harness/notes/: remove refuses with exit 4, lists notes/x.md, runs/r/digest.md and observations/a.md and leaves the worktree when those ignored files exist; a committed notes file alone does not trigger GATE 2b; remove succeeds after clean --yes; clean at station building exits 7 and removes nothing; clean without --yes lists and removes nothing; clean --yes at done removes the three directories and a project note listed in feature.json project_notes under the owner's .harness/notes/, and leaves an unlisted note there.
      4. Create tests/unit/test-working-files.py (plain script, ok/FAIL lines, exit 1 on FAIL): project_notes rejects "/abs.md", ".harness/notes/../x.md", ".harness/notes/a/b.md", "notes/x.md", ".harness/notes/.." and a non-string; targets order and lexists filtering; dry_run removes nothing; a notes symlink pointing at a directory outside the feature is unlinked and that directory's file survives; feature_directory with zero or two matches raises.

      Expected red before the work: clean --help exits 2 (unknown subcommand) and the new cases fail at e2bffca0. Do not touch tests/integration/test-post-merge-sweep.py or test-hooks-install.py; T-05 owns them.
  - id: T-04
    title: Record owned project notes in feature.json and delete the dead evidence readers
    traces: [SC-11, SC-13]
    change_type: cross_module
    execution_mode: main-session-direct
    execution_reason: DEC-174 - feature-record.py and the feature.json schema are enforcement surfaces the gates import; the schema path resolves to NOBODY (DEC-179).
    depends_on: [T-02]
    status: ready
    files:
      - .claude/skills/harness/bin/feature-record.py
      - .claude/skills/harness/bin/feature_record/budget.py
      - .claude/skills/harness/bin/feature_record/evidence.py
      - .claude/skills/harness/schemas/feature.json
      - tests/unit/test-feature-record.py
      - tests/integration/test-validate-feature-json.py
    verify: |
      set -e
      cd "$(git rev-parse --show-toplevel)"
      env -u HARNESS_AGENT_TYPE python3 tests/unit/test-feature-record.py
      env -u HARNESS_AGENT_TYPE python3 tests/integration/test-validate-feature-json.py
      env -u HARNESS_AGENT_TYPE python3 .claude/skills/harness/bin/feature-record.py project-note --help
      if grep -rn "run_evidence_problems" .claude/skills/harness/bin tests; then exit 1; fi
    intent: |
      Product checkout: the Harness repository itself, worktree /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2641-local-working-files, branch feat/FEAT-2641-local-working-files, base e2bffca0; every edit stays inside it. docs/spec.md, docs/decisions.md and docs/architecture.md do not exist here; the governing record is .harness/harness/docs/DECISIONS.md - read DEC-150, DEC-191, DEC-259 and this plan's D-03 and D-06. Run Python as env -u HARNESS_AGENT_TYPE python3.

      1. schemas/feature.json: add top-level property project_notes - type array, uniqueItems true, items type string with pattern ^\.harness/notes/(?!\.\.?$)[^/]+$ - with a description saying these are the .harness/notes/ paths this feature claims, written only by feature-record.py project-note, and that the working-file cleanup deletes only these (DEC-260). additionalProperties stays false.
      2. feature_record/budget.py: add cmd_project_note(args). A --path not matching that pattern prints "project-note: --path must be .harness/notes/<name>, got <path>" to stderr and exits 2 without touching the file. Otherwise it writes through the same locked, schema-checked write path set-mission uses, appending the path to project_notes (creating the list) only when absent, and prints "ADDED project_notes <path>" or "PRESENT project_notes <path>"; a repeat call leaves the file bytes unchanged. Extend the module docstring's verb list.
      3. feature-record.py: register subcommand project-note (help "record a .harness/notes/ path this feature owns") with the shared --file option and --path (required), set_defaults(func=cmd_project_note) imported from feature_record.budget; the entry stays a thin parser per DEC-259.
      4. feature_record/evidence.py: delete run_evidence_problems, _check_cycle_evidence, _check_refusal and _verify_lead_cycle_evidence, which T-02 left without a caller, plus any helper left with no caller in bin/ or tests/; keep resolve_evidence_ref, verify_evidence_ref, verify_historical_cycle_count and verify_run_digest_owner, which feature_record/runs.py calls at write time (D-03 keeps those checks).
      5. tests/unit/test-feature-record.py: add project-note cases - adds the path; a second call leaves the bytes identical and prints PRESENT; each of "/abs.md", ".harness/notes/../x.md", ".harness/notes/a/b.md", "notes/x.md" and ".harness/notes/.." exits 2 with the file bytes unchanged. Delete only cases that exercise the deleted functions. The methods test_run_start_after_a_handoff_owes_a_succession_and_refuses_without_one and test_run_start_with_succession_reason_lands_run_and_judgement_in_one_write stay byte-identical (SC-13).
      6. tests/integration/test-validate-feature-json.py: a record carrying project_notes [".harness/notes/grilling-x-2026-01-01.md"] validates; one carrying "notes/x.md" is refused naming project_notes.

      Expected red before the work: project-note --help exits 2 at e2bffca0 and the new cases fail; keep that output for qa.
  - id: T-05
    title: Make ship read the ledger, make abandon and reject clean working files, and delete prune-run-evidence
    traces: [SC-05, SC-06, SC-09, SC-14]
    change_type: cross_module
    execution_mode: main-session-direct
    execution_reason: DEC-174 - gh-sync.py ship, abandon and reject are refusing gates over irreversible GitHub writes, and prune-run-evidence.py is a ship gate; their tests and the ship door change with them.
    depends_on: [T-03, T-04]
    status: ready
    files:
      - .claude/skills/harness/bin/gh-sync.py
      - .claude/skills/harness/bin/prune-run-evidence.py
      - tests/unit/test-prune-run-evidence.py
      - tests/unit/test-gh-sync-abandon-sources.py
      - tests/integration/gh_sync_support.py
      - tests/integration/test-gh-sync-ship.py
      - tests/integration/test-gh-sync-abandon.py
      - tests/integration/test-post-merge-sweep.py
      - tests/integration/test-hooks-install.py
      - .omp/commands/harness-ship.md
    verify: |
      set -e
      cd "$(git rev-parse --show-toplevel)"
      for f in tests/unit/test-gh-sync-abandon-sources.py tests/integration/test-gh-sync-ship.py tests/integration/test-gh-sync-abandon.py tests/integration/test-post-merge-sweep.py tests/integration/test-hooks-install.py; do env -u HARNESS_AGENT_TYPE python3 "$f"; done
      test ! -e .claude/skills/harness/bin/prune-run-evidence.py
      test ! -e tests/unit/test-prune-run-evidence.py
      if grep -nE "handoff-validate|_prune_abandoned_runs" .claude/skills/harness/bin/gh-sync.py; then exit 1; fi
      if grep -n "prune-run-evidence" .omp/commands/harness-ship.md; then exit 1; fi
    intent: |
      Product checkout: the Harness repository itself, worktree /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2641-local-working-files, branch feat/FEAT-2641-local-working-files, base e2bffca0; every edit stays inside it. docs/spec.md, docs/decisions.md and docs/architecture.md do not exist here; the governing record is .harness/harness/docs/DECISIONS.md - read DEC-203, DEC-230, DEC-238, DEC-252 and this plan's D-05, D-07 and D-08. Run Python as env -u HARNESS_AGENT_TYPE python3.

      1. gh-sync.py cmd_ship: delete the BUG-1129 block that checks notes/handoff-validate.md. In its place, at the same position (after the worktree refusal, before any GitHub write), load feature.json with record_read.load_feature_json and accept when any runs entry has squad "validator", an id matching re.compile(r"(?:^|-)(?:validate|fix)-") and verdict "PASS" case-insensitively (the predicate prune-run-evidence.py's _is_validate_run used; define it here). Otherwise, unless handoff_policy.exempt_reason(feat_dir)[0] is truthy, die with "validation incomplete: feature.json records no validator validate or fix run at PASS, so ship would record a terminal station for work never validated. No GitHub state was changed. Close the validate run PASS (or, for a plan built entirely main-session-direct, mark every task execution_mode: main-session-direct) and ship again." - exit 1, a refusal, never a skip. Rewrite the comment above it to say why (BUG-1129, DEC-260: ship runs where notes never exist).
      2. cmd_abandon: replace _prune_abandoned_runs (delete it) with working_files.clean(feat_dir, owner_root) where owner_root is feature_corpus.owner_root(feat_dir); it runs in the same place - only when the station reads abandoned, after it is recorded - and the else branch prints "gh-sync: FAILED - working files not removed: the station was not recorded abandoned, so they are kept". Each removed path prints as "gh-sync: removed <path>". The dry run (_report_abandon_dry_run) lists each working_files.targets path as "gh-sync: would remove <path>". Update cmd_abandon's docstring and comments that name runs/ and INV-51.
      3. cmd_reject: the printed list gains one "remove <path>" line per working_files.targets path; under --yes, after _run_reject_steps succeeded and, on the numeric-successor path, after the station is recorded rejected, call working_files.clean with emit printing "gh-sync: removed <path>". A failed step or station write exits 1 as today and removes nothing.
      4. Delete bin/prune-run-evidence.py and tests/unit/test-prune-run-evidence.py. In .omp/commands/harness-ship.md delete the whole bullet that begins "On ship, before the PR - prune run evidence (#1997)" through its closing commit instruction.
      5. Tests. test-gh-sync-ship.py: replace the handoff-validate cases with - a feature with no notes/ directory and a validator validate-c0 run at PASS passes the precondition; one with only a fix-c1-validator PASS passes; one whose validator run is FAIL, or which has only an eng PASS, is refused before any gh call (stub records no call); an all-main-session-direct plan is exempt. test-gh-sync-abandon.py: abandon --yes removes notes/, runs/, observations/ and a project note listed in project_notes under the owner .harness/notes/, leaves an unlisted note; the dry run lists them and removes nothing; a refused station write removes nothing; reject --yes removes them on both the none and the numeric-successor paths and a failed reject step removes nothing. gh_sync_support.py: fixture helpers for these. test-gh-sync-abandon-sources.py: update only references to the deleted prune. test-post-merge-sweep.py and test-hooks-install.py: fixtures that wrote notes/handoff-validate.md to satisfy ship write a validator validate run at PASS into feature.json instead, and the case asserting ship refuses without the note asserts it refuses without the PASS run; add one sweep case - a terminal feature whose worktree holds an ignored notes/x.md is shipped but its worktree survives, and the output carries "WOULD DISCARD WORKING FILE" (SC-09).

      Expected red before the work: at e2bffca0 the no-notes PASS case is refused with "validation incomplete" and abandon leaves notes/ and observations/; keep that output for qa.
  - id: T-06
    title: Read expertise receipts from local disk and clean working files after merge-distill
    traces: [SC-07, SC-10]
    change_type: cross_module
    execution_mode: main-session-direct
    execution_reason: DEC-174 - merge-gate.py and expertise-merge.py are the serialized distill gate and its receipt verifier.
    depends_on: [T-03]
    status: ready
    files:
      - .claude/skills/harness/bin/merge-gate.py
      - .claude/skills/harness/bin/expertise-merge.py
      - tests/integration/test-merge-gate.py
      - tests/integration/test-expertise-merge.py
      - {path: tests/unit/test-expertise-receipt-paths.py, create: true}
    verify: |
      set -e
      cd "$(git rev-parse --show-toplevel)"
      env -u HARNESS_AGENT_TYPE python3 tests/unit/test-expertise-receipt-paths.py
      env -u HARNESS_AGENT_TYPE python3 tests/integration/test-expertise-merge.py
      env -u HARNESS_AGENT_TYPE python3 tests/integration/test-merge-gate.py
      if grep -n "ls-tree" .claude/skills/harness/bin/expertise-merge.py; then exit 1; fi
    intent: |
      Product checkout: the Harness repository itself, worktree /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2641-local-working-files, branch feat/FEAT-2641-local-working-files, base e2bffca0; every edit stays inside it. docs/spec.md, docs/decisions.md and docs/architecture.md do not exist here; the governing record is .harness/harness/docs/DECISIONS.md - read DEC-219, DEC-253 and this plan's D-04 and D-05. Run Python as env -u HARNESS_AGENT_TYPE python3.

      1. expertise-merge.py: replace pr_receipt_paths(real_root, feature_dir, base_sha) with receipt_paths(feature_dir) - every name in feature_dir/notes matching RECEIPT_NAME_RE, sorted, as absolute paths; an absent notes directory gives []. No git call and no base exclusion: receipts are never on any base (D-04). Update load_active and every other caller; base_sha keeps its other uses (replay base blobs, coverage). feature_directory(root, feature) becomes a call to working_files.feature_directory mapping WorkingFilesError to _refuse(9, <its message>). The module docstring's sentence that the receipt travels in the PR says instead that it is a local working file, never committed, removed by the post-merge cleanup (DEC-260).
      2. merge-gate.py merge_distill: after _verified_merge returns, while still holding the lock, resolve the feature directory with working_files.feature_directory(root, feature) and run working_files.clean(feature_dir, feature_corpus.owner_root(root), emit=<collect>); add "cleaned": [removed paths] to the evidence. If clean raises OSError, distill_main prints the evidence JSON with "cleaned" holding what was removed and "cleanup_error" the error text, prints to stderr "merge-distill: MERGED <feature> PR #<n>, but working-file cleanup failed: <error>; run feature-worktree.py clean --repo <repo> --id <feature> --yes", and returns 4 (distill_main returns 0, 3 or the lock refusal code today; if harness_merge's refusal can be 4, use the lowest code no branch returns and name it in the docstring). Any refusal before the merge removes nothing.
      3. tests/integration/test-expertise-merge.py: delete the cases asserting a receipt already on the base is excluded; add - in a fixture whose .gitignore ignores .harness/*/features/*/notes/, two receipts written by member-ops and never committed are both read by replay --check, which reports replayed true.
      4. tests/integration/test-merge-gate.py (its fixture copies the repository .gitignore, which now ignores notes/): a distill whose receipts exist only on disk merges through the stub gh, and the evidence lists cleaned notes/, runs/, observations/ and a project note claimed in feature.json, which no longer exist; an unclaimed .harness/notes/ file survives; a refusal (uncommitted .harness change) leaves every working file in place; a cleanup made to fail (notes/ replaced by a directory the process cannot remove) returns 4 and prints the MERGED message.
      5. Create tests/unit/test-expertise-receipt-paths.py (plain script, ok/FAIL lines, exit 1 on FAIL): loads expertise-merge.py by path, writes two receipt-shaped names and one non-matching name into a temp feature notes directory, asserts receipt_paths returns exactly the two sorted, and [] for an absent notes directory.

      Expected red before the work: at e2bffca0 merge-distill leaves notes/ in place and receipt_paths does not exist; keep that output for qa.
  - id: T-07
    title: Rewrite the instructions that commit working files or name retired gates
    traces: [SC-14, SC-16]
    change_type: docs
    execution_mode: main-session-direct
    execution_reason: The skill, agent and command files resolve to NOBODY (DEC-179) and describe the DEC-174 enforcement change, so they land with it.
    depends_on: [T-03, T-04, T-05, T-06]
    status: ready
    files:
      - .claude/skills/harness/references/distillation.md
      - .claude/skills/harness/references/checkout-upgrade.md
      - .claude/skills/harness/references/build-phase.md
      - .claude/skills/harness/references/ledger.md
      - .claude/skills/harness/references/succession.md
      - .claude/skills/harness/SKILL.md
      - .claude/skills/harness/teams/validate.yaml
      - .claude/skills/harness-uat/SKILL.md
      - .omp/agents/harness-qa.md
      - .omp/agents/harness-visual-designer.md
      - .omp/commands/harness.md
      - .harness/README.md
    verify: |
      set -e
      cd "$(git rev-parse --show-toplevel)"
      F=".claude/skills/harness/references/distillation.md .claude/skills/harness/references/checkout-upgrade.md .claude/skills/harness/references/build-phase.md .claude/skills/harness/references/ledger.md .claude/skills/harness/references/succession.md .claude/skills/harness/SKILL.md .claude/skills/harness/teams/validate.yaml .claude/skills/harness-uat/SKILL.md .omp/agents/harness-qa.md .omp/agents/harness-visual-designer.md .omp/commands/harness.md .harness/README.md"
      if grep -nE "INV-43|INV-15/INV-46|INV-17|DEC-257|prune-run-evidence|track run records|Committed, so what|committed, so what|commits the receipts|committed with the run record|runs/distill-\*/digest.md" $F; then exit 1; fi
      grep -q "feature-record.py project-note" .claude/skills/harness/SKILL.md
      grep -q "feature-worktree.py clean" .omp/commands/harness.md
      grep -q "feature-worktree.py clean" .claude/skills/harness/references/distillation.md
      grep -q "DEC-260" .harness/README.md
      env -u HARNESS_AGENT_TYPE python3 .claude/skills/harness/bin/check-skill-refs.py .
      env -u HARNESS_AGENT_TYPE python3 .claude/skills/harness/bin/check-skill-weight.py .
    intent: |
      Product checkout: the Harness repository itself, worktree /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2641-local-working-files, branch feat/FEAT-2641-local-working-files, base e2bffca0; every edit stays inside it. docs/spec.md, docs/decisions.md and docs/architecture.md do not exist here; the governing record is .harness/harness/docs/DECISIONS.md and this plan's D-01 to D-08. Rule skills carry the rule, one clause of why and a DEC pointer (DEC-158); cite DEC-260 for the new rule. Change only what is listed; keep every other sentence.

      references/distillation.md: in step 3's "Before merge" paragraph, commit and push only the reconstructed Expertise files; the original and replacement receipts and the distill runs' records (runs/distill-*/digest.md, state.yaml, .run-identity.json) are local working files, ignored by .gitignore and never staged (DEC-260); merge-distill replays the worktree's local receipts. Replace the paragraph about an aborted run's untracked records making remove refuse with: feature-worktree.py remove refuses while working files remain, which keeps the worktree alive for distill. Step 4 becomes: observation logs are local working files, read here and never injected; nothing archives them. Add step 5: after it merges, merge-gate.py merge-distill deletes the feature's notes/, runs/, observations/ and the project notes its feature.json project_notes lists, and prints them; exit 4 means merged but cleanup failed - run feature-worktree.py clean --repo <repo> --id <FEAT> --yes; never delete them before the merge, because replay reads the receipts.
      references/checkout-upgrade.md: replace the "Run records checklist (BUG-2399)" bullet with a "Working files checklist (DEC-260)" bullet: pause teams, distill and worktree removal; run merge-gitignore.py <root>; review git diff -- .gitignore; run git rm -r --cached --sparse --ignore-unmatch with the four pathspecs ':(glob).harness/*/features/*/notes/**' ':(glob).harness/*/features/*/runs/**' ':(glob).harness/*/features/*/observations/**' ':(glob).harness/notes/**'; commit .gitignore and the untracking as their own commit; history is not rewritten and files stay on disk. In the following "Re-run the checklist" bullet replace "the BUG-2399 run-UI rule" with "the DEC-260 working-file rules".
      references/build-phase.md, references/ledger.md, references/succession.md: every sentence saying INV-43 grades a late succession says instead that feature-record.py run-start refuses the successor run without its succession; delete ledger.md's sentences about INV-15/INV-46 reading refusal provenance and about harness.json seam_era_start.
      harness/SKILL.md step 1: "runs/ and notes/ are archives" becomes "runs/ and notes/ are local working files"; after the set-mission sentence add: record each .harness/notes/ path your dispatch hands you as made for this feature (the grilling artifact, its facts file) with feature-record.py project-note --file <feature.json> --path <path>; cleanup deletes only those (DEC-260).
      teams/validate.yaml: the comment saying the qa receipt is committed with the run record says it stays in the local run record, never committed (DEC-260).
      harness-uat/SKILL.md: "Committed, so what was accepted and when is on the record." becomes "A local working file, never committed (DEC-260); the ship briefing carries what was accepted and when."
      .omp/agents/harness-qa.md: "Main commits the receipts with the closed run record (tracked files, DEC-257); you do not commit them." becomes "The receipts stay in the local run record (DEC-260); nobody commits them."
      .omp/agents/harness-visual-designer.md: the prototype line becomes "Lives in notes/prototypes/<FEAT>/, a local working file never committed (DEC-260); the plan signature records the approval (DEC-75)."
      .omp/commands/harness.md section 4: the shipped row adds - if the user declines the distill, once the station reads done run feature-worktree.py clean --repo <repo> --id <flow-id> --yes, which removes the feature's local working files and lets the post-merge sweep remove the worktree; the abandon row adds that --yes also removes the feature's working files after recording the station.
      .harness/README.md: the notes row says project notes are local working files; the "Committed, except run UI" paragraph says everything is committed except each feature's notes/, runs/ and observations/ and the project .harness/notes/, which are git-ignored local working files removed at distill or by abandon, reject or clean (DEC-260).
  - id: T-08
    title: Record DEC-260, strike DEC-257, amend the affected decisions, regenerate the index
    traces: [SC-15]
    change_type: docs
    execution_mode: main-session-direct
    execution_reason: The decision record describes the DEC-174 enforcement change and lands with it, as in FEAT-2557 and FEAT-2581.
    depends_on: [T-01, T-02, T-03, T-04, T-05, T-06, T-07]
    status: ready
    files:
      - .harness/harness/docs/DECISIONS.md
      - .harness/harness/docs/DECISIONS-INDEX.md
    verify: |
      set -e
      cd "$(git rev-parse --show-toplevel)"
      env -u HARNESS_AGENT_TYPE python3 .claude/skills/harness/bin/gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md
      env -u HARNESS_AGENT_TYPE python3 .claude/skills/harness/bin/check-decision-anchors.py
      env -u HARNESS_AGENT_TYPE python3 - <<'PY'
      import re, yaml
      t = open(".harness/harness/docs/DECISIONS.md").read()
      p = yaml.safe_load(open(".harness/harness/features/FEAT-2641-local-working-files/plan.yaml"))
      def sec(d):
          m = re.search(r"^## " + d + r" .*?(?=^## DEC-|\Z)", t, re.S | re.M)
          return m.group(0) if m else ""
      assert sec("DEC-260"), "DEC-260 missing"
      assert "DEC-260" in sec("DEC-257") and "struck" in sec("DEC-257").lower(), "DEC-257 strike record"
      bad = [(r["dec"], r["clause"][:60]) for r in p["decisions_affected"] if r["disposition"] != "keep" and r["clause"] in sec(r["dec"])]
      bad += [(r["dec"], "keep clause gone") for r in p["decisions_affected"] if r["disposition"] == "keep" and r["clause"] not in sec(r["dec"])]
      assert not bad, bad
      print("decision landing ok")
      PY
    intent: |
      Product checkout: the Harness repository itself, worktree /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2641-local-working-files, branch feat/FEAT-2641-local-working-files, base e2bffca0; every edit stays inside it. docs/spec.md, docs/decisions.md and docs/architecture.md do not exist here; this task edits .harness/harness/docs/DECISIONS.md itself. Read DEC-188 and DEC-205 first (strike flat contradictions with a strike record; amend in place as current truth; no amendment notes; numbers never reused) and DEC-86 for the strike-record shape.

      1. Append DEC-260 (if main has gained DEC-260 by build time, use the next free number and record that change against this task's verify and the D-NN dec fields before landing). Title: Feature working files are local: notes, runs and observations are never committed. Body, current truth, in the entry style of DEC-257: Chose - D-01 to D-08 of FEAT-2641's plan.yaml, each as one paragraph (the four ignored classes and the guard test; the eleven retired check-state rows and INV-40 (c), INV-7 kept as arithmetic; no committed home, write-time evidence checks kept as provenance; receipts local and replayed by merge-distill, distill identity in feature.json runs; the working_files.py routine and its four callers; feature.json project_notes and feature-record.py project-note; ship's ledger precondition; feature-worktree.py remove's working-file gate), plus D-09's seam_era_start note. Over - committing working files, rewriting history, receipts in a tracked path, local-only check-state rows, deleting ship's precondition. Because - main gained 5,376 objects from 2026-10-08 to a55453f38d, about half notes and runs, Kaya prototype PNGs 12 MiB; deleting later never shrinks history; the operator ruled notes exist only for distill and expertise. Tradeoff accepted - answers, rulings, receipts, UAT results and validate run records are not retained after cleanup; pulling the merged main deletes the untracked copies from every checkout's disk (each stays readable through git show at an older sha); an in-flight branch still tracking its working files must untrack them before merging; a shipped feature's worktree stays until distill or clean runs. Record - FEAT-2641, #2641; strikes DEC-257; amends the DECs this plan's decisions_affected lists as amend.
      2. DEC-257: replace its body with a strike record per DEC-188 - one paragraph: struck under DEC-188 because run records are now local working files, never tracked; DEC-260 is the named successor; its merge-distill and remove consequences are restated in DEC-260. Keep its heading line.
      3. For every amend row in plan.yaml decisions_affected, replace the quoted clause in that entry with text stating the current truth its reason names: DEC-238 (abandon prune becomes the shared cleanup; ship keeps no run evidence and prune-run-evidence.py is deleted), DEC-44, DEC-130, DEC-131, DEC-154, DEC-156 (both bullets), DEC-157, DEC-159 (INV-17 sentence and clause 2), DEC-160 (item 3 and the duplicated-whitelist sentence), DEC-203, DEC-208, DEC-215, DEC-230 (both clauses), DEC-237, DEC-252 (both clauses), DEC-253 (both clauses), DEC-255. The quoted clause text must not survive in its entry; keep clauses must survive untouched.
      4. Regenerate the index with gen-decisions-index.py, then hand-write the ruling after ' :: ' for DEC-260 (at most 30 words) and rewrite the rulings of DEC-257 (struck, successor DEC-260), DEC-215, DEC-238, DEC-252 and DEC-253 wherever their current ruling text names a retired invariant or committed receipts or run records (the ' :: ' tail is hand-written; regeneration alone never changes it). Re-run gen-decisions-index.py --stdout and diff until identical.
  - id: T-09
    title: Reconcile the reader and duration registries and run the cumulative gates
    traces: [SC-12, SC-13, SC-14]
    change_type: config
    execution_mode: main-session-direct
    execution_reason: DEC-174 - the canonical-reader classification and shard durations are read by the CI route and shard gates; the terminal cumulative checks run after every code task.
    depends_on: [T-01, T-02, T-03, T-04, T-05, T-06, T-07, T-08]
    status: ready
    files:
      - tests/integration/canonical-reader-classification.json
      - tests/integration/integration-durations.json
    verify: |
      set -e
      cd "$(git rev-parse --show-toplevel)"
      env -u HARNESS_AGENT_TYPE python3 .claude/skills/harness/bin/check-plan-routes.py --canonical-reader-audit
      for f in tests/integration/test-run-unit-tests-shards.py tests/integration/test-run-unit-tests-layout.py tests/integration/test-check-domain-post.py tests/integration/test-check-domain-approval.py tests/integration/test-validate-digest-shadows.py tests/unit/test-handoff-done-when.py tests/unit/test-working-files-untracked.py; do env -u HARNESS_AGENT_TYPE python3 "$f"; done
      git diff --quiet e2bffca0 -- tests/integration/test-check-domain-post.py tests/integration/test-check-domain-approval.py tests/integration/test-validate-digest-shadows.py tests/unit/test-handoff-done-when.py
      if grep -rn --include=*.py --include=*.md --include=*.yml --include=*.yaml --include=*.ts "prune-run-evidence" .claude .omp .github tests; then exit 1; fi
    intent: |
      Product checkout: the Harness repository itself, worktree /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2641-local-working-files, branch feat/FEAT-2641-local-working-files; every edit stays inside it. docs/spec.md, docs/decisions.md and docs/architecture.md do not exist here; the governing record is .harness/harness/docs/DECISIONS.md (DEC-183, DEC-211, DEC-213). Rebase onto current main first if it has moved; both registries change on main independently (0b5aa6e4 touched the classification).

      1. tests/integration/canonical-reader-classification.json: run env -u HARNESS_AGENT_TYPE python3 .claude/skills/harness/bin/check-plan-routes.py --canonical-reader-audit; delete every row whose file or call site T-02 to T-06 removed (check_state/seams.py, check_state/run_state.py, the deleted check_state/feature_record.py and plan.py functions, prune-run-evidence.py, gh-sync.py's handoff check and _prune_abandoned_runs, expertise-merge.py's ls-tree exclusion, the deleted feature_record/evidence.py functions); add a row for every new reader site the audit reports (bin/working_files.py, gh-sync.py's ledger precondition, feature-worktree.py clean's station read, feature-record.py project-note) classified with the category and remedy canonical_reader_audit.py defines for that call. Re-run until it exits 0 with no unresolved site.
      2. tests/integration/integration-durations.json: delete the entries for tests/integration/test-check-state-handoff.py and test-check-state-inv51.py; add tests/integration/test-check-state-local-files.py with its duration measured by one run, in the existing field shape; keep every other entry.
      3. Run the verify. SC-12 and SC-13 rest on the four named test files staying byte-identical to e2bffca0 and passing; if any of them changed, stop and report it, never edit it here.
