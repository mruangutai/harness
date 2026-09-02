# Security review — BUG-1128 `amend` verb — panel c2 (review_sha 08dd66bb)

## BLUF

V1–V4's remedies do fix what cycle 0 reproduced, and the two self-caught bugs are real fixes
too — verified live. But the fixes are narrower than their own docstrings claim, and I found a
**live, silent, exit-0 data-loss regression on ordinary input** that neither cycle 0 nor the
author's own mutation suite exercises: a comment or blank line sitting between the amended
field and the next field is swept into the replaced range and permanently deleted, on any
`amend`, while `AMENDED`/`APPLIED` print and the identity check passes — because the check
only compares the ONE field the caller asked for, never the bytes around it. This is the same
class of harm V1 was meant to close and gates on its own. I also confirmed a second, narrower
gap in V1/V2's block-scalar recognition (`|2-`-style headers), and a crash class in
`--value-file` handling one layer over V4. Approval-unreachability and do-no-harm-on-refusal
both re-confirmed clean.

## FINDING 1 (HIGH, must-fix) — filler content between fields is silently deleted by any amend of the preceding field

**`plan-merge.py:1054-1059`.** `_field_block`'s scan for a PLAIN (non-block) field's end stops
only at `ITEM_ID_RE` or a `SIBLING_KEY_RE` match at `<= indent`. A comment or blank line
matches neither, so it is inside the range the splice replaces — and the splice deletes it,
because the replacement is only the new field's rendered text.

**Reproduced live**, plan built from realistic content (a task with a hand-written comment,
then a blank-line variant, both under `/tmp/secc2/repo/.harness/features/BUG-999{2,3}-*`):

```
    title: Fix the thing
    # NOTE: keep this
    intent: |
      ...
```
```
$ plan-merge.py amend --key tasks --id T-24 --field title --show
    title: Fix the thing
    # NOTE: keep this      <-- the comment is INSIDE the shown/hashed block
sha256: 7396fdac...
$ plan-merge.py amend --key tasks --id T-24 --field title \
    --expect-sha256 7396fdac... --value-file newtitle.txt
AMENDED tasks:T-24.title
APPLIED ...
```
Result: `title:` reloads correctly (the identity check has nothing to object to), but
`# NOTE: keep this` is gone from the file — permanently, at exit 0, with no diagnostic. The
blank-line variant (`title:` \n\n `intent: |`) reproduces identically: the blank line vanishes.

