# REUSE angle — FEAT-104 cycle 10 simplify — PF-C10-01 fix delta

## BLUF
**Leave it.** The fix reuses the existing `_head(...)` convention correctly (23 pre-existing
call sites, matched exactly), does not repeat the sorted-repr-join idiom often enough (2
occurrences, not the 3+ threshold that would justify a shared formatter), and its one literal
duplication (the schema path string, spelled 3 times) is deliberate — the reader-facing message
must name an openable path independent of how the validator resolved it at runtime. No helper is
warranted; the two new blocks are near-identical in shape but carry materially different remedy
sentences, and the only shared residue is `_head(...)` plus a two-line sorted-repr join that is
already exactly as small as any helper wrapping it would be.

## Q1 — does `check-domain.sh` already carry a keyed-problem helper, and does the fix use it?
Yes: `_head(text)` at `check-domain.sh:1295` (closure over `VERB`/`display`/`rel`, returns the
head sentence line). Pre-existing call count (excluding the two new lines): **23** — lines 1306,
1325, 1328, 1337, 1394, 1523, 1571, 1580, 1608, 1679, 1732, 1755, 1762, 1769, 1774, 1790, 1801,
1808, 1815, 1832, 1852, 1889, 1927. Both new lines (`1663`, `1671`) call it with the same
one-arg-sentence signature — the fix matches the established convention exactly, it does not
reimplement or bypass `_head`. There is no sibling helper anywhere in the file for "head sentence
+ keyed remedy line" as a single call — every one of the 23 pre-existing sites pairs `_head(...)`
with its own inline `out.append(f"  ...")` remedy line immediately after, same as the two new
blocks do. That is the file's convention, and the fix matches it.

## Q2 — is `", ".join(repr(key) for key in sorted(...))` repeated 3+ times?
No. Exactly **2** occurrences in the whole file, both inside this delta:
`check-domain.sh:1661-1662` (`_missing_names`, over `_missing_required`) and `check-domain.sh:1670`
(`_names`, over `_offending`, pre-existing — unchanged by this fix, this line's `_offending` set
already existed and was already joined this way before the fix). A file-wide grep for
`", ".join(` turns up only one other user, at `check-domain.sh:988`, over `_advertise` for a
wholly unrelated CLI-permission message with no `repr`/`sorted`. Threshold in the brief is 3+; at 2
occurrences a shared formatter is not warranted, and even if it were, see Q3 — the two call sites
diverge immediately after the join (different labels, different remedy sentences), so a formatter
would only ever wrap the two-line join itself, which is already minimal.

## Q3 — judgement call: duplication worth collapsing, or two different sentences that rhyme?
**Two different sentences that rhyme — not worth collapsing.** The prompt's own framing is
correct and I confirm it against the source: `check-domain.sh:1663-1668` (missing-required block)
and `:1671-1677` (undeclared/evidence-shape block) share `_head(...)` + the sorted-repr join
pattern, but their remedy sentences are semantically distinct — one directs the agent to
"Required step fields are declared in run-state-schema.json; supply each required field"
(`:1666-1667`), the other to the `evidence` escape hatch and its lowercase-identifier/scalar
vocabulary (`:1673-1676`). A shared helper would need `head_text`, `label` ("missing key(s)" vs
"offending key(s)"), `keys`, and the full remedy sentence as separate parameters — at which point
the helper's body is `_head(head) ; f"  {label}: {join}. {remedy}"`, i.e. it saves nothing over
the two inline `out.append` pairs already there, while adding an indirection a reader must jump to
in order to see either sentence in full. Not worth it.

## Q4 — does the fix restate the schema-path constant, and is that a genuine reuse finding?
The literal string `run-state-schema.json` appears **4** times in the surrounding block:
- `check-domain.sh:1621` — computed: `_schema_path = os.path.join(sys.argv[3], "run-state-schema.json")` (join input, not message text)
- `check-domain.sh:1667` — message text, missing-required remedy (new)
- `check-domain.sh:1674` — message text, undeclared/evidence remedy (unchanged by this fix)
- `check-domain.sh:1682` — message text, the `except` branch's failure message (unchanged by this fix)

Of these, only line 1667 is new in this delta; 1674 and 1682 already existed before the fix and
already repeated the same literal. **Not a genuine reuse finding.** The three message-text
occurrences are deliberately not derived from `_schema_path` (`sys.argv[3]`-relative, a caller-
supplied absolute directory at runtime) because the message must name a path the human reader can
open from the repo root regardless of which worktree or invocation resolved `_schema_path` at
runtime — printing `_schema_path` itself would leak a worktree-relative or CLI-argument-dependent
string instead of the stable repo path a reader actually needs to open the file. This is the same
display-path-vs-match-path distinction already documented at `check-domain.sh:1296-1303` for
`_head` itself (worktree-stripped display vs. match path) — the codebase already treats
"path used for I/O" and "path named in reader-facing prose" as legitimately different strings.
Cost of the current state: if the schema file's location within the repo changes, three string
literals need updating instead of one — but this pattern already existed for 2 of the 3
occurrences before this fix, is now one instance larger, and remains a plain grep-and-replace risk
class already tolerated everywhere else `_head`-adjacent prose references a path constant. Not
worth introducing a module-level constant inside the embedded-Python-in-shell block for a single
added literal.

## Backlog notes (advisory, out of scope for this delta)
- BACKLOG: the pre-existing repetition of the schema-path literal across `:1674` and `:1682`
  predates this fix and is untouched by it; a module-level `_SCHEMA_REL = "run-state-schema.json"`
  inside the embedded block would need `os.path.join(".claude/skills/harness/bin", _SCHEMA_REL)`
  reconciled against the runtime `_schema_path` build at `:1621` too — out of scope here per the
  dispatch (anything outside the two-file delta is a backlog note, not a finding).

## Verification
`git -C /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-104-strict-digest-schema status --porcelain` → **empty output** (clean tree), observed both before and after this read-only review. No writes were made to any file; no scratch probes were needed for this angle (static grep/read only).
