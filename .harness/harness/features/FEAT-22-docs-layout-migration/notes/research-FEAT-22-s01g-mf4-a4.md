# FEAT-22 · S-01g revision pass — MF-4 closed, A4 folded (plan r6 → r7)

**BLUF.** MF-4 is closed: `test-check-domain.py:924` is now enumerated in T-05's intent with its
subject PINNED to `.harness/harness/docs/SPEC.md`, and T-05's verify gained one runnable clause that
fires on the migrated call text and cannot be satisfied by the repointed `:789` site. A4 is folded
into T-09's allow-list. Three hunks, nothing else. Approval stays `pending`; neither approval block
was touched. Pin `0f12f14` re-confirmed (`git rev-parse HEAD` = `0f12f14c166d…`), legacy line count
in `test-check-domain.py` re-measured at **19**.

## 1. Is `:924` enumerated with the pinned subject?

**Yes.** New entry at `plan.yaml:688-705`, in numeric order after the `:801-826` entry and before
`test-bash-write-guard.py`. It carries: the pinned subject `.harness/harness/docs/SPEC.md`, the
unchanged exit-0 expectation, the causal chain (target-side filter in `harness_boundary.classify`
discards the `docs/**` match once the legacy path stops being a control-plane target, hook exits 2),
the reason the subject is pinned rather than free (any other in-domain path greens the case and the
count while silently dropping **hook-path** coverage of the docs surface), and the pair distinction —
`:924` is the hook half, `:789` is the `--resolve` half, both naming the same path after the move.

One wording guard added deliberately: the entry states `:924` does **not** become a
refused-direction case. It keeps asserting exit 0 on the granted new path; the file's single
refused-direction survivor stays `guide.md`. That is what protects the exactly-one-legacy-line count.

## 2. Are both of T-05's failure modes closed?

- **(a) `n=1` exactly-one-legacy-line count (now `plan.yaml:596-598`)** — closed. `:924` was one of
  the 19 legacy lines and is now enumerated for repointing, so following T-05's intent literally
  leaves exactly one (`docs/harness/guide.md`, the refused-direction survivor). Before this pass it
  left two.
- **(b) `PASS test-check-domain.py` (now `:588-590`) via case (h)** — closed. Repointing `:924` to
  the migrated path restores exit 0 for case (h) against the post-T-03 classifier, so the script can
  pass and the integration suite's expected-FAIL set stays at the one stale-index script.

`T-10`'s `19 → 1` arithmetic **stays true** with the entry present — it already assumed this fix.
Not restated anywhere.

## 3. The clause added, and the sanity run

Shipped verbatim at `plan.yaml:605-606`:

    grep -qF 'hook(".harness/harness/docs/SPEC.md", "harness-documentor")' $B/test-check-domain.py \
      || { echo "case (h) at :924: the hook subject is not pinned to the migrated docs path"; exit 1; }

`-F` was used because the call text carries parentheses and dots; an `-E` pattern would silently
never match and would redden a correct execution mid-cluster.

The pattern was **extracted back out of the shipped plan line** (`sed -n 605p`), not retyped, and
fired four ways against the real file at the pin:

| # | Input | Expect | Got |
|---|---|---|---|
| A | `test-check-domain.py` as it stands at `0f12f14` (legacy) | no match | `exit=1` |
| B | same file, `sed 's#"docs/harness/SPEC.md"#".harness/harness/docs/SPEC.md"#g'` (migrated sim) | match, once | `924:    r = hook(".harness/harness/docs/SPEC.md", "harness-documentor")`, `exit=0` |
| C | migrated sim with case (h) repointed to `.harness/harness/docs/BUILD.md` | no match | `exit=1` |
| D | migrated `:789` line alone (`subprocess.run([HOOK, "--resolve", ".harness/harness/docs/SPEC.md"]`) | no match | `exit=1` |

C proves the clause fails on any other in-domain subject. D proves the repointed `:789` site, which
carries the identical path string after the move, cannot satisfy it — the anchor is the `hook(` call
shape, not the path.

## 4. Diff hunk line ranges in `plan.yaml`

`plan.yaml` is **untracked** at this pin (`git status` shows `??`), so `git diff -U0` produces
nothing; ranges below are git-style, computed against the r6 text (1196 → 1217 lines, +21):

    @@ -604,0 +605,2 @@     T-05 verify — the case (h) clause
    @@ -685,0 +688,18 @@    T-05 intent — the :924 enumeration entry
    @@ -969,0 +990,1 @@     T-09 verify — the A4 allow-list arm

Three hunks, all pure insertions. No existing line was modified or reflowed. `verify:` stayed a
literal `|` block in both tasks.

## 5. A4 resolution

Resolved as the self-consistent pair the dispatch sanctioned, which is A4's own remedy shape and
therefore in scope, not gratuitous:

- **Added** one arm to T-09's commit-audit allow-list, now `plan.yaml:990`: `docs/harness/*) ;;`
- **Kept** `grep -v '^docs/harness/'`, now `plan.yaml:994` (was `:973`) — **unmodified**.

Why the pair rather than either alone: under `diff.renames=false` the five moves appear as five
deletes plus five adds, so `--name-only` emits source-side `docs/harness/*` paths. Without the arm
the loop fatals on a correct commit; without the `grep -v` those source-side paths would count
toward the 28-file destination-side floor. With both, the loop accepts them and `k` stays a
destination-side count. Under `diff.renames` unset at git 2.50.1 (dev-ops' measurement) neither is
reached — the destination-only output is unchanged by this edit.

## 6. Consistency and line-shift checks

- **T-05 SHAPE PIN** — the block inside T-05's SURVIVING LEGACY LITERALS section, content-anchored
  on "SHAPE PIN, because the count is exact" (re-measured after the edits at `plan.yaml:723-726`),
  unchanged: "Every other site listed above is repointed" **remains true** with `:924` present,
  because `:924` is listed and is repointed. Read it with the new entry in place; it needed no word,
  so none was added.
- **Line-shift check — closed, independently.** `grep -n 'plan\.yaml:[0-9]'` over the plan returns
  exactly one hit — re-measured after the edits it prints `845:` (it was `825:` before the pass,
  shifted by the +20 lines both T-05 insertions add above it) — and it is
  `.claude/skills/harness/templates/plan.yaml:44` —
  a template file path in T-06's intent prose, not a pin into this plan. No task's `verify:` pins a
  `plan.yaml` line range, so no pin shifted and nothing needed fixing.
- `yaml.safe_load` reloads the file cleanly: 11 tasks, 7 decisions, `approval.status: pending`.
- `check-plan-routes.py` exits **0**, `0 violation(s)` (routing untouched; the DEVIATION lines are
  the pre-existing carve-out declarations, all accepted).

## Not re-opened

Withdrawn S-02b MF-1 remedy; closed Q1 suite measurement; Q4's accepted residual at `:789`; T-10's
`19 → 1`; the 28-file floor; the expected-FAIL pin. None was read for re-litigation and none was
edited.

## Open questions

None.
