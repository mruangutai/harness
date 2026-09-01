# UI/operator-surface review — BUG-1128 panel c2 — review_sha 08dd66bb

## Verdict: FAIL — two live silent-corruption/misinformation defects survive the panel's fix

## Measured census

`git diff --stat fe5c5b57..08dd66bb`: 7 files, only `plan-merge.py` (+/-), `test-plan-merge.py`
(+157), and feature bookkeeping (`feature.json`, two `notes/handoff-*.md`, `plan.yaml`,
`review_sha`) — **zero** UI-extension files
(`html|css|scss|tsx|jsx|vue|svelte|less`) changed since the c1 pin (`grep -c` over
`git diff --name-only` returns 0). No `DESIGN.md` in this feature at either pin (confirmed at
c1, unchanged). There is still no rendered UI in this diff. The one operator surface in scope
is `plan-merge.py`'s `amend` CLI, per the dispatch's explicit adjacent-surface instruction.

I ran the real binary against five fixtures built from the actual failure shapes the dispatch
named, rather than reading the strings in isolation (see Evidence). All fixtures/probes live
under `/tmp/uirev-bug1128-*`; nothing in the worktree was touched (`git status --porcelain` on
it is empty).

## Item 1 — cycle-0's F1/F2, adjudicated against the new pin

**F2 (under-lock exit-6 refusal names neither hash) — STILL OPEN, unchanged text.**
plan-merge.py:1162 today reads verbatim what it read at fe5c5b57:
`"plan-merge: {args.id}.{args.field} changed between the read and the lock."` — no hash, no
remedy sentence. Its pre-lock sibling at plan-merge.py:1128-1130 still names both:
`"...expected {args.expect_sha256} actual sha256: {actual}. Re-run --show and re-derive your
replacement."` None of the four closed panel findings touched this code path — it was never in
scope for V1-V4. Severity unchanged: **med, advisory**.

**F1 (exit-2 message has no pasteable recovery command) — STILL OPEN, unchanged text.**
plan-merge.py:1123-1125, byte-identical to c1: `"plan-merge: a replace needs BOTH
--expect-sha256 and --value-file. ... Run --show first."` Still does not reconstruct
`--file <resolved> --key <key> --id <id> --field <field> --show`. Severity unchanged: **med,
advisory**.

## Item 2 — the new messages

