# Review — harness-code-reviewer — FEAT-32 — c0

**Verdict: FAIL.** One demonstrated CRITICAL: `check-domain.sh`'s D-10 approval guard (both limbs) is
bypassed by a governed agent's `Edit` — proven live against the real repository's own
`plan.yaml`, exit 0, no stderr, resulting file parses as a forged approval. This is the exact
class REQ-11/D-10/SC-21 exist to close, and no other layer catches it (D-10 itself says layer 2 is
unreachable via `Edit`). Everything else reviewed is sound or is an already-accepted residual.

All line numbers are `git show 5107efb:<path>` line numbers. All "confirmed" claims below were
executed against the pinned SHA's actual code (working tree verified byte-identical to 5107efb for
every file cited, via `git diff 5107efb -- <path>`, except `feature.json` which nothing here touches).

## 1. CRITICAL — the approval guard's indent-based limb B is defeated by re-indenting the block

`check-domain.sh:606` (limb A, exact substring) and `:610-629` (limb B). Limb B's second check
(`:617-629`) reads the child indent **once**, from whatever the on-disk children currently use
(`_child_indent`, `:486`), and only flags a `new_string` line that reproduces a known child key
**at that same indent**. Limb A only denies when `old_string` is itself a substring of the
on-disk approval block.

**Defeat:** an `Edit` whose `old_string` starts *inside* the approval block but extends *past* its
end into the next top-level key, and whose `new_string` reproduces the same keys **re-indented
consistently** (2→4 spaces), satisfies neither limb:
- Limb A: `old_string` includes the trailing key (e.g. `lanes:`), so it is not a substring of
  `on_disk_block` (which stops before it) → no denial.
- Limb B sub-1: `new_string` contains no line starting with `approval:` → no denial.
- Limb B sub-2: `new_string`'s reindented lines have indent 4, `ind` read from disk is 2 →
  `(len(nl)-len(nl.lstrip())) != ind` is true for every line → skipped → no denial.

**Demonstrated, not hypothesized.** Ran the real `check-domain.sh` against FEAT-32's own committed
`plan.yaml` (`.harness/harness/features/FEAT-32-concurrent-write-merge/plan.yaml`), as `harness-pm`:

```
old_string = "  status: approved\n  approved_by: operator\n  date: 2026-08-22\n\nlanes:"
new_string = "    status: REVOKED\n    approved_by: attacker\n    date: 2026-08-22\n\nlanes:"
```
Result: **exit 0, empty stderr.** Applying the same substitution to the real file content and
loading it with `yaml.safe_load` gives:
```
approval: {'status': 'REVOKED', 'approved_by': 'attacker', 'date': datetime.date(2026, 8, 22)}
```
a fully valid, semantically forged approval mapping — not corrupted YAML, an actually-usable forgery.

**Why this isn't the already-known set.** Cases 5a–5e in `test-check-domain.py` (targeted, mid-line,
`replace_all`, block-introduction, task-body) never construct an `old_string` that crosses the
block's boundary, so limb A's "substring of on_disk_block" test is never exercised at its actual
failure mode; none reindents, so limb B's fixed-indent assumption is never exercised either.
`test-check-domain.py`'s BRIEF/PLAN.md cases (12–13) use `_fire_write` only — there is **no** `Edit`
coverage at all for the markdown-heading fragment, a related but separately-untested gap (BRIEF.md's
own fields sit at indent 0, so `_child_indent`'s `l[:1].isspace()` requirement means limb B's sub-2 is
already permanently inert there; limb A alone is what protects BRIEF/PLAN.md, and it does, for a
direct non-boundary-crossing edit — I did not find a working bypass there, but did not exhaustively
search it either).

