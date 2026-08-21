# STATE — FEAT-32-concurrent-write-merge

## Current

Phase: **plan**, at its terminus. Round 4 (the Q1 amend) is committed. `approval.status` is `pending`
in `plan.yaml` and `## Approval` is `pending` in `BRIEF.md` — both verified **byte-identical to the
previous commit by `diff` against `git show HEAD:`**, not asserted. Nothing here signs. Run 4 returned
**PASS**, one pm, **zero send-backs**.

**Q1 IS ANSWERED, AND THE RULING'S OWN RULE WAS WRONG.** The ruling handed down one rule: deny an Edit
whose payload holds a `status:` key at exactly two spaces. It denies the TARGETED edit and **allows the
`replace_all` sweep** — the worse of the two attacks it was written to close. The discriminator is a
fact about the FILE; the rule inspects a PAYLOAD, which the writer authors rather than reads from the
file, so `old_string: "status: pending"` with `replace_all: true` contains no two-space line start at
all and flips 18 lines. The measurement was true and constrained nothing.

**pm's replacement (`plan.yaml:1739-1753`).** **Limb A** — deny when `old_string` occurs as a substring
of the approval block's on-disk byte range: exact, no reconstruction, no `replace_all` semantics,
indentation-INDEPENDENT. **Limb B** — the `new_string` limb for payloads that INTRODUCE a signature, at
*the indent the fragment uses ON DISK*, with `:1751` explicitly refusing to hardcode two spaces. All
three attack shapes denied; a task's four-space `status:` still allowed. The trade is a conservative
false positive: an `old_string` of `date:` alone is denied. That is the price of closing `replace_all`.

**LAYER 1 MUST BE PRE, STRUCTURALLY — not by the refusability argument I sent down.**
`old_string`/`new_string` appear NOWHERE in `check-domain.sh` except the comment at `:1039` saying they
are deliberately unused, so the PRE path has never inspected an Edit payload. DEC-180 (`@5105`) fixes
the SHAPE gate as post-hoc-capable from DISK while the DOMAIN phase is `_governed and not _post`, so a
domain-aware post-hoc backstop cannot exist. There is no fallback detection of a flipped signature.

**THE CONVENTION CAVEAT WAS NARROWED, CORRECTLY.** Limb A reads no indentation, so the comment I
mandated would have asserted a failure mode the rule no longer has — a false comment in shipped code.
`:1794-1796` scopes it: limb B dies to a reformatting, limb A survives. `check-domain.sh` must still
carry the literal `CONVENTION, NOT A YAML GUARANTEE` and T-14's verify greps for it (`:1672`).

**Layer 2 landed in T-03 as step 7b, additive to step 7.** Step 7 makes the tool INCAPABLE of writing a
signature (its output); 7b makes it NOTICE a caller that tried (its input), refusing exit 8 on a
parsed-value difference. D-10 `:306-312` keeps the enforcement/backstop distinction explicit and records
that layer 2 is reachable only when the writer CHOOSES to invoke the tool.

**BRIEF.md gained SC-21** (+18 lines, above `## Approval`, which stayed byte-identical): binds both
layers, asserts each payload shape INDIVIDUALLY rather than by a count, and goes red two independent
ways — `check-domain.sh`'s guard literal and `plan-merge.py`'s `APPROVAL_REFUSAL` each mutated to
`False`, the latter asserted as byte-identity AND the proposal's task being ABSENT, because layer 2's
carry-forward would otherwise let a result-only assertion pass with the refusal off.

**Verified independently at `6bb7d82`.** `safe_load` clean; **17 tasks**, **10 decisions**;
`check-plan-routes.py` exits **0**, **0 VIOLATION / 6 DEVIATION** — unchanged from round 3, so no route
drift. Unit exit 0 (981 lines, 767 `ok`, **179** `^PASS`, 0 `^FAIL`); integration exit 0 (1035 lines,
742 `ok`, **218** `^PASS`, 0 `^FAIL`, **3 containing `ERROR`**). Baselines now IN the plan with their
sha: `test-check-domain.py` **167** `ok`, enforced by `[ "$n" -ge 167 ]` in T-14's verify;
`test-dispatch-guard.py` exit **2** recorded as Python's no-such-file, T-07 creates it.
`validate-feature-json.py` exits 0; `check-state.sh` exits 1 with FEAT-32's sole VIOLATION being
"BRIEF.md is NOT approved" — the terminus.

**Q5 CLOSED at a SECOND sha.** Integration re-run at `6bb7d82` (zero `.claude/` changes since
`62f861c`, per `git diff --name-only`): exactly 3 lines contain `ERROR`, all three `ok` lines whose test
NAME carries the word — `:92`, `:115`, and `:176`'s gh-sync loud-pair case. Confirmed, not relayed;
recorded at `:1439` with the sha. They must not gate.

