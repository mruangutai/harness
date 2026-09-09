# Code review c6 — BUG-1309 ownership decision table — merge-gate.py @ 894adc0f

## Stage 1 — spec compliance: PASS

Diff at pin (`894adc0f^..894adc0f`, `.claude/skills/harness/bin/merge-gate.py`, +7/-11) rewrites
`feature_for` so **usability is a precondition of matching**, not a separate flag: a record can be
"matched" only via `isinstance(document, dict) and document.get("branch") == branch`
(merge-gate.py:100-108). This traces directly to SC-04's "every deny is earned by the LOCAL
receipt" and REQ-07 — the previous `unusable` scan-wide sentinel (cycle 5) denied merges on the
strength of an UNRELATED feature's malformed record, which was never "earned by the LOCAL receipt"
of the branch actually being merged. The fix is narrowly scoped to `feature_for` and the one
`if document is None:` clause in `main()`; nothing else changed. No scope creep, nothing missing
for this narrow repair.

## Stage 2 — code quality

### Enumeration (one fixture, `/tmp/mg_enum.py` + `/tmp/mg_enum2.py`, driven through `merge-gate.sh`
exactly as the PreToolUse contract feeds it — hook JSON on stdin, `HARNESS_PROJECT_DIR` env,
`GH_BIN` for the gh seam)

Axes: (1) command form, (2) remote read (gh-only), (3) branch matched by usable record, (4) own
record shape, (5) foreign unusable record present, (6) receipt state.

| # | command | remote read | own record | foreign unusable | receipt | exit | decision | note |
|---|---|---|---|---|---|---|---|---|
| existing T-05×19 | all forms | n/a/ok/fail | healthy/absent | present/absent | all 5 states | 0 | allow/deny | already green, validator-lead-confirmed; not re-run |
| A1 | git merge | n/a | **non-dict** | absent | n/a | 0 | **allow (silent)** | own-branch record unattributable → treated as no-record |
| A2 | git merge | n/a | **unparseable bytes** | absent | n/a | 0 | **allow (silent)** | same as A1 via JSONDecodeError |
| A3 | git merge | n/a | non-dict (1st glob hit) + healthy owed (2nd dir, same branch) | — | owed | 0 | **deny**, names the healthy dir | proves a healthy same-branch record still wins regardless of scan order |
| B1 | git merge (no branch arg) | n/a | healthy/absent(n/a) | — | — | 0 | **deny, `feat="this feature"`** | `local_branch()` raises `FileNotFoundError` (git unresolvable via PATH) before `feat_dir` is set; caught by outer `except Exception` |
| B2 | gh pr merge 7 | fails (gh also unresolvable) | — | — | — | 0 | **deny, `feat="this feature"`** | same mechanism via the gh→local_branch fallback |
| B3 (control) | git merge (no branch arg) | n/a | healthy | — | owed | 0 | deny, names FEAT-9001 | normal PATH: `local_branch` resolves fine, feat correctly named |
| C1 | git merge | n/a | healthy, entry absent | — | plan.yaml **empty** (parses to `None`) | 0 | deny, `feat="could not evaluate FEAT-9001..."` generic wording | `recovery_command_for`'s `plan.get(...)` raises `AttributeError` on `None`; caught by outer except — still fails **closed**, feat is correctly named here (exception fires after `feat_dir` set) |
| C2 | git merge | n/a | healthy, entry absent | — | plan.yaml **absent** | 0 | deny, names command `recover-terminal` | `harness_yaml.load_file` raises → caught *inside* `recovery_command_for` → safe default |
| D1 | git merge | n/a | non-dict | — | n/a, repo **unpinned** | 0 | **allow (silent)** | repo-unpinned D-09 deny is never reached — `document is None` short-circuits first |
| E1 | git merge | n/a | non-dict, **era-exempt feature name** | — | n/a | 0 | **allow (silent, no stderr)** | era-exempt informational message also never reached (same short-circuit) |
| F1 | git status | n/a | non-dict | — | n/a | 0 | allow | non-merge command never calls `feature_for` at all |
| G1 | git merge | n/a | non-dict | — | sync **false** | 0 | allow | sync-off short-circuit, `feature_for` never called |
| H1 | git merge | n/a | — | — | harness.json malformed | 0 | allow (silent) | outer `except Exception: return` — pre-existing, unrelated to this diff |
| I1 | gh pr merge 7 | **fails** | healthy | — | held (`opened`) | 0 | allow, DEC-138 stderr | exercises the *second* copy of the "could not verify…" message |
| I2 | gh pr merge 7 | succeeds | healthy | — | held (`not-applicable`) | 0 | allow (silent) | remote read success + held entry |

