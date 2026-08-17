# Review — harness-ui-reviewer — FEAT-22-docs-layout-migration (Mode A, unit 4, cycle 2 recheck)

BLUF: **FAIL.** Cycle-1 Finding 1 is **CLOSED** — all five assertions r5 added to T-03's verify
(`plan.yaml:363–384`) were measured at the pin against the exact standard the finding set: each
fails a token-swap-only build. This cycle's FAIL is a **NEW** must_fix, unrelated to Finding 1,
surfaced by adjudicating pm's own open question at `test-check-domain.py:785–788` (JOB 2). Not the
same reason twice — do not escalate on that basis.

## Scope check

Base confirmed: `git rev-parse HEAD` = `0f12f14c166d231ddf648cc00ff4d12029ce0122`, matching the
dispatch's pin, before reading anything else. Working tree carries unrelated untracked artifacts
from other in-flight features; none touch this feature's files. Per LEAVE DISCIPLINE, this recheck
covers only JOB 1 (the five new T-03 assertions) and JOB 2 (the one named open question). Cycle-1's
"checked clean" list, the DESIGN.md/prototype question, and a fresh `grant(ed)` sweep are explicitly
out of scope and were not re-run.

## JOB 1 — Finding 1 recheck: CLOSED

All four sites, all measured directly against `harness_boundary.py` at 0f12f14 (`git show
0f12f14:.claude/skills/harness/bin/harness_boundary.py`), not against pm's account:

- **`:84`** (`plan.yaml:367–368`, `grep -B20 'HARNESS_CONTROL_PLANE = \[' | grep -qi redundant`).
  Confirmed at the pin: the 20-line window above `HARNESS_CONTROL_PLANE = [` contains no instance
  of "redundant" in any case. A token-swap-only build (respell the glob, leave the comment's
  reasoning untouched) fails this assertion. Closes the gap.
