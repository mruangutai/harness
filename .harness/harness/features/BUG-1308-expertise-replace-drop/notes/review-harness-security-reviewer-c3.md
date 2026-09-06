# Security review — BUG-1308 expertise-replace-drop — cycle 3 (final)

Pin graded: `5942e34e82cf84fd127ff496fdb64202ad647ba6`, read via `git show <sha>:<path>` and
independently confirmed byte-identical to the worktree's current `expertise-merge.py` /
`harness_merge.py` (`git diff 5942e34e..HEAD --stat` touches only `feature.json`). All findings
below are execution-based: a full copy of `expertise-merge.py` + `harness_merge.py` at the pin was
run against fresh fixtures under `$TMPDIR` (no repo file touched — see `git status --porcelain` at
the end).

## Verdict: FAIL (high) — one genuine, execution-proven must_fix in Task 2's target-grammar gap

## Task 1 — structured-content injection (VL-01/VL-05 lineage): **CLOSED, confirmed**

Ran every case the dispatch named against a live fixture, then re-parsed the resulting file with
the tool's own `parse_expertise`:

| input | exit | file changed | re-parsed Patterns count |
|---|---|---|---|
| lone `\u2028` as whole entry | 0 | yes | 2 (correct — no forgery) |
| trailing `\u2028` after text | 0 | yes | 2 (correct) |
| empty string `""` | 0 | yes | 2 (correct) |
| leading `\u2028` + trailing text | **12 MALFORMED** | no | — |
| each of `\v \f \x1c \x1d \x1e \x85 \u2028 \u2029`, **leading** position | **12 MALFORMED**, every char | no | — |

Confirmed directly in Python that for all 8 documented separator characters, `lone`/`trailing`
give `len(value.splitlines()) == 1` (accepted) and `leading` gives `== 2` (rejected) — the guard's
behaviour matches `str.splitlines()` exactly, character for character, in every position tested.
A lone/trailing separator that slips through cannot forge anything: when the whole file is later
re-split by `.splitlines()`, it produces one extra **empty** physical line that matches neither
`SECTION_RE` nor `ENTRY_RE` nor the continuation-line rule, so it is silently discarded by the
parser — never a forged header, entry, or cap crossing. No reclassification observed in any case.

`check-expertise.sh` (`:73` — `open(path, encoding="utf-8").read().splitlines()`) uses the
**identical** Python `str.splitlines()` call `parse_expertise` uses — confirmed by reading its
embedded script. There is no three-way divergence between the op validator, the tool's own
parser, and the downstream format checker; VL-05's fix (share one definition of "a line") holds
for the actual consumer, not just for the writer's own round-trip.

**VL-01: CLOSED. VL-05: CLOSED.** (A markdown *renderer* outside this codebase, e.g. GitHub's
preview, might still treat NEL/PS/LS differently than Python — noted as environment-level
residual, info-only, since it is outside every consumer this tool actually has.)

## Task 2 — target/path integrity: **NOT closed — must_fix, high**

`_validate_target_section` (`expertise-merge.py:191-203`) checks only: non-empty, `str`, single
physical line (`_reject_multiline`). It never checks `target` against `ENTRY_RE`'s id grammar
(`^[A-Za-z]{1,3}-\d+$`, `:43`) — the one place in this file that grammar is spelled — even though
SPEC §5.3 and DEC-219 both describe `target` as *the entry id itself* ("keyed on section plus
entry id, both required"). Confirmed by grep: `ENTRY_RE` is referenced exactly once, inside
`parse_expertise`; never inside op validation.

**Demonstrated A — silent, permanent entry loss.** `add target="PPPP-1"` (4 letters, exceeds the
`{1,3}` cap) is accepted (exit 0, `ADDED PPPP-1`) and rendered verbatim as
`- PPPP-1: malformed id grammar test`. Re-parsing that same file with the tool's own
`parse_expertise` does not recognize it (`ENTRY_RE` requires ≤3 letters) — it is invisible to
`base_sections`. Running a **second, entirely unrelated** op (`replace G-01` in a different
section) on the same file causes the render step to rebuild every section from parsed
`base_sections` plus applied ops, and — since `PPPP-1` was never in `base_sections` and no op
named it — it is **silently dropped from the file entirely**, with no refusal, warning, or
outcome line. Verified end to end (`driver3.py`): add PPPP-1 → file contains it → unrelated
`replace G-01` → PPPP-1 is gone, file otherwise correct.

**Demonstrated B — a crafted target forges a real duplicate id, then permanently locks it.**
`add target="P-01: fake prefix"` (still a single line, still non-empty, so it passes every
existing check) is accepted (exit 0, `ADDED P-01: fake prefix`) because `_resolve_add`'s
duplicate check compares the **opaque raw target string** against existing ids — `"P-01"` ≠
`"P-01: fake prefix"` — not what `ENTRY_RE` will actually extract once the line is written and
re-read. The rendered line is `- P-01: fake prefix: real entry text`; `ENTRY_RE` parses this back
as id **`P-01`** — the same id as the pre-existing `- P-01: existing pattern one.`. The file now
genuinely re-parses with a duplicate `P-01` (confirmed: `parse_expertise` returns two `P-01`
tuples). A subsequent, entirely legitimate `replace target="P-01"` then hits
`_check_base_ambiguity` and is refused at **exit 11** ("the id appears 2 times") —
**permanently**, since nothing exposed by this tool can disambiguate the two entries again; only
a human hand-editing the raw file outside the tool recovers it.

Both outcomes are exactly what the dispatch asked to prove or drop; both are now proven, not
theoretical, and reproduce on a fresh fixture every time (`driver2.py`, `driver3.py`,
`driver4.py`).

**Severity: high, must_fix.** Attacker capability assumed: ability to author one
`expertise_update` op — the exact untrusted-JSON-from-an-LLM-agent threat this review is scoped
against. Impact: permanent, tool-mediated denial of correction for a specific governed Expertise
entry (a file injected into every future spawn of that agent) plus silent, unannounced loss of any
entry added with a malformed id. This defeats VL-03's cycle-1 fix (duplicate-id ambiguity
detection, closed at `3488ca38`) through a new vector this cycle's `ops` subcommand introduces —
`cmd_apply`'s pre-existing path cannot reach this, because there `id` only ever comes from
`ENTRY_RE`'s own match on the proposal text, so it is grammar-constrained by construction; `ops`'s
new `target` JSON field is not.

