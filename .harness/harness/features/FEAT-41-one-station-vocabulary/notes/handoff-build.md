## Next

Cycle 3's three highs are closed (`5ae94e5`). TWO ITEMS ARE THE OPERATOR'S, NOT A BUILD PASS:

- **SC-01 is literally false** and the panel refused to narrow it: `_STATION_KEYS` has 54 tracked
  hits, ALL narrative prose in `notes/` and `observations/`, ZERO in any `.py`/`.sh`/`.json`. Read
  as "no source declares a second vocabulary" it is true and verified.
- **MF-4 (med)**: `cmd_apply` creates a plan with no station validation, and a directory with no
  `BRIEF.md` is never approval-checked. The gating half PREDATES `7c4f0bd`; what this feature adds
  is that such a directory can now satisfy INV-34.

AND ONE DESIGN QUESTION ABOVE THE PANEL: `plan-sign-gate.py` is a DENYLIST of evasion forms. Three
cycles, three members of one class (`--`, continuation, `${IFS}`, now `$(...)`). The structural
answer is an identity check inside `cmd_sign_approval`, and it CANNOT be written today - no runtime
identity signal reaches a subprocess (`HARNESS_AGENT_ID` is a marker inside agent definition files,
not an env var). Verified, not assumed.

WHAT TO CHECK HARDEST NEXT: the `station_only: true` marker. MF-3 replaced an
absence-as-credential with a positive declaration, so anything that can FORGE the marker restores
the hole; and INV-34's remediation text now instructs operators to write it.

Cycle 0/1/2 verdict items stay closed: T-15 ratified in D-15, T-10 recorded not rewritten, T-18
STRUCK in D-16, C2-01 answered by the operator in D-17.

## Trust

- unit exit 0, 505 PASS; integration exit 0, 819 PASS; check-state.sh exit 0, ZERO violations, zero tracebacks — verified-at 5ae94e5
- MF-2's NUL crash is PRE-EXISTING in `harness_boundary.real`, not introduced by C2-02: identical fixture on origin/main crashes the same way. My first probe was INVALID (no team-config.yaml, so the boundary never reached classify) — verified-at 5ae94e5
- realpath does NOT raise on a symlink loop; it is non-strict and resolves as far as it can. My own docstring claimed otherwise and that claim justified a dead branch — verified-at 5ae94e5
- (inv34.e) is NOT vacuous, mutated on BOTH layers: keying reverted -> ok, loader reverted -> ok, BOTH reverted -> FAIL. Two independent layers — verified-at 5ae94e5
- MF-1's fix SCANS for balanced parens rather than regexing; `\$\([^)]*\)` stops at the first `)` and a nested substitution would have leaked through a fix that looked correct — verified-at 5ae94e5
- SC-08 measured VERBATIM against its own text: 0 feature.json carry `status`; schema 10 properties / 7 required / additionalProperties false — verified-at 80a919e
- Cycle 2's own findings and T-19's two proven walls are closed and re-verified by cycle 3's panel; detail is in `42bc5fe..80a919e` — verified-at 5ae94e5
- The station-only exemption is SCOPING: the only way to pass the approval check otherwise was to fabricate twelve signatures; control (inv34.d) was green before the exemption — verified-at 80a919e
- BUG-1030's audit: 45 statuses stripped, 44 terminal and correct, 1 non-terminal — measured against origin/main, not inferred — verified-at e071509
- Gated HIGH code-grade records: 0, measured with the NEW code_grade.py (it moved upstream) against merge-base 7c4f0bd — verified-at 542e888
- Cycles 0 and 1 are fully closed and each finding was re-verified at source by a later independent panel; detail is in `787c7fa..c4da870` — verified-at e071509
- T-14's invariant is INV-33 now, not 32: FEAT-45 shipped its own INV-32 first, so it owns the number; both suites' cases pass side by side — verified-at 8fa2d04
- F-04's realpath half does NOT reproduce as a PATH SHAPE: `./`, `..`, doubled slash and absolute are denied; the SYMLINKED-FILE case was the real hole and is H-01 — verified-at 42bc5fe

## Dead Ends

- Do NOT resolve paths on ONE side only in check-domain.sh. Shape-matching the as-typed path stays (it is stronger for `./`, `..`, doubled slashes and absolute paths, all denied), but resolution must realpath the path AND the root or it lands in a different spelling namespace and silently matches nothing. This entry twice recorded a conclusion that was too narrow: first "do not re-fix F-04's realpath half" (which talked past the symlinked-FILE hole, H-01), then "do not rewrite the readlink walk as realpath" (which forbade the actual fix, C2-02). Resolution answers what a path BECOMES; inode identity answers whether two names are the SAME FILE; a hardlink needs the second
- Do NOT close SC-08 by editing SC-08, and do NOT delete BUG-1071's `feature.json.status` — it has no plan.yaml, so that key is the only record it is in review. Issue #1079
- Do NOT reconcile `_record_station` and `_commit_terminal_station` to use the same words: written-nowhere and written-but-uncommitted have OPPOSITE correct answers, both asserted
- Do NOT exempt `--date` from sign-approval's escaping; a type-aware exemption is a hole in the check that closes F-02
- Do NOT add a `required` column to plan-merge.py's VERBS table; if a verb needs an optional argument it gets its own registration
- Do NOT re-run the one-time board pass; it is idempotent but it WRITES, and a run against a moved plan would move cards the panel has not seen
- Do NOT touch `review_sha` in any other feature.json — T-14's intent forbids it, and 19 directories carry honestly-stale-looking pins from layout history
- Do NOT edit `plan.yaml` with Write or Edit; T-09 closed that route for every author including the main session — use `plan-merge.py` verbs
- Do NOT treat `--kind unit` as the suite: it covers 29 of 56 scripts and that gap hid T-01's breakage for four tasks
- Do NOT quote a retired station spelling in a comment — SC-02 greps for it, and this feature tripped that four times

## Working Set

- .harness/harness/features/FEAT-41-one-station-vocabulary/plan.yaml
- .harness/harness/features/FEAT-41-one-station-vocabulary/BRIEF.md
- .harness/logs/2026-08-31.md
- .claude/skills/harness/bin/check-domain.sh
- .claude/skills/harness/bin/check-state.sh
