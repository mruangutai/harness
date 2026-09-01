# Security review — BUG-1128 `amend` verb — panel c1

Scope owned: items 1 (compare-and-swap), 4 (approval reachability), and the trust boundary
generally (path handling, lock, secrets/log exposure). Items 2, 3, 5, 6, 7 explicitly left to
peers (code-reviewer, QA, UI-reviewer per the live hub roster); item 3 is referenced below only
because my item-4 probing produced direct evidence bearing on it.

## Headline

Item 4 (`approval:` unreachable) holds — proven, not merely argued. Item 1 (compare-and-swap) is
sound — the under-lock re-check is genuinely load-bearing and the pre-lock check is a
non-load-bearing fast-fail. But probing item 4 surfaced a **HIGH-severity, empirically confirmed**
defect outside my assigned items that must gate: `_field_block` binds `--field` to the FIRST
line in the item matching the field's name, even when that line sits INSIDE an earlier field's
block-scalar body. A caller who runs the documented workflow (`--show` → copy the hash → replace)
can have the tool silently splice into the WRONG field, corrupting it, while reporting
`AMENDED <key>:<id>.<the field the caller asked for>` and exiting 0. The field the caller actually
asked to change is left untouched.

## Item 4 — `approval:` reachability — REFUTED, confirmed unreachable

- **Direct route blocked.** `--key approval` is rejected before the file is even opened:
  `plan-merge.py:1020`, exit 2. Verified live: `plan-merge.py amend --key approval --id status
  --field status --show` → exit 2, the DEC-120 message.
- **Indirect route structurally impossible, not merely undefended.** `_item_range` bounds an
  item to `ranges[key]` from `_index_top_keys` — i.e. strictly before the NEXT top-level key.
  `_field_block` bounds a field to `[first, last)` inside that item. The splice
  (`cur[:f2] + rendered + cur[l2:]`) only ever replaces bytes in that exact half-open range.
  There is no code path by which the replacement text — however constructed — can move those
  boundaries: they are computed from the file's OWN existing structure before the caller's value
  is ever read.
- **`--value-file` content cannot forge structure either.** `_field_lines` renders the value
  through `yaml.safe_dump({field: value})` (a python `str`, never re-parsed as YAML) and then
  prefixes EVERY emitted line — blank lines excepted — with the field's own non-empty indent
  (`plan-merge.py:266-269`). A value containing literal text like `\napproval:\n  status:
  approved` is dumped as a quoted/escaped scalar and then indented, so it can never emit a
  column-0 line; a synthetic top-level key is structurally unrepresentable through this path.
  YAML anchors/aliases/merge keys embedded in the value are likewise inert: they are string
  bytes inside a `safe_dump`-rendered scalar, never re-parsed as YAML syntax.
- **DO-NO-HARM does not loosen this.** The schema-skip-on-invalid-base branch
  (`plan-merge.py:~1090`) only skips the POST-splice legality check; it has no effect on the
  splice's physical byte range, which is fixed before the schema question is even asked. Tested
  live: the mis-binding defect below reproduces on a schema-VALID base, so DO-NO-HARM isn't even
  the enabling condition for the worst thing I found.
- Symlink/traversal on `--file` also checked as part of the same trust boundary: a symlink placed
  at a legal-looking `.harness/features/FEAT-X/plan.yaml` path pointing outside any features tree
  is refused (exit 9, `require_destination`'s `realpath`-based tail match), verified live.

**Verdict on item 4: approval is genuinely unreachable, directly and indirectly, structurally
rather than by convention.**

## NEW finding (must-fix) — field-block mis-binding corrupts an unrelated field, silently, with a false success signal

**Mechanism.** `_field_block` (`plan-merge.py:983`) scans an item top-to-bottom for the FIRST
line matching `^(\s*)(field):` at an indent deeper than the item's dash — with no awareness of
whether that line is a real sibling key or merely text sitting inside an EARLIER field's
block-scalar (`verify: |`, `intent: |`, `because: ...`) body. Real task `verify:` bodies in this
repo are shell/python snippets that routinely contain `word:`-shaped lines (dict literals,
assertions, comments referencing another field by name) at a deeper indent than the item's dash.

**Reproduced live**, at `/tmp/secreview/repo/.harness/features/BUG-9999-secfix/plan.yaml`, a
schema-valid fixture built from real excerpts (D-05, D-14, T-23 verbatim from FEAT-46's actual
plan.yaml) plus a second task, T-24, whose `verify: |` block contains one plausible line
(`      intent: forged-inside-verify-body`, a stand-in for the kind of in-body text real verify
scripts already carry) BEFORE T-24's real `intent: |` field:

```
$ plan-merge.py amend --key tasks --id T-24 --field intent --show
      intent: forged-inside-verify-body
      print('audit ok')
      "
sha256: 962e885...
```
`--show` for `--field intent` printed the TAIL OF THE VERIFY BLOCK, not the intent field — the
compare-and-swap hash is already bound to the wrong bytes at this point.

```
$ plan-merge.py amend --key tasks --id T-24 --field intent \
    --expect-sha256 962e885... --value-file replacement.txt
AMENDED tasks:T-24.intent
APPLIED ...
```
Exit 0. Result: `verify:`'s heredoc is now truncated mid-script (the closing quote and
`print(...)` line are gone, replaced by `intent: Corrected intent text after amend.`), and the
REAL `intent:` field two lines below is **completely untouched** — the change the caller asked
for never happened. The tool's own success line names the field the caller intended, not the
field it actually wrote.

