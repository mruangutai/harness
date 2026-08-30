# Code review c1 (targeted) — FEAT-38-decisions-current-knowledge @ 2557950

Scope: F-4 ONLY, per dispatch. Not a fresh review — cycle-0 Stage 1 already PASSed and nothing
outside the four in-scope files changed since. All citations below are `git show 2557950:<path>`,
never a working-tree read.

## F-4 recap (my cycle-0 finding + my own Q1 on the anchors sibling)

`CLAIM_RE` in `check-decision-claims.py` silently dropped a malformed marker from `extract_claims` —
never counted, never failed, only a total-zero regression caught. I flagged the identical shape for
`ANCHOR_RE` in `check-decision-anchors.py` as Q1 (non-gating at c0). The remedy under review adds, at
both sites: a lookalike regex (`CLAIM_LOOKALIKE_RE` / `ANCHOR_LOOKALIKE_RE`) and a `Malformed*`
exception, mirroring `gen-decisions-index.py`'s `ROW_LOOKALIKE_RE`/`MalformedRow` shape.

## Verdict: F-4 is CLOSED at both sites. All five checks below pass, live, at the pin.

### 1. Detector fires — driven live, in-process, against pinned bytes

Loaded both modules at `2557950` via `compile()`/`exec()` on `git show` output (no disk write of the
checker itself; harness_boundary resolved via the real, unchanged bin dir on `sys.path`), then fed the
exact near-miss shapes cycle-0 proved invisible:

- claims: single `:` instead of `::` → **raises `MalformedClaim`** (previously: 0 claims found, no
  signal). Trailing text after `-->` → **raises `MalformedClaim`** (previously: 0 claims found).
- anchors: out-of-allowlist extension (`some_script.rb:12`, `notes.txt:5`) → **raises
  `MalformedAnchor`** for both (previously: silently never extracted).

### 2. Width — narrow enough not to false-positive, wide enough to catch real near-misses

Ran `extract_claims`/`extract_anchors` against the FULL pinned `DECISIONS.md` body: **zero**
`MalformedClaim`/`MalformedAnchor` raised — none of the document's 11 genuine claim-marker comments
or 20 genuine anchors false-positive. `CLAIM_LOOKALIKE_RE` is anchored on `^\s*<!--\s*claim:` (no
slack before the keyword), so a comment merely *mentioning* "claim" without that exact prefix shape
would not match — and the document has no other `<!--` comments to test this against (all 11 are
markers). Known-positive near-misses (§1) all correctly flagged. No false-positive or under-catch
found.

### 3. Loud failure reaches the exit code and the operator

Read `main()` directly at the pin: `extract_claims`/`extract_anchors` calls are wrapped in a `try`
that catches `MalformedClaim`/`MalformedAnchor` specifically (no broader `except`), prints each
offending line with its line number, prints `examined 0 <kind>(s), N failed`, and calls `sys.exit(1)`
— never falls through to 0. Confirmed by real subprocess end-to-end run (pinned source written to a
`/tmp` scratch file, executed as `python3 <script> --file <malformed-fixture>`, no import shortcuts):

```
claims:  exit=1, stdout: "<fixture>:3: malformed claim marker (...): <!-- claim: ... : 1 -->\nexamined 0 claim(s), 1 failed"
anchors: exit=1, stdout: "<fixture>:1: malformed anchor citation (...): See `some_script.rb:12` ...\nexamined 0 anchor(s), 1 failed"
```

### 4. Pinned by a test — confirmed by mutation, not by reading

`test-check-decision-claims.py` carries `test_malformed_claim_marker_single_colon_reports_line_and_exits_one`
and `test_malformed_claim_marker_trailing_text_reports_line_and_exits_one`; `test-check-decision-anchors.py`
carries `test_malformed_anchor_extension_reports_line_and_exits_one`. Both suites support a
`CHECK_DECISION_*_BIN` env override, so I ran them, unmodified, against **two** targets:

- **Baseline** (pinned checker, byte-identical): both targeted tests report `ok`.
- **Mutant** (a `/tmp`-only copy with the lookalike-detection branch reverted to the pre-fix
  silent-skip shape — `extract_claims`/`extract_anchors` no longer raise): both targeted tests go
  **red** (`FAIL - test_malformed_claim_marker_single_colon...: expected exit 1, got 0: 'examined 0
  claim(s), 0 failed'`, and the anchors equivalent — differential confirmed for both).

For an unmasked signal (my `/tmp` harness for the surrounding suite hit an unrelated `git ls-files`
env artifact — stale inherited `PWD` and non-git-repo tmp nesting, not a checker defect — that
affected unrelated `git-ls-files`-dependent cases in both baseline and mutant equally), I also ran the
mutant checkers directly with `cwd` set to the real worktree (a valid git repo) against the same
malformed fixtures: **`exit 0`, `examined 0 claim(s)/anchor(s), 0 failed`** — the exact silent-vanish
F-4 named, reproduced on demand from the neutered code and absent from the shipped code. This is the
clean mutation-kill proof; the pinned code does not exhibit it.

### 5. No regression in normal operation — discovery counts at the pin

Ran both pinned, unmutated checkers end-to-end against the pinned `DECISIONS.md`:

```
check-decision-claims.py  --file <pinned DECISIONS.md>: exit 0, "examined 11 claim(s), 0 failed"
check-decision-anchors.py --file <pinned DECISIONS.md>: exit 0, "examined 20 anchor(s), 0 failed"
```

Matches cycle-0's counts at `3928c70` exactly (11 claims, 20 anchors) — non-zero, so this is not a
sweep-over-an-empty-set pass; the fix adds no false positives against the live authority.

## Other observations

A security reviewer is concurrently re-grading the RCE fix in `check-decision-claims.py` in the same
file/commit. I read `refusal_reason`/`_refusal_reason_git`/`_refusal_reason_grep`/`_subprocess_env`
incidentally while establishing exit-code plumbing (§3) but did not evaluate them against the RCE
question — that is their domain, not re-derived here, and I saw nothing there that reads as a defect
in passing.

Pre-existing, not mine: `git status --porcelain` in the worktree shows five untracked stray entries at
the repo root (`100644`, `1788036665430977000`, `2`, two hex-named files) plus an untracked grilling
note — present before my session started and unchanged by it (confirmed via `git status --porcelain`
immediately before writing this note, matching the pre-probe snapshot). Not touched, not explained by
my work; flagging in case they are leftover artifacts from an earlier agent's tooling defect.

## No other Stage 2 findings. F-4 closed at both sites; nothing else raised.

```yaml
VERDICT: PASS
DIGEST:
  headline: "F-4 closed at both sites. CLAIM_LOOKALIKE_RE/MalformedClaim and ANCHOR_LOOKALIKE_RE/MalformedAnchor both fire live on the exact near-miss shapes cycle-0 proved invisible (single-colon typo, trailing text, out-of-allowlist extension), are narrow enough to produce zero false positives against the full pinned DECISIONS.md, reach exit 1 with a named, line-numbered failure through main()'s own try/except (no swallowing except), and are pinned by tests whose discrimination I proved by mutation — the exact pre-fix silent-vanish (exit 0, 'examined 0') reproduces only from a hand-neutered /tmp copy, never from the shipped code. Normal-operation counts unchanged from cycle-0 (11 claims / 20 anchors, both exit 0)."
  severity_max: info
  high_finding: false
  findings: 0
  must_fix: []
  spec_violations: []
  reviewed: "2557950 (targeted F-4 recheck; base_sha 7ebfc9e not re-diffed, per dispatch)"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-38-decisions-current-knowledge/notes/review-harness-code-reviewer-c1.md
```
