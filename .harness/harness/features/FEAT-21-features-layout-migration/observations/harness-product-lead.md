# Observations — harness-product-lead — FEAT-21-features-layout-migration

- 2026-08-14: Stop-hook deadlock while hosting `plan-feature`. I dispatched s2 (eng-lead) and s3
  (visual-designer) with `run_in_background: true`, then tried to yield the turn to await their
  completion notifications. `validate-digest.py --hook` rejected the stop with the full team-digest
  field list, because a lead cannot stop without a terminal digest. But the run was `status: running`
  with two steps provably in flight (`dispatched_at` set, `completed_at` none), so any digest I could
  have emitted would have asserted a terminal state that was false. Net: a lead with backgrounded
  members in flight has no legal way to yield. Workaround used — keep the turn alive with
  non-colliding reads and durable writes. Raised as an `open_question` to the harness owner rather
  than absorbed; the real fix is either foregrounded dispatch for steps the next action depends on,
  or a hook that recognises in-flight steps.

- 2026-08-14: The dispatch I was handed asserted "`layout_fixtures.py` STUB texts co-change in the
  same commit". pm returned the opposite — no edit needed — and pm was right.
  `layout_fixtures.py:68` compares `set(STUB)` to `{r.path for r in READER_TABLE}`: the import-time
  guard fires on KEY drift, i.e. a reader row added, removed or renamed. The STUB values are
  synthetic fragments (`.harness/repoA/features/...`), not copies of the real scripts, and the
  migrated variants already carry a segment. FEAT-21 adds and removes no row, so the guard stays
  quiet. The constraint's own parenthetical ("its import-time guard reddens loudly if keys drift")
  actually supports pm's conclusion — the operator constraint contradicted itself, and reading the
  guard settled it in one grep.

- 2026-08-14: Two LEAVE-list items in my dispatch were wrong on the merits, and pm caught both.
  `branch-create-gate.sh:77` runs `ls -d "$root/.harness/features/${flow}"*` and line 78 DENIES when
  nothing matches — post-move, no branch is creatable for any feature. `.gitignore:7` is
  `.harness/features/*/runs/**` and its own comment names the consequence ("run dirs dirty the
  working tree and the dirty-tree halt (SPEC 8.6) deadlocks the next crew"). Both were on the
  detector's DO-NOT-READ list as unit-9-lands-anytime, which is true of the DETECTOR but false of the
  TREE: the detector not reading a file says nothing about whether that file hard-breaks. I verified
  both at source before relaying rather than passing the override up unexamined.

- 2026-08-14: pm's T-02 intent named "the orchestrator domain's bare `.harness/features/**` entry" as
  an easy-to-miss site. Opened it — `team-config.yaml:28`, exactly as described, comment
  "its feature's STATE.md, feature.json, runs/". A cited pointer that survived being opened.

- 2026-08-14: `feature.json` and `STATE.md` are absent from a freshly planned feature dir and that is
  CORRECT, not a gap in pm's work — `team-config.yaml:28` grants `.harness/features/**` to the
  orchestrator, which creates them at dispatch. pm owns only BRIEF.md, plan.yaml and notes/. Worth
  remembering before flagging a "missing" feature record at plan time.
