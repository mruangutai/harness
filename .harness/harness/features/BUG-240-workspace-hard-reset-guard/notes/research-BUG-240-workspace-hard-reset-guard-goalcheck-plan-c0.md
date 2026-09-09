# Plan goal-check — BUG-240 — against stated intent (`notes/intake-BUG-240.md`)

## DOES THIS PLAN DELIVER THE OPERATOR'S STATED INTENT?

**yes-with-gaps.** Every clause of the issue's Scope paragraph and every one of its five
Verification bullets is carried by a REQ, an SC and at least one task, and nothing in the plan
delivers anything the intake ruled out. But **one factual measurement asserted inside T-01's
`intent:` is false at 6d969ed, and it makes BOTH tasks' `verify:` commands unpassable as written** —
so the plan as drafted cannot green its own gates, in either order.

Judged at the worktree, HEAD 6d969ed. Baseline measured: `python3 tests/unit/test-factory-workspace.py`
→ `30/30 checks passed.`, rc 0 — so T-01's `rc == 1` can only come from its new FAIL lines.

| # | Item | Grade | Citation |
|---|---|---|---|
| 1 | Scope clauses → REQ → task, both directions | VERIFIED | below |
| 2 | Five Verification bullets → discharging SC | GAP (SC-04 ordering) | below |
| 3 | Nothing ruled out is delivered; no widening | VERIFIED (0 over-reach) | plan.yaml:42-43,154-155,204-205 |
| 4 | Both `verify:` executable and truthful | GAP (fatal, ×1; wrong-reason red, ×1) | plan.yaml:54,139-140 |
| 5 | `intent:` leaves no behavioural discretion | VERIFIED (discretion is test shape only) | plan.yaml:180-205 |

## 1 — Scope clauses, mapped both ways

| Scope clause (intake:32-36) | REQ | Tasks |
|---|---|---|
| (1) computed path IS the harness checkout → refuse | REQ-01 | T-01 cases 5-6 (plan.yaml:116-134), T-02 (180-187) |
| (2) target has uncommitted changes → refuse | REQ-02 | T-01 cases 1-3 (89-107), T-02 (189-197) |
| "before the first destructive git command" | REQ-01/02 wording, REQ-05 | T-02 insertion at 176-178 |
| refusal names the path AND which condition fired | REQ-03 | T-01 case 2 (`uncommitted` + path) and case 5 (`control-plane`, NOT `uncommitted`), T-02's two `refuse` strings (181-196) |
| must NOT offer a `--force` | REQ-06 | T-01 case 7 (136-143), T-02 (204-205) |
| (implied by (2)) ignored dirt is not work | REQ-04 | T-01 case 4 (109-114), T-02 (196-197) |

Reverse direction: REQ-01→T-01/T-02, REQ-02→T-01/T-02, REQ-03→T-01/T-02, REQ-04→T-01/T-02,
REQ-05→T-01 case 4 + existing (A)(B)(C) + T-02:189-191, REQ-06→T-01 case 7 + T-02:204-205. No
orphan REQ; both tasks trace all six (plan.yaml:35,147).

## 2 — Verification bullets → SC, and whether the method can produce the evidence

| Bullet (intake:39-44) | SC | Method could discharge it? |
|---|---|---|
| dirty tracked refused, file byte-identical | SC-01 | **yes** — cases 2-3 build a REAL repo pair and re-read the bytes (plan.yaml:78-107); a plausible defect (no guard) reaches `reset --hard origin/main` and destroys them, so it reddens for the right reason |
| ignored-only NOT refused | SC-02 | **yes** — case 4 asserts exit 0, `junk/scratch.txt` present, HEAD on `factory/issue-42` (109-114); a `--ignored` defect reddens |
| self-path refused even when clean | SC-03 | **yes, post-T-02 only** — case 5 exercises the refusal with `_control_plane_root` substituted; case 6 pins the real identity. See G2: case 6 asserts equality with the exact expression T-02 is told to write (plan.yaml:132-133 vs 169-170) — implementation restatement, not a consumer observable; it is case 5 that observes behaviour |
| clean scratch refreshes exactly as today | SC-04 | **partial** — G3: nothing asserts the `fetch → checkout <default> → reset --hard` order that SC-04 names |
| `run-unit-tests.sh` exits 0 | SC-05 | **not as drafted** — G1 makes the suite unable to reach green |

No SC's evidence is a restatement of the plan's own instruction except case 6 as noted; SC-06 is
`inspection` (BRIEF.md:77-80), so case 7's source-text assertions are a tripwire, not the evidence.

## 3 — Nothing ruled out

Checked each bullet of "What the operator did NOT ask for" (intake:93-98) against both tasks'
`files:`, `intent:` and `verify:`. No flag/env override is added and one is forbidden
(plan.yaml:204-205); `workspace_path` is untouched (T-02 `files:` is the single production file,
154-155) and its derivation is only *called*; `fleet.yaml` validation and the clone branch are
untouched; `_checkout_issue_branch` is explicitly left unchanged (209-210). **Over-reach: none.**

## 4 — Executability, and every asserted measurement re-measured

