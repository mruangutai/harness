# Receipt — harness-data-engineer — simplify angle — FEAT-27

**BLUF:** Two findings, both real, neither touches an assertion. (1) `inject-expertise.sh` carries
a manual sort step that duplicates ordering bash's own glob expansion already guarantees — confirmed
empirically, not just by reading. (2) `check-expertise.sh` has a dead comment reference to a
"CHANGE 1" label that doesn't exist in the file. Both are surgical, low-risk deletions/text fixes.
No finding here weakens or removes a test assertion.

## Finding 1 — redundant sort duplicates glob's own ordering

**File · lines:** `.claude/skills/harness/bin/inject-expertise.sh:82-90`

```bash
sorted_idx=()
if [ "${#repo_segments[@]}" -gt 0 ]; then
  while IFS= read -r line; do
    sorted_idx+=("${line%%:*}")
  done < <(
    for i in "${!repo_segments[@]}"; do
      printf '%s:%s\n' "$i" "${repo_segments[$i]}"
    done | sort -t: -k2
  )
fi
```

**Summary:** This block re-sorts `repo_segments` by segment name using an index-pair + `sort -t: -k2`
subshell, but the `repo_segments`/`repo_files` arrays were already populated in the order the
preceding glob (`"$root"/.harness/*/expertise/"$agent.md"`) yielded — and bash pathname expansion is
sorted lexicographically by the shell itself, before the loop ever runs. I verified this directly:
created `.harness/{zeta,alpha,mid}/expertise/agent.md` on disk in that (non-alphabetical) creation
order, then ran a bare `for f in .harness/*/expertise/agent.md` glob — output came back
`alpha, mid, zeta`. The explicit sort step never changes the order the loop already receives.

**Cost:** ~10 extra lines, a `read` loop, and a forked `sort` subshell process, all producing output
identical to the input order. It is not wrong, but it is a second place the ordering guarantee lives
— if a future edit changes the glob to something that isn't naturally sorted (e.g. `find` with
`-print0` piped through something order-unstable) without also revisiting this block, the two could
silently drift, and nobody would notice because the block would still "work," just redundantly.
`test-inject-expertise.py` case2 (`harness`, `kaya` segments) does not discriminate this — the test
fixture happens to create files in already-alphabetical order, so it passes whether or not the sort
runs at all.

**Alternative:** Delete the `sorted_idx` block (lines 82-90) and the loop below that consumes it;
iterate `repo_segments`/`repo_files` directly in glob order, since that order is already the sorted
one. One-line instruction: "drop the manual index-sort in `inject-expertise.sh` and iterate the
glob-populated arrays directly."

**What would prove it safe:** Delete the block, iterate in glob order, and re-run
`test-inject-expertise.py` case2 with a **reordered fixture** that first proves the discriminating
gap (e.g. create `zeta` before `alpha` — which is what I actually did to confirm the glob is
pre-sorted) so the test can no longer pass by accident either way.

## Finding 2 — dead reference to a nonexistent "CHANGE 1" comment

**File · line:** `.claude/skills/harness/bin/check-expertise.sh:62`

```python
def classify_tier(path):
    """Classify by the resolved absolute path, never the argument as typed —
    a bare-path invocation from a cwd under .harness/... must still resolve
    to its true tier (see check-expertise.sh's CHANGE 1 note)."""
```

**Summary:** The docstring points a reader at "check-expertise.sh's CHANGE 1 note" for more context.
I grepped the file (`grep -n CHANGE check-expertise.sh`) — the only other `CHANGE` marker present is
`CHANGE 2` at line 150 (the advisory token-scan comment). There is no `CHANGE 1` anywhere in the
file; the label narrates an earlier draft/review round of this diff rather than describing the
present code, and now points nowhere.

**Cost:** A reader chasing "CHANGE 1" for the promised rationale finds nothing, has to reconstruct
the reasoning from the surrounding code instead, and may reasonably suspect the file is missing a
chunk of intended context (it isn't — the label is just a review-round artifact).

**Alternative:** Replace `"(see check-expertise.sh's CHANGE 1 note)"` with the actual rationale
inline, or drop the parenthetical entirely — the preceding clause ("a bare-path invocation ... must
still resolve to its true tier") already states the present fact on its own. One-line instruction:
"delete the trailing `(see check-expertise.sh's CHANGE 1 note)` parenthetical at
`check-expertise.sh:62`; the sentence stands without it."

**What would prove it safe:** `grep -n CHANGE .claude/skills/harness/bin/check-expertise.sh` after
the edit shows only the one remaining `CHANGE 2` marker (or none, if that label is cleaned too),
confirming no comment points at a heading that isn't in the file.

## Not flagged (checked, judged fine)

- `inject-expertise.sh`'s emit group (glob loop → segment filter → sort → emit block with the
  precedence line and per-tier `cap_body` calls): still reads as one linear pipeline — gather,
  classify, present — despite five features landing together. No restructuring proposed.
- `check-expertise.sh`'s tier classification (`classify_tier`) and the advisory token scan (lines
  ~150-157) are physically adjacent but functionally separable — the scan reads `tier` as a value
  the classifier already produced and gates on it once (`if tier == "craft"`), it does not reach
  back into classification logic. Reads as two things using one shared fact, not one tangled thing.
- Precedence-line wording/placement, `os.path.abspath()` classification, and the two-enforcement-point
  shape are explicitly settled — not re-litigated.

**Verdict for this angle: two findings, both advisory-severity text/structure fixes. Nothing here
proposes weakening, merging, or deleting any test assertion.**
