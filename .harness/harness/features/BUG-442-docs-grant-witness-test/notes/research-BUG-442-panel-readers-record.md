# Record repair — BUG-442 panel.readers now names the goalcheck reader

**Done, as a 2-line addition and nothing else.** `panel.readers` in
`.harness/harness/features/BUG-442-docs-grant-witness-test/plan.yaml` lists three readers —
`should-not-exist`, `scope`, `goalcheck` — each `status: ran`. INV-32's "reader goalcheck never ran
or was not recorded" line for this feature is gone. No re-grade, no re-plan: `approval`,
`status: review`, `panel.last_run`, `panel.cycle`, every task status and all four
`panel.findings` entries (including `PF-049c59c515c538bc41da6616176f8987`, still
`disposition: open`) reload identical.

## The evidence that goalcheck ran — re-derived, not taken from the dispatch

`notes/research-BUG-442-goalcheck-plan-c0.md`, read in full:

- verbatim question answered **yes** (`:3-6`);
- coverage graded **complete, no unowned clause**, five acceptance clauses each with an owner
  (`:11-19`);
- T-01's four literals verified against the real `.harness/team-config.yaml`, not assumed — census
  16 names with `set()` symmetric difference, `EXPECTED_DOCS_GRANTS`, M1's insertion point, M3's
  non-vacuity (`:23-44`);
- closes `None blocking.` (`:97`).

Nothing in it contradicts `status: ran`. `skipped` would have been the false entry.

## How it was written — the route matters for the next repair

`plan.yaml` has exactly one writer: `plan-merge.py` (check-domain DENIES Edit/Write, FEAT-41
REQ-05). For `panel` the only verb is `set-panel`, which replaces the block with
`yaml.safe_dump({"panel": panel})` — i.e. it re-serializes. That is compatible with a
minimal diff **because every `panel` block on disk was itself produced by that dumper**: dumping
the parsed panel of this plan reproduced lines 31-69 byte-for-byte before the change
(`ROUNDTRIP-IDENTICAL: True`), so appending one reader yields exactly two added lines.
`apply` cannot do this job — `panel` is not a union key, so a differing value exits 7 CONFLICT.

## Verification

- diff: 2 added lines at `panel.readers`, nothing else (reproduced verbatim in the DIGEST).
- loader: `harness_yaml.load_plan` parses; readers `[should-not-exist/ran, scope/ran, goalcheck/ran]`.
- `check-state.sh` **in the worktree**: zero INV-32 VIOLATION lines; the three BUG-442 INV-32
  notes are the unchanged finding dispositions. (Run from the main checkout it reports nothing
  about BUG-442 at all — this plan lives only in the worktree's `.harness`.)
- `git status --porcelain`: ` M …/plan.yaml` unstaged; nothing staged, nothing committed.

## Open questions

- **Q1 (non-blocking, orchestrator's):** the write makes INV-33 fire —
  `review_sha 9b3fde7e… is STALE`. Caused by this edit, not pre-existing: `9b3fde7e` is both the
  pinned `review_sha` (`feature.json` `review_sha`) and the last commit touching `plan.yaml`, so
  the file matched the pin until now. It clears when the record commit lands and `review_sha` is
  re-pinned. Only the record changed; no reviewed text moved.
- **Q2 (pre-existing, not mine):** `status is 'review' but notes/handoff-build.md is missing`
  (DEC-159), and `feature.json` shows as modified in the worktree by another hand.
