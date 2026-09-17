# Answers — FEAT-53 validate 24 (Q1: stop, or another T-27 round) — 2026-09-17

## Ruling: neither. Amend T-27; the all-unreadable 500 clause is unreachable.
`work.fleet_repositories` always seeds the readable set with the serving control plane (`work.py:96`, `repositories = {"harness": root}`), and `serve.py` refuses to start without `.harness/harness.json` (`prerequisite_errors`). While the server is answering, at least one segment is readable by construction; the ruled "500 only when NO segment can be read" state cannot occur. A control plane with zero features legitimately returns an empty 200 payload — that is an empty dashboard, not a fault. The `except Exception → 500` at `serve.py:160` already covers genuine collector failure (malformed fleet.yaml, unreadable root), and the existing invalid-config fixture exercises it.

Therefore: amend T-27 to strike the all-unreadable 500 requirement with this reason; QA's must_fix is discharged by amendment, not by code. No production change, so review_sha `daba2af5` stands. Re-run **qa only** to confirm the matrix against the amended T-27 (1 cycle). Then reset notes/uat.md and hand the UAT back. Cap: 2 cycles.

## Operator-observed at daba2af5 (live, this control plane)
`/api/work?window=all&repo=all` → 200, 165 items, one `errors[]` entry for `harness-factory-smoke`. `/api/work?window=90d&repo=harness` → 200. `/api/kpis?window=90d&repo=harness` → 200 in 3.7 s. The U-01 fix does what was ruled.
