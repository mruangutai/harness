# Receipt — harness-documentor — T-11 — c1

**PASS. DEC-138 and DEC-203 now state native Issue Types as present-tense truth, the eighth
read-back purpose carries the pinned row unwrapped on one physical line, and the index regenerates
byte-identical.** Two files changed, nothing staged, nothing committed.

## What landed

| Intent section | Where | What it now says |
|---|---|---|
| 1 — Mapping + type derivation | `DECISIONS.md:2933-2939` (Mapping), `:3038-3050` (**Issue type**), `:3052-3055` | Mapping's `T-NN` clause now says the issue carries a native type where the repository declares them. The former `change_type`→label paragraph is rewritten as **Issue type**: native type from `gh_issue_types.py`'s mapping (defect `Bug` incl. a `bugfix` sub-issue, backlog enhancement `Feature`, gh-sync and factory parents `Feature`, every other task sub-issue `Task` incl. `feature`, D-18), renameable at `.harness/harness.json github.issue_types` (four canonical keys); `bug`/`chore` not applied in that mode, `harness`/`feature:<FEAT>`/`factory:claimed`/`abandoned` applied in both; label derivation retained for a repository declaring no native types. A closing paragraph states the adopted-or-created-but-never-discovered rule and the asymmetric-truth boundary stand intact — receipt-based recovery, an adopted issue's type never changed |
| 2 — write-only reading | `DECISIONS.md:3029-3036` | The reads DEC-203's eighth purpose names are authorised; this feature adds exactly two (capability query; `node_id_args` node-id lookup immediately before a type-apply against a number the receipt already holds). One sentence, this file only, records that `gh_issues.internal_id_args` has read a recorded issue's id for sub-issue attach/detach since sub-issue mirroring shipped, was never enumerated, and keeps its call sites |
| 3 — DEC-203's list | `DECISIONS.md:6089-6106` | "carried forward and now **EIGHT purposes**"; purpose 8 is the pinned row (below) plus a consumer continuation naming `gh_issue_types.py`'s shared type-apply path, `gh-sync.py`, `factory_decompose.py`, and `probe-issue-types.py` for the read-back clause. Two paragraphs follow: the one-query/one-row bounds (JSON null vs declared names; node-id only against a recorded number; read-back only under the D-19 create opt-in; every value process-local apart from the `typed` receipt flag, reaching no approval-gated artifact) and the two-file pin guarded by `tests/unit/test-issue-types-pin.py` |
| 4 — index | `DECISIONS-INDEX.md` | Regenerated; `--stdout | diff` is clean. DEC-203's hand-written ruling said "read-back bounded to seven purposes" — falsified by this edit, so it now reads "eight purposes" (same word count; rulings are preserved verbatim across regeneration, `gen-decisions-index.py:13-14`, so the diff stays clean) |

No `DEC-138 amendment N` heading exists (DEC-205); the falsified paragraphs were rewritten in place.

## The pinned row — 394 characters, one physical line, `DECISIONS.md:6103`

```
whether a target repository supports native Issue Types, and which native issue types a repository declares; the node identifier of an issue whose number Harness already recorded locally, read by gh_issue_types.node_id_args immediately before a type-apply; and the native type assigned to an issue Harness created, read back by tests/manual/probe-issue-types.py under its explicit create opt-in
```

Proof, not eyeballing:

```
$ grep -n "whether a target repository supports native Issue Types" ... | awk length
line 6103 length=397          # 394 + the "8. " list prefix; one physical line
$ grep -c "whether a target repository supports native Issue Types" DECISIONS.md
1
$ python3  # re.search without DOTALL, the T-01/T-12 regex shape
chars: 394
newlines inside row: 0
byte-identical to plan.yaml:1665 pin: True
landed at .harness/harness/docs/DECISIONS.md:6103
```

T-12 must write these exact bytes into `.claude/skills/harness/references/github-mirror.md`.

## Verify block, run verbatim from the worktree root

```
$ grep -q "which native issue types a repository declares" .harness/harness/docs/DECISIONS.md || exit 1
$ grep -q "the native type assigned to an issue Harness created" .harness/harness/docs/DECISIONS.md || exit 1
$ grep -q "EIGHT purposes" .harness/harness/docs/DECISIONS.md || exit 1
$ grep -riq "DEC-138 amendment\|DEC-138 am\." .harness/harness/docs/DECISIONS.md && { echo ...; exit 1; }
$ python3 .claude/skills/harness/bin/gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md
VERIFY BLOCK EXIT: 0
```

The block emitted no other output: every clause is silent on success and the `diff` printed zero
bytes, which is its pass condition. Baseline before editing was clause 1/2/3 all missing (exit 1),
so the block was genuinely red first. `gen-decisions-index.py` prints nothing on success; the index
was separately checked for `RULING PENDING` (none) and the row-text diff (`grep -v` on `::` text)
showed only `@line` anchor shifts plus the DEC-203 ruling correction.

Nothing wider was run — no `bin/run-unit-tests.sh`, no formatter, no linter: `tests/unit/test-issue-types-pin.py` is
deliberately red until T-12 lands.

## Facts checked against code, not transcribed

- `gh_issue_types.py` does **not exist yet** (T-02 builds it). The mapping written into DEC-138 is
  the signed one, cross-read from plan `D-01/D-02/D-03/D-04/D-12/D-18` and T-01's assertion groups
  (`plan.yaml:453-482`), not from the module.
- `internal_id_args` call sites confirmed at `eb9d044e` by `git show`: `gh-sync.py:974`, `:1215`,
  `factory_gh.py:981`. `wayfind.py:271`/`:279` also call it — wayfinding, outside DEC-138's mirror,
  so deliberately not named in the sentence the intent scoped to sub-issue attach/detach.
- Label vocabulary confirmed live: `harness`/`chore`/`bug`/`enhancement`/`abandoned` in
  `gh-sync.py:881-882`, `feature:<FEAT>` and `factory:claimed` in `factory_decompose.py:326,395`.
  `factory_decompose.py` does create issues (`:422`), so naming it a consumer is accurate.

## Open

- `DECISIONS.md:2938` says issue numbers are recorded in **`feature.yaml`**; the shipped receipt is
  `feature.json` (`gh-sync.py` `feature_json_write`). Pre-existing, untouched, out of T-11's scope.
