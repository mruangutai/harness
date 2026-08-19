# Observations — harness-orchestrator — FEAT-27-expertise-repository-tier

- 2026-08-19: Pre-change baseline of `inject-expertise.sh`, captured at `253287f` BEFORE T-02 edits
  it, because T-02 changes what the hook DISCOVERS and after that the exit code stops being evidence
  (P-09). Per agent, `context_lines` from `hookSpecificOutput.additionalContext`:
  `harness-qa` 134, `harness-orchestrator` 149, `harness-dev-ops` 35, `harness-frontend-dev` 0,
  `some-other-agent` 0. Exactly one header emitted — `## Your Expertise — this codebase (project
  tier, authoritative on conflict)`. No global tier ($HOME/.harness absent) and no codebase-map block
  (`.harness/codebase/` does not exist in this repo).
  The discriminator this buys: after T-02 and BEFORE T-04, every one of those line counts must be
  UNCHANGED and only the header wording may move, because no repository tier exists on disk yet. A
  count that moves at T-02 means the hook is emitting something it should not.

- 2026-08-19: `harness-frontend-dev` returning 0 lines is the live state T-02's case 10 is written
  against — it holds a craft GRANT in `team-config.yaml` but has no craft file on disk. Confirmed by
  running the hook, not by reading the manifest. 15 craft files, 16 grants.

- 2026-08-19: This feature's plan puts 3 of 6 tasks in the `main-session-direct` lane, so the build
  cannot run as one orchestrator session. The packing that minimises round trips is: run the
  dependency-free TEAM tasks first (T-02, T-03), which unblocks ALL THREE layer-0 tasks at once
  (T-04 needs T-01+T-03, T-06 needs T-03+T-04), so they hand over as a single ordered batch instead
  of three separate relays. Ordering the segments by lane rather than by task number turned 3
  round trips into 2.

- 2026-08-19: The layer-0 handover note deliberately does NOT copy each task's `intent:` and
  `verify:` out of `plan.yaml` — it ships the `yaml.safe_load` extraction command instead. A copy of
  an approved artifact is a copy that can drift from the signature; an extraction command cannot.
  The intents here run to 40+ lines with byte-exact assertion strings in them, so the drift risk was
  not theoretical.

- 2026-08-19: A concurrent session branched this SHARED checkout mid-run, so `git checkout -b` had
  put me on the wrong branch and my signed-artifacts commit landed on a chore branch (#433's
  foreign-pen shape). Repair that worked without disturbing a live subagent: `git stash push --
  <feature-dir>`, checkout the real branch, `git cherry-pick <the commit>`, `git stash pop` — run as
  ONE bash invocation so the window where tracked files are absent from the tree is sub-second. The
  tell to check first: `git diff --name-only <target-branch> HEAD` — if it lists only files no live
  subagent touches, the switch is safe.

- 2026-08-19: Do not verify a branch-repair claim from the reporting agent's summary. The coordinator
  reported the amendment commit was "already on main"; local `main` did not contain it and was one
  commit behind — the content was on `origin/main` under a different sha from a squash merge. The
  conclusion (do not cherry-pick it) was right, the stated reason was checkable and only half true,
  and `git branch -a --contains <sha>` plus `git log origin/main` settled it in one call.
