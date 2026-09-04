# APPLY-S-04 receipt — FEAT-54 validation c2

Verdict: PASS

Removed only the unreachable `if not evidence` branch from `tests/manual/probe-handoff-comprehension.py`; `measured` now increments unconditionally after `measure_note`. This is behavior-preserving because `measure_note` constructs its returned dictionary by zipping the two constant `ARMS` with the two-element `arm_notes` tuple, so every normal return contains two evidence entries. The two constant arm calls, inputs, evidence, counters, bounded-input checks, and experiment behavior remain unchanged.

Because source changed, the orchestrator must rerun the QA matrix before accepting validation c2.

## Scoped verification

Command (run from the assigned worktree):

```text
python3 tests/unit/test-probe-handoff-comprehension.py
```

Result: exit 0; 6 tests passed.

Verbatim output:

```text
handoff comprehension probe: DRY RUN
model: test-model
arms: as-written, done-when-stripped
questions:
- What is the one immediate next action?
- What exact scope must be completed?
- Which authorities define when that action is complete?
- What evidence would show that every authority is satisfied?
notes:
- /private/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpb0bwwwwi/.harness/harness/features/FEAT-test/notes/handoff-valid.md
planned model calls: 2 (not executed)
.note: /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpgzbs0kec/handoff-repository-outside.md
error: refusing note: path is not a feature handoff note
handoff comprehension probe: REAL RUN
model: test-model
arm labels: as-written, done-when-stripped
total evidence:
arm: as-written; coverage: 0/0; complete answers: 0/0
arm: done-when-stripped; coverage: 0/0; complete answers: 0/0
all complete answers: 0/0
note: /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpwgqza_i0/handoff-absolute-outside.md
error: refusing note: path is not a feature handoff note
handoff comprehension probe: REAL RUN
model: test-model
arm labels: as-written, done-when-stripped
total evidence:
arm: as-written; coverage: 0/0; complete answers: 0/0
arm: done-when-stripped; coverage: 0/0; complete answers: 0/0
all complete answers: 0/0
note: /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpgzbs0kec/.harness/harness/features/FEAT-test/notes/../../../../../outside/handoff-traversal.md
error: refusing note: path is not a feature handoff note
handoff comprehension probe: REAL RUN
model: test-model
arm labels: as-written, done-when-stripped
total evidence:
arm: as-written; coverage: 0/0; complete answers: 0/0
arm: done-when-stripped; coverage: 0/0; complete answers: 0/0
all complete answers: 0/0
.note: /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmp9s8u2fsd/.harness/harness/features/FEAT-test/notes/handoff-directory.md
error: refusing note: target is not a regular file
handoff comprehension probe: REAL RUN
model: test-model
arm labels: as-written, done-when-stripped
total evidence:
arm: as-written; coverage: 0/0; complete answers: 0/0
arm: done-when-stripped; coverage: 0/0; complete answers: 0/0
all complete answers: 0/0
.note: /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmp8ifcwrfu/.harness/harness/features/FEAT-test/notes/handoff-link.md
error: refusing note: symlinks are not allowed
handoff comprehension probe: REAL RUN
model: test-model
arm labels: as-written, done-when-stripped
total evidence:
arm: as-written; coverage: 0/0; complete answers: 0/0
arm: done-when-stripped; coverage: 0/0; complete answers: 0/0
all complete answers: 0/0
note: /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmp8ifcwrfu/.harness/harness/features/FEAT-test/notes/handoff-link.md
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
note: /private/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpxvg_c744/.harness/harness/features/FEAT-test/notes/handoff-valid.md
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
.note: /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpk6xhk6jk/.harness/harness/features/FEAT-test/notes/not-a-handoff.md
error: refusing note: path is not a feature handoff note
handoff comprehension probe: REAL RUN
model: test-model
arm labels: as-written, done-when-stripped
total evidence:
arm: as-written; coverage: 0/0; complete answers: 0/0
arm: done-when-stripped; coverage: 0/0; complete answers: 0/0
all complete answers: 0/0
note: /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpk6xhk6jk/.harness/harness/features/FEAT-test/notes/handoff-oversized.md
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
Ran 6 tests in 0.019s

OK


Wall time: 0.10 seconds
```

No broader command was run.
