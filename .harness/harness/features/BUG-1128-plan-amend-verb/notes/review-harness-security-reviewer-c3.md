# Security review — BUG-1128 `amend` verb — panel c3 (review_sha `20775866`)

## BLUF

Attacked the four specific mechanisms the dispatch named, on live `/tmp` copies, not arguments.
**Zero exit-0 corruption paths found.** Every attempted splice-boundary attack, CAS race, and
`--value-file` structure-injection either (a) landed correctly and safely, or (b) was refused
before any byte touched disk. The two remaining defects are unchanged carry-forwards from the
c2 panel (BLOCK_HEAD_RE header-order gap, `--value-file` open() crash) — both still live,
both still fail-closed, both still non-corrupting. `PASS`.

## Scope

In scope: items 1–6 as assigned (splice integrity, CAS, identity-check branch derivation,
`--value-file` structural injection, path/symlink handling, secrets). **Out of scope, and why:**
`check-state.sh` and the mutation-suite claims are QA's per the dispatch's own constraint
("other members run only targeted probes"); N2 (test tautology)/N4 (code grades)/N5 (schema
branch coverage) are code-reviewer/QA lenses, not mine — though my live probes incidentally
produced behavioral evidence that `_verify_amend` is NOT a no-op (see item 3), which QA's
mutation work can use as a floor, not a substitute for it.

All experiments: `/tmp/secc3/repo/.harness/harness/features/BUG-90{01..10}-*/plan.yaml`, built
fresh, never the real FEAT-46 plan or any tracked file. Safe to discard.

## Item 1 — splice integrity — SAFE, both sides of `comments_are_document` measured