**Unreachable combinations, with the structural reason:**
- *"branch matched by a usable record" ∧ "that record is unusable"* — **impossible by construction.**
  `feature_for`'s match condition is `isinstance(document, dict) and document.get("branch") ==
  branch`; a non-dict or unparseable record fails `isinstance(...)` and is `continue`d before the
  branch comparison ever runs, so it can never be the thing that "matches." Verified: A1/A2/D1/E1
  all reduce to the identical no-record allow path.
- *remote-read axis × command form = git* — the gh-only axis never applies to a `git merge` command:
  `head_branch` returns on `kind == "git" and value` before any `gh_head` call exists in that branch
  (merge-gate.py:88-94).
- *era-exempt = yes ∧ repo-unpinned deny fires* — the era-exempt `return` (merge-gate.py:141-143)
  is unconditional and precedes the repo-pin check; an era-exempt feature can never reach the D-09
  deny regardless of its actual `github.repo` value.
- *era-exempt = yes ∧ own record unusable* — reachable (E1) but the era-exempt informational stderr
  line is *not* reached either, since `document is None` returns first. Same short-circuit as D1.

### Direct answers

**(a) Does any input let an unattributable record still influence the outcome? NO**, verified.
A1/A2/D1/E1 all show a non-dict or unparseable record — whether it is the *current branch's own*
record or a foreign bystander (already covered by the shipped suite's "unrelated non-object … does
not block" and "no-record branch ignores unrelated malformed record" cases) — is always reduced to
exactly the same outcome as if no record existed for that branch at all: silent allow (or an allow
with only the DEC-138 stderr note if gh resolution also failed). A3 additionally shows a healthy
matching record elsewhere in the same glob scan is *not* shadowed by an earlier malformed hit — so
the fix is genuinely symmetric, not merely "foreign records don't block."

**(b) Does any input produce a DENY naming no feature an operator can act on? YES**, verified
(B1/B2). When `git`/`gh` is unresolvable via `PATH` (an unusual but real misconfiguration — a
stripped hook environment, a broken shell profile), `local_branch()`'s bare `subprocess.run(["git",
…])` raises `FileNotFoundError` from inside `head_branch()`, called *before* `feat_dir` is
assigned. `main()`'s outer `except Exception:` (merge-gate.py:155-156) then denies interpolating
the `feat = "this feature"` seed set at merge-gate.py:132 — literally `"merge-gate: could not
evaluate this feature's Build-entry receipt…"`. No feature ID, no path, no re-run command. The
merge is still refused (fails **closed**, not open — no security bypass), but the operator has
nothing to act on.

**Novelty check (894adc0f^):** both (b)'s mechanism and its exact wording are present, unchanged,
in the parent commit — `git show 894adc0f^:.claude/skills/harness/bin/merge-gate.py` has the
identical `feat = "this feature"` seed, the identical unguarded `local_branch()`, and the identical
terminal `except Exception: deny(f"...{feat}'s Build-entry receipt...")`. **This is pre-existing,
not introduced by this pin's rewrite** — the diff touched only `feature_for` and the
`document is None` branch, neither of which is on the path that reaches this. Flagging per the
explicit dispatch instruction to construct and report it, not as a regression.

### Table vs. four patches (dispatch Q4)

The **ownership predicate** — does a usable record own this branch — is now expressed exactly
once, in `feature_for` (merge-gate.py:100-108), and no reachable state is decided in more than one
place: each of `main()`'s five ordered exits (no-record / era-exempt / held / repo-unpinned /
owed) covers a disjoint state and none overlaps (era-exempt precedes and pre-empts repo-unpinned
by construction — see unreachable list above; that is deliberate design, not diffusion of the same
decision). This is a genuine single-point fix, not four patches wearing one.

One real but minor byte-for-byte duplication survives, **pre-existing (unchanged by this pin)**:
the DEC-138 "could not verify this merge…" f-string is copy-pasted verbatim at merge-gate.py:136-137
and :145-146 (confirmed via I1: the second site fires under `entry="opened"` + gh failure). At the
second site the phrase "owes no build-entry receipt" is slightly inaccurate — the record is
actually *held*, not owed — a message-wording nit, not a decision-logic split.

### Code grade

`code-grade.py --base $(git merge-base origin/main 894adc0f) --head 894adc0f`: 50 passing.
4 grade-2 functions fail their bar but each already carries an in-source `GRADE-2 REASON:` comment
(merge-gate.py:120 for `main`; test-check-state.py:4619, test-hooks-install.py:392,
test-post-merge-sweep.py:883) — all four reasons predate this pin (unchanged context lines in the
diff). No grade-1 and no below-bar-non-grade-2 function anywhere in range → `code_grade: grade_2`,
not `fail`.

## Findings (none gate)

1. **[med, pre-existing]** merge-gate.py:69-72 (`local_branch`) + :132,155-156 (`main`) — an
   unresolvable `git`/`gh` binary raises before `feat_dir` is set, producing a DENY that names
   literally "this feature." Fails closed (safe), but unactionable. Reproduced live (B1/B2);
   present unchanged at 894adc0f^, so out of scope as a regression for this pin but live in the
   file under review.
2. **[low, pre-existing]** merge-gate.py:136-137 / :145-146 — the DEC-138 stderr message is
   duplicated verbatim across two call sites; the second occurrence's "owes no build-entry receipt"
   wording is inaccurate when the record is actually held. Cosmetic; unchanged by this pin.

## Verdict

Stage 1 passes; Stage 2 has no high/critical findings and no must_fix. `severity_max: med`,
driven by finding 1 (pre-existing) and the reasoned grade-2 functions, none of which gate.
