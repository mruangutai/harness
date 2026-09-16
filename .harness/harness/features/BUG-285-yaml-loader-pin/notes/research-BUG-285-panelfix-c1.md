# panelfix c1 — T-02's catch set closed, and pinned by SC-11

**The panel's one must_fix is closed by two writes: T-02's `intent:` now DECIDES
`except (json.JSONDecodeError, UnicodeDecodeError, OSError) as e:` with its reasoning, and BRIEF
SC-06 now grades the COVERAGE rather than the literal pair while new SC-11 runs a non-UTF-8
`feature.json` through `load_factory`.** One blocking question remains: SC-11's check needs a
matching sentence in T-03's `intent:`, which this cycle may not write (exact text in the DIGEST).

## Premises, re-measured at source in this worktree (not adopted on report)

- `issubclass(json.JSONDecodeError, ValueError)` True; `issubclass(UnicodeDecodeError, ValueError)`
  True; `issubclass(UnicodeDecodeError, json.JSONDecodeError)` **False**;
  `issubclass(UnicodeDecodeError, OSError)` **False**.
- `open(p, encoding="utf-8").read()` on bytes `\xff\xfe` raises `UnicodeDecodeError`; the current
  reader absorbs it in its own arm (`harness_yaml.py:259`, whose comment forbids simplifying the
  pair). `factory_cli.py:88-96` is the generic handler that would print the class name.
- `harness_yaml.DuplicateKeyError` and `harness_yaml.MissingDependency` are both `YamlParseError`
  subclasses (measured `__mro__`), so `factory_decompose.py:122` refuses both today.
- `json.loads` on 2 000 and 20 000 nesting levels parses; 200 000 raises `RecursionError`, which is
  **not** a `ValueError`.

## The decision, and what it gives up

**Chosen: the explicit three-name tuple.** Rejected `except ValueError` (the common ancestor): its
original stated reason still holds — breadth would report an unrelated `ValueError` raised deeper in
the call as an invalid `feature.json`, and the try body is two statements, so breadth buys nothing.
Rejected a read-then-parse split: `refuse()`'s message is fixed byte-for-byte, so both arms would
emit the identical string — a branch with no observable difference. **The cost of the tuple is that
it is hand-maintained**, which is exactly the defect that just occurred; what stops the recurrence is
not the tuple but SC-06 (coverage, not spelling) and SC-11 (behaviour).

## The enumeration the finding was really about

`intent:` item 2b now lists every failure `load_file` absorbed and where each lands: missing file
(pre-empted by the `os.path.exists` early return at `:114-115` — an absent file is a DEFAULT, not a
refusal; the `OSError` arm covers only the disappear-after-check race), directory-in-place-of-file
(`IsADirectoryError`, `OSError`), unreadable file (`PermissionError`, `OSError`), undecodable bytes
(`UnicodeDecodeError` — the finding), malformed text (`JSONDecodeError`), non-mapping document (no
exception; the `isinstance` guard at `:124` stays). Two entries change behaviour and owe no new arm:
**duplicate key** (was `DuplicateKeyError`, now silent last-wins — already disclosed in BRIEF's
Constraints and Risk, so the enumeration is complete without one) and **PyYAML absent** (was
`MissingDependency`; the failure mode disappears with a stdlib parser). `RecursionError` is named as
considered-and-excluded with its measurement, so a later reader cannot read it as missed.

## Criteria

- **SC-06** (`BRIEF.md:133-146`) no longer certifies the incomplete pair. It grades three coverages
  and says the spelling is free; a handler omitting the decode failure fails it.
- **SC-11** (`BRIEF.md:170-181`), new, `verify: automated  evidence: unit`. Non-UTF-8 bytes in,
  observable refusal out (`SystemExit`, `EXIT_REFUSED`, path in stderr, and neither
  `unexpected failure` nor the string `UnicodeDecodeError`). **Traced to T-03's existing `verify:`**,
  which already runs the unit file and the unit-kind runner with no command change.
- SC-11 is honest about its discrimination: it is green under the OLD YAML reader too (`load_file`
  caught the decode failure), so it is a standing guard against re-narrowing, not a red-then-green
  proof. REQ-06 needs no rewording — "never prints an exception class name" already binds this input.

## Open

- **Blocking:** T-03's `intent:` has no instruction to write SC-11's check. Exact proposed sentence
  is in the DIGEST for the product lead. Without it SC-11 traces to a `verify:` that runs a check
  nobody was told to write.
- Unchanged from the panel and not mine: the `approval.status: approved` (2026-09-09) versus BRIEF
  `pending` disagreement now spans a fourth amendment.
