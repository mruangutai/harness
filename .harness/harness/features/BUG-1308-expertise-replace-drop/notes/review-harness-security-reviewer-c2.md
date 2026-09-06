# Security review — cycle 2 — BUG-1308-expertise-replace-drop

review_sha `48d2285be7770a7e630b0a11c8136a55b2d351e3`, graded exclusively via `git show <sha>:<path>` — no
plain-file reads. `git diff 48d2285b..HEAD --stat` confirms HEAD differs only by `feature.json`, so this
grading applies unchanged to the pinned tip.

**BLUF: FAIL, severity high.** The lead's prediction P1 reproduces exactly as stated, and is worse in
practice than framed: a single well-formed `replace` op can forge not just an extra entry but a fake
`## Section (max N)` header that reclassifies an entire tail of legitimate entries into a different,
now-over-cap section. REQ-03 ("no operation can leave a section over its cap") is false as delivered.
VL-01's cause — the validator's newline alphabet is narrower than the parser's — was only half-closed:
`\n`/`\r` were blocked, the other 8 of 9 Unicode line-breaking characters `str.splitlines()` recognizes
were not.

## Finding SEC-01 (high, gating, bug) — validator/parser alphabet mismatch still open, REQ-03 still false

`_reject_multiline` (expertise-merge.py ~L170) rejects only `"\n" in value or "\r" in value`.
`parse_expertise` (~L63) splits with `str.splitlines()`, which also breaks on `\v \f \x1c \x1d \x1e
\x85 \u2028 \u2029` (8 of the 9 probed characters — `\t` is the only one that does **not** split).
`render` (~L103) writes `f"- {eid}: {text}"` verbatim. `_check_caps` counts only the in-memory
parsed-list length, never a round-trip through the file that would exist after write.

**Reproduction (P1, exact command run at the pin, in-process, no disk writes — `resolve_ops`/`render`/
`parse_expertise` are documented PURE functions):** load `expertise-merge.py`+`harness_merge.py`
source via `git show 48d2285b:<path>` into in-memory modules, then:
```
base Gotchas = 15 entries (AT cap)
ops = [{"op":"replace","target":"G-08","section":"Gotchas",
        "entry":"harmless text\u2028- G-16: forged additional entry"}]
resolve_ops(base_sections, base_order, ops)
```
**Observed:** `_reject_multiline` does not raise. `resolve_ops` returns `[('REPLACED','G-08')]` (exit 0
in the real CLI). In-memory Gotchas length stays 15 (cap check passes). `render()` writes the U+2028
literally inline in the G-08 line. Re-parsing that rendered text with the tool's own `parse_expertise`
yields **16** Gotchas entries — a phantom `G-16` — i.e. VL-01's symptom, reproduced through a different
character, cap violated in what every consumer (this tool on the next invocation, `check-expertise.sh`,
a human) actually reads.

**Escalated reproduction, cross-section (worse than P1 as framed):** a `replace` on a `Patterns` entry
(14/15, room for one) whose `entry` is `"real text\x0b## Gotchas (max 15)\x0b- G-16: forged..."` (VT,
`\x0b`) — resolves and renders exit-0 exactly as above. Re-parsing shows `Patterns` collapsed to 7 and
`Gotchas` grown to **23** (the forged G-16 plus the 7 legitimate `P-08..P-14` entries, silently
reclassified into `Gotchas` by the injected header). This is not merely a cap breach in the section the
op named — it is instruction reassignment across the file's structure, using nothing the shape
validator refuses.

**Prediction P2 (apply path NOT exploitable this way) — confirmed true**, and it is *why* the gap is
`ops`-specific: an `apply --entries` proposal is parsed via the same `parse_expertise`/`splitlines()`
**before** the cap check runs, so the identical embedded-U+2028 payload becomes its own real parsed
entry at proposal-parse time (verified: `prop_sections == {'Gotchas': [('G-99','harmless text'),
('G-100','forged additional entry')]}`), and the cap check correctly sees 17>15 and refuses at exit 8.
`ops`'s `entry` is instead one opaque JSON string, counted as one list element regardless of what
`splitlines()` would later do to it — the asymmetry is the root cause, not a JSON-specific one.