- **`:221`** (`plan.yaml:369–372`, negative grep for `holds no.*entry anywhere`). Confirmed at the
  pin: the docstring reads "team-config.yaml grants `docs/**` and holds no `docs/harness/**` entry
  anywhere" (line 220–222) — exactly the pattern. A token-swap-only build (respell the glob token,
  leave the sentence otherwise intact) trips this grep and fails. **Ruling on the negative-only
  ceiling: acceptable, not a residual gap on Finding 1.** The verify enforces exactly what the
  intent mandates — the false claim must not survive (`plan.yaml:426–427`, "MUST NOT SURVIVE IN ANY
  SPELLING") — and the plan's own intent explicitly delegates replacement-correctness to a human
  reader rather than claiming to check it: "the verify can force the false claim out but cannot
  prove the replacement is right; the replacement sentence is yours to get right, and a reviewer
  reads it" (`plan.yaml:430–431`). pm's vacuity argument for skipping a positive check holds: the
  candidate positive handle, "Target-keyed, not glob-keyed" (`:220`), is unchanged pre- and
  post-fix, so a positive grep on it would pass a build that changed nothing. A declared ceiling
  with a named human receiver is a checkable contract about its own limits, which is what Mode A
  asks for. Advisory-only residual: a determined edit could still delete the forbidden phrase and
  leave a grammatically incomplete or differently-false sentence undetected — inherent to grepping
  freeform prose, not a gap specific to this site, and not worth another cycle.
- **`:315–316`** (`plan.yaml:379–383`, awk window keyed on `guide.md` as unique anchor).
  Confirmed at the pin: `guide.md` appears exactly once in the file (line 315), so the uniqueness
  precondition holds today. **Ruling on soundness: sound, not brittle.** The window is
  anchor-relative (`g-8` to `g+3`), so it survives line drift elsewhere in the file, matches the
  intent's own "within eight lines above and three below" instruction (`plan.yaml:467–468`)
  exactly, and fails CLOSED on both zero anchors and multiple anchors (`c!=1`) rather than passing
  silently. A token-swap-only build — respell the destination path in the `guide.md` comment,
  leave "what makes `docs/**` grant" unchanged — does not introduce the literal
  `.harness/*/docs/**` anywhere in the 12-line window (the actual occurrence of that string, in
  the control-plane list, sits at line 90, well outside any window centered near 315), so the
  assertion correctly fails it.
- **`:111–112`** (`plan.yaml:373–378`, require `-> ../../../.claude`, forbid `-> ../../.claude`).
  Empirically checked the substring risk this shape can carry (P-15): confirmed via `grep -F` and
  Python that `-> ../../.claude` is **not** a substring of `-> ../../../.claude` — the `-> ` anchor
  prefix on both patterns prevents the periodic `../` unit from producing a false match. Confirmed
  at the pin that the current text is exactly `docs/harness/<link>/agents/x.md` with `<link> ->
  ../../.claude` (line 111), so a minimal re-anchor-only fix (new base, same two-climb target)
  trips the forbidden-string check and fails, while the required three-climb literal is absent and
  also fails — both directions of the token-swap trap are covered.

**Correction carried forward, as directed.** Cycle-1's Finding 1 said `:111–112` "carries no legacy
substring at all to force a change." That was wrong for `:111`: `docs/harness/<link>/agents/x.md`
literally contains `docs/harness` and was already forced to change by T-03's pre-existing whole-file
negative grep. The real gap the cycle-1 finding should have named was that the whole-file check
cannot discriminate a *correct* three-climb rewrite from an *incorrect* minimal two-climb rewrite —
both clear the legacy-substring check identically. r5's two new assertions target exactly that real
gap (require three climbs, forbid two), not the invisibility claim my prose made. Recorded here per
rule 15 rather than silently superseded.

**Residual not gating:** `:112`'s trailing clause ("stayed inside `docs/` for every comparison") has
no assertion of its own. The intent only asks it be kept "consistent with the new base" without a
literal, and the clause's claim (naive comparison stays nominally inside a `docs/`-prefixed path)
remains true regardless of exact segment count, so it is not a second instance of the climb-count
defect. Advisory only.

**Verdict on Finding 1: `must_fix: []`.** All four sites now carry an assertion a command can run
that fails against the exact token-swap-only build the original finding described.

## JOB 2 — `test-check-domain.py:785–788`: ruled `must_fix`, severity `med`

Verified independently at the pin, not from pm's report:

- `git show 0f12f14:.claude/skills/harness/bin/test-check-domain.py` lines 784–788 read: "no
  `docs/harness/**` entry exists anywhere in team-config.yaml, so a glob-keyed classifier would have
  nothing to match it against" — the same falsified-claim shape as `harness_boundary.py:221`
  pre-fix. `.harness/team-config.yaml` at the pin (line 117) confirms only `docs/**` is granted
  today; T-02 (`plan.yaml:310`) adds `.harness/*/docs/**` alongside it — the entry this comment
  claims does not exist.
- T-05's intent mandates the rewrite explicitly and in caps: "ITS COMMENT AT :785-788 MUST BE
  REWRITTEN, NOT CARRIED... Say what the case still proves... and drop the glob-keyed claim rather
  than leaving a stale reason standing" (`plan.yaml:648–656`).
- T-05's verify (`plan.yaml:581–606`) has exactly one assertion that touches this region: an
  exact-count check, `n=$(grep -cE "$P" test-check-domain.py); test "$n" = 1`, where `P =
  'docs/harness|"docs", ?"harness"'`, and the single permitted occurrence is pinned to the
  refused-direction case's path argument elsewhere in the file (`plan.yaml:685–692`). **This does
  not close the gap.** A token-swap-only edit — respell `docs/harness/**` to `.harness/*/docs/**`
  inside the :788 comment, leave "no ... entry exists anywhere ... nothing to match" standing —
  removes the only literal the count check greps for (`docs/harness`), so `n` stays at 1 and the
  assertion passes, while the comment now asserts something T-02 just made false. No other T-05
  assertion, and no T-09/T-10 backstop (checked: T-09's verify is gate-green plus commit-hygiene
  only, no prose-content check on this file), covers it.
- **Ruling: `must_fix`, not advisory.** The discriminator is the same one Finding 1 used throughout
  JOB 1: a mandated semantic change needs an assertion that fails a token-swap-only build. This site
  fails that test. The contrast with `:221` sharpens the ruling rather than undermining it: at
  `:221` the plan **declares** its ceiling and assigns the residual to a named human reader
  (`plan.yaml:430–431`); here T-05 mandates the rewrite in the same register and assigns enforcement
  to nobody.
- **Severity `med`, not `high`.** Cycle-1's "why this gates" for `harness_boundary.py` rested on two
  components: (a) DEC-174 carve-out blast radius — the file decides live write-guard verdicts — and
  (b) the file-agnostic Mode A criterion, permanent falsehood with zero detection for a mandated
  content change. Component (a) set severity to high; component (b) is what makes something a
  finding at all, and it transfers here unchanged. Component (a) does not: a stale comment in a test
  file's rationale does not itself decide a live access-control verdict — the underlying test
  assertion (resolves to `harness-documentor`) still passes correctly regardless of the comment's
  truthfulness, so the blast radius is a future-engineer-misreads-the-rationale risk, not a
  live-system correctness risk. `must_fix` non-empty gates `FAIL` on its own; `med` accurately
  encodes "gates, but not for blast-radius reasons."
- **Remedy, shape only** (pm's to write, matching the plan's own idiom at `harness_boundary.py:221`):
  one negative grep in T-05's verify against the rewritten comment's window, forbidding the
  false-claim shape ("no ... entry exists anywhere ... nothing to match") from surviving, the same
  way `plan.yaml:369–372` does for `:221`.

## Accessibility and theme parity

Not applicable, unchanged from cycle 1: every surface in this recheck's scope is shell/Python source
and test-file comments — no rendered output, no colour, no interactive state.

## Mode A checklist (recheck scope only)

- Checkable: Finding 1's four sites — yes, closed. The Q2 site — no, and now flagged.
- Internally consistent: yes. The plan's own T-03 idiom (declared ceiling with human receiver vs.
  mandated rewrite with enforcement) is the standard this recheck applied to both sites; it produced
  different rulings for a reason, not by inconsistency.
