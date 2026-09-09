# Security review c3 — BUG-1309-mirror-build-entry — review_sha 0f8ec4bda7c96050d2d9bcddb30f96132cde5b54

## BLUF
**FAIL — one HIGH.** The DEC-138-vs-internal-error posture is correctly preserved (verified by
reading the diff line-for-line: it is a pure indent-and-wrap, zero logic changed). But the new
`try/except Exception: deny(...)` wrapping `main()`'s body routes a **pre-existing, unrelated-feature**
bug in `feature_for()` into a **repo-wide** merge lockout: a malformed `feature.json` belonging to
*any* feature anywhere in the tree — not the one being merged — can now deny merges for every other,
perfectly compliant feature, indefinitely, with a deny message that misattributes the fault to "this
feature." Demonstrated by direct execution below, not inferred.

## The four questions, answered

**1. Bypass direction (DENY → ALLOW, or a decision escapes emission) — PASS, none found.**
The new `try` wraps the *entire* post-`merge_ref` decision body; its `except` clause only ever calls
`deny()`. Every one of the pre-existing ALLOW returns (`document is None`, era-exempt, `entry in
{opened, not-applicable, recovered-terminal}`) is a normal `return`, not an exception — it exits before
the `except` can fire, so no ALLOW path was reclassified. `git show 0f8ec4bd -- merge-gate.py` confirms
this by construction: every changed line is either the added `try:`/`except Exception:` pair or an
existing line re-indented one level, byte-identical text otherwise. No decision point was moved,
reordered, or dropped between the merge-command-identification point and `main()` returning.

**2. DEC-138 posture (failed GH read → ALLOW; internal error → DENY) — PASS, preserved exactly.**
The DEC-138 "could not verify… allowing it" print-then-return sites (`:133-136`, `:142-145`) are now
*textually* inside the new `try`, but neither raises — they're unconditional `return`s — so they are
unaffected by the `except`. The refusal-decides-on-the-LOCAL-record posture (a GH outage never
overrides a locally-owed receipt) is unchanged: same code, same order, only re-indented. This
mechanically closes the specific question this cycle exists to grade.

**3. Injection / trust boundary — PASS, no widening.** No new argument, environment value, or shell
construct is passed to `subprocess.run` (`gh_head`, `local_branch`) or to a shell; those call sites
are untouched by the diff (same argv list, same call sites, only enclosing indentation changed).

**4. Information exposure — PASS, and slightly improved.** The new catch-all `deny()` message
(`merge-gate.py:154`) is a fixed string with **no interpolation at all** — no path, no exception
text, no traceback, no `gh` output. It is the only `deny()`/`print()` site in the file that
interpolates nothing (contrast `{failure}`, `{feat}`, `{value}`, `{command_line}` elsewhere) — a
conservative choice that avoids leaking whatever internal detail *caused* the exception. (The UI
reviewer flags this same fact from the opposite angle — MED, non-gating — as a diagnosability gap,
not an exposure risk; the two findings are compatible, not contradictory: less detail is safer here
but harder to debug.)

**5. Denial-of-service direction — FAIL, HIGH. Demonstrated by execution, not argued.**
`feature_for()` (`:98-104`, unchanged by this diff) scans **every** `feature.json` under
`ROOT/.harness/*/features/*/feature.json` on **every** merge attempt, for **every** feature, checking
`document.get("branch") == branch`. Its per-file `try/except (OSError, json.JSONDecodeError): continue`
only catches read/parse failures — a file that parses as valid JSON but is not an object (e.g. `[]`)
sails through the `except`, and the very next line, `document.get("branch")`, raises `AttributeError`
on *whichever* glob entry glob happens to visit that has this shape — regardless of whether that
entry belongs to the feature actually being merged.