**Abuse scenario:** any producer of an `expertise_update` ops payload — a compromised/prompt-injected
distilling agent, or a careless one that skips SKILL.md's instructed (not enforced) `check-expertise.sh`
step — smuggles arbitrary extra "governing" bullets, or reclassifies existing ones into a section whose
rules they did not originate from, into a file injected verbatim into every future spawn of that agent
as instructions. `check-expertise.sh` (same `splitlines()` parser) *would* catch this on inspection —
but nothing in `expertise-merge.py` or `inject-expertise.sh` calls it; it is honor-system, run only if
the same agent that just forged the file chooses to run it and to honor a `FAIL`.

**Fix shape (not prescribed, but the gate is what's missing):** `_reject_multiline` must refuse the
same alphabet `str.splitlines()` recognizes, not just `\n`/`\r` — or `_check_caps` must count entries by
round-tripping the candidate output through `render`+`parse_expertise` rather than the pre-render list.

## Finding SEC-02 (info, backlog, chore) — destination check is an unanchored suffix match; pre-existing, unchanged by this diff

`require_expertise_destination`/`harness_merge.require_destination` matches the **realpath's tail**
against `EXPERTISE_TAIL`, with no requirement that the resolved path sit under the actual project
root. Verified by pure path-string computation (no filesystem symlinks touched): a traversal such as
`.harness/expertise/../../tmp/evil/.harness/expertise/harness-pm.md` resolves outside the repo and
still matches — accepted — because it ends in a legal-looking tail; likewise
`/tmp/attacker-controlled/.harness/expertise/harness-pm.md`. `git diff origin/main..48d2285b --
.claude/skills/harness/bin/harness_merge.py` is **empty** — this function is untouched by this feature.
`cmd_ops` calls the identical, already-existing `require_expertise_destination` the `apply` path has
called since FEAT-30/27; the gap (documented by the function's own docstring as deliberately partial —
it checks WHERE, never WHO) is not new and not introduced by `ops`. Matches the already-signed D-01
risk (repository Expertise entry P-03: `inject-expertise.sh` globs any `.harness/<segment>/expertise/`
with no per-repo isolation). Not this cycle's defect; noted so a later reviewer doesn't re-raise it.

## Finding SEC-03 (info, backlog, chore) — JSON-decode-error byte-identity is asserted only by code reading, not by a test

`cmd_ops`'s `transform()` raises `MergeRefusal(12, ...)` on `json.JSONDecodeError` **before**
`locked_update` ever reaches its tempfile-write step (`new_bytes = transform(base_bytes)` raises first)
— byte-identity for this refusal follows by construction, same code path as every other refusal stage.
But unlike stages 7/8/10/11/12(shape) — each covered with an explicit sha256-before/after assertion in
`test-expertise-merge.py` (cases 14, 15, 20, 21, 22, 23, 24) — no case feeds `--ops` a syntactically
invalid JSON blob (only wrong-*shape* JSON, e.g. a digest-mapping wrapper, is tested). Advisory test-
coverage gap for QA, not a security defect: routed as a `chore`, not gating this panel.

## Finding SEC-04 (info, no action) — data exposure and locking: assessed, nothing new

- `CONFLICT`(7) echoes `existing text`/`proposed text`; `MALFORMED OPS`(12) echoes `type(...).__name__`
  and key names — all to stdout, all content the invoking agent already authored (the proposal) or
  already read (the base file via injection). No privilege the actor doesn't already hold (P-02).
  Pre-existing `harness_merge.py` gap (its own docstring, issue #627: checks WHERE a write lands, never
  WHO asked) is unaffected by this diff, since the file is byte-identical to `origin/main`.
- Lock file: `<file>.lock`, `os.O_CREAT|O_RDWR`, default umask permissions — unchanged code
  (`harness_merge.py` diff empty). Gitignored (`.gitignore:46 .harness/**/*.lock`) — never committed.
- Same lock, same path, across `apply` and `ops`: confirmed by code (`locked_update(path, ...)` in both
  `cmd_apply`/`cmd_ops` receives the identical `resolved` value) and by `test-expertise-merge.py`
  case18 (`case_concurrent_writers`), which races an `apply` child against an `ops` child under a
  test-held production lock and asserts neither exits early.

## Per-file record (all seven paths in the batch, at the pin)

| File | Conclusion |
|---|---|
| `.claude/skills/harness/bin/expertise-merge.py` | SEC-01: validator/parser alphabet mismatch reopens VL-01's class via 8 other line-breaking chars; falsifies REQ-03. In scope, gating. |
| `tests/unit/test-expertise-ops.py` | u17/u18 assert only `\n`/`\r` reject; no case for `\v \f \x1c \x1d \x1e \x85 \u2028 \u2029`. Coverage gap, not this panel's gate (QA's domain), noted under SEC-01. |
| `tests/integration/test-expertise-merge.py` | case21/22 same `\n`/`\r`-only coverage; cases 14/15/20/23/24 do assert byte-identity correctly for every OTHER refusal stage; no invalid-JSON-syntax case (SEC-03); case18 corroborates shared locking (SEC-04). |
| `.claude/skills/harness-distill/SKILL.md` | Documents the `ops` mechanism and exit table accurately; instructs `check-expertise.sh` as a step (not enforced elsewhere). Nothing in it instructs an unsafe action — the gap is the tool's, not the instruction's. |
| `.harness/harness/docs/SPEC.md` §5.3 | Describes the mechanism (base-snapshot rebuild, caps checked once on final state) accurately as *implemented* — but the underlying REQ-03 guarantee it documents is false per SEC-01. Nothing here instructs unsafe use. |
| `.harness/harness/docs/DECISIONS.md` DEC-219 | Same: accurate description of the chosen mechanism; makes no claim about the newline/line-separator alphabet either way, so not itself false — the code beneath it is. |
| `.harness/harness/docs/DECISIONS-INDEX.md` row 219 | One-line summary, consistent with the full entry. Nothing in my lens. |

