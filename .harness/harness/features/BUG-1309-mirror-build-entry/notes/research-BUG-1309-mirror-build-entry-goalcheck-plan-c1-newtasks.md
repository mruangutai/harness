# Goal-check — BUG-1309 plan cycle 1 — T-10 and T-11 only

**No — not yet. T-10 delivers the operator's stated intent in full; T-11 delivers it in substance but
carries two defects that must be closed before signature: one required test kind is left without any
owner (T-07's sweep), and three of its thirty cases are relabelled copies of integration guards, which
DEC-217's Over clause forbids by name.** Neither defect touches the settled policy; both are one-clause
fixes. T-01..T-09 not re-graded.

## 1. Do the two tasks close the three gate failures?

| Gate failure | Owner | Sufficient? |
|---|---|---|
| `(e-green) SC-14` RED — fixture commits no `build_entry`, T-07's retention branch correctly keeps the worktree (`post-merge-sweep.sh:221-233`) | T-10 (`plan.yaml:1444-1503`) | **Yes.** `files:` is the only file that must change (`tests/integration/test-hooks-install.py:406` is the single call site, as intent claims at :1481). `verify:` is well-formed: the file prints `PASS: <name>` (`test-hooks-install.py:502`) and all three needles are true prefixes of real assertion names (:419, :429, plus the new one). |
| `feature.always: [unit, integration]`, T-03 integration-only | T-11 BE-25..BE-30 over `_recover_terminal_conflict`/`_recover_terminal_report` (`gh-sync.py:1225`, `:1240`) | **Yes.** |
| `bugfix` + `touches_runtime_code` → `unit`; T-02, T-04, T-06, T-07 add none | T-02 → BE-11..BE-20; T-04 → BE-21..BE-24; T-06 → BE-01..BE-10 (`feature_schema.py:226`, `:324` are T-06's own runtime change, and `check-state.sh:2002,2011` is INV-37 reading exactly those two) | **T-07 IS UNOWNED.** T-11 lists `depends_on: [T-02, T-03, T-04, T-06]` (`plan.yaml:1510`) and traces no T-07 REQ. BE-10 asserts the era SET, never the sweep's branch. And the branch is unreachable from `tests/unit/`: it lives inside the `python3 -I - <<'PYEOF'` heredoc opened at `post-merge-sweep.sh:29`, so there is nothing to import. Per `harness-qa-gate` step 5 this resolves `missing` → FAIL, not a soft skip. |

Attribution is not per task — the gate classifies each *logical change* from the diff
(`harness-qa-gate/SKILL.md:30,65`), so T-11's two files legitimately discharge the floor for the
gh-sync.py and feature_schema.py changes whatever task hosts them. That model is what makes T-11 a
legal owner; it is also why T-07's bash-hosted change has no route.

## 2. DEC-217 conformance — judged case by case, on the specified assertions

**Conformant except BE-21, BE-22 and BE-23, which I would strike or re-aim.** Each is the same
predicate and the same observable as an existing integration case, one layer down:
BE-21 ≡ `test-gh-sync.py:3602` ("non-era absent refuses", rc 2, message names `gh-sync.py open`);
BE-22 ≡ `:3612` ("station discriminator", `recover-terminal` present and no bare `open`);
BE-23 ≡ `:3618` ("era-exempt continues", exit 0, stderr names the exemption). DEC-217 (`DECISIONS.md:6876-6878`)
forbids exactly "copying an already mutation-proven integration contract guard into `tests/unit/**`
solely to satisfy a directory label". BE-24 shows the legal shape — a recorded `opened` printing
*nothing at all* (`gh-sync.py:1370-1376`) is a table row the T-04 bed never constructs.

Every other case discriminates, and two do so strongly:
- BE-11/BE-12 reach a state **no command can produce**: the out-of-enum coercion at `gh-sync.py:624-626`
  and the falsy-drop at `:933`. The writer only ever writes enum values, so integration cannot get there;
  its build_entry assertions (`test-gh-sync.py:1404,1420,1427`) only cover the absent-default rows.
- BE-14 (`recovery-required` → `opened`) and BE-15 (no downgrade under `record_build_entry`,
  `gh-sync.py:947-948`) are transitions the T-02 bed never runs; `:3482` only re-runs `open` on `opened`.
- BE-16..BE-20 are the five-branch truth table of the four-conjunct guard at `gh-sync.py:187-189`.
  Integration touches four branches at one call site each (`:3441,:3431,:3451,:3575`) and never BE-18's
  conjunction or BE-19's absent-file leg. BE-16 is the all-true positive control without which the four
  negatives prove nothing; keep it.
- BE-01..BE-10 are decision-table rows over `recovery_command_for` (`feature_schema.py:324-338`), of
  which integration exercises two outcomes; BE-02's trailing slash pins the `rstrip` at `:326`.
- BE-30's exact-list assertion over `_recover_terminal_report` is SC-05's zero-task-sub-issues property
  at a second, cheaper seam and over four adoption states the bed grades at one.

## 3. Does T-10 weaken SC-14?

**No — it strengthens it.** The intent explicitly retains `not os.path.isdir(dest)` unchanged
(`plan.yaml:1490-1492`); the new assertion adds the *reason*, keying on `"post-merge-sweep: removed"`
present and `"records github.build_entry"` absent — that second string is the sweep's own SKIP text
(`post-merge-sweep.sh:230-231`), so the case can never green again on the retention branch having fired.
Crucially the repair is a **committed receipt**, not a widened era set: intent states the synthetic name
can never be exempt (`:1472-1473`), so the era policy is untouched. The `(e-red)` case keeps
`expect_removed=False` (`test-hooks-install.py:487`) and its survival becomes attributable to the
repointed shim alone. No coverage is lost: the absent-`build_entry` sweep path is graded by T-07's own
two cases under SC-06 (`BRIEF.md:118-127`).

## 4. Scope discipline

`change_type: scaffolding` is **honest**. `harness.json` `test_matrix.scaffolding.always` is `[]`
(`.harness/harness.json:234-236`), and a diff consisting solely of two new `tests/unit/test-*.py` files
is genuinely test-only — demanding a unit test of a unit test is circular, and the typing does not
control the gate anyway (§1). No production file appears in `files:` and the intent forbids one
(`plan.yaml:1524-1525`).

Traces: T-11's five all hold — REQ-03/REQ-04 via BE-11..BE-16, REQ-06 via BE-17..BE-24, REQ-08 via
BE-28..BE-30, REQ-10 via BE-01..BE-10 (INV-37's only two Python inputs). T-10's REQ-02 holds
(`BRIEF.md:37-38`, "release the worktree"). **T-10's REQ-09 is thin**: REQ-09 (`BRIEF.md:53-54`) is the
*keep* outcome, and T-10 asserts its complement — the negative control. T-07 owns the positive half.

## 5. The operator's stated intent — four clauses, individually

1. **Refusals key on the LOCAL record.** Upheld, and reinforced. BE-21..BE-24 call
   `_build_entry_preflight(feat_dir, rec)` with a local `rec`; no BE case consults a remote. T-10
   deliberately records a committed `"opened"` rather than routing through a fake-`gh` open run, and says
   why (`plan.yaml:1494-1496`).
2. **Era set exempts the three refusals; retention keys on the RECORDED value.** Untouched. BE-10 pins
   exact, case-sensitive, non-prefix membership — the property both `post-merge-sweep.sh:223` and
   `gh-sync.py:1361` branch on — and forbids asserting the set's size or contents
   (`plan.yaml:1566-1567`), correctly, given the regeneration comment at `feature_schema.py:222-225`.
   T-10 adds a receipt; it does not add a name to the set.
3. **Recovery is explicit and operator-approved.** Untouched. BE-25..BE-30 exercise only the pure
   conflict/report helpers — the report-and-ask half — and no case reaches `--yes`, removes it, or
   asserts a write. `cmd_recover_terminal`'s `--yes` gate (`gh-sync.py:1277`) is unmentioned by either task.
4. **A partial remote write or an unpinned repo records NOTHING.** Upheld and sharpened: BE-17 pins the
   `_NO_RECORD` sentinel (`gh-sync.py:188,288-289`), BE-18 the `remote_written` conjunct, BE-19 the
   absent-file conjunct, each asserting **key absence, never a falsy value** (`plan.yaml:1606-1607`).

## 6. Signature readiness — every residual

| # | Residual | Blocking | The one clause that closes it |
|---|---|---|---|
| R1 | T-07's `unit` floor has no owner; the sweep's branch is heredoc-hosted and not importable (§1) | **yes** | Either an operator/Advisor ruling recording the `unit` kind as not-applicable for a heredoc-hosted runtime surface (a DEC-217 sibling), or a new task extracting the sweep body to an importable module. **Not pm's to decide** — it changes an approved decision's reach. |
| R2 | BE-21..BE-23 are relabelled integration guards, against DEC-217's Over clause (§2) | **yes** | Amend T-11's intent so each names a state or observable `test-gh-sync.py:3596-3624` cannot construct, keeping the ids so the verify's `seq 1 30` range still holds. |
| R3 | T-11's FIXTURES paragraph (`plan.yaml:1543-1545`) says `recovery_command_for` "reads the segment after features". It does not — it uses `os.path.basename(feat_dir.rstrip("/"))` (`feature_schema.py:326`). The segment-after-features reader is `_feature_dir_name` (`:307-321`), a different function | no | Correct the sentence. The mandated fixture path shape still works, so no case changes. |
| R4 | T-10's `traces:` claims REQ-09, which T-07 owns; T-10 asserts its complement (§4) | no | Drop REQ-09 from the trace, or state in intent that it is the negative control for T-07's positive case. |
| R5 | The dispatch's "BRIEF.md SC-14" does not exist — this BRIEF stops at SC-10. SC-14 is FEAT-34 T-13's criterion (`tests/integration/test-hooks-install.py:2`) | no | Nothing in the plan. Recorded so no later reader grades BUG-1309 against a criterion it does not own. |
| R6 | `approval.status: approved` at `date: '2026-09-04'` (`plan.yaml:3-6`) stands over a task set that has since gained T-10 and T-11; `BRIEF.md:166-170` records approval at 2026-09-06. **The operator must see the date and task-set mismatch before re-signing.** Not edited here, and not pm's to edit | **yes** | The main session's `sign-approval` after the operator reviews the amended task set. |

Open questions for the tier above: R1 is a decision, not a task. Everything else is a plan edit.