**ONE DEFECT SURVIVES THE AMEND**, from a measurement taken after the dispatch left. The entry parser
still splits on the **LAST** space (`:1716`, `rsplit(" ", 1)` at `:1974`). Executed against the real
`main_session.writes`: `.harness/*/features/*/BRIEF.md ## Approval` yields tail `Approval`, matching
neither fragment test, so the entry becomes fragment-less and — by the spec's own third kind —
CONTRIBUTES NO DENIAL. Both `## Approval` entries silently disarm; only the plan.yaml mapping survives,
which is the very special case Q3 refused to hardcode. FIRST-space splitting parses all four correctly.

**THE INDENT CONVENTION IS ALREADY INVERTED BETWEEN TWO OF THE THREE FILES, AT HEAD** — which is why
limb B's refusal to hardcode is load-bearing, and the plan carries no counter-example proving it.
Measured at `6bb7d82`: `plan.yaml` — 23 files, 23 signatures at TWO spaces (one each), 176 task lines at
four. `BRIEF.md` — 31 files, 32 signatures at ZERO indent, no indented `status:` anywhere. `PLAN.md` — 9
files, 10 signatures at ZERO indent and **27 TASK lines at TWO spaces**, the exact inverse. A hardcoded
two-space rule on `PLAN.md` denies 27 legitimate lines and misses every signature.

**NO #551 OCCURRENCE THIS ROUND, and I nearly recorded one.** At 13:22 I read
`runs/2026-08-21-01-product/digest.md` and it opened "**the amend is NOT done** … re-dispatch is a full
re-spend", written 13:19 as the lead's defensive draft against a forced close. The lead then completed
normally and REWROTE the same file at 13:36 with `VERDICT: PASS`. A digest is written and rewritten
DURING a run, so reading one mid-flight and treating it as final is a trap — mtime against the return is
the discriminator. I had this in draft as occurrence 9 before re-reading. Occurrences stand at 8.

**A run-id defect, third shape in three rounds.** The lead minted `runs/2026-08-21-01-product` —
zero-padded, so it sorts BEFORE `2026-08-21-1-product` and round 4 reads as round 1. Round 3's digest
still sits in round 2's dir, which is why `check-state.sh` notes run `2026-08-21-3-product` referenced
with its dir absent. `runs/**` is gitignored (`.gitignore:7`), so this file and `feature.json` are the
durable record. Left uncorrected: renaming now would erase evidence of a live defect.

`cycles_used` **0** of 10 (lead reported zero send-backs). Runs **4** of 20.

**My own errors, because rule 15 applies to me.** "Dispatch pm early, spend the wait measuring" and
"verify the premise before planning on it" pull against each other and I resolved it wrongly: I
dispatched the ruling's rule as sound, then measured against it. A dispatch is unrecallable here, and
only pm's independence stopped the hole shipping. A premise check is not parallelisable with the work
depending on it; my P-06 says this for review findings and I did not apply it to my own dispatch. I also
wrote here that BRIEF.md was unchanged before running `git diff --stat`; it had gained SC-21.

## Open Questions

- Q1 **BLOCKING — the entry parser disarms two of the three files it covers.** `:1716` specifies "split
  on the LAST space"; `:1974` asserts with `rsplit(" ", 1)`. Executed against the real
  `main_session.writes` at `6bb7d82`, both `## Approval` entries contribute NO denial, collapsing the
  three-file mechanism to a plan.yaml special case. FIRST-space splitting parses all four. T-14's cases
  12 and 13 would catch it at build, so the cost is one build cycle rather than a shipped fail-open —
  but it should not be signed. **pm's to fix; one short amend.**
- Q2 **BLOCKING — the same amend should carry the inversion evidence.** Limb B rightly refuses to
  hardcode two spaces (`:1751`) but the plan records no counter-example. `PLAN.md`'s 27 two-space TASK
  lines against its zero-indent signatures is that proof. Numbers and shas in `## Current`.
- Q3 **BLOCKING.** Sign or amend both artifacts. `BRIEF.md` gained SC-21 this round, on top of REQ-11's
  widening and SC-20 last round, REQ-12/SC-17/SC-18/SC-19 before that, SC-16 withdrawn.
- Q4 **NOT blocking — limb A's false positive is a real trade you may want to reverse.** An `old_string`
  of `date:` alone is denied. Closing `replace_all` costs that; the literal indent rule avoids it and
  ships the hole.
- Q5 **NOT blocking — SC-14's shrink detector is not reproducible as recorded.** Unit `^PASS` is 179 at
  `6bb7d82`, matching the 179 recorded at `62f861c`, pinning the definition as `^PASS`. Integration is
  **218** against the **221** recorded at `62f861c`, with **zero** `.claude/` changes between the shas.
  Settling it needs a run at `62f861c`, a checkout I may not perform. The count is polluted anyway: two
  scripts print their own `PASS <name>` line on top of the runner's, so 16 lines cover 14 scripts.
- Q6 **NOT blocking, main session's act.** #551 needs occurrences 7 and 8 (not 9 — see above), and a
  backlog row against run-dir minting. An agent composing a GitHub post is forbidden (DEC-138 am.6) and
  `gh-sync.py` has no subcommand for it.
