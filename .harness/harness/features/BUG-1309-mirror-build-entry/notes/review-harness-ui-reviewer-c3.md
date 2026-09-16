# UI Review — BUG-1309-mirror-build-entry — cycle 3 (Mode B, pin 0f8ec4bd)

## Verdict: PASS — no rendered UI surface; one MED advisory on the new catch-all deny message, non-gating

## Measured census (this commit only, per dispatch's target: "ONE remediation: commit 0f8ec4bd")

`git show --stat 0f8ec4bda7c96050d2d9bcddb30f96132cde5b54`: 2 files —
`.claude/skills/harness/bin/merge-gate.py` (+26/-23) and `tests/integration/test-merge-gate.py`
(+12/0). Extension census: **2 `.py` hits, 0** for `html|htm|css|scss|sass|less|jsx|tsx|vue|svelte`.
No new/changed `DESIGN.md` anywhere in this commit or under this feature's directory (confirmed at
c0/c2, unchanged). **No rendered UI surface in this diff** — matches repo Expertise P-01.

## The one surface the dispatch named: the new catch-all deny message

Per dispatch, checked the operator-facing text this commit adds. Full diff read at
`.claude/skills/harness/bin/merge-gate.py:118-154` (raw). The remediation wraps the whole
post-`merge_ref` body of `main()` in `try/except Exception`, and the new `except` clause
(line 153-154) calls:

```
deny("merge-gate: could not evaluate this feature's Build-entry receipt, so this merge is denied. Repair the feature record and re-run the merge.")
```

**No `DESIGN.md`/UI contract governs this repo's hook output.** The applicable "equivalent
contract" is a repo-wide house convention, evidenced by two independent precedents in the same
`bin/` directory, both authored for this same mirror/receipt system:

- `validate-digest.py:1016-1017` — `except (OSError, ValueError) as exc: return f"pre-signature
  feature record {feature_json!r} is unreadable ({exc})."` — names the exact path AND the
  exception.
- `gh-sync.py` — five separate `except Exception as e` operator-facing messages
  (lines 232, 282, 1590-1592, 2042, 2107-2116, 2163-2164) — **every one** interpolates `{e}`
  (the caught exception text) into the printed/denied reason.

`merge-gate.py`'s own pre-existing style matches this: every other `deny()`/`print(...,
file=sys.stderr)` call in this file interpolates the concrete fact that drove the branch
(`{failure}`, `{feat}`, `{value}`, `{command_line}`). DEC-100 (`DECISIONS.md:1370`) independently
establishes the bar for this repo's hook messages generically: a message must "tell the reader
what to do differently," not merely restate the fact.

**Finding — MED, non-gating.** The new catch-all message clears DEC-100's bare-minimum bar (it
does say what to do: "repair … and re-run"), but it is the only `except Exception` in this file or
its two closest siblings that (a) doesn't bind the exception to a name (`except Exception:`, not
`as e`) and (b) doesn't interpolate anything into the operator-facing text — no path, no field, no
exception detail. Concrete failure scenario, drawn from the diff's own new fixtures: for
`test-merge-gate.py`'s new "T-05 empty plan fails closed" case, the artifact that is actually
broken is `plan.yaml` (empty file → `feature_schema.recovery_command_for`'s `plan.get(...)` on
`None` raises `AttributeError`, per `feature_schema.py:329-333`); for "T-05 non-object feature
record fails closed," the broken artifact is `feature.json` (a JSON array, so `document.get(...)`
raises `AttributeError` in `feature_for`, `merge-gate.py:98-104`). Both land on the byte-identical
message "Repair the feature record." An operator seeing that text after the plan.yaml case has no
signal steering them toward `plan.yaml` over `feature.json` — the one prior use of "feature
record" in this codebase (`validate-digest.py:1017`) ties that exact phrase to `feature.json`
specifically, which would send them to inspect the wrong file first.

**Why this doesn't gate:** it is a diagnosability/consistency gap in operator CLI text, not an
accessibility exclusion, not a misrepresentation of the fail-closed posture, and not a defect in
the posture this cycle exists to grade — the DEC-138-vs-internal-error separation itself is
correct and unchanged by this finding (confirmed: the GitHub-outage branches at lines 133 and
139-141 are untouched by this commit, still fail OPEN with the DEC-138 wording, still outside the
new `try`'s reach for that specific print-then-return path... actually they ARE inside the new
`try` block now, but neither raises, so behavior is unaffected — read the whole function, no
regression there). This is advisory polish consistent with the file's own established style, not a
must-fix.

## Accessibility / theme parity

Not applicable — no rendered surface, no colour, no theme in this diff. (Per project Expertise
G-02, stated explicitly rather than omitted.)

## Open questions
None.