I reproduced this directly (temp fixture, real `merge-gate.sh`/`merge-gate.py` at this pin, no repo
files touched):
- Feature `FEAT-A-fixture`, branch `feature/test`, `build_entry: "opened"` (would ALLOW on its own).
- Feature `FEAT-B-unrelated` (different branch, not being merged), `feature.json` = `[]` (valid JSON,
  non-object — the same shape the diff's own new "T-05 non-object feature record fails closed" test
  uses, but for a file that isn't the one being merged).
- `git merge feature/test` against this tree → **denied**:
  `{"hookSpecificOutput":{...,"permissionDecision":"deny","permissionDecisionReason":"merge-gate:
  could not evaluate this feature's Build-entry receipt, so this merge is denied. Repair the feature
  record and re-run the merge."}}`
  — for a feature (`FEAT-A-fixture`) whose *own* record is entirely valid and would allow.

**Before this diff**, the identical corrupt-`FEAT-B` scenario hit the same `AttributeError`, but with
no enclosing `try/except` in `main()` it propagated uncaught out of `main()`: the hook process exits
non‑2 (an unhandled exception, not `sys.exit(2)`), which per this repo's own established posture
(only `exit 2` blocks a hook — G-01) is **non-blocking**: the merge would have silently been
**allowed**, with a traceback on stderr nobody is required to read. The fix is directionally correct
(an internal error should not silently permit), but it converts a narrow, single-invocation, silent
bypass into a **repo-wide, persistent, cross-feature merge lockout**: one bad `feature.json` —
anywhere, including a long-dormant, already-shipped feature nobody is looking at — now blocks every
future merge for every feature in the project until someone finds and repairs it, and the emitted
message actively points them at the wrong file ("this feature's Build-entry receipt", when the
actual broken record belongs to a different feature entirely).

I confirmed no such landmine exists in this repo's *current* `.harness/*/features/*/feature.json` set
today (scanned all of them: none are non-dict). This is a design/blast-radius defect, not evidence of
an active incident.

**Threat framing:** no privilege escalation is required — the actor who corrupts `FEAT-B`'s record
(deliberately, or by an ordinary bug/interrupted write/bad merge-conflict resolution) does not already
control `FEAT-A`'s merge outcome; after the corruption, they effectively do. That is exploitable by a
user (or a mistake) against another user/feature's ability to merge at all — the severity table's
"high: exploitable by a user of the system against another user or the system."

**Why the obvious one-line fix isn't safe to prescribe here:** narrowing `feature_for`'s per-file
catch to also swallow a non-dict document (e.g. `isinstance(document, dict) and document.get(...)`)
would fix the cross-feature case, but it would silently make the *matching* feature's own malformed
record undetectable too (it would just never match → `document is None` → falls to the ALLOW branch),
which is exactly the regression this whole fix exists to close and exactly what the new
"non-object feature record fails closed" test pins against. The real remedy has to distinguish "the
document that matches my branch is itself malformed" (must stay fail-closed) from "a document
belonging to some other branch is malformed" (must never affect my merge) — that's a real design
decision for engineering, not a one-line patch, so I'm naming the requirement rather than prescribing
the diff.

## Threat model

| boundary | STRIDE | mitigated |
|---|---|---|
| exception after merge-command identification → decision | Tampering (fail-open→fail-closed conversion) | true — no bypass; only ever produces `deny` |
| DEC-138 GH-read-failure vs internal-error separation | Tampering | true — identical logic, unchanged by the wrap |
| catch-all deny message content | Information disclosure | true — zero interpolation, nothing to leak |
| subprocess/`gh` argv construction | Injection | true — untouched by this diff |
| cross-feature `feature_for()` glob scan + new fail-closed wrapper | Denial of service | **false** — demonstrated: one unrelated feature's malformed `feature.json` denies every merge, repo-wide, indefinitely |

## Assessed and dismissed (not findings)
- Both cycle-0 highs, the cycle-2 HIGH this commit fixes, the signed refusal/era/recovery-terminal
  posture, the four grade-2 functions, ship backlog B-1..B-6 (checked `STATE.md:23-26` directly — none
  of B-1..B-6 mention `feature_for`'s glob scan or cross-feature corruption): not re-raised, per the
  dispatch's settled list.
- The UI reviewer's MED (message doesn't say *which* file broke, for the single-feature case): a
  different, narrower question than mine (diagnosability within one feature vs. cross-feature blast
  radius) — compatible, not overlapping; not restated here as my own finding.

## Findings
1. **HIGH — Cross-feature denial of service via `feature_for()`'s full-tree glob scan routed into the
   new fail-closed wrapper.** `merge-gate.py:98-104` + `:129-154`. A malformed (valid-JSON,
   non-object) `feature.json` belonging to *any* feature in the repo denies merges for *every* other
   feature, with no diagnostic pointing at the actual broken file, until an operator finds and repairs
   it by inspection. Demonstrated by direct execution against this pin. Remedy requires distinguishing
   "the matched document is malformed" (correctly fail-closed) from "an unrelated document is
   malformed" (must never affect the decision) — an engineering design call, not prescribed here.

## open_questions
None blocking — this is a routing decision for engineering (how to make `feature_for` distinguish
"my own record is bad" from "someone else's record is bad" without reopening the fail-open gap the
new tests just closed), not information I lack.
