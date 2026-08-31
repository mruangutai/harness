# Receipt — documentor — fold three merged amendments (FEAT-38, fold-merge)

**All three amendment sub-sections that arrived with the FEAT-44 merge are folded into their
entries' current truth and deleted. `**Amendment` occurrences in the authority: 0 (counted in
Python).** `test-gen-decisions-index.py` exits 0, all 11 cases green including
`test_no_amendment_construct_survives_in_the_authority`. Nothing committed; HEAD untouched.

## The three folds

| Entry | New span | Where the falsified claim now lives |
|---|---|---|
| DEC-159 | 3674–3745 | `**The in-flight warning...**` para, sentence beginning **"No Claude hook is registered for this any more, and none is to be proposed again:"** (3726) — names `context-watch-hook.py`, the `.claude/settings.json` `Write\|Edit\|Bash` registration, and FEAT-44 #923 deleting both, as a past clause of the present-tense OMP `tool_result` delivery. |
| DEC-198 | 5601–5669 | `**Chose:**` para, sentence **"The default was once sourced to `.claude/skills/harness/bin/context-watch.py`, which is retired and absent from the tree"** (5608–5610), with the Claude-sidecar/`.omp/config.yml` reason and the "re-homing not a redefinition" force (5611). Second falsified claim — the earlier draft's "key absent" assertion — survives at 5618–5619. |
| DEC-201 | 5809–5941 | `**Self-identification is no longer part of the ruling...**` para, **"The retired scheme is recorded here so it cannot be re-proposed as new:"** (5872–5875) plus **"Its two-call constraint was CORRECT and died with the mechanism rather than being found wrong"** (5875–5878), closing "a claim that was right and became inapplicable is not a claim that was refuted." |

## DEC-201 evidence limits — all six survive

1. ONE OMP build, twice, one machine (2026-08-28, 2026-08-29) — 5881
2. probe + raw output committed at `.harness/.../FEAT-44-omp-context-advisory/evidence/README.md` — 5882–5883 (path exists)
3. version-floor risk: a later OMP may rename or drop the accessor — 5883–5884
4. not unwatched: `probe-omp-session-accessor.py` dispatches a real subagent and **fails, never skips** — 5884–5886 (file exists)
5. MANUAL check, not a CI gate (needs omp binary + live credentials) — 5886–5888
6. one build's observed behaviour, not a timeless property of the OMP API — 5888–5889

Untouched in DEC-201, as bounded: never-wait ruling, `echo hold` incident numbers (5842, 5899),
three 2026-08-23 probes (5855), 1057.1s + dispatch-level-override limit (5895, 5903), bands,
lineage (5930). No new supersession added; DEC-204's existing supersession is restated as a
cross-reference only (5870–5872). Stray `---` that arrived with the DEC-201 amendment is gone.

## Verification (observed)

- `gen-decisions-index.py` regeneration is a **fixpoint** — two runs, sha256 identical (`a32e946ac110…`).
- **orphans: 0** (row ids − live headings = ∅; also refs-graph orphans = 0).
- **rows 188 = live `## DEC-` headings 188.**
- `test-gen-decisions-index.py` → **exit 0**, 11/11 ok.
- `check-decision-anchors.py` → 20 anchors examined, 0 failed.
- `**Amendment` count in `DECISIONS.md`: **0** (Python `str.count` over lines).
- Symbols confirmed live: `export const DEFAULT_CONTEXT_WARN_TOKENS = 200000;` at
  `.omp/extensions/harness-hooks.ts:428`, `export function resolveContextWarnTokens` at `:519`.
  `.harness/harness.json:169` = `200000`, rationale sibling at `:170` — anchors kept verbatim.
  `context-watch.py` and `context-watch-hook.py` absent from the tree, as asserted.

## Notes (reported, not edited)

- DEC-159 line 3714–3718 still describes `check-domain.sh`'s handoff shape gate as `>40 lines`
  while 3697 says the cap was raised to ~60 at DEC-160. Out of scope for this fold (un-amended
  remainder); flagged for whoever owns DEC-159's next pass.