**Impact.** `harness-pm` — the persona this feature exists to stop from touching its own approval —
can flip `plan.yaml`'s `approval.status` (and `approved_by`, `date`) via one `Edit` call, silently.
D-10 states plainly that layer 2 (`plan-merge.py`'s parse-and-compare refusal) is **unreachable** by
an agent using `Edit` directly, so there is no second chance. SC-21 claims "each payload shape is
asserted individually" for exactly this guard, but the shape that actually defeats it was never in
the corpus — the automated SC passes today because it was never asked the discriminating question,
not because the guard holds.

**Class:** this is precisely the concurrent/adversarial-write defect class FEAT-32 exists to close,
now reopened one layer up (a governed agent silently owning a signature only the main session may
hold), which is why I rank it critical rather than high.

`must_fix`. Refs: REQ-11, D-10, SC-21.

## 2. MED — `inflight_registry.release()` crashes on a schema-valid-but-malformed claim, leaking it until TTL

`inflight_registry.py:206`: `oldest_idx = min(range(len(claims_list)), key=lambda i:
claims_list[i]["started_at"])` — direct bracket indexing. Every other place in this file that reads
`started_at` uses `.get("started_at", 0)` (`_expire`, `:89`). `release()` alone skips `_expire`
entirely and does not tolerate a missing key.

**Demonstrated** (pure function call, no disk write):
```
claims_list = [{'started_at': 100, 'dispatcher':'x'}, {'dispatcher':'y'}]
min(range(len(claims_list)), key=lambda i: claims_list[i]['started_at'])
→ KeyError: 'started_at'
```
This propagates out of the `harness_merge.locked_update` transform (before any write — the file is
left untouched, consistent with the core's contract) to `validate-digest.py:895`'s
`_reg.release(_root, agent)`, which is wrapped (`:896-901`) — fails open, logged, "it will expire on
its TTL." So this does **not** violate DEC-100 (no block), but it is a real, executable failure that
the code's own comment already half-anticipates for lock contention, and does not anticipate for a
malformed record: **one bad entry blocks release of every other claim for that persona**, not just
the malformed one. Under normal operation nothing ever writes a malformed entry (`claim()` at
`:188` always writes all three keys), so this is unreachable without prior external corruption or a
future schema change — advisory, not exploitable today. The concrete consequence, if it does trigger:
the lead that dispatched the affected persona sees `live_children` (which *is* `_expire`-safe) still
report the completed child as live, and is refused its own return (`validate-digest.py:911-917`,
D-09) for up to `CLAIM_TTL_SECONDS` (3600s) even though that child already reported and finished.

Not must_fix (unreachable under current write paths), but worth a one-line consistency fix
(`.get("started_at", 0)`) given how deliberately the rest of the file already does this.

## 3. MED, unverified hypothesis — same-persona-type collision on the dispatcher key

`inflight_registry.py`'s claim schema has no lead-**instance** identity, only the persona-type
string (`agent_type`, e.g. `"harness-eng-lead"`). D-09's `live_children(root, agent)` filters live
claims by `c.get("dispatcher") == dispatcher` where `dispatcher` is that same type string. Per D-09's
own recorded residual, an orphaned child of an interrupted lead is never released by anyone but
itself. If the orchestrator then dispatches a **fresh** `harness-eng-lead` instance for the same
feature while the old instance's orphan is still running, the new instance's own early return would
be refused by `live_children` matching the **old, unrelated** instance's still-live child — a
false "you have children in flight" naming a child this lead never dispatched.

I could not execute this (it requires simulating an actual interrupted spawn + a respawn of the
same persona type, which a read-only reviewer cannot produce). It is grounded in the code as read,
not demonstrated. Distinct from D-09's two named residuals (stop_hook_active pass-through, the
orphan itself being unrefusable) — this is about a **different, later, unrelated lead instance**
being wrongly refused, which D-09's text does not mention. Flagging as an open question rather than
must_fix given it is unverified.

## Checks that came back clean

- **Root probe (#3).** Both `dispatch-guard.sh:89` and `validate-digest.py:877` (and
  `check-domain.sh`'s pre-existing, unchanged root logic) test `os.path.isfile(.../
  "team-config.yaml")` — the manifest file, never the `.harness` directory. `git diff
  12c66b3..5107efb` shows no new/changed line anywhere touching `isdir` + `.harness`. Registry root
  is taken from payload `cwd` first in both hooks, matching the operator ruling.
- **Merge core (#4).** `harness_merge.locked_update` (`:121`): a `MergeRefusal` or any exception
  raised inside `transform` happens strictly before the tempfile is created (`:143`), so the
  destination is left byte-identical in both cases. `os.replace` failure is caught and the tempfile
  removed (`:148-153`) — no dangling tempfile on an ordinary failure. **Exception:** a `SIGKILL`
  between the tempfile write and `os.replace` does leave the tempfile behind (nothing sweeps it) —
  informational only, not required by any REQ/SC, same shape as every other `os.replace`-based
  writer in this house.
  `require_destination` (`:156`) matches on `os.path.realpath(os.path.abspath(path))` — confirmed
  by reading, consistent with the docstring's dot-dot/symlink claim.
  All four consumers (`plan-merge.py`, `observations-merge.py`, `expertise-merge.py`,
  `inflight_registry.py`) import `harness_merge` and call only `locked_update`/`require_destination`
  — grepped for `fcntl`/`O_EXCL`/`os.replace` in each and found none outside `harness_merge.py`
  itself (SC-11 holds). `inflight_registry.py` has no `require_destination` call, correctly — its
  path is derived from `root` + a fixed relative constant, never from an agent-supplied `--file`, so
  it is not an instance of the exit-9 destination class at all.
- **Fail-open discipline (#2), the parts I could execute.** `inflight_registry._parse` (`:56`)
  returns `{}` and reports on stderr for corrupt JSON, empty bytes, `None`, and a non-object JSON
  value — confirmed by direct call. `dispatch-guard.sh`'s T-08 block wraps both `live_claim` and
  `claim` in one `except Exception` (`:124-130`) that exits 0 — a malformed-registry
  `AttributeError` (tested directly: a persona value that is a string or a list of non-dicts raises
  `AttributeError` in `_expire`) is caught here and passes the dispatch through, loudly. Both hooks'
  manifest-read failures (`check-domain.sh`'s `_approval_entries`, `:409-441`) fail open with a
  named stderr line, matched by existing tests (cases 9/10a/10b in `test-check-domain.py`) — not
  re-reported.
- **Suite.** Re-ran `run-unit-tests.sh --kind integration` at HEAD (== 5107efb for every file this
  review covers): exit 0, 0 lines matching `^FAIL `. Not re-run for `--kind unit` (nothing in scope
  touches `UNIT_SCRIPTS`).
- **Docs/records (SC-12, SC-18, D-10's three-artifact fix).** `harness-spec-driven/SKILL.md:15-18`
  and `harness-expertise/SKILL.md:36-37` each name the merge-tool invocation; neither still
  instructs a bare write. `harness-pm.md`, `harness-orchestrator.md`, and
  `templates/plan.yaml:24-25` all now name the main session as sole signer, consistent with
  `team-config.yaml`'s `main_session.writes` entries. `.gitignore` covers both
  `.harness/.inflight-claims.json` and `.harness/**/*.lock`; `run-unit-tests.sh` and
  `harness.json`'s `integration.detect` both register all five new test files.

## Not re-litigated (per dispatch)

SC-13's deleted counts, BRIEF's "seven" vs plan's "eight", the registry's 1.0s lock timeout vs the
10s file-merge default, the registry root from payload `cwd`, #720/#718, T-07 vs T-08, T-13/T-17
pending status, the five understated task statuses — all confirmed present as described, none
re-raised.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "check-domain.sh's D-10 approval guard is bypassed live by a governed Edit that spans the block boundary and re-indents its children — a real forged plan.yaml approval, exit 0, no stderr, demonstrated against the repo's own file."
  severity_max: critical
  findings: 4
  must_fix:
    - "check-domain.sh:606-629 — limb A (substring test) and limb B (fixed-indent key match) both miss an Edit whose old_string spans past the approval block's end and whose new_string re-indents the block's children consistently; demonstrated live against .harness/harness/features/FEAT-32-concurrent-write-merge/plan.yaml as harness-pm, exit 0, resulting approval mapping parses as {status: REVOKED, approved_by: attacker}. Violates REQ-11/D-10/SC-21."
  spec_violations:
    - { kind: mismatch, path: .claude/skills/harness/bin/check-domain.sh, ref: D-10 }
    - { kind: mismatch, path: .claude/skills/harness/bin/check-domain.sh, ref: SC-21 }
  reviewed: "12c66b3..5107efb"
  human_commits_in_scope: []
  open_questions:
    - { id: Q1, question: "inflight_registry.py:206's release() uses claims_list[i][\"started_at\"] (bracket indexing) instead of .get(\"started_at\", 0) used everywhere else in the file; a schema-valid-but-malformed entry (missing started_at) raises KeyError, caught upstream (fails open, non-blocking) but leaks that persona's whole claim list until CLAIM_TTL_SECONDS. Unreachable under current write paths (claim() always writes a well-formed record) but a one-line inconsistency worth closing.", blocking: false }
    - { id: Q2, question: "D-09's live_children keys only on the dispatcher's persona-TYPE string, with no lead-instance identity. A fresh lead of the same persona type, dispatched after a DEC-131 orphan from an interrupted predecessor is still running, would be wrongly refused on its own return citing a child it never dispatched. Not executed (requires simulating an interrupted spawn + respawn); flagging as unverified.", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-32-concurrent-write-merge/notes/review-harness-code-reviewer-c0.md
```
