# Receipt: simplify-append-eng · SIMPLIFICATION angle

BLUF: no findings. The append guard is minimal; deleting it would reintroduce the hidden-correction (fail-open) failure.

Scope read: `validate-digest.py::_append_record` (1851-1875), the 3c1923cf diff of the test and SKILL.md. Read-only; nothing run.

- Deletion test: the guard (`:1864-1867`) adds no new module or wrapper. It reuses `_last_record` and the one `suffix` value that is then written, so the checked bytes equal the written bytes. Removing it would let an open prose fence swallow the appended object, so the durable reader would not return it. No pass-through is added.
- `last == obj` early return (`:1862`) is needed for idempotency. It is not subsumed by the guard, because a repeat must write nothing.
- The two refusal tests are distinct. The first-record case has no prior record; the stale-correction case has one that an open fence could mask. Merging them would drop a path. The closed-prose case is the positive control.
- SKILL.md adds four lines. They state the author-side rule once and are not duplicated elsewhere in the diff. No restated-rule drift was seen.
- No comments narrate the change, and there are no redundant conjuncts.

Principles applied: Delete First (read in full this run). I looked for removals and found the diff already minimal, so nothing is proposed.

Findings: [] (empty)