The dispatch asked specifically to attack the side the author did NOT already fix (the block
side, `comments_are_document=False`, was the author's self-caught bug). Attacked the plain-
scalar side (`=True`):

- **Case A** (`BUG-9001-a`): a two-line plain-scalar fold ending in a comment, then a sibling
  key. Ground truth (`yaml.safe_load`) folds the two lines and ends there. `--show` matches
  exactly. An identity replace round-trips; the comment **survives** untouched after the splice
  (`grep` the post-write file: `# a comment ending the fold` present, unchanged position).
- **Case C** (`BUG-9003-c`): a run of blank/comment/blank/comment lines trailing the fold.
  `_trim_tail`'s backward walk correctly strips all four, `--show` matches ground truth, and
  the identity replace leaves **all four trailing lines intact** post-splice.
- **Case B** (`BUG-9002-b`) — the dispatch's exact shape, "continuation lines followed by a
  comment that is itself followed by more continuation-looking text": constructed it, then
  checked `yaml.safe_load` ground truth **first** — it is a `ParserError` (comments always
  terminate a plain-scalar fold in real YAML, so anything after one that isn't a new key is
  invalid YAML — there is no valid document shape matching the dispatch's concern). `--show`
  does mis-report (folds the comment and the trailing text into the printed value — a known,
  already-flagged misleading-read class), but a write attempt hits `transform`'s
  `yaml.safe_load(raw)` gate **before** any splice and refuses at **exit 8**, file byte-
  identical (md5 confirmed). This closes the class structurally, not by luck: the only way to
  make the locator's tolerance-of-comments matter is to build a document that is already
  invalid YAML, and invalid bases never reach the splice.
- **Case J** (`BUG-9010-j`): re-confirmed the author's OWN fix (block-scalar side) still holds
  — a `#`-shaped line that is CONTENT inside a `verify: |` body is preserved verbatim by
  `--show`, matching `yaml.safe_load` ground truth exactly. No regression.

## Item 2 — compare-and-swap — SOUND, under-lock re-check proven to use fresh bytes

- **Case D** (`BUG-9004-d`): captured a hash for `T-24.title`, then — between read and write —
  inserted an unrelated task (`T-02`, 8 extra lines including a 4-line block scalar) *before*
  `T-24` in the file, shifting every subsequent line number, while leaving `T-24.title`'s bytes
  (and hash) unchanged. Replayed the original hash. The write landed correctly at the **new**
  offset; `T-01`/`T-02` (including the inserted block scalar) are byte-for-byte untouched. This
  is not an argument from reading `transform` — it is direct proof the under-lock path
  re-derives `_item_range`/`_field_block` from the freshly-read `base_bytes`, not from anything
  computed before the lock.
- **Case I** (`BUG-9009-i`): a legitimate concurrent write changes `T-24.title`; a stale caller
  retries with the pre-change hash → refused at **exit 6**, exact expected-vs-actual hashes
  named, file left at the legitimate writer's value. Matches c1's finding, reconfirmed at this
  pin.
- **Case E** (`BUG-9005-e`): file truncated to 0 bytes between read and write (worst-case
  "replaced" simulation). Replay with the old hash → refused at **exit 3** ("vanished... under
  the lock"), and the tool writes nothing (file stays 0 bytes, not corrupted further).
- **Symlink/traversal**: a `plan.yaml` that is itself a symlink resolving outside any features
  tree, and a `--file` argument containing `../../../../etc/hosts`, both refused at **exit 9**
  with the resolved path named. `require_destination`'s realpath check runs once and every
  subsequent open uses the resolved string, not the original argument.
- **Residual TOCTOU**: the only theoretical window is an attacker swapping the filesystem entry
  at `resolved`'s own directory *during* this single process's execution, between the realpath
  call and the final `os.replace`. That requires write access to the same directory the trusted
  invoking agent already has full authority over — same trust level as the caller, not a
  privilege boundary. Rated realistically: **low**, unchanged from c1's assessment, and
  `os.replace` still makes the final write atomic regardless.

## Item 3 — `_verify_amend`'s `want` derivation — safe by construction, not just by test

`want`'s branch selector (`BLOCK_HEAD_RE.match(cur[f2])`, in `transform`) and `_render_field`'s
own branch selector (`BLOCK_HEAD_RE.match(original[0])`, where `original[0] == cur[f2:l2][0]`)
read the **identical list element** with nothing mutating `cur` between the two reads. They
cannot structurally diverge — this is stronger than a test could show, since no input can reach
a code path that reads a different value at that index. Exercised behaviorally too: **Case G**
(`BUG-9007-g`, the still-live BLOCK_HEAD_RE gap, see below) mis-binds `--show` to the wrong
block, and the follow-on write is refused at exit 5 with the check correctly comparing "asked
for" vs "reloads as" — direct behavioral proof `_verify_amend` is not a no-op, complementing
whatever QA's mutation suite finds about the *test*'s pinning (separate question, not mine).

## Item 4 — `--value-file` cannot forge structure — 10 probes, zero structural injections

Ran five value-file shapes (column-0 `approval:`-mapping-shaped text, a `---` document
separator, an embedded `\x00`, a lone `\r` with no `\n`, and a body whose dedented form
re-parses as its own two-key mapping) against **both** a plain-scalar target (`title`) and a
block-scalar target (`verify: |`) on `BUG-9008-h`.

**9 of 10**: wrote successfully (exit 0), and in every case `yaml.safe_load` of the result shows
`doc.keys() == ['schema','feature','tasks']` and `task.keys() == ['id','title','verify',
'status']` — **no `approval:` key, no sibling key, ever created.** The plain-scalar path routes
through `_field_lines`/`safe_dump`, which quotes/escapes as needed (double-quoted with `\n`
escapes for the `approval:`-shaped text; single-quoted continuation for the CR-derived text).
The block-scalar path re-indents every line explicitly (`body_indent` prefix, blank lines as
bare `\n`) regardless of what the line itself contains, so a value can never emit a column-0
line inside a `|` body — structurally can't dedent below the block's own indentation.

**1 of 10** (NUL byte into the block-scalar target): the verbatim splice embeds the raw `\x00`
uncontrolled, producing genuinely invalid YAML (`unacceptable character #x0000`). **Caught and
refused at exit 5** by `_verify_amend`'s post-splice reload — not by the renderer. File
untouched (confirmed). Worth recording as INFO: this shows `_verify_amend` is load-bearing for
a *third* failure class (invalid-scalar-content) beyond the two it was built for (wrong-field,
re-formed value) — if that check were ever weakened, this exact input would write unparseable
YAML at exit 0. Not a live gap today; a coupling worth knowing before anyone touches that check.

The lone-CR case also surfaced a non-security data-fidelity note: `open(value_file,
encoding="utf-8")` (no `newline=''`) applies Python's universal-newlines translation, so a raw
`\r` in the value file silently becomes `\n` before it ever reaches the renderer. Harmless here
(still safely quoted/escaped either way) but worth knowing if a future caller needs byte-exact
value-file fidelity.

## Item 5 — path/file handling — rated for a trusted-agent caller, per the dispatch's framing

- Symlink and `..`-traversal refusals: exit 9, both confirmed above (item 2).
- `--value-file`/`--file` open with no validation is realistically fine: the same principal
  supplying the flag supplies the whole command line and already has full filesystem authority
  — no privilege boundary crossed by letting it read/write within that authority.
- **Carried forward, unchanged, still live**: `with open(args.value_file, encoding="utf-8")`
  (`plan-merge.py`, `cmd_amend`) is still unwrapped. Reproduced live at this exact pin: a
  missing path, a directory, and non-UTF-8 bytes each crash with an **uncaught Python
  traceback at exit 1** — outside the tool's own documented vocabulary `{0,2,3,4,5,6,8,9}`.
  This is `plan-merge-test-panel c2`'s Finding 3, explicitly triaged non-blocking then
  ("fail-closed... not worth a cycle of its own") — confirmed the file is **never touched** in
  any of the three cases (the `open()` runs before `locked_update`). Still true. **MED**
  (contract/availability, zero corruption) — not new, not escalating, carried at its prior
  rating since nothing has changed.
- **Carried forward, unchanged, still live**: `BLOCK_HEAD_RE` (`^(\s*)([A-Za-z_][\w-]*):\s*
  ([|>][+-]?\d*)\s*$`) still only matches chomp-then-digit order, never `|2-`/`>3+`. Reproduced
  live (**Case G**, `BUG-9007-g`): `--show --field title` on a task whose `verify: |2-` body
  contains a `title:`-shaped line prints the WRONG block (misleading read, exit 0). The
  follow-on write with that hash is refused at **exit 5** — `_verify_amend` catches it every
  time, file byte-identical (confirmed). **MED** (misleading read, fail-closed write) — carried
  at its c2 rating, unaddressed but non-corrupting.

## Item 6 — secrets/PII

Grepped the full diff (`fe5c5b57~1..20775866`, both files) for credential-shaped strings
(password/secret/token/api-key/credential/bearer/private-key markers) — zero matches. Refusal
and `--show` messages do echo field values, ids, and hashes verbatim (e.g. `asked for:
'Malicious Title'`) — acceptable here specifically because `AMENDABLE_KEYS` is `(tasks,
decisions)` only, `approval:` is structurally unreachable (confirmed direct at exit 2, and
indirectly across all 10 item-4 injection probes — none ever produced an `approval:` key), and
the plan schema carries no credential-shaped field for either key. Nothing this verb touches is
ever a secret.

## Verdict basis

No exit-0 corruption, no CAS bypass, no structural injection, no reachable `approval:` write —
across every mechanism the dispatch named, measured rather than argued. The two carried-forward
MED items are unchanged, already triaged non-blocking by the c2 panel, still fail-closed today.
`severity_max: med`, `must_fix: []`.
