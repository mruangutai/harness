# Research — plan_merge two-file amendment atomicity (FEAT-2488)

Observed at 2491336e43310cb3e95ae3110d098726ed4dc454 (worktree HEAD, BRIEF pending). Authority: the grilling
artifact `.harness/notes/grilling-plan-merge-atomicity-e-2026-11-23.md` and the fact base
`.harness/notes/facts-plan-merge-store-e-2026-11-23.md`; this note records only what the plan adds to them.

## Findings that shaped the plan

- **The grill's zero-hit predicate misses one file.** `plan_merge/approval.py#_write_brief_signature` carries its
  own `tempfile.mkstemp` + `os.replace` for the signed BRIEF. Deleting `guards._replace_bytes`/`_restore_plan` alone
  leaves `mkstemp|os.replace` hits under `plan_merge/`. The plan moves that write onto a public
  `harness_merge.replace_bytes` (no transactionality change; sign-approval's preliminary writes stay a non-goal).
- **A re-run refuses before it reaches any lock.** `record-amendments` and `amend` both run a preflight
  (`_record_amendments_preflight`, `_amend_preflight`) that reads the plan before any `harness_merge` call. Recovery
  only inside `locked_update` would therefore leave a torn state in place on the most natural "next invocation" (the
  operator re-running the verb). Plan: every plan-merge verb except the read-only `check` recovers right after
  destination resolution (`guards._resolve_plan`).
- **A feature.json-only writer can move the ledger between crash and recovery** (gh-sync, factory, rework write — all
  through `feature_json_write.write_feature_json` → `harness_merge.locked_update`, none holding the plan lock). A
  byte-image roll-forward keyed on recorded hashes would then find feature.json in neither state. Plan: every
  `locked_update` recovers a journal in its directory before writing, so no sanctioned writer can move a member
  first; a member matching neither state (an editor or git write) refuses loudly with the journal kept (D-02).
- **The ledger write must keep feature.json's schema non-regression check.** `feature_json_write.write_feature_json`
  wraps the caller's transform with that check internally; the plan exposes the wrapped transform
  (`schema_checked_transform`) so the pair primitive can carry it without `harness_merge` importing a consumer.
- **The required CI canonical-reader audit inventories `harness_merge.py`** (`tests/integration/canonical-reader-classification.json`
  `scanned_files`). The journal's `json.loads` is a new reader site and needs one exempt `module_internal_format` row;
  `check-plan-routes.py` itself is not edited. Classified `plan_merge/amend.py` symbols (`_load_structured_value`,
  `_ledgered_target`, `cmd_amend.transform`) must keep their names.
- **Lock order today:** `approval.py`'s rework write takes `feature.json.lock` before, never while, holding the plan
  lock; `sign-approval`'s `signed_task_hashes` write takes it inside the plan transform (plan → feature.json). The pair
  primitive takes the same order; nothing acquires them reversed.
- **fsync.** `harness_merge.locked_update` performs no fsync (`harness_merge.py#locked_update`); the claim lives only in
  `feature_json_write.py`'s module docstring ("the fsync, and the os.replace"). fsync matters only for OS crash or
  power loss — a SIGKILL leaves the page cache intact — so the journal is fsync'd (file, then its directory after the
  rename, so the journal entry is durable before the first member rename) and ordinary writes stay as they are.
- **Exit code.** A refused journal (unreadable, or a member in neither recorded state) uses exit 5, whose contract in
  `plan-merge.py`'s docstring already covers "a side failed to parse or failed its shape check"; the docstring gains that
  clause.
- **Baseline counts for SC-05** at 2491336e: `case_1985_amend_restores_the_plan_when_the_ledger_fails` 1 check,
  `case_b1716_record_amendments_is_all_or_nothing` 4, `case_b1716_record_amendments_restores_the_plan_on_a_ledger_io_error` 3 — 8 in all.

## Choices left as digest notes (fail the D-NN bar)

- INV-40's message is not changed to name a pending journal: check-state is a gate (DEC-174) and convergence
  happens on the next write, so the message gains nothing durable.
