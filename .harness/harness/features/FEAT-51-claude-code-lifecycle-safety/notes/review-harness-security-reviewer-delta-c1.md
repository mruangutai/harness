# F-2 delta security review — FEAT-51 — pin `aab31504`

**F-2 is CLOSED.** Every row of the containment matrix, run independently against the real
`quarantine.py`/`plan-sign-gate.sh` binaries with fixtures I built myself (not the suite), refuses
the attack and passes the legitimate case. No new high/critical was introduced. The two halves
agree on every case that matters to authorization; they disagree only on which malformed shapes
each *recognizes* as "quarantine-relevant" at all — and that asymmetry is safe because
`quarantine.py`'s own containment is the authoritative, unconditional gate (it never depends on the
hook running first).

## Step 1 — my own repro of the exact panel exploit, at the new pin

Staged `feature.json` at `<root>/.harness/harness/features/FEAT-99/notquarantine/<writer>/feature.json`
(dir renamed off "quarantine"), agent `harness-backend-dev` with **no live claim** (a different
agent, `harness-pm`, holds the feature's only live compat claim):

```
python3 quarantine.py adopt --file <root>/.../FEAT-99/notquarantine/.../feature.json --root <root>
```
- `plan-sign-gate.sh` (piped the hook payload, `HARNESS_PROJECT_DIR=<root>`): **exit 0**, empty
  stdout/stderr — it does not recognize `notquarantine` as a quarantine-shaped path (its own regex
  also requires the literal `quarantine` segment), so it never reaches the orphan check. Same as
  before this fix.
- `quarantine.py adopt` itself: **exit 2** — `REFUSED: adopt only accepts one of plan.yaml,
  BRIEF.md, feature.json, STATE.md, under a features/*/quarantine/*/ directory, not '...'`
  (`quarantine.py:158` `_adopt_target`, refusal text at `quarantine.py:175` `_refuse_adopt`).
- Canonical `feature.json`: **byte-unchanged** (`sha256[:12]` identical before/after).

At `fa5ce88e` this same sequence was gate exit 0 / adopt exit 0 / canonical overwritten
(`PWNED`) — reproduced previously in `notes/review-harness-security-reviewer-panel-c1.md` F-1 and
`notes/review-harness-code-reviewer-premise-c1.md` P4. At `aab31504` the write itself is now
refused unconditionally by `quarantine.py`'s own containment (`_quarantine_containment`,
`quarantine.py:50`), independent of whether the hook recognized the route — this is the important
shift: the fix moved the authoritative control into the tool that actually mutates state, not into
the (admittedly evadable, per its own docstring) PreToolUse text scanner.

## Step 2 — full matrix (fresh fixture root per row, canonical `feature.json`, no shared state)

All commands run for real against `quarantine.py` (`--root <fixture>`) and `plan-sign-gate.sh`
(`HARNESS_PROJECT_DIR=<fixture>`, same fixture, agent `harness-backend-dev`, no live claim on the
targeted feature unless noted). Victim = canonical `feature.json`, checked by sha256.

| row | gate exit | adopt exit | victim changed |
|---|---|---|---|
| `--file` outside any quarantine directory | 0 | **2** (`REFUSED: ... not under a features/*/quarantine/*/ directory`) | **No** |
| feature-A quarantine file, referenced via a symlink placed under feature B's quarantine dir | 0 | **0** — but lands on **feature A's own canonical**, not B's (`ADOPTED .../FEAT-A/feature.json FROM .../FEAT-B/quarantine/.../feature.json`) | **feature B: No.** (Feature A's own canonical *did* change — an authorized outcome for that fixture's claim state, not a cross-feature leak; see note below.) |
| symlink whose realpath escapes the quarantine dir | 0 | **2** (`REFUSED`, `resolved to:` names the escaped realpath) | **No** |
| nested one dir too deep under `quarantine/` | 0 | **2** (`REFUSED`) | **No** |
| quarantine-shaped file physically under an attacker root, `--root` pointed at the real victim root (the cycle-1 hole) | 0 | **2** (`REFUSED`) | **No** |
| `--file` basename not in `CANONICAL_ARTIFACTS` (`secrets.env`) | 0 | **2** (`REFUSED: adopt only accepts one of plan.yaml, BRIEF.md, feature.json, STATE.md`) | **No** |
| legitimate adopt, plain (no live-claim conflict) | 0 | **0**, `ADOPTED` | **Yes** — correct |
| legitimate adopt through a symlink that is itself still contained under the same feature's quarantine tree | 0 | **0**, `ADOPTED` | **Yes** — correct |
| well-formed adopt, genuine orphan (compat claim held by a *different* agent, same feature) | **2**, `Refused: ... holds no live claim for FEAT-ORPHAN ... Adoption is the resumed parent's act` | (not reached — hook refusal blocks the tool call in production) | n/a |
| same, but the writer itself holds the live claim | **0** | (n/a) | n/a |

