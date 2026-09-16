# SEC-F-10 validator repair receipt

Result: PASS. The real `ask()` subprocess argv now contains exactly one `--no-tools` and no `--auto-approve`. The existing list-form subprocess seam is unchanged. Validator send-backs/cycles: 1.

## RED

Command:

```text
python3 tests/unit/test-probe-handoff-comprehension.py
```

Observed failure (exit 1; 7 tests discovered/run):

```text
======================================================================
FAIL: test_ask_disables_tools_without_auto_approval (__main__.ProbePathSecurityTest.test_ask_disables_tools_without_auto_approval)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-54-handoff-done-when/tests/unit/test-probe-handoff-comprehension.py", line 105, in test_ask_disables_tools_without_auto_approval
    self.assertEqual(1, argv.count("--no-tools"))
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 1 != 0

----------------------------------------------------------------------
Ran 7 tests in 0.015s

FAILED (failures=1)
```

## GREEN / authorized validator-cycle verify

Command:

```text
python3 tests/unit/test-probe-handoff-comprehension.py
```

Exact output (exit 0):

```text
.handoff comprehension probe: DRY RUN
model: test-model
arms: as-written, done-when-stripped
questions:
- What is the one immediate next action?
- What exact scope must be completed?
- Which authorities define when that action is complete?
- What evidence would show that every authority is satisfied?
notes:
- /private/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmp08jtczvh/.harness/harness/features/FEAT-test/notes/handoff-valid.md
planned model calls: 2 (not executed)
.note: /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpg6tmepgr/handoff-repository-outside.md
error: refusing note: path is not a feature handoff note
handoff comprehension probe: REAL RUN
model: test-model
arm labels: as-written, done-when-stripped
total evidence:
arm: as-written; coverage: 0/0; complete answers: 0/0
arm: done-when-stripped; coverage: 0/0; complete answers: 0/0
all complete answers: 0/0
note: /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmp7z4sm_0p/handoff-absolute-outside.md
error: refusing note: path is not a feature handoff note
handoff comprehension probe: REAL RUN
model: test-model
arm labels: as-written, done-when-stripped
total evidence:
arm: as-written; coverage: 0/0; complete answers: 0/0
arm: done-when-stripped; coverage: 0/0; complete answers: 0/0
all complete answers: 0/0
note: /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpg6tmepgr/.harness/harness/features/FEAT-test/notes/../../../../../outside/handoff-traversal.md
error: refusing note: path is not a feature handoff note
handoff comprehension probe: REAL RUN
model: test-model
arm labels: as-written, done-when-stripped
total evidence:
arm: as-written; coverage: 0/0; complete answers: 0/0
arm: done-when-stripped; coverage: 0/0; complete answers: 0/0
all complete answers: 0/0
.note: /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmponlys2g7/.harness/harness/features/FEAT-test/notes/handoff-directory.md
error: refusing note: target is not a regular file
handoff comprehension probe: REAL RUN
model: test-model
arm labels: as-written, done-when-stripped
total evidence:
arm: as-written; coverage: 0/0; complete answers: 0/0
arm: done-when-stripped; coverage: 0/0; complete answers: 0/0
all complete answers: 0/0
.note: /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmptn_h2tqk/.harness/harness/features/FEAT-test/notes/handoff-link.md
error: refusing note: symlinks are not allowed
handoff comprehension probe: REAL RUN
model: test-model
arm labels: as-written, done-when-stripped
total evidence:
arm: as-written; coverage: 0/0; complete answers: 0/0
arm: done-when-stripped; coverage: 0/0; complete answers: 0/0
all complete answers: 0/0
note: /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmptn_h2tqk/.harness/harness/features/FEAT-test/notes/handoff-link.md
error: refusing note: symlinks are not allowed
handoff comprehension probe: REAL RUN
model: test-model
arm labels: as-written, done-when-stripped
total evidence:
arm: as-written; coverage: 0/0; complete answers: 0/0
arm: done-when-stripped; coverage: 0/0; complete answers: 0/0
all complete answers: 0/0
.handoff comprehension probe: REAL RUN
model: test-model
arm labels: as-written, done-when-stripped
note: /private/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpe67n3dv2/.harness/harness/features/FEAT-test/notes/handoff-valid.md
note sha256: 445da21d1b0668eeb9b7a3958ee14ec14fe2434ba4ac8a539a8493924f4066a3
required facts (1):
- safe
arm: as-written
coverage: 1/1
covers every fact: yes
answer:
safe
arm: done-when-stripped
coverage: 1/1
covers every fact: yes
answer:
safe
note complete answers: 2/2
total evidence:
arm: as-written; coverage: 1/1; complete answers: 1/1
arm: done-when-stripped; coverage: 1/1; complete answers: 1/1
all complete answers: 2/2
.note: /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpw0ptevm6/.harness/harness/features/FEAT-test/notes/not-a-handoff.md
error: refusing note: path is not a feature handoff note
handoff comprehension probe: REAL RUN
model: test-model
arm labels: as-written, done-when-stripped
total evidence:
arm: as-written; coverage: 0/0; complete answers: 0/0
arm: done-when-stripped; coverage: 0/0; complete answers: 0/0
all complete answers: 0/0
note: /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpw0ptevm6/.harness/harness/features/FEAT-test/notes/handoff-oversized.md
error: refusing note: note exceeds 1048576 bytes
handoff comprehension probe: REAL RUN
model: test-model
arm labels: as-written, done-when-stripped
total evidence:
arm: as-written; coverage: 0/0; complete answers: 0/0
arm: done-when-stripped; coverage: 0/0; complete answers: 0/0
all complete answers: 0/0
.
----------------------------------------------------------------------
Ran 7 tests in 0.017s

OK
```

## Files touched

- `tests/manual/probe-handoff-comprehension.py`
- `tests/unit/test-probe-handoff-comprehension.py`
- `.harness/harness/features/FEAT-54-handoff-done-when/notes/receipt-harness-dev-ops-2026-09-03-sec-f10-c5.md` (this required receipt)
