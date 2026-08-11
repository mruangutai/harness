# Receipt — harness-pm — FEAT-12 revision pass — 2026-08-10-03-product

**Path note:** the dispatch named
`notes/receipt-harness-pm-2026-08-10-03-product.md`. `check-domain.sh` BLOCKED that path for
`harness-pm` (permitted list is `notes/research-*.md`, `notes/uat-*.md`, BRIEF, PLAN, plan.yaml).
Raised as an open question rather than worked around; this file is the same content at a permitted
path.

**All of R-1..R-9, A-1..A-5 and D-06 landed. Nothing was judged wrong.** Two dispatch premises are
stale and one new residue was found; all three are in `open_questions`, none blocking.

Artifacts: `.harness/features/FEAT-12-end-copy-distribution/BRIEF.md` and `plan.yaml`.
Approval blocks untouched — `plan.yaml` `approval.status: pending` / `approved_by: none` /
`date: none`; BRIEF `## Approval` / `status: pending`.

## Working state differs from the dispatch's premise

Dispatch said branch `chore/202-strike-propagation-checker` at `365a8a9`, PR #213 open. Measured:
HEAD is `687fd3e` on `main`; `1e5f55d` is *the merge of PR #213*. I worked at HEAD rather than
checking out `365a8a9` — that would un-land #202 and contradict R-8. Every new measured claim
written into either artifact carries `687fd3e`; claims re-used from the orchestrator's M-1..M-6
carry their own date or `365a8a9`. R-2's two anchors were re-derived at HEAD and are unchanged:
`.harness/team-config.yaml:204-206` and `.claude/skills/harness/templates/team-config.yaml:196-198`,
identical text in both.

## Per item

- **R-1** — `D-01` rewritten: the triple is explicitly *not* one committed set; the working-tree-only
  rule for agents is stated once and referenced where it binds. `T-02` intent item 3 restated from
  M-1. `T-02` verify gained a real presence half — `test -d .claude/agents` plus a recorded
  pre-deletion count file that must be `> 0`. `T-05` commit body no longer names the agent files
  (the commit contains none) and says why its remote verify has no agents clause. BRIEF Problem and
  `SC-04` rewritten.
- **R-1, the honest part** — no post-hoc command can witness 16→0, because all 16 files match
  `harness-*.md` and the directory ends up empty. So `T-02` now *records* the pre-count to
  `notes/kaya-agents-count-before.txt` before deleting, and the verify asserts that file is non-empty
  and `> 0`. A verify claiming to observe the transition would have been the same vacuity inverted.
- **R-2** — `T-11` intent gained enumerated item 5 (the DEC-85 SHARP EDGE block, both files); the
  DEC-85 rationale sentence is kept and only `it owns deploy` and the `and deploy` in
  `merge and deploy stay user-gated` are cut. `T-11` verify gained two absence clauses and three
  presence clauses (`SHARP EDGE (DEC-85)`, `bypasses path checks`, `user-gated`, each = 2 files).
- **R-3** — `T-05`'s Q1 preamble and working-tree branch deleted; the authorization scope
  (`mruangutai/kaya-ai` `master`, deletion commit only, nothing in this repo) is stated first. Q1
  retired into a new `## Settled rulings` section in BRIEF, not deleted.
- **R-4 / A-1 / A-5** — `T-02` encodes the split as an execution-time rule: `git ls-files` decides
  the `git rm -f -r --` set, `rm -rf` takes the remainder. No new count written into the plan.
- **R-5** — `T-03` retitled, enumeration replaced with M-6's full eight across four events, the four
  surviving `.claude/hooks/` scripts and both top-level keys named, and the SC-06/Task-spawn reason
  stated in the intent where the builder reads it. `D-02` restated from M-6.
- **R-6** — all five DEC-161 citations removed, including `T-13` case 4's assertion and `T-14`'s
  `grep -c '^## DEC-161'` line. `D-01` re-derives the authority from `deploy.sh:52-59` and `:264-268`
  and records that `deploy.sh:54`'s own DEC-161 attribution is unfounded. Two non-citing mentions
  survive on purpose (`D-01` explaining that; `T-13` telling the builder not to re-add the
  assertion). T-10/T-11/T-12/T-14's count-equals-zero verifies untouched, per Q4.
- **R-7** — `D-02.because` converted from plain scalar to `>-`. Every scalar re-checked (below).
- **R-8** — `T-10`'s five-item DEC-174 list corrected to four; `D-03.because` now cites DEC-188
  directly; BRIEF's DEC-174 bullet (the whole 140-143 span, list line included) and the
  propagation-checker bullet rewritten; the five `ok-stale` escapes removed with prose that carries
  the same meaning.
- **R-9** — BRIEF's false "untracked" sentence replaced with M-3/M-4's measured reason, and it is
  the same sentence that authorizes `git rm -f`.
