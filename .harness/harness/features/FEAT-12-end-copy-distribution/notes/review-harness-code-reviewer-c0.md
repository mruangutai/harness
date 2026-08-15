# Review — FEAT-12 end-copy-distribution — c0

Reviewed `278de74..d543809` (`278de74` = `git merge-base main chore/203-end-copy-distribution`).
`d543809` confirmed as branch tip (`git log -1 d543809`). All citations below read at `d543809`
via `git show d543809:<path>` unless stated otherwise. Human commits in range (`--grep='\[harness:human\]'`):
none — `f3452bf`, `8782ee1`, `7f29d6c` are main-session-direct (layer-0 tasks under DEC-179), not
`[harness:human]`, and inherit ordinary review same as team output.

## VERDICT: FAIL — one must_fix, high

## Must-fix

**T-01/T-04's kaya-`.harness` manifest is not what the signed plan specifies, and it does not carry
the evidence SC-05 claims it does.**

Plan intent for T-01 directs an exact command: `find .harness -type f -print0 | LC_ALL=C sort -z |
xargs -0 shasum -a 256`, redirected to `notes/kaya-harness-manifest-before.txt`, followed by two
appended trailer lines `TOTAL_FILES <n>` / `TOP_LEVEL <...>`. T-04 repeats this "verbatim" for the
after-capture. SC-05 rests on this: *"the same total file count, and the same per-file sha256 ...
differ in nothing."*

Read at `d543809`:
- `notes/kaya-harness-manifest-before.txt` — 377 lines, every line a bare path
  (`.harness/.DS_Store`, `.harness/codebase/.DS_Store`, ...). `grep -cE '^[0-9a-f]{64}'` returns
  `0`. No `TOTAL_FILES` / `TOP_LEVEL` line anywhere (`grep -c` returns `0`).
- `notes/kaya-harness-manifest-after.txt` — same: 377 lines, `0` hash-shaped lines, `0` trailer
  lines.