**Why this passes undetected.** `cmd_amend`'s only post-splice checks are `yaml.safe_load`
parses and `_schema_error` (skipped when the base was already invalid). Neither catches this:
the corrupted `verify:` value is still a non-empty string, so `REQUIRED_TASK_FIELDS` presence
is satisfied and the schema is "legal" by its own (shallow, presence-only) definition. Unlike
`sign-approval`, which the dispatch already flagged as carrying `_verify_signature` — a
post-splice check that the reloaded value literally equals what was asked for — `cmd_amend` has
no equivalent identity check. That absent check is exactly what would have caught this: had
`cmd_amend` asserted `yaml.safe_load(spliced)[key-item][field] == value_text` after the splice
(mirroring `_verify_signature`'s own reasoning), this defect would refuse instead of report
false success.

**Blast radius and why it gates.** This is the artifact every plan gate depends on, and the
whole reason this verb exists is that hand-editing it is denied. A caller doing exactly what the
tool's own help text prescribes (`Run --show first`) gets a false `AMENDED` confirmation while a
DIFFERENT field of the SAME item silently loses content — here, the task's own `verify:` gate
script. No malice required, no unusual access — only an ordinary verify/intent body that happens
to contain a line shaped like another field's name, which is a plausible, not contrived, shape
for the shell/python content these fields carry throughout this repository.

**Scope note.** Live-checked the real FEAT-46 plan.yaml this feature was built for (the fixture
at the FEAT-46 worktree, not a copy): reconstructed every task/decision's field boundary via
`_item_range`/`_field_block` and diffed each against `yaml.safe_load`'s ground truth for
`verify`, `intent`, `title`, `choice`, `because`, `dec` — zero mismatches today. The document
does not currently trigger this defect; nothing in the tool prevents the NEXT one from doing so,
and no test in `test-plan-merge.py`'s ten `case_amend_*` covers a field-block located inside
another field's body.

## Item 1 — compare-and-swap — sound, pre-lock check confirmed non-load-bearing

- The pre-lock hash check (`plan-merge.py`, before `locked_update`) is a fast, UNLOCKED read —
  it can be stale the instant it returns.
- The load-bearing check is inside `transform`: `locked_update` opens `path` fresh, UNDER the
  exclusive `flock`, and `transform` re-derives `_item_range`/`_field_block` and re-hashes
  against that fresh read before splicing. Because every one of the five verbs (including
  `amend`) routes through the same `locked_update`, no other verb-mediated writer can interleave
  between that fresh read and the write — they serialize on the same lock. This closes the
  TOCTOU window completely for every writer that goes through this tool.
- Verified live: after `--show` captured a hash, a second (legitimate) `amend` call changed the
  same field first; the STALE caller's replace, retried with the old hash, was refused at the
  fast pre-lock path (exit 6, "the field changed since you read it"). Consistent with the
  documented design.
- Lock DoS bounded, verified live: with `plan.yaml.lock` held externally via a raw `flock`, a
  correctly-hashed `amend` call blocked for exactly `LOCK_TIMEOUT_SECONDS` (10.13s measured) and
  then refused cleanly (exit 6, `LOCKED: ...`), with **no partial write** — file unchanged. This
  is shared machinery across all five verbs (`harness_merge.py`), not new to `amend`, and the
  module's own docstring already accepts the residual gap (no identity source, issue #627) as
  out of scope for this feature.
- **Residual, pre-existing, out of scope for this feature:** a writer that bypasses
  `harness_merge.locked_update` entirely (a raw file write) is not defended by this lock — but
  that route is exactly what FEAT-41 T-09's Edit/Write DENY gate closes at a different layer.
  Not a new gap; not this verb's to fix.

## Other trust-boundary checks (no findings)

- **`--value-file` destination asymmetry** (no `require_destination` guard, unlike `--file`):
  not a vulnerability. It is a READ of caller-supplied content, never written anywhere by this
  tool; the same principal that supplies `--value-file` already supplies the whole command line
  and could embed the value directly. No privilege boundary is crossed by letting it read an
  arbitrary path.
- **Secrets/log exposure:** refusal messages print ids, field names, hashes, and the plan path —
  no credentials are handled anywhere in this code, and `--show`'s field-body output is by
  design (revealing exactly what the tool is about to compare-and-swap on), no more than a
  direct read of the same file would reveal.

## Scoped out

Items 2 (single-renderer / regression-guard discrimination), 3 (field-block bounding root
cause — though my repro above is direct evidence for it), 5 (registration-table reasoning), 6
(the decisive real-replace-against-FEAT-46 functional experiment), 7 (staged blocks correctly
unapplied) are not this role's lens and are left to the code-reviewer/QA/UI-reviewer legs of the
panel, several of whom are actively working them per the live roster. Item 3 in particular should
be read together with my new finding above — same root cause, found via item-4 probing rather
than direct assignment.

## Fixtures

`/tmp/secreview/repo/.harness/features/BUG-9999-secfix/plan.yaml` (built from real FEAT-46
D-05/D-14/T-23 excerpts) and `/tmp/secreview/outside-secret.yaml` — scratch, not part of any
tracked tree, safe to discard.