- Journal format is JSON with base64 member images; one journal per primary, named `<primary>.harness-merge.journal`
  (superseded the c0 draft's one-per-directory `.harness-merge.journal` at panel c1, PF-dbbfd79d).

## Panel c1 dispositions (run r-20261123-1-plan-product)

Every finding is `resolved` on `panel:`; this is the rationale the finding shape cannot carry.

- **PF-dbbfd79d (high, substance, T-01) — applied.** The journal is now named for its primary
  (`plan.yaml.harness-merge.journal`) and read only under that primary's lock, which every writer of it holds
  for its whole life, so the generation read is the current one and cannot change or vanish before release.
  The single-primary rule is structural (the name), not a docstring. T-01 pins the J1→J2, fresh-J2 and
  disappearance interleavings through a test-side `acquire` wrapper that mutates disk before the real lock —
  deterministic, no sleeps, no threads, no production hook.
- **PF-750aa466 (high, substance, T-02; core half in T-01) — applied.** `locked_pair_update` raises
  `JournalPending` for any failure after the journal's rename and lets earlier failures propagate unchanged, so
  `write_plan_and_ledger` reports from the exception type, never from the disk. Post-commit feedback is caught,
  noted on stderr best-effort, and the verb still prints its receipts and exits 0 (T-02 cases h and i; SC-01).
- **PF-c21a7b32 (high, substance, T-02) — applied.** T-02's verify now runs the observations, expertise and
  inflight-registry suites too: every SC-07 suite at the terminal task.
- **PF-0b1c6afc (med, substance, T-02) — applied.** Case (e) increments `cycles_used` 0→1 (a required integer,
  schema-valid) and asserts it; fixtures check `_sign` exits 0 first.
- **PF-4cdc0885 (low, form) — applied in place.** `decisions_affected` gains DEC-230 `keep` on the INV-40
  signed-hash clause (verbatim line). `resolved_by: T-02`, the task whose ledger write the clause grades.
- **PF-70a14133 (low, proportionality, T-02) — declined with evidence; hook kept.** The premise ("every SC-01
  outcome lands identically without the preflight call") is false for the plan-at-after torn state:
  `cmd_record_amendments` runs `_record_amendments_preflight` → `amendments.py#_amendment_against_plan`, which
  raises exit 6 ("recorded before") lock-free before `_record_amendments_locked`; `cmd_amend` runs
  `amend.py#_amend_preflight` → `_amend_preconditions`, which `_die(6)`s on the stale hash before any
  `harness_merge` call. Without `_resolve_plan`'s recovery the re-run exits 6 and the ledger stays without its
  judgement. T-02 case (a) now runs both verbs from that state, so the hook is red-proven, not asserted.
- **PF-4e796612 (low, proportionality, SC-03 / T-01) — trimmed.** SC-03 becomes `verify: inspection` of
  `harness_merge.py#locked_pair_update` (the grilling's "test or code anchor cited"); the call-recording test is
  gone from T-01. The gap is named in BRIEF `## Verification gaps`.
- **PF-e44c490d (info, proportionality, D-02 / T-01) — applied.** Recovery runs only for journals naming the file
  being written; a pending or diverged journal blocks only its members' writers. An unreadable journal still fails
  closed for its directory (it cannot say which files it names). The premise was overstated here — observations
  and notes live in subdirectories, not beside plan.yaml — but the narrowing costs nothing.
- **PF-397af347 (info, proportionality, T-02) — trimmed.** The base-worktree six-suite baseline and its receipt
  file are removed from T-02 and SC-07; unedited assertions passing at the pin carry "as before". The red
  torn-state run and SC-04's stdout baseline stay.

All task-changing `plan-merge.py` calls this run printed no `APPROVAL-RESET:` receipt, so there was no gh-sync call.

## Panel c2 dispositions (run r-20261123-1-plan-product, cycle 2)

All three new findings are `resolved` on `panel:`; the nine c1 findings stay present and resolved after
`record-panel --cycle 2` (12 findings, none open). Each repair is stated as an acceptance behaviour the implementer
must prove with a named test case; the scope reader's loop is spent, so these go to the operator unread.

- **PF-cc9533d1 (high, substance, T-01/T-02) — applied; `resolved_by: T-02`** (the task whose diagnostics the
  finding grades; the core half is in T-01). Behaviour now pinned: a replay that fails after it starts writing is
  committed-pending, never a traceback and never "nothing was written". T-01 §3 widens `JournalPending` with
  `replay`; §6 raises it for any failure of a member `replace_bytes` or the journal unlink, journal kept. The
  "completed replay with a cleanup error" class is removed rather than classified: §6 drops the post-unlink
  directory fsync, matching the pair's own unlink (Delete First); a crash-resurrected journal names members already
  at after and replays as a no-op, or refuses DIVERGED — fail closed. T-02 §2 gives the replay case its own truthful
  lines ("this command did not write its change; ... stays pending"); §3 makes `_resolve_plan` print them and exit 2,
  and any other recovery Exception (necessarily before a member write) exit 2 with "no file was changed" — no
  Traceback. Proven by T-01's new replay-failure unit case and T-02 case (j) (preflight and pair paths, then
  convergence on re-run). SC-01's existing clause "a ledger write that fails after the journal is published is
  reported as journaled ..., never as nothing was written" already covers a replay's ledger write; BRIEF unchanged.
- **PF-484f97f2 (high, substance, T-02) — applied; `resolved_by: T-02`.** Confirmed at
  2491336e: base `harness_merge.py` has no `replace_bytes`; `locked_update` renames with module `os.replace(tmp_path,
  path)`. Case (i) now wraps `os.replace` filtered on the feature.json destination — one seam present in both trees —
  and must first check the wrapper raised before grading the message. The red-run sentence requires (i) at the base to
  fail on its outcome checks after the reached-the-seam check passed, so the base run records the old "restored"
  diagnostic differing (SC-01's "both failure reports differing").
- **PF-ebc96c4b (med, substance, T-01) — applied; `resolved_by: T-01`.** `_journals_naming` is declared a hint;
  `_recover_journal(journal_path, path, timeout)` re-checks under the primary's lock that the current generation still
  names `path`, returning False and writing nothing otherwise. `_read_journal` refuses duplicate member names as
  JOURNAL UNREADABLE, so a P,P record refuses at exit 5 instead of timing out LOCKED. D-02's text is reconciled ("lock-free
  discovery is only a hint ... acted on only as re-read, membership included, under its primary's lock"). Proven by
  interleaving case (iv) (J1 for P,X replaced by J2 for P,Y: `recover_journals(X)` false, nothing changes) and the
  duplicate-member unit case.

Edits: `amend` on T-01.intent, T-02.intent and D-02.choice; no files, verify, traces or task-set change. None printed
an `APPROVAL-RESET:` receipt, so there was no gh-sync call. `plan-merge.py check`: 2 tasks, 13 anchors, 0 failures.
