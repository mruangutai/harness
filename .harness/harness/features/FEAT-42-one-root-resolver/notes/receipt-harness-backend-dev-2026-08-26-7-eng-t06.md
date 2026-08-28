# Receipt — harness-backend-dev — T-06 — 2026-08-26

Task: single-flight root resolution, TTL, session-scoped expiry, ambiguous-release refusal, and
an absolute remedy, in `.claude/skills/harness/bin/inflight_registry.py` and
`.claude/skills/harness/bin/test-inflight-registry.py`.

## The four mandated RED cases (written before their fix, run, watched fail)

Command: `python3 .claude/skills/harness/bin/test-inflight-registry.py` (pre-fix tree).

```
FAIL - case11: ttl_shorter_than_cycle - CLAIM_TTL_SECONDS is one cycle (1200s), not the old 3600s (3600)
FAIL - case12: foreign_session_expired - a claim from a DIFFERENT session reads as absent though fresh (('raised', 'TypeError("claim() got an unexpected keyword argument \'session\'")'))
FAIL - case12: foreign_session_expired - a session mismatch is not counted as TTL expiry (('raised', 'TypeError("claim() got an unexpected keyword argument \'session\'")'))
FAIL - case12: foreign_session_expired - the entry remains on disk for its OWN session to find
FAIL - case13: release_refuses_ambiguous - two live claims are refused, not oldest-popped, and 0 is returned (True)
FAIL - case13: release_refuses_ambiguous - both claims remain on disk untouched ({'harness-backend-dev': [{'cwd': '/b', 'dispatcher': 'harness-eng-lead', 'started_at': 1787799775.683234}]})
FAIL - case13: release_refuses_ambiguous - stderr says how many were left
FAIL - case14: remedy_is_absolute - release_cmd(root, agent) exists
FAIL - case14: remedy_is_absolute - shape check skipped, release_cmd is absent
```
Full run: 12/68 checks failed (8 above plus 4 assertions inside the same cases whose parent
check also failed, all counted in the total).

## Item 6's literal instruction — the required red proof

Item 6 as literally written (`:258` moved to a single `#628` line with NO split) reds
`test-dispatch-guard.py` case 6, because `dispatch-guard.sh` only ever emits `#628` and
`test-dispatch-guard.py:169-170` still asserts `#551` in stderr. Captured before the citation
was split:

Command: `python3 .claude/skills/harness/bin/test-dispatch-guard.py` (inflight_registry.py
carrying the literal, unsplit `#628` line).

```
FAIL  case 6: it cites the issue so the reader can find out why
      | dispatch-guard: BLOCKED - single-flight (harness-pm)
  existing claim started 2026-08-27T03:03:51.919921+00:00, dispatched by harness-product-lead
  this is issue #628: the second writer would otherwi
```
27 of 28 cases passed.

Fix applied immediately after: `refusal_lines` now emits `#628` on the plan.yaml sentence AND
a second line, `"  (the original single-flight report is #551.)"`, that carries `#551` with no
`plan.yaml` on it. Both grep clauses in T-06's verify are satisfied and
`test-dispatch-guard.py` returned to 28/28 green — see the digest for the confirming run.

## Full post-fix runs

`python3 .claude/skills/harness/bin/test-inflight-registry.py` → `PASS - 69/69 checks passed`
`python3 .claude/skills/harness/bin/test-dispatch-guard.py` → `28 of 28 cases passed`
`python3 .claude/skills/harness/bin/test-validate-digest.py` → `ALL PASSED` (exit 0) at the
moment I ran it — the real `.harness/.inflight-claims.json` was `{}` at that instant. This
suite is non-hermetic by design (its `[hook]` cases shell out and read the live registry); an
earlier run in this same session, before any tree edits, printed the documented 6 `[hook]`
FAILs plus the umbrella line when a live claim happened to be present. Neither state reflects
a defect in this task's files — see the digest for the full account.
