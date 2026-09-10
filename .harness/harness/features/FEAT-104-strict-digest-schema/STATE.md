# STATE

## Current

- feature: FEAT-104-strict-digest-schema
- run: 2026-09-09-04-panel-validator — the reviewer panel at pinned `review_sha` 6126ac07
- squad: validator (review team: code, qa, security, ui — all four in one turn)
- status: validate STOPPED at the escalation boundary; the fix is the main session's

**The panel returned ESCALATE, `severity_max: high`, and `gates.review` is
`advisory_unless_high`, so that severity gates.** Panel composition: `code` PASS, `qa` PASS,
`security` FAIL, `ui` PASS (scoped IN and graded, not scoped out). Send-backs inside the run: 0, so
`cycles_used` stays 7/10; the re-panel after the new pin is the cycle-8 rework run. runs 14/20 —
`max_total_runs` is informational and the runs still earn their place: each of the last four
resolved something and none repeated another's measurement.

**F1 (high) is real and now has an EXECUTION witness, which the panel could not obtain.** The
`schema_version` floor in `check-domain.sh:1589-1592` is keyed on file CREATION (`os.path.lexists`),
and the closed step schema at `:1622` gates on `_valid_version` computed from the PROPOSED document
(`:1593-1597`), never the value on disk; `check-state.sh:1486-1489` sweeps on that same
self-declared value. An update write that declares `schema_version: 1` over an already-created
version-2 run is therefore accepted, and the run leaves both enforcement layers permanently and
silently. This falsifies REQ-02's second sentence. The panel had two independent code reads and no
execution, because `bash-write-guard.sh` correctly refuses a read-only reviewer's repro. This
orchestrator closed that gap by measurement: `python3 tests/integration/test-check-domain.py` in the
worktree, case `schema_version floor refuses a version-2 checkpoint downgrade` — **exit 0, the
downgrade is ACCEPTED** where the case expects 2. The eleven sibling cases pass, including the
version-1 update that shares the same `_existing_write` helper, so the call shape is sound and the
witness is not an artifact of the fixture.

**Main owns the remedy and said so.** F1, F2 and F3 all land inside the DEC-174 carve-out
(`check-domain.sh`, `check-state.sh`, `validate-digest.py` and their tests), which no harness team
may edit, so no fix cycle is routable to any lead. Main is fixing F1 directly, is also addressing
F2 and SC-08/F3, and instructed this run to stop at the escalation boundary and return a fix handoff
rather than a goal-check or a briefing. **No goal-check ran. No UAT was generated. No briefing was
written.** All three wait on the new pin.

`tests/integration/test-check-domain.py` is UNCOMMITTED-MODIFIED in the worktree (22:56) — Main's
own test-first red case for F1, confirmed by Main. It is not this run's work, was not touched, and
was not committed; the commit from this run names only this feature's own validation artifacts by
pathspec. The four reviewer notes and the panel run dir are preserved.

**SC-13 is `verify: uat` and applies.** The BRIEF's briefing-time assumption that this feature has
no UAT criterion is false: SC-13 is the DEC-174 operator read of this exact diff, `gates.uat` is
`blocking_when_uat_criteria_exist`, and no harness run can close it. F1 is a concrete thing for that
read to look for. SC-12 is `verify: inspection` and was deliberately not exercised on this run.

`check-state.sh` exits 1 in this worktree on five INV-29 standing-worktree violations, every one of
them another feature's checkout. FEAT-104 itself carries no violation — the INV-26 card/plan
mismatches and the INV-6 unpinned-validator report that stood at the build seam are both cleared by
the station write and the pin.

## Open Questions

- Q1 (blocking, F1, DEC-174 carve-out — main session only): should `check-domain.sh` compare a
  non-creation write's `schema_version` against the on-disk value, or simply refuse any decrease?
  SC-11 and SC-15 deliberately keep version-1 updates writable, so the remedy must refuse a
  DECREASE rather than reinstate the creation floor.
- Q2 (not blocking): order F1 against SIMPLIFY's S2. F1's remedy has to be written into two files
  today because the run-state shape carries two hand-written enforcement layers. If those layers are
  to be consolidated, F1 should be fixed once against the consolidated layer rather than twice and
  merged.
- Q3 (not blocking, F2, med): `check-state.sh:1590` validates every completed lead run's digest
  through the raw persona `lead`, which `validate-digest.py:1407` exempts from the undeclared-key
  check, while `_host` at `:1577` already holds the real persona and is unused. Should the sweep
  pass `_host`, so a key that slipped through the acknowledged `stop_hook_active` one-shot is caught
  at rest?
- Q4 (not blocking, F3, med): SC-08 requires the rejection to name the declaration route by file
  AND symbol as an asserted substring. `validate-digest.py:1414-1421` names the symbols and no
  file, and its test asserts only those symbol tokens, so the by-file half is neither emitted nor
  tested. The step-key message does it correctly. Accept SC-08 under a narrowed reading, or add the
  filename and its assertion?
- Whether the INV-26 card/plan mismatch is a harness defect rather than drift. Unchanged, still
  unanswered, and no longer firing for this feature now that the parent and sub-issues moved to
  `review`.
- `check-domain.sh`'s worktree-claim guard is keyed per persona with no per-session identity, so a
  live claim on another feature refuses this feature's same-persona agent its own writes. Raised by
  the simplify lead; a harness defect, not a finding about this diff.
