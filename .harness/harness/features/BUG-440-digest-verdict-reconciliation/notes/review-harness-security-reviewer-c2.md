# Security re-review — BUG-440-digest-verdict-reconciliation — cycle 2

review_sha: `a1a67956a5844c67ce098e9580ee6692a92f9a30` (prior: `2964cddbbfe465d1268cb12a248861d8a28e31a6`)

## BLUF

**PASS.** The census confirms the remedy was test-only: `.claude/skills/harness/bin/check-state.sh`
is byte-for-byte identical between the two pins (`git diff <old>..<new> -- check-state.sh` is empty);
`tests/integration/test-check-state.py` is the only file that moved (65 insertions / 59 deletions,
pure refactor + two fixture edits). Every REQ-03(d)/no-write/security property that attaches to
`check-state.sh` therefore carries forward from cycle 1 unchanged, by construction — no re-derivation
performed. The one carried finding, V-05, is unaffected: still **low**, still open, not touched by
this cycle because its remedy was never assigned to T-01.

## Census (measured, not predicted)

```
tests/integration/test-check-state.py | 124 ++++++++++++++++++----------------
1 file changed, 65 insertions(+), 59 deletions(-)
```
`check-state.sh` diff: empty. No other files in the feature's source surface moved.

## Carried finding: V-05 — STILL OPEN, severity unchanged (low)

**Mechanism** (`check-state.sh:1552-1557`, unchanged bytes): `os.path.basename(_feat_dir)` (feature
directory name) and `_rid` (run directory basename) are spliced into the INV-37 operator message via
plain f-string interpolation; `_dm.group(1)` and `_rv` (the two verdict tokens) are `!r`-quoted
(`repr()`, which escapes and quotes). A directory name containing structure-breaking characters —
embedded newline, an `INV-`-prefixed substring, or a fake trailing clause — is not escaped and can
make the printed line look like a different or additional finding to an operator skimming raw stdout.

**Concrete precondition** (unchanged from cycle 1): the attacker must be able to create a directory
under `.harness/<repo>/features/<name>/` (or `runs/<id>/`) — i.e. already hold filesystem write
access to the control plane tree this gate protects — *and* have already written a `feature.json` +
`digest.md` pair with mismatched verdicts to make INV-37 fire at all. That is the same privilege
level needed to forge the verdict record the gate exists to catch (P-02: an actor who already
controls the compared values already holds the privilege the spoofed *display* would grant them
nothing beyond). The gate's blocking decision itself (`code == 1`, computed from `_dm.group(1) !=
_rv`) is untouched by directory-name content — only the human-facing transcript can be visually
forged, not the exit code an automated caller reads. This keeps it at **low**, not higher: it is a
display-integrity gap on an already-compromised-input path, not a bypass of the block.

**Does the new fixture code change exploitability?** No. `_bug440_build`/`_bug440_validate_fixture`
use only hardcoded literal directory names (`"M"`, `"E"`, `"N"`, `"I"`, `"G"`, `"X"`, `"O"`,
`"FEAT-TEST"`) — none exercise or validate the unescaped-name path, and neither adds nor removes any
sanitization at the production call site (which is unchanged, byte-identical, code). V-05's status
is exactly what it was at cycle 1: real, low, unremedied, and out of scope for this test-only fix
(cycle-1 never put it in must_fix).

## New code audit (`_bug440_digest`, `_bug440_build`, `_bug440_validate_fixture`)

- **Sandbox containment**: `_bug440_build` writes only through `os.path.join(fdir, ...)` where `fdir`
  descends from the caller's `tempfile.TemporaryDirectory()` (`tmp`); the run-name path segments are
  the same seven hardcoded literals above — no fixture value is attacker- or environment-controlled,
  so there is no path-traversal vector into `os.makedirs`/`open`.
- **Wrong-root clobber risk**: `_bug440_validate_fixture` calls `run(tmp)`, and `run()` (unchanged,
  `test-check-state.py:95-98`) executes the script with `cwd=tmp` and an environment built by
  `_root_env(tmp)` — it cannot reach outside the temp tree by construction; this was true before the
  refactor and is untouched by it.
- **Secret/host-path leakage**: fixture digests carry only synthetic placeholder content (`headline:
  synthetic BUG-440 fixture`, `team: eng`, `artifact: fixture/digest.md`) — no absolute host paths,
  credentials, or environment values are written into any file the fixture produces.

## REQ-04 (no-write) — reconfirmed at this pin

Grepped the full INV-15/INV-37 region (`check-state.sh:1524-1557`): the only I/O call is
`open(dg, encoding="utf-8", errors="replace").read()` — read-mode only. No `open(..., "w")`,
`os.makedirs`, `os.rename`, or `shutil.*` call appears in the region. Since the file is byte-identical
to the pin cycle 1 already verified, this is confirmation of an unchanged fact, not new evidence.

## STRIDE — angles that apply to a local, read-only, offline gate

- **Tampering — in scope, and it's the point.** The threat this feature defends against *is*
  tampering with `feature.json`/`digest.md` after the fact; REQ-01's "blocking, not a warning" clause
  is exactly the anti-tampering contract. QA's mutation results (V-02/V-03, now resolved per the
  isolated fixtures) are the load-bearing evidence for this angle, not mine to re-derive.
- **Repudiation — inapplicable to this diff.** The gate's stdout is the only audit surface and this
  code makes no new claim about persisting or signing it; that property (or its absence) predates
  this feature and this diff does not change it.
- **Spoofing, Information disclosure, Denial of service, Elevation of privilege — inapplicable.** No
  new identity assertion, no new data exposed beyond what the gate always read locally, no new
  unbounded loop or expensive operation, no privilege boundary crossed (local script, same user).

## Verdict

V-02 and V-03's isolated-fixture remedies (module-level helpers, `X`'s digest text now carrying a
real `VERDICT:` line, the standalone `("M",)`-only tree) are orthogonal to security and change
nothing this role grades; confirmed by reading the diff, not re-litigated. V-05 remains the only
open security finding, unchanged in severity or mechanism.

```yaml
VERDICT: PASS
DIGEST:
  headline: "check-state.sh is byte-identical between pins by measured diff; the test-only remedy introduces no new security surface, and the one carried finding (V-05, low, output-spoofing on unescaped operator-facing names) is unchanged and still open."
  in_scope: true
  scope_reason: "check-state.sh moved zero bytes (measured git diff), so REQ-04 no-write and V-05's mechanism carry forward unchanged; the new test helpers were audited for sandbox escape, wrong-root clobber, and secret leakage since they are new code even though non-production."
  severity_max: low
  findings: 1
  must_fix: []
  threat_model:
    - { boundary: "feature.json/digest.md verdict comparison (INV-37)", stride: T, mitigated: true }
    - { boundary: "operator-facing gate stdout (feature/run directory name interpolation)", stride: I, mitigated: false }
    - { boundary: "gate stdout as sole audit trail", stride: R, mitigated: true }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/BUG-440-digest-verdict-reconciliation/notes/review-harness-security-reviewer-c2.md
```
