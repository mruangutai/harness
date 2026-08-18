# QA — FEAT-23, `e527bca` — third-round re-proof of the exit contract

**Verdict: PASS.** Both commissioned mutations pin. No fourth class on the argument axis. One
non-argument path (closed stdout) exits 120, correctly out of scope per the caller-mistake
contract — advisory only.

HEAD confirmed `e527bca` (`git rev-parse HEAD`). All reads pinned there.

## Probe 1 — try/except removal, full suite under mutation

Mutated in worktree `.claude/worktrees/qa-feat23-probe1` at `e527bca` (never the working tree).
Baseline SHA-256 of `board-station.py`: `515c6601...43314a1`.

Removing `try/except ValueError` around `int(issue_arg)` reddens **3 of 11** cases, not just the
over-cap one:
- `rc6=1` for the 4301-digit over-cap string (the commissioned case) — confirmed.
- `rc3=1` (part of the combined "missing argument" check) for `"not-a-number"`.
- `rc4=1` for superscript-2 (`²`).
- `rc5` (Arabic-Indic `٢`) still passes — that class is caught by `isascii()`/`isdigit()`, not by
  the try/except, so it is unaffected by this mutation.

Restore verified two ways: `git diff --exit-code` on the file → exit 0, and SHA-256 after restore
== SHA-256 before (`515c6601...43314a1`, byte-identical). Worktree removed
(`git worktree remove --force`).

## Probe 2 — `issue_arg.isascii()` → `str(issue_number).isascii()` (the description's own wording)

This is the load-bearing check the round exists to re-prove. The commit's own docstring says the
ASCII test runs "on the parsed value"; the code at `:77` does not — `issue_arg.isascii()` reads
the ORIGINAL STRING; only `issue_number <= 0` uses the parsed value.

Mutating to the description's stated version (`str(issue_number).isascii()`) reddens exactly
**one** case: `rc5=0` for Arabic-Indic (`٢`) — **"it moved issue 2's card"**, i.e. the wrong-card
class silently reopens. This converts "the placement looks right" into "the suite pins the
placement" — a genuine discriminating proof, not a description read literally.

Restore verified the same two ways: `git diff --exit-code` → 0, SHA-256 after ==
`515c6601...43314a1` (same baseline, confirming Probe 1's restore *and* Probe 2's restore both
landed byte-identical). Worktree removed.

**Conclusion: the code, not the docstring, is correct — and now measurably so.** (The docstring's
"on the parsed value" claim is itself now suspect prose; worth a one-line fix, not a blocker —
`:33` in the module docstring's EXIT CONTRACT section describes the ASCII check without stating
which string it runs against, so no correction is strictly required there. The COMMIT MESSAGE'S
"on the parsed value" framing is the only place the false claim lives, and it is not something a
test gate touches.)

## Probe 3 — exit-space fuzz (argument axis + one non-argument axis)

Run from a `mktemp -d` directory with no `.harness/team-config.yaml` ancestor — never reaches
`gh_board.set_station` (the hard safety bound).

All rows below are genuine two-argument invocations (`<issue-number> <station>`) — an earlier
pass of this table wrongly dropped the station argument on 8 rows, which meant those runs never
reached `int()` or the conjuncts, only the `len(argv) != 2` gate. Rerun with the station argument
present:

| input | rc |
|---|---|
| `''` (with a station arg present) | 2 |
| whitespace-only `'   '` | 2 |
| `' 42 '` | 2 |
| `'4_2'` | 2 |
| `'+5'` | 2 |
| `'-5'` | 2 |
| `'0'` | 2 |
| `'007'` | **0** — parses to `7` via `int()`, passes `isascii()`/`isdigit()`, is `> 0`: a
  genuinely valid positive integer, so it clears the usage gate and reaches the environmental
  path ("no harness root found above the current directory — nothing written"). Not a rejection. |
| `'٢'` (U+0662, Arabic-Indic 2) | 2 |
| `'²'` (U+00B2, superscript 2) | 2 |
| `'1٢'` (mixed-script — CPython's `int()` DOES accept this, returns `12`; measured directly:
  `python3 -c "print(int('1٢'))"` → `12`) | 2 |
| invalid-UTF-8 argv byte (`\xff`, arrives as lone surrogate) | 2 |
| `'9'*4300` (under cap) | 0 (writes nothing — no harness root above the temp dir, as expected;
  this is the environmental-precondition path, not a rejection) |
| `'9'*4301` (over cap) | 2 |
| 0-argument shape | 2 |
| 1-argument shape | 2 |
| 3-argument shape | 2 |

**`int(' 42 ')` and `int('4_2')` both succeed in Python** — measured directly:
`python3 -c "print(int(' 42 '), int('4_2'), int('1٢'))"` → `42 42 12`. Both `' 42 '` and `'4_2'`
still exit 2 here, but NOT via the `try/except ValueError` — they are rejected by the
`issue_arg.isascii() and issue_arg.isdigit()` conjunct: `' 42 '.isdigit()` is `False` (space is
not a digit), `'4_2'.isdigit()` is `False` (underscore is not a digit). So `isdigit()` is the
conjunct doing the rejecting for these two, not the parse step.

**Corrected claim: not every non-valid-pair input exits 2 — `'007'` is actually a VALID positive
integer (leading zeros do not make it invalid) and correctly exits 0 via the environmental path,
not a rejection.** With that reclassified, no argument-axis input that previously exited 2 now
exits 0, and no argument that should be rejected exits 0. **No fourth class found on the argument
axis.**

