# UI review — BUG-1309 c18 — test-only diff census

**Verdict: PASS.** No operator-visible string changed; the two new/amended assertions that DO pin
operator-facing wording pin it at fragment granularity (identity + remedy token), which is the
right level for text an operator reads — narrow enough to survive prose edits, specific enough to
catch a missing feature ID or a missing remedy command.

## Measured census (not predicted)

```
git -C <worktree> diff --stat 9fe5cf31^..9fe5cf31
 tests/integration/test-merge-gate.py | 38 +++++++++++++++++++++++++++++++++++-
 1 file changed, 37 insertions(+), 1 deletion(-)

git -C <worktree> diff --name-only 9fe5cf31^..9fe5cf31
 tests/integration/test-merge-gate.py
```
One file, test-only, matches dispatch exactly. Zero html/css/scss/tsx/jsx/vue/svelte/less files in
the diff (repo project-tier P-01: no rendered UI surface exists in this repo by default). No
DESIGN.md, no markdown contract, changed.

`git diff 9fe5cf31^..9fe5cf31 -- .claude/skills/harness/bin/merge-gate.py` → **0 lines**. Confirmed
directly, not assumed: production source, and therefore every `permissionDecisionReason` string the
gate can print, is byte-unchanged at this pin. Source strings read at
`.claude/skills/harness/bin/merge-gate.py:174` (ambiguity deny), `:188` (unpinned-repo deny), `:192`
(single-owner deny) — none touched.

## Operator-visible surface: the two places this diff touches wording

1. **Gap A case** (`test-merge-gate.py:66-68`) — renamed from `"T-05 non-era absent build_entry
   denies"` to `"... denies naming feature and re-run command"`, and now asserts `"FEAT-9001-
   fixture-non-era" in reason` in addition to the pre-existing `"gh-sync.py open" in reason`. This
   pins that the single-owner deny names the feature ID as literal substring, alongside the already-
   pinned remedy-command token. Matches SC-04's clause verbatim ("that single-owner deny carries a
   reason naming the feature and the re-run command", BRIEF.md:108-110).
2. **Gap B case** (`:164-174`) — new. Asserts `"FEAT-9001-fixture-non-era" in reason and era_id in
   reason and "gh-sync.py" not in reason`. The `not in` clause is a real discriminator, not
   incidental: read against source, the ambiguity-deny template (`merge-gate.py:174`, "Correct the
   duplicated top-level `branch` field… no receipt command clears this") contains no `gh-sync.py`
   substring anywhere, so this negative assertion cannot pass by accident — it genuinely
   distinguishes ambiguity-deny wording (no remedy offered) from single-owner-deny wording (remedy
   named).

Both assertions pin **substrings of dynamic content** (a feature ID, an era ID, a fixed command
fragment) rather than the full sentence. That is the correct granularity for operator-facing prose:
it binds the two facts an operator actually needs (which feature, what to run next) without pinning
phrasing an editor should be free to improve later. Gap C's new case (`:183-206`) asserts only
`d is None` — the noise-tolerance case makes zero wording assertions, so it introduces no new pinned
string at all.

## UAT cross-check

`notes/uat-BUG-1309-mirror-build-entry.md` (unchanged by this commit) quotes the single-owner deny
verbatim at Step 3: `merge-gate: FEAT-9001-uat-scratch records github.build_entry=recovery-required
… This merge is denied until python3 .claude/skills/harness/bin/gh-sync.py open <dir> records one.`
Both substrings the amended Gap A case now pins — a feature-ID token and `gh-sync.py open` — are
present in that quoted operator-facing text, so the newly-pinned assertions are consistent with what
a human operator is shown and told to expect. The UAT script does not walk the ambiguity/duplicate-
claimant or era-ordering scenario (Gap B's case) at all — that is a pre-existing UAT coverage gap,
untouched by this diff, out of scope for a test-only cycle with an exhausted budget; not re-raised
as a finding here, noted for the record only.

## Advisory, not mine to own (naming the right lens)

While reading the `check()`/print format to judge assertion granularity I confirmed PRED-4
(Evidence/QA's prediction, not UI's): the amended case name `"T-05 non-era absent build_entry
denies naming feature and re-run command"` is a strict superstring of the old name enumerated in the
`verify:` block (`plan.yaml:1065-1066`, `"T-05 non-era absent build_entry denies"`), and that block
matches with `grep -qF "ok    $n"` — a literal substring match. **CONFIRMED, non-breaking**: the old
literal is a prefix of the new line the amended case prints (`ok    T-05 non-era absent build_entry
denies naming feature and re-run command`), so the substring match still succeeds. This is test-
harness wiring, not operator-visible text — Evidence/QA's lens owns it; I report it only because I
measured it in passing.

## Findings

None gate. No accessibility/theme-parity/state-completeness section applies: this diff has no
rendered surface and no colour-only state encoding (repo Expertise G-02 rationale) — CLI pass/fail
print lines are the entire operator-visible format here, and they are unchanged in structure.

`git status --porcelain` checked at start and end of this review: only a pre-existing modification
to `feature.json` (not made by me — I made zero writes to the tree). No probe/mutation copies were
needed for this task; the census and string-consistency checks were read-only.
