# UI design-check — FEAT-58 plan draft — CLI/hook operator surface

Mode: **A** (pre-build; grading the drafted contract in `plan.yaml`, not built code).

**Conclusion first: FAIL.** Two HIGH findings on the same seam — the six named exits in
`worktree-state.py` (T-03/D-10) never require the `--verify` message to name the concrete remedy
per exit, and critically never forbid a uniform "run `--repair`" message that would be **actively
wrong** on the one exit (8, dirty tree) `--repair` explicitly declines to fix. That same gap
propagates into the automatic hooks (T-12/T-16): when a shim's delegate exists but
`worktree-state.py --repair` itself fails, `exec` passthrough means the raw, unattributed exit
code and message become the hook's own output, and no test exercises that shape — only the
"delegate missing" shape is tested. Both are cheap to close at the spec level (message-content
requirements, one more T-16 case); neither is a rebuild.

## 1. The six named exits (T-03, D-10) — DEFECTIVE, severity HIGH

`{id: F-01, severity: high}` — T-03 pins six distinct **exit codes** (3–8) and requires six
pairwise-distinct **reason tokens**, and requires `--verify` to "print one line naming that check
and what it observed." That specifies *what* is wrong per exit. It never specifies *which command
resolves it* — and the omission is not cosmetic, because the six exits do **not** share one remedy:
exits 3–7 (cone, skip-bits, symlink absent, symlink wrong target, multiple feature dirs) are all
fixed by `--repair`; exit 8 (dirty tree) is explicitly declined by `--repair` ("`--repair` does NOT
silently discard a dirty tree: it reports and exits 8 like `--verify`"). A natural, spec-compliant
implementation that prints one generic "run `worktree-state.py --repair`" tail on every failing
check would be **correct for five exits and false for the sixth** — telling an operator to run a
command that will not fix their tree, exactly on the one path where the tree is provably not
self-healing. **Lands on: T-03, D-10.** Ask: add to T-03's message contract that each of the six
messages names its own remedy, and that exit 8's message explicitly states the tree must be
resolved by hand (commit/stash) before retrying — never suggests `--repair`.

`{id: F-02, severity: med}` — Related, narrower: nothing in T-03/SC-15/SC-16 bars past-tense or
action-implying wording ("restored", "reapplied") from leaking into the `--verify` message, and
SC-16 only asserts the **tree state** is byte-for-byte unchanged, not the message **text** — a
`--verify` message that says "cone reapplied" would still pass SC-16 while lying about what
happened. **Lands on: T-03 (message contract), T-04 (test-worktree-state-norepair.py).** Ask: state
the tense constraint in T-03's intent (present/observational only on the `--verify` path) and add
one assertion in T-04's suite that the `--verify` failure message contains no repair-completed
verb.

## 2. `--verify` vs. `--repair` legibility — see F-01/F-02 above; otherwise clean

The mode split itself is legible and well-built: `--verify` is spec'd to report-only (SC-16
enforces byte-identity), `--repair` is spec'd to fix idempotently (SC-17), and the DoD's own framing
("a gate that quietly fixes state hides that something broke it") is honoured by the exit-code
design. The one gap is exactly F-01/F-02: the failing-`--verify` message is never required to *say*
"repair is the remedy" (or, for exit 8, that it is not), so the mode distinction is correct in
mechanism but under-specified in the words an operator actually reads.

## 3. Hook diagnostics (T-12, T-16, D-03) — DEFECTIVE, two sub-findings, (b) is worse

