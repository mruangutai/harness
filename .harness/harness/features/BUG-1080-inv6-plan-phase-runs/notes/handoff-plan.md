# Handoff - BUG-1080, plan -> build - written at 9f2a0702, seq-1

## Next

Fix INV-6 in `check-state.sh` so the plan-phase panel run DEC-207 legalises can be
recorded without reddening the gate. Main-session-direct under DEC-174: this is
gate-script and validator-test code, so it must not run through the enforcement path it
changes. Test-first.

- `.claude/skills/harness/bin/check-state.sh` - the INV-6 predicate
- `.claude/skills/harness/bin/feature-schema.json` - `runs[]` is `additionalProperties: false`
- `.claude/skills/harness/bin/test-check-state.py` - six red-first cases
- `issue://1080` - the filed defect and its measurements

## Trust

- claim - the three rules admit no satisfying value - verified-at 9f2a0702 - source: read
  `check-state.sh` INV-6, `validate-digest.py:891-905`, `DECISIONS.md:6348`.
- claim - recording the panel is what reds the gate - verified-at 9f2a0702 - source:
  FEAT-46's `consolidated-plan-findings-c1.md:84` records exactly one violation at panel
  time; the second appeared when the runs were recorded.
- claim - INV-6 predates DEC-207 - verified-at 9f2a0702 - source: `git log -S` on the
  INV-6 message returns 2026-08-25; DEC-207 shipped 2026-08-31 with FEAT-45.

## Dead ends

- Keying the exemption on `approval.status == pending` - UNVERIFIED as a fix, ruled out by
  reasoning: the plan-phase runs remain in `runs[]` after signature while `review_sha` is
  unpinned until the Building -> Review seam (BUG-1071 `f0a0149`), so it would red the gate
  for the whole build phase. Source: operator ruling, this conversation, 2026-08-31.
- Pinning `review_sha` to silence INV-6 - source: `validate-digest.py:891-905` refuses a
  plan review when it is pinned, and the record would falsely assert a commit was reviewed.
- Widening the `runs` tuple - source: INV-7 (`:441`) and the INV-22 loop (`:509`) unpack
  exactly three elements, so widening breaks two invariants to serve one.

## Working set

- `.claude/skills/harness/bin/check-state.sh`
- `.claude/skills/harness/bin/test-check-state.py`
- `.claude/skills/harness/bin/feature-schema.json`