- `diff` between the two is empty (T-04's verify, `diff ... && echo IDENTICAL`, does pass).

This is `find .harness -type f | sort` output, not `shasum -a 256` output — the shasum step was
never actually run, or its output was stripped down to the path column before being written. Two
independent deviations from the signed intent, both silently accepted:

1. **No per-file sha256 anywhere in the artifact.** SC-05's specific claim — "the same per-file
   sha256 ... differ in nothing" — is not evidenced by this file at all. What the artifact actually
   proves is a strictly weaker claim: the same *set of file paths* exists before and after. A file
   whose **content** changed while its name did not (e.g. a stray write landing inside kaya's
   `.harness/` during the T-02/T-03/D-06 deletion work, or any other process touching that
   directory in the same window) would produce byte-identical manifests here and this artifact
   would report `IDENTICAL` regardless.
2. **The `TOTAL_FILES`/`TOP_LEVEL` trailer the intent calls for "so a later reader can tell the
   capture apart from a partial one"** is absent from both files.

T-01's own `verify:` (`test -s ... && awk 'END{print NR}' ... | awk '$1>50{...}'`) only checks
non-empty and >50 lines — it does not check for a hash column or the trailer, so it passed on the
weaker artifact without objection. T-04's `verify:` only diffs the two captures against each other,
so it certifies **consistency**, never **correctness** of the capture method — the textbook shape
this project's history already flags (DEC-169: an absence/consistency check that was going to pass
anyway proves nothing about the thing it's supposed to be evidence for).

**Consequence:** SC-05 is the sole verification gap-filler named in the BRIEF's own `## Verification
gaps` section for REQ-04 ("kaya-ai's own accumulated state under its `.harness/` is untouched by
this work, in full"). `feature.yaml`'s `sc_tally` records this SC as not yet formally checked
(`"formal goal-check pending"`). As delivered, the artifact this feature would point a goal-check at
cannot actually rule out silent content damage to kaya's `.harness/` state — it can only rule out
added or removed files. This is inspection-verified (Stage 1, `SC-05`), and it fails the "details
match the specific values decided" test: the plan named `shasum -a 256` and two trailer lines
specifically, and neither shipped.

**Recommendation:** re-run T-01 and T-04's captures with the exact command specified (including
`shasum -a 256` and the trailer lines) before SC-05 is marked met. This does not conflict with the
signed plan — it is what the plan already specifies; the deviation is in execution, not intent.

## Primary question — is "factory_config.py is its only reader" true?

Settled: **it is false under the strict "opens/parses the file" reading**, and the plan's own
directed wording used that reading. `check-state.sh:761` (`fleet_p = os.path.join(H, "factory",
"fleet.yaml")`) and `:768` (`fleet = harness_yaml.load_file(fleet_p)`) independently parse
`fleet.yaml` for its `INV-24` invariant — never through `factory_config.load_fleet()`. Confirmed
pre-existing and **unchanged by this diff** (`git diff 278de74..d543809 -- .../check-state.sh` is
empty), so this is not a regression this feature introduced, and `check-state.sh` is one of the
four DEC-174 files this feature may not touch — the remedy is the prose, not the script.

What this means for each surface, checked against code rather than against other prose:
- **`docs/harness/SPEC.md` §3.3** — new text (confirmed via diff, the whole section is added by
  this diff). Its literal sentence is scoped: *"Every **factory tool** ... never parses
  `fleet.yaml` itself."* `check-state.sh` is not framed anywhere as one of "the factory tools," so
  this specific sentence survives a narrow reading — but the citation naming
  `factory_workspace.py:113`, `factory_land.py:46`, `factory_decompose.py` is incomplete:
  `factory_claim.py:202` is a confirmed fourth `factory_config.load_fleet()` call site, absent from
  the citation (all four line numbers verified directly against the sha).
- **`factory_config.py:1`'s own docstring**, *"the only reader of `.harness/factory/fleet.yaml`
  (SC-08)"* — unqualified, no "factory tool" scoping, and false given `check-state.sh`. Confirmed
  byte-identical between `278de74` and `d543809` — pre-existing, not written or touched by this
  feature, and its `(SC-08)` citation names neither this feature's `SC-08` (DEC-12/DEC-113 strike)
  nor anything resolvable from this diff — pre-existing and out of this feature's scope to fix, not
  a finding against this diff, but flagged because it directly contradicts the fleet-model story
  this feature just wrote next to it.
- **`README.md`**'s "four factory scripts" claim — checked complete. `factory_cli.py` and
  `factory_gh.py` also exist in `bin/` and both mention "fleet" in prose, but neither has a
  `if __name__ == "__main__"` / CLI entry point (verified: `grep -n '__main__'` returns nothing for
  either) and `factory_gh.py` has zero `fleet`/`load_fleet` references at all — they are libraries,
  not "factory scripts" in the sense the sentence uses. The board/workspace/repository framing
  ("take their ... from `factory_config.py` ... rather than parsing the fleet declaration
  themselves") holds in its literal sense: none of the four scripts opens `fleet.yaml`; each calls
  `factory_config.load_fleet()`. That several of them then index the returned dict directly
  (`fleet["board"]["owner"]` and siblings, duplicated across `factory_claim.py:207-210`,
  `factory_decompose.py:374-377`, `factory_land.py:87-90`, with no dedicated `factory_config`
  board-accessor) is real but pre-existing and untouched by this diff (`git diff` for all four
  files against base is empty) — out of Stage 2 scope here.

Reading used to settle T-12's directed intent ("factory_config.py is its only reader"): "reader" =
opens/parses the file. Under that reading the phrase as delivered in `SPEC.md` (scoped to "factory
tool") is defensible; the unscoped form in `factory_config.py`'s pre-existing docstring is not, and
neither is the plan's own directed phrasing taken literally. This is a decision question with a
recommendation (qualify `SPEC.md`'s framing to name `check-state.sh`'s independent `INV-24` read, or
soften `factory_config.py`'s docstring claim in a future feature), not a must_fix — the remedy would
touch either DEC-174-protected territory or contradict the signed plan's directed wording.

## Other findings (ranked, none gates)

- **low** — `test-no-distribution.py` `ALLOW_LIST`'s comment asserts "EXACTLY TWO ENTRIES ...
  never derived from what happens to be present, so a new unswept site fails" — but nothing in the
  test asserts `len(ALLOW_LIST) == 2` or validates each entry. A later feature that reintroduces a
  forbidden token and "fixes" the red gate by appending a third path to `ALLOW_LIST` would go
  undetected by this file itself (P-01 shape: the comment advertises a guarantee the code doesn't
  enforce).
- **low** — same file, `case2`'s `read_text()` returns `None` on `OSError` and the caller
  `continue`s past it silently. A tracked-but-unreadable file (bad symlink, permission bit,
  deleted-from-worktree-but-still-tracked) is skipped from the token sweep entirely, so the absence
  half would pass for that file without ever checking it. Narrow precondition, but it is exactly the
  fail-open shape this review is asked to hunt.
- **low** — `case3_presence_fleet_has_exactly_two_repos` asserts `len(repos) == 2`. `SC-03` asks for
  containment ("`repos:` list **contains** `mruangutai/kaya-ai` ... alongside `mruangutai/harness`"),
  not exclusivity. `SPEC.md` §3.3 (this feature's own new text) advertises "Onboarding a repository
  is one edit" — the very next onboarding will redden this specific assertion in
  `test-no-distribution.py`, pointing debugging effort at the distribution-sweep test rather than at
  the fleet file that actually changed. Detail mismatch against the decided value (Stage 1, minor).
- **low** — `test-upgrade-config.py`'s two new sections (T-10's positive-wording assertions) are
  labelled "6" and "7" but land physically before the file's existing section "5" — cosmetic
  numbering only, tests still run and both correctly assert the *new* wording is present
  (`"checkout is incomplete"`, `"complete checkout of this repository"`) and the retired command
  string is absent, which is what the dispatch asked me to check. No functional issue.

## Already-found items — dispositions

1, 2 — settled by qa with mutants, not re-litigated.
3 — agree, still open, low: `SC-02`/`T-09` both say "case 20", the actual name is `case_21`. PM's
    to correct, not a code defect.
4 — agree, still open, low: `T-10`'s comment-only edits in `test-check-plan-routes.py` have no
    standing test (file is `ALLOW_LIST`-exempt). Exactly one file.

## Stage 1 sweep — everything else checked and matching

`fleet.yaml` (T-06), `deploy.sh`/`harness-deploy.md` deletion (T-07/T-08), `upgrade-config.py` +
`test-upgrade-config.py` (T-10), `check-plan-routes.py`/`wayfind.py` comment rewrites (T-10),
`.harness/README.md`, `templates/README.md`, `templates/team-config.yaml`, `.harness/team-config.yaml`
(T-11, exactly the three sites in two files the BRIEF Constraints name — no more), `DECISIONS.md`
DEC-12 struck whole / DEC-113 reduced to the surviving precedence ruling (T-14), `DECISIONS-INDEX.md`
(large diff is pure line-number churn from DEC-12's removal, not scope creep) — all read against
`d543809` and match their task's intent and traced REQ/D. `fleet.yaml` T-06 verify block matches the
committed schema and repo entries exactly.
