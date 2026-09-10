# T-09 · repaired product run digest — validation measurement

**The repair holds.** `validate-digest.py lead <digest>` exits **0** with `digest ok` and nothing on
stderr. The appended block at line 120 is the operative one, its `adequacy_notes:` is a 6-item block
sequence, and the run `state.yaml` is **CLEAN** against `run-state-schema.json`. Read-only run; one
file written (this note).

## 1. Validator — literal output and exit status

Invoked from the worktree root, persona first:

```
$ python3 .claude/skills/harness/bin/validate-digest.py lead .harness/harness/features/FEAT-104-strict-digest-schema/runs/2026-09-09-01-t09-product/digest.md; echo "exit=$?"
digest ok
exit=0
```

Stream-separated re-run to rule out interleaving: **stdout = `digest ok\n` (10 bytes)**, **stderr =
empty (0 bytes)**, **exit 0**. No warning line, no second violation queued behind a first — the error
list is empty, so nothing is being masked.

## 2. The appended block is the one the validator reads

Measured on the file at `digest.md` (153 lines):

| Measurement | Value |
|---|---|
| all lines matching `^VERDICT:` | 72, 120 |
| **last `^VERDICT:`** | **120** |
| all lines matching `adequacy_notes:` | 79, 127 |
| **last `adequacy_notes:`** | **127** |
| line 127 content after the colon | `''` (empty — no inline scalar) |
| lines 128–133 | six `    - "..."` entries |
| `safe_load` of the block at 120–152 | `adequacy_notes` → **`list`, 6 items** |

Line 79 (the superseded block) still carries the prose scalar — correctly preserved. The correction is
an append, not a rewrite, so `check-domain.sh`'s #1058 extends-only guard is satisfied and
`validate-digest.py`'s last-`VERDICT:`-onward rule lands on the list form.

## 3. `state.yaml` — CLEAN

`schema_version: 2`. Validated the parsed YAML against
`.claude/skills/harness/bin/run-state-schema.json` with `jsonschema.Draft202012Validator`
(throwaway heredoc, nothing written to the repo): **0 errors**.

- Undeclared top-level keys: **none** (15 keys, all in `properties`).
- Undeclared `steps[]` keys on `t09-decisions`: **none** (20 keys).
- `evidence` keys failing `^[a-z][a-z0-9_]*$`: **none** (7 keys).
- `evidence` values that are not a scalar or scalar-array: **none**. `dec223_index_anchor: "7092"` is a
  quoted string scalar, which the `oneOf` admits.

Both closed schemas (`additionalProperties: false` on the root and on `steps[]`) pass, so this is
genuine conformance, not an open-schema pass.

## 4. Provenance of the tree I measured

`git status --porcelain` is **empty** and HEAD is `50c4bce9`. That is not evidence the digest was
committed — `git show HEAD:<digest>` reports *exists on disk, but not in 'HEAD'*. The path is
**gitignored**: `.gitignore:7 → .harness/*/features/*/runs/**` matches both `digest.md` and
`state.yaml`.

So the dispatch's expectation that `digest.md` would appear as a pre-existing *modification* does not
hold in either direction: it never appears in `git status` at all. Nothing was reverted. My figures
are therefore working-tree figures by necessity, taken while the product lead was live — see Q2.

My note path is **not** ignored (`git check-ignore` did not match it), so it is the single `??` entry
attributable to me.

## Open questions

- **Q1** — Run digests and `state.yaml` are gitignored, so a review pinned to a `review_sha` cannot
  read them and the extends-only guard is the *only* thing protecting the record. Intended?
  (non-blocking)
- **Q2** — I measured the working tree because no committed copy exists. If the lead appends again,
  lines 120/127 move. Re-derive rather than citing these numbers. (non-blocking)
- **Q3** — The appended block carries `sc_status: []` while the run reports `VERDICT: PASS` on a task
  tracing to requirements; the validator accepts it. Is an empty `sc_status` on a build-flow lead
  digest contract-correct, or a gap the schema should close? (non-blocking)
