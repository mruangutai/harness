# Grilling — Claude Code lifecycle safety — 2026-09-01

## Destination

Claude Code can suspend a parent with live children without polling or fabricating a terminal verdict. If the parent is interrupted, children may finish analysis but cannot race a replacement writer; a resumed parent explicitly adopts or discards the result. OMP behavior does not change.

## Settled

- What happens to live children when a Claude Code parent is interrupted? → They may finish read-only analysis, while feature-artifact writes are quarantined until a resumed parent explicitly adopts the result.
- How does a Claude Code parent end a normal turn while children are live? → It makes a nonterminal suspension with no verdict; the host wakes the same parent when the child finishes, and only then is a terminal digest required.
- May the parent poll while suspended? → No. The parent does not poll at all.
- Which backlog defects define the work? → Issues #280 and #551 together. Issue #628 is not part of the feature.

## Not yet specified

- None. Engineering may choose the narrowest host-compatible quarantine and wake mechanism that satisfies the settled behavior.

## Out of scope

- OMP lifecycle behavior — DEC-204 already supplies blocking nested tasks and process-owned supervision.
- Rebuilding plan merge safety — FEAT-32 already shipped `plan-merge.py` for issue #628.
- Letting an orphan write canonical feature artifacts and repairing the race afterward — the required boundary prevents the concurrent write.
- Polling, sleeps, heartbeat calls, or fabricated work while a child runs — explicitly rejected by the operator.

## Facts I verified (so pm does not re-derive them)

- Issue #280 is now scoped to Claude Code compatibility and records the historical orphan-child behavior — GitHub issue #280, checked 2026-09-01.
- Issue #551 records the normal `SubagentStop` refusal while members are live and the resulting false-reporting/context-burn failures — GitHub issue #551, checked 2026-09-01.
- OMP declares every lead and member `blocking: true`; DEC-204 says the parent model stays inactive until the child returns and a dead supervisor does not imply detached work survived — `.omp/agents/harness-*.md` and DEC-204, verified at `6ddcac39521cbc7c93b280f8eb4bad13a8ab6893`.
- Claude Code has no durable child-process owner; compatibility claims use the bounded TTL path — `inflight_registry.py`, verified at `6ddcac39521cbc7c93b280f8eb4bad13a8ab6893`.
- Issue #628's safeguard is already implemented by FEAT-32 in `plan-merge.py`; `test-plan-merge.py` passes its union, conflict, approval-preservation, destination, parse-error, and concurrency cases — executed on 2026-09-01 at `6ddcac39521cbc7c93b280f8eb4bad13a8ab6893`.