**Why the identity check (V3/H6) does not catch it.** `_verify_amend` (`plan-merge.py:315`)
checks `got[0].get(field) != want` — one field, by name. It was written to catch a splice that
lands in the WRONG field (V3's actual bug); it was never designed to, and does not, catch a
splice that lands in the RIGHT field but over-captures neighboring bytes. Cycle 0's own V1
finding was framed as "a prose line was mistaken for a key" — that mechanism (block-scalar
bodies) is now guarded. This is the adjacent, unguarded mechanism: a plain field's own
end-of-block boundary is still just "next key or end of item," with no allowance for
non-key filler, and V1's fix never touched that code path.

**Blast radius.** No adversarial input required — an ordinary reviewer-left comment
(`# see D-14 for why`) or a blank line for readability, immediately preceding the field
someone amends, is destroyed silently. `test-plan-merge.py`'s only comment case
(`case_amend_preserves_comments_elsewhere`, ~:1153) places its comment in the file PREAMBLE,
which `_field_block` never scans — it does not intersect this code path at all, so it proves
nothing about it. None of the ten `case_amend_*` cases put a comment or blank line between two
fields of the same item.

## FINDING 2 (MED) — `BLOCK_HEAD_RE` does not recognize the legal `<indicator><digit>` header order (e.g. `|2-`, `>3+`)

**`plan-merge.py:1004`**: `BLOCK_HEAD_RE = r"^(\s*)([A-Za-z_][\w-]*):\s*([|>][+-]?\d*)\s*$"` only
matches chomp-then-digit order (`|-2`), never digit-then-chomp (`|2-`). Both orders are legal
YAML (spec allows either); PyYAML parses `|2-` correctly as a block scalar
(`yaml.safe_load` confirmed live). Two distinct consequences, both confirmed live at
`/tmp/secc2/repo/.harness/features/BUG-9998-h4/plan.yaml`:

**(a) Read path (`--show`) mis-binds and hands back a false receipt, exit 0.** With
`verify: |2-` whose body contains a line shaped like `title: fake-key-shaped-line`, and a REAL
`title: after` two lines below:
```
$ plan-merge.py amend --key tasks --id T-1 --field title --show
      title: fake-key-shaped-line     <-- inside verify's (unrecognized) body, not the real title
sha256: d4fe7374...
```
A caller trusting this receipt to review "the current title" sees fabricated content. The
follow-on WRITE self-protects here — `_verify_amend` refuses at exit 5 because the real
`title` field never actually changes to the asked-for value (confirmed live, file byte-
identical after refusal) — so this sub-finding is a **misleading read, not a corrupting
write**. Same mechanism reproduces for a block header with a trailing comment
(`verify: |  # literal`, also legal YAML, also unmatched by `BLOCK_HEAD_RE`) and for a nested
mapping carrying the same key name (`checks: {verify: ...}` before the real `verify:`) —
both confirmed live, both fail-closed on write for the same reason.

**(b) Write path silently drops the literal-block FORM when the target field itself carries
the header.** Amending `verify` (the `|2-` field itself, correctly located this time since the
scan finds `verify:` by name) succeeds at exit 0 — content round-trips correctly, so
`_verify_amend` passes — but `_render_field` (`plan-merge.py:1061`) also gates on
`BLOCK_HEAD_RE.match(original[0])`, which is `None` for `|2-`, so it routes through
`_field_lines`/`safe_dump` instead of preserving the literal block. Confirmed:
```
before: verify: |2-
          first line ...
after:  verify: 'python3 -c "

          print(''replaced verify body'')

          "'
```
Content is preserved; the on-disk FORM is not. This is the exact contract V2's docstring says
is load-bearing ("`yaml.safe_dump` never emits `|`... SPEC.md:1813 makes that literal form a
byte-exact contract") — silently broken here for a legal, if uncommon, header shape.

## FINDING 3 (MED) — `--value-file` crashes with an uncaught traceback instead of a documented refusal

**`plan-merge.py:1132-1133`**, `with open(args.value_file, encoding="utf-8") as fh: value_text
= fh.read()` — unwrapped, and runs BEFORE `locked_update`/the lock. Confirmed live for three
input classes, each an uncaught Python exception at exit 1 with a full stack trace to stderr:
absent path (`FileNotFoundError`), a directory (`IsADirectoryError`), and non-UTF-8 bytes
(`UnicodeDecodeError`, raised one line later at `value_text = fh.read()`). The tool's own
documented exit-code vocabulary is `{0,2,3,4,5,6,8,9}` (every `sys.exit` call in the file) —
`1` is outside it. **No corruption**: because this runs before the lock, the plan file is
never touched (confirmed by md5 before/after). This is V4's class ("a broken input crashes
instead of refusing cleanly") one layer over — the base-parse instance was fixed; the
value-file instance was not. Impact is availability/contract, not integrity: a caller or
wrapper script that switches on the documented exit codes gets an undocumented one instead of
a clean refusal.

## FINDING 4 (INFO) — CRLF plan.yaml amends correctly but leaves mixed line endings

Amending a field in a CRLF-encoded `plan.yaml` (built via a raw `\r\n` fixture) correctly
locates and identity-checks the field — confirmed live — but the newly-written field's line
ends in bare `\n` (from `_field_lines`/`_render_field`, both hardcode `f"...{line}\n"`) while
every untouched line keeps `\r\n`. Not a corruption or a wrong value; a hygiene/robustness note
only — flagging because the dispatch asked for it explicitly.

## FINDING 5 (INFO) — the do-no-harm schema-check branch, the only consumer of the self-caught `reloaded` fix, is exercised by none of the ten `case_amend_*` tests

**`plan-merge.py:1187-1191`** (`if _schema_error(base_doc) is None: err = _schema_error(reloaded)
...`) only runs when the BASE document is already schema-valid. `harness_yaml.py:288`'s
`REQUIRED_TASK_FIELDS` is `(id, title, change_type, execution_mode, files, verify, intent)`.
Both `test-plan-merge.py`'s amend fixtures — `_amend_plan()` (:970) and `_block_plan()` (:1246)
— give their tasks only `id, title, verify/intent, status`; neither ever sets `change_type`,
`execution_mode`, or `files` (grepped the full `case_amend_*` range, zero matches). So
`_schema_error(base_doc)` is non-`None` for every existing amend test, the skip condition is
always true, and the schema-check branch — the ONLY place `_verify_amend`'s returned
`reloaded` document is used, i.e. exactly the branch the author's self-caught `NameError` fix
lives in — never runs in the suite. **I built an independent schema-valid fixture and
confirmed live that the mechanism is currently correct**: amending `execution_mode` to an
illegal value on a schema-complete base refuses cleanly at exit 8, file byte-identical. This is
not a live defect — it is a coverage gap on a security-relevant check with zero regression
protection: a future edit could reintroduce the `NameError` or a bypass and nothing in
`test-plan-merge.py` would catch it before it shipped.

## Re-confirmed clean (no new findings)

- **`approval:` unreachable, both routes.** `AMENDABLE_KEYS = ("tasks", "decisions")`
  (`plan-merge.py:978`) and `ITEM_ID_RE` (:979) are byte-unchanged from cycle 0; direct
  `--key approval` still refuses at exit 2 (verified live), and the indirect route remains
  structurally closed for the same reason cycle 0 established (splice range is computed from
  the file's own structure before the value is read). Still pinned by
  `test-plan-merge.py:1135` (`case_amend_refuses_an_unknown_key`).
- **Do-no-harm on refusal, every exit code exercised.** Confirmed byte-identical files (md5)
  after refusals at exit 2 (missing hash/value-file, approval key), 3 (absent id), 4 (absent
  field), 5 (unparseable-after-splice, wrong-field-write, both from Finding 2), 6 (stale hash),
  and 8 (schema violation, Finding 5's fixture) — no partial writes reached disk under the lock
  in any case I drove.
- **`--value-file` as a read of caller-supplied content**: unchanged reasoning from cycle 0 —
  the same principal supplying `--value-file` already supplies the whole command line, so this
  is not a new privilege boundary. Only its FAILURE MODE (Finding 3) is new.

## Fixtures

All scratch, under `/tmp/secc2/`, safe to discard: `repo/.harness/features/BUG-999{2..8}-*` and
`BUG-9994-crlf`, `BUG-9995-quoted`, `BUG-9996-nested`, `BUG-9997-comment-header`, `BUG-9993-schema`
(plan.yaml fixtures for each probe), plus loose value-files (`newtitle*.txt`, `newverify*.txt`,
`badmode.txt`, `badutf8.bin`).