- **A-2** — content-preserving check, not a bare parse. Both `#<digits>` tokens in the raw file
  (`#202`, `#206`) survive into the loaded structure with no reduction in count; every
  `because`/`choice`/`intent`/`execution_reason`/`verify` value's loaded tail is present in the raw
  text. Zero folded `verify:` blocks; all 14 retain newlines.
- **A-3** — every `verify:` is still `|`. Only `because`/`choice` prose uses `>-`.
- **A-4** — both extended verifies were run today and both FAIL for the right reason; `T-03`'s was
  additionally run against a simulated post-edit `settings.json` and PASSES (`ok 4 hooks remain`).
- **D-06** — `.claude/settings.json.harness-bak` **deferred, declared**. The discriminating grep:
  `merge-settings.py` has exactly three `harness-bak` hits — `:325` a comment, `:326`
  `shutil.copyfile(path, path + ".harness-bak")`, `:338` a print. **Write-only, never read back.**
  Per the operator's own stated test the deferral is inert. What settled it beyond inertness: no REQ
  covers it (REQ-03 is tooling, REQ-06 is dangling hooks, REQ-07 is this repo) and
  `merge-settings.py:325` says the backup exists because harness edits a file *the project owns and
  harness does not*. Recorded as `D-06` **and** in BRIEF `## Constraints`, with its reversal cost.

## Gate results

- `check-plan-routes.py`: **exit 0**, `0 violation(s) across 7 plan(s)`. FEAT-12's two advisory lines
  are the predicted ones and nothing was restructured to chase them:
  - `DEVIATION T-01 .harness/features/FEAT-12-end-copy-distribution/notes/kaya-harness-manifest-before.txt granted to harness-orchestrator but declared main-session-direct`
  - `DEVIATION T-04 .harness/features/FEAT-12-end-copy-distribution/notes/kaya-harness-manifest-after.txt granted to harness-orchestrator but declared main-session-direct`

  T-02's new note file produced no third deviation.
- `git rm` behaviour, reproduced in a scratch repo (never in kaya): mixed tracked+untracked pathspec
  → exit 128 `fatal: pathspec ... did not match any files`, nothing removed; modified tracked path →
  exit 1 `error: the following file has local modifications`; with `-f` → exit 0; tracked path already
  deleted from disk → `-f -r` exits 0 and stages it.
- kaya `settings.json` re-measured today: 12 registrations, 8 harness, 4 non-harness, all four under
  `.claude/hooks/`; top-level keys exactly `hooks` and `env`. M-6 confirmed.

## New findings routed, not absorbed

1. **kaya's six git worktrees.** `.claude/worktrees/*/` each carry their own
   `.claude/skills/harness*` tree — 56 such directories, untracked and gitignored (which is why they
   are absent from M-3's 63). Outside all three of T-02's globs, so nothing here reaches them, and
   `SC-04` is worded against `.claude/skills/`. But REQ-03's "a session opened directly in `kaya-ai`
   has no harness capability" is broader than what this feature delivers. Declared out of scope in
   BRIEF `## Constraints`; not silently absorbed into T-02.
2. **`deploy.sh:18` — agents go global only (DEC-113).** So kaya's 16 on-disk agent files were never
   put there by a project copy. BRIEF's Problem paragraph now says this; it is the reason the triple
   cannot be treated as one distributed set.
3. **Removing the `ok-stale` escapes is safe.** Checked rather than assumed: BRIEF sits under
   `.harness/features/`, which is on T-13 case 2's exclusion list and outside T-14's verify
   pathspec, so the five verbatim quoted strings cannot redden either sweep.
4. **`git rm` takes `.claude/skills/` with it, and that would have aborted T-05.** Measured:
   `ls -1 kaya/.claude/skills` returns 21 entries, all `harness*`, nothing else. Reproduced in the
   scratch repo: `git rm -f -r` on the last tracked child removes the parent directory from disk,
   and a following `git add -- <that dir>` exits 128 `fatal: pathspec ... did not match any files`.
   Three fixes landed: T-02's verify no longer asserts `test -d .claude/skills` (it would have
   failed on a *correct* execution); T-02's intent states the disappearance is expected; **T-05's
   stage line narrowed to `git add -- .claude/settings.json`**, since T-02's `git rm` already stages
   every tracked deletion and `rm -rf` only ever touches untracked paths. T-05's confirm step keeps
   all three pathspecs, so it still audits the full staged set. `.claude/commands/` survives —
   `review-team.md` is in it.
5. **REQ-03 was falsified by the worktree deferral** — it said "no `harness*` skill directories" with
   no path qualifier, while 56 such directories live under `.claude/worktrees/`. Narrowed to the
   three top-level directories T-02 and SC-04 actually cover, with the deferral named inline. That
   is narrowing to match a declared deferral, not scope widening.
6. **The pre-count file is self-attested by construction** — written and read by the same task. T-02's
   intent now requires it to be the literal output of `ls -1 .claude/agents | wc -l` run before any
   deletion, with the command quoted beside the number in the receipt. That is what makes it evidence
   at goal-check rather than an assertion.