**T-01's verify cannot pass.** It demands `ok    BUG-240 no bypass: the parser rejects --force`
(plan.yaml:54), but the case behind that name asserts `"os.environ"` occurs **exactly once** in
`factory_workspace.py` (plan.yaml:139-140). It occurs **three** times — `factory_workspace.py:22`
(module docstring), `:39` (run_git docstring), `:48` (the code). Case 7 therefore prints `FAIL`, the
seventh grep fails, and the `&&` chain is non-zero. The same assertion also makes **T-02's verify**
unpassable (plan.yaml:158-159): T-02 adds no `os.environ`, so the file can never go green.

Per-name state at the moment T-01 exists and T-02 does not:

| Name | Demanded | Will obtain | Right reason? |
|---|---|---|---|
| dirty tracked: exits 2 before any fetch | FAIL | FAIL — no guard, exit 0, `fetch` recorded | yes |
| dirty tracked: refusal line names path + condition | FAIL | FAIL — stderr empty | yes |
| dirty tracked: file survives byte-identical | FAIL | FAIL — real `reset --hard` destroys it | yes, reproduces the defect |
| self checkout: refused when clean | FAIL | FAIL — but only via the `getattr(fw,"_control_plane_root",None) is None` skip (plan.yaml:127-128) | **no — red on symbol absence, the refusal is never exercised** |
| control-plane root: agrees with harness_boundary | FAIL | FAIL — `AttributeError`, reported through `check()` | absence is this case's own subject, so acceptable |
| ignored-only dirt: not refused | ok | ok — real git completes the refresh, HEAD `factory/issue-42` (`ISSUE = 42`, test file) | yes |
| no bypass: parser rejects `--force` | ok | **FAIL** — see above | **no** |

Measurements asserted in `intent:`, each opened and measured:

| Claim | Result |
|---|---|
| `.agents/skills` is a symlink to `../.claude/skills`, one production file | CONFIRMED (`os.path.islink` → True) |
| `"--force"`, `"--yes"`, `"FACTORY_FORCE"` absent from the file | CONFIRMED (grep rc 1) |
| `"os.environ"` occurs exactly once | **CONTRADICTED — 3× at :22, :39, :48** |
| `_checkout_issue_branch` docstring says "force-aligned" | CONFIRMED (its docstring) |
| existing case (K) is the last case; `check`/`Recorder`/`run_main(rec, extra_args, workspace_root)`/`checkout_path(wr)` exist | CONFIRMED (test-factory-workspace.py) |
| existing case (A) asserts clone-first with no extra git call | CONFIRMED (`kinds[0] == "clone"`, `"fetch" not in kinds`) |
| `factory_config` already imports `harness_boundary` and carries that `_BIN_DIR` line | CONFIRMED (factory_config.py:34,37) |
| `harness_boundary.MARKER = .harness/team-config.yaml`; `resolve_root(bin_dir, strict=True)` | CONFIRMED (harness_boundary.py:54,66 — `strict=False` is a real keyword) |
| insertion point: after `path`/`branch`, before the `.git` isdir branch | CONFIRMED (factory_workspace.py:117-120) |
| `factory_cli.refuse` prints one `factory: <tool>: ...` line and exits 2; `run` traps the wordier "unexpected failure" | CONFIRMED (factory_cli.py:43,50-52,90) |
| `run-unit-tests.sh --kind unit` is a real invocation | CONFIRMED (run-unit-tests.sh:18,23,30) |

Aside, not a plan defect: the intake's own item 5 puts `workspace_path` at `factory_config.py:399-404`;
it is at **394-399**. The plan repeats no line range from it.

## 5 — Discretion left to the builder

None on behaviour: predicate (realpath identity; `dirt.strip()` non-empty), placement (between
:118 and :120, dirty check inside the isdir test), both refusal string quadruples, and the exit code
(via `factory_cli.refuse`) are all literal (plan.yaml:169-201). Discretion is local test shape only:
the driver cases 2-4 use for real git, and case 5's fleet fixture — `run_main`/`good_fleet_dict`
hardcode `REPO = "acme/widget"`, so the repo-name override case 5 needs (plan.yaml:121-123) cannot
come from the named helper. Acceptable, but see G4.

## Gaps — what is missing (no rewrites proposed)

- **G1 (fatal).** A true measurement behind T-01 case 7: the `os.environ`-exactly-once assertion is
  false at 6d969ed, so both `verify:` commands are unsatisfiable (plan.yaml:54,139-140,158-159).
- **G2.** Any case whose pre-T-02 red is caused by the destructive behaviour for the *self-checkout*
  condition. Case 5's FAIL comes from `_control_plane_root` being absent (plan.yaml:127-128), so
  REQ-01's discrimination is unproven in the red state.
- **G3.** An assertion of the `fetch → checkout <default_branch> → reset --hard` sequence SC-04
  names (BRIEF.md:71-73). Existing cases assert only clone-first, fetch-present, issue-branch-last.
- **G4.** A fixture route for case 5's repo-name override; the helper the intent points at cannot
  express it (test-factory-workspace.py `good_fleet_dict`/`run_main`).

Advisory, outside the intake: D-01's negative half — a harness checkout at some *other*
`workspace_root` must still be refreshed (plan.yaml:26-28) — has no case.
