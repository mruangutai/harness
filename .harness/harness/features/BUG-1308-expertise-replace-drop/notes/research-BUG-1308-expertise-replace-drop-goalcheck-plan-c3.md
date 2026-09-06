# Goal-check — BUG-1308 plan, cycle 3 (post panel-fix consistency grade)

**DOES THIS PLAN DELIVER THE OPERATOR'S STATED INTENT?**

**YES — PASS.** The rank 1–7 panel-fix pass left the plan internally consistent: every case id the
verifies grep is defined, every SC still names an observable its declared method can falsify, the
dependency graph is still a topological order, and nothing was waived. Three advisory pointer
imprecisions are named below; none of them makes a criterion unmeetable or a task unexecutable.

## 1. Internal consistency — decisions × task intents × SCs

- T-01 verify greps `u1 u2 u3 u5 u6 u7 u8 u9 u10 u11 u12 u13 u14 u15 u16`; the intent defines
  exactly those (plan.yaml:339-341 vs :450-502). `u4` is explicitly retired, not reassigned
  (:501-502) — consistent with D-02/D-15(2) deleting the cross-section condition.
- T-02 verify greps `case11..case20`; the intent defines exactly those (:525-527 vs :542-681).
  case14's retired sub-case (a) is recorded as DELETED with its exit-12 replacement pointed at
  case20 (:557-561) — matches SC-04's "no third condition" (BRIEF.md:75-81).
- Exit codes carry one meaning each: 7 CONFLICT (add, differing text), 8 CAP EXCEEDED, 9
  destination, 10 MISSING TARGET, 11 AMBIGUOUS TARGET (two conditions only, D-03 + D-12's
  drop+add), 12 MALFORMED OPS (shape, incl. missing/empty `section` and `op: merge`). D-03, D-04,
  D-05, D-10, D-12 and every case agree.
- SC-09's second direction is reachable only via the `--ops` help naming the verbs; T-01 item 3
  (:435-440) mandates exactly that, and case17 (:583-592) consumes it. No orphan.
- Baselines re-derived at working tree: `CAPS` (expertise-merge.py:37), `compute_union` returning
  `(merged, order, conflicts)` and keeping base text on conflict (:113-139, so u10 is true),
  `harness_merge.acquire` (:105) and `locked_update` locking `path + ".lock"` (:121-133, so
  case18's contention idiom is the production path), `LOCK_TIMEOUT_SECONDS = 10.0` (:36, so the
  2.0s hold window claim holds), `## DEC-2NN` heading shape and `**Chose:/Over:/Because:/Tradeoff
  accepted:**` labels (DECISIONS.md:6762+, DEC-215 is last so 216 is free), and the
  `- DEC-NNN … :: <ruling>` index row shape (DECISIONS-INDEX.md:215). Every T-04 verify grep can
  match after the strip.

## 2. Traceability

Every SC is produced by at least one task: SC-01→case11, SC-02→case12, SC-03→case13,
SC-04→u13+case20(a)(b)+case14(b)(c), SC-05→case15, SC-06→case16+suite, SC-07→u10+unit suite,
SC-08→case11/case12, SC-09→case17(+T-03 text), SC-10→T-04, SC-11→case18, SC-12→case19+u11+u12.
Every task traces ≥1 REQ (T-01 REQ-01..07, T-02 REQ-01..09, T-03 REQ-08, T-04 REQ-08); every
REQ-01..09 is claimed by ≥1 task.

## 3. Falsifiability — checked one by one, not sampled

All twelve name an observable and can go red by their declared method. The two that were the
fix pass's subject are now the strongest: SC-07 rests on u10's permanent-red compute_union case,
and SC-09 asserts per-copy WHICH direction fails across three drifted copies, so neither direction
is satisfied by construction. SC-11's three RED shapes and SC-12's reversal-at-the-resolver are
both discharged by a named case.

## 4. Verify blocks

T-01/T-02 are existence-grep + single-suite invocations over files those tasks write (red before
the work: the file does not exist). T-03 and T-04 grep normalised token sets over the exact files
they edit and T-04 runs the one generator test. No verify runs a project-wide suite and no verify
asserts anything a predecessor deletes — case8, the only pre-existing detector, reads the CAPS
mappings (test-expertise-merge.py:266-283), not the SKILL.md region T-03 rewrites.
`check-plan-routes.py` on this plan: 0 violations, exit 0.

## 5. Dependency shape

T-01 [] → T-03 [T-01], T-04 [T-01], T-02 [T-01, T-03]. Acyclic, topologically orderable, and the
single main-session barrier is the one D-13 prices (T-04 correctly does NOT depend on T-03).

## 6. Scope

Task `files:` ⊆ the seven lane rows. `approval.status` is `pending`, `approval.rulings` absent, and
the one open finding (PF-12c69147, low) is recorded open with no acceptance and no waiver.

## Advisory — named, not repaired

- **A1 · plan.yaml:680-681.** The trailing gloss says "u13 and u14 are their unit halves" of case20
  sub-cases (a) and (b). u14 is the unit half of (c) (payload-not-a-list); (a)/(b)'s half is u13
  alone. Prose mis-attribution inside `intent`; the operative case texts are correct.
- **A2 · plan.yaml:580-582.** case17 defines CONTRACT as collected "the way case 8 collects its
  vocabulary", but case8 collects the CAPS mapping (test-expertise-merge.py:266-283) and has no
  vocabulary. The analogy points at nothing; case17's own definition ("op verbs named by the ops
  vocabulary line, read as TEXT") is self-sufficient, so a builder is not blocked.
- **A3 · BRIEF.md:76-81 vs plan.yaml:670-675.** SC-04 requires the exit-12 line to name the
  offending key `section` AND the op's index, at the resolver and through the CLI; case20(a)/(b)
  assert the key token only. The index clause is discharged by u13, and SC-04's evidence is
  `unit, integration`, so the criterion stays falsifiable — the CLI half simply asserts a subset.

## Panel record, this cycle

`panel.readers` now carries three entries — should-not-exist (ran, fable-advisor),
scope (ran, harness-code-reviewer), goalcheck (ran, harness-pm, 0 findings), closing INV-32's
third-reader gap (check-state.sh:533,541-547). The goalcheck reader's cycle-2 evidence is
`notes/research-BUG-1308-expertise-replace-drop-goalcheck-plan-c2.md` (PASS); this note is its
cycle-3 run. `panel.findings` is unchanged: 14 entries, 13 `resolved` + 1 `open`, deep-equal to the
pre-write state including every id, severity, summary and `resolved_by`. `cycle` and `last_run`
untouched.
