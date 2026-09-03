# Code Review — FEAT-52-factory-control-plane — impl-c9

`review_sha: d8c42a9df691f3e4774047138ef9caeb0c8f5850`, diffed against
`merge-base(main, review_sha) = 8ff525e246ba3af9d69d08646e52be28d7546c47`. HEAD (`fa6efda6`)
differs from the pin only in `feature.json`; every claim below is grounded at the pin via
`git show <sha>:<path>` or by running the checked-out tests, which are byte-identical to the pin
for every file cited (confirmed by diff against `feature.json`'s single-line delta).

## BLUF

**FAIL.** Stage 1 fails on its own terms: eight of fifteen success criteria are unmet at the
pinned tree, seven of them because the *committed automated evidence the criterion itself names*
was never written even though every corresponding task reads `status: done` — the production code
mostly exists and in several cases visibly works when hand-driven, but "verify: automated,
evidence: unit/integration" means a committed test, and for SC-01, SC-02, SC-03, SC-06, SC-08,
SC-12 and SC-13 no such test exists in the tree at the pin. On top of the missing-evidence class,
two are genuine fail-open defects: `inflight_registry.feature_root` silently collapses onto the
control-plane root on `AmbiguousWorktree` (SC-10's own guarantee), and `dispatch-guard.sh`'s new
tool-grant read swallows every read/parse failure with **zero stderr line**, unlike every other
fail-open branch in the same file, which all say so out loud.

## Per-criterion table

| SC | Verdict | Basis |
|---|---|---|
| SC-01 | **NOT MET** | `test-inject-expertise.py` case4 asserts the injected value is absolute but never sets `cwd=` on the subprocess and never asserts the injected path differs from it — the discriminating assertion SC-01 names by name is absent. |
| SC-02 | **NOT MET** | The no-non-zero-exit clause (grep + positive control) exists and passes (T-14). The UNRESOLVED-branch clause has zero committed test — `grep -c UNRESOLVED test-inject-expertise.py` = 0. Manually confirmed the code branch itself is correct (see Findings, informational). |
| SC-03 | **NOT MET** | Requires 5 separate named scope-completeness assertions (S1-S5). `test-check-instruction-paths.py` asserts only 3 (qa-gate, expertise, handoff); `.omp/agents/harness-backend-dev.md` (S4) and `templates/PLAN.md` (S5) are never asserted present in `--list-scope`. |
| SC-04 | **MET** | `test-anchor-directions.py` run live against the pin (`HARNESS_REVIEW_SHA=d8c42a9d...`): all 6 rows + whole-scope-at-pin PASS. |
| SC-05 | **MET** | RED proof asserts both the inline (`:1:`) and fenced (`:3:`) line numbers and the 2-violation summary in one case; GREEN twin passes. |
| SC-06 | **NOT MET** | T-05's mandated "prove the read" case (temp product-shaped cwd, no `.agents`/`.claude`, assert the anchored path opens and the pre-change bare path does not) is absent from `test-check-instruction-paths.py`. Zero hits for "systematic-debugging" or "product-shaped" anywhere in `.claude/skills/harness/bin/`. |
| SC-07 | **MET** (inspection) | `.harness/team-config.yaml`: zero-line diff base→pin. All 16 `.omp/agents/*.md` diffs are body-prose hunks only (confirmed hunk headers on the 4 lead/orchestrator files land at lines 30-146, never near the `tools:` frontmatter block at the top). |
| SC-08 | **NOT MET** | The workflow step exists, is inside `integration:`, and distinguishes exit 1/exit 2/missing-summary correctly (`.github/workflows/tests.yml:200-216`). The *committed assertion proving that step exists and can go RED against two mutants* — the criterion's actual deliverable — is absent: zero hits for "workflow" or "tests.yml" in any `bin/test-*.py`. |
| SC-09 | **MET** (inspection) | `harness-handoff/SKILL.md:63-68` states both placeholders, the resolving command, and the read-only policy. `DECISIONS.md:6563` (DEC-212) plus `DECISIONS-INDEX.md:211` row exist; T-13's own verify (`gen-decisions-index.py --stdout \| diff -` and `test-gen-decisions-index.py`) both pass clean at the pin. |
| SC-10 | **NOT MET** | `inflight_registry.py:265-271` `feature_root()` wraps `worktree_for_feature` in a blanket `except Exception: return owner_root`, which also swallows `AmbiguousWorktree` — the resolver's own documented "never guess, refuse instead" exception (`harness_boundary.py:185-229`). On an ambiguous match the write silently collapses onto the control-plane root, exactly the case SC-10 says must never happen. No test exercises this branch (`test-inflight-registry.py` case35 covers only single-match, no-match, short-form and zero-match). |
| SC-11 | **MET** | Whole-scope run at pin: `scanned 62 file(s), 0 violation(s)`; T-15 row 3 and row 6 (the two mirror-class sites) pass at the pin. |
| SC-12 | **NOT MET** | Only the `HARNESS_PATH_DRIFT: unknown` branch is exercised (case4, incidentally, via an empty fixture root with no checker present). The `none` clean-file case and the `N unanchored path(s)` + file:line RED case — the pair SC-12 explicitly requires — do not exist anywhere in `test-inject-expertise.py`. |
| SC-13 | **NOT MET** | `test-dispatch-guard.py` is byte-identical between base and pin (508 lines, zero-line diff, confirmed both ways). None of the four required cases (REFUSED / ALLOWED / DISCRIMINATION / MISMATCH REFUSED) exist. No other file in the repository references `HARNESS-FEATURE-TREE-ROOT` in a test context. |
| SC-14 | **MET** | Four separate findings below. |
| SC-15 | **MET** | `test-check-domain.py`'s `_feat52_foreign_cwd_receipt_pair` (new function, code-grade PASS, grade 4) runs live and passes: "SC-15 PAIR: foreign product cwd allows its feature-worktree receipt and refuses its product twin." |

## SC-14 — four separate per-file findings (verify: inspection)

1. **`.omp/agents/harness-product-lead.md:92`** — MET. States "You hold no shell.
   `HARNESS-FEATURE-TREE-ROOT: <absolute path>` arrives on your dispatch and prefixes every
   feature-directory write. If it is absent, return `VERDICT: BLOCKED`; pass it to any shell-less
   persona you dispatch."
2. **`.omp/agents/harness-eng-lead.md:110`** — MET. Byte-identical statement to (1).
3. **`.omp/agents/harness-validator-lead.md:138`** — MET. Byte-identical statement to (1).
4. **`.omp/agents/harness-orchestrator.md:146`** — MET (the matching emit duty, not the receive
   duty). "For every shell-less lead dispatch, include `HARNESS-FEATURE-TREE-ROOT: <absolute
   path>` resolved once with `python3 <HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/inflight_registry.py
   feature-root --feature <FEAT>`; dispatch-guard.sh refuses its absence at exit 2."

`harness-handoff/SKILL.md:65-66` — MET. Carries the exception ("If your persona holds no shell,
do not run that command...") immediately beside the self-resolution command at line 65.

## D-06 direction rule at S1-S5, and `.claude/agents/**` sync

`test-anchor-directions.py` run with `HARNESS_REVIEW_SHA` pinned to the review sha: all 6
rows PASS, confirming S1 (qa-gate), S2 (expertise), S3 (handoff receipt), S4 (backend-dev
debugging-skill read), S5 (templates/PLAN.md team-config read) each carry the correct anchor at
the pinned commit. `sync-agent-adapters.py --check` exits 0 — `.claude/agents/**` is generated,
not hand-diverged.

## Findings, ranked

### F1 — HIGH, BLOCKING. `dispatch-guard.sh:145-153` — silent fail-open on an unreadable/malformed
persona file, contradicting the task's own intent and the file's own convention.

```
tools_file = os.path.join(owner_root, ".omp", "agents", dispatched + ".md")
raw_agent = open(tools_file, encoding="utf-8").read()
...
except Exception:
    has_bash = True
```

T-09's own intent (plan.yaml:855-857) requires: *"If the file is missing, unreadable, or carries
no tools: key, print one stderr line saying the tool grant for that persona could not be read and
PASS THROUGH."* No stderr line is printed. Every other fail-open branch in this same file prints
one (e.g. the "not a harness agent" branch at line ~63, whose comment literally reads "A gap of
OURS, said out loud rather than swallowed"). **Failure scenario:** a bad edit corrupts
`.omp/agents/harness-product-lead.md`'s frontmatter (missing `tools:` key, or the file goes
missing). Every subsequent dispatch to `harness-product-lead` is now treated as if it held `bash`
— the entire shell-less-refusal mechanism this feature adds is silently disabled for that persona,
and the operator has no stderr breadcrumb anywhere pointing at the cause. This directly undermines
REQ-06's own stated guarantee ("a persona left unable to resolve it is refused loudly rather than
left to guess a root") — here it is left to guess, and nothing says so.

### F2 — HIGH, BLOCKING. `inflight_registry.py:265-271` — `feature_root()` swallows
`AmbiguousWorktree` and silently collapses onto the control-plane root, defeating SC-10's own
stated guarantee.

```
def feature_root(owner_root, feature):
    try:
        resolved = harness_boundary.worktree_for_feature(owner_root, feature)
    except Exception:
        return owner_root
    return resolved if resolved is not None else owner_root
```

`worktree_for_feature`'s docstring (`harness_boundary.py:185-229`) is explicit: `AmbiguousWorktree`
exists so the resolver "never guesses" when two linked worktrees prefix-match one feature id.
`feature_root` catches it anyway and returns the control-plane root as if no worktree existed.
**Failure scenario:** a feature with two linked worktrees whose basenames both prefix-match
(`FEAT-90-alpha` and `FEAT-90-alpha-redo`, say) — `inflight_registry.py feature-root --feature
FEAT-90-alpha` silently prints the control-plane root instead of refusing. If a lead's dispatcher
runs that exact command to populate `HARNESS-FEATURE-TREE-ROOT:` (per `harness/SKILL.md`'s emit
duty), the dispatch carries the control-plane root; `dispatch-guard.sh:171-177`'s own comparison
(`reg.feature_root(owner_root, declared)`) computes the identical silently-wrong value, so the two
sides agree and the guard passes the dispatch. The lead's receipt and observations then land in
the control plane, off whichever worktree the feature is actually building in — invisible at that
worktree's `review_sha`, which is precisely the failure class D-06 exists to end. No test exercises
this branch (`test-inflight-registry.py` case35 has no ambiguous-worktree case).

### F3 — HIGH, BLOCKING. SC-13 has zero committed evidence — `dispatch-guard.sh`'s entire
shell-less-refusal mechanism is unverified.

`test-dispatch-guard.py` is byte-identical between the merge-base and the pin (508 lines, 0-line
diff both directions). None of T-09's four mandated cases (REFUSED / ALLOWED / DISCRIMINATION /
MISMATCH REFUSED) exist. This is the primary mechanism the feature relies on to keep the three
shell-less leads from guessing a write root (D-08), and it ships with no automated proof it does
what it claims, despite `verify: automated, evidence: integration` and `status: done`. The harness
already possesses the exact fixture-building helpers this task needed (`_checkout()`,
`fire(..., env=...)`) — the gap is not a missing capability, it is missing work.

### F4 — HIGH, BLOCKING. SC-06 (fifth path family, product-clone skill read) has zero committed
evidence.

`check-instruction-paths.py` and the five agent files anchor the debugging-skill path correctly
(confirmed by SC-04 row 4), but T-05's own mandated proof — that the anchored path actually opens
from a product-shaped cwd and the pre-change bare path does not — was never written into
`test-check-instruction-paths.py`. This is the one family the BRIEF calls out as producing "no
signal at all" when it fails; shipping it with no test is the exact risk profile the family exists
to close.

### F5 — MED, BLOCKING (bundles with F3/F4's pattern). SC-01, SC-02 (UNRESOLVED half), SC-08, and
SC-12 all have code that appears correct on manual inspection but no committed test proving it.

Manually verified at the pin (not committed anywhere): the UNRESOLVED branch of
`inject-expertise.sh` does emit `HARNESS_CONTROL_PLANE_ROOT: UNRESOLVED` and the exact
`VERDICT: BLOCKED` sentence, exit 0 — confirmed by invoking the script via process substitution
from a rootless cwd. The `HARNESS_PATH_DRIFT` mechanism and the CI wiring both read correctly on
inspection (`check-instruction-paths.py`'s `scope()`/`main()` derive `--list-scope` and the scanned
count from the same `scope(root)` call, so an empty-scope silent-pass is not possible; `.github/workflows/tests.yml:200-216`
is inside `integration:` and distinguishes exit 1/2/missing-summary correctly). None of this is
disputed as *broken* — it is reported here because `verify: automated` names a committed artifact,
not a reviewer's manual confirmation, and a later edit to any of these branches has nothing
red to catch it. Ranked below F1-F4 because the underlying mechanisms are demonstrably functional
today, unlike F1/F2 which are live defects, and F3/F4 which cover the two mechanisms with the
widest blast radius (every dispatch; every product-clone doer).

### F6 — LOW, non-blocking. `check-instruction-paths.py:26` `scope` and `:62` `violations` grade 1
(cognitive 31 and 52 respectively, bar 4) — both new functions, code-grade FAIL/high.
`inflight_registry.py:635` `main` grades 1 (ABC 45.4, bar 4) — a worsened regression from this
feature's `feature-root` verb addition, FAIL/high. `check-instruction-paths.py:90` `main` grades 2
(cyclomatic+cognitive+abc, bar 4) — REASON: it is the CLI's single argument-dispatch function;
splitting scan-selection from the print/exit-code loop would relocate, not remove, the complexity
of "which files, what happened, what to print" and every sibling `bin/*.py` CLI entry point in
this codebase keeps that shape. Not `must_fix` — style/maintainability, not a behavioral gap — but
worth a follow-up given `violations()` and `scope()` are exactly the functions this review's
Stage-1 findings turn on being correct.

Test-code grade-1 records (`test-anchor-directions.py:41 main`, `test-inflight-registry.py:1081
main`, both ABC-driven, bar 3) and grade-2 records (`test-check-instruction-paths.py:26 main`,
REASON: linear sequence of independent fixture-and-assert blocks, the ABC total is fan-out breadth
not nested logic; `test-inflight-registry.py:1016 case_35_feature_root_cli`, REASON: five
sequential CLI-subprocess assertions in the sibling suite's established one-function-per-case
style) are noted for completeness; per policy these never gate on their own.

`code_grade: fail` (four blocking high-severity records exist in the reviewed range;
`merge-base` used for this run matches what `validate-digest.py` will independently recompute).

## Not re-raised (already-known / out of scope per dispatch)

`check-state.sh` VIOLATION lines (FEAT-51/BUG-1033, worktree-only), the 6 `team-config.yaml`
DEVIATION sub-cases (environmental), the deliberate absence of `HARNESS_FEATURE_TREE_ROOT` from
`harness-backend-dev.md`'s adapter file, the untracked feature directory, and `STATE.md`'s stale
status — all per the dispatch's explicit ruled-list.

## Verdict

**FAIL.** `must_fix` = {F1, F2, F3, F4}, each independently sufficient (severity_max: high).
F5 bundles four further unmet criteria at med severity and is also blocking per the stated
acceptance rule ("FAIL if any success criterion is unmet"). Recommend routing back to the
implementer: F3/F4/F5 are pure test-writing gaps against code that in several cases already works
(cheap to close); F1 needs one `print(..., file=sys.stderr)` line; F2 needs `feature_root` to
either propagate `AmbiguousWorktree` to its caller (who already fails open with a stderr line at
`dispatch-guard.sh:172-175`) or print its own diagnostic before falling back — not silently.
