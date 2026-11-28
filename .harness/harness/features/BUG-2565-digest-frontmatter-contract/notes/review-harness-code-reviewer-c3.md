# BUG-2565 code review c3 — FAIL

**F-1 remains open (T-03, SC-07).** The three exact c2 witnesses are fixed, but generation still silently changes bytes and the parsed value of an unrelated `description` in valid YAML. `--check` subsequently reports `agent output: ok` on the damaged file. All 16 shipped agents are clean at this pin.

## Stage 1 — spec compliance

Reviewed `104252db9bf39c4acafb0c994a745d8c1cc806fc..b9c98761ff82c408a1c58a974cfd10d60eee31b1`, focused on `ed064577..b9c98761`. No `[harness:human]` commits or dirty tracked product files. `3ab3471f..b9c98761` changes only the pin record. The F-1 ruling authorizes the T-03 generator, its witnesses, and the supporting reader inventory; the fix delta has no other product changes. The intended extraction and strict-parse check serve SC-07/D-01 but do not meet byte preservation (`BRIEF.md:29`).

1. **High · substance · T-03 · `.claude/skills/harness/bin/gen-agent-output.py:51–62,87–95,107–129` — silent non-generated value loss.** Put the three lines `description: 'keep`, `"out\u0070ut": middle`, and `end'` in an agent, followed by genuine stale `structured` and `output` entries. The middle line is literal description text, not a mapping key. The new quoted-token decoding makes the line look like `output`, so the generator removes it. Strict YAML reads the same top-level keys before and after, but the description changes from `keep "out\u0070ut": middle end` to `keep end`. The write exits 0; a later `--check` exits 0. The bare lookalike `output: middle` fails the same way. Repair must select generated top-level YAML spans, not qualifying physical lines, and preserve other key/value bytes.
2. **Med · substance · T-03 · `.claude/skills/harness/bin/gen-agent-output.py:65–84,125–128` — valid stale flow value cannot be regenerated.** `output: {` followed by `  type: old, nested: [one, two]` and a column-zero `}` strictly parses before the write. The span heuristic leaves the closing `}` orphaned. The prospective parse correctly refuses; both commands exit 2 and leave all agents untouched, including an earlier stale agent. This is fail-closed, not data loss, but regeneration does not replace this valid stale output without a manual YAML rewrite.

### Raw-byte CLI measurements

Used pinned schema and agent blobs in disposable scratch roots and the unchanged pinned generator from the feature tree. Statuses are `--check before / write / --check after`. `--check` wrote nothing on every case; the body was unchanged throughout. `Yes (refusal)` means the input itself was untouched, not successfully regenerated.

| Input | Other bytes preserved | Pre-write guard | Statuses |
| --- | --- | --- | --- |
| c2 `-mode: keep me` after stale output | Yes | Accept | 1/0/0 |
| c2 indentationless sequence with inter-item comment; comment before next key | Yes | Accept | 1/0/0 |
| c2 escaped `"struc\u0074ured"` key | Yes | Accept | 1/0/0 |
| Inline flow mapping and sequence | Yes | Accept | 1/0/0 |
| Multiline flow mapping with column-zero `}` | Yes (refusal) | Reject prospective parse | 2/2/2 |
| `output: |-` block scalar with blank line | Yes | Accept | 1/0/0 |
| Comment between `output:` and its value | Yes | Accept | 1/0/0 |
| Tab inside quoted sibling value | Yes | Accept | 1/0/0 |
| Tab used for YAML indentation | Yes (refusal) | Reject current parse | 2/2/2 |
| CRLF, stale values and `-mode` | Yes | Accept | 1/0/0 |
| Escaped quoted `description` as sole spelling | Yes | Accept | 1/0/0 |
| Plain `description` plus escaped quoted `description` | Yes (refusal) | Reject duplicate key (prospective parse ran first) | 2/2/2 |
| Nested sequences under `output` | Yes | Accept | 1/0/0 |
| Bare or escaped key lookalike inside multiline `description` | **No: value line lost** | **Accept** | 1/0/0 |
| `output: stale`, then column-zero and indented comments above `mode: keep` | `mode` bytes kept; both comments lost | Accept | 1/0/0 |
| NEL between `output: stale` and `-mode: keep` | Yes (refusal) | Reject changed key set | 2/2/2 |

### Inspection continuity

- SC-04 — `.omp/extensions/harness-hooks.ts:1763`: pinned `.omp` sweep found none of the retired names; deleted loader absent.
- SC-05 — `notes/research-frontmatter-binding-probe.md:7–19,43–56`: unchanged OMP 19.2.1 receipt records controls absent, off-schema rejected, conforming accepted; I matched blob `96f4332cea14e629fca682433197fee6aa96f893` to the pinned documentor.
- SC-08 — `.claude/skills/harness/bin/digest_projection.py:249`: projection, schemas and agent output unchanged since c2; carry forward the operator-accepted QA parity, not an independent parity rerun.
- SC-09 — `.harness/README.md:176–189`, `BUILD.md:55–64`, `SPEC.md:779,1335–1339`, `harness-team/SKILL.md:146–148`, `org.html:282`: unchanged, pinned retired-control sweep empty.
- SC-10 — `DECISIONS.md:1411,2682,2727,6329,6776,6823,8069`, `DECISIONS-INDEX.md:109,132,206,231`: unchanged from c2.
- SC-11 — `notes/research-yield-refusal-probe.md:6–19`, `.harness/README.md:184–188`, `BUILD.md:60–63`: unchanged OMP 19.2.1 receipt and docs record three refusals, failed status, no consumed schema retry and no refused task data.

## Stage 2 and mechanical digest grade

Substantive code-quality review did not proceed because Stage 1 failed. The independently required pinned `code-grade.py` run found no production failure (`render` grade 4, 7/2/15.5). **Med · substance · T-03 · new non-gating grade-2 record**: `tests/unit/test-digest-projection.py:245`, `case_generator_edges` (7/5/30.0, ABC driver). Retain the concrete transform/assertion pairs next to one another because extracting assertion logic solely to lower ABC would obscure what each edit is expected to preserve. Prior `walk` and `case_generator` grade-2 records are unchanged: `walk` keeps recursive paths adjacent to the expectations they represent; `case_generator` keeps initial write, idempotence and drift against the same fixture. No source change or live enforcement-path execution.