### Beyond the argument axis — closed stdout

`board-station.py 326 Plan` with stdout closed before the interpreter's shutdown flush (measured
via `Popen(...).stdout.close()` before `communicate()`, 5 runs from a no-root temp dir):
**consistently exits 120**, with `BrokenPipeError: [Errno 32] Broken pipe` reported during
`sys.stdout` flush at interpreter shutdown. Not 1, not 2 — always 120 across all 5 runs.

Per the dispatch's rating rule: this is a **non-argument** path (closed pipe), outside the
caller-mistake contract the docstring governs. **Advisory, not a blocker.** The remedy, if taken,
is a scoping clause in the docstring ("EXIT CONTRACT governs argument-shape mistakes only; a
consumer closing stdout mid-write is not covered and may exit non-standard"), never a code guard.
No other non-argument path was probed (no import-failure or signal test run — out of scope per
the same rule, and the dispatch names closed-pipe specifically).

## Probe 4 — the two corrections in `harness-simplify/SKILL.md`

**Dangling antecedent:** `git diff 78e87dc..e527bca` shows the sentence changed from "is the same
smell" (previous round's finding — "smell" appeared nowhere earlier in the file, no antecedent) to
"is a sign of the same thing" (`:87`). "The same thing" now plausibly refers back to the altitude
question two sentences earlier (`:83-85`): "is the capability at the right home... Is there one
authoritative statement of a rule... or several that can drift" — a methodology living only in
session prompts is exactly that failure (not at its rightful home, not a single authority). Weak
but present antecedent; "smell" is gone from the file entirely (`grep -n -i smell` — zero hits,
normalized/case-insensitive). Treat this as resolved, not perfectly worded.

**Per-`##`-section surface counts** (re-derived directly, not from T-02's file-global verify,
which cannot see a per-section regression):

| `##` section | plan surface | code surface |
|---|---|---|
| REUSE | 1 | 1 |
| SIMPLIFICATION | 1 | 1 |
| EFFICIENCY | 1 | 1 |
| ALTITUDE | 1 | 1 |

All four sections are exactly 1/1 as expected. No regression.

## check-domain.sh Edit denial in the worktree

Recurred as expected — `Edit` on the worktree copy of `board-station.py` was denied (domain
guard scopes qa to notes/observations paths only, worktree or not). Wrote the mutation via
`Bash`/`python3` instead, as last round; restore verified by SHA-256 + `git diff --exit-code`
both times. Not filed as a new open_question per this dispatch's instruction.

## Coverage note

The standing suite (`test-board-station.py`, 11 cases, all green at HEAD) already encodes both
of this round's discriminating mutations as its own cases 4-r5 (Arabic-Indic) and 4-r6 (over-cap)
— this round's contribution is *proving* those cases actually discriminate against the specific
mutations named in the commit description, not merely asserting the suite's shape looks right.

```yaml
VERDICT: PASS
DIGEST:
  headline: Both commissioned mutations pin (over-cap try/except and ASCII-on-parsed-value); no fourth class on the argument axis; closed-stdout exits 120 and is advisory, out of the caller-mistake contract.
  suite: pass
  failures: 0
  matrix_ok: true
  severity_max: none
  kinds:
    - { kind: unit, state: satisfied, cmd: "python3 .claude/skills/harness/bin/test-board-station.py", named_tests: 11 }
  coverage_gaps: []
  sc_evidence:
    - { id: SC-exit-contract, test: ".claude/skills/harness/bin/test-board-station.py:196-206 (case 4, r5/r6) — proven discriminating this round via worktree mutation, not just present" }
  probe_results:
    probe1_over_cap_mutation: "PASS — try/except removal reddens rc6=1 (commissioned case) plus rc3=1 and rc4=1 (not-a-number, superscript-2); rc5 (Arabic-Indic) unaffected. Restore verified: git diff --exit-code=0, SHA-256 before/after identical (515c6601...43314a1)."
    probe2_ascii_placement_mutation: "PASS — str(issue_number).isascii() (description's stated wording) reddens rc5=0 for Arabic-Indic, silently moving issue 2's card. Confirms the CODE's current placement (issue_arg.isascii() on the original string) is correct and load-bearing; the description's 'on the parsed value' framing is inaccurate prose, not a code defect. Restore verified same two ways, same SHA-256."
    probe3_argument_axis_fourth_class: false
    probe3_note: "First pass of the fuzz table dropped the station arg on 8 rows (measured len(argv)==1 gate, not the parse); rerun with both args present. '007' correctly exits 0 (parses to 7, a valid positive int, environmental no-root path) not 2 -- reclassified as valid input, not a rejection gap."
    probe3_nonargument_findings: "closed stdout -> exit 120 consistently (5/5 runs), BrokenPipeError at shutdown flush. Advisory per the caller-mistake scoping rule, not a blocker."
    probe4_dangling_antecedent: "resolved — 'same smell' (no antecedent) replaced with 'a sign of the same thing', which now points at the altitude question stated two sentences earlier. Weak but present."
    probe4_per_section_counts: "REUSE 1/1, SIMPLIFICATION 1/1, EFFICIENCY 1/1, ALTITUDE 1/1 — all four sections exact, re-derived per-section not file-global."
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-23-ship-flow-fixes/notes/qa-2026-08-18-16-construct-validator.md
```
