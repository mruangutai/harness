# Build ruling by delegated authority — FEAT-2337 — 2026-11-22 — merge-gate timeout

Authority: the operator's delegation (`notes/answers-2026-11-22-signoff.md`). Ruled by
`fable-advisor` (`AdvisorB5MergeGate`). Raised by the T-03 builder.

**Gap.** T-01 lists merge-gate.py in `BASH_GATES`, but it is in neither `NARROW_GATES` nor
`BROAD_GATES`, so `classifyPolicyRun` applies the helper convention. A merge-gate killed at
`POLICY_TIMEOUT_MS` (30 s) therefore returns a non-blocking reason, and `git merge` / `gh pr merge`
proceeds unchecked. The bypass is reachable in practice: merge-gate's own subprocess budget is
60 s, and its `gh pr view` call has no timeout. Before FEAT-2337 a hung merge-gate hung the session
instead. The grilling settled that "a timeout means what that gate's own failure means under
DEC-100", and merge-gate's own-failure convention is fail-closed.

**Ruling: A**, a recorded deviation within signed scope. merge-gate.py joins `NARROW_GATES` with a
TS applicability classifier, so a timeout or abnormal exit refuses only a matching merge command;
unrelated Bash stays allowed.

1. **merge-gate.py itself is untouched.** It stays bootstrap-first per DEC-234 and keeps its
   exit-2 fail-closed convention. It does not gain stdlib-first applicability; the fix is entirely
   on the TS side.
2. **The classifier must not be `mainMergeGate`'s `\bmerge\b` word prefilter**, which also matches
   `git merge --abort`, `rg merge src/` and `echo merge`. Port merge-gate.py's `merge_ref` logic:
   direct gh/git detection, nested to depth 3, and the `--abort` / `--continue` / `--quit`
   exemptions in `merge_target`. The word prefilter may remain as a cheap pre-screen at most.
3. **Corpus agreement.** `tests/integration/test-merge-gate.py` gains an `APPLICABILITY_CORPUS`.
   It is an out-of-list path, approved by this ruling. Its Python leg runs against a healthy root,
   because merge-gate refuses everything on a broken root. The runtime suite checks agreement
   between the TS classifier and merge-gate.py, as it does for the other three narrow gates.
4. **Explicit tests.** A guarded merge is refused on timeout; unrelated Bash is allowed on timeout.
5. **Docs.** T-03's DEC-100 (DECISIONS.md ~1404-1408) contradicts itself on merge-gate. Rewrite
   both sentences in place: merge-gate is a narrow gate, its process failures and timeouts refuse
   only the matching merge, and its own caught failures exit 2. Update SPEC §4.2 to match.