`{id: F-03, severity: med}` — **(a) Silent success.** Nothing in T-03 or T-12 requires `--repair` to
emit a line when it actually changes something on a run fired automatically by `post-checkout`,
`post-merge` or `post-rewrite`. T-03's "prints one line" requirement is scoped to the `--verify`
bullet only; `--repair`'s bullet says nothing about output on success. An agent running bare `git
worktree add` — which the DoD explicitly says must work with the agent "expecting nothing to
happen" — gets a tree that was silently mutated (skip-bits, symlink, cone) with zero record that it
happened. **Lands on: T-03.** Ask: require `--repair` to print one line per check it actually
repaired (silent only when every check already passed, true no-op).

`{id: F-04, severity: high}` — **(b) Failure, and this is the worse of the two.** T-12's "never
non-zero, one diagnostic line" rule is written for exactly one shape: **the delegate file is
missing or not executable.** It says nothing about the shape where the delegate exists and runs but
`worktree-state.py --repair` itself exits non-zero (the exit-8 dirty-tree case is the realistic
instance, since checks 1–4/4b are self-repairing). In that shape, `exec "$delegate" "$@"` means the
hook process's exit code and stdout/stderr *are* `worktree-state.py`'s, verbatim — no
`post-checkout:`/`post-rewrite:`-style prefix, nothing distinguishing it from git's own hook
chatter. T-16 tests only the missing-delegate shape (Part 2 explicitly repoints delegates at a
missing path); no case exercises "delegate present, repair fails." This is the worse failure
because, unlike (a), the tree is **still broken** here — the exact corpus-deletion-adjacent state
this feature exists to prevent — and the operator has no legible, attributable signal that a
harness hook is the source, on paths (bare `git worktree add`, an ordinary merge, a rebase) where
they expect silence. **Lands on: T-12, T-16.** Ask: T-12's intent must require the shim to attribute
a non-zero `worktree-state.py` exit with the same hook-name-prefixed wording style used for the
missing-delegate case (not bare passthrough), and T-16 must add a "delegate present, `--repair`
legitimately fails" case per shim, asserting both the attributed message and that the tree is still
in its broken state afterward.

## 4. The audit's refusal (T-08, D-05, REQ-03) — CLEAN

`{id: F-05, severity: low}` — The design avoids the collision the assignment warns about **by
construction**, not by message wording: inside a linked worktree the expected set is computed as
exactly `{basename(root)}`, so a correctly-materialised sparse worktree always equals its expected
set and never reaches the refusal branch at all — "sparse and expected" and "something is broken"
cannot produce the same message because the first case never emits one. The refusal message itself
("reached N of M expected feature directories" + sorted missing/unexpected names) is concrete and
carries the counts REQ-03 requires. State this plainly: **item 4 is clean**, a real, non-padding
finding. One minor, low-severity gap folds into F-06 below: like T-03, this message never names a
remedy action. **Lands on: T-08.** Ask (low, optional): add a trailing remedy line, e.g. "run
`worktree-state.py --repair`", consistent with F-06.

## 5. Consistency with the shipped diagnostic style — DEFECTIVE, severity MED

`{id: F-06, severity: med}` — Read live: every refusal in `check-domain.sh` and
`bash-write-guard.sh` pairs `"<script>: BLOCKED — <reason>."` with at least one indented remedy
line — `"Fix: chmod +x it"` (check-domain.sh:2620), `"Fix: git config core.hooksPath ..."`
(check-domain.sh:2608), `"Use \`.agents/skills/harness/bin/feature-worktree.py remove\`: it refuses
on a dirty tree..."` (bash-write-guard.sh:585), `"Write it there instead"` (check-domain.sh:948).
`check-state.sh` — the exact file T-08 edits — follows the same pattern at its own existing INV-31
findings (line 2595 `"Fix: make git runnable in this checkout."`, 2608, 2617, 2620). Neither T-03's
new `worktree-state.py` messages nor T-08's new "reached N of M" message is required to carry that
trailing remedy line — a real departure from a convention that is load-bearing and present
elsewhere in the very files being touched. By contrast, T-12's hook shims are **clean** on this
axis: they explicitly reuse `post-merge:29-32`'s existing one-line wording with no remedy tail,
matching that tier's own (simpler) precedent exactly — the Python-gate tier and the shell-shim tier
have different established conventions, and T-12 correctly matches its tier while T-03/T-08 do not
match theirs. **Lands on: T-03, T-08.** Ask: add a trailing remedy line to each new refusal message
in both files, matching the "Fix: ..."/"Use \`...\`" pattern already present in `check-state.sh`
and its siblings — this is the same mechanism that would close F-01's dirty-tree-specific ask.

## Rollup

| id | severity | lands_on |
|---|---|---|
| F-01 | high | T-03, D-10 |
| F-02 | med | T-03, T-04 |
| F-03 | med | T-03 |
| F-04 | high | T-12, T-16 |
| F-05 | low | T-08 |
| F-06 | med | T-03, T-08 |

`severity_max = high` (F-01, F-04) → gates FAIL per the design-check contract. All six findings
are independently actionable at the spec level (message-content requirements + one added T-16 test
case); none requires new mechanism, new task, or a scope change.
