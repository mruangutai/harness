# Security review — BUG-1309-mirror-build-entry — cycle 5 (pin 473d82cb)

## Verdict: FAIL — severity_max=high, must_fix=2

Both directions asked for were judged and executed against a live fixture (`bash .claude/skills/harness/bin/merge-gate.sh`, `HARNESS_PROJECT_DIR` pointed at a tmp repo). LOOSER is clean. TIGHTER is not: the sentinel is a global boolean across the *whole* repo scan, not scoped to the target branch's own record, and it is only set for one of several malformed-record shapes. That produces one new false-DENY class and leaves one false-ALLOW class open that this very fix claims to close.

## F1 — HIGH — cross-feature false DENY (new, induced-on-healthy-repo)

`.claude/skills/harness/bin/merge-gate.py:98-108` — `unusable` accumulates across **every** `feature.json` the glob reaches (all features, all repo segments), not just the one matching the branch being merged. `:139` denies whenever `document is None and unusable`, with no attribution of *which* record was unusable.

**Executed** (`/tmp/sec_c5_repro.py`): repo with two features — A: healthy, tracked, branch `feature/test` (unrelated to the merge under test); B: malformed `feature.json` = `[]` (also unrelated). Merged branch `other`, which has no feature record of its own at all — pre-473d82c this silently allowed (untracked branch, correct). Result at this pin: `rc=0, decision=deny, reason="merge-gate: could not evaluate a feature's Build-entry receipt, so this merge is denied. Repair the malformed feature record and re-run the merge."` — a merge with **zero relationship** to feature B is blocked by feature B's corruption. The reason names no feature, giving the operator no lead to the actual broken file.

Blast radius: any one malformed/bootstrap-state `feature.json` anywhere under `.harness/*/features/*/` blocks **every** merge in the repo whose branch isn't itself a currently-tracked healthy record — including ordinary untracked branches (dependency bumps, hotfixes). This is the DoS shape the dispatch asked to press on, and it reproduces on the first try, no adversarial timing needed. It also broadens past JSON-shape malformation: a huge file anywhere in the scan that raises `MemoryError` (not caught by `except (OSError, json.JSONDecodeError)`) propagates to the outer catch-all at `:159` and denies unconditionally for the same reason, same blast radius.

Threat: STRIDE-D. Actor: anyone/anything (including an ordinary bug in another script, not just an attacker) able to write one `feature.json` in one feature directory gains an incidental veto over every other feature's merges.

## F2 — HIGH — false ALLOW persists on the target's own broken record (fix is incomplete, not a re-litigation)

`.claude/skills/harness/bin/merge-gate.py:100-102` — `except (OSError, json.JSONDecodeError): continue` treats a torn/truncated write, a permission-denied file, or a directory literally named `feature.json` as **invisible**, not as `unusable`. Only a *parseable-but-wrong-type* document (`[]`, `null`, a scalar) sets the sentinel.

**Executed** (`/tmp/sec_c5_repro2.py`): target branch's *own and only* `feature.json` (a) truncated mid-object, (b) `chmod 0000` — both: `rc=0, decision=None, stderr=""`. Silent allow, in both cases, of a merge for a feature that (per the fixture) owes a Build-entry receipt. This is exactly the failure mode 473d82c is titled to close ("reject unusable target record") — closed for one malformed shape, open for two others that are at least as easy to produce.

Two reachable actors: (1) an ordinary process crash or non-atomic write mid-flight on a *legitimate* update to the target's own record — the torn write the dispatch asked about is real and it fails open, not closed; (2) a developer/agent who owes the receipt and wants to merge anyway has a one-line bypass of their own gate: truncate or `chmod 000` their own `feature.json` before merging. Either way the control the whole BUG-1309 line exists to enforce is defeated.

Threat: STRIDE-T (tampering with, or accidental corruption of, the gate's own input defeats the gate).

## LOOSER direction — clean, verified

Malformed records cannot mask a healthy match: the branch-equality check (`document.get("branch") == branch`, `:106`) only runs on values that already passed `isinstance(document, dict)` — a non-dict record never reaches it, so it can never impersonate a different branch's record. When a healthy match *is* found, the function returns `unusable=False` explicitly (`:107`), discarding any `unusable=True` seen earlier in the same scan — order-independent by construction, not by luck. Confirmed by code trace plus the existing, still-passing fixture case ("T-05 unrelated non-object feature record does not block healthy merge" in `tests/integration/test-merge-gate.py`). No crafted or corrupted `feature.json` anywhere lets a merge that should DENY instead ALLOW.

## Data exposure — clean

New deny string (`:140`) is a fixed sentence; no path, token, repo name, or document content is interpolated. Pre-existing DEC-138/era/repo-pin stderr lines are unchanged by this diff and were already assessed in prior cycles (not re-litigated here).

## Input-shape census (Q4)

| shape | classified | outcome |
|---|---|---|
| JSON list / scalar / `null` (valid JSON, wrong type) | `unusable=True` | contributes to F1/covered by intended fix |
| truncated / invalid JSON | silently skipped, not unusable | F2 — false allow if it's the target's own record |
| unreadable (chmod 000) | `PermissionError` → silently skipped, not unusable | F2 |
| directory named `feature.json` | `IsADirectoryError` → silently skipped, not unusable | F2 |
| huge file (`MemoryError`) | uncaught, propagates to outer catch-all | F1 (denies unconditionally, any branch) |
| symlink to a FIFO/slow device | `open()` follows it; a stalled reader hangs the hook | not executed — same write-domain as the rest, lower priority; flagged as hardening only (info) |

## Not re-raised (settled per dispatch)

`gh_head` OSError fail-open, era bypass on absence, internal-error fail-open, prior bystander lockout (crash-based), silent-allow-on-`[]` (now closed) — all pre-existing/settled, not restated. F1 and F2 are new/incompletely-closed variants of the same failure family, distinguished above by concrete execution, not restatement.

## Recommendation (not a mandate — routing is the lead's call)

Scope `unusable` to the target branch's own candidate record (e.g., only set it for a record whose directory/branch cannot be ruled out, or track "was the target's branch's record itself unusable" instead of a scan-wide OR), and widen the unusable classification to cover parse/read failure, not only wrong-type — the two fixes are likely one change to `feature_for`'s control flow.