**Exit-8, unparseable base (plan-merge.py:1145-1147).** Text: `"plan-merge: the plan on disk
does not parse, so amend cannot tell whether its own splice made things worse — {exc}"`.
**Measured, not assumed: this does NOT name the document**, contrary to the dispatch context's
framing ("refusing exit 8 naming the document"). I built a base with `title: [unclosed` and ran
the real replace (Evidence #1): the refusal prints only "the plan on disk" plus PyYAML's own
`exc`, which itself says `in "<unicode string>"` — an anonymous string, not `resolved`. Every
sibling refusal in the same function (`_item_range`'s exit-3, `_field_block`'s exit-4) DOES
interpolate `{resolved}` into the message. This one silently drops the house convention.
**med** — a single interactive invocation usually lets the operator infer the file from what
they typed, but a script driving `amend` over several plans in a loop gets an error it cannot
attribute.

**`_verify_amend`'s three exit-5 refusals — the "splice defect, not a bad value" wording
(plan-merge.py:333) does NOT reach an operator-caused case in any of my probes**, and I could
not construct one through the exposed splice mechanics: `_field_lines` always emits through
`yaml.safe_dump` (syntactically closed), and the block-scalar path (`_render_field`) always
re-indents every body line to a floor of `indent+2`, so nothing I fed it broke `yaml.safe_load`.
I probed three shapes (a pre-existing comment neighbour, a nested-mapping same-name key, a
pre-existing duplicate id) and none reached the UNPARSEABLE branch — each resolved to a
*different* one of the three messages instead (see below). I flag, not close, this: I cannot
rule out a shape I did not try, and the mechanism-level question of what CAN break
`yaml.safe_load` post-splice is a source-analysis question for code-review, not something a
message-wording audit can exhaustively disprove.

**Duplicate-id refusal (plan-merge.py:341-342), confirmed live on an operator's OWN
pre-existing data**, not a splice defect: a plan with two `- id: T-01` items under `tasks:`
refuses at exit 5 with `"REFUSED: T-01 appears 2 time(s) under tasks: after the amendment;
exactly one is required. A duplicate id cannot be amended unambiguously."` (Evidence #2). The
attribution is correct — it does not blame "a splice defect" — but it names no document and no
remedy action (e.g. "deduplicate T-01 under tasks: by hand before using amend"). **low**: fail-
closed, no data loss, just a completeness gap consistent with F1's shape.

**"Does not reload as written" refusal (plan-merge.py:345-348), confirmed live on a nested-
mapping same-name key** (Evidence #3, see item 2b below): fires correctly, fail-closed, and is
the best-formed message of the three — it shows both `asked for:` and `reloads as:` values. It
does not say *why* (the nested key mis-bind), but that is defensible: diagnosing the mechanism
is not what a refusal owes the operator when the alternative (proceeding) is unsafe. **info**,
no gate.

## Item 2b — a location mis-bind V1's fix does not close, found while probing item 2

V1's remedy makes block-scalar *bodies* opaque, but a **nested mapping** containing a key of
the same name is real YAML syntax, not opaque text, and `_field_block`'s scan (plan-merge.py
:1078-1093) matches the FIRST `SIBLING_KEY_RE` hit deeper than the item indent — it does not
require that hit be at the field's own (shallowest) depth. Fixture:
```
  - id: T-05
    checks:
      verify: nested value, not the real field
    verify: the real top-level verify
```
`amend --field verify --show` returns the **nested** line and its hash at **exit 0, silently
misinforming a read** — the top-level `verify:` is never seen (Evidence #3). This is not new
data loss (V3's identity check refuses the subsequent *replace*, exit 5, file untouched — see
above), but `--show` is a read path with no write to refuse: an operator using `--show` merely
to inspect a value gets the wrong one with no warning. **med** — misinformation without
corruption, but on the tool's only read-only introspection command.

## Item 3 — is the `AMENDED tasks:T-NN.field` receipt adequate? No — H1 reproduces live.

Fixture: `T-01` with `title:`, then a **comment line** `# NOTE: keep this comment, it documents
a gotcha`, then `verify:` (Evidence #4). `--show --field title` returns the title line **plus
the comment** as one block (`_field_block`'s non-block-scalar tail scan stops only at
`ITEM_ID_RE` or a sibling key at ≤ indent — a comment matches neither, so it is swallowed into
whichever field precedes it). Running the real replace: `AMENDED tasks:T-01.title`, **exit 0**.
The plan on disk after: the comment is **gone**, `title:` holds the new value, `verify:`
untouched.

The receipt is the entire operator-visible evidence of this write, and it carries **nothing**
that would let the operator notice: no line-count delta, no diff, no "N lines removed" note —
just the field that was intentionally changed, reported as if it were the only thing that
changed. `_verify_amend` cannot see this either (H6 confirmed): it checks only that
`got[0][field] == want`; it asserts nothing about any other line in the document, so a
comment — or, by the same mechanism, a blank line, or any other content that fails to match
`ITEM_ID_RE`/`SIBLING_KEY_RE` — sitting between the amended field and the next real key is
deleted with the tool's own success channel actively vouching for the write. **This is
must-fix: high.** It is the same failure class (`AMENDED` at exit 0 while something the
operator did not ask to touch is destroyed) the whole cycle's remedies exist to close, and nothing
in the receipt or the identity check detects it.

## Item 4 — `--show`/`--value-file` shape asymmetry (V6): still a live interaction trap

`--show` prints the FULL field block **including the `field:` key line** (plan-merge.py:1118,
`sys.stdout.write(block ...)` where `block = "".join(lines[first:last])`); `--value-file` reads
the bare **value**, with no key line, per `_render_field`'s contract. The two flags' `--help`
text uses different words for this ("block" vs "value") but nothing states the shapes are
incompatible, and the natural read-then-replace workflow the tool otherwise encourages (`--show`
to learn the hash, then feed a value back) invites exactly the naive pipe-through.

I reproduced it (Evidence #5): captured `--show`'s block for `verify: run the thing`, stripped
only the `sha256:` trailer (the one line an operator would obviously exclude), and fed the rest
back as `--value-file`. Result: **exit 0**, `AMENDED tasks:T-01.verify`, and the field now reads
`verify: '    verify: run the thing'` — a self-referential string embedding the key name and
original indentation. **The V3 identity check does not catch this**, and cannot in principle:
the corrupted value IS byte-for-byte what the operator supplied as `value_text`, so `want`
equals `got[0]['verify']` exactly. The check protects against the tool re-forming or
mis-locating a value; it has no opinion on whether the value the operator handed it was the one
they meant. **must-fix: high**, independent of V3 — this is a second, still-open route to a
silent wrong-value write at exit 0, discovered by using the tool's own two flags together in
the way their descriptions invite.

## Evidence log

1. `title: [unclosed` base, real replace → exit 8, `"the plan on disk does not parse..."` +
   PyYAML's `in "<unicode string>"` (no path either way).
2. Pre-existing duplicate `T-01` under `tasks:`, real replace → exit 5, `"T-01 appears 2
   time(s) under tasks:..."`.
3. Nested `checks: {verify: ...}` beside top-level `verify:` → `--show` silently returns the
   nested line at exit 0; a subsequent replace correctly refuses at exit 5, `"does not reload
   as written... asked for: 'run the corrected check' reloads as: 'the real top-level verify'"`,
   plan file unchanged.
4. `title:` + a comment line + `verify:` → replace of `title` → exit 0, `AMENDED
   tasks:T-01.title`, comment deleted from disk.
5. `--show` block for `verify:` piped (minus the `sha256:` line) into `--value-file` → exit 0,
   `AMENDED tasks:T-01.verify`, field now `'    verify: run the thing'`.

## Open questions

- Q1 (blocking on the panel's FAIL/PASS call, not on me): items 3 and 4 each reproduce a
  silent wrong-value write at exit 0 that V3's identity check does not and structurally cannot
  catch (item 3: the check only compares the ONE named field; item 4: the corrupted value is
  exactly what was asked for). Does code-review want to independently confirm these are real
  gaps in `_verify_amend`'s guarantee rather than message-layer artifacts? I read the check's
  logic (plan-merge.py:334-348) but a second reader of the splice mechanism would strengthen
  this.
- Q2 (non-blocking): item 2b (nested-mapping mis-bind on `--show`) is a location mis-bind V1's
  docstring claims to have closed ("BLOCK-SCALAR AWARE... found independently by three
  readers"). Is a nested mapping in scope for that fix, or a distinct defect class the panel
  should track separately? I did not find test coverage for it either way.

## Files touched
None in the reviewed worktree — read-only. Scratch fixtures under `/tmp/uirev-bug1128-*/`,
outside any tracked tree.
