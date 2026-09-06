# EFFICIENCY angle — BUG-1306 hermeticity diff — nothing found

**BLUF: no efficiency finding.** The added cost is ~400ns, once, at module import. That is
five to six orders of magnitude below any "hot-path millisecond" threshold and does not touch
session entry (this is a test module, not a gate/hook run at every session start).

## What was measured

`os.environ.pop("HARNESS_AGENT_TYPE", None)` (test-plan-merge.py:38, added by this diff) is a
single dict `del`-or-noop. Timed directly: `timeit` over 100k calls to the same operation gave
**391.9ns/call** (see command run this session, `env -u HARNESS_AGENT_TYPE python3 -c
"import timeit; timeit.timeit(...)"`). It runs exactly once, at module import, not per-case,
not per-subprocess-spawn. Verdict: nanoseconds, explicitly not a finding per the skill's own
"measure before flagging" instruction.

## The one real efficiency question (checked per dispatch step 2)

Grepped every `env=` call site in the file (`grep env=`, file lines 145-152, 1117-1119,
1140-1142). Two cases build an explicit environment mapping:

- `case_1103_sign_approval_refuses_a_governed_agent` (line 1117): `dict(os.environ,
  HARNESS_AGENT_TYPE="harness-pm")` — deliberately re-adds the variable to test the governed
  path. This is the opposite of duplicating the pop's work; it needs the variable present, so
  it must set it explicitly regardless of what module import did.
- `case_1103_..._negative_control_absent_is_main_session` (line 1140): `{k: v for k, v in
  os.environ.items() if k != "HARNESS_AGENT_TYPE"}` — this DOES redundantly re-filter a key the
  module-level pop already removed. However: (a) this case body is one of the two explicitly
  named as LEAVE in the shared context — "both `case_1103_` case bodies … are byte-identical to
  the pre-fix blob and must stay so" — so it predates this diff and its cost is not something
  this change introduced; (b) even so, costed honestly: a dict comprehension over
  `os.environ.items()` (a few dozen entries in a typical CI/dev shell) is itself sub-microsecond
  and runs once per case invocation, not in any loop. Not a finding either way — flagging it
  would also contradict the settled LEAVE.

No case duplicates a subprocess spawn, re-spawns twice where once would do, or reconstructs an
environment it previously inherited *because of* the module-level pop.

## Verdict

Nothing found. The change is a one-time, module-import-time dict operation with a measured
cost of ~400ns — not a hot path, not session entry, not repeated I/O, no duplicated
subprocess/env work attributable to this diff.

No repo file edited; no formatter/linter/build/project-wide suite run. HEAD unchanged.
