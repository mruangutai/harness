# Review — FEAT-40 DESIGN.md (Mode A, pre-build contract) — harness-ui-reviewer

## BLUF

The contract for the five pinned operator-facing string sets (`ship`'s HELD/FAILED lines,
`abandon`'s dry-run/confirm flow, the Bash gate's refusal, `check-state.sh`'s INV-31) is sound and
measures correctly against the cited code. One real defect: **Q1 is tagged `non-blocking` while its
own closing sentence demands operator resolution before signature** — a direct self-contradiction on
the one open question whose substance (a machine reader for `ship`'s terminal-batch failure) closes
the exact silent-failure class this feature exists to fix. `must_fix`.

## Self-scope

IN. Confirmed independently, not on the dispatch's say-so: `gh-sync.py:102-121` (`skip`/`die`/
`refuse`), the collision constraint at `post-merge-sweep.sh:187,192-194`, and every citation in
Contracts 2-5 were re-measured against the tree at `cc84b29` and match. This is the operator-facing
command surface FEAT-19 established as a designed artifact for this repo.

## Verified measurements (independent re-check of DESIGN.md's own citations)

- `gh-sync.py:102-121` — `skip()`/`die()`/`refuse()` print exactly the three prefix/exit shapes
  Contract 1's table claims.
- `gh-sync.py:986-990` (DESIGN.md cites `986-991`) and `:1000-1009` (cites `1000-1008`) — `abandon`'s
  current close-as-`not_planned` + `abandoned` label, and the `parent_origin`-gated parent close.
  Accurate.
- Grepped every non-test `.py` under `.claude/skills/harness/bin/` for `input(` — zero hits. Contract
  3's "confirmation is not a prompt" premise holds.
- `post-merge-sweep.sh:187,192-194` — `combined = stdout+stderr`; `if "gh-sync: SKIP" in combined:`
  declines removal. Exact match to Contract 2's hard constraint.
- `check-state.sh:1084, :1191, :1346` — the three `CANNOT RUN` precedents Contract 5 cites. Exact
  match.
- Swept every literal Contract 2/3/4/5 pins against the substring `gh-sync: SKIP` — none contains it.
  No collision found.

## must_fix

**Q1's blocking tag contradicts its own text.** `DESIGN.md:216` — `Q1 (non-blocking, recommended)`.
`DESIGN.md:224-225` — "The operator should decide **before signature**." Under this repo's own
`open_questions` vocabulary (`blocking: true|false`), "must be resolved before signature" *is* the
definition of blocking; a signer filtering on blocking-only items will pass over it.

This is substantive, not cosmetic. Q1 asks whether `ship`'s new terminal-batch-failure summary line
gets a **machine reader** — whether `post-merge-sweep.sh` (or an equivalent) declines worktree removal
when a card silently misses `Done`. Contract 2 deliberately keeps `FAILED`/`HELD` distinct from
`SKIP`, so `post-merge-sweep.sh` as written today does not trip on either new literal. `plan.yaml` has
no task touching `post-merge-sweep.sh` (checked: the only hit is a reference inside T-02's probe
intent, never a file-to-change). So DESIGN.md as drafted, if signed with Q1 left open, permits shipping
the terminal write with **no downstream gate on a partial failure** — the precise defect class (a card
silently misses its terminal state, nothing downstream reports it) this feature exists to end,
reintroduced at the one place it is newly written.

**Recommendation:** reclassify Q1 to `blocking: true`, or resolve it inside Contract 2 (commit either
to Q1's own suggested fix — emit a `gh-sync: SKIP` line, reusing the existing token, when the batch is
incomplete — or to wiring `post-merge-sweep.sh`'s grep to a new literal) before signature.

## Advisory (not blocking)

- **Batch summary stream unpinned.** Contract 2 states the per-card HELD line is "printed on stdout"
  but never states which stream the two-line batch summary (`HELD n of m` / `FAILED n of m`) uses.
  Inferable from the codebase's convention (bare/SKIP/ERROR-em-dash/REFUSED all use plain `print()`;
  only per-card `ERROR -` writes are explicit `file=sys.stderr`) — an implementer will likely default
  to stdout correctly — but Contract 1 pins stream for every existing shape, so leaving the two new
  lines unpinned is an inconsistency in the contract's own stated discipline.
- **`FAILED` names which card, not why**, by deliberate design (Contract 2's own table: "the why is
  above it," on a separate stderr `ERROR -` line). Reasoned, not an oversight — but worth the
  operator's eyes: a consumer reading only the summary line (without full scrollback) gets *which*,
  never *why*.
- **Theme/colour-contrast is explicitly not applicable.** This is a batch CLI surface with no
  colour-only state encoding — stated here rather than left as a silent omission.

## Dimensions judged sound

- **Prototype gate (`needs_prototype: false`).** Sound, independently reasoned (not a restatement of
  FEAT-19's rationale): `abandon`'s two-step flow is argv-driven and non-interactive with no state held
  between invocations, and the stated hinge — flips to `true` only if `abandon` ever reads stdin — is
  the correct one, because only a live prompt introduces isatty/pipe/captured-output behavior a
  prototype could test that the pinned text cannot.
- **Refusal's three clauses (Contract 4).** Correct call. SC-07 only requires the substring
  `gh-sync.py abandon`; a bare name alone would route a finished ticket toward the destructive path
  (`gh-sync.py:986-990`, verified). The untracked clause states a recovery ("close it in the GitHub web
  UI"), addressing the brief's concern about a legitimate close with no stated path. Clause ordering
  (finished-first, "do nothing") matches the likeliest real operator intent.
- **Collision risk.** No pinned literal contains `gh-sync: SKIP`; `FAILED` is deliberately kept
  distinct from the existing per-card `ERROR -` token, correctly reasoned in Contract 2.

## Verdict

FAIL — one `must_fix` (Q1's blocking-tag contradiction), `severity_max: high` because its unresolved
substance permits reintroducing the feature's own target defect at the terminal write.
