# plan-panelfix c9 — pm amendment record — FEAT-51-claude-code-lifecycle-safety

**BLUF.** The cycle-9 must-fix is closed by AMENDING THE RECORD, not by new enforcement: D-19 now
states that the quarantine boundary bounds exactly the two governed write routes, and REQ-04, the
`## Goal`, a new `## Verification gaps` bullet and T-06's mandated DEC-210 entry all carry that
qualification. **REQ-04's amendment is a SCOPE REDUCTION of an unsigned requirement and the operator
must accept it at signature** — verbatim before/after below. Both approvals still read `pending`.
`plan.yaml` written by one `plan-merge.py apply` recreate; `cmp` against the proposal exits **0**.

## The scope reduction — REQ-04, verbatim

BEFORE:
```
- REQ-04: A live child of an interrupted parent may finish read-only analysis, and its writes to
  canonical feature artifacts are quarantined instead of landing.
```
AFTER:
```
- REQ-04: A live child of an interrupted parent may finish read-only analysis, and its writes to
  canonical feature artifacts are quarantined instead of landing **on the two governed write routes
  the harness gates** — the `Write`/`Edit` editor route through `check-domain.sh`, and the
  `plan-merge.py` mutating verbs plus `quarantine.py adopt` through `plan-sign-gate.sh`. A generic
  `Bash` write to a canonical artifact that lies inside the writer's own domain is NOT covered
  (D-19).
```
`## Goal` took the same qualification in one clause. REQ-01..REQ-03 and REQ-05..REQ-07 are
byte-unchanged (proved by parsing both files' REQ regions and comparing with `==`).

## What landed

| item | remedy | where |
|---|---|---|
| F-A high | admit the hole, file enforcement as backlog — D-18's precedent, per the operator's F-1 ruling | D-19 (`dec: DEC-210`), REQ-04, `## Goal`, new gaps bullet, T-06 bullet list |
| F-C med | T-06's "exactly these claims" list rewritten IN PLACE to be what D-15 mandates | T-06 `intent:` |
| F-B med | T-02 gains a step replacing the LAST line of `children_refusal_lines`, + one asserted label, + a new verify conjunct | T-02 `intent:`/`verify:` |
| F-F low | every T-01 anchor re-measured at `0bc57c88` | T-01 `intent:` |
| panel record | cycle 9, 3 readers `ran`, 13 findings (7 carried byte-identically) | `panel:` |

D-15 untouched — it remains the record of WHY the supersession happened. No task added or deleted;
no enforcement code designed.

## T-06 — the two superseded bullets are gone

Removed, first eight words each:
- "Quarantine is a WRITE boundary, not a kill. A" — the bullet whose tail read "…is refused at the
  check-domain.sh Write gate on the canonical artifacts and told the exact quarantine path…"
- "The four canonical artifacts are plan.yaml, BRIEF.md, feature.json" — the bullet asserting the
  Write gate bites on "the last three" and resting `plan.yaml` on FEAT-41's editor denial.

Replaced by: a route-neutral quarantine-boundary bullet; a two-gate bullet naming `check-domain.sh`
(`Write`/`Edit`, on `BRIEF.md`/`feature.json`/`STATE.md`) and `plan-sign-gate.sh` (`PreToolUse`
`Bash`, on the four mutating `plan-merge.py` verbs and `quarantine.py adopt`); a bullet stating
`plan.yaml`'s only write route is `plan-merge.py` through `Bash`; and a "what it does NOT cover"
bullet carrying both the D-18 `discard` clause and the D-19 generic-`Bash` clause.

**T-06's `verify:` is unchanged and remains satisfiable from the bullet list alone**: the awk region
is the LAST `## DEC-` entry, which is DEC-210 by construction, and the bullets require the literals
`plan-sign-gate.sh` and `plan-merge.py` inside it; the index grep and the regeneration diff are the
task's own remaining steps. T-08's three guards are also reachable — `Bash` occurs as a whole word,
and one sentence carries BOTH `plan.yaml` and `plan-merge.py`.

## T-01 — anchors re-measured in the worktree at HEAD (`0bc57c88` content)

`validate-digest.py`: `VERDICTS` `:35` unchanged · `hook_mode()` `:1453`→`:1565` · `stop_hook_active`
`:1494`→`:1606` · STEP ONE `:1527`→`:1639` · `_reg.release(` →`:1646` · STEP TWO / `D-09 RETURN
CONTRACT` `:1549`→`:1661` · `live_children` `:1563`→`:1675` · `children_refusal_lines`
`:1575`→`:1687` · `release_cmd` →`:1698` · `return 2` `:1594`→`:1706` · `last_assistant_message`
`:1602`→`:1714` · the two-steps-order comment `:1498`→`:1610` · unavailable registry `:1510`→`:1622`
· no root `:1523`→`:1635` · release failure-swallowing `:1544`→`:1656`. **Beyond the floor list:**
`no agent_type` pass-through now `:1598` and `non-harness agent_type` now `:1604` (both previously
unnumbered) are named explicitly; `:1527` today lands in `check_artifact_file()` (`:1486`), which is
the wrong-function hazard F-F measured. `VALIDATE_DIGEST_BIN` is `:18` of
**test**-validate-digest.py, confirmed unchanged.

`test-validate-digest.py` — T-09-group anchors CONFIRMED unchanged: `case()` `:239`, `t09()` `:1227`,
`_reg_module()` `:1231`, `_t09_root()` `:1241`, `_t09_fire()` `:1249`, `run_t09()` `:1283`,
`claims()` `:1286`. Only the registration moved: `main()` `:3036`→`:3571`, with
`fails += run_t09()` at `:3578`.

The literals-are-the-anchors hedge is kept; provenance now says re-measured at `0bc57c88`.

## F-B, at source

`inflight_registry.py:521-537`. The last appended line (`:532-536`) reads "…an immediate second
identical return ships…" and names no suspension — the instruction that produces occurrence 7's
false terminal verdict. T-02 now directs replacing that one line with a `VERDICT: SUSPENDED` +
`awaiting:` statement, keeps the `#551` line above it byte-unchanged, and asserts both halves under
the label `the children refusal names SUSPENDED and never says a repeated return ships`, which is a
new conjunct of T-02's `verify:`.

## Open questions for the operator

- **Q1 (blocking, F-A):** accept the narrowed REQ-04 + `## Goal` + gaps bullet as the disposition, or
  rule otherwise. The plan now admits the hole and files generic write-route enforcement as backlog.
- **Q2 (F-D, `open`):** narrowing SC-02's `awaiting` set-equality to a subset/echo is approval-gated.
- **Q3 (F-E, `open`):** T-08's coupling of three permanent suite tests to DEC-210's prose is a named
  future cost, filed as backlog, not a defect in this plan.
- **Q4 (harness defect, not a plan finding):** `harness-code-reviewer` cannot terminally yield on a
  plan-phase dispatch — `validate-digest.py` refuses `code_grade` on an unpinned feature while
  `feature.json` already records `code_grade: n_a`. Route to the harness owner.