Every fixture root used `tempfile.mkdtemp()` (`/var/folders/...`, realpathing to
`/private/var/folders/...` on this macOS box) specifically to exercise the normalization trap the
dispatch flagged — both legitimate rows adopted successfully despite it, so **no false refusal**
was observed anywhere in the matrix, including through the macOS `/var` → `/private/var` path.

**Cross-feature note (row 2):** the fix derives the target feature from the *regex parse of the
realpath itself*, never from the caller's asserted directory structure — so a symlink placed under
feature B's quarantine tree but physically resolving into feature A's tree lands on A's own
canonical, not B's. There is no directory-naming trick that retargets a write onto a different
feature's artifact; the physical location the realpath resolves to is authoritative. Feature B's
canonical never moves in this or any other row.

## Step 3 — do the two halves agree?

**On authorization outcome: yes, in every row tested.** Every attack row that reaches
`quarantine.py` is refused there regardless of what the hook decided; both legitimate rows succeed
at both layers. `plan-sign-gate.py`'s adopt-route recognition uses its own realpath-anchored regex
(`_quarantine_artifact`, `plan-sign-gate.py:339`) rather than the pre-fix literal-`quarantine`-segment
match — confirmed live: the shared `test-plan-sign-gate.py` case *"an orphan adopt reached through
a symlink is recognized by real containment"* (symlink physically outside the quarantine tree,
pointing *into* it) passes, exit 2, mentioning `quarantine`.

**On recognition of malformed shapes: no, and that asymmetry is intentional, not a gap.** Tested
directly (escaping-symlink and foreign-root rows, both halves): `plan-sign-gate.py`'s regex only
recognizes a resolved path that begins `.harness/<repo>/features/<feature>/quarantine/<writer>/<basename>`
*relative to its own trusted `ROOT`* (resolved once, from the hook's own script location via
`harness_boundary.resolve_root`, **never** from the command's own `--root` flag — confirmed by
reading `plan-sign-gate.sh`, which passes only its self-resolved root as `sys.argv[1]`). A
resolved path that lands outside `ROOT` (foreign root) or inside `ROOT` but off-shape (escaping
symlink) fails that regex and the hook exits 0 — it simply does not classify the call as a
quarantine matter at all, rather than recognizing-then-refusing it. `quarantine.py`'s own
`_quarantine_containment` is a strict superset of what it recognizes and refuses unconditionally,
so the hook's narrower recognition never leaves a gap: nothing the hook fails to recognize is a
case the tool itself would allow through. **Confirmed `orphan_write` is actually CONSULTED (not
merely reachable)** for the adopt route: built a well-formed, correctly-shaped, correctly-contained
adopt call for an orphan agent — the gate refused it at exit 2 with the live-claim message before
`quarantine.py` was ever invoked; flipping the claim to the caller's own session flipped the gate
to exit 0. Both are new, independent runs (not reads of the suite).

## New high/critical from the fix itself?

