# Receipt — T-02, main session (DEC-174 direct) — 2026-11-27

Run at the worktree tip after T-01 (0b92e4cb), HARNESS_AGENT_TYPE unset.

## verify (verbatim from plan.yaml T-02)

```text
T-02 decisions PASS
exit=0
```

The `--stdout | diff` half printed nothing. `gen-decisions-index.py` rewrote one index row: DEC-259's derived tags moved from `[plan,state,dispatch,skills]` to `[plan,state,dispatch,domain]` because its Because text changed. Its ruling text is unchanged.