**Fix shape** (not applied — read-only review): anchor-match `target` against the same
`[A-Za-z]{1,3}-\d+` grammar `ENTRY_RE` already spells, at the same Step-A gate
`_validate_target_section` already occupies, refusing at exit 12 on failure. This closes both
demonstrated paths at their shared root cause.

## Task 3 — atomicity / fail-closed (REQ-06): **PASS, confirmed**

For each of exit 8 (cap, 15→16 Patterns via a 15-op batch), 10 (missing target), 11 (proposal-level
duplicate target), and 12 (malformed verb) — in every case with the refusing op placed **last** in
a multi-op batch whose earlier ops would otherwise have applied — sha256(file) before == after,
every time. `locked_update` only reaches `tempfile.mkstemp` after `transform()` returns without
raising; a `MergeRefusal` inside `transform` is re-raised before that line, so no temp file is ever
created on any of these four paths. The only new filesystem entry after each refusal is the
`.lock` file, which `harness_merge.py`'s own docstring documents as intentionally never removed
(flock has no stale state) — not a stray artifact.

## Task 4 — destination guard: **PASS, confirmed**

`cmd_ops` calls the identical `require_expertise_destination` → `harness_merge.require_destination`
`cmd_apply` uses; no `ops`-specific bypass exists. Verified by execution, target file byte-identical
before/after in all three cases:
- plain non-Expertise absolute path → exit 9, nothing written.
- `.harness/expertise/../../outside/secret.txt` (`..` traversal whose realpath resolves outside
  both legal tiers) → exit 9, `outside/secret.txt` untouched.
- `.harness/expertise/harness-symlinked.md` (syntactically legal tail) as a symlink whose realpath
  resolves to `outside/secret.txt` → exit 9, target file untouched — the realpath-based check
  defends exactly as its docstring claims.

## Task 5 — information exposure: **advisory (low), not gating**

No refusal path (7, 8, 9, 10, 11, 12) can smuggle a literal newline: every field that gets echoed
(`target`, `entry`) is validated single-line for **every** op in Step A, before Step B/C ever
construct a message that echoes them — confirmed no forged distinct `APPLIED`/`ADDED`/etc. line is
reachable through a real line break.

Found instead: exit 7 (`CONFLICT`, reachable via `add` against an existing id with different
text) echoes the attacker-controlled `entry` **verbatim, unsanitized**, to stdout
(`_resolve_add`, `f"  proposed text: {entry}"`). Demonstrated: an entry containing
`\x1b[31m…\x1b[0m \x1b[2K\x1b[1A` (color + erase-line + cursor-up — none of which are in the
recognized separator set, so all pass the single-line guard) is written raw to stdout on refusal.
This can visually rewrite a preceding line in a live terminal, or fool a downstream consumer that
substring-scrapes stdout instead of routing on the documented exit code (this tool's own docstring:
"Exit codes are part of the interface… T-07 routes an agent's behaviour on them").
Not new to this diff: `cmd_apply`'s pre-existing, unrelated conflict path builds its `CONFLICT`
lines with the identical unsanitized-echo shape (`f"  proposed text: {prop_txt}"`) — this diff's
`_resolve_add`/`cmd_ops` reproduces rather than introduces the pattern, and a real fix (escaping
non-printables in every refusal-line interpolation) belongs in the shared `harness_merge.py`
layer, wider than this feature's own scope. Graded low/advisory, tagged `bug`, backlog — not
gating this ship.

## git status --porcelain (this session, worktree root)

```
 M .harness/harness/features/BUG-1308-expertise-replace-drop/observations/harness-pm.md
?? .harness/harness/features/BUG-1308-expertise-replace-drop/notes/research-BUG-1308-expertise-replace-drop-goalcheck-sc-c3.md
?? .harness/harness/features/BUG-1308-expertise-replace-drop/notes/review-harness-qa-c3.md
?? .harness/harness/features/BUG-1308-expertise-replace-drop/notes/review-harness-ui-reviewer-c3.md
```
All three entries are concurrently-running sibling reviewers' own artifacts, not mine; I made no
edits inside the worktree. All reproductions ran against copies under `$TMPDIR`
(`/var/folders/.../T/bug1308sec/`).