## Threat model

| Boundary | STRIDE | Mitigated |
|---|---|---|
| LLM-authored `ops` JSON → Expertise file injected into every future spawn as instructions | Tampering / Elevation of privilege (content forgery = instruction injection into the control plane) | **false** — SEC-01 |
| `--file` destination vs. project root | Tampering (write outside intended tree) | false, but pre-existing/unchanged (SEC-02), not this diff's gate |
| Refusal-path stdout vs. cross-agent secrecy | Information disclosure | true (no new exposure; actor already held the data) |
| Lock file lifecycle under SIGKILL/crash | Denial of service | true (flock releases on process death; case10 covers this; unchanged code) |

## Open questions
None blocking — the finding is fully reproduced and self-contained.

## Verification statement
Every claim above was executed at the pin, not inferred: `_reject_multiline`, `resolve_ops`, `render`,
`parse_expertise`, and `compute_union` were loaded as real in-memory modules from `git show
48d2285b:<path>` (no disk writes — I hold no Write grant on source and the shell write-guard blocks
file-writing bash regardless of destination, so every repro is a call into the tool's own documented-
pure functions, never a reimplementation). The whitespace-character enumeration table (9 candidates,
8 splitting) was run directly against Python's `str.splitlines()`. The destination-regex probes were
pure string/path computation with no real symlinks. `git diff origin/main..48d2285b --
.claude/skills/harness/bin/harness_merge.py` was run and is empty, supporting the pre-existing/unchanged
claims in SEC-02/SEC-04.

`git status --porcelain` at completion (mine only would be this file, which was untracked before this
write; the other two entries below are concurrent peers' in-flight work in the same worktree, not
mine):
```
 M .harness/harness/features/BUG-1308-expertise-replace-drop/observations/harness-pm.md
?? .harness/harness/features/BUG-1308-expertise-replace-drop/notes/research-BUG-1308-expertise-replace-drop-goalcheck-sc-c2.md
?? .harness/harness/features/BUG-1308-expertise-replace-drop/notes/review-harness-ui-reviewer-c2.md
```
