# Batch A — main-session execution record — 2026-08-11

The DEC-174 carve-out tasks, executed directly by the main session. Narrative belongs here, not in
the handoff note: a handoff is intent, trust, dead ends and a working set, and the shape gate
caught the mistake at 85 lines against its 60 cap.

**gh-sync ran BEFORE T-04, on the operator's ruling.** 12 sub-issues #264-#275 under #204,
`parent_origin: adopted`, milestone 8. The #252 defect — creating a parent instead of adopting one —
did NOT recur, but only because `--parent 204` was passed explicitly. The bug is dormant, not fixed.

**T-02 defect: its intent and its verify contradict each other.** The intent mandates the combined
command `python3 -m pip install pyyaml jsonschema`; the verify greps the literal substring
`install jsonschema`, which the combined form does not contain. **Written exactly as the signed
intent specifies, T-02 fails its own signed verify.**

Resolved without weakening the intent: the gate stays ONE gate, the combined command stays, and a
genuinely useful extra line was added (only one package missing -> install just that one) which
also carries the literal. This is eng-lead's G-04 shape — when a verify greps a literal string, the
work must carry that string even where the prose form reads better.

Backlog candidate, not this feature's to fix: a `verify:` whose literal cannot be produced by its
own `intent:` is undetectable at plan time. `check-plan-routes.py` checks routing and budget, not
whether a task's two halves agree.

**T-02 result:** verify exit 0. Two probe lines, ONE STOP gate covering both packages. CLAUDE.md at
75 lines against its 80 budget; the shape gate accepts it at exit 0.