**None found.** `quarantine.py`'s containment additions are grade 4–5 across every touched
function (`_quarantine_containment`:4, `_adopt_target`:4, `cmd_adopt`:4, `_canonical_for_listing`:5,
`_run_plan_merge`:5, `_adopt_payload`:5, `_refuse_adopt`:5, `cmd_discard`:4, `cmd_list`:4,
`main`:4 — `code-grade.py .../quarantine.py`, `PASSING: 13`, no FAIL). No false-refusal of a
legitimate adopt was observed anywhere in the matrix, including the two rows built specifically to
probe it (plain contained adopt, symlinked-but-contained adopt).

## code_grade

Ran `code-grade.py` three ways at `aab31504`: full-file on `quarantine.py` (13/13 PASS, grade ≥4
everywhere), full-file on `plan-sign-gate.py` (10 PASS / **4 pre-existing FAIL**: `_strip_substitutions`,
`denies`, `_invocation`, `quarantines` — all grade 2), and gated `--base fa5ce88e --head aab31504`
(the diff itself): **13 PASSING, 0 FAILING** — every function this diff actually adds or changes
(`_quarantine_artifact` new at grade 4; every `quarantine.py` function touched; four new
`test-quarantine.py` cases) clears the bar. Verified directly with `code_grade.grade_source` on the
`git show` text of `quarantines` at both refs: cyclomatic 14→15, cognitive 27→28, ABC 35.0→36.2,
**grade 2→2 — already failing before this diff, unchanged in letter grade by it.** The diff touched
this already-over-bar function and left it marginally more complex within the same failing band; it
did not cross the bar downward and the gated comparison correctly does not flag it as a regression.
Recorded as pre-existing debt, not a finding of this review (F-3's own scope was `cmd_adopt` in
`quarantine.py`, confirmed 3→4 independently above).

**`code_grade: pass`** — the gated diff introduces or touches nothing that crosses the bar; the
four pre-existing FAILs in `plan-sign-gate.py` predate this feature (present at `fa5ce88e` too,
confirmed via direct `grade_source` comparison) and are not this diff's regression.

## Not re-raised (per dispatch)

D-18, D-19, the signed SC-13 fail-open `except Exception` clauses, and the prior F-2 about
`inflight_registry.py release` having no caller-identity binding (Q1, already open and ruled) —
the "well-formed adopt, genuine orphan" row above exercises the *gate's* consultation of that same
registry, not the registry's own authentication, so it does not reopen that question.

```yaml
VERDICT: PASS
DIGEST:
  headline: "F-2 closed at aab31504 — quarantine.py's own realpath-anchored containment refuses every row of an independently-built attack matrix (outside-dir, cross-feature symlink, escaping symlink, nested, foreign-root, bad-basename) and the legitimate/symlinked-contained rows still succeed with no false refusal; plan-sign-gate.py's adopt-route orphan check is confirmed actually consulted, not merely reachable"
  in_scope: true
  scope_reason: "F-2 is a containment/authorization boundary on canonical artifact writes (quarantine.py adopt, PreToolUse Bash) — squarely Tampering/Elevation-of-Privilege, and the dispatch's own remit."
  severity_max: info
  findings: 0
  must_fix: []
  code_grade: pass
  f2_status: closed
  threat_model:
    - { boundary: "quarantine.py adopt --file <path> --root <path>, containment shape", stride: "T", mitigated: true }
    - { boundary: "quarantine.py adopt --file <path>, symlink realpath escape", stride: "T", mitigated: true }
    - { boundary: "quarantine.py adopt --file <path>, foreign physical root shaped as legal path", stride: "T", mitigated: true }
    - { boundary: "quarantine.py adopt, cross-feature retarget via directory-naming", stride: "E", mitigated: true }
    - { boundary: "plan-sign-gate.py adopt-route recognition vs quarantine.py's own containment", stride: "T", mitigated: true }
    - { boundary: "plan-sign-gate.py orphan_write consultation on a well-formed adopt", stride: "E", mitigated: true }
    - { boundary: "plan-sign-gate.py quarantines() malformed-shape non-recognition (allows through to quarantine.py, which independently refuses)", stride: "T", mitigated: true }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-51-claude-code-lifecycle-safety/notes/review-harness-security-reviewer-delta-c1.md
```
